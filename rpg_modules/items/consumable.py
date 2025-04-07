"""
Consumable item class for RPG games.
"""

from typing import Dict, Any
from .base import Item

class Consumable(Item):
    """Class representing consumable items like potions."""
    
    def __init__(
        self,
        consumable_type: str,
        effect_value: int,
        quality: str,
        prefix: str = None
    ):
        """
        Initialize a consumable item.
        
        Args:
            consumable_type: Type of consumable (health, mana, etc.)
            effect_value: Value of the consumable's effect
            quality: Quality level of the consumable
            prefix: Special prefix that adds effects
        """
        super().__init__(quality, None, prefix)  # Consumables don't have materials
        self.consumable_type = consumable_type
        self.effect_value = effect_value
        
    @property
    def base_name(self) -> str:
        """Get the base name of the consumable."""
        return f"{self.consumable_type.capitalize()} Potion"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert consumable to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "consumable_type": self.consumable_type,
            "effect_value": self.effect_value
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Consumable':
        """Create a consumable from dictionary data."""
        return cls(
            consumable_type=data["consumable_type"],
            effect_value=data["effect_value"],
            quality=data["quality"],
            prefix=data.get("prefix")
        ) 