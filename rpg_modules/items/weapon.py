"""
Weapon item class for RPG games.
"""

from typing import Dict, Any
from .base import Item

class Weapon(Item):
    """Class representing weapons that can be equipped."""
    
    def __init__(
        self,
        weapon_type: str,
        attack_power: int,
        quality: str,
        material: str,
        prefix: str = None
    ):
        """
        Initialize a weapon.
        
        Args:
            weapon_type: Type of weapon (sword, axe, etc.)
            attack_power: Base attack power of the weapon
            quality: Quality level of the weapon
            material: Material the weapon is made from
            prefix: Special prefix that adds effects
        """
        super().__init__(quality, material, prefix)
        self.weapon_type = weapon_type
        self.attack_power = attack_power
        
    @property
    def base_name(self) -> str:
        """Get the base name of the weapon."""
        return self.weapon_type.capitalize()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert weapon to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "weapon_type": self.weapon_type,
            "attack_power": self.attack_power
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Weapon':
        """Create a weapon from dictionary data."""
        return cls(
            weapon_type=data["weapon_type"],
            attack_power=data["attack_power"],
            quality=data["quality"],
            material=data["material"],
            prefix=data.get("prefix")
        ) 