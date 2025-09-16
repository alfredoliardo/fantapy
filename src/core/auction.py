from typing import Dict, List, Optional
from core.auctioneer import IAuctioneer
from core.bid import Bid
from core.budget_strategies import BudgetStrategy, LimitedBudgetStrategy
from core.caller import Caller
from core.calling_strategy.base import CallingStrategy
from core.enums import PlayerRole
from core.events import AuctionEvent, AuctionStarted, BidPlaced, ParticipantJoined, PlayerCalled, TurnStarted
from core.market_rules import MarketRule, UniquePlayerMarket
from core.ownership_policies import NoDuplicatesOwnershipPolicy, OwnershipPolicy
from core.participant import GuestParticipant, IParticipant, TeamParticipant
from core.player import Player
from core.team import Team
from core.team_building_strategies.base import TeamBuildingStrategy
from core.team_building_strategies.fixed_max_strategy import FixedMaxStrategy


class Auction:
    def __init__(
        self,
        auction_id:str,
        name:str,
        budget_strategy:BudgetStrategy = LimitedBudgetStrategy(1000),
        market_rules:MarketRule = UniquePlayerMarket(),
        ownership_policy:OwnershipPolicy = NoDuplicatesOwnershipPolicy(),
        team_building_strategy:TeamBuildingStrategy = FixedMaxStrategy(
            {
                 PlayerRole.P: 3,
                 PlayerRole.D: 8,
                 PlayerRole.C: 8,
                 PlayerRole.A: 6,
            }
        ),        
        teams:int = 8,
        players:List[Player] = [
             Player(1,"Davis K.", PlayerRole.A, "Udinese"),
             Player(2,"Paz N.", PlayerRole.C, "Como"),
             Player(3,"Mina", PlayerRole.D, "Cagliari"),
             Player(4,"Svilar", PlayerRole.P, "Roma"),
        ]
             
    ) -> None:
    
        
        self.participants:Dict[int,IParticipant] = {}
        self.auction_id = auction_id
        self.name = name

        self.budget_strategy = budget_strategy
        self.market_rule = market_rules
        self.ownership_policy = ownership_policy
        self.team_building_strategy = team_building_strategy

        self.teams:Dict[int, Team] = self._generate_teams(teams, self.budget_strategy, self.ownership_policy)
        self.player_pool:List[Player] = players


        self.current_caller:Optional[Caller] = None
        self.current_player:Optional[Player] = None
        self.current_bids:List[Bid] = []
        self.best_bid:Optional[Bid] = None

        #self.calling_strategy = calling_strategy
        self.callers = []
        self.subscribers = []

    def _generate_teams(self, n: int, budget_strategy: BudgetStrategy, ownership_policy: OwnershipPolicy) -> dict[int, Team]:
        return {
            i: Team(
                team_id=str(i),
                name=f"Team {i}",
                budget_strategy=budget_strategy,
                ownership_policy=ownership_policy
            )
            for i in range(1, n + 1)
        }

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

    def set_calling_strategy(self,strategy:CallingStrategy):
        self.calling_strategy = strategy

    