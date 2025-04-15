"""
Dungeon generation module for the RPG game.
Implementation of the Veilmaster's Fortress dungeon from dungeonlayout.MD.
"""

import pygame
import random
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
from .map import Map, BiomeType
from .enums import TileType
from .constants import TILE_SIZE

class RoomType(Enum):
    """Types of rooms in the Veilmaster's Fortress dungeon."""
    ENTRANCE = "entrance"
    CORRIDOR = "corridor"
    OUTER_COURTYARD = "outer_courtyard"
    HALL_OF_ECHOES = "hall_of_echoes"
    GOLEM_FORGE = "golem_forge"
    CHASM_OF_WHISPERS = "chasm_of_whispers"
    GALLERY_OF_SHADOWS = "gallery_of_shadows"
    SANCTUM_OF_SEALS = "sanctum_of_seals"
    RITUAL_CHAMBER = "ritual_chamber"

class EntranceType(Enum):
    """Types of entrances to the Veilmaster's Fortress dungeon."""
    MAIN_GATE = "main_gate"
    COLLAPSED_TUNNEL = "collapsed_tunnel" 
    SKYBRIDGE = "skybridge"

class DungeonTile(Enum):
    """Special dungeon tile types for the Veilmaster's Fortress."""
    FLOOR = "dungeon_floor"
    WALL = "dungeon_wall"
    DOOR = "dungeon_door"
    LOCKED_DOOR = "locked_door" 
    STAIRS_UP = "stairs_up"
    STAIRS_DOWN = "stairs_down"
    INVISIBLE_BRIDGE = "invisible_bridge"
    PORTAL = "portal"
    BRAZIER = "brazier"
    WATER_BASIN = "water_basin"
    STATUE = "statue"
    CHIME = "chime"
    TITAN = "titan"
    PAINTING = "painting"

class PuzzleState(Enum):
    """States for puzzles in the dungeon."""
    UNSOLVED = "unsolved"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"

