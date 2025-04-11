"""
Main game module.
"""

import pygame
import random
import math
import os
from typing import Dict, List, Tuple, Optional, Union
from rpg_modules.items import ItemGenerator, Item, Weapon, Armor, Hands, Consumable
from rpg_modules.items.base import Inventory, Equipment
from rpg_modules.ui import InventoryUI, EquipmentUI, ItemGeneratorUI as GeneratorUI, QuestUI
from rpg_modules.entities import Player
from rpg_modules.entities.monster import Monster, MonsterType
from rpg_modules.quests import QuestGenerator, QuestType, QuestLog
from rpg_modules.core.map import Map
from rpg_modules.core.camera import Camera
from rpg_modules.core.assets import load_assets as load_core_assets
from rpg_modules.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    WHITE, BLACK, RED, GREEN, BLUE, GRAY,
    QUALITY_COLORS, UI_DIMENSIONS
)
from rpg_modules.core.map import TileType

# Player stats
PLAYER_HP = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5

# Monster stats
MONSTER_HP = 50
MONSTER_ATTACK = 5
MONSTER_DEFENSE = 2
MAX_MONSTERS = 30  # Maximum number of monsters allowed at once

# Asset paths
ASSET_PATH = "assets"
FLOOR_IMAGE = "floor.png"
WALL_IMAGE = "wall.png"
PLAYER_IMAGE = "player.png"
MONSTER_IMAGE = "monster.png"

