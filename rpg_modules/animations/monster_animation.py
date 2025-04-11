import pygame
from typing import Optional, Tuple
from ..entities.monster import MonsterType
from .base import Direction, AnimationState, MonsterIcon

class MonsterAnimation:
    """Handles monster animations using the MonsterIcon system."""
    
    def __init__(self, monster_type: MonsterType):
        """Initialize the monster animation system."""
        self.monster_type = monster_type
        # Convert MonsterType enum to string for MonsterIcon
        if hasattr(monster_type, 'name'):
            monster_type_str = monster_type.name.lower()
        else:
            monster_type_str = str(monster_type).lower()
        self.icon = MonsterIcon(monster_type_str)
        self.direction = Direction.DOWN
        self.state = AnimationState.IDLE
        self.frame = 0
        self.animation_timer = 0
        self.base_size = 96  # Increased base size for better visibility
        self.surface = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        self.needs_update = True
    
    def update(self, moving: bool):
        """Update the animation state."""
        # Update state based on movement
        if moving:
            self.state = AnimationState.WALKING
        else:
            self.state = AnimationState.IDLE
        
        # Update frame counter
        self.frame = (self.frame + 1) % 4
        self.needs_update = True
    
    def draw(self, screen: pygame.Surface, position: Tuple[int, int], size: int, direction: Optional[Direction] = None) -> None:
        """Draw the monster animation at the given screen coordinates."""
        try:
            # Use provided direction or fallback to current direction
            current_direction = direction if direction is not None else self.direction
            
            # Ensure we have a valid Direction enum
            if isinstance(current_direction, str):
                try:
                    current_direction = Direction[current_direction.upper()]
                except ValueError:
                    current_direction = Direction.DOWN
            elif not isinstance(current_direction, Direction):
                current_direction = Direction.DOWN
            
            # Create a temporary surface for the scaled monster
            temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw the monster icon with proper scaling and direction
            self.icon.render(temp_surface, size, current_direction)
            
            # Calculate center position for drawing
            pos_x = position[0] - size // 2
            pos_y = position[1] - size // 2
            
            # Draw at the centered position
            screen.blit(temp_surface, (pos_x, pos_y))
            
        except Exception as e:
            print(f"Error in monster animation draw: {e}")
            # Fallback to simple circle if advanced rendering fails
            try:
                radius = size // 3
                center_x = position[0]
                center_y = position[1]
                color = self.icon._get_monster_color()
                pygame.draw.circle(screen, color, (center_x, center_y), radius)
            except Exception as e:
                print(f"Error in fallback circle draw: {e}")
    
    def set_direction(self, direction: Direction):
        """Set the monster's facing direction."""
        if self.direction != direction:
            self.direction = direction
            self.needs_update = True
    
    def set_state(self, state: AnimationState):
        """Set the monster's animation state."""
        if self.state != state:
            self.state = state
            self.needs_update = True 