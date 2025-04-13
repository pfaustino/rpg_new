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
import traceback

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

# Global reference to the current game state
game_state = None

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
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the game state."""
        print("\n=== Initializing Game State ===")
        
        # Create map
        print("Creating game map...")
        self.map = Map(50, 50)
        print(f"Map created with dimensions: {self.map.width}x{self.map.height}")
        
        # Create player
        print("Creating player...")
        self.player = Player(self.map.width * TILE_SIZE // 2, self.map.height * TILE_SIZE // 2)
        print(f"Player spawn position: ({self.player.x // TILE_SIZE}, {self.player.y // TILE_SIZE})")
        
        # Make sure player's inventory is set up properly
        if not hasattr(self.player, 'inventory') or not isinstance(self.player.inventory, Inventory):
            self.player.inventory = Inventory()
        
        # Make sure player's equipment is set up properly
        if not hasattr(self.player, 'equipment') or not isinstance(self.player.equipment, Equipment):
            self.player.equipment = Equipment()
        print("Player created with proper inventory")
        
        # Create camera
        print("Creating camera...")
        self.camera = Camera(self.player)
        print("Camera created")
        
        # Initialize monster system
        print("\nInitializing monster system...")
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Create UI elements
        print("\nCreating UI elements...")
        self.inventory_ui = InventoryUI(screen, self.player.inventory.items)
        self.equipment_ui = EquipmentUI(screen, self.player.equipment.slots)  # Use player's equipment
        self.generator_ui = GeneratorUI(SCREEN_WIDTH - 400, 10)
        
        # Set up equipment callback
        self.inventory_ui.set_equip_callback(self.equip_item_from_inventory)
        print("Equipment callback set for inventory UI")
        
        # Create quest log and initialize quest UI with it
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(screen, self.quest_log)
        print("UI elements created")
        
        # Load assets
        print("\nLoading assets...")
        self.assets = load_assets()
        print("Assets loaded")
        
        # Initial monster spawn
        self._spawn_initial_monsters()
        print(f"Total monsters spawned: {len(self.monsters)}")
        for monster_type in MonsterType:
            if self.monster_counts[monster_type] > 0:
                print(f"- {monster_type.name}: {self.monster_counts[monster_type]}")
            
        # Game running state
        self.running = True
        
        print("\n=== Game State Initialized ===")
        
    def update(self, dt, events):
        """Update game state."""
        # Process events passed from main loop (not calling pygame.event.get() again)
        
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
                    # Toggle inventory UI
                    self.inventory_ui.toggle()
                    # Show equipment UI when inventory is shown, hide when inventory is hidden
                    if self.equipment_ui.visible != self.inventory_ui.visible:
                        self.equipment_ui.toggle()
                    # Hide generator UI if inventory is closed
                    if not self.inventory_ui.visible and self.generator_ui.visible:
                        self.generator_ui.toggle()
                elif event.key == pygame.K_e:
                    # Toggle equipment UI and ensure inventory is visible too
                    self.equipment_ui.toggle()
                    # Show/hide inventory with equipment
                    if self.equipment_ui.visible != self.inventory_ui.visible:
                        self.inventory_ui.toggle()
                    # Hide generator UI when viewing equipment
                    if self.equipment_ui.visible and self.generator_ui.visible:
                        self.generator_ui.toggle()
                elif event.key == pygame.K_q:
                    self.quest_ui.toggle()
                elif event.key == pygame.K_g:
                    # Toggle generator UI
                    self.generator_ui.toggle()
                    
                    # When generator is visible, ensure inventory is visible too
                    if self.generator_ui.visible and not self.inventory_ui.visible:
                        self.inventory_ui.toggle()
                        
                    # Hide equipment when generator is shown
                    if self.generator_ui.visible and self.equipment_ui.visible:
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
        
        # Check for monster hover
        self._check_monster_hover()
        
        # Pass events to UI elements after handling zoom
        for event in events:
            if event.type != pygame.MOUSEWHEEL:  # Skip wheel events for UI
                self.inventory_ui.handle_event(event)
                self.equipment_ui.handle_event(event)
                self.quest_ui.handle_event(event)
                if self.generator_ui.visible:  # Only handle events when visible
                    self.generator_ui.handle_event(event, self.player)
                    # Re-sync inventory after possible item generation
                    self.inventory_ui.inventory = self.player.inventory.items
        
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
        
        # Draw player status bars and attack icon in top-right corner
        self._draw_player_status_bars(screen)
        
        # Draw monster tooltip if hovering over a monster
        if self.hovered_monster:
            self._draw_monster_tooltip(screen, self.hovered_monster)
        
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
        
        # First check if inventory should be drawn
        if self.inventory_ui.visible:
            # Position inventory UI on the left
            self.inventory_ui.x = 10
            self.inventory_ui.y = 10
            self.inventory_ui.rect.topleft = (self.inventory_ui.x, self.inventory_ui.y)
            self.inventory_ui.draw(screen)
        
        # Next check if equipment should be drawn    
        if self.equipment_ui.visible:
            # Position equipment UI on the right
            self.equipment_ui.x = SCREEN_WIDTH - self.equipment_ui.rect.width - 10
            self.equipment_ui.y = 10
            self.equipment_ui.rect.topleft = (self.equipment_ui.x, self.equipment_ui.y)
            self.equipment_ui.draw(screen)
        
        # Finally check if generator should be drawn
        if self.generator_ui.visible:
            # Position generator UI on the right
            self.generator_ui.x = SCREEN_WIDTH - self.generator_ui.rect.width - 10
            self.generator_ui.y = 10
            # Ensure the rect is updated with the new position
            self.generator_ui.rect.x = self.generator_ui.x
            self.generator_ui.rect.y = self.generator_ui.y
            self.generator_ui.rect.topleft = (self.generator_ui.x, self.generator_ui.y)
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

    def _draw_player_status_bars(self, screen):
        """Draw player health, mana, stamina bars and attack cooldown icon."""
        # Calculate bar dimensions and positions
        bar_width = 150
        bar_height = 20
        bar_spacing = 5
        border_width = 2
        
        # Position in top-right corner with some margin
        start_x = SCREEN_WIDTH - bar_width - 20
        start_y = 15
        
        # Draw health bar
        health_percent = self.player.health / self.player.max_health
        self._draw_status_bar(screen, start_x, start_y, bar_width, bar_height, 
                            health_percent, (200, 50, 50), "Health")
        
        # Draw mana bar
        mana_percent = self.player.mana / self.player.max_mana
        self._draw_status_bar(screen, start_x, start_y + bar_height + bar_spacing, 
                            bar_width, bar_height, mana_percent, (50, 50, 200), "Mana")
        
        # Draw stamina bar
        stamina_percent = self.player.stamina / self.player.max_stamina
        self._draw_status_bar(screen, start_x, start_y + (bar_height + bar_spacing) * 2, 
                            bar_width, bar_height, stamina_percent, (50, 200, 50), "Stamina")
        
        # Draw attack cooldown icon
        icon_size = 40
        icon_x = start_x - icon_size - 10
        icon_y = start_y
        
        # Create a simple sword icon
        pygame.draw.rect(screen, (150, 150, 150), (icon_x, icon_y, icon_size, icon_size))
        
        # Draw sword shape
        sword_color = (200, 200, 200)
        # Sword handle
        pygame.draw.rect(screen, sword_color, 
                      (icon_x + icon_size//2 - 3, icon_y + icon_size//2, 6, icon_size//2 - 5))
        # Sword guard
        pygame.draw.rect(screen, sword_color, 
                      (icon_x + icon_size//4, icon_y + icon_size//2, icon_size//2, 5))
        # Sword blade
        pygame.draw.polygon(screen, sword_color, [
            (icon_x + icon_size//2, icon_y + 5),
            (icon_x + icon_size//2 - 7, icon_y + icon_size//2),
            (icon_x + icon_size//2 + 7, icon_y + icon_size//2)
        ])
        
        # Calculate cooldown overlay
        # For now just showing a random cooldown for demonstration
        # In a real implementation, this would use the player's attack cooldown
        cooldown_percent = (pygame.time.get_ticks() % 3000) / 3000
        
        # Draw cooldown overlay (darker area showing remaining cooldown)
        if cooldown_percent < 1.0:
            # Create a semi-transparent overlay to show cooldown
            cooldown_height = int(icon_size * cooldown_percent)
            cooldown_surface = pygame.Surface((icon_size, cooldown_height), pygame.SRCALPHA)
            cooldown_surface.fill((0, 0, 0, 128))  # Semi-transparent black
            screen.blit(cooldown_surface, (icon_x, icon_y + icon_size - cooldown_height))

    def _draw_status_bar(self, screen, x, y, width, height, fill_percent, color, label=None):
        """Draw a status bar with border and optional label."""
        # Draw border
        border_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (200, 200, 200), border_rect, 2)
        
        # Draw fill
        fill_width = int((width - 4) * fill_percent)
        fill_rect = pygame.Rect(x + 2, y + 2, fill_width, height - 4)
        pygame.draw.rect(screen, color, fill_rect)
        
        # Draw label if provided
        if label:
            font = pygame.font.Font(None, 18)
            label_surface = font.render(label, True, (255, 255, 255))
            label_x = x + 5
            label_y = y + (height - label_surface.get_height()) // 2
            screen.blit(label_surface, (label_x, label_y))
        
        # Draw percentage text
        percent_text = f"{int(fill_percent * 100)}%"
        font = pygame.font.Font(None, 18)
        percent_surface = font.render(percent_text, True, (255, 255, 255))
        percent_x = x + width - percent_surface.get_width() - 5
        percent_y = y + (height - percent_surface.get_height()) // 2
        screen.blit(percent_surface, (percent_x, percent_y))

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

    def equip_item_from_inventory(self, inventory_index):
        """Equip an item from the inventory to the appropriate equipment slot."""
        print(f"\nDEBUG: ==== EQUIP ATTEMPT START ====")
        print(f"DEBUG: Attempting to equip item from inventory index {inventory_index}")
        print(f"DEBUG: Total items in inventory: {len(self.player.inventory.items)}")
        print(f"DEBUG: Equipment instance: {self.player.equipment}")
        print(f"DEBUG: Available equipment slots: {self.player.equipment.slots.keys()}")
        
        if not (0 <= inventory_index < len(self.player.inventory.items)):
            print(f"DEBUG: Invalid inventory index: {inventory_index}")
            print(f"DEBUG: ==== EQUIP ATTEMPT FAILED - INVALID INDEX ====\n")
            return False
        
        item = self.player.inventory.items[inventory_index]
        if item is None:
            print("DEBUG: No item at this inventory index")
            print(f"DEBUG: ==== EQUIP ATTEMPT FAILED - NO ITEM ====\n")
            return False
        
        print(f"DEBUG: Attempting to equip {item.display_name} from inventory slot {inventory_index}")
        print(f"DEBUG: Item type: {type(item).__name__}")
        
        # Handle consumable items differently - use them immediately
        if hasattr(item, 'consumable_type'):
            # Apply consumable effect to player
            print(f"DEBUG: Item is a consumable of type: {item.consumable_type}")
            print(f"Using {item.display_name}...")
            if item.consumable_type == 'health':
                old_health = self.player.health
                self.player.health = min(self.player.max_health, self.player.health + item.effect_value)
                print(f"Restored {self.player.health - old_health} health. Player health: {self.player.health}/{self.player.max_health}")
            elif item.consumable_type == 'mana':
                old_mana = self.player.mana
                self.player.mana = min(self.player.max_mana, self.player.mana + item.effect_value)
                print(f"Restored {self.player.mana - old_mana} mana. Player mana: {self.player.mana}/{self.player.max_mana}")
            elif item.consumable_type == 'stamina':
                old_stamina = self.player.stamina
                self.player.stamina = min(self.player.max_stamina, self.player.stamina + item.effect_value)
                print(f"Restored {self.player.stamina - old_stamina} stamina. Player stamina: {self.player.stamina}/{self.player.max_stamina}")
            
            # Remove the consumable from inventory
            self.player.inventory.items[inventory_index] = None
            print(f"DEBUG: Removed consumable from inventory slot {inventory_index}")
            
            # Update UI immediately
            self.inventory_ui.inventory = self.player.inventory.items
            print(f"DEBUG: Updated inventory UI after consuming item")
            print(f"DEBUG: ==== EQUIP ATTEMPT SUCCESS - CONSUMED ITEM ====\n")
            return True
        
        # Get the current item from the slot this item would go into before equipping
        # This allows us to swap the items
        slot = None
        
        # Determine which slot this item belongs in
        if hasattr(item, 'weapon_type'):
            slot = 'weapon'
            print(f"DEBUG: Item is a weapon of type {item.weapon_type}, will use slot '{slot}'")
        elif hasattr(item, 'armor_type'):
            slot = item.armor_type.lower()
            print(f"DEBUG: Item is armor of type {item.armor_type}, will use slot '{slot}'")
        elif hasattr(item, 'is_hands'):
            slot = 'hands'
            print(f"DEBUG: Item is hands armor, will use slot '{slot}'")
            
        if slot is None:
            print(f"DEBUG: Could not determine appropriate slot for item")
            print(f"DEBUG: Item has attributes: {dir(item)}")
            print(f"DEBUG: ==== EQUIP ATTEMPT FAILED - UNKNOWN ITEM TYPE ====\n")
            return False
            
        # Verify slot exists in equipment
        if slot not in self.player.equipment.slots:
            print(f"DEBUG: Determined slot '{slot}' not found in equipment slots")
            print(f"DEBUG: Available slots: {list(self.player.equipment.slots.keys())}")
            print(f"DEBUG: ==== EQUIP ATTEMPT FAILED - INVALID SLOT ====\n")
            return False
            
        # Get the current item in that slot before equipping
        current_equipped_item = self.player.equipment.slots[slot]
        if current_equipped_item:
            print(f"DEBUG: Current item in slot '{slot}': {current_equipped_item.display_name}")
        else:
            print(f"DEBUG: No item currently in slot '{slot}'")
        
        # Use Equipment.equip_item method instead of direct slot manipulation
        equip_success = self.player.equipment.equip_item(item)
        if not equip_success:
            print(f"DEBUG: Equipment.equip_item failed to equip the item")
            print(f"DEBUG: ==== EQUIP ATTEMPT FAILED - EQUIP_ITEM FAILED ====\n")
            return False
            
        print(f"DEBUG: Successfully equipped '{item.display_name}' in slot '{slot}'")
        
        # Return the previously equipped item to inventory
        self.player.inventory.items[inventory_index] = current_equipped_item
        if current_equipped_item:
            print(f"DEBUG: Returned '{current_equipped_item.display_name}' to inventory slot {inventory_index}")
        else:
            print(f"DEBUG: Cleared inventory slot {inventory_index}")
            
        # Update UI immediately
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        print(f"DEBUG: Updated inventory and equipment UIs")
        print(f"DEBUG: ==== EQUIP ATTEMPT SUCCESS ====\n")
        return True

    def _check_monster_hover(self):
        """Check if mouse is hovering over any monster."""
        # No hover checks if UI is open
        if self.inventory_ui.visible or self.equipment_ui.visible or self.generator_ui.visible or self.quest_ui.visible:
            self.hovered_monster = None
            return
            
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        zoom = self.camera.get_zoom()
        
        # Convert screen position to world position
        world_x = (mouse_pos[0] / zoom) - self.camera.x
        world_y = (mouse_pos[1] / zoom) - self.camera.y
        
        # Check each monster
        self.hovered_monster = None
        for monster in self.monsters:
            # Simple distance-based hover detection
            dx = monster.x - world_x
            dy = monster.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # If mouse is within monster's hitbox (using size as a radius)
            if distance <= monster.size:
                self.hovered_monster = monster
                break

    def _draw_monster_tooltip(self, screen, monster):
        """Draw a tooltip showing monster stats when hovering over it."""
        # Calculate tooltip dimensions
        tooltip_width = 240
        tooltip_height = 180
        padding = 10
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Position tooltip near mouse but ensure it stays on screen
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] - tooltip_height - 10
        
        # Adjust if tooltip would go off screen
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = SCREEN_WIDTH - tooltip_width - 10
        if tooltip_y < 10:
            tooltip_y = 10
        
        # Create tooltip rectangle
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Get border color based on monster level
        # Calculate level from monster attributes
        # Stronger monsters get more impressive colors
        monster_power = (monster.health / 100 + monster.attack_damage / 10) * (1 + monster.speed / 5)
        
        # Assign color based on power level
        if monster_power > 20:  # Legendary
            border_color = QUALITY_COLORS['Legendary']  # Gold
        elif monster_power > 15:  # Masterwork
            border_color = QUALITY_COLORS['Masterwork']  # Purple
        elif monster_power > 10:  # Polished
            border_color = QUALITY_COLORS['Polished']  # Blue
        else:  # Standard
            border_color = QUALITY_COLORS['Standard']  # Green
        
        # Draw tooltip background and border
        pygame.draw.rect(screen, (30, 30, 30, 220), tooltip_rect)  # Dark background
        pygame.draw.rect(screen, border_color, tooltip_rect, 3)  # Colored border
        
        # Draw monster name
        font_large = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 20)
        
        name_text = f"{monster.monster_type.name}"
        name_surface = font_large.render(name_text, True, (255, 255, 255))
        screen.blit(name_surface, (tooltip_x + padding, tooltip_y + padding))
        
        # Draw health bar
        health_percent = monster.health / monster.max_health
        bar_width = tooltip_width - (padding * 2)
        bar_height = 15
        bar_x = tooltip_x + padding
        bar_y = tooltip_y + 40
        
        # Health bar border
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Health bar fill
        fill_width = int(bar_width * health_percent)
        pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, fill_width, bar_height))
        
        # Health text
        health_text = f"Health: {monster.health}/{monster.max_health}"
        health_surface = font_small.render(health_text, True, (255, 255, 255))
        screen.blit(health_surface, (bar_x + 5, bar_y - 2))
        
        # Draw monster stats
        stats = [
            f"Attack: {monster.attack_damage}",
            f"Speed: {monster.speed}",
            f"Range: {monster.attack_range} tiles"
        ]
        
        y_offset = bar_y + bar_height + 10
        for stat in stats:
            stat_surface = font_small.render(stat, True, (255, 255, 255))
            screen.blit(stat_surface, (tooltip_x + padding, y_offset))
            y_offset += 20
        
        # Draw difficulty rating
        difficulty_text = self._get_monster_difficulty_text(monster)
        difficulty_color = self._get_monster_difficulty_color(monster)
        difficulty_surface = font_small.render(difficulty_text, True, difficulty_color)
        screen.blit(difficulty_surface, (tooltip_x + padding, y_offset + 10))
        
    def _get_monster_difficulty_text(self, monster):
        """Get a text description of monster difficulty relative to player."""
        # Calculate monster power
        monster_power = (monster.health / 100 + monster.attack_damage / 10) * (1 + monster.speed / 5)
        
        # Calculate player power (simplified formula)
        player_power = (self.player.health / 100 + self.player.attack / 10) * (1 + 3 / 5)  # Assuming player speed is 3
        
        # Determine difficulty based on power difference
        power_ratio = monster_power / player_power if player_power > 0 else monster_power
        
        if power_ratio < 0.5:
            return "Difficulty: Trivial"
        elif power_ratio < 0.75:
            return "Difficulty: Easy"
        elif power_ratio < 1.25:
            return "Difficulty: Normal"
        elif power_ratio < 2.0:
            return "Difficulty: Hard"
        else:
            return "Difficulty: Deadly"
    
    def _get_monster_difficulty_color(self, monster):
        """Get color based on monster difficulty relative to player."""
        # Calculate monster power
        monster_power = (monster.health / 100 + monster.attack_damage / 10) * (1 + monster.speed / 5)
        
        # Calculate player power (simplified formula)
        player_power = (self.player.health / 100 + self.player.attack / 10) * (1 + 3 / 5)  # Assuming player speed is 3
        
        # Determine difficulty based on power difference
        power_ratio = monster_power / player_power if player_power > 0 else monster_power
        
        if power_ratio < 0.5:
            return (128, 128, 128)  # Gray for trivial
        elif power_ratio < 0.75:
            return (0, 255, 0)      # Green for easy
        elif power_ratio < 1.25:
            return (255, 255, 0)    # Yellow for normal
        elif power_ratio < 2.0:
            return (255, 128, 0)    # Orange for hard
        else:
            return (255, 0, 0)      # Red for deadly

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
        if hasattr(item, 'weapon_type'):
            slot = 'weapon'
            print(f"DEBUG: Equipment.equip_item - item is a weapon of type {item.weapon_type}")
        elif hasattr(item, 'is_hands'):
            slot = 'hands'
            print(f"DEBUG: Equipment.equip_item - item is hands armor")
        elif hasattr(item, 'armor_type'):
            slot = item.armor_type.lower()
            print(f"DEBUG: Equipment.equip_item - item is armor of type {item.armor_type}")
        else:
            print(f"DEBUG: Equipment.equip_item - could not determine slot for item: {item.display_name if hasattr(item, 'display_name') else item}")
            
        if slot and slot in self.slots:
            self.slots[slot] = item
            print(f"DEBUG: Equipment.equip_item - successfully equipped item in slot '{slot}'")
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

# Helper functions that use the global game_state
def get_game_state():
    """Get the current global game state instance."""
    global game_state
    print(f"DEBUG: get_game_state called, returning: {game_state}")
    return game_state

class Game:
    """Main game class that manages the game state"""
    
    def __init__(self):
        """Initialize the main game instance"""
        global game_state
        
        print("Starting main function...")
        
        # Initialize Pygame
        pygame.init()
        print("Pygame initialized")
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG Game")
        print("Display mode set")
        
        # Create clock for timing
        self.clock = pygame.time.Clock()
        print("Clock created")
        
        # Create game state (it will create all other components)
        self.game_state = GameState(self.screen)
        print("Game state created")
        
        # Set the global game_state for external access - no longer needed but kept for compatibility
        global game_state  # Need to declare again due to Python scoping rules
        game_state = self.game_state
        print(f"DEBUG: Global game_state set to: {game_state}")
        
    def run(self):
        """Run the main game loop"""
        # Main game loop
        running = True
        while running:
            # Handle events - collect events ONLY ONCE
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    
            # Update game state - pass the events
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            self.game_state.update(dt, events)
            
            # Draw everything
            self.game_state.draw(self.screen)
            
            # Print FPS (using carriage return to stay on same line)
            fps = self.clock.get_fps()
            print(f"FPS: {fps:.1f}", end='\r')
        
        # Clean up
        pygame.quit()

def main():
    """Start the game."""
    # Create and run the game
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 