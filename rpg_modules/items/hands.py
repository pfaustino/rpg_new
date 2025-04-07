"""
Hands (gauntlets) item class for RPG games.
"""

from typing import Dict, Any
from .base import Item

class Hands(Item):
    """Class representing gauntlets that can be equipped."""
    
    def __init__(
        self,
        defense: int,
        dexterity: int,
        quality: str,
        material: str,
        prefix: str = None
    ):
        """
        Initialize gauntlets.
        
        Args:
            defense: Base defense value of the gauntlets
            dexterity: Dexterity bonus provided by the gauntlets
            quality: Quality level of the gauntlets
            material: Material the gauntlets are made from
            prefix: Special prefix that adds effects
        """
        super().__init__(quality, material, prefix)
        self.defense = defense
        self.dexterity = dexterity
        
    @property
    def base_name(self) -> str:
        """Get the base name of the gauntlets."""
        return "Gauntlets"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert gauntlets to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "defense": self.defense,
            "dexterity": self.dexterity
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hands':
        """Create gauntlets from dictionary data."""
        return cls(
            defense=data["defense"],
            dexterity=data["dexterity"],
            quality=data["quality"],
            material=data["material"],
            prefix=data.get("prefix")
        ) 