from abc import ABC, abstractmethod
from typing import List, Optional
from core.caller import Caller


class CallingStrategy(ABC):
    def __init__(self,callers:List[Caller]):
        self.callers = callers

    @abstractmethod
    def next_caller(self) -> Caller:
        """Restituisce chi deve chiamare il prossimo giocatore"""
        pass