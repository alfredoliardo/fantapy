from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List
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
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, auction_id: str, ws: WebSocket):
        await ws.accept()
        if auction_id not in self.active:
            self.active[auction_id] = []
        self.active[auction_id].append(ws)

    def disconnect(self, auction_id: str, ws: WebSocket):
        if auction_id in self.active and ws in self.active[auction_id]:
            self.active[auction_id].remove(ws)

    async def broadcast(self, auction_id: str, message: dict):
        if auction_id not in self.active:
            return
        dead = []
        for ws in self.active[auction_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(auction_id, ws)


manager = ConnectionManager()


# --- ROUTES ---

@router.post("/")
def create_auction(data: AuctionCreate):
    auction_id = str(uuid.uuid4())
    auction = Auction(
        auction_id=auction_id,
        auction_name=data.name,
        host_name=data.nickname,
        # budget_strategy e altro ancora possono essere passati in futuro
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
async def auction_ws(ws: WebSocket, auction_id: str, nickname:str):
    if auction_id not in auctions:
        await ws.close(code=1008)  # policy violation
        return

    await manager.connect(auction_id, ws)
    auction = auctions[auction_id]

    # Invia subito snapshot iniziale al nuovo client
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
    await ws.send_json({"type": "auction_snapshot", "payload": snapshot.dict()})

    # Broadcast a tutti che è entrato un nuovo client
    await manager.broadcast(auction_id, {
        "type": "participant_joined",
        "payload": {"id": "temp", "name": nickname}
    })

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            # Qui puoi gestire i messaggi dei client
            # Es: {"type": "place_bid", "amount": 50}
            if msg["type"] == "ping":
                await ws.send_json({"type": "pong"})
            else:
                await manager.broadcast(auction_id, msg)

    except WebSocketDisconnect:
        manager.disconnect(auction_id, ws)
        await manager.broadcast(auction_id, {
            "type": "participant_left",
            "payload": {"id": "temp", "name": "anonymous"}
        })
