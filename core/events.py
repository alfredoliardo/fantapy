from dataclasses import dataclass, field
from typing import Optional, Dict

from backend.models.player import Player
from core.caller import Caller, SystemCaller


@dataclass
class AuctionEvent:
    type: str
    payload: Dict


@dataclass
class TurnStarted(AuctionEvent):
    caller: Caller = field(default_factory=SystemCaller)
    type: str = "turn_started"

    def __post_init__(self):
        self.payload = {"caller": self.caller.name}


@dataclass
class PlayerCalled(AuctionEvent):
    player: Player
    type: str = "player_called"

    def __post_init__(self):
        self.payload = {"player": self.player.name, "role": self.player.role.name}
