from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from typing import Dict, List

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in sviluppo apri tutto, poi restringi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stato in memoria (MVP, poi SQLite)
auctions: Dict[str, dict] = {}
connections: Dict[str, List[WebSocket]] = {}

@app.post("/create_auction")
async def create_auction(params: dict):
    auction_id = f"auction_{len(auctions)+1}"
    auctions[auction_id] = {
        "params": params,
        "participants": {},
        "current_player": None,
        "bids": [],
        "status": "waiting"
    }
    connections[auction_id] = []
    return {"auction_id": auction_id}

@app.websocket("/ws/{auction_id}/{user}")
async def websocket_endpoint(ws: WebSocket, auction_id: str, user: str):
    await ws.accept()
    connections[auction_id].append(ws)
    try:
        while True:
            data = await ws.receive_json()
            if data["type"] == "join":
                auctions[auction_id]["participants"][user] = {
                    "budget": auctions[auction_id]["params"].get("budget", 500),
                    "squad": []
                }
                await broadcast(auction_id, {"type": "user_joined", "user": user})

            elif data["type"] == "start_player":
                player = data["player"]
                auctions[auction_id]["current_player"] = player
                auctions[auction_id]["bids"] = []
                await broadcast(auction_id, {"type": "player_started", "player": player})

            elif data["type"] == "bid":
                bid = {"user": user, "amount": data["amount"]}
                auctions[auction_id]["bids"].append(bid)
                await broadcast(auction_id, {"type": "new_bid", "bid": bid})

            elif data["type"] == "end_player":
                # assegna al miglior offerente
                if auctions[auction_id]["bids"]:
                    winner = max(auctions[auction_id]["bids"], key=lambda x: x["amount"])
                    auctions[auction_id]["participants"][winner["user"]]["budget"] -= winner["amount"]
                    auctions[auction_id]["participants"][winner["user"]]["squad"].append({
                        "player": auctions[auction_id]["current_player"],
                        "price": winner["amount"]
                    })
                    await broadcast(auction_id, {"type": "player_assigned", "winner": winner})
                auctions[auction_id]["current_player"] = None
                auctions[auction_id]["bids"] = []
    except WebSocketDisconnect:
        connections[auction_id].remove(ws)

async def broadcast(auction_id: str, message: dict):
    for conn in connections[auction_id]:
        await conn.send_json(message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
