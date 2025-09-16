from core.auction import Auction
from core.auction_factory import AuctionFactory
from core.calling_strategy.sequential_calling_strategy import SequentialCallingStrategy


class TeamDrivenAuctionFactory(AuctionFactory):
    def __init__(self, teams, bidding_strategy):
        self.teams = teams
        self.bidding_strategy = bidding_strategy

    def create(self, auction_id: str, name: str) -> Auction:
        auction = Auction(auction_id, name)
        auction.set_calling_strategy(SequentialCallingStrategy(self.teams))

        return auction
