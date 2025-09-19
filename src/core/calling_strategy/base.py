from abc import ABC, abstractmethod
from core.team import Team


class CallingStrategy(ABC):

    @abstractmethod
    def next_caller(self) -> Team:
        """Restituisce quale team deve chiamare il prossimo giocatore"""
        pass