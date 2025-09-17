from typing import List, Optional
from core.bid import Bid
from core.bidding_strategies import BiddingStrategy
from core.caller import Caller
from core.player import Player


class Turn:
    def __init__(self, number:int, caller:Caller, player:Player, bidding_strategy:BiddingStrategy) -> None:
        self.caller = caller
        self.player = player
        self.bidding_strategy = bidding_strategy
        self.bids:List[Bid] = []
        self.winner:Optional[Bid] = None
    
    def pass_turn(self):
        return

    def place_bid(self, bid:Bid):
        #TODO: validazione dell'offerta
        self.bids.append(bid)

    def close(self):
        return self.winner