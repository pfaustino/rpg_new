"""
Map management for the RPG game.
"""

import pygame
import random
from typing import List, Tuple, Dict, Optional
from .constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Map:
    """Class for managing the game world map."""
    
    def __init__(self, width: int = 50, height: int = 50):
        """
        Initialize the map.
        
        Args:
            width: Width of the map in tiles (default: 50)
            height: Height of the map in tiles (default: 50)
        """
        self.width = width
        self.height = height
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        
        # Initialize map grid (0 = floor/grass, 1 = wall/obstacle)
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        
        # List of wall rectangles for collision detection
        self.walls: List[pygame.Rect] = []
        
        # Generate initial map
        self._generate_map()
        
    def _generate_map(self) -> None:
        """Generate an outdoor map with scattered obstacles."""
        # Start with all grass (0)
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 0
        
        # Add border walls
        for x in range(self.width):
            self.grid[0][x] = 1  # Top wall
            self.grid[self.height-1][x] = 1  # Bottom wall
        for y in range(self.height):
            self.grid[y][0] = 1  # Left wall
            self.grid[y][self.width-1] = 1  # Right wall
        
        # Add random rock formations and obstacles
        num_obstacles = random.randint(10, 15)
        for _ in range(num_obstacles):
            self._add_obstacle()
        
        # Add some small scattered rocks
        num_rocks = random.randint(20, 30)
        for _ in range(num_rocks):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if random.random() < 0.3:  # 30% chance for a 2x2 rock
                for dx in range(2):
                    for dy in range(2):
                        self.grid[y+dy][x+dx] = 1
            else:  # Single rock
                self.grid[y][x] = 1
        
        # Update wall collision rectangles
        self._update_wall_rects()
        
    def _add_obstacle(self) -> None:
        """Add a natural-looking obstacle formation."""
        # Choose random starting point
        x = random.randint(3, self.width - 4)
        y = random.randint(3, self.height - 4)
        
        # Determine obstacle size
        size = random.randint(3, 6)
        
        # Create irregular shape using random walks
        points = [(x, y)]
        for _ in range(size):
            last_x, last_y = points[-1]
            for _ in range(3):  # Try 3 times to find valid position
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                new_x = last_x + dx
                new_y = last_y + dy
                if (2 <= new_x < self.width-2 and 
                    2 <= new_y < self.height-2):
                    points.append((new_x, new_y))
                    break
        
        # Fill in the obstacle points
        for px, py in points:
            self.grid[py][px] = 1
            # Sometimes extend the obstacle
            if random.random() < 0.4:
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    nx, ny = px + dx, py + dy
                    if (2 <= nx < self.width-2 and 
                        2 <= ny < self.height-2):
                        self.grid[ny][nx] = 1
                    
    def _update_wall_rects(self) -> None:
        """Update the list of wall rectangles for collision detection."""
        self.walls.clear()
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    self.walls.append(pygame.Rect(
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    ))
                    
    def get_spawn_position(self) -> Tuple[int, int]:
        """Find a valid spawn position for the player (floor tile)."""
        # Try to spawn near the center of the map
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Try positions in expanding circles around the center
        for radius in range(5):  # Try up to 5 tiles away from center
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if 0 <= x < self.width and 0 <= y < self.height and self.grid[y][x] == 0:
                        return x, y
                        
        # If no position found near center, fall back to random position
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[y][x] == 0:  # If it's a floor tile
                return x, y
                
    def is_wall(self, x: int, y: int) -> bool:
        """
        Check if the given tile coordinates contain a wall.
        
        Args:
            x: X coordinate in tiles
            y: Y coordinate in tiles
            
        Returns:
            True if the tile is a wall, False otherwise
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 1
        return True  # Consider out-of-bounds as walls
        
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if a position is valid (within bounds and not a wall).
        
        Args:
            x: X coordinate in tiles
            y: Y coordinate in tiles
            
        Returns:
            True if the position is valid (within bounds and not a wall), False otherwise
        """
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                not self.is_wall(x, y))
                
    def is_walkable(self, x: int, y: int) -> bool:
        """
        Check if a tile is walkable (floor tile).
        
        Args:
            x: X coordinate in tiles
            y: Y coordinate in tiles
            
        Returns:
            True if the tile is walkable (floor), False otherwise
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 0  # 0 = floor
        return False  # Out of bounds is not walkable
        
    def get_walls(self) -> List[pygame.Rect]:
        """Get the list of wall rectangles for collision detection."""
        return self.walls
        
    def draw(self, screen: pygame.Surface, camera, assets: Dict[str, pygame.Surface]) -> None:
        """
        Draw the visible portion of the map.
        
        Args:
            screen: The pygame surface to draw on
            camera: The camera object tracking the player
            assets: Dictionary of game assets including 'wall' and 'floor' tiles
        """
        # Create default surfaces if assets are missing
        if 'floor' not in assets:
            floor_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            floor_surface.fill((50, 30, 20))  # Brown for floor
            pygame.draw.rect(floor_surface, (60, 40, 30), 
                           (1, 1, TILE_SIZE-2, TILE_SIZE-2))  # Lighter border
            assets['floor'] = floor_surface
            
        if 'wall' not in assets:
            wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_surface.fill((100, 100, 100))  # Gray for walls
            pygame.draw.rect(wall_surface, (80, 80, 80), 
                           (1, 1, TILE_SIZE-2, TILE_SIZE-2))  # Darker border
            assets['wall'] = wall_surface
        
        # Calculate the range of tiles that are visible
        # Note: camera.x and camera.y are negative, so we negate them to get the correct range
        start_x = max(0, int(-camera.x / TILE_SIZE))
        end_x = min(self.width, int((-camera.x + SCREEN_WIDTH) / TILE_SIZE) + 1)
        start_y = max(0, int(-camera.y / TILE_SIZE))
        end_y = min(self.height, int((-camera.y + SCREEN_HEIGHT) / TILE_SIZE) + 1)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position
                # Since camera.x and camera.y are negative, we add them to get the correct screen position
                screen_x = x * TILE_SIZE + camera.x
                screen_y = y * TILE_SIZE + camera.y
                
                # Draw floor tile
                screen.blit(assets['floor'], (screen_x, screen_y))
                
                # Draw wall if present
                if self.grid[y][x] == 1:
                    screen.blit(assets['wall'], (screen_x, screen_y))
                    
    def to_dict(self) -> Dict:
        """Convert map state to dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Map':
        """Create a map from dictionary data."""
        map_obj = cls(data["width"], data["height"])
        map_obj.grid = data["grid"]
        map_obj._update_wall_rects()
        return map_obj 