"""
Dynamic game settings for the RPG game.
"""

class GameSettings:
    """
    A class to store and manage dynamic game settings that can be changed during gameplay.
    
    This class uses the Singleton pattern to ensure there's only one instance of the settings
    throughout the game. Access settings through GameSettings.instance().
    """
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Get the singleton instance of GameSettings."""
        if cls._instance is None:
            cls._instance = GameSettings()
        return cls._instance
    
    def __init__(self):
        """Initialize default settings."""
        if GameSettings._instance is not None:
            raise RuntimeError("GameSettings is a singleton. Use GameSettings.instance() instead.")
        
        # Map settings
        self.map_width = 80
        self.map_height = 80
        
        # Monster settings
        self.monster_speed_multiplier = 2.0  # Default: normal speed (1.0)
        
        # Player settings
        self.player_speed_multiplier = 1.0
        
        # Difficulty settings
        self.difficulty_level = 1  # 1 = easy, 2 = medium, 3 = hard
        
        # Environment settings
        self.day_night_cycle_enabled = True
        
        # Debug settings
        self.debug_visualization = False  # Toggle for debug visualization like bounding boxes
        
    def reset_to_defaults(self):
        """Reset all settings to their default values."""
        self.monster_speed_multiplier = 1.0
        self.player_speed_multiplier = 1.0
        self.difficulty_level = 1
        self.day_night_cycle_enabled = True
        self.debug_visualization = False
    
    def adjust_difficulty(self, level):
        """
        Adjust game settings based on difficulty level.
        
        Args:
            level: 1 = easy, 2 = medium, 3 = hard
        """
        self.difficulty_level = level
        
        if level == 1:  # Easy
            self.monster_speed_multiplier = 0.8
        elif level == 2:  # Medium
            self.monster_speed_multiplier = 1.0
        elif level == 3:  # Hard
            self.monster_speed_multiplier = 1.2
        
    def increase_monster_speed(self, increment=0.1):
        """Increase monster speed by the given increment."""
        self.monster_speed_multiplier += increment
        print(f"Monster speed increased to {self.monster_speed_multiplier:.1f}x")
        
    def decrease_monster_speed(self, decrement=0.1):
        """Decrease monster speed by the given decrement."""
        self.monster_speed_multiplier = max(0.1, self.monster_speed_multiplier - decrement)
        print(f"Monster speed decreased to {self.monster_speed_multiplier:.1f}x")

# Initialize the singleton instance
GameSettings._instance = GameSettings() 