import random
from typing import Dict, List
from core.caller import ICaller
from core.calling_strategy.base import CallingStrategy
from core.team import Team

class SequentialTeamCallingStrategy(CallingStrategy):
    def __init__(self, team_callers:Dict[Team, ICaller], clockwise: bool = True):
        self.index = random.randint(0, len(team_callers)-1)
        self.clockwise = clockwise
        self.team_callers = team_callers

    def next_caller(self) -> List[ICaller]:        
        step = 1 if self.clockwise else -1

        self.index = (self.index + step) % len(self.teams)
        return self.teams[self.index]