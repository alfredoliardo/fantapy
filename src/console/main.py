import asyncio
import uuid
from core.auction import Auction
from core.player import Player
from core.enums import PlayerRole
from core.budget_strategies import LimitedBudgetStrategy
from core.market_rules import UniquePlayerMarket
from core.ownership_policies import NoDuplicatesOwnershipPolicy
from core.team_building_strategies.fixed_max_strategy import FixedMaxStrategy
from core.user import User


async def main():
   user_name = input("Ciao, come ti chiami: ")
   user = User(str(uuid.uuid4), user_name)

   auction_name = input("Inserisci nome asta: ")
   teams = int(input("Quanti team: "))

   auction = await create_auction(auction_name, user.name, teams)
   
   print(f"Auction creted: {auction.auction_id}")

   await auction.join(user.name)

async def create_auction(name, user, teams):
    return Auction(
        str(uuid.uuid4),
        auction_name=name,
        host_name=user,
        teams=teams
    )

if __name__ == "__main__":
    asyncio.run(main())
