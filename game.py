"""
Main game module.
"""

import pygame
import random
import math
import os
import json
import pickle
from typing import Dict, List, Tuple, Optional, Union
from rpg_modules.items import ItemGenerator, Item, Weapon, Armor, Hands, Consumable
from rpg_modules.items.base import Inventory, Equipment
from rpg_modules.ui import InventoryUI, EquipmentUI, ItemGeneratorUI as GeneratorUI, QuestUI, SystemMenuUI
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
import numpy as np
import types

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

# Sound asset paths
SOUND_PATH = os.path.join(ASSET_PATH, "sounds")
PLAYER_ATTACK_SOUND = "player_attack.wav"
MONSTER_ATTACK_SOUND = "monster_attack.wav"
PLAYER_HIT_SOUND = "player_hit.wav"
MONSTER_HIT_SOUND = "monster_hit.wav"
LEVEL_UP_SOUND = "level_up.wav"

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
    
    # Create sounds directory if it doesn't exist
    if not os.path.exists(SOUND_PATH):
        os.makedirs(SOUND_PATH)
        print(f"Created sounds directory at {SOUND_PATH}")
    
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

def load_sounds():
    """Load all game sound effects or create simple tones if they don't exist."""
    sounds = {}
    
    # Ensure sounds directory exists
    if not os.path.exists(SOUND_PATH):
        os.makedirs(SOUND_PATH)
        print(f"Created sounds directory at {SOUND_PATH}")
    
    # Define sound names and files
    sound_files = {
        'player_attack': os.path.join(SOUND_PATH, PLAYER_ATTACK_SOUND),
        'monster_attack': os.path.join(SOUND_PATH, MONSTER_ATTACK_SOUND),
        'player_hit': os.path.join(SOUND_PATH, PLAYER_HIT_SOUND),
        'monster_hit': os.path.join(SOUND_PATH, MONSTER_HIT_SOUND),
        'level_up': os.path.join(SOUND_PATH, LEVEL_UP_SOUND)
    }
    
    # Try to load sounds from files, or create simple sounds
    for sound_name, sound_path in sound_files.items():
        # Check if the file exists
        if os.path.exists(sound_path):
            try:
                # Try to load the sound file
                sounds[sound_name] = pygame.mixer.Sound(sound_path)
                sounds[sound_name].set_volume(0.7)
                print(f"Loaded sound file: {sound_name}")
            except pygame.error as e:
                print(f"Error loading sound {sound_path}: {e}")
                # Create a simple tone as fallback
                sounds[sound_name] = _create_simple_sound(sound_name)
        else:
            print(f"Sound file not found: {sound_path}, creating simple tone")
            sounds[sound_name] = _create_simple_sound(sound_name)
    
    return sounds

def _create_simple_sound(sound_type):
    """Create an 8-bit style sound effect using numpy."""
    # Basic sound parameters
    sample_rate = 22050  # Hz
    amplitude = 127  # For 8-bit audio (0-255 with 128 as center)
    
    # Configure sound parameters based on sound type
    if sound_type == 'player_attack':
        # Quick sword swing sound - descending pitch
        duration = 0.2  # seconds
        base_freq = 800  # Hz
        
        # Time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Frequency decreases over time
        freq = base_freq * (1 - t*2)
        
        # Amplitude decreases over time (fade out)
        amp = amplitude * (1 - t)
        
        # Generate samples
        samples = 128 + amp * np.sin(2 * np.pi * freq * t)
            
    elif sound_type == 'monster_attack':
        # Low growl sound
        duration = 0.3  # seconds
        
        # Time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Low frequency with vibrato
        freq = 200 + 20 * np.sin(30 * t)
        
        # Add some noise
        noise = 10 * (2 * np.random.random(len(t)) - 1)
        
        # Generate base samples
        samples = 128 + amplitude * 0.8 * np.sin(2 * np.pi * freq * t)
        
        # Add noise
        samples = samples + noise
        
        # Apply volume envelope - rise and fall
        envelope = (1 - np.abs(2 * t/duration - 1))
        samples = 128 + (samples-128) * envelope
            
    elif sound_type == 'player_hit':
        # Impact sound - thud
        duration = 0.2  # seconds
        
        # Time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Sharp attack, quick decay
        envelope = np.exp(-t * 20)
        freq = 300 + 50 * np.exp(-t * 30)
        
        # Generate samples
        samples = 128 + amplitude * envelope * np.sin(2 * np.pi * freq * t)
            
    elif sound_type == 'monster_hit':
        # Monster getting hit - higher pitched impact
        duration = 0.15  # seconds
        
        # Time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Metallic frequency with quick decay
        freq = 500 * (1 - t*0.5)
        envelope = np.exp(-t * 25)
        
        # Add some noise for impact
        noise = 15 * np.random.random(len(t)) * envelope
        
        # Generate samples
        samples = 128 + amplitude * envelope * np.sin(2 * np.pi * freq * t) + noise
            
    elif sound_type == 'level_up':
        # Level up - 3 ascending notes
        duration = 0.5  # seconds
        note_duration = duration / 3
        frequencies = [440, 550, 660]  # A4, C#5, E5 (A major triad)
        
        all_samples = []
        
        for note_idx, freq in enumerate(frequencies):
            # Time array for this note
            t = np.linspace(0, note_duration, int(note_duration * sample_rate), endpoint=False)
            
            # Each note fades in and out
            if note_idx < 2:
                envelope = np.sin(np.pi * t / note_duration)
            else:
                # Last note has longer release
                envelope = np.sin(np.pi * t / note_duration * 0.5)
            
            # Generate note samples
            note_samples = 128 + amplitude * envelope * np.sin(2 * np.pi * freq * t)
            all_samples.append(note_samples)
        
        # Combine all notes
        samples = np.concatenate(all_samples)
    else:
        # Default beep
        duration = 0.2  # seconds
        base_freq = 440  # Hz
        
        # Time array
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Generate samples
        samples = 128 + amplitude * np.sin(2 * np.pi * base_freq * t)
    
    # Ensure samples are in 8-bit range (0-255)
    samples = np.clip(samples, 0, 255).astype(np.uint8)
    
    try:
        # Create sound from numpy array
        sound = pygame.mixer.Sound(buffer=samples)
        # Set appropriate volume
        sound.set_volume(0.7)
        print(f"Created 8-bit style sound for: {sound_type}")
        return sound
    except Exception as e:
        print(f"Error creating sound: {e}")
        # Return an empty sound in case of error
        empty_sound = pygame.mixer.Sound(buffer=bytearray(1000))
        empty_sound.set_volume(0.1)
        return empty_sound

