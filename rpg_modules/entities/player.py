"""
Player entity class for RPG games.
"""

import pygame
from typing import Optional, Dict, List, Any
from ..items import Item

class Player:
    """Class representing the player character."""
    
    def __init__(self, x: int = 0, y: int = 0):
        """
        Initialize the player.
        
        Args:
            x: Initial x position
            y: Initial y position
        """
        self.x = x
        self.y = y
        self.speed = 5
        self.inventory: List[Optional[Item]] = [None] * 40  # 40 inventory slots
        self.equipment: Dict[str, Optional[Item]] = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None,
            'weapon': None
        }
        
        # Load player sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((0, 255, 0))  # Green color for player
        
    def move(self, dx: int, dy: int) -> None:
        """
        Move the player by the given delta.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self.x += dx * self.speed
        self.y += dy * self.speed
        
    def add_item(self, item: Item) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: The item to add
            
        Returns:
            True if the item was added successfully, False if inventory is full
        """
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                return True
        return False
        
    def equip_item(self, inventory_index: int) -> bool:
        """
        Equip an item from the inventory.
        
        Args:
            inventory_index: Index of the item in inventory to equip
            
        Returns:
            True if the item was equipped successfully
        """
        if not (0 <= inventory_index < len(self.inventory)):
            return False
            
        item = self.inventory[inventory_index]
        if item is None:
            return False
            
        # Determine equipment slot based on item type
        slot = None
        if isinstance(item, Item):
            if hasattr(item, 'weapon_type'):
                slot = 'weapon'
            elif hasattr(item, 'armor_type'):
                slot = item.armor_type
                
        if slot and slot in self.equipment:
            # Unequip current item if any
            current_item = self.equipment[slot]
            if current_item:
                self.inventory[inventory_index] = current_item
                
            # Equip new item
            self.equipment[slot] = item
            self.inventory[inventory_index] = None
            return True
            
        return False
        
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the player on the screen.
        
        Args:
            screen: The pygame surface to draw on
        """
        screen.blit(self.sprite, (self.x, self.y))
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert player state to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "speed": self.speed,
            "inventory": [
                item.to_dict() if item else None
                for item in self.inventory
            ],
            "equipment": {
                slot: item.to_dict() if item else None
                for slot, item in self.equipment.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(data["x"], data["y"])
        player.speed = data["speed"]
        
        # Restore inventory
        for i, item_data in enumerate(data["inventory"]):
            if item_data:
                player.inventory[i] = Item.from_dict(item_data)
                
        # Restore equipment
        for slot, item_data in data["equipment"].items():
            if item_data:
                player.equipment[slot] = Item.from_dict(item_data)
                
        return player 