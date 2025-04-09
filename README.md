# RPG Game

A 2D RPG game built with Python and Pygame.

## Code Organization

### Key Files and Their Purposes

- `rpg_modules/animations/base.py`: Central location for all monster and entity animation code
  - Contains the core animation system
  - All monster rendering methods
  - Particle system implementation
  - DO NOT create new animation files - extend this one instead

- `rpg_modules/entities/monster.py`: Primary monster logic and behavior
  - Monster type definitions
  - Monster behavior patterns
  - Stats and attributes
  - DO NOT use monster_2.py - this is the current implementation

- `rpg_modules/core/`:
  - `map.py`: Map generation and management
  - `assets.py`: Asset loading and resource management
  - `camera.py`: Camera and viewport handling
  - `constants.py`: Game-wide constants and configurations

- `rpg_modules/utils/`:
  - `colors.py`: Color utilities and constants
  - `logging.py`: Logging configuration
  - `ui.py`: UI helper functions
  - `fonts.py`: Font management

### Common Development Tasks

1. Adding a new monster type:
   - Add type to `MonsterType` enum in `rpg_modules/entities/monster.py`
   - Add rendering method in `rpg_modules/animations/base.py`
   - Add monster stats in `rpg_modules/entities/monster.py`

2. Modifying monster animations:
   - All monster rendering code is in `rpg_modules/animations/base.py`
   - Use existing helper methods like `_draw_shadow`, `_draw_highlight`, etc.
   - Particle effects are handled by the particle system in the same file

3. Adding new game features:
   - Core game logic goes in `game.py`
   - UI components go in `rpg_modules/ui/`
   - Utility functions go in `rpg_modules/utils/`

### Code Style Guidelines

1. Monster rendering methods:
   - All render methods should be in `base.py`
   - Follow the pattern: `_render_monster_type(self, surface, size, direction, anim)`
   - Use existing helper methods for common effects
   - Include proper error handling

2. Particle effects:
   - Use the existing particle system in `base.py`
   - Don't create new particle implementations

3. Animation patterns:
   - Reuse existing animation utilities
   - Keep timing consistent with other animations
   - Use the `anim` dictionary for animation values

## Getting Started

A simple RPG game built with Python and Pygame, featuring:
- Inventory system with tooltips
- Equipment system with tooltips
- Item generator with different types and qualities
- Basic player movement and map rendering

## Requirements
- Python 3.x
- Pygame 2.x

## Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install -e .
```

## Running the Game
```bash
python -m game
```

## Controls
- Arrow keys: Move player
- I: Toggle inventory/equipment view
- G: Toggle item generator
- ESC: Close UI windows/exit game
- Click items to equip/unequip them

## Features
- Grid-based inventory system
- Equipment slots for different item types
- Item tooltips showing detailed stats
- Item generator with various types and qualities
- Quality-based color coding for items 