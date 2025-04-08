"""
Camera management for the RPG game.
"""

import pygame
from typing import Tuple
from rpg_modules.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    """Class for managing the game camera."""
    
    def __init__(self, target=None):
        """
        Initialize the camera.
        
        Args:
            target: Optional entity (usually player) for the camera to follow
        """
        self.target = target
        self.x = 0
        self.y = 0
        self.map_width = 0
        self.map_height = 0
        # Initialize camera position if target is provided
        if target:
            self.update(target)
        
    def set_map_bounds(self, map_width: int, map_height: int) -> None:
        """Set the map bounds for camera movement."""
        self.map_width = map_width
        self.map_height = map_height
        
    def update(self, target=None) -> None:
        """
        Update camera position to follow the target.
        
        Args:
            target: Optional new target to follow (defaults to initial target)
        """
        if target is None:
            target = self.target
            
        if target:
            # Center the camera on the target
            # The camera position is negated because we want to move the world
            # in the opposite direction of the player's movement
            target_center = target.get_center_position()
            self.x = -(target_center[0] - SCREEN_WIDTH // 2)
            self.y = -(target_center[1] - SCREEN_HEIGHT // 2)
            
            # Keep camera within map bounds
            if self.map_width > 0 and self.map_height > 0:
                self.x = min(0, max(self.x, -(self.map_width - SCREEN_WIDTH)))
                self.y = min(0, max(self.y, -(self.map_height - SCREEN_HEIGHT))) 