"""
Specific quest reward implementations.
"""

from typing import List, Optional
from dataclasses import dataclass
from .base import QuestReward
from ..items import Item

@dataclass
class ItemReward(QuestReward):
    """Reward that grants specific items."""
    description: str
    item: Item
    amount: int = 1
    
    def grant(self, player) -> bool:
        """Add the item(s) to the player's inventory."""
        for _ in range(self.amount):
            if not player.inventory.add_item(self.item):
                return False
        return True

@dataclass
class ExperienceReward(QuestReward):
    """Reward that grants experience points."""
    description: str
    amount: int
    
    def grant(self, player) -> bool:
        """Add experience to the player."""
        player.add_experience(self.amount)
        return True

@dataclass
class GoldReward(QuestReward):
    """Reward that grants gold currency."""
    description: str
    amount: int
    
    def grant(self, player) -> bool:
        """Add gold to the player's currency."""
        player.add_gold(self.amount)
        return True

@dataclass
class MultiReward(QuestReward):
    """Combines multiple rewards into one."""
    description: str
    rewards: List[QuestReward]
    
    def grant(self, player) -> bool:
        """Grant all contained rewards."""
        all_granted = True
        for reward in self.rewards:
            if not reward.grant(player):
                all_granted = False
        return all_granted 