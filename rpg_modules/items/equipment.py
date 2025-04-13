"""
Equipment item classes for RPG games.
"""

from typing import Optional, List
from .base import Equipment

class Weapon(Equipment):
    """A weapon that can be equipped."""
    
    def __init__(
        self,
        name: str,
        weapon_type: str,
        attack_power: int,
        material: str,
        quality: str = "Common",
        prefix: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize a weapon.
        
        Args:
            name: The name of the weapon
            weapon_type: The type of weapon (sword, axe, etc.)
            attack_power: The base attack power of the weapon
            material: The material the weapon is made from
            quality: The quality level of the weapon
            prefix: Optional prefix modifier for the weapon
            description: Optional description of the weapon
        """
        super().__init__(name, "weapon", material, quality, prefix, description)
        self.weapon_type = weapon_type
        self.attack_power = attack_power
        
    def get_stats_display(self) -> List[str]:
        """Get a list of stat strings to display in tooltips."""
        stats = super().get_stats_display()
        stats.extend([
            f"Type: {self.weapon_type}",
            f"Attack: {self.attack_power}"
        ])
        return stats

class Armor(Equipment):
    """Armor that can be equipped."""
    
    def __init__(
        self,
        name: str,
        armor_type: str,
        defense: int,
        material: str,
        quality: str = "Common",
        prefix: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize armor.
        
        Args:
            name: The name of the armor
            armor_type: The type of armor (chest, legs, etc.)
            defense: The base defense value of the armor
            material: The material the armor is made from
            quality: The quality level of the armor
            prefix: Optional prefix modifier for the armor
            description: Optional description of the armor
        """
        super().__init__(name, armor_type, material, quality, prefix, description)
        self.armor_type = armor_type
        self.defense = defense
        
    def get_stats_display(self) -> List[str]:
        """Get a list of stat strings to display in tooltips."""
        stats = super().get_stats_display()
        stats.extend([
            f"Type: {self.armor_type}",
            f"Defense: {self.defense}"
        ])
        return stats

class Hands(Equipment):
    """Gauntlets that can be equipped."""
    
    def __init__(
        self,
        name: str,
        defense: int,
        dexterity: int,
        material: str,
        quality: str = "Common",
        prefix: Optional[str] = None
    ):
        """
        Initialize gauntlets.
        
        Args:
            name: The name of the gauntlets
            defense: The base defense value of the gauntlets
            dexterity: The dexterity bonus of the gauntlets
            material: The material the gauntlets are made from
            quality: The quality level of the gauntlets
            prefix: Optional prefix modifier for the gauntlets
        """
        super().__init__(name, "hands", material, quality, prefix)
        self.defense = defense
        self.dexterity = dexterity
        
    def get_stats_display(self) -> List[str]:
        """Get a list of stat strings to display in tooltips."""
        stats = super().get_stats_display()
        stats.extend([
            "Type: Gauntlets",
            f"Defense: {self.defense}",
            f"Dexterity: {self.dexterity}"
        ])
        return stats 