"""
Base classes for items in the RPG game.
"""

import pygame
from typing import Optional, Dict, Any, List, Tuple
from ..core.constants import TILE_SIZE, GRAY, QUALITY_COLORS

class Item:
    """Base class for all items in the game."""
    
    def __init__(self, name: str, quality: str = "Common", prefix: Optional[str] = None):
        """
        Initialize an item.
        
        Args:
            name: The name of the item
            quality: The quality level of the item
            prefix: Optional prefix modifier for the item
        """
        self.name = name
        self.quality = quality
        self.prefix = prefix
        
        # Load sprite based on item type and name
        self.sprite = None  # Will be loaded by subclasses
        
    @property
    def display_name(self) -> str:
        """Get the display name of the item, including quality and prefix."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        if self.quality and self.quality != "Common":
            parts.append(self.quality)
        if self.name:
            parts.append(self.name)
        return " ".join(parts) if parts else "Unknown Item"
        
    @property
    def quality_color(self) -> Tuple[int, int, int]:
        """Get the color associated with this item's quality."""
        return QUALITY_COLORS.get(self.quality, GRAY)
        
    def get_equipment_sprite(self) -> pygame.Surface:
        """Get the sprite for this item."""
        if not self.sprite:
            # Load sprite based on item type and name
            sprite_path = f"assets/items/{self.__class__.__name__.lower()}/{self.name.lower()}.png"
            try:
                self.sprite = pygame.image.load(sprite_path)
            except pygame.error:
                # Create a default colored square if sprite not found
                self.sprite = pygame.Surface((32, 32))
                self.sprite.fill(self.quality_color)
        return self.sprite
        
    def get_stats_display(self) -> List[str]:
        """Get a list of stat strings to display in tooltips."""
        stats = []
        if self.quality != "Common":
            stats.append(f"Quality: {self.quality}")
        if self.prefix:
            stats.append(f"Effect: {self.prefix}")
        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization."""
        return {
            "type": self.__class__.__name__,
            "quality": self.quality,
            "prefix": self.prefix
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create an item from dictionary data."""
        item = cls(data["name"], data.get("quality"), data.get("prefix"))
        return item

    def __str__(self) -> str:
        """String representation of the item."""
        return f"{self.display_name} ({self.quality})"

    def __repr__(self) -> str:
        """Detailed string representation of the item."""
        return f"{self.__class__.__name__}(name='{self.name}', quality='{self.quality}', prefix='{self.prefix}')"

class Equipment(Item):
    """Base class for equipment items that can be worn."""
    
    def __init__(
        self,
        name: str,
        slot: str,
        material: str,
        quality: str = "Common",
        prefix: Optional[str] = None
    ):
        """
        Initialize equipment.
        
        Args:
            name: The name of the equipment
            slot: The equipment slot this item goes in
            material: The material the equipment is made from
            quality: The quality level of the equipment
            prefix: Optional prefix modifier for the equipment
        """
        super().__init__(name, quality, prefix)
        self.slot = slot
        self.material = material
        
    def get_stats_display(self) -> List[str]:
        """Get a list of stat strings to display in tooltips."""
        stats = super().get_stats_display()
        stats.extend([
            f"Slot: {self.slot.capitalize()}",
            f"Material: {self.material}"
        ])
        return stats 

class Equipment:
    """Class to manage equipped items."""
    def __init__(self):
        self.slots = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None,
            'weapon': None
        }
        
    def get_equipped_item(self, slot: str) -> Optional[Item]:
        """Get the item equipped in the given slot."""
        return self.slots.get(slot)
        
    def equip_item(self, item: Item) -> bool:
        """
        Equip an item in its appropriate slot.
        Returns True if successful, False if no appropriate slot.
        """
        slot = None
        if isinstance(item, Weapon):
            slot = 'weapon'
        elif isinstance(item, Hands):
            slot = 'hands'
        elif isinstance(item, Armor):
            slot = item.armor_type.lower()
            
        if slot and slot in self.slots:
            self.slots[slot] = item
            return True
        return False
        
    def unequip_item(self, slot: str) -> Optional[Item]:
        """Unequip and return the item in the given slot."""
        if slot in self.slots:
            item = self.slots[slot]
            self.slots[slot] = None
            return item
        return None

class Inventory:
    """Class to manage the player's inventory."""
    def __init__(self, capacity: int = 40):  # Changed from 32 to 40 to match 5x8 grid
        self.items = [None] * capacity
        
    def add_item(self, item: Item) -> bool:
        """Add an item to the first empty slot. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False
        
    def remove_item(self, item: Item) -> bool:
        """Remove the first occurrence of an item. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is item:
                self.items[i] = None
                return True
        return False
        
    def get_item_at(self, index: int) -> Optional[Item]:
        """Get the item at the given index."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None 