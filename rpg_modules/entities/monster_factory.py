from typing import Dict, Optional, Type
from .monster import Monster, MonsterType
from .monster_icons import MonsterIcon

class MonsterFactory:
    """Factory class for creating and managing monsters."""
    
    def __init__(self):
        self._monster_templates: Dict[str, Dict] = {}
        self._monster_icons: Dict[str, MonsterIcon] = {}
        
    def register_monster_type(self, monster_type: str, template: Dict) -> None:
        """Register a new monster type with its template."""
        self._monster_templates[monster_type] = template
        
    def create_monster(self, monster_type: MonsterType, x: int, y: int) -> Monster:
        """Create a new monster of the specified type at the given position."""
        monster = Monster(monster_type, x, y)
        
        # Set monster attributes based on type
        if monster_type == MonsterType.DRAGON:
            monster.health = 200
            monster.damage = 50
            monster.speed = 2
        elif monster_type == MonsterType.SPIDER:
            monster.health = 80
            monster.damage = 20
            monster.speed = 4
        elif monster_type == MonsterType.GHOST:
            monster.health = 100
            monster.damage = 30
            monster.speed = 3
        elif monster_type == MonsterType.SKELETON:
            monster.health = 120
            monster.damage = 35
            monster.speed = 2
        elif monster_type == MonsterType.SLIME:
            monster.health = 60
            monster.damage = 15
            monster.speed = 1
            
        return monster
    
    def get_monster_icon(self, monster_type: str) -> MonsterIcon:
        """Get or create a monster icon for the specified type."""
        if monster_type not in self._monster_icons:
            self._monster_icons[monster_type] = MonsterIcon(monster_type)
        return self._monster_icons[monster_type]
    
    def update_monster_icons(self, dt: float) -> None:
        """Update all monster icons."""
        for icon in self._monster_icons.values():
            icon.update(dt)
    
    def clear_monster_icons(self) -> None:
        """Clear all monster icons."""
        self._monster_icons.clear()

# Create a global instance
monster_factory = MonsterFactory() 