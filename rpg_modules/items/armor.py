"""
Armor item class for RPG games.
"""

from typing import Dict, Any
from .base import Item

class Armor(Item):
    """Class representing armor that can be equipped."""
    
    def __init__(
        self,
        armor_type: str,
        defense: int,
        quality: str,
        material: str,
        prefix: str = None
    ):
        """
        Initialize an armor piece.
        
        Args:
            armor_type: Type of armor (head, chest, etc.)
            defense: Base defense value of the armor
            quality: Quality level of the armor
            material: Material the armor is made from
            prefix: Special prefix that adds effects
        """
        super().__init__(quality, material, prefix)
        self.armor_type = armor_type
        self.defense = defense
        
    @property
    def base_name(self) -> str:
        """Get the base name of the armor."""
        return self.armor_type.capitalize()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "armor_type": self.armor_type,
            "defense": self.defense
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Armor':
        """Create an armor piece from dictionary data."""
        return cls(
            armor_type=data["armor_type"],
            defense=data["defense"],
            quality=data["quality"],
            material=data["material"],
            prefix=data.get("prefix")
        ) 