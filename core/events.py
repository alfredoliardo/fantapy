# core/events.py
from dataclasses import dataclass, field
from typing import Dict

from core.caller import Caller
from core.player import Player

@dataclass
class AuctionEvent:
    type: str
    payload: Dict = field(init=False)   # non viene richiesto all'init


@dataclass
class TurnStarted(AuctionEvent):
    caller: Caller = None
    type: str = field(init=False, default="turn_started")

    def __post_init__(self):
        self.payload = {"caller": self.caller.name}


@dataclass
class PlayerCalled(AuctionEvent):
    player: Player = None
    type: str = field(init=False, default="player_called")

    def __post_init__(self):
        self.payload = {"player": self.player.name, "role": self.player.role}

@dataclass
class BidPlaced(AuctionEvent):
    type: str = "bid_placed"
    team: str = ""
    amount: int = 0

    def __post_init__(self):
        self.payload = {"team": self.team, "amount": self.amount}


@dataclass
class PlayerAssigned(AuctionEvent):
    type: str = "player_assigned"
    team: str = ""
    player: str = ""

    def __post_init__(self):
        self.payload = {"team": self.team, "player": self.player}