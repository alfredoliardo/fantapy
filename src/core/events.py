# core/events.py
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AuctionEvent:
    type: str
    payload: Dict = field(init=False)  # popolato in __post_init__ dai figli


@dataclass
class AuctionStarted(AuctionEvent):
    auction_id: str
    type: str = field(init=False, default="auction_started")

    def __post_init__(self):
        self.payload = {"auction_id": self.auction_id}


@dataclass
class ParticipantJoined(AuctionEvent):
    participant_id: int
    name: str
    type: str = field(init=False, default="participant_joined")

    def __post_init__(self):
        self.payload = {"id": self.participant_id, "name": self.name}


@dataclass
class TurnStarted(AuctionEvent):
    caller_name: str
    type: str = field(init=False, default="turn_started")

    def __post_init__(self):
        self.payload = {"caller": self.caller_name}


@dataclass
class PlayerCalled(AuctionEvent):
    player_id: str
    player_name: str
    role: str
    type: str = field(init=False, default="player_called")

    def __post_init__(self):
        self.payload = {
            "player_id": self.player_id,
            "player": self.player_name,
            "role": self.role,
        }


@dataclass
class BidPlaced(AuctionEvent):
    team_id: str
    team_name: str
    amount: int
    type: str = field(init=False, default="bid_placed")

    def __post_init__(self):
        self.payload = {
            "team_id": self.team_id,
            "team": self.team_name,
            "amount": self.amount,
        }


@dataclass
class PlayerAssigned(AuctionEvent):
    team_id: str
    team_name: str
    player_id: str
    player_name: str
    type: str = field(init=False, default="player_assigned")

    def __post_init__(self):
        self.payload = {
            "team_id": self.team_id,
            "team": self.team_name,
            "player_id": self.player_id,
            "player": self.player_name,
        }
