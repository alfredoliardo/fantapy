from typing import Dict, List, Optional
from core.auctioneer import IAuctioneer
from core.bid import Bid
from core.caller import Caller
from core.calling_strategy.base import CallingStrategy
from core.enums import PlayerRole
from core.events import AuctionEvent, AuctionStarted, BidPlaced, ParticipantJoined, PlayerCalled, TurnStarted
from core.participant import GuestParticipant, IParticipant, TeamParticipant
from core.player import Player
from core.slot_strategies.base import SlotValidationStrategy
from core.slot_strategies.default import DefaultSlotValidation
from core.team import Team


class Auction:
    def __init__(
        self,
        auction_id:str,
        name:str,        
        participants:int = 8,
        initial_budget:float = 1000,
        players:List[Player] = [
             Player(1,"Davis K.", PlayerRole.A, "Udinese"),
             Player(2,"Paz N.", PlayerRole.C, "Como"),
             Player(3,"Mina", PlayerRole.D, "Cagliari"),
             Player(4,"Svilar", PlayerRole.P, "Roma"),
        ],
        slot_strategy:SlotValidationStrategy = DefaultSlotValidation(),     
    ) -> None:
    
        
        self.participants:Dict[int,IParticipant] = {}
        self.auction_id = auction_id
        self.name = name

        self.teams = [Team(team_id=i,name=f"Team {i+1}", budget=self.initial_budget) for i in range(participants)]

        self.initial_budget = initial_budget
        self.player_pool:List[Player] = players


        self.current_caller:Optional[Caller] = None
        self.current_player:Optional[Player] = None
        self.current_bids:List[Bid] = []
        self.best_bid:Optional[Bid] = None

        #self.calling_strategy = calling_strategy
        self.callers = []
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def _publish(self, event: AuctionEvent):
            for cb in self.subscribers:
                cb(event)


    async def join(self, name:str) -> IParticipant:
        new_id = self.participants.__len__() + 1
        new_participant:GuestParticipant = GuestParticipant(new_id,name)
        self.participants[new_id] = new_participant

        self._publish(ParticipantJoined("participant_joined", participant=new_participant))
        return new_participant
    
    async def assign_team(self, participant_id:int, team:Team, caller:Caller):
        p = self.participants.get(participant_id)
        if not p:
            raise ValueError("Participant not found")
        team_participant = TeamParticipant(p.id,team, caller)
        self.participants[p.id] = team_participant

    async def start_auction(self):
        self._publish(AuctionStarted(self))
        await self.next_turn()
        pass

    async def next_turn(self):
        #seleziona il prossimo chiamante
        pass
        #self.current_caller = self.calling_strategy.next_caller()
        #self._publish(TurnStarted(caller=self.current_caller))

        #qui si potrebbe implementare la logica per preparare la player_pool

        #il chiamante seleziona un giocatore da mettere all'asta
        #self.current_player = await self.current_caller.choose_player(self.player_pool)

                
    def place_bid(self, team: Team, amount: int) -> Optional[AuctionEvent]:
            if not self.current_player:
                return None
            if amount > self.current_bid and team.budget >= amount:
                self.current_bid = amount
                self.current_bidder = team
                return BidPlaced(team=team.name, amount=amount)
            return None
    