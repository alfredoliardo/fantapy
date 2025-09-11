from backend.models.enums import PlayerRole
from services.slot_strategies.base import SlotValidationStrategy

class DefaultSlotValidation(SlotValidationStrategy):
    DEFAULT_SLOTS = {
        PlayerRole.GOALKEEPER: 3,
        PlayerRole.DEFENDER: 8,
        PlayerRole.MIDFIELDER: 8,
        PlayerRole.FORWARD: 6,
    }

    def __init__(self, custom_slots=None):
        self.slots = custom_slots or DefaultSlotValidation.DEFAULT_SLOTS

    def can_add_player(self, team, player):
        role = player.role
        role_count = sum(1 for p, _ in team.players if p.role == role)
        return role_count < self.slots[role]

    def describe_rule(self) -> str:
        return f"Limiti per ruolo: {self.slots}"
