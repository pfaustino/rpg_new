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
            item_type = self.__class__.__name__.lower()
            if hasattr(self, 'armor_type'):
                item_type = 'armor'
                name = self.armor_type.lower()
            elif hasattr(self, 'weapon_type'):
                item_type = 'weapon'
                name = self.weapon_type.lower()
            elif hasattr(self, 'consumable_type'):
                item_type = 'consumable'
                name = self.consumable_type.lower()
            else:
                name = self.name.lower()
                
            sprite_path = f"assets/items/{item_type}/{name}.png"
            try:
                # Try to load the sprite
                self.sprite = pygame.image.load(sprite_path)
                print(f"Loaded sprite from {sprite_path}")
            except (pygame.error, FileNotFoundError):
                print(f"Creating placeholder sprite for {item_type}/{name}")
                # Create a default colored square if sprite not found
                self.sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
                
                # Create different placeholder shapes based on item type
                if item_type == 'weapon':
                    # Weapon placeholder (sword shape)
                    color = self.quality_color
                    pygame.draw.polygon(self.sprite, color, [(10, 5), (22, 5), (22, 27), (16, 27), (10, 21)])
                    pygame.draw.rect(self.sprite, (100, 100, 100), (12, 5, 8, 12))  # handle
                elif item_type == 'armor':
                    # Armor placeholder based on armor type
                    color = self.quality_color
                    if name == 'head':
                        pygame.draw.circle(self.sprite, color, (16, 16), 10)
                        pygame.draw.circle(self.sprite, (50, 50, 50), (16, 16), 10, 2)
                    elif name == 'chest':
                        pygame.draw.polygon(self.sprite, color, [(10, 8), (22, 8), (24, 24), (8, 24)])
                        pygame.draw.line(self.sprite, (50, 50, 50), (16, 8), (16, 24), 2)
                    elif name == 'legs':
                        pygame.draw.rect(self.sprite, color, (10, 6, 12, 20))
                        pygame.draw.line(self.sprite, (50, 50, 50), (16, 6), (16, 26), 2)
                    elif name == 'feet':
                        pygame.draw.ellipse(self.sprite, color, (8, 12, 16, 8))
                        pygame.draw.rect(self.sprite, color, (8, 12, 16, 4))
                    elif name == 'hands':
                        pygame.draw.circle(self.sprite, color, (12, 16), 6)
                        pygame.draw.circle(self.sprite, color, (20, 16), 6)
                    else:
                        pygame.draw.rect(self.sprite, color, (8, 8, 16, 16))
                elif item_type == 'consumable':
                    # Consumable placeholder (potion shape)
                    if name == 'health':
                        color = (255, 50, 50)  # Red for health
                    elif name == 'mana':
                        color = (50, 50, 255)  # Blue for mana
                    else:
                        color = (50, 255, 50)  # Green for stamina
                        
                    pygame.draw.rect(self.sprite, (200, 200, 200), (12, 8, 8, 16))
                    pygame.draw.rect(self.sprite, color, (10, 12, 12, 12))
                    pygame.draw.ellipse(self.sprite, (200, 200, 200), (10, 6, 12, 8))
                else:
                    # Generic placeholder
                    self.sprite.fill(self.quality_color)
                
                # Save the sprite for future use
                try:
                    import os
                    os.makedirs(os.path.dirname(sprite_path), exist_ok=True)
                    pygame.image.save(self.sprite, sprite_path)
                    print(f"Saved placeholder sprite to {sprite_path}")
                except Exception as e:
                    print(f"Could not save placeholder sprite: {e}")
                    
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
        # Adding debug prints
        print(f"DEBUG: Attempting to equip item: {item.display_name}")
        print(f"DEBUG: Item type: {type(item).__name__}")
        
        slot = None
        
        # Check for Weapon type
        if hasattr(item, 'weapon_type'):
            slot = 'weapon'
            print(f"DEBUG: Item identified as weapon, using slot '{slot}'")
        # Check for armor type
        elif hasattr(item, 'armor_type'):
            armor_type = item.armor_type.lower()
            if armor_type in self.slots:
                slot = armor_type
                print(f"DEBUG: Item identified as armor with type '{armor_type}', using slot '{slot}'")
            else:
                print(f"DEBUG: Armor type '{armor_type}' not found in available slots")
        # Check for hands item
        elif hasattr(item, 'is_hands') and getattr(item, 'is_hands'):
            slot = 'hands'
            print(f"DEBUG: Item identified as hands equipment, using slot '{slot}'")
        else:
            print(f"DEBUG: Could not determine appropriate slot for item {item.display_name}")
            print(f"DEBUG: Available slots: {list(self.slots.keys())}")
            print(f"DEBUG: Item attributes: {dir(item)}")
            
        if slot and slot in self.slots:
            self.slots[slot] = item
            print(f"DEBUG: Successfully equipped {item.display_name} in slot '{slot}'")
            return True
            
        print(f"DEBUG: Failed to equip {item.display_name} - no suitable slot found")
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