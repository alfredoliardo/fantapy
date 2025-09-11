from .enums import PlayerRole

class Player:
    def __init__(self, player_id: int, name: str, role: PlayerRole, realTeam: str):
        self.player_id = player_id
        self.name = name
        self.role = role
        self.realTeam = realTeam

    def __repr__(self):
        return f"<Player {self.player_id}: {self.name} ({self.role.name})>"
