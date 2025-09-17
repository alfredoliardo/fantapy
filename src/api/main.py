<<<<<<< HEAD
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routers import auctions
# Path assoluto basato sulla posizione di questo file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    raise RuntimeError(f"Frontend directory not found: {FRONTEND_DIR}")

app = FastAPI()

# Routers
app.include_router(auctions.router, prefix="/auctions", tags=["auctions"])

# Static frontend
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# WebSocket router
=======
from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uuid
import json

from core.auction import Auction

app = FastAPI()

# Configura CORS
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auctions: Dict[str, Auction] = {}
connections: Dict[str, List[WebSocket]] = {}

@app.post("/auctions/{auction_id}/assign")
async def assign_team(auction_id: str, participant_id: int = Body(...), team_id: int = Body(...)):
    if auction_id not in auctions:
        return {"error": "Auction not found"}
    
    auction = auctions[auction_id]
    team = auction.teams.get(team_id)
    participant = auction.participants.get(participant_id)

    if not team or not participant:
        return {"error": "Invalid participant or team"}
    
    await auction.assign_team(participant_id, team, caller=None)  # type: ignore # TODO: definire caller default

    # broadcast
    for conn in connections[auction_id]:
        await conn.send_json({
            "type": "team_assigned",
            "payload": {
                "participant_id": participant_id,
                "participant_name": participant.name,
                "team_id": team_id,
                "team_name": team.name
            }
        })
    
    return {"ok": True}

@app.post("/auctions")
async def create_auction(name: str, host_name: str):
    auction_id = str(uuid.uuid4())
    auction = Auction(auction_id, name, host_name)
    auctions[auction_id] = auction
    connections[auction_id] = []
    return {"auction_id": auction_id}

@app.websocket("/ws/{auction_id}/{nickname}")
async def websocket_endpoint(ws: WebSocket, auction_id: str, nickname: str):
    await ws.accept()

    if auction_id not in auctions:
        await ws.send_json({"error": "Auction not found"})
        await ws.close()
        return

    auction = auctions[auction_id]
    participant = await auction.join(nickname)

    payload = {"id": participant.id, "name": nickname}

    # invia conferma al nuovo client
    await ws.send_json({
        "type": "joined",
        "payload": payload
    })

    # invia participant_joined anche al nuovo client
    await ws.send_json({
        "type": "participant_joined",
        "payload": payload
    })

    # broadcast agli altri
    for conn in connections[auction_id]:
        await conn.send_text(json.dumps({
            "type": "participant_joined",
            "payload": payload
        }))

    connections[auction_id].append(ws)
>>>>>>> 5929443 (turn)
