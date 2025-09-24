from abc import ABC, abstractmethod
from typing import List
from core.caller import ICaller

class CallingStrategy(ABC):

    @abstractmethod
    def next_caller(self) -> List[ICaller]:
        """Restituisce l'entità che deve chiamare il prossimo giocatore"""
        pass