class Room:
    """Represents a room in the dungeon."""
    
    def __init__(self, room_type: RoomType, x: int, y: int, width: int, height: int):
        self.room_type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connected_rooms = []
        self.doors = []  # [(x, y), ...] coordinates of doors
        self.puzzle_state = PuzzleState.UNSOLVED if self._has_puzzle() else None
        self.special_features = []  # List of special features in the room
        
    def get_rect(self) -> pygame.Rect:
        """Get the rectangle representing this room."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, 
                          self.width * TILE_SIZE, self.height * TILE_SIZE)
    
    def _has_puzzle(self) -> bool:
        """Check if this room type has a puzzle."""
        puzzle_rooms = [
            RoomType.HALL_OF_ECHOES, 
            RoomType.GOLEM_FORGE,
            RoomType.CHASM_OF_WHISPERS,
            RoomType.GALLERY_OF_SHADOWS,
            RoomType.SANCTUM_OF_SEALS
        ]
        return self.room_type in puzzle_rooms
    
    def get_center(self) -> Tuple[int, int]:
        """Get the center coordinates of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def add_door(self, x: int, y: int):
        """Add a door to the room."""
        self.doors.append((x, y))
    
    def add_connection(self, room):
        """Connect this room to another room."""
        if room not in self.connected_rooms:
            self.connected_rooms.append(room)
            
    def contains_point(self, x: int, y: int) -> bool:
        """Check if this room contains the given point."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def is_border_tile(self, x: int, y: int) -> bool:
        """Check if the given coordinates are on the border of the room."""
        return (x == self.x or x == self.x + self.width - 1 or 
                y == self.y or y == self.y + self.height - 1)

class Dungeon(Map):
    """
    Dungeon map implementation for the Veilmaster's Fortress.
    Inherits from the base Map class and overrides generation methods.
    """
    
    def __init__(self, width: int, height: int, seed: Optional[int] = None):
        """Initialize the dungeon map."""
        super().__init__(width, height, seed)
        
        # Dungeon-specific properties
        self.rooms: List[Room] = []
        self.entrance_room = None
        self.ritual_chamber = None
        self.entrance_type = random.choice(list(EntranceType))
        self.corridors = []  # List of corridor coordinates
        self.puzzle_states = {}  # Dictionary of puzzle states
        
        # Special room coordinates for each type
        self.room_positions = {room_type: None for room_type in RoomType}
        
        # Override the map generation
        self._generate_dungeon()
    
    def _generate_dungeon(self):
        """Generate the Veilmaster's Fortress dungeon layout."""
        # Clear any existing map data
        self.base_grid = [[TileType.STONE for _ in range(self.width)] for _ in range(self.height)]
        self.decoration_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.collision_grid = [[True for _ in range(self.width)] for _ in range(self.height)]
        
        # Set ambient biome for the dungeon
        self.biome_grid = [[BiomeType.MOUNTAIN for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate the basic structure
        self._create_rooms()
        self._create_corridors()
        self._place_doors()
        self._add_special_features()
        
        # Update collision grid
        self._update_wall_rects()
        
        print(f"Dungeon generation complete with {len(self.rooms)} rooms")
    
    def _create_rooms(self):
        """Create the main rooms of the dungeon."""
        # Define the room layout - these values could be adjusted
        room_configs = {
            RoomType.ENTRANCE: {"min_size": (8, 8), "max_size": (12, 12)},
            RoomType.OUTER_COURTYARD: {"min_size": (15, 15), "max_size": (20, 20)},
            RoomType.HALL_OF_ECHOES: {"min_size": (12, 25), "max_size": (15, 30)},
            RoomType.GOLEM_FORGE: {"min_size": (14, 14), "max_size": (18, 18)},
            RoomType.CHASM_OF_WHISPERS: {"min_size": (16, 16), "max_size": (20, 20)},
            RoomType.GALLERY_OF_SHADOWS: {"min_size": (14, 14), "max_size": (18, 18)},
            RoomType.SANCTUM_OF_SEALS: {"min_size": (16, 16), "max_size": (20, 20)},
            RoomType.RITUAL_CHAMBER: {"min_size": (12, 12), "max_size": (16, 16)}
        }
        
        # Create one room for each type defined in the flow
        room_sequence = [
            RoomType.ENTRANCE,
            RoomType.OUTER_COURTYARD,
            RoomType.HALL_OF_ECHOES,
            RoomType.GOLEM_FORGE,
            RoomType.CHASM_OF_WHISPERS,
            RoomType.GALLERY_OF_SHADOWS,
            RoomType.SANCTUM_OF_SEALS,
            RoomType.RITUAL_CHAMBER
        ]
        
        # Calculate spacing for rooms based on map size
        total_rooms = len(room_sequence)
        vertical_spacing = self.height // (total_rooms + 1)
        
        # Place rooms in a sequence from bottom to top
        for i, room_type in enumerate(room_sequence):
            config = room_configs[room_type]
            min_width, min_height = config["min_size"]
            max_width, max_height = config["max_size"]
            
            # Randomize room size within constraints
            width = random.randint(min_width, max_width)
            height = random.randint(min_height, max_height)
            
            # Calculate position (centered horizontally, staggered vertically)
            x = (self.width - width) // 2
            # Add some horizontal variation
            x += random.randint(-10, 10)
            x = max(1, min(x, self.width - width - 1))
            
            # Position rooms from bottom to top with spacing
            y = self.height - (i + 1) * vertical_spacing - height // 2
            y = max(1, min(y, self.height - height - 1))
            
            # Create the room
            room = Room(room_type, x, y, width, height)
            self.rooms.append(room)
            
            # Store special rooms
            if room_type == RoomType.ENTRANCE:
                self.entrance_room = room
            elif room_type == RoomType.RITUAL_CHAMBER:
                self.ritual_chamber = room
            
            # Store room position for future reference
            self.room_positions[room_type] = (x, y, width, height)
            
            # Carve out the room in the map
            self._carve_room(room)
            
            print(f"Created {room_type.value} room at ({x}, {y}) with size {width}x{height}")
    
    def _carve_room(self, room: Room):
        """Carve out a room in the dungeon map."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                # Skip if outside map bounds
                if not (0 <= x < self.width and 0 <= y < self.height):
                    continue
                
                # Set floor for interior, walls for border
                if room.is_border_tile(x, y):
                    self.base_grid[y][x] = TileType.STONE_WALL
                    self.collision_grid[y][x] = True
                else:
                    self.base_grid[y][x] = TileType.STONE
                    self.collision_grid[y][x] = False
    
    def _create_corridors(self):
        """Create corridors connecting the rooms."""
        # Connect each room to the next in sequence
        for i in range(len(self.rooms) - 1):
            current_room = self.rooms[i]
            next_room = self.rooms[i + 1]
            
            # Connect the rooms
            self._connect_rooms(current_room, next_room)
            
            # Register the connection
            current_room.add_connection(next_room)
            next_room.add_connection(current_room)
        
        # Add a few more connections for non-linearity (shortcuts)
        num_extra_connections = random.randint(2, 4)
        available_rooms = self.rooms.copy()
        
        for _ in range(num_extra_connections):
            if len(available_rooms) < 2:
                break
                
            # Pick two random rooms that aren't already directly connected
            room1 = random.choice(available_rooms)
            available_rooms.remove(room1)
            
            candidates = [r for r in available_rooms if r not in room1.connected_rooms]
            if not candidates:
                continue
                
            room2 = random.choice(candidates)
            
            # Connect the rooms with a corridor
            self._connect_rooms(room1, room2)
            
            # Register the connection
            room1.add_connection(room2)
            room2.add_connection(room1)
    
    def _connect_rooms(self, room1: Room, room2: Room):
        """Create a corridor between two rooms."""
        start_x, start_y = room1.get_center()
        end_x, end_y = room2.get_center()
        
        # Use L-shaped corridors
        # First go horizontally
        current_x, current_y = start_x, start_y
        
        # Carve horizontal corridor
        while current_x != end_x:
            step_x = 1 if current_x < end_x else -1
            current_x += step_x
            
            # Skip if inside a room
            if any(room.contains_point(current_x, current_y) for room in self.rooms):
                continue
                
            # Create corridor tile
            if 0 <= current_x < self.width and 0 <= current_y < self.height:
                self.base_grid[current_y][current_x] = TileType.STONE
                self.collision_grid[current_y][current_x] = False
                self.corridors.append((current_x, current_y))
                
                # Add walls alongside corridor
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    nx, ny = current_x + dx, current_y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and 
                            self.base_grid[ny][nx] != TileType.STONE and
                            not any(room.contains_point(nx, ny) for room in self.rooms)):
                        self.base_grid[ny][nx] = TileType.STONE_WALL
                        self.collision_grid[ny][nx] = True
        
        # Then go vertically
        while current_y != end_y:
            step_y = 1 if current_y < end_y else -1
            current_y += step_y
            
            # Skip if inside a room
            if any(room.contains_point(current_x, current_y) for room in self.rooms):
                continue
                
            # Create corridor tile
            if 0 <= current_x < self.width and 0 <= current_y < self.height:
                self.base_grid[current_y][current_x] = TileType.STONE
                self.collision_grid[current_y][current_x] = False
                self.corridors.append((current_x, current_y))
                
                # Add walls alongside corridor
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    nx, ny = current_x + dx, current_y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and 
                            self.base_grid[ny][nx] != TileType.STONE and
                            not any(room.contains_point(nx, ny) for room in self.rooms)):
                        self.base_grid[ny][nx] = TileType.STONE_WALL
                        self.collision_grid[ny][nx] = True
    
    def _place_doors(self):
        """Place doors at room entrances."""
        # Check corridor tiles that are adjacent to room borders
        for x, y in self.corridors:
            # Check all adjacent tiles
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Skip if outside map
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                
                # If this is a wall tile, check if it's part of a room border
                if self.base_grid[ny][nx] == TileType.STONE_WALL:
                    for room in self.rooms:
                        if room.is_border_tile(nx, ny):
                            # Place a door here
                            self.base_grid[ny][nx] = TileType.DOOR
                            self.collision_grid[ny][nx] = False
                            room.add_door(nx, ny)
                            break
    
    def _add_special_features(self):
        """Add special features to rooms based on their type."""
        for room in self.rooms:
            if room.room_type == RoomType.HALL_OF_ECHOES:
                self._add_hall_of_echoes_features(room)
            elif room.room_type == RoomType.GOLEM_FORGE:
                self._add_golem_forge_features(room)
            elif room.room_type == RoomType.CHASM_OF_WHISPERS:
                self._add_chasm_features(room)
            elif room.room_type == RoomType.GALLERY_OF_SHADOWS:
                self._add_gallery_features(room)
            elif room.room_type == RoomType.SANCTUM_OF_SEALS:
                self._add_sanctum_features(room)
            elif room.room_type == RoomType.RITUAL_CHAMBER:
                self._add_ritual_chamber_features(room)
    
    def _add_hall_of_echoes_features(self, room: Room):
        """Add shifting walls puzzle to Hall of Echoes."""
        center_x, center_y = room.get_center()
        
        # Add some decorative elements that hint at sound-based mechanics
        for _ in range(5):
            x = random.randint(room.x + 1, room.x + room.width - 2)
            y = random.randint(room.y + 1, room.y + room.height - 2)
            
            # Place soundwave-like markings (represented as special decoration)
            self.decoration_grid[y][x] = TileType.ROCK
    
    def _add_golem_forge_features(self, room: Room):
        """Add Titan's Core puzzle to Golem Forge."""
        center_x, center_y = room.get_center()
        
        # Place the Titan in the center
        if 0 <= center_x < self.width and 0 <= center_y < self.height:
            self.decoration_grid[center_y][center_x] = TileType.ROCK
            
        # Place the three fragments around the room
        for i in range(3):
            angle = i * (2 * math.pi / 3)
            radius = min(room.width, room.height) // 3
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            if (room.x < x < room.x + room.width - 1 and 
                room.y < y < room.y + room.height - 1):
                self.decoration_grid[y][x] = TileType.ROCK
    
    def _add_chasm_features(self, room: Room):
        """Add invisible bridge puzzle to Chasm of Whispers."""
        center_x, center_y = room.get_center()
        
        # Create a chasm (water) in the center
        chasm_width = room.width // 2
        chasm_height = room.height // 2
        
        for y in range(center_y - chasm_height//2, center_y + chasm_height//2):
            for x in range(center_x - chasm_width//2, center_x + chasm_width//2):
                if (room.x < x < room.x + room.width - 1 and 
                    room.y < y < room.y + room.height - 1):
                    self.base_grid[y][x] = TileType.WATER
                    
        # Create invisible bridge path (normal floor but with special visual cue)
        bridge_start_x = center_x - chasm_width//2
        bridge_end_x = center_x + chasm_width//2
        
        # Path with some curves
        current_x = bridge_start_x
        current_y = center_y + random.randint(-2, 2)
        
        while current_x <= bridge_end_x:
            if (room.x < current_x < room.x + room.width - 1 and 
                room.y < current_y < room.y + room.height - 1):
                self.base_grid[current_y][current_x] = TileType.STONE
                self.collision_grid[current_y][current_x] = False
                
            current_x += 1
            if random.random() < 0.3:  # 30% chance to move vertically
                current_y += random.choice([-1, 1])
    
    def _add_gallery_features(self, room: Room):
        """Add portal painting puzzle to Gallery of Shadows."""
        # Add paintings along the walls
        for i in range(4):  # 4 paintings
            # Choose a wall
            wall = random.choice(["top", "bottom", "left", "right"])
            
            if wall == "top":
                x = random.randint(room.x + 2, room.x + room.width - 3)
                y = room.y + 1
            elif wall == "bottom":
                x = random.randint(room.x + 2, room.x + room.width - 3)
                y = room.y + room.height - 2
            elif wall == "left":
                x = room.x + 1
                y = random.randint(room.y + 2, room.y + room.height - 3)
            else:  # right
                x = room.x + room.width - 2
                y = random.randint(room.y + 2, room.y + room.height - 3)
                
            # Place the painting
            if 0 <= x < self.width and 0 <= y < self.height:
                self.decoration_grid[y][x] = TileType.ROCK
    
    def _add_sanctum_features(self, room: Room):
        """Add elemental seal puzzle to Sanctum of Seals."""
        center_x, center_y = room.get_center()
        
        # Create four "sealed doors" in the cardinal directions
        door_positions = [
            (center_x, room.y + 1),  # North
            (center_x, room.y + room.height - 2),  # South
            (room.x + 1, center_y),  # West
            (room.x + room.width - 2, center_y)  # East
        ]
        
        # Add one elemental seal feature near each door
        features = [TileType.ROCK, TileType.WATER, TileType.STONE, TileType.BUSH]
        
        for i, (x, y) in enumerate(door_positions):
            if 0 <= x < self.width and 0 <= y < self.height:
                # Place locked door
                self.base_grid[y][x] = TileType.STONE_WALL
                self.collision_grid[y][x] = True
                
                # Place the element symbol nearby
                element_x = x + random.randint(-2, 2)
                element_y = y + random.randint(-2, 2)
                
                if (room.x < element_x < room.x + room.width - 1 and 
                    room.y < element_y < room.y + room.height - 1):
                    self.decoration_grid[element_y][element_x] = features[i]
    
    def _add_ritual_chamber_features(self, room: Room):
        """Add final boss area features to Ritual Chamber."""
        center_x, center_y = room.get_center()
        
        # Create a circular ritual area in the center
        radius = min(room.width, room.height) // 4
        
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                if (room.x < x < room.x + room.width - 1 and 
                    room.y < y < room.y + room.height - 1):
                    # Calculate distance from center
                    dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    
                    if dist <= radius:
                        # Create ritual circle
                        self.base_grid[y][x] = TileType.DIRT
                        
                    if abs(dist - radius) < 0.5:
                        # Create circle border
                        self.decoration_grid[y][x] = TileType.ROCK
        
        # Place the boss in the center
        self.decoration_grid[center_y][center_x] = TileType.ROCK
    
    def get_spawn_position(self) -> Tuple[int, int]:
        """Get the spawn position for the player in the dungeon."""
        if self.entrance_room:
            # Spawn near the entrance
            center_x, center_y = self.entrance_room.get_center()
            return center_x, center_y
        
        # Fallback to default
        return super().get_spawn_position()
    
    def get_exit_position(self) -> Tuple[int, int]:
        """Get the position of the dungeon exit (ritual chamber)."""
        if self.ritual_chamber:
            center_x, center_y = self.ritual_chamber.get_center()
            return center_x, center_y
        
        # Fallback
        return self.width // 2, self.height // 2 