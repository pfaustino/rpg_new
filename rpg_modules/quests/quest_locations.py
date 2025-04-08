"""
Quest location and navigation system.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import random

@dataclass
class QuestLocation:
    """Represents a location for a quest objective."""
    location_id: str
    area_name: str
    coordinates: Tuple[int, int]  # (x, y) tile coordinates
    radius: int  # Radius in tiles for objective area
    description: str
    is_discovered: bool = False

class QuestNavigation:
    """Manages quest locations and navigation."""
    
    def __init__(self, game_map):
        """Initialize the quest navigation system."""
        self.game_map = game_map
        self.locations: Dict[str, QuestLocation] = {}
        self.active_markers: Dict[str, List[Tuple[int, int]]] = {}
        
    def add_location(self, location: QuestLocation) -> bool:
        """Add a new quest location."""
        if location.location_id in self.locations:
            return False
            
        self.locations[location.location_id] = location
        return True
        
    def get_location(self, location_id: str) -> Optional[QuestLocation]:
        """Get a quest location by ID."""
        return self.locations.get(location_id)
        
    def discover_location(self, location_id: str) -> bool:
        """Mark a location as discovered."""
        location = self.get_location(location_id)
        if not location:
            return False
            
        location.is_discovered = True
        return True
        
    def generate_objective_area(self, location: QuestLocation) -> List[Tuple[int, int]]:
        """Generate coordinates for objectives within a location's radius."""
        coords = []
        center_x, center_y = location.coordinates
        
        # Generate points in a circular pattern
        for r in range(1, location.radius + 1):
            for angle in range(0, 360, 45):  # 8 points per radius
                x = center_x + int(r * cos(angle))
                y = center_y + int(r * sin(angle))
                
                # Check if the tile is valid and walkable
                if self.game_map.is_valid_position(x, y) and self.game_map.is_walkable(x, y):
                    coords.append((x, y))
                    
        return coords
        
    def set_active_markers(self, quest_id: str, location_id: str) -> bool:
        """Set active markers for a quest's objectives."""
        location = self.get_location(location_id)
        if not location:
            return False
            
        # Generate objective coordinates
        objective_coords = self.generate_objective_area(location)
        self.active_markers[quest_id] = objective_coords
        return True
        
    def clear_markers(self, quest_id: str):
        """Clear markers for a quest."""
        if quest_id in self.active_markers:
            del self.active_markers[quest_id]
            
    def get_markers(self, quest_id: str) -> List[Tuple[int, int]]:
        """Get markers for a quest."""
        return self.active_markers.get(quest_id, [])
        
    def get_distance_to_location(self, player_pos: Tuple[int, int], location_id: str) -> float:
        """Calculate distance from player to a quest location."""
        location = self.get_location(location_id)
        if not location:
            return float('inf')
            
        px, py = player_pos
        lx, ly = location.coordinates
        return ((px - lx) ** 2 + (py - ly) ** 2) ** 0.5
        
    def get_direction_to_location(self, player_pos: Tuple[int, int], location_id: str) -> str:
        """Get a cardinal direction to a quest location."""
        location = self.get_location(location_id)
        if not location:
            return "Unknown"
            
        px, py = player_pos
        lx, ly = location.coordinates
        
        dx = lx - px
        dy = ly - py
        
        if abs(dx) > abs(dy):
            return "East" if dx > 0 else "West"
        else:
            return "South" if dy > 0 else "North"
            
    def get_navigation_hint(self, player_pos: Tuple[int, int], location_id: str) -> str:
        """Get a navigation hint for a quest location."""
        location = self.get_location(location_id)
        if not location:
            return "Location not found"
            
        if location.is_discovered:
            distance = self.get_distance_to_location(player_pos, location_id)
            direction = self.get_direction_to_location(player_pos, location_id)
            return f"Head {direction} to {location.area_name} ({int(distance)} tiles away)"
        else:
            return f"Search for {location.description}" 