from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict
import uuid
import json

from api.models import AuctionDTO, PlayerDTO, TeamDTO
from core.auction import Auction
from core.team import Team

router = APIRouter()

# In-memory storage per demo
auctions: Dict[str, Auction] = {}

class AuctionCreate(BaseModel):
    name: str
    nickname: str
    budget: int
    max_teams: int


# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        # auction_id -> { participant_id: websocket }
        self.active_connections: dict[str, dict[int, WebSocket]] = {}

    async def connect(self, auction_id: str, ws: WebSocket):
        await ws.accept()
        if auction_id not in self.active_connections:
            self.active_connections[auction_id] = {}

    def register(self, auction_id: str, participant_id: int, ws: WebSocket):
        if auction_id not in self.active_connections:
            self.active_connections[auction_id] = {}
        self.active_connections[auction_id][participant_id] = ws

    def unregister(self, auction_id: str, participant_id: int):
        if auction_id in self.active_connections:
            self.active_connections[auction_id].pop(participant_id, None)

    async def broadcast(self, auction_id: str, message: dict):
        if auction_id not in self.active_connections:
            return
        to_remove = []
        for pid, ws in self.active_connections[auction_id].items():
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(pid)
        for pid in to_remove:
            self.unregister(auction_id, pid)


manager = ConnectionManager()


# --- ROUTES ---

@router.post("/")
def create_auction(data: AuctionCreate):
    auction_id = str(uuid.uuid4())
    auction = Auction(
        auction_id=auction_id,
        auction_name=data.name,
        host_name=data.nickname
    )
    auctions[auction_id] = auction
    return {"auction_id": auction_id, "join_url": f"/auctions/{auction_id}/ws"}


@router.get("/{auction_id}", response_model=AuctionDTO)
def get_auction(auction_id: str):
    if auction_id not in auctions:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction = auctions[auction_id]

    return AuctionDTO(
        id=auction.auction_id,
        name=auction.name,
        participants=[p.name for p in auction.participants.values()],
        teams=[
            TeamDTO(
                id=t.id,
                name=t.name,
                players=[
                    PlayerDTO(
                        id=p.player_id,
                        name=p.name,
                        role=p.role.name,
                        team_name=p.realTeam
                    ) for p in t.roster
                ],
                budget=t.spent,
            )
            for t in auction.teams.values()
        ],
        current_caller=auction.current_caller.name if auction.current_caller else None,
        current_player=auction.current_player.name if auction.current_player else None,
    )


@router.websocket("/{auction_id}/ws")
async def auction_ws(ws: WebSocket, auction_id: str):
    if auction_id not in auctions:
        await ws.close(code=1008)  # policy violation
        return

    await manager.connect(auction_id, ws)
    auction = auctions[auction_id]

    # Invia subito snapshot iniziale
    snapshot = AuctionDTO(
        id=auction.auction_id,
        name=auction.name,
        participants=[p.name for p in auction.participants.values()],
        teams=[
            TeamDTO(
                id=t.id,
                name=t.name,
                players=[
                    PlayerDTO(
                        id=p.player_id,
                        name=p.name,
                        role=p.role.name,
                        team_name=p.realTeam
                    ) for p in t.roster
                ],
                budget=t.spent,
            )
            for t in auction.teams.values()
        ],
        current_caller=auction.current_caller.name if auction.current_caller else None,
        current_player=auction.current_player.name if auction.current_player else None,
    )
    await ws.send_json({"type": "auction_snapshot", "payload": snapshot.model_dump_json()})

    participant_id = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "ping":
                await ws.send_json({"type": "pong"})

            elif msg["type"] == "join":
                nickname = msg["payload"]["name"]
                participant = await auction.join(nickname)

                participant_id = participant.id
                manager.register(auction_id, participant_id, ws)

                await ws.send_json({
                    "type": "joined",
                    "payload": {"id": participant.id, "name": participant.name}
                })

                await manager.broadcast(
                    auction_id,
                    {
                        "type": "participant_joined",
                        "payload": {"id": participant.id, "name": participant.name},
                    }
                )

            else:
                # broadcast generico
                await manager.broadcast(auction_id, msg)

    except WebSocketDisconnect:
        if participant_id is not None:
            manager.unregister(auction_id, participant_id)
            await manager.broadcast(auction_id, {
                "type": "participant_left",
                "payload": {"id": participant_id}
            })
