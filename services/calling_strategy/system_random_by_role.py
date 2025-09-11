import random
from typing import List, Optional
from core.caller import Caller
from core.enums import PlayerRole
from core.player import Player
from services.calling_strategy.base import CallingStrategy


class RandomByRoleStrategy(CallingStrategy):
    def __init__(self, role: PlayerRole):
        self.role = role
    
    def next_caller(self, possible_callers: List[Caller]) -> Caller:
        return super().next_caller(possible_callers)

    def select_next_player(self, available_players: List[Player]) -> Optional[Player]:
        candidates = [p for p in available_players if p.role == self.role]
        return random.choice(candidates) if candidates else None