# Game states
class GameState:
    """Manages the global game state."""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the game state."""
        print("\n=== Initializing Game State ===")
        
        # Store screen reference
        self.screen = screen
        
        # Create map
        print("Creating game map...")
        self.map = Map(50, 50)
        print(f"Map created with dimensions: {self.map.width}x{self.map.height}")
        
        # Create player
        print("Creating player...")
        self.player = Player(self.map.width * TILE_SIZE // 2, self.map.height * TILE_SIZE // 2)
        print(f"Player spawn position: ({self.player.x // TILE_SIZE}, {self.player.y // TILE_SIZE})")
        
        # Make sure player's inventory is set up properly with correct capacity
        if not hasattr(self.player, 'inventory') or not isinstance(self.player.inventory, Inventory):
            print("Creating new inventory for player")
            self.player.inventory = Inventory(40)  # Ensure capacity is set to 40
        
        # Add some initial items to player inventory for testing
        print("Adding some test items to player inventory...")
        try:
            from rpg_modules.items.generator import ItemGenerator
            item_gen = ItemGenerator()
            
            # Add a few test items of different types
            for _ in range(5):
                item = item_gen.generate_item()
                if item:
                    success = self.player.inventory.add_item(item)
                    print(f"Added test item: {item.display_name} - Success: {success}")
            
            # Debug info about inventory state
            filled_slots = sum(1 for item in self.player.inventory.items if item is not None)
            print(f"Player inventory now has {filled_slots}/{len(self.player.inventory.items)} items")
            print(f"First few inventory slots: {[str(item) if item else 'None' for item in self.player.inventory.items[:5]]}")
        except Exception as e:
            print(f"Error adding test items: {e}")
            import traceback
            traceback.print_exc()
        
        # Make sure player's equipment is set up properly
        if not hasattr(self.player, 'equipment') or not isinstance(self.player.equipment, Equipment):
            print("Creating new equipment for player")
            self.player.equipment = Equipment()
        
        # Override player's on_level_up method to play sound
        original_on_level_up = self.player.on_level_up
        def new_on_level_up():
            # Call the original method
            original_on_level_up()
            # Play level up sound
            if hasattr(self, 'sounds') and 'level_up' in self.sounds:
                self.sounds['level_up'].play()
                print("Playing level up sound!")
        self.player.on_level_up = new_on_level_up
        
        print(f"Player created with inventory capacity: {len(self.player.inventory.items)}")
        
        # Create camera
        print("Creating camera...")
        self.camera = Camera(self.player)
        print("Camera created")
        
        # Initialize monster system
        print("\nInitializing monster system...")
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Create UI elements
        print("\nCreating UI elements...")
        # Create inventory UI with explicit reference to player's inventory
        self.inventory_ui = InventoryUI(screen)
        # Explicitly set the inventory reference
        self.inventory_ui.inventory = self.player.inventory.items
        print(f"Inventory UI created with reference to player inventory: {id(self.player.inventory.items)}")
        
        # Create equipment UI with direct reference to player equipment
        self.equipment_ui = EquipmentUI(screen)
        self.equipment_ui.equipment = self.player.equipment.slots
        self.equipment_ui.set_player(self.player)  # Set player reference for stat calculations
        print(f"Equipment UI created with reference to player equipment: {id(self.player.equipment.slots)}")
        
        # Create other UI components
        self.generator_ui = GeneratorUI(SCREEN_WIDTH - 400, 10)
        
        # Add a method to refresh the inventory UI reference
        def refresh_inventory_ui(self):
            """Refresh the inventory UI to make sure it uses the current player inventory items."""
            print(f"DEBUG: Refreshing inventory UI - Inventory has {sum(1 for item in self.player.inventory.items if item is not None)}/{len(self.player.inventory.items)} items")
            # Ensure the UI is using the player's current inventory reference
            self.inventory_ui.inventory = self.player.inventory.items
            
        self.refresh_inventory_ui = types.MethodType(refresh_inventory_ui, self)
        
        # Call refresh to ensure UI is using the correct inventory reference
        self.refresh_inventory_ui()
        
        # Set up equipment callback
        self.inventory_ui.set_equip_callback(self.equip_item_from_inventory)
        print("Equipment callback set for inventory UI")
        
        # Create quest log and initialize quest UI with it
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(screen, self.quest_log)
        
        # Create system menu UI
        self.system_menu_ui = SystemMenuUI(screen)
        self._setup_system_menu_callbacks()
        
        print("UI elements created")
        
        # Load assets
        print("\nLoading assets...")
        self.assets = load_assets()
        print("Assets loaded")
        
        # Load sound effects
        print("\nLoading sound effects...")
        self.sounds = load_sounds()
        print("Sound effects loaded")
        
        # Initial monster spawn
        self._spawn_initial_monsters()
        print(f"Total monsters spawned: {len(self.monsters)}")
        for monster_type in MonsterType:
            if self.monster_counts[monster_type] > 0:
                print(f"- {monster_type.name}: {self.monster_counts[monster_type]}")
            
        # Game running state
        self.running = True
        self.paused = False
        self.current_attack_effect = None  # Track current attack animation
        self.save_file = 'savegame.json'
        
        # Game save path
        self.save_path = "save"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # Load saved game if it exists
        self.load_game()
        
        print("\n=== Game State Initialized ===")
        
    def _setup_system_menu_callbacks(self):
        """Set up callbacks for system menu options."""
        self.system_menu_ui.set_callback("Resume Game", self._resume_game)
        self.system_menu_ui.set_callback("Save Game", self._save_game)
        self.system_menu_ui.set_callback("Load Game", self._load_game)
        self.system_menu_ui.set_callback("New Game", self._new_game)
        self.system_menu_ui.set_callback("Quit Game", self._quit_game)
        
    def _resume_game(self):
        """Resume the game by hiding the system menu."""
        self.system_menu_ui.toggle()
        print("Game resumed")
        
    def _save_game(self):
        print("Saving game...")
        # Save the game state to a file
        save_data = {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'mana': getattr(self.player, 'mana', 0),
                'max_mana': getattr(self.player, 'max_mana', 0),
                'xp': getattr(self.player, 'xp', getattr(self.player, 'experience', 0)),
                'level': self.player.level,
                'inventory': [item.to_dict() if item is not None else None for item in self.player.inventory.items],
                'equipment': {slot: item.to_dict() for slot, item in self.player.equipment.slots.items() if item is not None}
            },
            'map': {
                'current_map': getattr(self.map, 'name', 'default_map'),
                'player_visited': list(self.player_visited) if hasattr(self, 'player_visited') else []
            }
        }
        os.makedirs('save', exist_ok=True)
        with open('save/savegame.json', 'w') as f:
            json.dump(save_data, f, indent=2)
        print("Game saved to save\\savegame.json")
        try:
            # Only close the system menu if it's currently visible
            if self.system_menu_ui.visible:
                self.system_menu_ui.toggle()
        except Exception as e:
            print(f"Error saving game: {e}")
        self.paused = False

    def load_game(self):
        """Load the game state from a file if it exists."""
        import os
        import json
        save_path = os.path.join(self.save_path, self.save_file)
        print(f"Attempting to load game from: {save_path}")
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    save_data = json.load(f)
                    print("Save data loaded successfully.")
                
                # Load player data
                player_data = save_data.get('player', {})
                self.player.rect.x = player_data.get('x', self.player.rect.x)
                self.player.rect.y = player_data.get('y', self.player.rect.y)
                self.player.level = player_data.get('level', self.player.level)
                if hasattr(self.player, 'xp'):
                    self.player.xp = player_data.get('xp', getattr(self.player, 'xp', 0))
                elif hasattr(self.player, 'experience'):
                    self.player.experience = player_data.get('xp', getattr(self.player, 'experience', 0))
                if hasattr(self.player, 'gold'):
                    self.player.gold = player_data.get('gold', getattr(self.player, 'gold', 0))
                if hasattr(self.player, 'health'):
                    self.player.health = player_data.get('health', getattr(self.player, 'health', 0))
                elif hasattr(self.player, 'hp'):
                    self.player.hp = player_data.get('health', getattr(self.player, 'hp', 0))
                if hasattr(self.player, 'max_health'):
                    self.player.max_health = player_data.get('max_health', getattr(self.player, 'max_health', 0))
                elif hasattr(self.player, 'max_hp'):
                    self.player.max_hp = player_data.get('max_health', getattr(self.player, 'max_hp', 0))
                if hasattr(self.player, 'mana'):
                    self.player.mana = player_data.get('mana', getattr(self.player, 'mana', 0))
                if hasattr(self.player, 'max_mana'):
                    self.player.max_mana = player_data.get('max_mana', getattr(self.player, 'max_mana', 0))
                if hasattr(self.player, 'stamina'):
                    self.player.stamina = player_data.get('stamina', getattr(self.player, 'stamina', 0))
                if hasattr(self.player, 'max_stamina'):
                    self.player.max_stamina = player_data.get('max_stamina', getattr(self.player, 'max_stamina', 0))
                if hasattr(self.player, 'attack_type'):
                    self.player.attack_type = player_data.get('attack_type', getattr(self.player, 'attack_type', ''))
                if hasattr(self.player, 'base_attack'):
                    self.player.base_attack = player_data.get('base_attack', getattr(self.player, 'base_attack', 0))
                if hasattr(self.player, 'defense'):
                    self.player.defense = player_data.get('defense', getattr(self.player, 'defense', 0))
                if hasattr(self.player, 'dexterity'):
                    self.player.dexterity = player_data.get('dexterity', getattr(self.player, 'dexterity', 0))
                print("Player data applied.")
                
                # Reset inventory with proper capacity
                inventory_capacity = len(self.player.inventory.items)
                self.player.inventory.items = [None] * inventory_capacity
                print(f"Reset inventory with capacity {inventory_capacity}.")
                
                # Load inventory items
                for item_data in save_data.get('inventory', []):
                    if item_data:  # Only process non-None items
                        item = self._create_item_from_data(item_data)
                        if item:
                            self.player.inventory.add_item(item)
                print(f"Loaded {sum(1 for item in self.player.inventory.items if item is not None)} items into inventory.")
                
                # Clear current equipment
                for slot in self.player.equipment.slots:
                    self.player.equipment.unequip_item(slot)
                print("Current equipment cleared.")
                
                # Load equipped items
                for slot, item_data in save_data.get('equipment', {}).items():
                    item = self._create_item_from_data(item_data)
                    if item:
                        self.player.equipment.equip_item(item)
                print(f"Loaded {len(save_data.get('equipment', {}))} equipped items.")
                
                # Make sure the inventory UI is updated with the new inventory
                self.refresh_inventory_ui()
                
                # Update equipment UI with player
                self.equipment_ui.equipment = self.player.equipment.slots
                self.equipment_ui.set_player(self.player)
                
                print("Refreshed inventory UI after loading.")
                
                print(f"Game loaded from {save_path}")
                # Only close the system menu if it's currently visible
                if self.system_menu_ui.visible:
                    self.system_menu_ui.toggle()
            except Exception as e:
                print(f"Error loading game: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No saved game found at {save_path}.")

    def _create_item_from_data(self, item_data):
        """Create an item object from saved data."""
        if not item_data:
            return None
        
        quality = item_data.get('quality', 'Common')
        if item_data.get('weapon_type'):
            return Weapon(
                weapon_type=item_data.get('weapon_type', 'Sword'),
                attack_power=item_data.get('attack_power', 5),
                quality=quality,
                material=item_data.get('material', 'Iron'),
                prefix=item_data.get('prefix', None)
            )
        elif item_data.get('armor_type'):
            if item_data.get('armor_type') == 'hands':
                return Hands(
                    defense=item_data.get('defense', 3),
                    dexterity=item_data.get('dexterity', 1),
                    quality=quality,
                    material=item_data.get('material', 'Leather'),
                    prefix=item_data.get('prefix', None)
                )
            else:
                return Armor(
                    armor_type=item_data.get('armor_type', 'Chest'),
                    defense=item_data.get('defense', 5),
                    quality=quality,
                    material=item_data.get('material', 'Iron'),
                    prefix=item_data.get('prefix', None)
                )
        elif item_data.get('consumable_type'):
            return Consumable(
                consumable_type=item_data.get('consumable_type', 'health'),
                effect_value=item_data.get('effect_value', 20),
                quality=quality
            )
        return None

    def _load_game(self):
        """Load a previously saved game."""
        print("Loading game...")
        self.load_game()
        # The system menu toggle is now handled in load_game() based on menu visibility

    def _new_game(self):
        """Start a new game."""
        print("Starting new game")
        self.restart_game()
        self.system_menu_ui.toggle()

    def _quit_game(self):
        """Signal the game to quit."""
        self._save_game()  # Save before quitting
        self.running = False
        print("Game quitting...")
        
    def restart_game(self):
        """Restart the game with a fresh state."""
        # Reset player
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)
        
        # Reset camera
        self.camera = Camera()
        
        # Reset monsters
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        
        # Reset map
        self.map = GameMap(MAP_WIDTH, MAP_HEIGHT)
        
        # Spawn initial monsters
        self._spawn_initial_monsters()
        
        # Reset death locations
        self.recent_death_locations = []
        
        # Make sure the inventory UI is updated with the new player's inventory
        self.inventory_ui.inventory = self.player.inventory.items
        self.refresh_inventory_ui()
        
        # Update equipment UI with new player reference
        self.equipment_ui.equipment = self.player.equipment.slots
        self.equipment_ui.set_player(self.player)
        
        print(f"Reset inventory UI to new player inventory with {len(self.player.inventory.items)} slots")
        
    def update(self, dt, events):
        """Update game state."""
        # Process events passed from main loop (not calling pygame.event.get() again)
        
        # Check for system menu visibility first
        if self.system_menu_ui.visible:
            # When system menu is open, only handle its events
            for event in events:
                if self.system_menu_ui.handle_event(event):
                    return  # Event was handled by system menu
            
            # Update system menu
            self.system_menu_ui.update()
            return
        
        # Handle UI component visibility and interaction
        for event in events:
            # Process different event types
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    # Toggle both inventory and equipment UI
                    self.inventory_ui.toggle()
                    # Make equipment UI match inventory UI visibility
                    if self.equipment_ui.visible != self.inventory_ui.visible:
                        self.equipment_ui.toggle()
                    
                    if self.inventory_ui.visible:
                        # Refresh inventory UI when opening
                        self.refresh_inventory_ui()
                        print(f"Opened inventory and equipment UI, refreshed with {sum(1 for item in self.player.inventory.items if item is not None)} items")
                elif event.key == pygame.K_e:
                    # Toggle equipment only
                    self.equipment_ui.toggle()
                elif event.key == pygame.K_g:
                    # Toggle generator UI
                    self.generator_ui.toggle()
                elif event.key == pygame.K_q:
                    # Toggle quest UI
                    self.quest_ui.toggle()
                elif event.key == pygame.K_ESCAPE:
                    # Handle ESC key: First close any open UI windows, then toggle system menu if needed
                    if self.inventory_ui.visible:
                        self.inventory_ui.toggle()
                        # Make equipment UI match inventory UI visibility
                        if self.equipment_ui.visible:
                            self.equipment_ui.toggle()
                        print("Closed inventory UI with ESC key")
                    elif self.equipment_ui.visible:
                        self.equipment_ui.toggle()
                        print("Closed equipment UI with ESC key")
                    elif self.generator_ui.visible:
                        self.generator_ui.toggle()
                        print("Closed generator UI with ESC key")
                    elif self.quest_ui.visible:
                        self.quest_ui.toggle()
                        print("Closed quest UI with ESC key")
                    else:
                        # Only open system menu if no other UI is visible
                        self.system_menu_ui.toggle()
                        print("Toggled system menu with ESC key")
                # Attack type switching with number keys
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    # Convert key to attack type (1-4)
                    attack_type = event.key - pygame.K_0
                    
                    # Check resource requirements before switching
                    if attack_type == 2 and self.player.stamina < 15:  # Heavy attack
                        print("Not enough stamina for Heavy attack! (Requires 15 stamina)")
                    elif attack_type == 3 and self.player.mana < 20:  # Magic attack
                        print("Not enough mana for Magic attack! (Requires 20 mana)")
                    else:
                        # Switch attack type if resources are available
                        success = self.player.switch_attack_type(attack_type)
                        if success:
                            attack_name = self.player.get_attack_type_name()
                            attack_range = self.player.get_attack_range()
                            print(f"Switched to {attack_name} attack! Range: {attack_range:.1f}")
                        else:
                            print("Could not switch attack type. Unknown error.")
                # Potion hotkeys
                elif event.key in [pygame.K_7, pygame.K_8, pygame.K_9]:
                    potion_type = None
                    if event.key == pygame.K_7:  # Health potion
                        potion_type = 'health'
                    elif event.key == pygame.K_8:  # Mana potion
                        potion_type = 'mana'
                    elif event.key == pygame.K_9:  # Stamina potion
                        potion_type = 'stamina'
                    
                    if potion_type:
                        self._use_potion_of_type(potion_type)
                # Add test items with T key
                elif event.key == pygame.K_t:
                    self._add_test_items()
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom immediately
                if event.y > 0:  # Scroll up to zoom in
                    self.camera.zoom_in()
                elif event.y < 0:  # Scroll down to zoom out
                    self.camera.zoom_out()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks
                if event.button == 1:  # Left mouse button for attack
                    # Only process attack if no UI is visible
                    if not (self.inventory_ui.visible or self.equipment_ui.visible or 
                           self.generator_ui.visible or self.quest_ui.visible):
                        if self.player.can_attack():
                            # Attempt a fast attack on click
                            self.player.try_attack()
                            self._handle_player_attack()
        
        # Update death location expiry times
        self._update_death_locations()
        
        # Handle player input
        keys = pygame.key.get_pressed()
        walls = self.map.get_walls()
        # Only print wall count occasionally to reduce console spam
        if random.random() < 0.005:
            print(f"DEBUG: Passing {len(walls)} walls to player.handle_input()")
        self.player.handle_input(keys, walls)
        
        # Update player
        self.player.update(dt)
        
        # Process player attacks
        if keys[pygame.K_SPACE] and self.player.can_attack():
            self._handle_player_attack()
        
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
                # Apply the damage to the player
                self.player.take_damage(damage)
                # Play monster attack sound
                self.sounds['monster_attack'].play()
                # Play player hit sound
                self.sounds['player_hit'].play()
                print(f"{monster.monster_type.name} lvl {monster.level} attacks player for {damage} damage! Player health: {self.player.health}/{self.player.max_health}")
        
        # Try spawning new monsters occasionally
        if random.random() < 0.01:  # 1% chance each frame
            monster_type = random.choice([MonsterType.SLIME, MonsterType.SPIDER, MonsterType.WOLF])
            if self._try_spawn_monster(monster_type):
                print(f"New {monster_type.name} spawned!")
        
        # Update camera
        self.camera.update(self.player)
        
    def draw(self):
        """Draw the game state."""
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Draw the map and entities
        self._draw_map()
        self._draw_entities()
        
        # Draw attack effect if one is active
        if self.current_attack_effect:
            self._draw_attack_effect(self.screen)
        
        # Draw the UI on top
        self._draw_player_stats()
        self._draw_action_toolbar(self.screen)
        
        # Draw monster tooltip if hovering over a monster
        if self.hovered_monster and not (self.inventory_ui.visible or self.equipment_ui.visible or 
                                        self.generator_ui.visible or self.quest_ui.visible):
            self._draw_monster_tooltip(self.screen, self.hovered_monster)
        
        # DIAGNOSTIC: Draw inventory status directly on screen
        filled_slots = sum(1 for item in self.player.inventory.items if item is not None)
        font = pygame.font.Font(None, 24)
        inventory_status = f"Inventory: {filled_slots}/{len(self.player.inventory.items)} items"
        status_text = font.render(inventory_status, True, (255, 255, 0))
        self.screen.blit(status_text, (10, SCREEN_HEIGHT - 30))
        
        # Draw any active UI components
        if self.inventory_ui.visible:
            # Refresh inventory UI before drawing to ensure it shows the current state
            self.refresh_inventory_ui()
            self.inventory_ui.draw(self.screen)
        if self.equipment_ui.visible:
            self.equipment_ui.draw(self.screen)
        if self.generator_ui.visible:
            self.generator_ui.draw(self.screen, self.player)
        if self.quest_ui.visible:
            self.quest_ui.draw(self.screen)
        
        # Draw the system menu on top of everything if visible
        if self.system_menu_ui.visible:
            self.system_menu_ui.draw(self.screen)
        
        # Update the display
        pygame.display.flip()

    def _draw_map(self):
        """Draw the game map."""
        self.map.draw(self.screen, self.camera, self.assets)

    def _draw_entities(self):
        """Draw the game entities (player and monsters)."""
        # Draw player
        self.player.draw(self.screen, self.camera)
        # Draw monsters
        for monster in self.monsters:
            monster.draw(self.screen, self.camera)

    def _draw_player_stats(self):
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
        self._draw_status_bar(self.screen, start_x, start_y, bar_width, bar_height, 
                            health_percent, (200, 50, 50), "Health")
        
        # Draw mana bar
        mana_percent = self.player.mana / self.player.max_mana
        self._draw_status_bar(self.screen, start_x, start_y + bar_height + bar_spacing, 
                            bar_width, bar_height, mana_percent, (50, 50, 200), "Mana")
        
        # Draw stamina bar
        stamina_percent = self.player.stamina / self.player.max_stamina
        self._draw_status_bar(self.screen, start_x, start_y + (bar_height + bar_spacing) * 2, 
                            bar_width, bar_height, stamina_percent, (50, 200, 50), "Stamina")
        
        # Draw XP bar - calculate percentage towards next level
        # Formula: next level requires current_level * 100 XP
        xp_needed = self.player.level * 100
        xp_percent = self.player.experience / xp_needed
        xp_color = (180, 120, 255)  # Purple for XP
        self._draw_status_bar(self.screen, start_x, start_y + (bar_height + bar_spacing) * 3, 
                            bar_width, bar_height, xp_percent, xp_color, 
                            f"XP: {self.player.experience}/{xp_needed}")
        
        # Draw attack type indicator below status bars
        attack_type = self.player.attack_type
        attack_name = self.player.get_attack_type_name()
        
        # Set color based on attack type
        if attack_type == 1:  # Regular
            attack_color = (200, 200, 200)  # White
        elif attack_type == 2:  # Heavy
            attack_color = (255, 150, 0)    # Orange
        elif attack_type == 3:  # Magic
            attack_color = (100, 100, 255)  # Blue
        elif attack_type == 4:  # Quick
            attack_color = (0, 255, 100)    # Green
        else:
            attack_color = (150, 150, 150)  # Gray
        
        # Draw attack type text
        font = pygame.font.Font(None, 20)
        attack_text = f"Attack: {attack_name} (Press 1-4)"
        text_surface = font.render(attack_text, True, attack_color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (start_x, start_y + (bar_height + bar_spacing) * 4 + 5)
        self.screen.blit(text_surface, text_rect)
        
        # Draw attack cooldown icon
        icon_size = 40
        icon_x = start_x - icon_size - 10
        icon_y = start_y
        
        # Create a simple sword icon
        pygame.draw.rect(self.screen, (150, 150, 150), (icon_x, icon_y, icon_size, icon_size))
        
        # Draw sword shape with color matching the attack type
        sword_color = attack_color
        # Sword handle
        pygame.draw.rect(self.screen, sword_color, 
                      (icon_x + icon_size//2 - 3, icon_y + icon_size//2, 6, icon_size//2 - 5))
        # Sword guard
        pygame.draw.rect(self.screen, sword_color, 
                      (icon_x + icon_size//4, icon_y + icon_size//2, icon_size//2, 5))
        # Sword blade
        pygame.draw.polygon(self.screen, sword_color, [
            (icon_x + icon_size//2, icon_y + 5),
            (icon_x + icon_size//2 - 7, icon_y + icon_size//2),
            (icon_x + icon_size//2 + 7, icon_y + icon_size//2)
        ])
        
        # Calculate cooldown overlay
        current_time = pygame.time.get_ticks()
        last_attack_time = self.player.last_attack_time
        attack_cooldown = self.player.attack_cooldown
        
        cooldown_percent = min(1.0, (current_time - last_attack_time) / attack_cooldown)
        
        # Draw cooldown overlay (darker area showing remaining cooldown)
        if cooldown_percent < 1.0:
            # Create a semi-transparent overlay to show cooldown
            cooldown_height = int(icon_size * (1 - cooldown_percent))
            cooldown_surface = pygame.Surface((icon_size, cooldown_height), pygame.SRCALPHA)
            cooldown_surface.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(cooldown_surface, (icon_x, icon_y))

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
                print(f"Spawned {monster_type.name} lvl {monster.level} at tile ({tile_x}, {tile_y}) on {spawn_location}")
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

        # Get player level (default to 1 if not set)
        player_level = getattr(self.player, 'level', 1)

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
        
        # Monsters with special respawn behavior that can ignore death location restrictions
        can_respawn_anywhere = monster_type in [
            MonsterType.SLIME,  # Slimes can spawn anywhere as they split
            MonsterType.WRAITH,  # Wraiths can appear in death locations
            MonsterType.PHOENIX  # Phoenix respawns from its ashes
        ]
        
        # Define minimum distance from player and from death locations
        min_player_distance = 200
        min_death_distance = 150  # Minimum distance from recent death locations
        
        # Try multiple positions until we find a valid one
        for _ in range(30):  # Increased attempts to handle death location checks
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
            distance_to_player = math.sqrt(dx * dx + dy * dy)
            
            if distance_to_player < min_player_distance:
                continue
            
            # Check if too close to recent death locations (unless monster has special respawn)
            if not can_respawn_anywhere:
                too_close_to_death = False
                for death_loc, _, death_type in self.recent_death_locations:
                    death_x, death_y = death_loc
                    dx = pixel_x - death_x
                    dy = pixel_y - death_y
                    death_distance = math.sqrt(dx * dx + dy * dy)
                    
                    if death_distance < min_death_distance:
                        too_close_to_death = True
                        break
                
                if too_close_to_death:
                    continue
            
            # Check if we've reached max count for this type
            max_count = 10  # Default max count per type
            if self.monster_counts[monster_type] >= max_count:
                print(f"Max count reached for {monster_type.name}")
                return False
            
            # Valid position found, spawn the monster
            monster = Monster(pixel_x, pixel_y, monster_type)
            
            # Set monster level to be +/- 1 of player level
            level_diff = random.randint(-1, 1)
            monster.level = max(1, player_level + level_diff)
            
            # Adjust monster stats based on level
            level_multiplier = 1.0 + (monster.level - 1) * 0.2  # 20% increase per level
            monster.max_health = int(monster.max_health * level_multiplier)
            monster.health = monster.max_health
            monster.attack_damage = int(monster.attack_damage * level_multiplier)
            
            self.monsters.append(monster)
            self.monster_counts[monster_type] += 1
            spawn_location = "water" if is_water_tile else "land"
            print(f"Spawned {monster_type.name} lvl {monster.level} at tile ({tile_x}, {tile_y}) on {spawn_location}")
            return True
        
        print(f"Failed to find valid spawn position for {monster_type.name}")
        return False

    def _handle_monster_death(self, monster: Monster):
        """Handle monster death and potential item drops."""
        self.monster_counts[monster.monster_type] -= 1
        
        # Record death location to prevent immediate respawning in same area
        death_location = (monster.x, monster.y)
        self.recent_death_locations.append((
            death_location, 
            self.death_location_expiry,
            monster.monster_type
        ))
        
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
                    
                    # Set level to match player level +/- 1
                    player_level = getattr(self.player, 'level', 1)
                    level_diff = random.randint(-1, 1)
                    new_slime.level = max(1, player_level + level_diff)
                    
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
        
        # Make sure the inventory display is refreshed
        self.refresh_inventory_ui()
        
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
        
        name_text = f"{monster.monster_type.name} lvl {monster.level}"
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

    def _update_death_locations(self):
        """Update the list of recent death locations, removing expired ones."""
        # Decrement time for each death location
        for i in range(len(self.recent_death_locations) - 1, -1, -1):
            location, expiry, monster_type = self.recent_death_locations[i]
            expiry -= 1
            if expiry <= 0:
                # Remove expired location
                self.recent_death_locations.pop(i)
            else:
                # Update expiry time
                self.recent_death_locations[i] = (location, expiry, monster_type)

    def _handle_player_attack(self):
        """Handle player attacks against monsters."""
        # Get player attack range based on current attack type
        attack_range = self.player.get_attack_range()
        
        # Get player position
        px, py = self.player.x, self.player.y
        
        # Start with player facing direction to determine attack area
        direction = self.player.direction
        
        # Get mouse position and convert to world coordinates
        mouse_pos = pygame.mouse.get_pos()
        zoom = self.camera.get_zoom()
        mouse_world_x = (mouse_pos[0] / zoom) - self.camera.x
        mouse_world_y = (mouse_pos[1] / zoom) - self.camera.y
        
        # Calculate direction to mouse
        dx_mouse = mouse_world_x - px
        dy_mouse = mouse_world_y - py
        
        # Check if any monster is close to the mouse position
        closest_to_mouse = None
        closest_mouse_dist = float('inf')
        
        for monster in self.monsters:
            # Calculate distance from monster to mouse
            monster_to_mouse_dx = monster.x - mouse_world_x
            monster_to_mouse_dy = monster.y - mouse_world_y
            monster_to_mouse_dist = math.sqrt(monster_to_mouse_dx**2 + monster_to_mouse_dy**2)
            
            # Calculate distance from monster to player
            monster_to_player_dx = monster.x - px
            monster_to_player_dy = monster.y - py
            monster_to_player_dist = math.sqrt(monster_to_player_dx**2 + monster_to_player_dy**2)
            
            # Check if monster is in attack range and closer to mouse than previous monsters
            if monster_to_player_dist <= attack_range * 1.2 and monster_to_mouse_dist < closest_mouse_dist:
                closest_to_mouse = monster
                closest_mouse_dist = monster_to_mouse_dist
        
        # If we found a monster close to mouse and within attack range, use mouse direction
        if closest_to_mouse is not None and closest_mouse_dist < TILE_SIZE * 2:
            # Determine direction based on angle to mouse
            angle = math.degrees(math.atan2(dy_mouse, dx_mouse))
            
            # Convert angle to cardinal direction
            if -45 <= angle < 45:
                direction = 'east'
            elif 45 <= angle < 135:
                direction = 'south'
            elif -135 <= angle < -45:
                direction = 'north'
            else:  # angle >= 135 or angle < -135
                direction = 'west'
                
            print(f"DEBUG: Using mouse direction: {direction} (angle: {angle:.1f}°)")
        
        # Add some debug output
        attack_name = self.player.get_attack_type_name()
        print(f"DEBUG: Player {attack_name} attack - Range: {attack_range:.1f}, Position: ({px}, {py}), Direction: {direction}")
        
        # Get player damage based on current attack type
        damage = self.player.get_attack_damage()
        
        # Add debug info about resource usage
        attack_type = self.player.attack_type
        if attack_type == 2:  # Heavy - uses stamina
            stamina_cost = 15
            print(f"DEBUG: Heavy attack - Cost: {stamina_cost} stamina, Remaining: {self.player.stamina}/{self.player.max_stamina}")
        elif attack_type == 3:  # Magic - uses mana
            mana_cost = 20
            print(f"DEBUG: Magic attack - Cost: {mana_cost} mana, Remaining: {self.player.mana}/{self.player.max_mana}")
        elif attack_type == 4:  # Quick - faster cooldown
            cooldown_reduction = 200  # ms
            print(f"DEBUG: Quick attack - Cooldown reduced by {cooldown_reduction}ms")
        
        # Play player attack sound
        self.sounds['player_attack'].play()
        
        # Show visual effect based on attack type - to be displayed for a few frames
        # This would be better with a proper particle system, but for now just store the effect
        # details to be rendered in subsequent frames
        self.current_attack_effect = {
            'type': attack_type,
            'direction': direction,
            'position': (px, py),
            'timer': 10,  # frames
            'color': self._get_attack_type_color(attack_type)
        }
        
        # Check each monster to see if it's in range
        hit_any = False
        closest_dist = float('inf')
        closest_monster = None
        
        for monster in self.monsters[:]:
            # Calculate distance to monster
            dx = monster.x - px
            dy = monster.y - py
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Track closest monster for debugging
            if distance < closest_dist:
                closest_dist = distance
                closest_monster = monster
            
            # Check if monster is in attack range
            if distance <= attack_range:
                # For magic attack, no direction check needed (area effect)
                if attack_type == 3:
                    hit = True
                # For other attacks, check if monster is in front of player based on direction
                else:
                    # Normalize direction vector
                    if abs(dx) > abs(dy):  # More horizontal than vertical
                        if dx > 0 and direction == 'east':
                            hit = True
                        elif dx < 0 and direction == 'west':
                            hit = True
                        else:
                            hit = False
                    else:  # More vertical than horizontal
                        if dy > 0 and direction == 'south':
                            hit = True
                        elif dy < 0 and direction == 'north':
                            hit = True
                        else:
                            hit = False
                    
                    # For quick attacks, be more lenient
                    if attack_type == 4 and distance < attack_range * 0.7:
                        hit = True
                
                # For heavy attacks, larger area
                if attack_type == 2:
                    # Wider angle for heavy attack
                    angle = math.degrees(math.atan2(dy, dx))
                    
                    # Get player facing angle based on direction
                    if direction == 'east':
                        player_angle = 0
                    elif direction == 'south':
                        player_angle = 90
                    elif direction == 'west':
                        player_angle = 180
                    elif direction == 'north':
                        player_angle = 270
                    else:
                        player_angle = 0
                    
                    # Calculate angle difference
                    angle_diff = abs((angle - player_angle + 180) % 360 - 180)
                    
                    # If within 90 degrees of facing direction, hit is valid
                    if angle_diff <= 90:
                        hit = True
                    else:
                        hit = False
                
                # Apply damage if hit is valid
                if hit:
                    # Apply damage to monster
                    old_health = monster.health
                    monster.health -= damage
                    hit_any = True
                    
                    # Play hit sound
                    self.sounds['monster_hit'].play()
                    
                    # Determine attack type name for display
                    attack_name = self.player.get_attack_type_name()
                    
                    print(f"Player hit {monster.monster_type.name} lvl {monster.level} with {attack_name} Attack for {damage} damage! Monster health: {monster.health}/{monster.max_health}")
                    
                    # Apply special effects based on attack type
                    if attack_type == 2:  # Heavy attack
                        # Knockback effect
                        knockback_dist = 20  # pixels
                        angle = math.atan2(dy, dx)
                        monster.x += math.cos(angle) * knockback_dist
                        monster.y += math.sin(angle) * knockback_dist
                        print(f"Heavy attack knocked {monster.monster_type.name} back by {knockback_dist} pixels!")
                    
                    elif attack_type == 3:  # Magic attack
                        # Splash damage to nearby monsters
                        splash_count = 0
                        for other_monster in self.monsters:
                            if other_monster != monster:
                                other_dx = other_monster.x - monster.x
                                other_dy = other_monster.y - monster.y
                                other_dist = math.sqrt(other_dx * other_dx + other_dy * other_dy)
                                if other_dist < TILE_SIZE * 2:  # 2 tiles splash radius
                                    splash_damage = damage // 2  # Half damage for splash
                                    old_health = other_monster.health
                                    other_monster.health -= splash_damage
                                    splash_count += 1
                                    print(f"Magic splash damage! {other_monster.monster_type.name} took {splash_damage} damage (health: {other_monster.health}/{other_monster.max_health})")
                        if splash_count > 0:
                            print(f"Magic attack hit {splash_count} additional monsters with splash damage!")
                    
                    elif attack_type == 4:  # Quick attack has a chance to hit twice
                        # 20% chance to strike twice
                        if random.random() < 0.2:
                            bonus_damage = damage // 2  # Half damage for bonus hit
                            monster.health -= bonus_damage
                            print(f"Quick attack struck twice! Bonus hit for {bonus_damage} damage! Monster health: {monster.health}/{monster.max_health}")
                    
                    # Check if monster was killed
                    if monster.health <= 0 and old_health > 0:
                        print(f"Player killed {monster.monster_type.name} lvl {monster.level}!")
                        
                        # Award experience (simple formula: base 10 XP * monster level)
                        experience_reward = 10 * monster.level
                        self.player.add_experience(experience_reward)
                        print(f"Player gained {experience_reward} experience!")
        
        # If we didn't hit anything, show a miss message with debug info
        if not hit_any:
            if closest_monster:
                monster_type = closest_monster.monster_type.name
                print(f"Player {attack_name} Attack missed! Closest monster: {monster_type} at distance {closest_dist:.1f} (attack range: {attack_range:.1f})")
            else:
                print(f"Player {attack_name} Attack missed! No monsters nearby.")
                
    def _get_attack_type_color(self, attack_type):
        """Get color for the specified attack type."""
        colors = [
            (200, 200, 200),  # Regular (white)
            (255, 150, 0),    # Heavy (orange)
            (100, 100, 255),  # Magic (blue)
            (0, 255, 100)     # Quick (green)
        ]
        return colors[attack_type - 1] if 1 <= attack_type <= 4 else (255, 255, 255)
        
    def _draw_attack_effect(self, screen):
        """Draw the current attack effect."""
        effect = self.current_attack_effect
        if effect['timer'] <= 0:
            self.current_attack_effect = None
            return
            
        # Reduce timer
        effect['timer'] -= 1
        
        # Get effect details
        attack_type = effect['type']
        direction = effect['direction']
        px, py = effect['position']
        color = effect['color']
        
        # Calculate screen position with camera zoom
        zoom = self.camera.get_zoom()
        screen_x = int((px + self.camera.x) * zoom)
        screen_y = int((py + self.camera.y) * zoom)
        
        # Scale effect size based on zoom
        base_size = TILE_SIZE * zoom
        
        # Draw different effects based on attack type
        if attack_type == 1:  # Regular attack - simple slash
            # Draw a slash in the direction player is facing
            if direction == 'east':
                points = [
                    (screen_x + base_size, screen_y),
                    (screen_x + base_size * 1.5, screen_y - base_size * 0.3),
                    (screen_x + base_size * 1.7, screen_y),
                    (screen_x + base_size * 1.5, screen_y + base_size * 0.3)
                ]
            elif direction == 'west':
                points = [
                    (screen_x, screen_y),
                    (screen_x - base_size * 0.5, screen_y - base_size * 0.3),
                    (screen_x - base_size * 0.7, screen_y),
                    (screen_x - base_size * 0.5, screen_y + base_size * 0.3)
                ]
            elif direction == 'south':
                points = [
                    (screen_x, screen_y + base_size),
                    (screen_x - base_size * 0.3, screen_y + base_size * 1.5),
                    (screen_x, screen_y + base_size * 1.7),
                    (screen_x + base_size * 0.3, screen_y + base_size * 1.5)
                ]
            elif direction == 'north':
                points = [
                    (screen_x, screen_y),
                    (screen_x - base_size * 0.3, screen_y - base_size * 0.5),
                    (screen_x, screen_y - base_size * 0.7),
                    (screen_x + base_size * 0.3, screen_y - base_size * 0.5)
                ]
                
            # Draw slash with fading opacity based on timer
            alpha = int(200 * effect['timer'] / 10)
            slash_color = (*color, alpha)
            
            # Create a temporary surface for alpha blending
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(effect_surface, slash_color, points)
            screen.blit(effect_surface, (0, 0))
            
        elif attack_type == 2:  # Heavy attack - wide arc
            # Draw a wider arc in the direction player is facing
            center_x, center_y = screen_x + base_size//2, screen_y + base_size//2
            radius = base_size
            
            # Arc angles based on direction
            if direction == 'east':
                start_angle, end_angle = -45, 45
            elif direction == 'west':
                start_angle, end_angle = 135, 225
            elif direction == 'south':
                start_angle, end_angle = 45, 135
            elif direction == 'north':
                start_angle, end_angle = 225, 315
                
            # Convert to radians
            start_angle, end_angle = math.radians(start_angle), math.radians(end_angle)
            
            # Create points for arc
            arc_points = []
            steps = 12
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * i / steps
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                arc_points.append((x, y))
            
            # Add center to create a filled arc
            arc_points.append((center_x, center_y))
            
            # Draw with fading opacity
            alpha = int(180 * effect['timer'] / 10)
            arc_color = (*color, alpha)
            
            # Create surface for alpha blending
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(effect_surface, arc_color, arc_points)
            screen.blit(effect_surface, (0, 0))
            
        elif attack_type == 3:  # Magic attack - expanding circle
            # Calculate expanding circle
            radius = base_size * (1 + (10 - effect['timer']) / 5)
            center_x, center_y = screen_x + base_size//2, screen_y + base_size//2
            
            # Create fading color based on timer
            alpha = int(150 * effect['timer'] / 10)
            circle_color = (*color, alpha)
            
            # Create surface for alpha blending
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(effect_surface, circle_color, (center_x, center_y), int(radius))
            
            # Draw sparkles
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, radius * 0.8)
                spark_x = center_x + distance * math.cos(angle)
                spark_y = center_y + distance * math.sin(angle)
                spark_radius = random.uniform(2, 5) * zoom
                pygame.draw.circle(effect_surface, (255, 255, 255, alpha), 
                                 (int(spark_x), int(spark_y)), int(spark_radius))
                
            screen.blit(effect_surface, (0, 0))
            
        elif attack_type == 4:  # Quick attack - multiple small slashes
            # Draw multiple small slashes in direction
            center_x, center_y = screen_x + base_size//2, screen_y + base_size//2
            
            # Create temporary surface for alpha blending
            effect_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Directional offset for slashes
            if direction == 'east':
                dx, dy = 1, 0
            elif direction == 'west':
                dx, dy = -1, 0
            elif direction == 'south':
                dx, dy = 0, 1
            elif direction == 'north':
                dx, dy = 0, -1
            
            # Draw multiple small slashes
            for i in range(3):
                offset = (10 - effect['timer']) * 5 + i * 15
                slash_x = center_x + dx * offset * zoom
                slash_y = center_y + dy * offset * zoom
                
                # Small slash size
                slash_size = base_size * 0.4
                
                # Points for small slash
                if direction in ['east', 'west']:
                    points = [
                        (slash_x, slash_y - slash_size),
                        (slash_x + dx * slash_size, slash_y),
                        (slash_x, slash_y + slash_size)
                    ]
                else:
                    points = [
                        (slash_x - slash_size, slash_y),
                        (slash_x, slash_y + dy * slash_size),
                        (slash_x + slash_size, slash_y)
                    ]
                
                # Fade based on timer and position
                alpha = int(200 * effect['timer'] / 10 * (1 - i * 0.2))
                slash_color = (*color, alpha)
                
                pygame.draw.polygon(effect_surface, slash_color, points)
            
            screen.blit(effect_surface, (0, 0))

    def _draw_action_toolbar(self, screen):
        """Draw a toolbar showing attack types (1-4) and potion hotkeys (7-9)."""
        # Define constants
        toolbar_height = 60
        toolbar_y = screen.get_height() - toolbar_height
        toolbar_width = screen.get_width()
        
        # Create a fresh transparent toolbar surface
        toolbar_surface = pygame.Surface((toolbar_width, toolbar_height), pygame.SRCALPHA)
        
        # Draw main toolbar background
        pygame.draw.rect(toolbar_surface, (0, 0, 0, 128), (0, 0, toolbar_width, toolbar_height))
        
        # Draw divider line
        pygame.draw.line(toolbar_surface, (200, 200, 200), 
                         (toolbar_width // 2, 5), 
                         (toolbar_width // 2, toolbar_height - 5), 2)
        
        font = pygame.font.Font(None, 28)
        small_font = pygame.font.Font(None, 20)
        
        # Get current player resource values
        current_health = self.player.health
        max_health = self.player.max_health
        current_mana = self.player.mana
        max_mana = self.player.max_mana
        current_stamina = self.player.stamina
        max_stamina = self.player.max_stamina
        
        # FIRST PASS: Draw all button backgrounds
        
        # Check if attack types can be used based on resource requirements
        current_attack = self.player.attack_type
        
        # Check if any monsters are in attack range for visual indication
        closest_monster_dist = float('inf')
        player_pos = (self.player.x, self.player.y)
        base_attack_range = self.player.attack_range
        
        for monster in self.monsters:
            dx = monster.x - self.player.x
            dy = monster.y - self.player.y
            dist = math.sqrt(dx*dx + dy*dy)
            closest_monster_dist = min(closest_monster_dist, dist)
        
        # Calculate attack range for each attack type
        attack_ranges = [
            base_attack_range,             # Regular attack
            base_attack_range * 0.8,       # Heavy attack (shorter range)
            base_attack_range * 1.5,       # Magic attack (longer range)
            base_attack_range              # Quick attack
        ]
        
        # Draw attack slots (1-4) backgrounds
        for i in range(4):
            slot_x = 20 + i * 120
            slot_y = 10
            slot_width = 100
            slot_height = 40
            
            # Check if this attack type has the resources to be used
            can_use = True
            if i + 1 == 2:  # Heavy attack requires stamina
                can_use = current_stamina >= 15
            elif i + 1 == 3:  # Magic attack requires mana
                can_use = current_mana >= 20
            
            # Check if any monster is in range for this attack type
            monster_in_range = closest_monster_dist <= attack_ranges[i]
            
            # Set button color based on active state and usability
            if i + 1 == current_attack:
                if can_use:
                    if monster_in_range:
                        color = (80, 120, 200, 220)  # Bright blue for active and usable with monster in range
                    else:
                        color = (60, 100, 160, 200)  # Active attack, no monster in range
                else:
                    color = (100, 100, 160, 150)  # Dimmer blue for active but unusable (resource constraints)
            else:
                if can_use:
                    if monster_in_range:
                        color = (60, 60, 80, 180)  # Slightly brighter for inactive but usable with monster in range
                    else:
                        color = (40, 40, 60, 160)  # Inactive attack
                else:
                    color = (40, 40, 40, 120)  # Dark gray for unusable attacks
                
            # Draw attack button background
            pygame.draw.rect(toolbar_surface, color, (slot_x, slot_y, slot_width, slot_height), border_radius=5)
        
        # Prepare potion data
        potion_types = ["7: Health", "8: Mana", "9: Stamina"]
        
        # Get potion counts
        health_potions = sum(1 for item in self.player.inventory.items if item and hasattr(item, 'consumable_type') and item.consumable_type == 'health')
        mana_potions = sum(1 for item in self.player.inventory.items if item and hasattr(item, 'consumable_type') and item.consumable_type == 'mana')
        stamina_potions = sum(1 for item in self.player.inventory.items if item and hasattr(item, 'consumable_type') and item.consumable_type == 'stamina')
        potion_counts = [health_potions, mana_potions, stamina_potions]
        
        # Check if each potion can be used
        need_health = current_health < max_health
        need_mana = current_mana < max_mana
        need_stamina = current_stamina < max_stamina
        needs = [need_health, need_mana, need_stamina]
        
        # Draw potion slot backgrounds (7-9)
        for i in range(3):
            slot_x = toolbar_width // 2 + 20 + i * 120
            slot_y = 10
            slot_width = 100
            slot_height = 40
            
            # Check if this potion type is available and needed
            has_potions = potion_counts[i] > 0
            can_use = needs[i]
            
            # Set appropriate colors based on state
            if i == 0:  # Health potion
                if has_potions and can_use:
                    bg_color = (150, 30, 30, 240)  # Bright red for usable health potions
                elif has_potions:
                    bg_color = (80, 30, 30, 200)   # Medium red for available but not needed
                else:
                    bg_color = (40, 40, 40, 160)   # Dark gray for no potions
            elif i == 1:  # Mana potion
                if has_potions and can_use:
                    bg_color = (30, 30, 150, 240)  # Bright blue for usable mana potions
                elif has_potions:
                    bg_color = (30, 30, 80, 200)   # Medium blue for available but not needed
                else:
                    bg_color = (40, 40, 40, 160)   # Dark gray for no potions
            else:  # Stamina potion
                if has_potions and can_use:
                    bg_color = (30, 150, 30, 240)  # Bright green for usable stamina potions
                elif has_potions:
                    bg_color = (30, 80, 30, 200)   # Medium green for available but not needed
                else:
                    bg_color = (40, 40, 40, 160)   # Dark gray for no potions
            
            # Draw potion button background
            pygame.draw.rect(toolbar_surface, bg_color, (slot_x, slot_y, slot_width, slot_height), border_radius=5)
        
        # SECOND PASS: Draw all text on top of backgrounds
        
        # Draw attack slot text
        attack_titles = ["1: Regular", "2: Heavy", "3: Magic", "4: Quick"]
        attack_desc = [
            "Normal range, balanced damage",
            "15 Stam, -20% range, +50% dmg",
            "20 Mana, +50% range, +100% dmg",
            "Fast cooldown, -30% damage"
        ]
        
        for i in range(4):
            slot_x = 20 + i * 120
            slot_y = 10
            
            # Check usability for text color
            can_use = True
            if i + 1 == 2:  # Heavy attack
                can_use = current_stamina >= 15
            elif i + 1 == 3:  # Magic attack
                can_use = current_mana >= 20
                
            # Set text color based on usability
            if can_use:
                text_color = (255, 255, 255)  # White text for usable attacks
                desc_color = (220, 220, 220)  # Light gray for description
            else:
                text_color = (150, 150, 150)  # Gray text for unusable attacks
                desc_color = (130, 130, 130)  # Darker gray for description
            
            # Draw attack title
            text = font.render(attack_titles[i], True, text_color)
            toolbar_surface.blit(text, (slot_x + 10, slot_y + 5))
            
            # Draw attack description
            desc = small_font.render(attack_desc[i], True, desc_color)
            toolbar_surface.blit(desc, (slot_x + 10, slot_y + 25))
        
        # Draw potion slot text
        for i in range(3):
            slot_x = toolbar_width // 2 + 20 + i * 120
            slot_y = 10
            
            has_potions = potion_counts[i] > 0
            can_use = needs[i]
            
            # Always use bold white text for potion name to ensure visibility
            text = font.render(potion_types[i], True, (255, 255, 255))
            toolbar_surface.blit(text, (slot_x + 10, slot_y + 5))
            
            # Create appropriate status text
            if has_potions and not can_use:
                status_text = f"Count: {potion_counts[i]} (At Max)"
            else:
                status_text = f"Count: {potion_counts[i]}"
                
            # Draw status text (always light gray for consistency)
            count_text = small_font.render(status_text, True, (220, 220, 220))
            toolbar_surface.blit(count_text, (slot_x + 10, slot_y + 25))
        
        # Finally, blit the complete toolbar to the screen - only once!
        screen.blit(toolbar_surface, (0, toolbar_y))

    def _count_potions_of_type(self, potion_type):
        """Count the number of potions of a specific type in the player's inventory."""
        count = 0
        if hasattr(self.player, 'inventory'):
            for item in self.player.inventory.items:
                if item and hasattr(item, 'consumable_type') and item.consumable_type == potion_type:
                    count += 1
        return count

    def _use_potion_of_type(self, potion_type):
        """Find and use a potion of the specified type from inventory."""
        # First check if we have a potion of this type
        potion_index = None
        potion_item = None
        
        # Find the first potion of the requested type
        for i, item in enumerate(self.player.inventory.items):
            if (item and hasattr(item, 'consumable_type') and 
                item.consumable_type == potion_type):
                potion_index = i
                potion_item = item
                break
                
        if potion_index is None or potion_item is None:
            print(f"No {potion_type} potion in inventory")
            return False

        # Use the potion
        print(f"Using {potion_item.display_name} from hotkey...")
        if potion_type == 'health':
            old_health = self.player.health
            self.player.health = min(self.player.max_health, self.player.health + potion_item.effect_value)
            print(f"Restored {self.player.health - old_health} health. Player health: {self.player.health}/{self.player.max_health}")
        elif potion_type == 'mana':
            old_mana = self.player.mana
            self.player.mana = min(self.player.max_mana, self.player.mana + potion_item.effect_value)
            print(f"Restored {self.player.mana - old_mana} mana. Player mana: {self.player.mana}/{self.player.max_mana}")
        elif potion_type == 'stamina':
            old_stamina = self.player.stamina
            self.player.stamina = min(self.player.max_stamina, self.player.stamina + potion_item.effect_value)
            print(f"Restored {self.player.stamina - old_stamina} stamina. Player stamina: {self.player.stamina}/{self.player.max_stamina}")
        
        # Play a sound effect
        if 'player_hit' in self.sounds:
            self.sounds['player_hit'].play()
        
        # Remove the used potion from inventory
        self.player.inventory.items[potion_index] = None
        
        # Update UI
        self.inventory_ui.inventory = self.player.inventory.items
        self.refresh_inventory_ui()  # Make sure UI is completely refreshed
        
        return True

    def _add_test_items(self):
        """Add some test items to the player's inventory for debugging."""
        print("\n==== FORCING TEST ITEMS INTO INVENTORY ====")
        
        try:
            from rpg_modules.items.generator import ItemGenerator
            item_gen = ItemGenerator()
            
            # FORCE CLEAR inventory and recreate it (this is drastic but should work)
            self.player.inventory.items = [None] * 40
            print(f"RESET: Forcibly reset inventory to 40 empty slots")
            
            # Add 1 weapon (Legendary)
            weapon = item_gen.generate_item('weapon', 'Legendary')
            if weapon:
                self.player.inventory.items[0] = weapon
                print(f"ADDED: Legendary weapon directly to slot 0")
            
            # Add 9 armor pieces (mix of qualities)
            armor_qualities = ["Legendary", "Masterwork", "Polished", "Standard", 
                              "Legendary", "Masterwork", "Polished", "Standard", "Masterwork"]
            
            for i in range(9):
                armor = item_gen.generate_item('armor', armor_qualities[i])
                if armor:
                    self.player.inventory.items[i+1] = armor
                    print(f"ADDED: {armor_qualities[i]} armor directly to slot {i+1}")
            
            # Add 30 potions (roughly 10 of each type: health, mana, stamina)
            potion_qualities = ["Standard", "Polished", "Masterwork", "Legendary"]
            health_count = mana_count = stamina_count = 0
            slot_index = 10
            
            # Keep generating potions until we have filled all 30 slots or reached maximum attempts
            max_attempts = 100  # Prevent infinite loop
            attempts = 0
            
            while slot_index < 40 and attempts < max_attempts:
                # Determine which quality to use based on distribution:
                # 50% Standard, 30% Polished, 15% Masterwork, 5% Legendary
                rand = random.random()
                if rand < 0.5:
                    quality = "Standard"
                elif rand < 0.8:
                    quality = "Polished" 
                elif rand < 0.95:
                    quality = "Masterwork"
                else:
                    quality = "Legendary"
                    
                # Generate a consumable item
                potion = item_gen.generate_item('consumable', quality)
                
                # Check its type and decide whether to keep it based on our counts
                if not potion:
                    attempts += 1
                    continue
                    
                potion_type = potion.consumable_type
                
                # Determine if we should add this potion based on our current counts
                add_potion = False
                if potion_type == 'health' and health_count < 10:
                    health_count += 1
                    add_potion = True
                elif potion_type == 'mana' and mana_count < 10:
                    mana_count += 1
                    add_potion = True
                elif potion_type == 'stamina' and stamina_count < 10:
                    stamina_count += 1
                    add_potion = True
                
                if add_potion:
                    self.player.inventory.items[slot_index] = potion
                    print(f"ADDED: {quality} {potion_type} potion directly to slot {slot_index}")
                    slot_index += 1
                
                attempts += 1
            
            # Refresh the inventory UI reference
            self.inventory_ui.inventory = self.player.inventory.items
            
            # Call the refresh method to ensure UI stays in sync
            self.refresh_inventory_ui()
            
            # Debug info
            filled_slots = sum(1 for item in self.player.inventory.items if item is not None)
            print(f"INVENTORY STATUS: {filled_slots}/40 items")
            print(f"Potion distribution: Health: {health_count}, Mana: {mana_count}, Stamina: {stamina_count}")
            print(f"First 5 slots: {[str(item) if item else 'None' for item in self.player.inventory.items[:5]]}")
            print("==== TEST ITEMS ADDED SUCCESSFULLY ====\n")
        except Exception as e:
            print(f"ERROR: Failed to add test items: {e}")
            import traceback
            traceback.print_exc()

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
            dt = self.clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.game_state._quit_game()
                    running = False

            # Update game state
            self.game_state.update(dt, events)
            
            if not self.game_state.running:
                running = False

            # Draw game state
            if running:
                self.game_state.draw()
                pygame.display.flip()

        # Cleanup after game loop ends
        pygame.quit()
        print("Pygame resources cleaned up.")

def main():
    """Start the game."""
    # Initialize pygame with audio support
    pygame.init()
    
    # Initialize the mixer module specifically with good audio settings
    try:
        pygame.mixer.quit()  # Close any existing mixer
        pygame.mixer.pre_init(44100, -16, 2, 512)  # CD quality with small buffer
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)  # Set more channels for multiple sounds
        print("Audio system initialized successfully with 16 channels")
    except pygame.error as e:
        print(f"Warning: Audio system initialization failed: {e}")
    
    # Create and run the game
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 