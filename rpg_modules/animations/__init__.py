"""
Animation classes for RPG game entities.
"""

import pygame
import os
from typing import Tuple, Dict, Optional
from enum import Enum, auto
from ..utils.logging import logger
import math

class Direction(Enum):
    """Possible directions for animations."""
    DOWN = 0  # First row in sprite sheet
    LEFT = 1  # Second row
    RIGHT = 2  # Third row
    UP = 3  # Fourth row

class AnimationState(Enum):
    """Possible animation states."""
    IDLE = auto()
    WALKING = auto()
    ATTACKING = auto()
    HURT = auto()

from .base import MonsterIcon, PlayerIcon, AnimatedIcon

class Animation:
    """Base class for handling sprite animations."""
    
    def __init__(self, sprite_sheet_path: str, frame_size: Tuple[int, int], 
                 frame_count: int, animation_speed: float = 0.1):
        """
        Initialize an animation.
        
        Args:
            sprite_sheet_path: Path to the sprite sheet image
            frame_size: Size of each frame in the sprite sheet
            frame_count: Number of frames in the animation
            animation_speed: Time between frames in seconds
        """
        self.sprite_sheet = self._load_sprite_sheet(sprite_sheet_path)
        self.frame_size = frame_size
        self.frame_count = frame_count
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.time_since_last_frame = 0
        self.current_direction = Direction.DOWN
        self.current_state = AnimationState.IDLE
        
    def _load_sprite_sheet(self, path: str) -> pygame.Surface:
        """Load a sprite sheet from the given path."""
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            # Create a placeholder if sprite sheet not found
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(surface, (255, 0, 0), (0, 0, 32, 32))
            return surface
            
    def update(self, dt: float) -> None:
        """Update animation state."""
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % self.frame_count
            
    def get_current_frame(self) -> pygame.Surface:
        """Get the current frame of the animation."""
        frame_x = self.current_frame * self.frame_size[0]
        frame_y = self.current_direction.value * self.frame_size[1]
        return self.sprite_sheet.subsurface((frame_x, frame_y, *self.frame_size))
        
    def set_direction(self, direction: Direction) -> None:
        """Set the current direction of the animation."""
        self.current_direction = direction
        
    def set_state(self, state: AnimationState) -> None:
        """Set the current animation state."""
        self.current_state = state

class PlayerAnimation(Animation):
    """Player character animation."""
    
    def __init__(self):
        sprite_sheet_path = os.path.join("assets", "animations", "player.png")
        super().__init__(
            sprite_sheet_path=sprite_sheet_path,
            frame_size=(32, 32),
            frame_count=4,
            animation_speed=0.1
        )
        
    def update(self, dt: float) -> None:
        """Update player animation state."""
        super().update(dt)
        
    def draw(self, screen: pygame.Surface, position: Tuple[int, int], size: int = 32) -> None:
        """Draw the current animation frame."""
        frame = self.get_current_frame()
        if size != self.frame_size[0]:
            frame = pygame.transform.scale(frame, (size, size))
        screen.blit(frame, position)

