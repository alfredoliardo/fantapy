import random
from typing import List
from core.caller import Caller
from services.calling_strategy.base import CallingStrategy

class SequentialCallingStrategy(CallingStrategy):
    def __init__(self, clockwise: bool = True):
        self.index = -1
        self.clockwise = clockwise

    def next_caller(self, possible_callers: List[Caller]) -> Caller:
        if not possible_callers:
            return None # type: ignore
        step = 1 if self.clockwise else -1
        self.index = (self.index + step) % len(possible_callers)
        return possible_callers[self.index]