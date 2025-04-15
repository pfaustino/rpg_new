"""
Main RPG modules package.
"""

# Be selective about what we import to avoid circular dependencies
from rpg_modules.core import settings, constants, assets
from rpg_modules.entities import player, monster, monster_factory, monster_spawner

# Don't import UI components directly at package level
# Instead, let them be imported directly from the appropriate modules

__all__ = [
    'core',
    'entities',
    'items',
    'ui',
    'quests',
    'utils',
    'animations'
] 