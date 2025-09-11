from typing import Dict, List

from backend.models.enums import PlayerRole
from backend.models.player import Player
from core.caller import Caller, SystemCaller
from core.events import AuctionEvent, PlayerCalled, TurnStarted
from services.calling_strategy.base import CallingStrategy
from services.calling_strategy.sequential_calling_strategy import SequentialCallingStrategy
from services.slot_strategies.base import SlotValidationStrategy
from services.slot_strategies.default import DefaultSlotValidation


class Auction:
    def __init__(
        self,
        auction_id:str,
        name:str = "",
        calling_strategy:CallingStrategy = SequentialCallingStrategy(),
        initial_budget:float = 1000,
        participants:int = 8,
        slot_strategy:SlotValidationStrategy = DefaultSlotValidation()        
    ) -> None:
    
        self.auction_id = auction_id
        self.current_caller:Caller
        self.current_player:Player|None = None
        self.calling_strategy = calling_strategy
        self.player_pool:list[Player] = []
        self.callers:List[Caller] = [SystemCaller()]

    def _publish(self, event:AuctionEvent):
        pass

    def start_auction(self):
        self.next_turn()
        pass

    def next_turn(self):
        self.current_caller = self.calling_strategy.next_caller(self.callers)
        # pubblica evento turno iniziato
        self._publish(TurnStarted(caller=self.current_caller, payload={}))

        if(isinstance(self.current_caller, SystemCaller)):
            self.current_player = self.current_caller.choose_player(self.player_pool)
            if self.current_player:
                self._publish(PlayerCalled(player=self.current_player, payload={}))


    