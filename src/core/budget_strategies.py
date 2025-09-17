from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.player import Player
from core.team import Team  # solo per type hints
    
class BudgetStrategy(ABC):
    @abstractmethod
    def can_afford(self, team: Team, player: Player, price: float) -> bool:
        """Verifica se il team può permettersi il giocatore al prezzo dato."""
        pass

    @abstractmethod
    def apply_purchase(self, team: Team, player: Player, price: float) -> None:
        """Aggiorna lo stato del budget dopo un acquisto."""
        pass

class LimitedBudgetStrategy(BudgetStrategy):
    def __init__(self, initial_budget: float):
        self.budget = initial_budget

    def can_afford(self, team, player, price):
        return self.budget - team.spent >= price

    def apply_purchase(self, team, player, price):
        team.add_player(player,price)
        team.spent += price

class UnlimitedBudgetStrategy(BudgetStrategy):
    def can_afford(self, team, player, price):
        return True  # sempre possibile

    def apply_purchase(self, team, player, price):
        # non tocca il budget, ma traccia comunque la spesa
        team.spent += price
