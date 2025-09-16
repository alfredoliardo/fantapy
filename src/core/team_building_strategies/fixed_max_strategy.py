from typing import Dict

from core.enums import PlayerRole
from core.team_building_strategies.base import TeamBuildingStrategy


class FixedMaxStrategy(TeamBuildingStrategy):
    def __init__(self, max_slots: Dict[PlayerRole, int]):
        self.max_slots = max_slots

    def can_assign(self, team, player, price):
        current = team.count_by_role(player.role)
        return current < self.max_slots[player.role] and team.budget >= price

    def is_complete(self, team):
        return all(team.count_by_role(r) >= m for r, m in self.max_slots.items())

    def roles_remaining(self, team):
        return {r: max(0, m - team.count_by_role(r)) for r, m in self.max_slots.items()}
