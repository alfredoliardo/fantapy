# core/bid.py
from dataclasses import dataclass

from core.player import Player
from core.team import Team

@dataclass
class Bid:
    team: Team
    amount: int
    player: Player
