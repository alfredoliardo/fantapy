from abc import ABC, abstractmethod


# core/bidder.py
from abc import ABC, abstractmethod
from typing import Optional
from core.team import Team
from core.player import Player
from core.bid import Bid


class IBidder(ABC):
    @property
    @abstractmethod
    def team(self) -> Optional[Team]:
        """Restituisce la squadra per cui il bidder opera"""
        pass

    @abstractmethod
    async def get_bid(self, player: Player) -> Optional[float]:
        """Chiede in modo asincrono un'eventuale offerta da parte del bidder"""
        pass
    @abstractmethod
    def place_bid(self, player: Player, amount: float) -> Bid:
        """Crea un'offerta valida per il giocatore"""
        pass
