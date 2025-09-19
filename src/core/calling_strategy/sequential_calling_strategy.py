import random
from typing import List
from core.calling_strategy.base import CallingStrategy
from core.team import Team

class SequentialCallingStrategy(CallingStrategy):
    def __init__(self, teams:List[Team], clockwise: bool = True):
        self.index = random.randint(0, len(teams)-1)
        self.clockwise = clockwise
        self.teams = teams

    def next_caller(self) -> Team:        
        step = 1 if self.clockwise else -1

        self.index = (self.index + step) % len(self.teams)
        return self.teams[self.index]