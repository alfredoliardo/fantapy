from abc import ABC, abstractmethod

from core.enums import PlayerRole
from core.player import Player
from core.team import Team


class TeamBuildingStrategy(ABC):
    @abstractmethod
    def can_assign(self, team: Team, player: Player, price: int) -> bool: ...
    @abstractmethod
    def is_complete(self, team: Team) -> bool: ...
    @abstractmethod
    def roles_remaining(self, team: Team) -> dict[PlayerRole, int]: ...