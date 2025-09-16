from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
import uuid

router = APIRouter()

# In-memory storage per demo
auctions: Dict[str, dict] = {}

class AuctionCreate(BaseModel):
    name: str
    budget: int
    max_teams: int

@router.post("/")
def create_auction(data: AuctionCreate):
    auction_id = str(uuid.uuid4())
    auctions[auction_id] = {
        "id": auction_id,
        "name": data.name,
        "budget": data.budget,
        "max_teams": data.max_teams,
        "participants": [],
    }
    return {"auction_id": auction_id}
