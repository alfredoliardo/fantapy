import asyncio
import json
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from api.auction_room import AuctionRoom
from api.models import AuctionDTO, AuctionRoomDTO, ParticipantDTO, PlayerDTO, TeamDTO
from api.remote_participant import RemoteParticipant
from core.auction import Auction
from core.calling_strategy.sequential_calling_strategy import SequentialCallingStrategy
from core.enums import PlayerRole
from core.player import Player

router = APIRouter()

# In-memory storage per demo
auctions: Dict[str, AuctionRoom] = {}
auction_simulations: Dict[str, asyncio.Task] = {}


class AuctionCreate(BaseModel):
    name: str
    nickname: str
    budget: int
    max_teams: int


class AssignParticipantRequest(BaseModel):
    participant_id: str
    team_id: int


def _seed_default_players(auction: Auction) -> None:
    if auction.player_pool.get_all():
        return
    sample_data = [
        (1, "G. Donnarumma", PlayerRole.GOALKEEPER, "PSG"),
        (2, "T. Hernandez", PlayerRole.DEFENDER, "Milan"),
        (3, "M. de Ligt", PlayerRole.DEFENDER, "Bayern"),
        (4, "S. Milinkovic", PlayerRole.MIDFIELDER, "Al-Hilal"),
        (5, "N. Barella", PlayerRole.MIDFIELDER, "Inter"),
        (6, "D. Berardi", PlayerRole.FORWARD, "Sassuolo"),
        (7, "V. Osimhen", PlayerRole.FORWARD, "Napoli"),
        (8, "R. Leão", PlayerRole.FORWARD, "Milan"),
    ]
    players = [
        Player(pid, name, role, real_team)
        for pid, name, role, real_team in sample_data
    ]
    auction.player_pool.add_players(players)


def _build_snapshot(auction_room: AuctionRoom) -> AuctionRoomDTO:
    participant_assignments: Dict[str, List[str]] = {
        participant_id: []
        for participant_id in auction_room.participants
    }
    for team_id, participants in auction_room.team_to_participants.items():
        team_id_str = str(team_id)
        for participant in participants:
            participant_assignments.setdefault(participant.id, []).append(team_id_str)

    teams: List[TeamDTO] = []
    for team in auction_room.auction.teams.values():
        team_players = [
            PlayerDTO(
                id=p.player_id,
                name=p.name,
                role=p.role.name,
                team_name=p.realTeam,
            )
            for p in team.roster
        ]
        team_participants = [
            ParticipantDTO(
                id=participant.id,
                name=participant.name,
                assigned_teams=participant_assignments.get(participant.id, []),
            )
            for participant in auction_room.team_to_participants.get(team.id, [])
        ]
        teams.append(
            TeamDTO(
                id=team.id,
                name=team.name,
                players=team_players,
                budget=team.spent,
                participants=team_participants,
            )
        )

    current_caller = None
    current_player = None
    if auction_room.auction.current_turn is not None:
        current_caller = getattr(auction_room.auction.current_turn.caller, "name", None)
        player_obj = auction_room.auction.current_turn.player
        current_player = getattr(player_obj, "name", None) if player_obj else None

    snapshot = AuctionRoomDTO(
        auction=AuctionDTO(
            id=auction_room.auction.auction_id,
            name=auction_room.auction.name,
            teams=teams,
            current_caller=current_caller,
            current_player=current_player,
            started=auction_room.auction.started,
        ),
        participants=[
            ParticipantDTO(
                id=participant.id,
                name=participant.name,
                assigned_teams=participant_assignments.get(participant.id, []),
            )
            for participant in auction_room.participants.values()
        ],
    )
    return snapshot


async def _broadcast_snapshot(auction_room: AuctionRoom) -> AuctionRoomDTO:
    snapshot = _build_snapshot(auction_room)
    await auction_room.broadcast({
        "type": "auction_snapshot",
        "payload": snapshot.model_dump_json(),
    })
    return snapshot


def _player_to_payload(player: Player) -> dict:
    return {
        "player_id": player.player_id,
        "name": player.name,
        "role": player.role.name,
        "real_team": player.realTeam,
    }


def _get_callers_for_auction(auction_room: AuctionRoom) -> List[RemoteParticipant]:
    callers: List[RemoteParticipant] = []
    participant_ids = set()
    for participants in auction_room.team_to_participants.values():
        for participant in participants:
            if participant.id in auction_room.participants and participant.id not in participant_ids:
                callers.append(participant)
                participant_ids.add(participant.id)
    return callers


