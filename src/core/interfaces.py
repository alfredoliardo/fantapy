from abc import ABC, abstractmethod
from typing import List

from core.bidding_strategies import BiddingStrategy
from core.caller import ICaller
from core.player import Player


class IHost(ICaller, ABC):
    """Entità che gestisce l'asta."""
    
    @abstractmethod
    def announce(self, message: str) -> None:
        """Annuncia un messaggio a tutti i partecipanti"""
        pass

    async def choose_player(self, player_pool: List[Player]) -> Player | None:
        raise NotImplementedError

    async def choose_bidding_strategy(self) -> BiddingStrategy:
        raise NotImplementedError
