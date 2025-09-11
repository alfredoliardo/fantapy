from abc import ABC, abstractmethod

from core.player import Player
from core.team import Team


class SlotValidationStrategy(ABC):
    @abstractmethod
    def can_add_player(self, team: Team, player: Player) -> bool:
        """Ritorna True se il giocatore può essere aggiunto al team secondo la regola."""
        pass

    @abstractmethod
    def describe_rule(self) -> str:
        """Descrive la regola per logging o UI."""
        pass
