from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict
import uuid
import json

from api.auction_room import AuctionRoom
from api.models import AuctionDTO, AuctionRoomDTO, ParticipantDTO, PlayerDTO, TeamDTO
from api.remote_participant import RemoteParticipant
from core.auction import Auction
from core.team import Team

router = APIRouter()

# In-memory storage per demo
auctions: Dict[str, AuctionRoom] = {}

class AuctionCreate(BaseModel):
    name: str
    nickname: str
    budget: int
    max_teams: int


# --- ROUTES ---

@router.post("/")
def create_auction(data: AuctionCreate):
    auction_id = str(uuid.uuid4())
    auction = Auction(
        auction_id=auction_id,
        auction_name=data.name
    )
    auctions[auction_id] = AuctionRoom(auction)

    return {"auction_id": auction_id, "join_url": f"/auctions/{auction_id}/ws"}


@router.get("/{auction_id}", response_model=AuctionDTO)
def get_auction(auction_id: str):
    if auction_id not in auctions:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction = auctions[auction_id].auction

    auction_room = auctions[auction_id]
    return AuctionRoomDTO(
        auction=AuctionDTO(
            id=auction_room.auction.auction_id,
            name=auction_room.auction.name,
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
                for t in auction_room.auction.teams.values()
            ]
        ),
        participants=[
            ParticipantDTO(
                id=p.id,
                name=p.name
            )
            for p in auction_room.connections
        ]
    )


@router.websocket("/{auction_id}/ws")
async def auction_ws(ws: WebSocket, auction_id: str):
    if auction_id not in auctions:
        await ws.close(code=1008)  # policy violation
        return

    await ws.accept()
    auction_room = auctions[auction_id]
    auction = auction_room.auction

    # Invia subito snapshot iniziale
    snapshot = AuctionRoomDTO(
        auction=AuctionDTO(
            id=auction_room.auction.auction_id,
            name=auction_room.auction.name,
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
                for t in auction_room.auction.teams.values()
            ]
        ),
        participants=[
            ParticipantDTO(
                id=p.id,
                name=p.name
            )
            for p in auction_room.connections
        ]
    )
    await ws.send_json({"type": "auction_snapshot", "payload": snapshot.model_dump_json()})

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "join":
                nickname = msg["payload"]["name"]
                new_id = str(uuid.uuid4())
                participant = RemoteParticipant(new_id,nickname, ws)

                auction_room.join(participant)

                

                await ws.send_json({
                    "type": "joined",
                    "payload": {"id": participant.id, "name": participant.name}
                })

                await auction_room.broadcast({
                        "type": "participant_joined",
                        "payload": {"id": participant.id, "name": participant.name},
                })

            else:
                await auction_room.broadcast(msg)

    except WebSocketDisconnect:
        ...
