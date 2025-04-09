# UI Module Documentation

## Overview
The UI module manages all user interface components, including windows, buttons, tooltips, and other interactive elements.

## File Structure
- `windows.py`: Window management
  - Window creation
  - Window stacking
  - Focus management
- `buttons.py`: Button components
  - Button states
  - Click handling
  - Hover effects
- `tooltips.py`: Tooltip system
  - Tooltip creation
  - Positioning
  - Content formatting
- `layouts.py`: Layout management
  - Grid layouts
  - Flow layouts
  - Alignment

## Key Components

### Window System
- Features:
  - Window creation and management
  - Focus handling
  - Event propagation
  - Z-order management

### Button System
- Handles:
  - Button states (normal, hover, pressed)
  - Click events
  - Visual feedback
  - Accessibility

### Tooltip System
- Provides:
  - Contextual information
  - Dynamic positioning
  - Rich text formatting
  - Animation effects

## Development Guidelines

### Adding New UI Components
1. Choose appropriate base class
2. Implement required interfaces
3. Add event handling
4. Include accessibility

### Window Management
1. Handle focus properly
2. Manage z-order
3. Propagate events
4. Clean up resources

### Common Patterns
- Use layout managers
- Handle all events
- Provide visual feedback
- Support keyboard navigation

## Example Template for New UI Components
```python
# In new_component.py
class NewComponent(UIComponent):
    """
    Brief description of the new UI component.
    
    Attributes:
        attribute1 (type): Description
        attribute2 (type): Description
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize the new component.
        
        Args:
            x: X position
            y: Y position
            width: Component width
            height: Component height
        """
        super().__init__(x, y, width, height)
        self.attribute1 = None
        self.attribute2 = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle UI events.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled
        """
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    # Handle click
                    return True
            return False
        except Exception as e:
            logger.error(f"Error handling event: {e}")
            return False
            
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the component.
        
        Args:
            surface: Surface to draw on
        """
        try:
            # Drawing logic
            pass
        except Exception as e:
            logger.error(f"Error drawing component: {e}")
```

## Important Notes
1. Handle all events properly
2. Manage focus correctly
3. Clean up resources
4. Support keyboard navigation
5. Provide visual feedback 