"""
Map management for the RPG game.
"""

import pygame
import random
import math
from opensimplex import OpenSimplex
from typing import List, Tuple, Dict, Optional, Set
from enum import Enum
from .constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .camera import Camera

class BiomeType(Enum):
    """Enum for different biome types."""
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    SWAMP = "swamp"
    TUNDRA = "tundra"
    MOUNTAIN = "mountain"

class TileType(Enum):
    """Enum for different tile types."""
    # Base tiles
    GRASS = "grass"
    DIRT = "dirt"
    SAND = "sand"
    WATER = "water"
    STONE = "stone"
    # Decorative tiles
    FLOWER = "flower"
    TREE = "tree"
    BUSH = "bush"
    ROCK = "rock"
    REED = "reed"
    # Structure tiles
    STONE_WALL = "stone_wall"

class Map:
    """Class for managing the game world map with biomes and varied terrain."""
    
    BIOME_CONFIG = {
        BiomeType.PLAINS: {
            "base_tiles": [(TileType.GRASS, 0.7), (TileType.DIRT, 0.3)],
            "decorations": [(TileType.FLOWER, 0.1), (TileType.BUSH, 0.05)],
            "elevation_range": (0.2, 0.5),
            "moisture_range": (0.3, 0.6)
        },
        BiomeType.FOREST: {
            "base_tiles": [(TileType.GRASS, 0.8), (TileType.DIRT, 0.2)],
            "decorations": [(TileType.TREE, 0.15), (TileType.BUSH, 0.1), (TileType.FLOWER, 0.05)],
            "elevation_range": (0.3, 0.7),
            "moisture_range": (0.6, 1.0)
        },
        BiomeType.DESERT: {
            "base_tiles": [(TileType.SAND, 0.9), (TileType.DIRT, 0.1)],
            "decorations": [(TileType.ROCK, 0.05)],
            "elevation_range": (0.0, 0.3),
            "moisture_range": (0.0, 0.2)
        },
        BiomeType.SWAMP: {
            "base_tiles": [(TileType.DIRT, 0.6), (TileType.WATER, 0.4)],
            "decorations": [(TileType.REED, 0.1), (TileType.BUSH, 0.05)],
            "elevation_range": (0.0, 0.3),
            "moisture_range": (0.7, 1.0)
        },
        BiomeType.MOUNTAIN: {
            "base_tiles": [(TileType.STONE, 0.8), (TileType.DIRT, 0.2)],
            "decorations": [(TileType.ROCK, 0.2)],
            "elevation_range": (0.7, 1.0),
            "moisture_range": (0.2, 0.5)
        }
    }
    
    def __init__(self, width: int = 50, height: int = 50, seed: Optional[int] = None):
        """
        Initialize the map with the given dimensions.
        
        Args:
            width: Map width in tiles
            height: Map height in tiles
            seed: Optional seed for random generation
        """
        self.width = width
        self.height = height
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        
        # Initialize noise generators
        self.elevation_noise = OpenSimplex(seed=self.seed)
        self.moisture_noise = OpenSimplex(seed=self.seed + 1)
        
        # Initialize map layers
        self.biome_grid = [[BiomeType.PLAINS for _ in range(width)] for _ in range(height)]
        self.base_grid = [[TileType.GRASS for _ in range(width)] for _ in range(height)]
        self.decoration_grid = [[None for _ in range(width)] for _ in range(height)]
        self.collision_grid = [[False for _ in range(width)] for _ in range(height)]
        
        # List of wall rectangles for collision detection
        self.walls = []
        
        # Add a variety of biomes and terrain features
        self._generate_map()
        self._update_wall_rects()
        
        # Add image caching for better zoom performance
        self.scaled_images_cache = {}
        self.last_zoom = 1.0
        
    def _generate_map(self) -> None:
        """Generate a varied terrain map with different biomes."""
        # Create noise maps for elevation and moisture
        elevation = [[0 for _ in range(self.width)] for _ in range(self.height)]
        moisture = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Fill with noise values
        elevation_min = 1.0
        elevation_max = -1.0
        moisture_min = 1.0
        moisture_max = -1.0
        
        # Increase noise scale for more distinct biome borders
        noise_scale = 0.08  # Lower values create larger, more distinct regions

        print("Generating terrain with noise...")
        for y in range(self.height):
            for x in range(self.width):
                # Get noise values
                ex = x * noise_scale
                ey = y * noise_scale
                elevation[y][x] = self.elevation_noise.noise2(ex, ey)
                moisture[y][x] = self.moisture_noise.noise2(ex + 100, ey + 100)
                
                # Track min/max for normalization
                elevation_min = min(elevation_min, elevation[y][x])
                elevation_max = max(elevation_max, elevation[y][x])
                moisture_min = min(moisture_min, moisture[y][x])
                moisture_max = max(moisture_max, moisture[y][x])
        
        # Create some distinct terrain features
        # Create a desert area in the bottom left quadrant
        for y in range(self.height // 2, self.height):
            for x in range(0, self.width // 2):
                elevation[y][x] = 0.15  # Low elevation for desert
                moisture[y][x] = 0.1   # Low moisture for desert
        
        # Create a mountain area in the top right quadrant
        for y in range(0, self.height // 2):
            for x in range(self.width // 2, self.width):
                elevation[y][x] = 0.8  # High elevation for mountains
                moisture[y][x] = 0.3   # Medium-low moisture for mountains
        
        # Create a swamp area in the bottom right
        for y in range(self.height // 2, self.height):
            for x in range(self.width // 2, self.width):
                if (x > self.width * 0.75 and y > self.height * 0.75):
                    elevation[y][x] = 0.2  # Low elevation for swamp
                    moisture[y][x] = 0.9   # High moisture for swamp
        
        print("Normalization and biome assignment...")
        for y in range(self.height):
            for x in range(self.width):
                elevation[y][x] = (elevation[y][x] - elevation_min) / (elevation_max - elevation_min)
                moisture[y][x] = (moisture[y][x] - moisture_min) / (moisture_max - moisture_min)
                
                # Determine biome based on elevation and moisture
                self.biome_grid[y][x] = self._get_biome(elevation[y][x], moisture[y][x])
                
                # Generate base terrain
                self.base_grid[y][x] = self._get_base_tile(self.biome_grid[y][x])
                
                # Add decorations
                if random.random() < 0.1:  # 10% chance for decoration
                    self.decoration_grid[y][x] = self._get_decoration(self.biome_grid[y][x])
                    
                # Update collision grid - only decorations block movement, not water
                self.collision_grid[y][x] = (self.decoration_grid[y][x] in {TileType.TREE, TileType.ROCK})
        
        # Ensure distinct terrain patches
        self._add_terrain_patches()
        
        # Add border walls
        self._add_border_walls()
        
        # Update wall collision rectangles
        self._update_wall_rects()
        
    def _get_biome(self, elevation: float, moisture: float) -> BiomeType:
        """Determine biome type based on elevation and moisture levels."""
        for biome, config in self.BIOME_CONFIG.items():
            elev_min, elev_max = config["elevation_range"]
            moist_min, moist_max = config["moisture_range"]
            
            if (elev_min <= elevation <= elev_max and 
                moist_min <= moisture <= moist_max):
                return biome
        
        return BiomeType.PLAINS  # Default biome
    
    def _get_base_tile(self, biome: BiomeType) -> TileType:
        """Get a random base tile type based on biome configuration."""
        tiles = self.BIOME_CONFIG[biome]["base_tiles"]
        return random.choices([t[0] for t in tiles], 
                           weights=[t[1] for t in tiles])[0]
    
    def _get_decoration(self, biome: BiomeType) -> Optional[TileType]:
        """Get a random decoration type based on biome configuration."""
        decorations = self.BIOME_CONFIG[biome]["decorations"]
        if not decorations:
            return None
            
        if random.random() < sum(d[1] for d in decorations):
            return random.choices([d[0] for d in decorations],
                               weights=[d[1] for d in decorations])[0]
        return None
    
    def _add_border_walls(self) -> None:
        """Add impassable borders around the map."""
        for x in range(self.width):
            self.collision_grid[0][x] = True
            self.collision_grid[self.height-1][x] = True
        for y in range(self.height):
            self.collision_grid[y][0] = True
            self.collision_grid[y][self.width-1] = True
    
    def _update_wall_rects(self) -> None:
        """Update the list of wall rectangles for collision detection."""
        self.walls.clear()
        wall_count = 0
        for y in range(self.height):
            for x in range(self.width):
                # Only add wall-type tiles (not water) to collision rects
                base_tile = self.base_grid[y][x]
                if self.collision_grid[y][x]:
                    self.walls.append(pygame.Rect(
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    ))
                    wall_count += 1
        
        # Only print wall count during map generation, not for every update
        if wall_count > 0 and len(self.walls) > 0:
            print(f"DEBUG: Updated wall rectangles - {wall_count} walls added to collision list")
        
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
                    if 0 <= x < self.width and 0 <= y < self.height and not self.collision_grid[y][x]:
                        return x, y
                        
        # If no position found near center, fall back to random position
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if not self.collision_grid[y][x]:  # If it's a walkable tile
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
            return self.collision_grid[y][x]
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
                not self.collision_grid[y][x])
                
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
            return not self.collision_grid[y][x]
        return False  # Out of bounds is not walkable
        
    def get_walls(self) -> List[pygame.Rect]:
        """Get the list of wall rectangles for collision detection."""
        return self.walls
        
    def get_tile_at_position(self, pixel_x: int, pixel_y: int) -> Optional[TileType]:
        """
        Get the tile type at the given position in pixel coordinates.
        
        Args:
            pixel_x: X position in pixels
            pixel_y: Y position in pixels
            
        Returns:
            The tile type at the given position, or None if out of bounds
        """
        # Convert pixel coordinates to tile coordinates
        tile_x = int(pixel_x // TILE_SIZE)
        tile_y = int(pixel_y // TILE_SIZE)
        
        # Check if in bounds
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.base_grid[tile_y][tile_x]
        return None
        
    def draw(self, screen, camera, assets):
        """Draw the map on the screen."""
        # Get camera zoom level
        zoom = camera.get_zoom()
        
        # Calculate the visible tile range with a much larger buffer to avoid black areas
        # First, determine the actual visible area in world space
        visible_width = SCREEN_WIDTH / zoom
        visible_height = SCREEN_HEIGHT / zoom
        
        # Calculate the margin based on zoom level - higher zoom needs larger margins
        # Use a scaling factor that increases with zoom to prevent gray areas
        margin = int(16 * max(1, zoom / 2))
        
        # Calculate the visible tiles with a significant margin in each direction
        # This ensures we don't see black/gray areas even during quick zooms or at high zoom levels
        start_x = max(0, int((-camera.x / zoom) / TILE_SIZE) - margin)
        end_x = min(self.width, int((-camera.x / zoom + visible_width) / TILE_SIZE) + margin)
        start_y = max(0, int((-camera.y / zoom) / TILE_SIZE) - margin)
        end_y = min(self.height, int((-camera.y / zoom + visible_height) / TILE_SIZE) + margin)
        
        # Debug output to track drawing area - commented out to avoid console flooding
        # print(f"Drawing tiles from ({start_x},{start_y}) to ({end_x},{end_y}) - Zoom: {zoom:.2f}, Margin: {margin}")
        
        # Scale tile size once - use ceil to prevent gaps between tiles
        scaled_size = math.ceil(TILE_SIZE * zoom)
        
        # Clear the image cache if zoom level changed
        if abs(zoom - self.last_zoom) > 0.01:  # Only clear when zoom changes significantly
            self.scaled_images_cache = {}
            self.last_zoom = zoom
            print(f"DEBUG: Cleared image cache at zoom level {zoom:.2f}")
        
        # Draw tiles directly to the screen with zoom scaling
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position with zoom - ensure we use exact pixel positions
                screen_x = int((x * TILE_SIZE + camera.x) * zoom)
                screen_y = int((y * TILE_SIZE + camera.y) * zoom)
                
                # Draw base tile
                base_tile = self.base_grid[y][x]
                if base_tile.value in assets:
                    # Get the original tile image
                    orig_img = assets[base_tile.value]
                    
                    # Scale the image if zoom isn't 1.0
                    if abs(zoom - 1.0) > 0.01:  # Only scale if zoom is significantly different from 1.0
                        # Use cached version if available
                        cache_key = f"{base_tile.value}_{scaled_size}"
                        if cache_key not in self.scaled_images_cache:
                            # Create and cache a smoothly scaled version
                            self.scaled_images_cache[cache_key] = pygame.transform.scale(orig_img, (scaled_size, scaled_size))
                        
                        # Use the cached scaled image
                        screen.blit(self.scaled_images_cache[cache_key], (screen_x, screen_y))
                    else:
                        # Use the original image for better performance at 1.0 zoom
                        screen.blit(orig_img, (screen_x, screen_y))
                else:
                    # Fallback for missing textures
                    pygame.draw.rect(screen, (100, 100, 100), 
                                   (screen_x, screen_y, scaled_size, scaled_size))
                
                # Draw decoration on top if present
                decoration = self.decoration_grid[y][x]
                if decoration and decoration.value in assets:
                    # Get the original decoration image
                    orig_decor = assets[decoration.value]
                    
                    # Scale the image if zoom isn't 1.0
                    if abs(zoom - 1.0) > 0.01:  # Only scale if zoom is significantly different from 1.0
                        # Use cached version if available
                        cache_key = f"{decoration.value}_{scaled_size}"
                        if cache_key not in self.scaled_images_cache:
                            # Create and cache a smoothly scaled version
                            self.scaled_images_cache[cache_key] = pygame.transform.scale(orig_decor, (scaled_size, scaled_size))
                        
                        # Use the cached scaled image
                        screen.blit(self.scaled_images_cache[cache_key], (screen_x, screen_y))
                    else:
                        # Use the original image for better performance at 1.0 zoom
                        screen.blit(orig_decor, (screen_x, screen_y))
        
    def to_dict(self) -> Dict:
        """Convert map state to dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "collision_grid": self.collision_grid
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Map':
        """Create a map from dictionary data."""
        map_obj = cls(data["width"], data["height"])
        map_obj.collision_grid = data["collision_grid"]
        map_obj._update_wall_rects()
        return map_obj 

    def _add_terrain_patches(self):
        """Add distinct patches of specific terrain types"""
        # Add some stone outcroppings (mountains)
        for _ in range(10):  # Increase to 10 stone patches
            patch_x = random.randint(5, self.width - 10)
            patch_y = random.randint(5, self.height - 10)
            patch_size = random.randint(4, 10)  # Larger patches
            
            for dy in range(-patch_size, patch_size):
                for dx in range(-patch_size, patch_size):
                    y = patch_y + dy
                    x = patch_x + dx
                    # Check if position is in bounds
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Create a jagged circular patch with noise
                        distance = math.sqrt(dx**2 + dy**2)
                        noise_factor = random.random() * 2  # Add some randomness
                        if distance <= patch_size + noise_factor - 1:
                            self.base_grid[y][x] = TileType.STONE
        
        # Add some sand patches (deserts)
        for _ in range(12):  # Increase to 12 sand patches
            patch_x = random.randint(5, self.width - 10)
            patch_y = random.randint(5, self.height - 10)
            patch_size = random.randint(5, 12)  # Larger patches
            
            for dy in range(-patch_size, patch_size):
                for dx in range(-patch_size, patch_size):
                    y = patch_y + dy
                    x = patch_x + dx
                    # Check if position is in bounds
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Create a more organic patch shape
                        distance = math.sqrt(dx**2 + dy**2)
                        noise_factor = random.random() * 3  # More randomness
                        if distance <= patch_size + noise_factor - 2:
                            self.base_grid[y][x] = TileType.SAND
                            
        # Add dirt patches in various places
        for _ in range(15):  # 15 dirt patches
            patch_x = random.randint(5, self.width - 10)
            patch_y = random.randint(5, self.height - 10)
            patch_size = random.randint(3, 8)
            
            for dy in range(-patch_size, patch_size):
                for dx in range(-patch_size, patch_size):
                    y = patch_y + dy
                    x = patch_x + dx
                    # Check if position is in bounds
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Create a circular patch with varied edge
                        distance = math.sqrt(dx**2 + dy**2)
                        edge_variation = math.sin(dx * 0.5) + math.cos(dy * 0.5)  # Wavy edge
                        if distance <= patch_size + edge_variation:
                            self.base_grid[y][x] = TileType.DIRT
                            
        # Add water pools/lakes
        for _ in range(8):  # 8 water pools
            patch_x = random.randint(10, self.width - 15)
            patch_y = random.randint(10, self.height - 15)
            patch_size = random.randint(3, 6)
            
            for dy in range(-patch_size, patch_size):
                for dx in range(-patch_size, patch_size):
                    y = patch_y + dy
                    x = patch_x + dx
                    # Check if position is in bounds
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Create a rounded pool shape
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance <= patch_size * 0.8:  # Make it more circular
                            self.base_grid[y][x] = TileType.WATER
                            self.collision_grid[y][x] = False  # Make water walkable
                            
        # Add stone wall structures
        self._add_stone_walls()
        
        # Update wall rectangles after all terrain modifications
        self._update_wall_rects()
    
    def _add_stone_walls(self):
        """Add stone wall structures like ruins, small buildings, and walls."""
        # Add several wall structures
        num_structures = random.randint(5, 10)
        
        for _ in range(num_structures):
            structure_type = random.choice(['room', 'ruin', 'wall'])
            
            if structure_type == 'room':
                # Create a rectangular room with walls
                self._create_room()
            elif structure_type == 'ruin':
                # Create ruins with incomplete walls
                self._create_ruins()
            elif structure_type == 'wall':
                # Create a straight or L-shaped wall
                self._create_wall()
    
    def _create_room(self):
        """Create a rectangular room with stone walls."""
        # Choose random position that's not too close to the borders
        room_x = random.randint(10, self.width - 15)
        room_y = random.randint(10, self.height - 15)
        
        # Room dimensions
        width = random.randint(5, 8)
        height = random.randint(5, 8)
        
        wall_count = 0
        print(f"DEBUG: Creating room at ({room_x}, {room_y}) with dimensions {width}x{height}")
        
        # Create top and bottom walls
        for x in range(room_x, room_x + width):
            # Check if position is valid
            if 0 <= x < self.width and 0 <= room_y < self.height:
                self.base_grid[room_y][x] = TileType.STONE_WALL
                self.collision_grid[room_y][x] = True
                wall_count += 1
            
            if 0 <= x < self.width and 0 <= room_y + height - 1 < self.height:
                self.base_grid[room_y + height - 1][x] = TileType.STONE_WALL
                self.collision_grid[room_y + height - 1][x] = True
                wall_count += 1
        
        # Create left and right walls
        for y in range(room_y, room_y + height):
            if 0 <= room_x < self.width and 0 <= y < self.height:
                self.base_grid[y][room_x] = TileType.STONE_WALL
                self.collision_grid[y][room_x] = True
            
            if 0 <= room_x + width - 1 < self.width and 0 <= y < self.height:
                self.base_grid[y][room_x + width - 1] = TileType.STONE_WALL
                self.collision_grid[y][room_x + width - 1] = True
        
        # Add a doorway (entrance)
        door_wall = random.choice(['top', 'bottom', 'left', 'right'])
        
        if door_wall == 'top' and width > 2:
            door_x = room_x + random.randint(1, width - 2)
            if 0 <= door_x < self.width and 0 <= room_y < self.height:
                self.base_grid[room_y][door_x] = self.base_grid[room_y+1][door_x]  # Match the floor inside
                self.collision_grid[room_y][door_x] = False
        
        elif door_wall == 'bottom' and width > 2:
            door_x = room_x + random.randint(1, width - 2)
            if 0 <= door_x < self.width and 0 <= room_y + height - 1 < self.height:
                self.base_grid[room_y + height - 1][door_x] = self.base_grid[room_y + height - 2][door_x]
                self.collision_grid[room_y + height - 1][door_x] = False
        
        elif door_wall == 'left' and height > 2:
            door_y = room_y + random.randint(1, height - 2)
            if 0 <= room_x < self.width and 0 <= door_y < self.height:
                self.base_grid[door_y][room_x] = self.base_grid[door_y][room_x + 1]
                self.collision_grid[door_y][room_x] = False
        
        elif door_wall == 'right' and height > 2:
            door_y = room_y + random.randint(1, height - 2)
            if 0 <= room_x + width - 1 < self.width and 0 <= door_y < self.height:
                self.base_grid[door_y][room_x + width - 1] = self.base_grid[door_y][room_x + width - 2]
                self.collision_grid[door_y][room_x + width - 1] = False
        
        print(f"DEBUG: Room created with {wall_count} wall tiles")
    
    def _create_ruins(self):
        """Create ruins with incomplete walls."""
        # Choose random position that's not too close to the borders
        ruin_x = random.randint(10, self.width - 15)
        ruin_y = random.randint(10, self.height - 15)
        
        # Ruin dimensions
        width = random.randint(6, 10)
        height = random.randint(6, 10)
        
        # Create partial walls with gaps
        for x in range(ruin_x, ruin_x + width):
            # Top and bottom walls with gaps
            if random.random() < 0.7:  # 70% chance to place a wall segment
                if 0 <= x < self.width and 0 <= ruin_y < self.height:
                    self.base_grid[ruin_y][x] = TileType.STONE_WALL
                    self.collision_grid[ruin_y][x] = True
            
            if random.random() < 0.7:
                if 0 <= x < self.width and 0 <= ruin_y + height - 1 < self.height:
                    self.base_grid[ruin_y + height - 1][x] = TileType.STONE_WALL
                    self.collision_grid[ruin_y + height - 1][x] = True
        
        # Left and right walls with gaps
        for y in range(ruin_y, ruin_y + height):
            if random.random() < 0.7:
                if 0 <= ruin_x < self.width and 0 <= y < self.height:
                    self.base_grid[y][ruin_x] = TileType.STONE_WALL
                    self.collision_grid[y][ruin_x] = True
            
            if random.random() < 0.7:
                if 0 <= ruin_x + width - 1 < self.width and 0 <= y < self.height:
                    self.base_grid[y][ruin_x + width - 1] = TileType.STONE_WALL
                    self.collision_grid[y][ruin_x + width - 1] = True
    
    def _create_wall(self):
        """Create a straight or L-shaped wall."""
        # Choose random position and direction
        wall_x = random.randint(10, self.width - 15)
        wall_y = random.randint(10, self.height - 15)
        wall_length = random.randint(5, 12)
        
        # Choose wall type and direction
        wall_type = random.choice(['straight', 'L-shaped'])
        direction = random.choice(['horizontal', 'vertical'])
        
        if wall_type == 'straight':
            if direction == 'horizontal':
                # Create horizontal wall
                for x in range(wall_x, wall_x + wall_length):
                    if 0 <= x < self.width and 0 <= wall_y < self.height:
                        self.base_grid[wall_y][x] = TileType.STONE_WALL
                        self.collision_grid[wall_y][x] = True
            else:
                # Create vertical wall
                for y in range(wall_y, wall_y + wall_length):
                    if 0 <= wall_x < self.width and 0 <= y < self.height:
                        self.base_grid[y][wall_x] = TileType.STONE_WALL
                        self.collision_grid[y][wall_x] = True
        
        elif wall_type == 'L-shaped':
            # First leg length
            leg1_length = wall_length // 2
            
            if direction == 'horizontal':
                # First leg horizontal
                for x in range(wall_x, wall_x + leg1_length):
                    if 0 <= x < self.width and 0 <= wall_y < self.height:
                        self.base_grid[wall_y][x] = TileType.STONE_WALL
                        self.collision_grid[wall_y][x] = True
                
                # Second leg vertical (down)
                for y in range(wall_y, wall_y + wall_length - leg1_length):
                    if 0 <= wall_x + leg1_length - 1 < self.width and 0 <= y < self.height:
                        self.base_grid[y][wall_x + leg1_length - 1] = TileType.STONE_WALL
                        self.collision_grid[y][wall_x + leg1_length - 1] = True
            else:
                # First leg vertical
                for y in range(wall_y, wall_y + leg1_length):
                    if 0 <= wall_x < self.width and 0 <= y < self.height:
                        self.base_grid[y][wall_x] = TileType.STONE_WALL
                        self.collision_grid[y][wall_x] = True
                
                # Second leg horizontal (right)
                for x in range(wall_x, wall_x + wall_length - leg1_length):
                    if 0 <= x < self.width and 0 <= wall_y + leg1_length - 1 < self.height:
                        self.base_grid[wall_y + leg1_length - 1][x] = TileType.STONE_WALL
                        self.collision_grid[wall_y + leg1_length - 1][x] = True 