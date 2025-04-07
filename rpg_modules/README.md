# RPG Modules

A collection of reusable modules for creating RPG games with Pygame. This package provides essential components for building RPG games, including:

- Item System (weapons, armor, consumables)
- Inventory Management
- Equipment System
- Item Generation
- UI Components

## Installation

```bash
pip install rpg-modules
```

## Quick Start

```python
import pygame
from rpg_modules.items import ItemGenerator
from rpg_modules.ui import InventoryUI, EquipmentUI
from rpg_modules.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create UI elements
inventory = InventoryUI(x=50, y=50)
equipment = EquipmentUI(x=400, y=50)

# Generate some items
generator = ItemGenerator()
weapon = generator.generate_item('weapon', 'Legendary')
armor = generator.generate_item('armor', 'Masterwork')

# Add items to inventory
player.inventory.add_item(weapon)
player.inventory.add_item(armor)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle UI events
        inventory.handle_event(event, player)
        equipment.handle_event(event, player)
    
    # Draw UI
    inventory.draw(screen, player)
    equipment.draw(screen, player)
    
    pygame.display.flip()

pygame.quit()
```

## Features

### Item System
- Base Item class with quality levels and prefixes
- Weapon class with attack power and weapon types
- Armor class with defense and armor types
- Consumable items with various effects
- Hands/Gauntlets with defense and dexterity bonuses

### UI Components
- Grid-based inventory system
- Equipment slots with visual representation
- Item tooltips with detailed stats
- Color-coded item qualities
- Drag-and-drop functionality

### Item Generation
- Random item generation with quality levels
- Material-based attributes
- Prefix system for additional effects
- Balanced stat distribution

## Documentation

### Core Constants
All game constants are defined in `rpg_modules.core.constants`:
- Screen dimensions and tile sizes
- Color definitions
- Item types and qualities
- UI dimensions and styling

### Item Classes
```python
from rpg_modules.items import Item, Weapon, Armor, Consumable

# Create a custom weapon
weapon = Weapon(
    name="Dragon Slayer",
    weapon_type="Sword",
    material="Steel",
    quality="Legendary",
    attack_power=50
)

# Generate random items
from rpg_modules.items import ItemGenerator
generator = ItemGenerator()
random_weapon = generator.generate_item('weapon', 'Masterwork')
```

### UI Components
```python
from rpg_modules.ui import InventoryUI, EquipmentUI

# Create inventory (5x8 grid)
inventory = InventoryUI(
    x=50,
    y=50,
    width=300,
    height=500,
    rows=8,
    cols=5
)

# Create equipment window
equipment = EquipmentUI(
    x=400,
    y=50
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 