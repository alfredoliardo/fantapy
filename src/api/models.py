from pydantic import BaseModel
from typing import List, Optional

# --- Player ---
class PlayerDTO(BaseModel):
    id: int
    name: str
    role: str
    team_name: str


# --- Team ---
class TeamDTO(BaseModel):
    id: int
    name: str
    players: List[PlayerDTO]
    budget: float


# --- Participant ---
class ParticipantDTO(BaseModel):
    id: str
    name: str
    is_host: bool = False
    can_call: bool = False
    can_bid: bool = False
    assigned_teams: List[str] = []  # team ids a cui è associato


# --- Auction Core Snapshot ---
class AuctionDTO(BaseModel):
    id: str
    name: str
    teams: List[TeamDTO]
    current_caller: Optional[str] = None
    current_player: Optional[str] = None


# --- AuctionRoom Snapshot ---
class AuctionRoomDTO(BaseModel):
    auction: AuctionDTO
    participants: List[ParticipantDTO]
