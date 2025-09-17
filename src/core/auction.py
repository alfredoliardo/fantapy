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
from core.participant import GuestParticipant, HostParticipant, IParticipant, TeamParticipant
from core.player import Player
from core.player_pool_builders.base import PlayerPoolBuilder
from core.player_pool_builders.role_sequential_pool_builder import RoleSequentialPoolBuilder
from core.team import Team
from core.team_building_strategies.base import TeamBuildingStrategy
from core.team_building_strategies.fixed_max_strategy import FixedMaxStrategy
from core.turn import Turn


class Auction:
    def __init__(
        self,
        auction_id:str,
        auction_name:str,
        host_name:str,
        teams:int = 8,

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
        players:List[Player] = [
             Player(1,"Davis K.", PlayerRole.A, "Udinese"),
             Player(2,"Paz N.", PlayerRole.C, "Como"),
             Player(3,"Mina", PlayerRole.D, "Cagliari"),
             Player(4,"Svilar", PlayerRole.P, "Roma"),
        ]
             
    ) -> None:
    
<<<<<<< HEAD
        
        self.auction_id = auction_id
        self.name = auction_name        
=======
        self.player_pool_builder:PlayerPoolBuilder = RoleSequentialPoolBuilder([PlayerRole.P,PlayerRole.D,PlayerRole.C,PlayerRole.A], self.team_building_strategy)
        self.participants:Dict[int,IParticipant] = {}
        self.auction_id = auction_id
        self.name = auction_name

>>>>>>> 5929443 (turn)
        self.host:HostParticipant = HostParticipant(0,host_name)
        self.participants[self.host.id] = self.host

        self.participants:Dict[int,IParticipant] = {}


        self.budget_strategy = budget_strategy
        self.market_rule = market_rules
        self.ownership_policy = ownership_policy
        self.team_building_strategy = team_building_strategy

        self.teams:Dict[int, Team] = self._generate_teams(teams)
        self.player_pool:List[Player] = players


        self.current_caller:Optional[Caller] = None
        self.current_player:Optional[Player] = None
        self.current_bids:List[Bid] = []
        self.best_bid:Optional[Bid] = None

        self.turns: List[Turn] = []
        self.current_turn: Optional[Turn] = None

        #self.calling_strategy = calling_strategy
        self.callers = []
        self.subscribers = []

    def _generate_teams(self, n: int) -> dict[int, Team]:
        return {
            i: Team(
                team_id=str(i),
                name=f"Team {i}"
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

        self._publish(ParticipantJoined(participant_id=new_id, name=name))
        return new_participant
    
    async def assign_team(self, participant_id:int, team:Team, caller:Caller):
        p = self.participants.get(participant_id)
        if not p:
            raise ValueError("Participant not found")
        team_participant = TeamParticipant(p.id,team, caller)
        self.participants[p.id] = team_participant

    async def start_auction(self):
        self._publish(AuctionStarted(self.auction_id))

        turn = await self.next_turn()

        self.turns.append(turn)

        pass

    async def next_turn(self) -> Turn:
        #calcola il numero del turno
        turn_number = len(self.turns) + 1

        #crea il turno e lo ritorna
        #ottiene il prossimo chiamante
        caller = self.calling_strategy.next_caller()

        #costruisce il pool di giocatori selezionabili
        #player_pool = self.player_pool_builder.build_pool(self.player_pool, self.teams.items)
        player_pool = self.player_pool


        player = await caller.choose_player(player_pool)
        bidding_strategy = await caller.choose_bidding_strategy()
        
        new_turn = Turn(turn_number, caller, player, bidding_strategy)
        #self._publish(TurnStarted(caller=self.current_caller))

    def set_calling_strategy(self,strategy:CallingStrategy):
        self.calling_strategy = strategy

    