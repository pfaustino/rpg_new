"""
Camera management for the RPG game.
"""

import pygame
from typing import Tuple, Optional
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
        self.zoom = 1.0  # Current zoom level
        self.zoom_message = None  # Current zoom message
        self.zoom_message_timer = 0  # Timer for zoom message display
        # Initialize camera position if target is provided
        if target:
            self.update(target)
        
    def get_zoom(self) -> float:
        """Get the current zoom level."""
        return self.zoom
        
    def zoom_in(self) -> None:
        """Increase zoom level (up to 4.0x)."""
        if not self.can_zoom_in():
            return
            
        old_zoom = self.zoom
        
        # Store the target's center position before changing zoom
        if self.target:
            target_center = self.target.get_center_position()
            
        # Apply zoom - ensure we scale by a good amount for responsiveness
        self.zoom = min(4.0, self.zoom + 0.25)
        self.zoom_message = f"Zoom: {self.zoom:.1f}x"
        self.zoom_message_timer = 30  # Show message for 0.5 seconds at 60fps
        print(f"DEBUG: Zoom in detected! Old zoom: {old_zoom:.2f}, New zoom: {self.zoom:.2f}")
        
        # Force update to recenter on the target
        if self.target:
            self.update()
        
    def zoom_out(self) -> None:
        """Decrease zoom level (down to 0.75x)."""
        if not self.can_zoom_out():
            return
            
        old_zoom = self.zoom
        
        # Store the target's center position before changing zoom
        if self.target:
            target_center = self.target.get_center_position()
            
        # Apply zoom - ensure we scale by a good amount for responsiveness
        self.zoom = max(0.75, self.zoom - 0.25)
        self.zoom_message = f"Zoom: {self.zoom:.1f}x"
        self.zoom_message_timer = 30  # Show message for 0.5 seconds at 60fps
        print(f"DEBUG: Zoom out detected! Old zoom: {old_zoom:.2f}, New zoom: {self.zoom:.2f}")
        
        # Force update to recenter on the target
        if self.target:
            self.update()
        
    def can_zoom_in(self) -> bool:
        """Check if the camera can zoom in further."""
        return self.zoom < 4.0
        
    def can_zoom_out(self) -> bool:
        """Check if the camera can zoom out further."""
        return self.zoom > 0.75
    
    def is_zoom_in_progress(self) -> bool:
        """Check if zoom animation is in progress."""
        return self.zoom_message_timer > 0
        
    def reset_zoom(self) -> None:
        """Reset zoom level to 1.0x."""
        old_zoom = self.zoom
        
        # Store the target's center position before changing zoom
        if self.target:
            target_center = self.target.get_center_position()
            
        # Apply zoom - always set to 1.0 regardless of current value
        self.zoom = 1.0
        self.zoom_message = "Zoom Reset"
        self.zoom_message_timer = 60  # Show message for 1 second at 60fps
        print(f"DEBUG: Zoom reset detected! Old zoom: {old_zoom:.2f}, New zoom: {self.zoom:.2f}")
        
        # Force update to recenter on the target
        if self.target:
            self.update()
            
    def get_zoom_message(self) -> Tuple[Optional[str], int]:
        """Get the current zoom message and its remaining display time."""
        if self.zoom_message_timer > 0:
            self.zoom_message_timer -= 1
            return self.zoom_message, self.zoom_message_timer
        return None, 0
        
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
            # Get target's center position
            target_center = target.get_center_position()
            
            # Center the camera on the target, accounting for zoom
            # The camera position is negated because we want to move the world
            # in the opposite direction of the player's movement
            self.x = -(target_center[0] - SCREEN_WIDTH // 2 / self.zoom)
            self.y = -(target_center[1] - SCREEN_HEIGHT // 2 / self.zoom)
            
            # Keep camera within map bounds, accounting for zoom
            if self.map_width > 0 and self.map_height > 0:
                # Calculate effective bounds based on zoom
                effective_width = self.map_width * self.zoom
                effective_height = self.map_height * self.zoom
                
                # Adjust bounds to prevent seeing outside the map
                self.x = min(0, max(self.x, -(effective_width - SCREEN_WIDTH) / self.zoom))
                self.y = min(0, max(self.y, -(effective_height - SCREEN_HEIGHT) / self.zoom)) 