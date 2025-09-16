# auction/core/bidding_strategies.py

import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from core.player import Player
from core.team import Team
from core.market_rules import MarketRule


class BiddingStrategy(ABC):
    """Interfaccia astratta per tutte le strategie di bidding."""

    def __init__(self, market_rule: MarketRule):
        self.market_rule = market_rule

    @abstractmethod
    async def run_bidding(self, player: Player, teams: List[Team]) -> Optional[Team]:
        """Esegue la fase di bidding e restituisce il vincitore (o None)."""
        ...


# --------------------------------------------------------------------------
# 1. Offerte libere (rilanci incrementali finché scade il timer)
# --------------------------------------------------------------------------
class FreeBiddingStrategy(BiddingStrategy):
    def __init__(self, market_rule: MarketRule, countdown_seconds: int = 10):
        super().__init__(market_rule)
        self.countdown_seconds = countdown_seconds

    async def run_bidding(self, player, teams):
        if not self.market_rule.is_available(player):
            return None

        highest = 0
        winner: Optional[Team] = None

        # Qui ipotizziamo una logica semplificata:
        # - ogni bidder risponde in parallelo con una proposta
        # - prendiamo l'offerta massima
        # In un sistema reale: countdown, reset ad ogni rilancio, broadcast via WS
        bids = await asyncio.gather(
            *[
                t.bidder.make_bid(highest)
                for t in teams
                if t.ownership_policy.can_own(t, player)
            ]
        )

        for team, bid in zip(teams, bids):
            if bid and bid > highest:
                highest = bid
                winner = team

        return winner


# --------------------------------------------------------------------------
# 2. Poker bidding (turni sequenziali: rilancio o passo, senza rientrare)
# --------------------------------------------------------------------------
class PokerBiddingStrategy(BiddingStrategy):
    def __init__(self, market_rule: MarketRule, min_raise: int = 1):
        super().__init__(market_rule)
        self.min_raise = min_raise

    async def run_bidding(self, player, teams):
        if not self.market_rule.is_available(player):
            return None

        active = [
            t for t in teams if t.ownership_policy.can_own(t, player)
        ]
        highest = 0
        winner: Optional[Team] = None

        # ciclo a turni finché più di 1 rimane attivo
        while len(active) > 1:
            next_round = []
            for t in active:
                bid = await t.bidder.make_bid(highest)
                if bid is None:
                    continue  # passo definitivo
                if bid >= highest + self.min_raise:
                    highest = bid
                    winner = t
                    next_round.append(t)
                else:
                    # offerta troppo bassa = passo
                    continue
            active = next_round

        # se resta solo uno attivo → vincitore
        return winner if winner else (active[0] if active else None)


# --------------------------------------------------------------------------
# 3. Closed bid (busta chiusa simultanea)
# --------------------------------------------------------------------------
class ClosedBidStrategy(BiddingStrategy):
    def __init__(self, market_rule: MarketRule):
        super().__init__(market_rule)

    async def run_bidding(self, player, teams):
        if not self.market_rule.is_available(player):
            return None

        valid_teams = [
            t for t in teams if t.ownership_policy.can_own(t, player)
        ]
        if not valid_teams:
            return None

        bids = await asyncio.gather(
            *[t.bidder.make_bid(0) for t in valid_teams]
        )

        max_bid = max(bids) if bids else 0
        winners = [t for t, b in zip(valid_teams, bids) if b == max_bid]

        # In caso di parità, scegliamo il primo (o definisci altra regola: sorteggio)
        return winners[0] if winners else None
