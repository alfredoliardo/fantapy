
from abc import ABC, abstractmethod
import random
from typing import List, Optional

from core.player import Player


class SelectionStrategy:
    def select_player(self, available_players: List[str]) -> Optional[str]:
        raise NotImplementedError


class RandomSelectionStrategy(SelectionStrategy):
    def select_player(self, available_players: List[str]) -> Optional[str]:
        return random.choice(available_players) if available_players else None


class AlphabeticalSelectionStrategy(SelectionStrategy):
    def select_player(self, available_players: List[str]) -> Optional[str]:
        return sorted(available_players)[0] if available_players else None