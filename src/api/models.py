from typing import List, Optional
from pydantic import BaseModel


class PlayerDTO(BaseModel):
    id: int
    name: str
    role: str
    team_name: str

class TeamDTO(BaseModel):
    id: str
    name: str
    budget: float
    players: List[PlayerDTO]

class AuctionDTO(BaseModel):
    id: str
    name: str
    participants: List[str]
    teams: List[TeamDTO]
    current_caller: Optional[str] = None
    current_player: Optional[str] = None
