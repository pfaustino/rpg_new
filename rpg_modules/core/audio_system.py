"""
Audio system module for handling music and sound effects in the game.
"""

import pygame
import os
from typing import Dict, Optional

class AudioSystem:
    """
    Handles playing and managing game audio including music and sound effects.
    """
    
    def __init__(self, sound_path: str = "assets/audio"):
        """
        Initialize the audio system.
        
        Args:
            sound_path: Base path to audio assets
        """
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.sound_path = sound_path
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        
        # Audio settings
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.sound_enabled = True
        self.music_enabled = True
        
        # Current music track
        self.current_music = None
        
        # Create sound directory if it doesn't exist
        os.makedirs(sound_path, exist_ok=True)
        os.makedirs(os.path.join(sound_path, "music"), exist_ok=True)
        os.makedirs(os.path.join(sound_path, "sfx"), exist_ok=True)
        
        # Register default music tracks
        self._register_default_music()
        
        # Register default sound effects
        self._register_default_sounds()
    
    def _register_default_music(self):
        """Register default music tracks."""
        default_tracks = {
            "title_theme": "title_theme.mp3",
            "town_theme": "town_theme.mp3",
            "dungeon_theme": "dungeon_theme.mp3",
            "combat_theme": "combat_theme.mp3",
            "victory_theme": "victory_theme.mp3"
        }
        
        for track_id, filename in default_tracks.items():
            self.register_music(track_id, filename)
    
    def _register_default_sounds(self):
        """Register default sound effects."""
        default_sounds = {
            "button_click": "ui_click.wav",
            "quest_accept": "quest_accept.wav",
            "quest_complete": "quest_complete.wav",
            "objective_complete": "objective_complete.wav",
            "item_pickup": "item_pickup.wav",
            "level_up": "level_up.wav",
            "player_hit": "player_hit.wav",
            "enemy_hit": "enemy_hit.wav",
            "player_death": "player_death.wav",
            "enemy_death": "enemy_death.wav"
        }
        
        for sound_id, filename in default_sounds.items():
            self.register_sound(sound_id, filename)
    
    def register_sound(self, sound_id: str, filename: str) -> bool:
        """
        Register a sound effect.
        
        Args:
            sound_id: Identifier for the sound
            filename: Sound file name
            
        Returns:
            Success of registration
        """
        sound_path = os.path.join(self.sound_path, "sfx", filename)
        
        # Only try to load the sound if the file exists
        if os.path.exists(sound_path):
            try:
                self.sounds[sound_id] = pygame.mixer.Sound(sound_path)
                self.sounds[sound_id].set_volume(self.sound_volume)
                return True
            except Exception as e:
                print(f"Error loading sound {sound_id} from {sound_path}: {e}")
        else:
            # For development, create a dummy sound
            print(f"Sound file not found: {sound_path}, using placeholder")
            self.sounds[sound_id] = pygame.mixer.Sound(pygame.sndarray.array([0] * 44100))
            self.sounds[sound_id].set_volume(0.0)  # Silent
            
        return False
    
    def register_music(self, track_id: str, filename: str) -> bool:
        """
        Register a music track.
        
        Args:
            track_id: Identifier for the track
            filename: Music file name
            
        Returns:
            Success of registration
        """
        music_path = os.path.join(self.sound_path, "music", filename)
        
        # Only store the path, we'll load it when needed
        self.music_tracks[track_id] = music_path
        return True
    
    def play_sound(self, sound_id: str) -> bool:
        """
        Play a sound effect.
        
        Args:
            sound_id: Identifier for the sound to play
            
        Returns:
            Success of playback
        """
        if not self.sound_enabled:
            return False
            
        if sound_id in self.sounds:
            self.sounds[sound_id].play()
            return True
        else:
            print(f"Sound {sound_id} not registered")
            return False
    
    def play_music(self, track_id: str, loop: bool = True) -> bool:
        """
        Play a music track.
        
        Args:
            track_id: Identifier for the track to play
            loop: Whether to loop the track
            
        Returns:
            Success of playback
        """
        if not self.music_enabled:
            return False
            
        if track_id in self.music_tracks:
            music_path = self.music_tracks[track_id]
            
            # Only load and play if the file exists
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    
                    loops = -1 if loop else 0
                    pygame.mixer.music.play(loops)
                    
                    self.current_music = track_id
                    return True
                except Exception as e:
                    print(f"Error playing music {track_id} from {music_path}: {e}")
            else:
                print(f"Music file not found: {music_path}")
            
            return False
        else:
            print(f"Music track {track_id} not registered")
            return False
    
    def stop_music(self):
        """Stop the currently playing music."""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """Pause the currently playing music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause the currently playing music."""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float):
        """
        Set the music volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume: float):
        """
        Set the sound effects volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def toggle_music(self, enabled: Optional[bool] = None):
        """
        Toggle music on/off.
        
        Args:
            enabled: If provided, set to this value, otherwise toggle
        """
        if enabled is not None:
            self.music_enabled = enabled
        else:
            self.music_enabled = not self.music_enabled
            
        if not self.music_enabled:
            self.stop_music()
        elif self.current_music:
            self.play_music(self.current_music)
    
    def toggle_sound(self, enabled: Optional[bool] = None):
        """
        Toggle sound effects on/off.
        
        Args:
            enabled: If provided, set to this value, otherwise toggle
        """
        if enabled is not None:
            self.sound_enabled = enabled
        else:
            self.sound_enabled = not self.sound_enabled 