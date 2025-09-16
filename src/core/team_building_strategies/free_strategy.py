from core.team_building_strategies.base import TeamBuildingStrategy


class FreeStrategy(TeamBuildingStrategy):
    def can_assign(self, team, player, price):
        return team.budget >= price

    def is_complete(self, team):
        return False  # finisce solo quando pool esaurito o host decide

    def roles_remaining(self, team):
        return {}
