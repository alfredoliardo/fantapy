from abc import ABC, abstractmethod

from core.auction import Auction

class AuctionFactory(ABC):
    @abstractmethod
    def create(self, auction_id: str, name: str) -> Auction:
        pass
