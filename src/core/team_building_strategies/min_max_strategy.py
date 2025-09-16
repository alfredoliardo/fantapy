from typing import Dict
from core.enums import PlayerRole
from core.team_building_strategies.base import TeamBuildingStrategy


class MinMaxStrategy(TeamBuildingStrategy):
    def __init__(self, min_slots: Dict[PlayerRole, int], max_slots: Dict[PlayerRole, int]):
        self.min_slots = min_slots
        self.max_slots = max_slots

    def can_assign(self, team, player, price):
        current = team.count_by_role(player.role)
        return current < self.max_slots[player.role] and team.budget >= price

    def is_complete(self, team):
        # tutti i minimi rispettati e non eccedono massimi
        for r in self.min_slots:
            if team.count_by_role(r) < self.min_slots[r]:
                return False
        for r in self.max_slots:
            if team.count_by_role(r) > self.max_slots[r]:
                return False
        return True

    def roles_remaining(self, team):
        return {r: max(0, self.min_slots[r] - team.count_by_role(r)) for r in self.min_slots}
