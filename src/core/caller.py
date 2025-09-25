from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import WebSocket

from core.bidding_strategies import BiddingStrategy
from core.player import Player



class ICaller(ABC):
    """Entità che può chiamare un giocatore all'asta."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name
    
    @abstractmethod
    async def choose_player(self, player_pool:List[Player]) -> Optional[Player]:
        pass