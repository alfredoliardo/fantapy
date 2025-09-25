from typing import Dict, List, Optional
from core.enums import PlayerRole
from core.player import Player


class Team:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.president = None  
        self.budget:float = 500
        self.spent:float= 0
        self.roster: List[Player] = []

    def add_player(self, player: Player, price: float) -> None:
        self.roster.append(player)

    # Utility robuste
    def has_player(self, player: Player) -> bool:
        return any(p.player_id == player.player_id for p in self.roster)

    def player_count(self, player: Player) -> int:
        return sum(1 for p in self.roster if p.player_id == player.player_id)

    def count_by_role(self, role: PlayerRole) -> int:
        return sum(1 for p in self.roster if p.role == role)

    def get_roster_by_role(self) -> Dict[PlayerRole, List[Player]]:
        grouped: Dict[PlayerRole, List[Player]] = {}
        for p in self.roster:
            grouped.setdefault(p.role, []).append(p)
        return grouped
    def can_afford(self, amount: float) -> bool:
        return (self.budget - self.spent) >= amount

    def __repr__(self) -> str:
        return f"<Team {self.name} spent={self.spent} size={len(self.roster)}>"