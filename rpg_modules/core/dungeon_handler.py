"""
Dungeon handler module for managing dungeon instances and integrating them with the game.
"""

from typing import Dict, List, Tuple, Optional, Any
import json
import os
import pygame

from .dungeon import Dungeon, RoomType, PuzzleState, Room
from .enums import TileType
from .events import EventType, GameEvent

class DungeonHandler:
    """
    Handler for managing dungeon instances and gameplay.
    Integrates the dungeons with the main game systems.
    """
    
    def __init__(self, game):
        """Initialize the dungeon handler."""
        self.game = game
        self.current_dungeon = None
        self.active_puzzles = {}  # roomtype -> puzzle state
        self.discovered_rooms = set()  # Set of discovered room types
        self.puzzle_progress = {}  # Tracks progress of each puzzle
        self.player_position = None  # Last known player position in dungeon
        
        # Register event handlers
        self.game.event_system.register_handler(EventType.PLAYER_MOVE, self._on_player_move)
        self.game.event_system.register_handler(EventType.INTERACT, self._on_player_interact)
        
    def create_dungeon(self, width: int, height: int, seed: Optional[int] = None) -> Dungeon:
        """Create a new Veilmaster's Fortress dungeon instance."""
        self.current_dungeon = Dungeon(width, height, seed)
        self.active_puzzles = {
            RoomType.HALL_OF_ECHOES: PuzzleState.UNSOLVED,
            RoomType.GOLEM_FORGE: PuzzleState.UNSOLVED,
            RoomType.CHASM_OF_WHISPERS: PuzzleState.UNSOLVED,
            RoomType.GALLERY_OF_SHADOWS: PuzzleState.UNSOLVED,
            RoomType.SANCTUM_OF_SEALS: PuzzleState.UNSOLVED
        }
        self.puzzle_progress = {
            RoomType.HALL_OF_ECHOES: 0,  # Sound sequence steps completed
            RoomType.GOLEM_FORGE: 0,  # Core fragments collected
            RoomType.CHASM_OF_WHISPERS: 0,  # Bridge segments revealed
            RoomType.GALLERY_OF_SHADOWS: 0,  # Paintings activated
            RoomType.SANCTUM_OF_SEALS: 0   # Seals broken
        }
        self.discovered_rooms = {RoomType.ENTRANCE}
        
        # Return the dungeon instance for integration with game map
        return self.current_dungeon
        
    def get_current_room(self, player_x: int, player_y: int) -> Optional[Room]:
        """Get the room the player is currently in."""
        if not self.current_dungeon:
            return None
            
        for room in self.current_dungeon.rooms:
            if room.contains_point(player_x, player_y):
                # Mark room as discovered
                self.discovered_rooms.add(room.room_type)
                return room
                
        return None
    
    def update_puzzle_state(self, room_type: RoomType, new_state: PuzzleState):
        """Update the state of a puzzle."""
        if room_type in self.active_puzzles:
            self.active_puzzles[room_type] = new_state
            
            # If all puzzles are solved, unlock the final chamber
            if self._are_all_puzzles_solved():
                self._unlock_ritual_chamber()
                
            # Trigger an event for the UI to update
            self.game.event_system.trigger_event(
                GameEvent(EventType.PUZZLE_STATE_CHANGED, {
                    "room_type": room_type.value,
                    "state": new_state.value,
                    "progress": self.puzzle_progress[room_type]
                })
            )
    
    def increase_puzzle_progress(self, room_type: RoomType, amount: int = 1) -> bool:
        """Increase progress on a puzzle and check if it's solved."""
        if room_type not in self.puzzle_progress:
            return False
            
        self.puzzle_progress[room_type] += amount
        
        # Check if the puzzle is now solved
        max_progress = self._get_max_puzzle_progress(room_type)
        if self.puzzle_progress[room_type] >= max_progress:
            self.puzzle_progress[room_type] = max_progress
            self.update_puzzle_state(room_type, PuzzleState.SOLVED)
            return True
            
        # If not fully solved, but progress was made
        if self.active_puzzles[room_type] != PuzzleState.IN_PROGRESS:
            self.update_puzzle_state(room_type, PuzzleState.IN_PROGRESS)
            
        return False
    
    def _get_max_puzzle_progress(self, room_type: RoomType) -> int:
        """Get the maximum progress value for a given puzzle."""
        progress_map = {
            RoomType.HALL_OF_ECHOES: 5,      # 5 sound patterns to match
            RoomType.GOLEM_FORGE: 3,         # 3 fragments to collect
            RoomType.CHASM_OF_WHISPERS: 8,   # 8 bridge segments to reveal
            RoomType.GALLERY_OF_SHADOWS: 4,  # 4 paintings to activate
            RoomType.SANCTUM_OF_SEALS: 4     # 4 elemental seals to break
        }
        return progress_map.get(room_type, 1)
    
    def _are_all_puzzles_solved(self) -> bool:
        """Check if all puzzles have been solved."""
        return all(state == PuzzleState.SOLVED for state in self.active_puzzles.values())
    
    def _unlock_ritual_chamber(self):
        """Unlock the final ritual chamber."""
        # Find the ritual chamber
        ritual_chamber = next((room for room in self.current_dungeon.rooms 
                              if room.room_type == RoomType.RITUAL_CHAMBER), None)
        
        if not ritual_chamber:
            return
            
        # Unlock all doors leading to the ritual chamber
        for door_x, door_y in ritual_chamber.doors:
            # Change from locked door to normal door
            if 0 <= door_x < self.current_dungeon.width and 0 <= door_y < self.current_dungeon.height:
                if self.current_dungeon.base_grid[door_y][door_x] == TileType.STONE_WALL:
                    self.current_dungeon.base_grid[door_y][door_x] = TileType.DOOR
                    self.current_dungeon.collision_grid[door_y][door_x] = False
        
        # Trigger an event for this milestone
        self.game.event_system.trigger_event(
            GameEvent(EventType.RITUAL_CHAMBER_UNLOCKED, {})
        )
    
    def _on_player_move(self, event: GameEvent):
        """Handle player movement within the dungeon."""
        if not self.current_dungeon:
            return
            
        # Extract player position from event
        player_pos = event.data.get("position", (0, 0))
        player_x, player_y = player_pos
        
        # Convert world coordinates to grid coordinates
        from .constants import TILE_SIZE
        grid_x = player_x // TILE_SIZE
        grid_y = player_y // TILE_SIZE
        
        # Update player position
        self.player_position = (grid_x, grid_y)
        
        # Check which room the player is in
        current_room = self.get_current_room(grid_x, grid_y)
        if current_room:
            # First time entering a room with a puzzle
            if (current_room.room_type in self.active_puzzles and 
                current_room.room_type not in self.discovered_rooms):
                
                # Trigger an event for entering a puzzle room
                self.game.event_system.trigger_event(
                    GameEvent(EventType.ENTERED_PUZZLE_ROOM, {
                        "room_type": current_room.room_type.value
                    })
                )
    
    def _on_player_interact(self, event: GameEvent):
        """Handle player interactions with dungeon features."""
        if not self.current_dungeon or not self.player_position:
            return
            
        # Get interaction target and position
        target = event.data.get("target")
        target_pos = event.data.get("position")
        
        if not target or not target_pos:
            return
            
        # Convert world coordinates to grid coordinates
        from .constants import TILE_SIZE
        grid_x = target_pos[0] // TILE_SIZE
        grid_y = target_pos[1] // TILE_SIZE
        
        # Get current room
        current_room = self.get_current_room(*self.player_position)
        if not current_room:
            return
            
        # Handle interactions based on room type and target
        if current_room.room_type == RoomType.HALL_OF_ECHOES:
            self._handle_hall_of_echoes_interaction(target, grid_x, grid_y)
        elif current_room.room_type == RoomType.GOLEM_FORGE:
            self._handle_golem_forge_interaction(target, grid_x, grid_y)
        elif current_room.room_type == RoomType.CHASM_OF_WHISPERS:
            self._handle_chasm_interaction(target, grid_x, grid_y)
        elif current_room.room_type == RoomType.GALLERY_OF_SHADOWS:
            self._handle_gallery_interaction(target, grid_x, grid_y)
        elif current_room.room_type == RoomType.SANCTUM_OF_SEALS:
            self._handle_sanctum_interaction(target, grid_x, grid_y)
    
    def _handle_hall_of_echoes_interaction(self, target, x, y):
        """Handle interactions in the Hall of Echoes."""
        # Check if interacting with a sound marker
        if self.current_dungeon.decoration_grid[y][x] == TileType.ROCK:
            # Play sound effect
            self.game.audio_system.play_sound("echo")
            
            # Advance puzzle progress
            self.increase_puzzle_progress(RoomType.HALL_OF_ECHOES)
    
    def _handle_golem_forge_interaction(self, target, x, y):
        """Handle interactions in the Golem Forge."""
        # Check if interacting with a titan fragment
        if self.current_dungeon.decoration_grid[y][x] == TileType.ROCK:
            # Remove the fragment (collect it)
            self.current_dungeon.decoration_grid[y][x] = None
            
            # Advance puzzle progress
            self.increase_puzzle_progress(RoomType.GOLEM_FORGE)
    
    def _handle_chasm_interaction(self, target, x, y):
        """Handle interactions in the Chasm of Whispers."""
        # Check if interacting with water (potentially revealing bridge)
        if self.current_dungeon.base_grid[y][x] == TileType.WATER:
            # Check if this is part of the hidden bridge path
            # This would need a more sophisticated check in a real implementation
            
            # For demonstration, reveal a bridge segment
            self.current_dungeon.base_grid[y][x] = TileType.STONE
            self.current_dungeon.collision_grid[y][x] = False
            
            # Advance puzzle progress
            self.increase_puzzle_progress(RoomType.CHASM_OF_WHISPERS)
    
    def _handle_gallery_interaction(self, target, x, y):
        """Handle interactions in the Gallery of Shadows."""
        # Check if interacting with a painting
        if self.current_dungeon.decoration_grid[y][x] == TileType.ROCK:
            # Activate painting (visual effect would be handled by rendering system)
            
            # Advance puzzle progress
            self.increase_puzzle_progress(RoomType.GALLERY_OF_SHADOWS)
    
    def _handle_sanctum_interaction(self, target, x, y):
        """Handle interactions in the Sanctum of Seals."""
        # Check if interacting with an elemental seal
        if self.current_dungeon.decoration_grid[y][x] in [TileType.ROCK, TileType.WATER, TileType.STONE, TileType.BUSH]:
            # Remove the seal
            self.current_dungeon.decoration_grid[y][x] = None
            
            # Advance puzzle progress
            self.increase_puzzle_progress(RoomType.SANCTUM_OF_SEALS)
    
    def save_state(self) -> Dict:
        """Save the current dungeon state for game saving."""
        if not self.current_dungeon:
            return {}
            
        return {
            "active_puzzles": {k.value: v.value for k, v in self.active_puzzles.items()},
            "puzzle_progress": {k.value: v for k, v in self.puzzle_progress.items()},
            "discovered_rooms": [room.value for room in self.discovered_rooms],
            "player_position": self.player_position
        }
    
    def load_state(self, state: Dict):
        """Load a previously saved dungeon state."""
        if not state or not self.current_dungeon:
            return
            
        # Convert string keys back to enum types
        self.active_puzzles = {
            RoomType(k): PuzzleState(v) 
            for k, v in state.get("active_puzzles", {}).items()
        }
        
        self.puzzle_progress = {
            RoomType(k): v 
            for k, v in state.get("puzzle_progress", {}).items()
        }
        
        self.discovered_rooms = {
            RoomType(room) for room in state.get("discovered_rooms", [])
        }
        
        self.player_position = state.get("player_position")
        
        # If ritual chamber should be unlocked, make sure it is
        if self._are_all_puzzles_solved():
            self._unlock_ritual_chamber() 