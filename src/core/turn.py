from typing import List, Optional
from core.bid import Bid
from core.bidding_strategies import BiddingStrategy
from core.caller import Caller
from core.player import Player
from core.team import Team


class Turn:
    def __init__(self, number:int, caller:Team) -> None:
        self.number = number
        self.caller = caller
        self.player:Optional[Player] = None
        self.bidding_strategy:Optional[BiddingStrategy] = None
        self.bids:List[Bid] = []
        self.winner:Optional[Bid] = None
        self.status = "not_started"
    
    def skip(self):
        self.status = "passed"

    def call(self, player:Player, amount:float = 0):
        self.player = player
        self.status = "in_progress"

    def bid(self, bid:Bid):
        if self.status != "in_progress":
            raise Exception("Turn not in progress")
        
        self.bids.append(bid)