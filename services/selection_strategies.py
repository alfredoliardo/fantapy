# strategies/selection_strategy.py
from abc import ABC, abstractmethod
from typing import List, Optional
import random

from backend.models.enums import PlayerRole
from backend.models.player import Player

class SelectionStrategy(ABC):
    @abstractmethod
    def select_player(self, available_players: List[Player]) -> Optional[Player]:
        pass

class RandomSelection(SelectionStrategy):
    def select_player(self, available_players: List[Player]) -> Optional[Player]:
        return random.choice(available_players) if available_players else None

class AlphabeticalSelection(SelectionStrategy):
    def select_player(self, available_players: List[Player]) -> Optional[Player]:
        return sorted(available_players, key=lambda p: p.name)[0] if available_players else None
