from typing import List
from core.enums import PlayerRole
from core.player_pool_builders.base import PlayerPoolBuilder
from core.team_building_strategies.base import TeamBuildingStrategy


class RoleSequentialPoolBuilder(PlayerPoolBuilder):
    def __init__(self, role_order: list[PlayerRole], team_building: TeamBuildingStrategy):
        self.role_order = role_order
        self.current_role_index = 0
        self.team_building = team_building

    def build_pool(self, all_players, teams):
        role = self.role_order[self.current_role_index]
        candidates = [p for p in all_players if p.role == role]

        # escludi giocatori che nessun team potrebbe assegnarsi
        valid = [
            p for p in candidates
            if any(self.team_building.can_assign(t, p, 1) for t in teams)
        ]

        if not valid:
            # passa al ruolo successivo
            self.current_role_index += 1
            return self.build_pool(all_players, teams)

        return valid
