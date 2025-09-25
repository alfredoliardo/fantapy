from typing import List

from core.caller import ICaller
from core.calling_strategy.base import CallingStrategy


class SequentialCallingStrategy(CallingStrategy):
    """Strategia semplice: scorre ciclicamente la lista dei caller."""

    def __init__(self, callers: List[ICaller]):
        if not callers:
            raise ValueError("At least one caller is required")
        self._callers: List[ICaller] = callers
        self._index = -1

    def next_caller(self) -> List[ICaller]:
        if not self._callers:
            return []
        self._index = (self._index + 1) % len(self._callers)
        return [self._callers[self._index]]

    def update_callers(self, callers: List[ICaller]) -> None:
        self._callers = callers
        self._index = -1

    @property
    def callers(self) -> List[ICaller]:
        return list(self._callers)
