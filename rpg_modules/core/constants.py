"""
Core constants for the RPG game modules.
"""

# Display constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32
FPS = 60

# Game balance constants
# Note: Dynamic game settings like MONSTER_SPEED_MULTIPLIER have been moved to the GameSettings class

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)  # Brighter blue
GRAY = (100, 100, 100)
SILVER = (192, 192, 192)  # Common items
PURPLE = (200, 0, 255)  # Brighter purple
GOLD = (255, 215, 0)      # Legendary items

# Item generation constants
WEAPON_TYPES = ['Sword', 'Axe', 'Mace', 'Dagger', 'Staff']
ARMOR_TYPES = ['Head', 'Chest', 'Legs', 'Feet', 'Hands']
MATERIALS = ['Iron', 'Steel', 'Silver', 'Gold', 'Mithril']
QUALITIES = ['Standard', 'Polished', 'Masterwork', 'Legendary']

# Item prefixes by rarity
PREFIXES = {
    'common': ['Sharp', 'Sturdy', 'Balanced'],
    'uncommon': ['Vicious', 'Reinforced', 'Precise'],
    'rare': ['Soulbound', 'Ethereal', 'Celestial']
}

# UI constants
UI_COLORS = {
    'background': (50, 50, 50),
    'cell_background': (30, 30, 30),
    'text': WHITE,
    'border': WHITE,
}

# Quality colors
QUALITY_COLORS = {
    'Standard': (100, 255, 100),  # Light green
    'Polished': (0, 191, 255),    # Deep sky blue
    'Masterwork': (200, 0, 255),  # Bright purple
    'Legendary': (255, 215, 0),   # Gold
    'Common': (192, 192, 192)     # Silver/fallback
}

# Default font sizes
FONT_SIZES = {
    'small': 18,
    'medium': 24,
    'large': 32
}

# UI dimensions
UI_DIMENSIONS = {
    'inventory_width': 300,
    'inventory_height': 500,
    'equipment_width': 300,
    'equipment_height': 500,
    'generator_width': 400,
    'generator_height': 500,
    'tooltip_width': 300,
    'tooltip_height': 300,
    'slot_size': 70,
    'spacing': 20
} 