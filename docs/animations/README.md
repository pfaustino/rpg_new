# Animations Module Documentation

## Overview
The animations module handles all rendering and animation logic for the game. All animation code is centralized in `base.py` to maintain consistency and reusability.

## File Structure
- `base.py`: Core animation system
  - Contains all monster rendering methods
  - Particle system implementation
  - Animation utilities and helpers

## Key Components

### Monster Rendering
- All monster render methods follow the pattern:
  ```python
  def _render_monster_type(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict) -> bool
  ```
- Required features:
  - Main body rendering
  - Eye effects
  - Particle effects (when appropriate)
  - Error handling

### Particle System
- Located in `base.py`
- Used for:
  - Environmental effects
  - Spell effects
  - Monster-specific effects
- Features:
  - Alpha blending
  - Life cycle management
  - Color variations

### Animation Utilities
- `_draw_shadow`: Adds shadow effects
- `_draw_highlight`: Adds highlight effects
- `_draw_particles`: Manages particle rendering
- `_sanitize_color`: Ensures valid color values

## Development Guidelines

### Adding New Monster Types
1. Add render method to `base.py`
2. Follow existing patterns for:
   - Body rendering
   - Eye effects
   - Particle effects
3. Include proper error handling
4. Add documentation

### Modifying Existing Animations
1. Review current implementation
2. Maintain consistent timing
3. Use existing helper methods
4. Update documentation

### Common Patterns
- Use `self.anim_values` for animation timing
- Implement proper error handling
- Use helper methods for common effects
- Maintain consistent color schemes

## Example Template for New Render Methods
```python
def _render_new_monster(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict) -> bool:
    """
    Renders a new monster type.
    
    Args:
        surface: Pygame surface to render on
        size: Size of the monster
        direction: Current facing direction
        anim: Animation values dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Main body rendering
        # Eye effects
        # Particle effects
        return True
    except Exception as e:
        print(f"Error rendering new monster: {e}")
        return False
``` 