class MonsterAnimation:
    def __init__(self, monster_type):
        """Initialize monster animation using the MonsterIcon system."""
        self.monster_type = monster_type
        # Convert MonsterType enum to lowercase string for MonsterIcon
        if isinstance(monster_type, str):
            monster_type_str = monster_type.lower()
        else:
            monster_type_str = monster_type.name.lower()
        self.icon = MonsterIcon(monster_type_str)  # Create icon for this monster type
        self.base_size = 32  # Base size for scaling
        self.frame_size = (self.base_size, self.base_size)
        self.current_frame = None  # Store the current frame
        self.current_size = None  # Store the current size
        self.last_update = pygame.time.get_ticks()
        self.update_interval = 50  # Update animation every 50ms
        logger.debug(f"Created MonsterAnimation for {monster_type_str}")

    def get_frame(self, direction, frame_index, size=None):
        """Get the current animation frame."""
        current_time = pygame.time.get_ticks()
        
        # Ensure direction is a Direction enum
        if not isinstance(direction, Direction):
            print(f"Warning: Invalid direction type {type(direction)}, defaulting to Direction.DOWN")
            direction = Direction.DOWN
        
        # Use provided size or default to base_size
        render_size = size if size is not None else self.base_size
        
        # Only create new surface if size changed or no current frame
        if self.current_frame is None or self.current_size != render_size:
            self.current_frame = pygame.Surface((render_size, render_size), pygame.SRCALPHA)
            self.current_size = render_size
        
        # Update animation if enough time has passed
        if current_time - self.last_update > self.update_interval:
            try:
                # Clear the surface with transparency
                self.current_frame.fill((0, 0, 0, 0))
                
                # Update the monster icon's animation state
                self.icon.update(self.update_interval / 1000.0)  # Convert to seconds
                
                # Let the MonsterIcon handle all the rendering
                self.icon.render(self.current_frame, render_size, direction)
                
                self.last_update = current_time
            except Exception as e:
                logger.error(f"Error rendering monster {self.monster_type}: {e}")
                # Fallback rendering - draw a simple shape if rendering fails
                color = self._get_fallback_color()
                pygame.draw.circle(self.current_frame, color,
                                (render_size//2, render_size//2), 
                                render_size//3)
            
        return self.current_frame

    def _get_fallback_color(self):
        """Get a color for fallback rendering based on monster type."""
        color_map = {
            # Original monsters
            'SLIME': (0, 255, 128),      # Bright green
            'SPIDER': (139, 69, 19),     # Brown
            'GHOST': (200, 200, 255),    # Light blue
            'SKELETON': (200, 200, 200),  # Light gray
            'WOLF': (128, 128, 128),     # Gray
            
            # Elemental creatures
            'FIRE_ELEMENTAL': (255, 69, 0),    # Red-orange
            'ICE_ELEMENTAL': (135, 206, 250),  # Light sky blue
            'STORM_ELEMENTAL': (65, 105, 225),  # Royal blue
            'EARTH_GOLEM': (139, 69, 19),      # Saddle brown
            
            # Undead
            'ZOMBIE': (107, 142, 35),    # Olive drab
            'WRAITH': (75, 0, 130),      # Indigo
            'VAMPIRE': (139, 0, 0),      # Dark red
            'LICH': (75, 0, 130),        # Indigo
            
            # Magical creatures
            'PIXIE': (255, 192, 203),    # Pink
            'PHOENIX': (255, 69, 0),     # Red-orange
            'UNICORN': (255, 255, 255),  # White
            'GRIFFIN': (218, 165, 32),   # Golden rod
            
            # Forest creatures
            'TREANT': (34, 139, 34),     # Forest green
            'BEAR': (139, 69, 19),       # Saddle brown
            'DRYAD': (124, 252, 0),      # Lawn green
            
            # Dark creatures
            'DEMON': (139, 0, 0),        # Dark red
            'SHADOW_STALKER': (47, 79, 79),  # Dark slate gray
            'NIGHTMARE': (25, 25, 112),   # Midnight blue
            'DARK_WIZARD': (75, 0, 130),  # Indigo
            
            # Constructs
            'CLOCKWORK_KNIGHT': (192, 192, 192),  # Silver
            'STEAM_GOLEM': (169, 169, 169),       # Dark gray
            'ARCANE_TURRET': (138, 43, 226),      # Blue violet
            
            # Crystal Creatures
            'CRYSTAL_GOLEM': (176, 224, 230),    # Powder blue
            'PRISM_ELEMENTAL': (255, 0, 255),    # Magenta
            'GEM_BASILISK': (147, 112, 219),     # Medium purple
            
            # Psychic Anomalies
            'THOUGHT_DEVOURER': (186, 85, 211),  # Medium orchid
            'MEMORY_PHANTOM': (221, 160, 221),   # Plum
            'PSYCHIC_HYDRA': (218, 112, 214),    # Orchid
            
            # Time Entities
            'CHRONO_WRAITH': (255, 215, 0),     # Gold
            'TEMPORAL_TITAN': (218, 165, 32),    # Golden rod
            'TIME_WEAVER': (255, 223, 0),        # Gold
            
            # Astral Beings
            'NEBULA_PHANTOM': (148, 0, 211),     # Dark violet
            'COSMIC_GUARDIAN': (75, 0, 130),     # Indigo
            'ASTRAL_WALKER': (138, 43, 226),     # Blue violet
            
            # Nature Spirits
            'FOREST_GUARDIAN': (34, 139, 34),    # Forest green
            'VINE_WEAVER': (0, 128, 0),          # Green
            'MOSS_BEAST': (85, 107, 47),         # Dark olive green
            'BLOOM_SPIRIT': (144, 238, 144),     # Light green
        }
        
        if isinstance(self.monster_type, str):
            type_name = self.monster_type.upper()
        else:
            type_name = self.monster_type.name
            
        # Get color from map or generate one based on name hash
        if type_name in color_map:
            return color_map[type_name]
        else:
            # Generate a consistent color based on the type name
            name_hash = sum(ord(c) for c in type_name)
            r = (name_hash * 123) % 256
            g = (name_hash * 456) % 256
            b = (name_hash * 789) % 256
            return (r, g, b)

    def update(self, is_moving):
        """Update animation state."""
        # The actual update is handled in get_frame to ensure smooth animation
        pass

    def draw(self, screen, x, y, direction, size=None):
        """Draw the monster at the specified position with optional size."""
        try:
            # Ensure direction is a Direction enum
            if not isinstance(direction, Direction):
                print(f"Warning: Invalid direction type {type(direction)}, defaulting to Direction.DOWN")
                direction = Direction.DOWN
                
            # Get the properly sized frame
            frame = self.get_frame(direction, 0, size)
            frame_size = frame.get_width()  # Use actual frame size
            
            # Calculate position to center the frame
            pos_x = x - frame_size // 2
            pos_y = y - frame_size // 2
            
            # Draw the frame
            screen.blit(frame, (pos_x, pos_y))
            
        except Exception as e:
            logger.error(f"Error drawing monster {self.monster_type} at ({x}, {y}): {e}")
            # Fallback to simple shape if rendering fails
            color = self._get_fallback_color()
            render_size = size if size is not None else self.base_size
            pygame.draw.circle(screen, color,
                             (x, y),
                             render_size//3) 