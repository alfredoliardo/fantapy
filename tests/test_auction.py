import pytest
import asyncio

from core.budget_strategies import LimitedBudgetStrategy
from core.caller import Caller
from core.calling_strategy.base import CallingStrategy
from core.enums import PlayerRole
from core.events import AuctionStarted, ParticipantJoined
from core.market_rules import UniquePlayerMarket
from core.ownership_policies import NoDuplicatesOwnershipPolicy
from core.participant import GuestParticipant, TeamParticipant
from core.player import Player
from core.team import Team
from core.team_building_strategies.fixed_max_strategy import FixedMaxStrategy

from core.auction import Auction   # ⚠️ importa correttamente Auction dal tuo progetto


@pytest.mark.asyncio
async def test_create_auction_and_generate_teams():
    auction = Auction(
        auction_id="test-auction",
        name="Test Auction",
        budget_strategy=LimitedBudgetStrategy(1000),
        market_rules=UniquePlayerMarket(),
        ownership_policy=NoDuplicatesOwnershipPolicy(),
        team_building_strategy=FixedMaxStrategy(
            {
                PlayerRole.P: 3,
                PlayerRole.D: 8,
                PlayerRole.C: 8,
                PlayerRole.A: 6,
            }
        ),
        teams=4
    )

    assert auction.auction_id == "test-auction"
    assert len(auction.teams) == 4
    assert isinstance(next(iter(auction.teams.values())), Team)


@pytest.mark.asyncio
async def test_join_participant_publishes_event():
    auction = Auction("a1", "Auction test")

    published_events = []
    auction.subscribe(lambda e: published_events.append(e))

    p = await auction.join("Mario")

    assert isinstance(p, GuestParticipant)
    assert len(auction.participants) == 1
    assert any(isinstance(ev, ParticipantJoined) for ev in published_events)


@pytest.mark.asyncio
async def test_assign_team_converts_guest_to_team_participant():
    auction = Auction("a2", "Auction test 2")
    p = await auction.join("Luigi")

    team = next(iter(auction.teams.values()))

    class DummyCaller(Caller):
        async def choose_player(self, player_pool):
            return None

    await auction.assign_team(p.id, team, DummyCaller("dummy"))

    assigned = auction.participants[p.id]
    assert isinstance(assigned, TeamParticipant)
    assert assigned._team == team


@pytest.mark.asyncio
async def test_start_auction_publishes_event():
    auction = Auction("a3", "Auction test 3")

    published_events = []
    auction.subscribe(lambda e: published_events.append(e))

    await auction.start_auction()

    assert any(isinstance(ev, AuctionStarted) for ev in published_events)
