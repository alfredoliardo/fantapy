from abc import ABC, abstractmethod
from typing import List, Optional

from core.player import Player



class Caller(ABC):
    def __init__(self, name:str):
        self.name = name
    
    @abstractmethod
    def choose_player(self, available_players: List[Player]) -> Optional[Player]:
        pass

class SystemCaller(Caller):
    def __init__(self):
        super().__init__("system")        
    
    def choose_player(self, available_players: List[Player]) -> Optional[Player]:
        import random
        return random.choice(available_players) if available_players else None
    
class TeamCaller(Caller):
    def __init__(self, team_name: str):
        super().__init__(team_name)

    def choose_player(self, available_players: List[Player]) -> Optional[Player]:
        # qui potresti usare input o logica web
        print(f"{self.name} deve scegliere un giocatore")
        return available_players[0] if available_players else None
    
class HostCaller(Caller):
    def __init__(self, host_name:str):
        super().__init__(host_name)
    
    def choose_player(self, available_players: List[Player]) -> Player | None:
        return super().choose_player(available_players)
