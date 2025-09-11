from abc import ABC, abstractmethod
from typing import List, Optional

from backend.models.player import Player
from core.caller import Caller


class CallingStrategy(ABC):
    @abstractmethod
    def next_caller(self, possible_callers: List[Caller]) -> Caller:
        """Restituisce chi deve chiamare il prossimo giocatore"""
        pass