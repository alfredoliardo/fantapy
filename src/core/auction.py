from typing import Dict, List, Optional
from core.auctioneer import IAuctioneer
from core.bid import Bid
from core.bidding_strategies import BiddingStrategy
from core.budget_strategies import BudgetStrategy, LimitedBudgetStrategy
from core.caller import Caller
from core.calling_strategy.base import CallingStrategy
from core.calling_strategy.sequential_calling_strategy import SequentialCallingStrategy
from core.enums import PlayerRole
from core.events import AuctionEvent, AuctionStarted, BidPlaced, CallerChanged, ParticipantJoined, PlayerCalled, TurnStarted
from core.market_rules import MarketRule, UniquePlayerMarket
from core.ownership_policies import NoDuplicatesOwnershipPolicy, OwnershipPolicy
from core.player import Player
from core.player_pool import PlayerPool
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
        teams:int = 8     
    ) -> None:
    
        self.auction_id = auction_id
        self.name = auction_name
        self.teams:Dict[int, Team] = self._generate_teams(teams)        
        self.player_pool:PlayerPool = PlayerPool()


        self.turns:List[Turn] = []
        self.calling_strategy:CallingStrategy = SequentialCallingStrategy(list(self.teams.values()))
        self.started = False

        self.current_turn:Optional[Turn] = None



    def _generate_teams(self, n: int) -> dict[int, Team]:
        return {
            i: Team(
                id=i,
                name=f"Team {i}"
            )
            for i in range(1, n + 1)
        }


    async def start(self):
        if self.started:
            raise ValueError("Auction already started")
        self.started = True
        self._next_turn()

        self.current_turn = Turn(
            number=len(self.turns)+1,
            caller=self.calling_strategy.next_caller()
        )
        self.turns.append(self.current_turn)
        event = TurnStarted(
            turn_number=self.current_turn.number,
            caller_id=self.current_turn.caller.id,
            caller_name=self.current_turn.caller.name
        )

        return
    
    def _next_turn(self):
        # decide quale team è il chiamante
        next_team = self.calling_strategy.next_caller()
        turn = Turn(len(self.turns) + 1,next_team)

        self.current_turn = turn
        self.turns.append(turn)

    async def call(self, team_id:int, player:Player):
        if not self.current_turn:
            raise Exception("Auction not started")
        if self.current_turn.caller.id != team_id:
            raise PermissionError("Not this team's turn to call a player")
        self.current_turn.call(player)

        event = PlayerCalled(
            player_id=player.player_id,
            player_name=player.name,
            role=str(player.role.value)
        )

        return event
    
    async def bid(self, bid:Bid):
        if not self.current_turn:
            raise Exception("Auction not started")
        
        self.current_turn.bid(bid)

        event = BidPlaced(
            team_id=bid.team.id,
            team_name=bid.team.name,
            amount=bid.amount
        )

        return event
        

    def set_calling_strategy(self,strategy:CallingStrategy):
        self.calling_strategy = strategy

    