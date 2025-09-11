import random
from typing import List, Optional
from core.player import Player
from services.calling_strategy.base import CallingStrategy


class RandomAnyRoleStrategy(CallingStrategy):
    def select_next_player(self, available_players: List[Player]) -> Optional[Player]:
        return random.choice(available_players) if available_players else None