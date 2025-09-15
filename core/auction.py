from typing import Dict, List, Optional
from core.bid import Bid
from core.caller import Caller
from core.events import AuctionEvent, AuctionStarted, BidPlaced, PlayerCalled, TurnStarted
from core.player import Player
from core.team import Team
from services.calling_strategy.base import CallingStrategy
from services.calling_strategy.sequential_calling_strategy import SequentialCallingStrategy
from services.slot_strategies.base import SlotValidationStrategy
from services.slot_strategies.default import DefaultSlotValidation


class Auction:
    def __init__(
        self,
        auction_id:str,
        calling_strategy:CallingStrategy,
        name:str = "",
        participants:int = 8,
        initial_budget:float = 1000,
        players:List[Player] = [],
        slot_strategy:SlotValidationStrategy = DefaultSlotValidation(),     
    ) -> None:
    
        self.auction_id = auction_id
        self.name = name
        self.teams = [Team(team_id=i,name=f"Team {i+1}", budget=self.initial_budget) for i in range(participants)]
        self.initial_budget = initial_budget
        self.player_pool:List[Player] = players


        self.current_caller:Optional[Caller] = None
        self.current_player:Optional[Player] = None
        self.current_bids:List[Bid] = []
        self.best_bid:Optional[Bid] = None

        self.calling_strategy = calling_strategy
        self.callers = []
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def _publish(self, event: AuctionEvent):
            for cb in self.subscribers:
                cb(event)

    async def start_auction(self):
        self._publish(AuctionStarted(self))
        await self.next_turn()
        pass

    async def next_turn(self):
        #seleziona il prossimo chiamante
        self.current_caller = self.calling_strategy.next_caller()
        self._publish(TurnStarted(caller=self.current_caller))

        #qui si potrebbe implementare la logica per preparare la player_pool

        #il chiamante seleziona un giocatore da mettere all'asta
        self.current_player = await self.current_caller.choose_player(self.player_pool)

                
    def place_bid(self, team: Team, amount: int) -> Optional[AuctionEvent]:
            if not self.current_player:
                return None
            if amount > self.current_bid and team.budget >= amount:
                self.current_bid = amount
                self.current_bidder = team
                return BidPlaced(team=team.name, amount=amount)
            return None
    