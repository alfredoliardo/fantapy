# core/player_pool.py
from typing import List, Optional
from core.player import Player, PlayerRole
from core.team import Team


class PlayerPool:
    def __init__(self, players: Optional[List[Player]] = None, allow_duplicates: bool = False):
        self.players: List[Player] = players or []
        self.allow_duplicates = allow_duplicates
        self.assigned_players: dict[int, List[int]] = {}  # player_id -> [team_id]

    def add_player(self, player: Player):
        self.players.append(player)

    def add_players(self, players: List[Player]):
        self.players.extend(players)

    def get_all(self) -> List[Player]:
        return list(self.players)

    def get_by_role(self, role: PlayerRole) -> List[Player]:
        return [p for p in self.players if p.role == role]

    def get_available(self) -> List[Player]:
        """Ritorna i giocatori non ancora assegnati, o gestiti con duplicati se permesso."""
        if self.allow_duplicates:
            return self.players
        else:
            return [p for p in self.players if p.player_id not in self.assigned_players]

    def assign_to_team(self, player: Player, team: Team, price:Optional[float]=None) -> bool:
        """Tenta di assegnare un giocatore a un team. Ritorna True se l’assegnazione va a buon fine."""
        if not self.allow_duplicates and player.player_id in self.assigned_players:
            return False

        if player.player_id not in self.assigned_players:
            self.assigned_players[player.player_id] = []

        # evita che lo stesso team abbia due volte lo stesso giocatore
        if team.id in self.assigned_players[player.player_id]:
            return False

        self.assigned_players[player.player_id].append(team.id)
        team.add_player(player, price if price is not None else 0)
        return True

    def is_available_for_team(self, player: Player, team: Team) -> bool:
        """Controlla se un player può essere assegnato al team (regole duplicate incluse)."""
        if not self.allow_duplicates and player.player_id in self.assigned_players:
            return False
        if player.player_id in self.assigned_players and team.id in self.assigned_players[player.player_id]:
            return False
        return True
