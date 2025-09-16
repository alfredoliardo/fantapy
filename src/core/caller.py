from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import WebSocket

from core.player import Player



class Caller(ABC):
    """Entità che può chiamare un giocatore all'asta."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name
    
    @abstractmethod
    async def choose_player(self, player_pool:List[Player]) -> Optional[Player]:
        pass

class WebSocketCaller(Caller):
    def __init__(self, name: str, websocket: WebSocket):
        super().__init__(name)
        self.websocket = websocket

    async def choose_player(self, player_pool: List[Player]) -> Optional[Player]:
        # Mando la richiesta al client remoto
        await self.websocket.send_json({
            "type": "choose_player",
            "options": player_pool
        })
        # Aspetto la risposta del client
        data = await self.websocket.receive_json()

        return data.get("player")