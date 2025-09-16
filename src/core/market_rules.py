from abc import ABC, abstractmethod
from typing import List

from core.player import Player
from core.team import Team

class MarketRule(ABC):
    @abstractmethod
    def is_available(self, player: Player) -> bool:
        """C'è ancora disponibilità globale del player?"""
        ...

    @abstractmethod
    def register_assignment(self, team: Team, player: Player) -> None:
        ...

    # helper per pool/bidding
    def available_for_any_team(self, player: Player, teams: List[Team]) -> bool:
        if not self.is_available(player):
            return False
        # delega all’ownership per-team
        return any(t.ownership_policy.can_own(t, player) for t in teams)

class UniquePlayerMarket(MarketRule):
    def __init__(self):
        self.assigned: set[int] = set()

    def is_available(self, player: Player) -> bool:
        return player.player_id not in self.assigned

    def register_assignment(self, team: Team, player: Player) -> None:
        self.assigned.add(player.player_id)

class MultiCopyMarket(MarketRule):
    def __init__(self, max_copies: int):
        self.max_copies = max_copies
        self.counts: dict[int, int] = {}

    def is_available(self, player: Player) -> bool:
        return self.counts.get(player.player_id, 0) < self.max_copies

    def register_assignment(self, team: Team, player: Player) -> None:
        self.counts[player.player_id] = self.counts.get(player.player_id, 0) + 1