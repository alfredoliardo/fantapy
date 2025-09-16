from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from .auctions import auctions

router = APIRouter()

class JoinAuction(BaseModel):
    auction_id: str
    username: str

@router.post("/join")
def join_auction(data: JoinAuction):
    auction = auctions.get(data.auction_id)
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    participant_id = f"{data.username}-{len(auction['participants'])+1}"
    participant = {"id": participant_id, "username": data.username, "team_id": None}
    auction["participants"].append(participant)
    return {"participant_id": participant_id, "auction": auction}
