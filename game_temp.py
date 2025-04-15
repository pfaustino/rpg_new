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
from rpg_modules.ui import InventoryUI, EquipmentUI, ItemGeneratorUI as GeneratorUI, QuestUI, SystemMenuUI, DialogUI
from rpg_modules.entities import Player, NPC, NPCManager
from rpg_modules.entities.monster import Monster, MonsterType
from rpg_modules.quests import QuestGenerator, QuestType, QuestLog, MainQuestHandler
from rpg_modules.quests.manager import QuestManager
from rpg_modules.core.map import Map
from rpg_modules.core.camera import Camera
from rpg_modules.core.assets import load_assets as load_core_assets
from rpg_modules.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    WHITE, BLACK, RED, GREEN, BLUE, GRAY,
    QUALITY_COLORS, UI_DIMENSIONS
)
from rpg_modules.core.map import TileType
# Import save game functionality
from rpg_modules.savegame import save_game as module_save_game
from rpg_modules.savegame import load_game as module_load_game
from rpg_modules.savegame import resume_game as module_resume_game
from rpg_modules.savegame import create_item_from_data as module_create_item
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

# Global variables
global_game_state = None

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
        # Glorious level up sound - grand ascending fanfare
        duration = 2.0  # Full 2 seconds
        
        # Time array for the full sound
        t = np.linspace(0, duration, int(duration * sample_rate), endpoint=False)
        
        # Create multiple sections for a more complex sound
        samples = np.zeros(len(t)) + 128  # Start with silence at center point
        
        # First part: ascending major chord sequence (C, E, G, C)
        frequencies = [262, 330, 392, 523]  # C4, E4, G4, C5
        note_duration = 0.25  # each note is 0.25 seconds
        
        for i, freq in enumerate(frequencies):
            # Calculate start and end indices for this note
            start_idx = int(i * note_duration * sample_rate)
            end_idx = int((i + 1) * note_duration * sample_rate)
            
            if end_idx > len(t):
                break
                
            # Create a time array for just this segment
            t_segment = t[start_idx:end_idx] - t[start_idx]
            
            # Create an envelope that fades in and out
            envelope = np.sin(np.pi * t_segment / note_duration)
            
            # Generate the note and add it to our samples
            note = amplitude * 0.8 * envelope * np.sin(2 * np.pi * freq * t_segment)
            samples[start_idx:end_idx] += note
            
        # Second part: triumphant fanfare (t = 1.0 to 2.0)
        fanfare_start = int(1.0 * sample_rate)
        
        # Base frequencies for fanfare chords
        chord1 = [523, 659, 784]  # C5, E5, G5
        chord2 = [587, 740, 880]  # D5, F#5, A5
        chord3 = [659, 784, 988]  # E5, G5, B5
        chord4 = [523, 659, 784, 1047]  # C5, E5, G5, C6 (Final chord with octave)
        
        # Add chord progression
        chords = [chord1, chord2, chord3, chord4]
        chord_duration = 0.25  # each chord is 0.25 seconds
        
        for i, chord in enumerate(chords):
            # Calculate start and end indices for this chord
            start_idx = fanfare_start + int(i * chord_duration * sample_rate)
            end_idx = fanfare_start + int((i + 1) * chord_duration * sample_rate)
            
            if end_idx > len(t):
                break
                
            # Create a time array for just this segment
            t_segment = t[start_idx:end_idx] - t[start_idx]
            
            # Different envelope for each chord - last chord sustains longer
            if i < 3:
                envelope = np.sin(np.pi * t_segment / chord_duration)
            else:
                # Final chord has longer release
                envelope = np.sin(np.pi * t_segment / chord_duration * 0.5)
                envelope = np.clip(envelope, 0, 1)  # Keep only the attack/sustain part
            
            # Layer all frequencies in the chord
            chord_samples = np.zeros(end_idx - start_idx)
            for freq in chord:
                note = amplitude * 0.3 * envelope * np.sin(2 * np.pi * freq * t_segment)
                chord_samples += note
                
                # Add a subtle fifth above for richness on the final chord
                if i == 3:
                    overtone = amplitude * 0.1 * envelope * np.sin(2 * np.pi * freq * 1.5 * t_segment)
                    chord_samples += overtone
            
            # Add some subtle shimmer to the final chord
            if i == 3:
                shimmer_freq = 1400  # High frequency shimmer
                shimmer = amplitude * 0.05 * envelope * np.sin(2 * np.pi * shimmer_freq * t_segment)
                shimmer *= (0.5 + 0.5 * np.sin(2 * np.pi * 8 * t_segment))  # Modulate the shimmer
                chord_samples += shimmer
            
            # Add the chord to our main samples
            samples[start_idx:end_idx] += chord_samples
        
        # Add some subtle bells/sparkles throughout (especially in second half)
        for i in range(8):
            # Random timings for sparkle effects
            start_time = 1.0 + (i / 8) * 0.8  # Spread throughout the second half
            start_idx = int(start_time * sample_rate)
            sparkle_duration = 0.1
            end_idx = min(len(t), start_idx + int(sparkle_duration * sample_rate))
            
            if end_idx > len(t):
                break
                
            # Create a time array for just this segment
            t_segment = t[start_idx:end_idx] - t[start_idx]
            
            # Brief bell-like sound
            bell_freq = 1200 + i * 100  # Increasing frequencies
            envelope = np.exp(-t_segment * 40)  # Quick decay
            
            bell = amplitude * 0.15 * envelope * np.sin(2 * np.pi * bell_freq * t_segment)
            samples[start_idx:end_idx] += bell
        
        # Apply overall envelope to entire sound
        overall_envelope = 1.0 - 0.5 * np.exp(-(t/duration) * 3)  # Starts at 0.5, quickly rises to 1.0
        overall_envelope *= (1.0 - np.exp(-(2.0-t) * 10))  # Quick fade out at the end
        
        # Apply the overall envelope
        samples = 128 + (samples - 128) * overall_envelope
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
    """Class to manage the global game state."""
    def __init__(self, screen):
        """Initialize the game state."""
        try:
            self.screen = screen
            self.running = True
            self.paused = False
