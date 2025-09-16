from typing import Dict, List, Optional
from core.budget_strategies import BudgetStrategy
from core.enums import PlayerRole
from core.ownership_policies import OwnershipPolicy
from core.player import Player


class Team:
    def __init__(self, team_id: str, name: str,
                 budget_strategy: BudgetStrategy,
                 ownership_policy: OwnershipPolicy):
        self.id = team_id
        self.name = name
        self.spent:float= 0
        self.roster: List[Player] = []
        self.budget_strategy = budget_strategy
        self.ownership_policy = ownership_policy

    def add_player(self, player: Player, price: float) -> None:
        # 👇 Delego ai policy, NON hardcode
        if not self.ownership_policy.can_own(self, player):
            raise ValueError(f"{self.name} non può possedere altre copie di {player.name}")
        if not self.budget_strategy.can_afford(self, player, price):
            raise ValueError(f"{self.name} non può permettersi {player.name} a {price}")

        self.roster.append(player)
        self.budget_strategy.apply_purchase(self, player, price)

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

    def __repr__(self) -> str:
        return f"<Team {self.name} spent={self.spent} size={len(self.roster)}>"