def _ensure_calling_strategy(auction_room: AuctionRoom) -> List[RemoteParticipant]:
    callers = _get_callers_for_auction(auction_room)
    if not callers:
        return []
    strategy = getattr(auction_room.auction, "calling_strategy", None)
    if strategy is None:
        auction_room.auction.set_calling_strategy(SequentialCallingStrategy(callers))
    else:
        try:
            strategy.update_callers(callers)
        except AttributeError:
            auction_room.auction.set_calling_strategy(SequentialCallingStrategy(callers))
    return callers


async def _request_player_choice(callers: List[RemoteParticipant], available_players: List[Player]) -> tuple[Optional[Player], Optional[RemoteParticipant]]:
    if not callers or not available_players:
        return None, None
    tasks: Dict[asyncio.Task, RemoteParticipant] = {}
    for caller in callers:
        tasks[asyncio.create_task(caller.choose_player(available_players))] = caller

    done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)

    chosen_player: Optional[Player] = None
    chosen_caller: Optional[RemoteParticipant] = None

    for task in done:
        caller = tasks[task]
        try:
            result = task.result()
        except Exception:
            result = None
        if result is not None:
            chosen_player = result
            chosen_caller = caller
            break

    for task in pending:
        task.cancel()

    return chosen_player, chosen_caller


async def _run_bidding_phase(auction_room: AuctionRoom, player: Player) -> Optional[RemoteParticipant]:
    bidders = [
        participant
        for participant in auction_room.participants.values()
        if participant.team is not None
        and auction_room.auction.player_pool.is_available_for_team(player, participant.team)
    ]

    await auction_room.broadcast({
        "type": "bidding_started",
        "payload": {
            "player": _player_to_payload(player),
            "bidders": [{"id": b.id, "name": b.name, "team_id": b.team.id if b.team else None} for b in bidders],
        },
    })

    if not bidders:
        await auction_room.broadcast({
            "type": "bidding_result",
            "payload": {
                "status": "no_bidders",
                "player": _player_to_payload(player),
            },
        })
        return None

    offers = []
    for bidder in bidders:
        try:
            amount = await bidder.get_bid(player)
        except Exception:
            amount = None
        if amount is None:
            continue
        offers.append((amount, bidder))

    if not offers:
        await auction_room.broadcast({
            "type": "bidding_result",
            "payload": {
                "status": "no_bids",
                "player": _player_to_payload(player),
            },
        })
        return None

    offers.sort(key=lambda item: item[0], reverse=True)
    winning_amount, winner = offers[0]
    if winner.team is not None:
        auction_room.auction.player_pool.assign_to_team(player, winner.team, winning_amount)
        winner.team.spent += winning_amount

    await auction_room.broadcast({
        "type": "bidding_result",
        "payload": {
            "status": "won",
            "player": _player_to_payload(player),
            "winner": {
                "id": winner.id,
                "name": winner.name,
                "team_id": winner.team.id if winner.team else None,
                "team_name": winner.team.name if winner.team else None,
            },
            "amount": winning_amount,
        },
    })
    return winner


async def _run_auction_loop(auction_id: str, auction_room: AuctionRoom):
    auction = auction_room.auction
    end_reason: Optional[str] = None
    try:
        await auction_room.broadcast({
            "type": "auction_started",
            "payload": {"auction_id": auction_id},
        })

        while auction.started:
            available_pool = _ensure_calling_strategy(auction_room)
            strategy = getattr(auction, "calling_strategy", None)
            callers = strategy.next_caller() if strategy else available_pool
            available_players = auction.player_pool.get_available()

            if not callers:
                end_reason = "no_callers"
                await auction_room.broadcast({
                    "type": "auction_paused",
                    "payload": {"reason": end_reason},
                })
                break

            if not available_players:
                end_reason = "no_players"
                break

            await auction_room.broadcast({
                "type": "turn_waiting_for_player",
                "payload": {
                    "auction_id": auction_id,
                    "callers": [{"id": c.id, "name": c.name} for c in callers],
                    "player_pool": [_player_to_payload(p) for p in available_players],
                },
            })

            player, caller = await _request_player_choice(callers, available_players)
            if not player or not caller:
                await asyncio.sleep(0.2)
                continue

            await auction_room.broadcast({
                "type": "player_selected",
                "payload": {
                    "caller": {"id": caller.id, "name": caller.name},
                    "player": _player_to_payload(player),
                },
            })

            await _run_bidding_phase(auction_room, player)
            await _broadcast_snapshot(auction_room)

    except asyncio.CancelledError:
        raise
    finally:
        auction.started = False
        await auction_room.broadcast({
            "type": "auction_finished",
            "payload": {"auction_id": auction_id, "reason": end_reason},
        })
        await _broadcast_snapshot(auction_room)


