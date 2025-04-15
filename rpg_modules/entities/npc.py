"""
NPC entity class for RPG games.
"""

import pygame
from typing import Dict, Any, Optional, List, Tuple, Callable
from ..core.constants import TILE_SIZE

class NPC:
    """Class representing a non-player character that can be interacted with."""
    
    def __init__(self, x: float, y: float, npc_id: str, name: str, title: str = "", dialog_id: str = None):
        """Initialize an NPC."""
        # Position (tile coordinates)
        self.x = x
        self.y = y
        self.npc_id = npc_id
        self.name = name
        self.title = title
        self.dialog_id = dialog_id
        
        # Display attributes
        self.direction = "south"  # Default facing
        self.sprite = None
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # Seconds per frame
        self.collision_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        
        # Behavior 
        self.movement_pattern = "stationary"  # Options: stationary, patrol, wander
        self.patrol_points = []
        self.current_patrol_point = 0
        self.wander_radius = 3  # Tiles
        self.movement_timer = 0
        self.movement_delay = 3  # Seconds between movements
        self.is_moving = False
        self.movement_speed = 1  # Tiles per second
        
        # Interaction
        self.interaction_radius = 2  # Tiles
        self.interactable = True
        self.quest_giver = False
        self.merchant = False
        self.has_new_dialog = False
        
        # Visual indicators
        self.dialog_indicator_visible = False
        self.quest_indicator_visible = False
        self.indicator_bounce = 0
        self.indicator_bounce_speed = 2
        self.indicator_bounce_height = 5
        
    def update(self, dt: float, player_x: float, player_y: float):
        """Update the NPC state."""
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4 frames per animation
        
        # Update indicators
        self.indicator_bounce += self.indicator_bounce_speed * dt
        if self.indicator_bounce > 1 or self.indicator_bounce < 0:
            self.indicator_bounce_speed *= -1
            
        # Check if player is in interaction range
        player_dist_x = abs(self.x - player_x / TILE_SIZE)
        player_dist_y = abs(self.y - player_y / TILE_SIZE)
        player_in_range = (player_dist_x <= self.interaction_radius and 
                          player_dist_y <= self.interaction_radius)
        
        # Update visual indicators based on player proximity
        if player_in_range:
            if self.dialog_id:
                self.dialog_indicator_visible = True
            if self.quest_giver:
                self.quest_indicator_visible = True
        else:
            self.dialog_indicator_visible = False
            self.quest_indicator_visible = False
        
        # Handle movement if NPC isn't stationary
        if self.movement_pattern != "stationary":
            self.movement_timer += dt
            if self.movement_timer >= self.movement_delay:
                self.movement_timer = 0
                
                if self.movement_pattern == "patrol" and self.patrol_points:
                    # Move to next patrol point
                    self._move_to_next_patrol_point(dt)
                elif self.movement_pattern == "wander":
                    # Wander randomly within radius
                    self._wander_randomly(dt)
    
    def draw(self, screen: pygame.Surface, camera_x: int, camera_y: int, zoom: float = 1.0):
        """Draw the NPC on the screen."""
        # Calculate screen position
        screen_x = (self.x * TILE_SIZE - camera_x) * zoom
        screen_y = (self.y * TILE_SIZE - camera_y) * zoom
        
        # Don't draw if off screen
        screen_width, screen_height = screen.get_size()
        if (screen_x < -TILE_SIZE * zoom or screen_x > screen_width or
            screen_y < -TILE_SIZE * zoom or screen_y > screen_height):
            return
        
        # Draw NPC sprite
        if self.sprite:
            # Use the sprite's animation frame based on direction
            frame_y = {"south": 0, "west": 1, "east": 2, "north": 3}.get(self.direction, 0)
            frame_rect = pygame.Rect(
                self.animation_frame * TILE_SIZE,
                frame_y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            
            # Draw the sprite
            scaled_size = int(TILE_SIZE * zoom)
            sprite_rect = pygame.Rect(screen_x, screen_y, scaled_size, scaled_size)
            screen.blit(pygame.transform.scale(
                self.sprite.subsurface(frame_rect),
                (scaled_size, scaled_size)
            ), sprite_rect)
        else:
            # Draw a placeholder if no sprite
            placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (0, 100, 200), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(placeholder, (0, 0, 0), pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 1)
            scaled_size = int(TILE_SIZE * zoom)
            screen.blit(pygame.transform.scale(placeholder, (scaled_size, scaled_size)), (screen_x, screen_y))
            
        # Draw indicators
        indicator_y_offset = -10 - self.indicator_bounce * self.indicator_bounce_height
        
        if self.dialog_indicator_visible:
            self._draw_dialog_indicator(screen, screen_x + scaled_size // 2, 
                                       screen_y + indicator_y_offset, zoom)
            
        if self.quest_indicator_visible:
            self._draw_quest_indicator(screen, screen_x + scaled_size // 2,
                                      screen_y + indicator_y_offset - 15 * zoom if self.dialog_indicator_visible else screen_y + indicator_y_offset,
                                      zoom)
    
    def interact(self, player) -> bool:
        """Handle player interaction with the NPC."""
        if not self.interactable:
            return False
            
        # Make NPC face the player
        dx = player.x / TILE_SIZE - self.x
        dy = player.y / TILE_SIZE - self.y
        
        if abs(dx) > abs(dy):
            self.direction = "east" if dx > 0 else "west"
        else:
            self.direction = "south" if dy > 0 else "north"
            
        # Return whether this NPC has dialog to show
        return self.dialog_id is not None
    
    def get_dialog_id(self) -> Optional[str]:
        """Get the dialog ID for this NPC, if any."""
        return self.dialog_id
    
    def set_sprite(self, sprite_sheet: pygame.Surface):
        """Set the sprite sheet for this NPC."""
        self.sprite = sprite_sheet
    
    def _draw_dialog_indicator(self, screen: pygame.Surface, x: int, y: int, zoom: float):
        """Draw a speech bubble indicator above the NPC."""
        bubble_size = int(16 * zoom)
        
        # Draw speech bubble
        pygame.draw.circle(screen, (255, 255, 255), (x, y), bubble_size)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), bubble_size, 1)
        
        # Draw tail
        points = [
            (x, y + bubble_size - 2),
            (x - bubble_size//2, y + bubble_size + bubble_size//2),
            (x + bubble_size//4, y + bubble_size + bubble_size//4)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 1)
        
        # Draw "..." inside bubble
        for i in range(3):
            dot_x = x - bubble_size//2 + i * (bubble_size//3)
            pygame.draw.circle(screen, (0, 0, 0), (dot_x, y), max(2, int(2 * zoom)))
    
    def _draw_quest_indicator(self, screen: pygame.Surface, x: int, y: int, zoom: float):
        """Draw a quest indicator (!) above the NPC."""
        size = int(14 * zoom)
        
        # Draw exclamation mark
        pygame.draw.rect(screen, (255, 255, 0), pygame.Rect(
            x - size//4, 
            y - size, 
            max(2, int(size//2)), 
            size*3//4
        ))
        pygame.draw.circle(screen, (255, 255, 0), (x, y - size//8), max(2, int(size//4)))
    
    def _move_to_next_patrol_point(self, dt: float):
        """Move to the next point in the patrol route."""
        if not self.patrol_points:
            return
            
        target_x, target_y = self.patrol_points[self.current_patrol_point]
        
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Determine facing direction
        if abs(dx) > abs(dy):
            self.direction = "east" if dx > 0 else "west"
        else:
            self.direction = "south" if dy > 0 else "north"
        
        # Check if close enough to target
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            # Move to next patrol point
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            self.is_moving = False
            return
            
        # Move towards target
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            self.x += (dx / dist) * self.movement_speed * dt
            self.y += (dy / dist) * self.movement_speed * dt
            self.is_moving = True
            
        # Update collision rect
        self.collision_rect.x = self.x * TILE_SIZE
        self.collision_rect.y = self.y * TILE_SIZE
    
    def _wander_randomly(self, dt: float):
        """Wander randomly within the defined radius."""
        import random
        
        if not self.is_moving:
            # Choose a random point within radius
            angle = random.random() * 6.28  # 0 to 2π
            distance = random.random() * self.wander_radius
            target_x = self.x + distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            target_y = self.y + distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            
            # Set as temporary patrol point
            self.patrol_points = [(target_x, target_y)]
            self.current_patrol_point = 0
            self.is_moving = True
            
        # Move toward the temporary target
        self._move_to_next_patrol_point(dt)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert NPC state to dictionary for serialization."""
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "dialog_id": self.dialog_id,
            "movement_pattern": self.movement_pattern,
            "patrol_points": self.patrol_points,
            "wander_radius": self.wander_radius,
            "interaction_radius": self.interaction_radius,
            "interactable": self.interactable,
            "quest_giver": self.quest_giver,
            "merchant": self.merchant,
            "has_new_dialog": self.has_new_dialog
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPC':
        """Create an NPC instance from serialized data."""
        npc = cls(
            data["x"], 
            data["y"], 
            data["npc_id"], 
            data["name"],
            data.get("title", ""),
            data.get("dialog_id")
        )
        
        npc.direction = data.get("direction", "south")
        npc.movement_pattern = data.get("movement_pattern", "stationary")
        npc.patrol_points = data.get("patrol_points", [])
        npc.wander_radius = data.get("wander_radius", 3)
        npc.interaction_radius = data.get("interaction_radius", 2)
        npc.interactable = data.get("interactable", True)
        npc.quest_giver = data.get("quest_giver", False)
        npc.merchant = data.get("merchant", False)
        npc.has_new_dialog = data.get("has_new_dialog", False)
        
        return npc 