"""
Base item class for RPG games.
"""

import pygame
from typing import Optional, Dict, Any
from ..core.constants import TILE_SIZE, GRAY, QUALITY_COLORS

class Item:
    """Base class for all items in the game."""
    
    def __init__(
        self,
        quality: str,
        material: Optional[str] = None,
        prefix: Optional[str] = None
    ):
        """
        Initialize a base item.
        
        Args:
            quality: Quality level of the item
            material: Material the item is made from
            prefix: Special prefix that adds effects
        """
        self.quality = quality
        self.material = material
        self.prefix = prefix
        
        # Load default item sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((200, 200, 200))  # Default gray color
        
    @property
    def display_name(self) -> str:
        """Get the full display name of the item."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        if self.material:
            parts.append(self.material)
        parts.append(self.base_name)
        return " ".join(parts)
        
    @property
    def base_name(self) -> str:
        """Get the base name of the item without quality/material."""
        return "Item"
        
    def get_icon(self) -> pygame.Surface:
        """Get the inventory icon for this item."""
        return self.sprite
        
    def get_equipment_sprite(self) -> pygame.Surface:
        """Get the equipment sprite for this item."""
        return self.sprite

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization."""
        return {
            "type": self.__class__.__name__,
            "quality": self.quality,
            "material": self.material,
            "prefix": self.prefix
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(data["quality"], data.get("material"), data.get("prefix"))
        return item

    def __str__(self) -> str:
        """String representation of the item."""
        return f"{self.display_name} ({self.quality})"

    def __repr__(self) -> str:
        """Detailed string representation of the item."""
        return f"{self.__class__.__name__}(quality='{self.quality}', material='{self.material}', prefix='{self.prefix}')" 