from abc import ABC, abstractmethod
from core.caller import Caller
from core.team import Team

class IParticipant(ABC):
    @property
    @abstractmethod
    def id(self) -> int: ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificativo del partecipante (sempre presente)."""
        pass

    @abstractmethod
    def get_label(self) -> str: ...

class GuestParticipant(IParticipant):
    """Partecipante osservatore o ospite (futuri use case)."""
    def __init__(self, id:int, username: str):
        self._id = id
        self._name = username
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def get_label(self) -> str:
        return f"Guest: {self._name}"

class IInteractiveParticipant(IParticipant):
    @property
    @abstractmethod
    def caller(self) -> Caller: ...
 

class HostParticipant(IInteractiveParticipant):
    def __init__(self, id, name):
        self._id = id
        self._name = name

    @property
    def id(self) -> int:
        return self._id
    @property
    def name(self) -> str:
        return self._name

    def get_label(self) -> str:
        return f"Host: {self._name}"

    @property
    def caller(self) -> Caller:
        raise NotImplementedError


class TeamParticipant(IInteractiveParticipant):
    """Partecipante associato a un Team reale."""

    def __init__(self, id:int, team: Team, caller: Caller):
        self._id = id
        self._team = team
        self._caller = caller

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._team.name
    
    @property
    def caller(self) -> Caller:
        return self._caller

    def get_label(self) -> str:
        return f"Team: {self._team.name}"
    
class AuctioneerParticipant(IInteractiveParticipant):
    """Il banditore/host, gestito centralmente."""

    def __init__(self, caller: Caller):
        self._caller = caller

    @property
    def caller(self) -> Caller:
        return self._caller

    def get_label(self) -> str:
        return "Auctioneer"