def load_assets():
    """Load all game assets"""
    print("Loading assets...")
    
    # Load assets from the core module
    assets = load_core_assets()
    
    # Now add any game-specific assets that aren't in the core assets
    
    # Create placeholder assets directory if it doesn't exist
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
        print(f"Created assets directory at {ASSET_PATH}")
    
    # Add player image if not already in assets
    if 'player' not in assets:
        player_path = os.path.join(ASSET_PATH, "animations", "player.png")
        if not os.path.exists(player_path):
            # Create the animations directory if it doesn't exist
            os.makedirs(os.path.dirname(player_path), exist_ok=True)
            # Create a simple character sprite
            player_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(player_surface, (50, 100, 200), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//3)  # Body
            pygame.draw.circle(player_surface, (200, 150, 100), (TILE_SIZE//2, TILE_SIZE//3), TILE_SIZE//4)  # Head
            pygame.image.save(player_surface, player_path)
            print(f"Created player image at {player_path}")
            assets['player'] = pygame.image.load(player_path).convert_alpha()
    
    # Add monster image if not already in assets
    if 'monster' not in assets:
        monster_path = os.path.join(ASSET_PATH, MONSTER_IMAGE)
        if not os.path.exists(monster_path):
            monster_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # Create a simple monster sprite
            pygame.draw.polygon(monster_surface, (200, 50, 50),  # Red triangle body
                              [(TILE_SIZE//2, TILE_SIZE//4),
                               (TILE_SIZE//4, TILE_SIZE*3//4),
                               (TILE_SIZE*3//4, TILE_SIZE*3//4)])
            # Add eyes
            pygame.draw.circle(monster_surface, (255, 255, 255),
                             (TILE_SIZE*3//8, TILE_SIZE//2), 2)
            pygame.draw.circle(monster_surface, (255, 255, 255),
                             (TILE_SIZE*5//8, TILE_SIZE//2), 2)
            pygame.image.save(monster_surface, monster_path)
            print(f"Created monster image at {monster_path}")
            assets['monster'] = pygame.image.load(monster_path).convert_alpha()
    
    print("Assets loaded successfully")
    print("Available assets:", list(assets.keys()))
    return assets

# Game states
class GameState:
    """Manages the global game state."""
    
    def __init__(self, screen):
        """Initialize the game state."""
        print("\n=== Initializing Game State ===")
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Create game map
        print("Creating game map...")
        self.map = Map()
        print(f"Map created with dimensions: {self.map.width}x{self.map.height}")
        
        # Create player at center of map
        print("Creating player...")
        spawn_pos = (self.map.width * TILE_SIZE // 2, self.map.height * TILE_SIZE // 2)  # Center of map in pixels
        print(f"Player spawn position: ({spawn_pos[0] // TILE_SIZE}, {spawn_pos[1] // TILE_SIZE})")
        self.player = Player(spawn_pos[0], spawn_pos[1])
        # Initialize the inventory with empty slots instead of empty list
        self.player.inventory = Inventory()
        # Initialize the equipment as Equipment instance instead of empty dict
        self.player.equipment = Equipment()
        print("Player created with proper inventory")
        
        # Create camera
        print("Creating camera...")
        self.camera = Camera(self.player)
        self.camera.set_map_bounds(self.map.width * TILE_SIZE, self.map.height * TILE_SIZE)
        print("Camera created")
        
        # Initialize monsters list and counts
        print("\nInitializing monster system...")
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        
        # Create UI elements with empty containers
        print("\nCreating UI elements...")
        self.quest_log = QuestLog()  # Create empty quest log
        # Connect UI to the player's inventory and equipment
        self.inventory_ui = InventoryUI(screen, self.player.inventory.items)  # Use player's inventory
        self.equipment_ui = EquipmentUI(screen, self.player.equipment.slots)  # Use player's equipment
        self.quest_ui = QuestUI(screen, self.quest_log)  # Quest UI with empty log
        
        # Position the generator UI - position on right side when visible
        generator_x = SCREEN_WIDTH - UI_DIMENSIONS['generator_width'] - 10
        generator_y = 10  # Top of screen
        self.generator_ui = GeneratorUI(generator_x, generator_y)
        print("UI elements created")
        
        # Load assets
        print("\nLoading assets...")
        self.assets = load_assets()
        self.camera.assets = self.assets
        print("Assets loaded")
        
        # Spawn initial monsters
        print("\n=== Spawning Initial Monsters ===")
        self._spawn_initial_monsters()
        print(f"Total monsters spawned: {len(self.monsters)}")
        for monster_type in MonsterType:
            if self.monster_counts[monster_type] > 0:
                print(f"- {monster_type.name}: {self.monster_counts[monster_type]}")
        
        print("\n=== Game State Initialized ===")
        
    def update(self, dt):
        """Update game state."""
        # Store all events so we can process them for both zoom and UI
        events = pygame.event.get()
        
        # Handle zoom and other events first
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom immediately
                if event.y > 0:  # Scroll up to zoom in
                    self.camera.zoom_in()
                elif event.y < 0:  # Scroll down to zoom out
                    self.camera.zoom_out()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset zoom with 'R' key
                    self.camera.reset_zoom()
                elif event.key == pygame.K_i:
                    # Toggle inventory and equipment together
                    self.inventory_ui.toggle()
                    self.equipment_ui.toggle()
                    # Hide generator UI when viewing inventory
                    if self.generator_ui.visible:
                        self.generator_ui.toggle()
                elif event.key == pygame.K_e:
                    # Toggle equipment and inventory together
                    self.equipment_ui.toggle()
                    self.inventory_ui.toggle()
                    # Hide generator UI when viewing equipment
                    if self.generator_ui.visible:
                        self.generator_ui.toggle()
                elif event.key == pygame.K_q:
                    self.quest_ui.toggle()
                elif event.key == pygame.K_g:
                    # Toggle generator UI and show inventory for items
                    self.generator_ui.toggle()
                    # Always ensure inventory is visible with generator
                    if self.generator_ui.visible and not self.inventory_ui.visible:
                        self.inventory_ui.toggle()
                    # Hide equipment UI when viewing generator
                    if self.equipment_ui.visible and self.generator_ui.visible:
                        self.equipment_ui.toggle()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Handle player input
        keys = pygame.key.get_pressed()
        walls = self.map.get_walls()
        # Only print wall count occasionally to reduce console spam
        if random.random() < 0.005:
            print(f"DEBUG: Passing {len(walls)} walls to player.handle_input()")
        self.player.handle_input(keys, walls)
            
        # Update player
        self.player.update(dt)
        
        # Update UI elements
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        self.inventory_ui.update()
        self.equipment_ui.update()
        self.quest_ui.update()
        self.generator_ui.update()
        
        # Pass events to UI elements after handling zoom
        for event in events:
            if event.type != pygame.MOUSEWHEEL:  # Skip wheel events for UI
                self.inventory_ui.handle_event(event)
                self.equipment_ui.handle_event(event)
                self.quest_ui.handle_event(event)
                if self.generator_ui.visible:  # Only handle events when visible
                    self.generator_ui.handle_event(event, self.player)
        
        # Update monsters
        for monster in self.monsters[:]:
            monster.update(dt, (self.player.x, self.player.y))
            
            # Check for monster death
            if monster.health <= 0:
                self._handle_monster_death(monster)
                continue
                
            # Handle monster attacks
            dx = monster.x - self.player.x
            dy = monster.y - self.player.y
            dist = (dx * dx + dy * dy) ** 0.5
            
            if dist <= monster.attack_range * TILE_SIZE and monster.can_attack():
                damage = monster.attack()
                print(f"{monster.monster_type.name} attacks player for {damage} damage!")
        
        # Try spawning new monsters occasionally
        if random.random() < 0.01:  # 1% chance each frame
            monster_type = random.choice([MonsterType.SLIME, MonsterType.SPIDER, MonsterType.WOLF])
            if self._try_spawn_monster(monster_type):
                print(f"New {monster_type.name} spawned!")
        
        # Update camera
        self.camera.update(self.player)
        
    def draw(self, screen):
        """Draw the game state."""
        # Clear screen
        screen.fill((40, 40, 40))  # Dark gray background
        
        # Draw game world
        self.map.draw(screen, self.camera, self.assets)
        
        # Draw monsters
        for monster in self.monsters:
            monster.draw(screen, self.camera)
        
        # Draw player
        self.player.draw(screen, self.camera)
        
        # Get current tile type at player position
        current_tile = self.map.get_tile_at_position(self.player.x, self.player.y)
        
        # Draw coordinates and terrain in top-left corner
        font = pygame.font.Font(None, 24)
        tile_x = int(self.player.x / TILE_SIZE)
        tile_y = int(self.player.y / TILE_SIZE)
        pixel_x = int(self.player.x)
        pixel_y = int(self.player.y)
        
        # Format tile name for display
        terrain_type = "unknown"
        if current_tile:
            terrain_type = current_tile.value.replace('_', ' ').title()
        
        # Display player position info
        coord_text = f"Player Position - Tile: ({tile_x}, {tile_y}) Pixel: ({pixel_x}, {pixel_y})"
        text_surface = font.render(coord_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # Display terrain type - this is the one we're adding
        terrain_text = f"Player is on [{terrain_type}]"
        terrain_surface = font.render(terrain_text, True, (255, 255, 255))
        screen.blit(terrain_surface, (10, 35))
        
        # Display monster count
        monster_text = f"Active Monsters: {len(self.monsters)}"
        monster_surface = font.render(monster_text, True, (255, 255, 255))
        screen.blit(monster_surface, (10, 60))
        
        # Draw zoom message if active
        zoom_msg, timer = self.camera.get_zoom_message()
        if zoom_msg and timer > 0:
            msg_font = pygame.font.Font(None, 36)
            msg_surface = msg_font.render(zoom_msg, True, (255, 255, 255))
            msg_rect = msg_surface.get_rect()
            msg_rect.centerx = SCREEN_WIDTH // 2
            msg_rect.top = 10
            screen.blit(msg_surface, msg_rect)
        
        # Draw UI elements - adjust positioning to improve layout
        if self.inventory_ui.visible:
            # Position inventory UI on the left
            self.inventory_ui.x = 10
            self.inventory_ui.y = 10
            self.inventory_ui.rect.topleft = (self.inventory_ui.x, self.inventory_ui.y)
            self.inventory_ui.draw(screen)
            
            # Position equipment UI on the right when visible together with inventory
            if self.equipment_ui.visible:
                self.equipment_ui.x = SCREEN_WIDTH - self.equipment_ui.width - 10
                self.equipment_ui.y = 10
                self.equipment_ui.rect.topleft = (self.equipment_ui.x, self.equipment_ui.y)
                self.equipment_ui.draw(screen)
                
            # Position generator UI on right side when visible
            if self.generator_ui.visible:
                self.generator_ui.draw(screen, self.player)
        
        # Quest UI is independent
        self.quest_ui.draw(screen)
        
        # Draw keyboard controls at the bottom of the screen
        controls_font = pygame.font.Font(None, 20)
        controls_text = "Controls: I-Inventory | E-Equipment | G-Generator | Q-Quests | WASD-Movement | R-Reset Zoom | Mouse Wheel-Zoom"
        controls_surface = controls_font.render(controls_text, True, (200, 200, 200))
        controls_rect = controls_surface.get_rect()
        controls_rect.centerx = SCREEN_WIDTH // 2
        controls_rect.bottom = SCREEN_HEIGHT - 10
        screen.blit(controls_surface, controls_rect)
            
        # Update display
        pygame.display.flip()

    def _spawn_initial_monsters(self):
        """Spawn initial set of monsters."""
        # Use a wider variety of monster types for initial spawn
        land_monster_types = [
            # Original monsters
            MonsterType.SLIME, MonsterType.SPIDER, MonsterType.WOLF,
            # Elemental creatures
            MonsterType.FIRE_ELEMENTAL, MonsterType.ICE_ELEMENTAL, MonsterType.STORM_ELEMENTAL,
            # Undead
            MonsterType.ZOMBIE, MonsterType.WRAITH, MonsterType.VAMPIRE,
            # Magical creatures
            MonsterType.PIXIE, MonsterType.PHOENIX, MonsterType.UNICORN,
            # Forest creatures
            MonsterType.TREANT, MonsterType.BEAR, MonsterType.DRYAD,
            # Dark creatures
            MonsterType.DEMON, MonsterType.SHADOW_STALKER, MonsterType.NIGHTMARE,
            # Constructs
            MonsterType.CLOCKWORK_KNIGHT, MonsterType.STEAM_GOLEM, MonsterType.ARCANE_TURRET,
            # Crystal Creatures
            MonsterType.CRYSTAL_GOLEM, MonsterType.PRISM_ELEMENTAL, MonsterType.GEM_BASILISK
        ]
        
        water_monster_types = [
            MonsterType.WATER_SPIRIT, 
            MonsterType.MERFOLK, 
            MonsterType.KRAKEN, 
            MonsterType.SIREN, 
            MonsterType.LEVIATHAN
        ]
        
        spawn_count = 0
        
        # Shuffle the monster types to randomize which ones get spawned
        random.shuffle(land_monster_types)
        random.shuffle(water_monster_types)
        
        print("\nStarting initial monster spawn...")
        # Try to spawn monsters until we reach MAX_MONSTERS
        while spawn_count < MAX_MONSTERS and (land_monster_types or water_monster_types):
            # Alternate between water and land monsters to ensure diversity
            if spawn_count % 2 == 0 and land_monster_types:
                monster_type = land_monster_types.pop(0)  # Get next land monster type
                is_water_monster = False
            elif water_monster_types:
                monster_type = water_monster_types.pop(0)  # Get next water monster type
                is_water_monster = True
            elif land_monster_types:
                monster_type = land_monster_types.pop(0)  # Fallback to land if no water types left
                is_water_monster = False
            else:
                break  # No more monster types available
            
            print(f"Attempting to spawn {monster_type.name}...")
            
            # Try up to 20 positions for each monster type
            spawn_successful = False
            for _ in range(20):
                # Generate position away from player
                tile_x = random.randint(5, self.map.width - 6)
                tile_y = random.randint(5, self.map.height - 6)
                
                # Get the tile type at this location (directly access the base_grid)
                tile_type = self.map.base_grid[tile_y][tile_x]
                is_water_tile = tile_type == TileType.WATER
                
                # Skip if water type mismatch
                if is_water_monster != is_water_tile:
                    continue
                    
                pixel_x = tile_x * TILE_SIZE
                pixel_y = tile_y * TILE_SIZE
                
                # Check distance from player
                dx = pixel_x - self.player.x
                dy = pixel_y - self.player.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < 200:  # Minimum spawn distance
                    continue
                
                if self.map.is_wall(tile_x, tile_y):
                    continue
                
                # Spawn monster
                monster = Monster(pixel_x, pixel_y, monster_type)
                self.monsters.append(monster)
                self.monster_counts[monster_type] += 1
                spawn_count += 1
                spawn_location = "water" if is_water_tile else "land"
                print(f"Spawned {monster_type.name} at ({tile_x}, {tile_y}) on {spawn_location}")
                spawn_successful = True
                break
            
            # If spawn was unsuccessful, put the monster type back but at the end
            if not spawn_successful:
                print(f"Failed to find valid spawn position for {monster_type.name}")
                if is_water_monster:
                    water_monster_types.append(monster_type)
                else:
                    land_monster_types.append(monster_type)
        
        print(f"\nInitial spawn complete - {spawn_count} monsters spawned")

    def _try_spawn_monster(self, monster_type=None):
        """Try to spawn a monster of the given type or a random type."""
        if len(self.monsters) >= MAX_MONSTERS:
            print("Maximum monster count reached")
            return False

        # If no specific type provided, choose a random one from an expanded list
        if monster_type is None:
            monster_type = random.choice([
                # Original monsters
                MonsterType.SLIME, MonsterType.SPIDER, MonsterType.WOLF,
                # Elemental creatures
                MonsterType.FIRE_ELEMENTAL, MonsterType.ICE_ELEMENTAL, MonsterType.STORM_ELEMENTAL,
                # Undead
                MonsterType.ZOMBIE, MonsterType.WRAITH, MonsterType.VAMPIRE,
                # Magical creatures
                MonsterType.PIXIE, MonsterType.PHOENIX, MonsterType.UNICORN,
                # Forest creatures
                MonsterType.TREANT, MonsterType.BEAR, MonsterType.DRYAD,
                # Dark creatures
                MonsterType.DEMON, MonsterType.SHADOW_STALKER, MonsterType.NIGHTMARE,
                # Constructs
                MonsterType.CLOCKWORK_KNIGHT, MonsterType.STEAM_GOLEM, MonsterType.ARCANE_TURRET,
                # Crystal Creatures
                MonsterType.CRYSTAL_GOLEM, MonsterType.PRISM_ELEMENTAL, MonsterType.GEM_BASILISK,
                # Water Creatures
                MonsterType.WATER_SPIRIT, MonsterType.MERFOLK, MonsterType.KRAKEN, MonsterType.SIREN, MonsterType.LEVIATHAN
            ])

        # Determine if this is a water monster
        is_water_monster = monster_type in [
            MonsterType.WATER_SPIRIT, 
            MonsterType.MERFOLK, 
            MonsterType.KRAKEN, 
            MonsterType.SIREN, 
            MonsterType.LEVIATHAN
        ]
        
        # Try multiple positions until we find a valid one
        for _ in range(20):  # Increased attempts to 20 to handle water-specific spawning
            # Generate random position in tile coordinates
            tile_x = random.randint(2, self.map.width - 3)
            tile_y = random.randint(2, self.map.height - 3)
            
            # Get the tile type at this location (directly access the base_grid)
            tile_type = self.map.base_grid[tile_y][tile_x]
            is_water_tile = tile_type == TileType.WATER
            
            # Skip if water type mismatch (water monsters should only spawn in water, non-water monsters not in water)
            if is_water_monster != is_water_tile:
                continue
            
            # Convert to pixel coordinates
            pixel_x = tile_x * TILE_SIZE
            pixel_y = tile_y * TILE_SIZE
            
            # Check if position is walkable
            if self.map.is_wall(tile_x, tile_y):
                continue
            
            # Check distance from player
            dx = pixel_x - self.player.x
            dy = pixel_y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            min_distance = 200  # Increased minimum spawn distance
            if distance < min_distance:
                continue
            
            # Check if we've reached max count for this type
            max_count = 10  # Default max count per type
            if self.monster_counts[monster_type] >= max_count:
                print(f"Max count reached for {monster_type.name}")
                return False
            
            # Valid position found, spawn the monster
            monster = Monster(pixel_x, pixel_y, monster_type)
            self.monsters.append(monster)
            self.monster_counts[monster_type] += 1
            spawn_location = "water" if is_water_tile else "land"
            print(f"Spawned {monster_type.name} at tile ({tile_x}, {tile_y}) on {spawn_location}")
            return True
        
        print(f"Failed to find valid spawn position for {monster_type.name}")
        return False

    def _handle_monster_death(self, monster: Monster):
        """Handle monster death and potential item drops."""
        self.monster_counts[monster.monster_type] -= 1
        self.monsters.remove(monster)
        
        # Handle special death effects
        if monster.monster_type == MonsterType.SLIME:
            # Create smaller slimes
            if monster.size > 16:  # Minimum size check
                for _ in range(2):
                    new_slime = Monster(
                        monster.x + random.randint(-20, 20),
                        monster.y + random.randint(-20, 20),
                        MonsterType.SLIME
                    )
                    new_slime.size = max(16, monster.size - 8)
                    new_slime.health = new_slime.size * 2
                    new_slime.max_health = new_slime.health
                    self.monsters.append(new_slime)
                    self.monster_counts[MonsterType.SLIME] += 1

class Equipment:
    """Class to manage equipped items."""
    def __init__(self):
        self.slots = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None,
            'weapon': None
        }
        
    def get_equipped_item(self, slot: str) -> Optional[Item]:
        """Get the item equipped in the given slot."""
        return self.slots.get(slot)
        
    def equip_item(self, item: Item) -> bool:
        """
        Equip an item in its appropriate slot.
        Returns True if successful, False if no appropriate slot.
        """
        slot = None
        if isinstance(item, Weapon):
            slot = 'weapon'
        elif isinstance(item, Hands):
            slot = 'hands'
        elif isinstance(item, Armor):
            slot = item.armor_type.lower()
            
        if slot and slot in self.slots:
            self.slots[slot] = item
            return True
        return False
        
    def unequip_item(self, slot: str) -> Optional[Item]:
        """Unequip and return the item in the given slot."""
        if slot in self.slots:
            item = self.slots[slot]
            self.slots[slot] = None
            return item
        return None

class Inventory:
    """Class to manage the player's inventory."""
    def __init__(self, capacity: int = 40):  # Changed from 32 to 40 to match 5x8 grid
        self.items = [None] * capacity
        
    def add_item(self, item: Item) -> bool:
        """Add an item to the first empty slot. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False
            
    def remove_item(self, item: Item) -> bool:
        """Remove the first occurrence of an item. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is item:
                self.items[i] = None
                return True
        return False

    def get_item_at(self, index: int) -> Optional[Item]:
        """Get the item at the given index."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

def create_map(width: int, height: int) -> Tuple[pygame.sprite.Group, List[List[int]]]:
    """Create a simple map with walls around the edges"""
    print("Creating map...")
    walls = pygame.sprite.Group()
    map_grid = [[0 for _ in range(width)] for _ in range(height)]
    
    # Create walls around the edges
    for x in range(width):
        walls.add(Wall(x, 0))
        walls.add(Wall(x, height - 1))
        map_grid[0][x] = 1
        map_grid[height - 1][x] = 1
    
    for y in range(height):
        walls.add(Wall(0, y))
        walls.add(Wall(width - 1, y))
        map_grid[y][0] = 1
        map_grid[y][width - 1] = 1
    
    print("Map created")
    return walls, map_grid

def initialize_game():
    """Initialize the game and return the game state."""
    try:
        print("Initializing game...")
        # Initialize Pygame
        pygame.init()
        print("Pygame initialized")
        
        # Create screen
        print("Creating screen...")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG Game")
        print("Screen created")
        
        # Create game map
        print("Creating game map...")
        game_map = Map(50, 50)  # 50x50 grid
        if not game_map:
            raise RuntimeError("Failed to create game map")
        print("Game map created")
        
        # Create player at center of map
        print("Creating player...")
        spawn_pos = (game_map.width * TILE_SIZE // 2, game_map.height * TILE_SIZE // 2)  # Center of map in pixels
        print(f"Player spawn position: ({spawn_pos[0] // TILE_SIZE}, {spawn_pos[1] // TILE_SIZE})")
        player = Player(spawn_pos[0], spawn_pos[1])
        if not player:
            raise RuntimeError("Failed to create player")
        print("Player created")
        
        # Create camera
        print("Creating camera...")
        camera = Camera(player)
        camera.set_map_bounds(game_map.width * TILE_SIZE, game_map.height * TILE_SIZE)
        if not camera:
            raise RuntimeError("Failed to create camera")
        print("Camera created")
        
        # Create quest generator
        print("Creating quest generator...")
        item_generator = ItemGenerator()
        quest_generator = QuestGenerator(item_generator, game_map)
        if not quest_generator:
            raise RuntimeError("Failed to create quest generator")
        print("Quest generator created")
        
        # Create game state
        print("Creating game state...")
        game_state = GameState(screen)
        if not game_state:
            raise RuntimeError("Failed to initialize game state")
        print("Game state created")
        
        # Initialize player quests
        print("Initializing player quests...")
        game_state.initialize_player_quests(player)
        print("Player quests initialized")
        
        print("Game initialization complete")
        return game_state
    except Exception as e:
        print(f"Error during game initialization: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main game loop."""
    print("Starting main function...")
    
    # Initialize Pygame
    pygame.init()
    print("Pygame initialized")
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game")
    print("Display mode set")
    
    # Create clock for timing
    clock = pygame.time.Clock()
    print("Clock created")
    
    # Create game state (it will create all other components)
    game_state = GameState(screen)
    print("Game state created")
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_i:
                    game_state.inventory_ui.toggle()
                elif event.key == pygame.K_e:
                    game_state.equipment_ui.toggle()
                elif event.key == pygame.K_q:
                    game_state.quest_ui.toggle()
                elif event.key == pygame.K_g:
                    game_state.generator_ui.toggle()
            
            # Pass events to UI elements
            game_state.inventory_ui.handle_event(event)
            game_state.equipment_ui.handle_event(event)
            game_state.quest_ui.handle_event(event)
            if game_state.generator_ui.visible:  # Only handle events when visible
                game_state.generator_ui.handle_event(event, game_state.player)
        
        # Update game state
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        game_state.update(dt)
        
        # Draw everything
        game_state.draw(screen)
        
        # Print FPS (using carriage return to stay on same line)
        fps = clock.get_fps()
        print(f"FPS: {fps:.1f}", end='\r')
    
    # Clean up
    pygame.quit()

if __name__ == "__main__":
    main() 