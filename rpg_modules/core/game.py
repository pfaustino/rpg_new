from .dungeon import Dungeon, RoomType
from .dungeon_handler import DungeonHandler

class Game:
    def __init__(self):
        # Initialize systems
        self.event_system = EventSystem()
        self.audio_system = AudioSystem()
        
        # Initialize dungeon handler
        self.dungeon_handler = DungeonHandler(self)
        
    def load_dungeon(self, width=100, height=100, seed=None):
        """Create and load a new Veilmaster's Fortress dungeon."""
        dungeon = self.dungeon_handler.create_dungeon(width, height, seed)
        
        # Set the current map to the dungeon
        self.current_map = dungeon
        
        # Reposition player at dungeon entrance
        entrance_room = next((room for room in dungeon.rooms 
                             if room.room_type == RoomType.ENTRANCE), None)
                             
        if entrance_room:
            center_x = entrance_room.x + entrance_room.width // 2
            center_y = entrance_room.y + entrance_room.height // 2
            
            from .constants import TILE_SIZE
            self.player.x = center_x * TILE_SIZE
            self.player.y = center_y * TILE_SIZE
            
        # Trigger dungeon loaded event
        self.event_system.trigger_event(
            GameEvent(EventType.DUNGEON_LOADED, {
                "dungeon": dungeon
            })
        )
        
        return dungeon
    
    def save_game(self, save_path=None):
        """Save the current game state."""
        # Add dungeon state to save data
        save_data["dungeon"] = self.dungeon_handler.save_state()
    
    def load_game(self, save_path=None):
        """Load a saved game state."""
        # Load dungeon state if it exists
        if "dungeon" in save_data:
            self.dungeon_handler.load_state(save_data["dungeon"]) 