# --- ROUTES ---

@router.get("/")
def list_auctions() -> List[dict]:
    return [
        {
            "auction_id": auction_id,
            "name": room.auction.name,
            "join_url": f"/auctions/{auction_id}/ws",
            "started": room.auction.started,
        }
        for auction_id, room in auctions.items()
    ]


@router.post("/")
def create_auction(data: AuctionCreate):
    auction_id = str(uuid.uuid4())
    auction = Auction(auction_id, data.name, data.max_teams)
    _seed_default_players(auction)

    auctions[auction_id] = AuctionRoom(auction)

    return {"auction_id": auction_id, "join_url": f"/auctions/{auction_id}/ws"}


@router.get("/{auction_id}", response_model=AuctionRoomDTO)
def get_auction(auction_id: str):
    if auction_id not in auctions:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction_room = auctions[auction_id]
    return _build_snapshot(auction_room)


@router.websocket("/{auction_id}/ws")
async def auction_ws(ws: WebSocket, auction_id: str):
    if auction_id not in auctions:
        await ws.close(code=1008)  # policy violation
        return

    await ws.accept()
    auction_room = auctions[auction_id]
    snapshot = _build_snapshot(auction_room)
    await ws.send_json({"type": "auction_snapshot", "payload": snapshot.model_dump_json()})

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "join":
                nickname = msg["payload"]["name"]
                new_id = str(uuid.uuid4())
                participant = RemoteParticipant(new_id, nickname, ws)

                auction_room.join(participant)

                await ws.send_json({
                    "type": "joined",
                    "payload": {"id": participant.id, "name": participant.name}
                })
                await _broadcast_snapshot(auction_room)

            else:
                msg_type = msg.get("type")
                participant_id = msg.get("participant_id")
                routed = False
                if msg_type in {
                    "choose_player_response",
                    "place_bid_response",
                    "choose_bidding_strategy_response",
                } and participant_id:
                    participant = auction_room.participants.get(participant_id)
                    if participant:
                        participant.push_message(msg)
                        routed = True
                if not routed:
                    await auction_room.broadcast(msg)

    except WebSocketDisconnect:
        disconnected_ids = [
            pid for pid, participant in list(auction_room.participants.items())
            if participant._ws is ws
        ]
        for pid in disconnected_ids:
            auction_room.leave(pid)
        if disconnected_ids:
            await _broadcast_snapshot(auction_room)


@router.post("/{auction_id}/assign")
async def assign_participant(auction_id: str, payload: AssignParticipantRequest):
    if auction_id not in auctions:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction_room = auctions[auction_id]
    participant = auction_room.participants.get(payload.participant_id)
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")

    if payload.team_id not in auction_room.auction.teams:
        raise HTTPException(status_code=404, detail="Team not found")

    auction_room.assign_participant(participant, payload.team_id)
    snapshot = await _broadcast_snapshot(auction_room)
    return {"status": "assigned", "snapshot": snapshot.model_dump()}


@router.post("/{auction_id}/start")
async def start_auction(auction_id: str):
    if auction_id not in auctions:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction_room = auctions[auction_id]
    if auction_room.auction.started:
        raise HTTPException(status_code=400, detail="Auction already started")

    total_assigned = sum(len(v) for v in auction_room.team_to_participants.values())
    if total_assigned == 0:
        raise HTTPException(status_code=400, detail="No participants assigned to teams")

    callers = _ensure_calling_strategy(auction_room)
    if not callers:
        raise HTTPException(status_code=400, detail="No eligible callers")

    auction_room.auction.started = True
    await _broadcast_snapshot(auction_room)

    task = asyncio.create_task(_run_auction_loop(auction_id, auction_room))
    auction_simulations[auction_id] = task

    def _cleanup_task(t: asyncio.Task):
        auction_simulations.pop(auction_id, None)

    task.add_done_callback(_cleanup_task)
    return {"status": "started"}
