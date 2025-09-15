from abc import ABC, abstractmethod
from typing import List, Optional
from core.auction import Auction
from core.caller import Caller


class CallingStrategy(ABC):
    def __init__(self,auction:Auction):
        self.auction = auction

    @abstractmethod
    def next_caller(self) -> Caller:
        """Restituisce chi deve chiamare il prossimo giocatore"""
        pass