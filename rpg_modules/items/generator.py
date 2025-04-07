"""
Item generator for creating items with various properties.
"""

import random
from typing import Optional
from ..core.constants import (
    WEAPON_TYPES, ARMOR_TYPES, MATERIALS,
    QUALITIES, PREFIXES
)
from .weapon import Weapon
from .armor import Armor
from .hands import Hands
from .consumable import Consumable

class ItemGenerator:
    """Generator for creating items with various properties."""
    
    def _get_prefix_for_quality(self, quality: str) -> Optional[str]:
        """Get a random prefix appropriate for the item's quality."""
        if quality == 'Legendary':
            prefix_pool = PREFIXES['rare']
        elif quality == 'Masterwork':
            prefix_pool = PREFIXES['uncommon'] + PREFIXES['rare']
        elif quality == 'Polished':
            prefix_pool = PREFIXES['uncommon']
        else:  # Standard
            prefix_pool = PREFIXES['common']
            
        return random.choice(prefix_pool) if prefix_pool else None
    
    def generate_item(
        self,
        item_type: Optional[str] = None,
        quality: Optional[str] = None
    ):
        """
        Generate a random item with the given type and quality.
        
        Args:
            item_type: Optional type of item to generate ('weapon', 'armor', 'consumable')
            quality: Optional quality level for the item
            
        Returns:
            A randomly generated item of the specified type and quality
        """
        # Determine item type if not specified
        if not item_type:
            item_type = random.choice(['weapon', 'armor', 'consumable'])
            
        # Determine quality if not specified
        if not quality:
            quality = random.choice(QUALITIES)
            
        # Quality multiplier affects item stats
        quality_multiplier = {
            'Standard': 1.0,
            'Polished': 1.2,
            'Masterwork': 1.5,
            'Legendary': 2.0
        }.get(quality, 1.0)
        
        # Random chance for prefix based on quality
        prefix_chance = {
            'Standard': 0.1,
            'Polished': 0.2,
            'Masterwork': 0.4,
            'Legendary': 0.8
        }.get(quality, 0.1)
        
        prefix = self._get_prefix_for_quality(quality) if random.random() < prefix_chance else None
        material = random.choice(MATERIALS)
        
        if item_type == 'weapon':
            weapon_type = random.choice(WEAPON_TYPES)
            base_attack = random.randint(5, 15)
            attack_power = int(base_attack * quality_multiplier)
            
            return Weapon(
                weapon_type=weapon_type,
                attack_power=attack_power,
                quality=quality,
                material=material,
                prefix=prefix
            )
            
        elif item_type == 'armor':
            armor_type = random.choice(ARMOR_TYPES)
            if armor_type == 'hands':
                base_defense = random.randint(3, 8)
                defense = int(base_defense * quality_multiplier)
                dexterity = random.randint(1, 5)
                
                return Hands(
                    defense=defense,
                    dexterity=dexterity,
                    quality=quality,
                    material=material,
                    prefix=prefix
                )
            else:
                base_defense = random.randint(5, 15)
                defense = int(base_defense * quality_multiplier)
                
                return Armor(
                    armor_type=armor_type,
                    defense=defense,
                    quality=quality,
                    material=material,
                    prefix=prefix
                )
                
        else:  # Consumable
            effect_types = ['health', 'mana', 'stamina']
            consumable_type = random.choice(effect_types)
            base_value = random.randint(20, 50)
            effect_value = int(base_value * quality_multiplier)
            
            return Consumable(
                consumable_type=consumable_type,
                effect_value=effect_value,
                quality=quality
            ) 