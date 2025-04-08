"""
Specific quest reward implementations.
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from .base import QuestReward
from ..items import Item
import pygame

@dataclass
class ItemReward(QuestReward):
    """Reward that grants an item to the player."""
    item: Item = field(default=None)
    description: str = field(init=True, default="")
    icon: str = field(init=True, default="item")
    icon_color: Tuple[int, int, int] = field(init=True, default=(255, 255, 255))

    def __post_init__(self):
        """Initialize the description."""
        if not self.description:
            self.description = "No item" if self.item is None else f"Receive {self.item.name}"

    def grant(self, player) -> bool:
        """Add the item(s) to the player's inventory."""
        if self.item:
            return player.inventory.add_item(self.item)
        return False

    def get_icon_surface(self, size: int = 16) -> pygame.Surface:
        """Get the icon surface for this reward."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.icon_color, (0, 0, size, size))
        return surface

@dataclass
class ExperienceReward(QuestReward):
    """Reward that grants experience points to the player."""
    amount: int = field(default=0)
    description: str = field(init=True, default="")
    icon: str = field(init=True, default="exp")
    icon_color: Tuple[int, int, int] = field(init=True, default=(0, 255, 0))

    def __post_init__(self):
        """Initialize the description."""
        if not self.description:
            self.description = f"Gain {self.amount} experience"

    def grant(self, player) -> bool:
        """Add experience to the player."""
        player.add_experience(self.amount)
        return True

    def get_icon_surface(self, size: int = 16) -> pygame.Surface:
        """Get the icon surface for this reward."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.icon_color, (0, 0, size, size))
        return surface

@dataclass
class GoldReward(QuestReward):
    """Reward that grants gold to the player."""
    amount: int = field(default=0)
    description: str = field(init=True, default="")
    icon: str = field(init=True, default="gold")
    icon_color: Tuple[int, int, int] = field(init=True, default=(255, 215, 0))

    def __post_init__(self):
        """Initialize the description."""
        if not self.description:
            self.description = f"Receive {self.amount} gold"

    def grant(self, player) -> bool:
        """Add gold to the player."""
        player.add_gold(self.amount)
        return True

    def get_icon_surface(self, size: int = 16) -> pygame.Surface:
        """Get the icon surface for this reward."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.icon_color, (0, 0, size, size))
        return surface

class MultiReward:
    """Reward that combines multiple rewards."""
    def __init__(self, rewards: List[Union[ItemReward, ExperienceReward, GoldReward]], description: str = None):
        """Initialize the reward with a list of rewards."""
        self.rewards = rewards
        self.description = description or "Multiple rewards"
        self.icon = "multi"
        self.icon_color = (255, 255, 255)

    def grant(self, player) -> bool:
        """Grant all rewards to the player."""
        success = True
        for reward in self.rewards:
            if not reward.grant(player):
                success = False
        return success

    def get_icon_surface(self, size: int = 16) -> pygame.Surface:
        """Get the icon surface for this reward."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.icon_color, (0, 0, size, size))
        return surface 