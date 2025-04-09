# Entities Module Documentation

## Overview
The entities module manages all game entities, with a primary focus on monsters. It handles entity behavior, stats, and type definitions.

## File Structure
- `monster.py`: Primary monster implementation
  - Monster type definitions
  - Monster behavior patterns
  - Stats and attributes
- `monster_types.py`: Monster type definitions
  - Enum of all monster types
  - Type-specific attributes
  - DO NOT modify this file directly - use monster.py instead

## Key Components

### Monster Types
- Defined in `monster_types.py`
- Each type must have:
  - Unique identifier
  - Associated rendering method in `animations/base.py`
  - Stats configuration in `monster.py`

### Monster Implementation
- Located in `monster.py`
- Handles:
  - Monster creation and initialization
  - Behavior patterns
  - Stats management
  - Animation integration

## Development Guidelines

### Adding New Monster Types
1. Add type to `MonsterType` enum in `monster_types.py`
2. Add rendering method in `animations/base.py`
3. Add monster stats in `monster.py`
4. NEVER create duplicate animation files
5. NEVER modify `monster_types.py` directly

### Monster Animation Integration
1. All monster animations MUST be in `animations/base.py`
2. Follow the pattern:
   ```python
   def _render_monster_type(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict) -> bool
   ```
3. Use existing helper methods:
   - `_draw_shadow`
   - `_draw_highlight`
   - `_draw_particles`
   - `_sanitize_color`

### Common Patterns
- Use `MonsterType` enum for type checking
- Implement proper error handling
- Use the animation system in `base.py`
- Maintain consistent stats scaling

## Example Template for New Monster Types
```python
# In monster_types.py
class MonsterType(Enum):
    NEW_MONSTER = "new_monster"

# In monster.py
def create_monster(monster_type: MonsterType, position: Tuple[int, int]) -> Monster:
    """
    Creates a new monster of the specified type.
    
    Args:
        monster_type: Type of monster to create
        position: Starting position (x, y)
        
    Returns:
        Monster: New monster instance
    """
    try:
        # Monster creation logic
        return monster
    except Exception as e:
        logger.error(f"Error creating monster: {e}")
        return None

# In animations/base.py
def _render_new_monster(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict) -> bool:
    """
    Renders the new monster type.
    
    Args:
        surface: Pygame surface to render on
        size: Size of the monster
        direction: Current facing direction
        anim: Animation values dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Monster rendering logic
        return True
    except Exception as e:
        logger.error(f"Error rendering new monster: {e}")
        return False
```

## Important Notes
1. ALL monster animations MUST be in `animations/base.py`
2. NEVER create separate animation files
3. Use the existing particle system
4. Follow the established rendering patterns
5. Maintain consistent error handling 