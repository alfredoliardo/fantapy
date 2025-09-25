from pydantic import BaseModel, Field
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
    participants: List["ParticipantDTO"] = Field(default_factory=list)


# --- Participant ---
class ParticipantDTO(BaseModel):
    id: str
    name: str
    is_host: bool = False
    can_call: bool = False
    can_bid: bool = False
    assigned_teams: List[str] = Field(default_factory=list)  # team ids a cui è associato


# --- Auction Core Snapshot ---
class AuctionDTO(BaseModel):
    id: str
    name: str
    teams: List[TeamDTO]
    current_caller: Optional[str] = None
    current_player: Optional[str] = None
    started: bool = False


# --- AuctionRoom Snapshot ---
class AuctionRoomDTO(BaseModel):
    auction: AuctionDTO
    participants: List[ParticipantDTO]


TeamDTO.model_rebuild()
ParticipantDTO.model_rebuild()
AuctionDTO.model_rebuild()
AuctionRoomDTO.model_rebuild()
