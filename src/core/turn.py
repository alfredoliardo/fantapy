from typing import List, Optional
from core.bid import Bid
from core.bidder import IBidder
from core.bidding_strategies import BiddingStrategy
from core.caller import ICaller
from core.player import Player
from core.team import Team


class Turn:
    def __init__(
            self,
            number:int,
            caller: ICaller,
            player: Player,
            bidders: List[IBidder],
            bidding_strategy: BiddingStrategy
        ) -> None:
        self.number = number
        self.caller = caller
        self.player:Player = player
        self.bidders = bidders
        self.bidding_strategy:BiddingStrategy = bidding_strategy
        self.bids:List[Bid] = []
        self.winner:Optional[Bid] = None
        self.status = "not_started"
    
    async def start(self):
        """Avvia il turno e delega alla strategia di bidding"""
        self.winner = await self.bidding_strategy.run(
            player=self.player,
            bidders=self.bidders,
            turn=self
        )
        return self.winner

    def bid(self, bid:Bid):
        if self.status != "in_progress":
            raise Exception("Turn not in progress")
        
        self.bids.append(bid)