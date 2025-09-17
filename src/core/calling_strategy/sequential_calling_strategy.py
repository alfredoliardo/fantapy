import random
from typing import List

from fastapi import WebSocket
from core.caller import Caller, WebSocketCaller
from core.calling_strategy.base import CallingStrategy

class SequentialCallingStrategy(CallingStrategy):
    def __init__(self, ws:WebSocket, clockwise: bool = True):
        self.index = -1
        self.clockwise = clockwise

    def next_caller(self) -> Caller:
        if not self.callers:
            return None # type: ignore
        step = 1 if self.clockwise else -1
        self.index = (self.index + step) % len(self.callers)
        return self.callers[self.index]