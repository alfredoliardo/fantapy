from typing import Dict, Optional, List
from backend.models.auction import Auction
from backend.models.team import Team
from backend.models.player import Player
from backend.models.enums import PlayerRole
import uuid

class AuctionManager:
    def __init__(self):
        # memorizza tutte le aste in corso o passate
        self.auctions: Dict[str, Auction] = {}

    def create_auction(
        self,
        participants: int,
        player_pool: List[Player],
        budget_per_team: float = 1000,
        slots_per_role: Optional[Dict[PlayerRole, int]] = None
    ) -> Auction:
        auction_id = str(uuid.uuid4())
        auction = Auction(
            auction_id=auction_id,
            participants=participants,
            initial_budget=1000
        )
        self.auctions[auction_id] = auction
        return auction

    def get_auction(self, auction_id: str) -> Optional[Auction]:
        return self.auctions.get(auction_id)

    def list_auctions(self) -> List[Auction]:
        return list(self.auctions.values())

    def remove_auction(self, auction_id: str) -> bool:
        if auction_id in self.auctions:
            del self.auctions[auction_id]
            return True
        return False
