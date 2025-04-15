"""
Town map implementation for the RPG game.
This serves as the starting hub area where players can interact with NPCs, acquire quests, etc.
"""

import pygame
import random
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
from .map import Map, BiomeType
from .enums import TileType

class TownMapTile(Enum):
    """Special town map tile types."""
    COBBLESTONE = "cobblestone"
    BUILDING = "building"
    SHOP = "shop"
    TAVERN = "tavern"
    BLACKSMITH = "blacksmith"
    FOUNTAIN = "fountain"
    MARKET_STALL = "market_stall"
    INN = "inn"
    DUNGEON_ENTRANCE = "dungeon_entrance"
    ELDER_HOME = "elder_home"  # Added Elder Malik's home

class TownMap(Map):
    """
    Town map implementation serving as the hub area.
    Players start here and can interact with NPCs to acquire quests.
    """
    
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        """Initialize the town map."""
        super().__init__(width, height, seed)
        
        # Town-specific properties
        self.buildings = []  # [(x, y, width, height, type), ...]
        self.npcs = []  # List of NPC positions for spawning
        self.quest_givers = []  # List of quest giver positions
        self.dungeon_entrance = None  # Position of the entrance to the Veilmaster's Fortress
        self.special_locations = {}  # Dictionary of special locations like Elder Malik's home
        
        # Override the map generation
        self._generate_town()
    
    def _generate_town(self):
        """Generate the town layout."""
        # Clear any existing map data
        self.base_grid = [[TileType.GRASS for _ in range(self.width)] for _ in range(self.height)]
        self.decoration_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.collision_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Set ambient biome for the town
        self.biome_grid = [[BiomeType.PLAINS for _ in range(self.width)] for _ in range(self.height)]
        
        # Create streets/paths
        self._create_streets()
        
        # Place buildings
        self._place_buildings()
        
        # Place decorations
        self._place_decorations()
        
        # Place special buildings
        self._place_special_buildings()
        
        # Place NPCs and quest givers
        self._place_npcs()
        
        # Place dungeon entrance
        self._place_dungeon_entrance()
        
        # Update collision grid for buildings
        self._update_collision_grid()
        
        print(f"Town generation complete with {len(self.buildings)} buildings")
    
    def _create_streets(self):
        """Create a street layout for the town."""
        # Create main road east-west through center of town
        center_y = self.height // 2
        for x in range(0, self.width):
            for y in range(center_y - 2, center_y + 3):  # 5 tiles wide
                if 0 <= y < self.height:
                    self.base_grid[y][x] = TileType.DIRT
                    
        # Create north-south road through center of town
        center_x = self.width // 2
        for y in range(0, self.height):
            for x in range(center_x - 2, center_x + 3):  # 5 tiles wide
                if 0 <= x < self.width:
                    self.base_grid[y][x] = TileType.DIRT
        
        # Create some side streets
        num_side_streets = random.randint(3, 5)
        for _ in range(num_side_streets):
            if random.choice([True, False]):  # Horizontal street
                y = random.randint(10, self.height - 10)
                if abs(y - center_y) < 15:  # Not too close to main street
                    continue
                    
                for x in range(0, self.width):
                    for dy in range(-1, 2):  # 3 tiles wide
                        if 0 <= y + dy < self.height:
                            self.base_grid[y + dy][x] = TileType.DIRT
            else:  # Vertical street
                x = random.randint(10, self.width - 10)
                if abs(x - center_x) < 15:  # Not too close to main street
                    continue
                    
                for y in range(0, self.height):
                    for dx in range(-1, 2):  # 3 tiles wide
                        if 0 <= x + dx < self.width:
                            self.base_grid[y][x + dx] = TileType.DIRT
    
    def _place_buildings(self):
        """Place buildings in the town."""
        # List of building types with their dimensions and importance
        building_types = [
            ("INN", (10, 8), True),  # (type, (width, height), is_important)
            ("TAVERN", (8, 8), True),
            ("BLACKSMITH", (6, 8), True),
            ("SHOP", (8, 6), True),
            ("BUILDING", (6, 6), False),  # Regular houses
            ("BUILDING", (5, 7), False),
            ("BUILDING", (7, 5), False),
            ("MARKET_STALL", (3, 3), True)
        ]
        
        # Place important buildings first near the center
        center_x, center_y = self.width // 2, self.height // 2
        important_buildings = [b for b in building_types if b[2]]
        
        # Place important buildings around the main square
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Four quadrants around center
        
        for i, (building_type, size, _) in enumerate(important_buildings):
            if i < len(directions):
                dir_x, dir_y = directions[i]
                offset_x = random.randint(10, 20) * dir_x
                offset_y = random.randint(10, 20) * dir_y
                
                # Position building near street but not on it
                building_x = center_x + offset_x
                building_y = center_y + offset_y
                
                # Adjust to not overlap with streets
                if self.base_grid[building_y][building_x] == TileType.DIRT:
                    if dir_x > 0:
                        building_x += size[0] // 2 + 2
                    else:
                        building_x -= size[0] // 2 + 2
                        
                    if dir_y > 0:
                        building_y += size[1] // 2 + 2
                    else:
                        building_y -= size[1] // 2 + 2
                
                # Check if area is clear
                area_clear = True
                for y in range(building_y, building_y + size[1]):
                    for x in range(building_x, building_x + size[0]):
                        if not (0 <= x < self.width and 0 <= y < self.height):
                            area_clear = False
                            break
                        if any(self._is_point_in_building(x, y, b) for b in self.buildings):
                            area_clear = False
                            break
                    if not area_clear:
                        break
                
                if area_clear:
                    self.buildings.append((building_x, building_y, size[0], size[1], building_type))
                    self._place_building(building_x, building_y, size[0], size[1], building_type)
        
        # Fill in with regular buildings
        regular_buildings = [b for b in building_types if not b[2]]
        attempts = 100  # Limit attempts to prevent infinite loop
        
        while attempts > 0 and len(self.buildings) < 15:
            attempts -= 1
            
            # Pick a random building type
            building_type, size, _ = random.choice(regular_buildings)
            
            # Find a spot near a street
            for _ in range(20):  # Try 20 times to find a spot
                # Find a road tile
                road_x, road_y = random.randint(5, self.width - 6), random.randint(5, self.height - 6)
                if self.base_grid[road_y][road_x] != TileType.DIRT:
                    continue
                
                # Find a place nearby but not on the road
                offsets = [(5, 0), (-5, 0), (0, 5), (0, -5)]
                random.shuffle(offsets)
                
                for offset_x, offset_y in offsets:
                    building_x = road_x + offset_x
                    building_y = road_y + offset_y
                    
                    # Check boundaries
                    if not (5 <= building_x < self.width - size[0] - 5 and 
                            5 <= building_y < self.height - size[1] - 5):
                        continue
                    
                    # Check if area is clear
                    area_clear = True
                    for y in range(building_y - 1, building_y + size[1] + 1):
                        for x in range(building_x - 1, building_x + size[0] + 1):
                            if not (0 <= x < self.width and 0 <= y < self.height):
                                area_clear = False
                                break
                            # Check if this point is part of any existing building
                            if any(self._is_point_in_building(x, y, b) for b in self.buildings):
                                area_clear = False
                                break
                            # Check if this is a road tile
                            if self.base_grid[y][x] == TileType.DIRT:
                                area_clear = False
                                break
                        if not area_clear:
                            break
                    
                    if area_clear:
                        self.buildings.append((building_x, building_y, size[0], size[1], building_type))
                        self._place_building(building_x, building_y, size[0], size[1], building_type)
                        break
    
    def _is_point_in_building(self, x, y, building):
        """Check if a point is inside or bordering a building."""
        bx, by, bw, bh, _ = building
        return bx - 1 <= x <= bx + bw and by - 1 <= y <= by + bh
    
    def _place_building(self, x, y, w, h, building_type):
        """Place a building at the specified location."""
        # Add building to the list
        self.buildings.append((x, y, w, h, building_type))
        
        # Update the tiles
        for by in range(y, y + h):
            for bx in range(x, x + w):
                if 0 <= bx < self.width and 0 <= by < self.height:
                    self.base_grid[by][bx] = TileType.STONE_WALL
                    self.collision_grid[by][bx] = True
    
    def _place_decorations(self):
        """Place decorations around the town."""
        # Add a fountain in the town center
        center_x, center_y = self.width // 2, self.height // 2
        fountain_size = 3
        
        for y in range(center_y - fountain_size, center_y + fountain_size + 1):
            for x in range(center_x - fountain_size, center_x + fountain_size + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Check if it's within a circular area
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    if distance <= fountain_size:
                        self.base_grid[y][x] = TileType.WATER
                        
        # Add trees and bushes at the edges of town
        for _ in range(50):
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Only place on grass and away from buildings/roads
            if (self.base_grid[y][x] == TileType.GRASS and 
                not any(self._is_point_in_building(x, y, b) for b in self.buildings) and
                not any(self.base_grid[y+dy][x+dx] == TileType.DIRT 
                       for dx in range(-1, 2) for dy in range(-1, 2)
                       if 0 <= x+dx < self.width and 0 <= y+dy < self.height)):
                
                decoration = random.choice([TileType.TREE, TileType.BUSH, TileType.ROCK])
                self.decoration_grid[y][x] = decoration
                
                # Trees block movement
                if decoration == TileType.TREE:
                    self.collision_grid[y][x] = True
    
    def _place_special_buildings(self):
        """Place special buildings like Elder Malik's home."""
        # Place Elder Malik's home near the center of town
        center_x, center_y = self.width // 2, self.height // 2
        
        # Try to place the Elder's home in a significant location
        elder_home_placed = False
        elder_width, elder_height = 8, 8  # Larger than average building
        
        # Try to place it in a dignified location north of the center
        if not elder_home_placed:
            elder_x, elder_y = center_x - elder_width // 2, center_y - 20
            
            # Check if the space is clear
            clear = True
            for y in range(elder_y, elder_y + elder_height):
                for x in range(elder_x, elder_x + elder_width):
                    if (not self._is_in_bounds(x, y) or 
                        self.collision_grid[y][x] or 
                        self.base_grid[y][x] != TileType.GRASS):
                        clear = False
                        break
                if not clear:
                    break
            
            if clear:
                # Place the Elder's home
                self._place_building(elder_x, elder_y, elder_width, elder_height, TownMapTile.ELDER_HOME)
                elder_home_placed = True
                self.special_locations["elder_home"] = (elder_x + elder_width // 2, elder_y + elder_height)
                print(f"Placed Elder Malik's home at {elder_x}, {elder_y}")
        
        # If we couldn't place it in the ideal spot, try somewhere else
        if not elder_home_placed:
            for attempt in range(10):  # Try 10 times
                elder_x = random.randint(10, self.width - elder_width - 10)
                elder_y = random.randint(10, self.height - elder_height - 10)
                
                # Check if the space is clear
                clear = True
                for y in range(elder_y, elder_y + elder_height):
                    for x in range(elder_x, elder_x + elder_width):
                        if (not self._is_in_bounds(x, y) or 
                            self.collision_grid[y][x] or 
                            self.base_grid[y][x] != TileType.GRASS):
                            clear = False
                            break
                    if not clear:
                        break
                
                if clear:
                    # Place the Elder's home
                    self._place_building(elder_x, elder_y, elder_width, elder_height, TownMapTile.ELDER_HOME)
                    elder_home_placed = True
                    self.special_locations["elder_home"] = (elder_x + elder_width // 2, elder_y + elder_height)
                    print(f"Placed Elder Malik's home at {elder_x}, {elder_y}")
                    break
    
    def _place_npcs(self):
        """Place NPCs and quest givers around the town."""
        # Find potential NPC spots near buildings
        for building in self.buildings:
            bx, by, bw, bh, building_type = building
            
            # Special handling for Elder Malik's home
            if building_type == TownMapTile.ELDER_HOME:
                # Elder Malik should be placed outside his home
                entrance_x, entrance_y = bx + bw // 2, by + bh
                if self._is_in_bounds(entrance_x, entrance_y) and not self.collision_grid[entrance_y][entrance_x]:
                    # Add Elder Malik as the first quest giver (important!)
                    self.quest_givers.insert(0, (entrance_x, entrance_y))
            
            # Place quest givers in important buildings
            elif building_type in [TownMapTile.INN, TownMapTile.TAVERN, TownMapTile.BLACKSMITH, TownMapTile.SHOP]:
                # Find a position just outside the building entrance
                entrance_x, entrance_y = bx + bw // 2, by + bh
                if self._is_in_bounds(entrance_x, entrance_y) and not self.collision_grid[entrance_y][entrance_x]:
                    self.quest_givers.append((entrance_x, entrance_y))
                else:
                    # Try other sides if front is blocked
                    sides = [(bx - 1, by + bh // 2), (bx + bw, by + bh // 2), (bx + bw // 2, by - 1)]
                    for sx, sy in sides:
                        if (self._is_in_bounds(sx, sy) and 
                            not self.collision_grid[sy][sx] and 
                            self.base_grid[sy][sx] != TileType.STONE_WALL):
                            self.quest_givers.append((sx, sy))
                            break
            
            # Place regular NPCs around buildings
            for _ in range(random.randint(1, 3)):
                # Find a position near the building
                offset_x = random.randint(-2, bw + 1)
                offset_y = random.randint(-2, bh + 1)
                
                nx, ny = bx + offset_x, by + offset_y
                
                # Make sure it's on a valid tile and not colliding
                if (self._is_in_bounds(nx, ny) and
                    not self.collision_grid[ny][nx] and
                    self.base_grid[ny][nx] != TileType.WATER):
                    self.npcs.append((nx, ny))
    
    def _is_in_bounds(self, x, y):
        """Check if coordinates are within map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _place_dungeon_entrance(self):
        """Place the entrance to the Veilmaster's Fortress dungeon."""
        # Place it at the north edge of town
        center_x = self.width // 2
        entrance_y = 10  # Near the north edge, but not at the very edge
        
        # Find a spot on the north road
        for y in range(entrance_y - 5, entrance_y + 6):
            if self.base_grid[y][center_x] == TileType.DIRT:
                # Place a distinct entrance structure
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if 0 <= center_x + dx < self.width and 0 <= y + dy < self.height:
                            # Create a stone structure
                            if abs(dx) == 2 or abs(dy) == 2:
                                self.base_grid[y + dy][center_x + dx] = TileType.STONE_WALL
                                self.collision_grid[y + dy][center_x + dx] = True
                
                # Mark the entrance position
                self.dungeon_entrance = (center_x, y)
                
                # Make the actual entrance tile non-blocking
                self.collision_grid[y][center_x] = False
                break
    
    def _update_collision_grid(self):
        """Update the collision grid based on the placed objects."""
        for y in range(self.height):
            for x in range(self.width):
                # Buildings and trees block movement
                if self.base_grid[y][x] == TileType.STONE_WALL:
                    self.collision_grid[y][x] = True
                elif self.decoration_grid[y][x] == TileType.TREE:
                    self.collision_grid[y][x] = True
                # Water blocks movement
                elif self.base_grid[y][x] == TileType.WATER:
                    self.collision_grid[y][x] = True
    
    def get_spawn_position(self) -> Tuple[int, int]:
        """Get the spawn position for the player in the town."""
        # Spawn near the center of town
        center_x, center_y = self.width // 2, self.height // 2
        return center_x, center_y + 5  # Just south of the center fountain
    
    def get_quest_giver_positions(self) -> List[Tuple[int, int]]:
        """Get the positions of all quest givers in the town."""
        return self.quest_givers
    
    def get_special_location(self, location_id: str) -> Optional[Tuple[int, int]]:
        """Get the position of a special location by ID."""
        return self.special_locations.get(location_id)
    
    def get_elder_malik_position(self) -> Optional[Tuple[int, int]]:
        """Get Elder Malik's position."""
        if len(self.quest_givers) > 0:
            return self.quest_givers[0]  # Elder Malik is always the first quest giver
        return None
    
    def get_dungeon_entrance_position(self) -> Optional[Tuple[int, int]]:
        """Get the position of the entrance to the Veilmaster's Fortress dungeon."""
        return self.dungeon_entrance 