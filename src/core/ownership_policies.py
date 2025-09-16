# auction/core/policies/ownership.py
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from core.player import Player
if TYPE_CHECKING:
    from core.team import Team

class OwnershipPolicy(ABC):
    @abstractmethod
    def can_own(self, team: "Team", player: Player) -> bool:
        """Se il team può possedere (ancora) questo giocatore, a prescindere dal prezzo."""
        ...

    # opzionale, utile per filtri bidding/UI
    def can_bid(self, team: "Team", player: Player) -> bool:
        return self.can_own(team, player)
# Nessun clone: massimo 1 per team
class NoDuplicatesOwnershipPolicy(OwnershipPolicy):
    def can_own(self, team: "Team", player: Player) -> bool:
        return not team.has_player(player)

# Modalità “pazza”: fino a N cloni per team
class MaxCopiesOwnershipPolicy(OwnershipPolicy):
    def __init__(self, max_copies_per_player: int):
        assert max_copies_per_player >= 1
        self.max_copies_per_player = max_copies_per_player

    def can_own(self, team: "Team", player: Player) -> bool:
        return team.player_count(player) < self.max_copies_per_player
