from typing import Dict, List, Optional

from core.auctioneer import Auctioneer
from core.bid import Bid
from core.caller import Caller, SystemCaller
from core.events import AuctionEvent, BidPlaced, PlayerCalled, TurnStarted
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
        name:str = "",
        players:List[Player] = [],
        calling_strategy:CallingStrategy = SequentialCallingStrategy(),
        initial_budget:float = 1000,
        participants:int = 8,
        slot_strategy:SlotValidationStrategy = DefaultSlotValidation(),     
    ) -> None:
    
        self.auction_id = auction_id
        self.name = name
        self.initial_budget = initial_budget
        self.teams = [Team(team_id=i,name=f"Team {i+1}", budget=self.initial_budget) for i in range(participants)]
        self.player_pool:List[Player] = players


        self.current_caller:Optional[Caller] = None
        self.current_player:Optional[Player] = None
        self.current_bids:List[Bid] = []
        self.best_bid:Optional[Bid] = None

        self.calling_strategy = calling_strategy
        self.callers:List[Caller] = [SystemCaller()]
        self.subscribers = []

        self.auctioneer = Auctioneer(countdown_seconds=10, tick_callback=self._tick)
        self.auctioneer.on_finish = self._assign_player

    def subscribe(self, callback):
        self.subscribers.append(callback)
    def _publish(self, event: AuctionEvent):
            for cb in self.subscribers:
                cb(event)
 # ==== Auctioneer callbacks ====
    def _tick(self, remaining: int):
        # pubblichiamo evento countdown
        self._publish(AuctionEvent(type="tick", payload={"remaining": remaining}))

    def _assign_player(self, player: Player, team, amount: int):
        """Assegna giocatore al miglior offerente"""
        self._publish(
            AuctionEvent(
                type="player_assigned",
                payload={
                    "player": player.name,
                    "role": player.role,
                    "team": team.name if team else None,
                    "amount": amount,
                },
            )
        )
        # reset turn
        self.current_player = None
        self.current_bids.clear()
        self.best_bid = None

    def start_auction(self):
        self.next_turn()
        pass

    def next_turn(self):
        self.current_caller = self.calling_strategy.next_caller(self.callers)
        # pubblica evento turno iniziato
        self._publish(TurnStarted(caller=self.current_caller))

        if(isinstance(self.current_caller, SystemCaller)):
            self.current_player = self.current_caller.choose_player(self.player_pool)
            if self.current_player:
                self._publish(PlayerCalled(player=self.current_player))
                
    def place_bid(self, team: Team, amount: int) -> Optional[AuctionEvent]:
            if not self.current_player:
                return None
            if amount > self.current_bid and team.budget >= amount:
                self.current_bid = amount
                self.current_bidder = team
                return BidPlaced(team=team.name, amount=amount)
            return None
    