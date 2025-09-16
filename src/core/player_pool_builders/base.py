from abc import ABC, abstractmethod
from typing import List

from core.player import Player
from core.team import Team

class PlayerPoolBuilder(ABC):
    @abstractmethod
    def build_pool(self, all_players: List[Player], teams: List[Team]) -> List[Player]:
        """Ritorna la lista di giocatori selezionabili in questo turno"""
        pass
