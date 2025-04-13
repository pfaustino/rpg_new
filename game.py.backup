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
    """Manages the main game state."""
    
    def __init__(self, screen):
        """Initialize the game state."""
        global game_state
        game_state = self
        
        # Set up game window
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        
        # Initialize random number generator
        random.seed()
        
        # Screen dimensions and settings
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        # Load assets
        self.assets = load_assets()
        self.font = pygame.font.Font(None, 28)  # Default font
        self.debug_font = pygame.font.Font(None, 18)  # Smaller font for debug info
        self.title_font = pygame.font.Font(None, 48)  # Larger font for titles
        
        # Load sounds
        try:
            self.sounds = load_sounds()
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.sounds = {}
            
        # Set up game map
        self.map = Map(width=50, height=50, tile_size=TILE_SIZE)
        self.map.generate_map()
        
        # Set up player
        player_pos = self.map.find_empty_tile()
        self.player = Player(player_pos[0], player_pos[1], self.assets)
        self.player.inventory = Inventory(40)  # Player can carry 40 items
        self.player.equipment = EquipmentManager()
        
        # Initialize player stats
        self.player.health = PLAYER_HP
        self.player.max_health = PLAYER_HP
        self.player.mana = PLAYER_ATTACK
        self.player.max_mana = PLAYER_ATTACK
        self.player.stamina = PLAYER_DEFENSE
        self.player.max_stamina = PLAYER_DEFENSE
        
        # Initialize player equipment
        self.player.equipment.slots['weapon'] = Weapon(weapon_type="Sword", attack_power=10, quality="Common", material="Iron")
        self.player.equipment.slots['chest'] = Armor(armor_type="Chest", defense=5, quality="Common", material="Leather")
        self.player.equipment.slots['head'] = Armor(armor_type="Head", defense=2, quality="Common", material="Leather")
        self.player.equipment.slots['hands'] = Hands(defense=3, dexterity=1, quality="Common", material="Leather")
        self.player.equipment.slots['legs'] = Armor(armor_type="Legs", defense=4, quality="Common", material="Leather")
        self.player.equipment.slots['feet'] = Armor(armor_type="Feet", defense=2, quality="Common", material="Leather")
        
        # Initialize player quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
        # Track recently killed monster locations to prevent immediate respawning
        self.recent_death_locations = []
        self.death_location_expiry = 500  # Frames before a death location expires
        
        # Initialize UI references
        self.inventory_ui.inventory = self.player.inventory.items
        self.equipment_ui.equipment = self.player.equipment.slots
        
        # Initialize UI state
        self.refresh_inventory_ui()
        self.refresh_equipment_ui()
        
        # Initialize player stats
        self.player.level = 1
        self.player.xp = 0
        self.player.experience = 0
        self.player.gold = 0
        self.player.attack_type = 1
        self.player.base_attack = 10
        self.player.defense = 5
        self.player.dexterity = 10
        
        # Initialize player stats bars
        self.health_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (200, 50, 50), "Health")
        self.mana_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 50, 200), "Mana")
        self.stamina_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (50, 200, 50), "Stamina")
        self.xp_bar = self._create_status_bar(self.screen, 150, 20, 150, 20, 100, (180, 120, 255), "XP")
        
        # Initialize attack cooldown
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0
        
        # Initialize action toolbar
        self.action_toolbar = self._create_action_toolbar()
        
        # Initialize quest log
        self.quest_log = QuestLog()
        self.quest_ui = QuestUI(self.screen, self.quest_log)
        
        # Initialize system menu
        self.system_menu_ui = SystemMenuUI(self.screen)
        self._setup_system_menu_callbacks()
        
        # Initialize UI components
        self.inventory_ui = InventoryUI(self.screen)
        self.equipment_ui = EquipmentUI(self.screen)
        self.generator_ui = GeneratorUI(self.screen_width - 400, 10)
        
        # Initialize camera
        self.camera = Camera(self.player)
        
        # Initialize monster system
        self.monsters = []
        self.monster_counts = {monster_type: 0 for monster_type in MonsterType}
        self.hovered_monster = None  # Track which monster is currently being hovered
        
                
                # Update equipment UI
                self.equipment_ui.equipment = self.player.equipment.slots
                self.equipment_ui.set_player(self.player)
                print("UIs refreshed successfully")
            except Exception as e:
                print(f"ERROR refreshing UIs: {e}")
                traceback.print_exc()
            
            # Debug info
            filled_slots = sum(1 for item in self.player.inventory.items if item is not None)
            equipped_items = sum(1 for item in self.player.equipment.slots.values() if item is not None)
            
            print(f"INVENTORY STATUS: {filled_slots}/{len(self.player.inventory.items)} items added")
            print(f"EQUIPPED ITEMS: {equipped_items} items equipped")
            
            try:
                print(f"First 6 slots: {[item.display_name if item else 'None' for item in self.player.inventory.items[:6]]}")
                print(f"Equipment: {[(slot, item.display_name if item else 'None') for slot, item in self.player.equipment.slots.items() if item is not None]}")
            except Exception as e:
                print(f"ERROR displaying debug info: {e}")
            
            print("==== TEST ITEMS ADDED SUCCESSFULLY ====\n")
            
            return True
        except Exception as e:
            print(f"ERROR: Failed to add test items: {e}")
            import traceback
            traceback.print_exc()
            return False

class EquipmentManager:
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