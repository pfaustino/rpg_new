"""
Specific quest objective implementations.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from .base import QuestObjective, Quest
import pygame

@dataclass
class KillObjective(QuestObjective):
    """Objective to kill specific enemies."""
    target_type: str = field(init=False)
    description: str = field(init=False)
    required_progress: int = field(init=False)

    def __init__(self, target_type: str, description: str = "", required_progress: int = 1):
        self.target_type = target_type
        self.description = description
        self.required_progress = required_progress
        if not self.description:
            self.description = f"Kill {self.required_progress} {self.target_type}"
        self.marker_color = (255, 0, 0)  # Red for combat
        self.marker_shape = "triangle"  # Triangle for combat
        self.marker_size = 10  # Larger for combat
        self.icon = "monster"  # Monster icon

    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if a kill event matches this objective."""
        if event_data.get('type') != 'kill':
            return False
            
        killed_type = event_data.get('enemy_type')
        killed_id = event_data.get('enemy_id')
        
        # Check if killed enemy matches our target
        if killed_type != self.target_type:
            return False
            
        if hasattr(self, 'target_id') and self.target_id and killed_id != self.target_id:
            return False
            
        return self.update_progress()

@dataclass
class CollectObjective(QuestObjective):
    """Objective to collect specific items."""
    item_type: str = field(init=False)
    description: str = field(init=False)
    required_progress: int = field(init=False)

    def __init__(self, item_type: str, description: str = "", required_progress: int = 1):
        self.item_type = item_type
        self.description = description
        self.required_progress = required_progress
        if not self.description:
            self.description = f"Collect {self.required_progress} {self.item_type}"
        self.marker_color = (0, 255, 0)  # Green for collection
        self.marker_shape = "square"  # Square for items
        self.marker_size = 8
        self.icon = "item"
        # Set appropriate icon based on item type
        if "mushroom" in self.item_type.lower():
            self.icon = "mushroom"
        elif "plant" in self.item_type.lower() or "herb" in self.item_type.lower():
            self.icon = "plant"
        elif "ore" in self.item_type.lower() or "crystal" in self.item_type.lower():
            self.icon = "ore"

    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if an item collection event matches this objective."""
        if event_data.get('type') != 'collect':
            return False
            
        collected_type = event_data.get('item_type')
        collected_id = event_data.get('item_id')
        
        # Check if collected item matches our target
        if collected_type != self.item_type:
            return False
            
        if hasattr(self, 'item_id') and self.item_id and collected_id != self.item_id:
            return False
            
        return self.update_progress(event_data.get('amount', 1))

@dataclass
class ExploreObjective(QuestObjective):
    """Objective to explore specific locations."""
    location_id: str = field(init=False)
    area_name: str = field(init=False)
    description: str = field(init=False)
    required_progress: int = field(init=False)

    def __init__(self, location_id: str, area_name: str, description: str = "", required_progress: int = 1):
        self.location_id = location_id
        self.area_name = area_name
        self.description = description
        self.required_progress = required_progress
        if not self.description:
            self.description = f"Explore {self.area_name}"
        self.marker_color = (0, 0, 255)  # Blue for exploration
        self.marker_shape = "circle"  # Circle for areas
        self.marker_size = 12  # Larger for areas
        self.icon = "exp"  # Experience icon for exploration
        self.discovered = False
        self.objective_coords = []

    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if a location discovery event matches this objective."""
        if event_data.get('type') != 'explore':
            return False
            
        discovered_id = event_data.get('location_id')
        discovered_coords = event_data.get('coordinates')
        
        if discovered_id != self.location_id:
            return False
            
        # Check if the discovered coordinates match any of our objective coordinates
        if discovered_coords and discovered_coords in self.objective_coords:
            if not self.discovered:
                self.discovered = True
                return self.update_progress()
                
        return False

@dataclass
class DeliverObjective(QuestObjective):
    """Objective to deliver items to NPCs."""
    item_id: str = field(init=False)
    target_npc_id: str = field(init=False)
    description: str = field(init=False)
    required_progress: int = field(init=False)

    def __init__(self, item_id: str, target_npc_id: str, description: str = "", required_progress: int = 1):
        self.item_id = item_id
        self.target_npc_id = target_npc_id
        self.description = description
        self.required_progress = required_progress
        if not self.description:
            self.description = f"Deliver item to {self.target_npc_id}"
        self.marker_color = (255, 165, 0)  # Orange for delivery
        self.marker_shape = "diamond"  # Diamond for NPCs
        self.marker_size = 10
        self.icon = "item"  # Item icon for delivery
        self.delivered = False

    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if an item delivery event matches this objective."""
        if event_data.get('type') != 'deliver':
            return False
            
        delivered_item = event_data.get('item_id')
        target_npc = event_data.get('npc_id')
        
        if delivered_item != self.item_id or target_npc != self.target_npc_id:
            return False
            
        if not self.delivered:
            self.delivered = True
            return self.update_progress()
            
        return False

    def draw_marker(self, screen: pygame.Surface, x: int, y: int):
        """Draw a diamond-shaped marker for NPC delivery objectives."""
        points = [
            (x, y - self.marker_size),  # Top point
            (x + self.marker_size, y),  # Right point
            (x, y + self.marker_size),  # Bottom point
            (x - self.marker_size, y)   # Left point
        ]
        pygame.draw.polygon(screen, self.marker_color, points)

@dataclass
class DialogObjective(QuestObjective):
    """Objective to talk to NPCs and complete dialog sequences."""
    dialog_id: str = field(init=False)
    description: str = field(init=False)
    required_progress: int = field(init=False)
    npc_id: Optional[str] = field(default=None, init=False)
    dialog_completed: bool = field(default=False, init=False)
    
    def __init__(self, dialog_id: str, description: str = "", required_progress: int = 1, npc_id: Optional[str] = None):
        self.dialog_id = dialog_id
        self.description = description
        self.required_progress = required_progress
        self.npc_id = npc_id
        if not self.description:
            self.description = f"Talk to NPC about {self.dialog_id}"
        self.marker_color = (255, 255, 0)  # Yellow for dialog
        self.marker_shape = "diamond"  # Diamond for NPCs
        self.marker_size = 10
        self.icon = "dialog"  # Dialog icon
        
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if a dialog event matches this objective."""
        if event_data.get('type') != 'dialog':
            return False
            
        dialog_id = event_data.get('dialog_id')
        
        # Check if the dialog matches our target
        if dialog_id != self.dialog_id:
            return False
            
        # Check NPC ID if specified
        if self.npc_id and event_data.get('npc_id') != self.npc_id:
            return False
            
        # Check if dialog reached a conclusion state
        dialog_state = event_data.get('dialog_state', '')
        if dialog_state != 'conclusion' and 'complete' not in dialog_state:
            return False
            
        if not self.dialog_completed:
            self.dialog_completed = True
            return self.update_progress()
            
        return False
        
    def draw_marker(self, screen: pygame.Surface, x: int, y: int):
        """Draw a marker for dialog objectives."""
        # Draw a speech bubble shape
        bubble_radius = self.marker_size
        # Main circle
        pygame.draw.circle(screen, self.marker_color, (x, y), bubble_radius)
        # Outline
        pygame.draw.circle(screen, (0, 0, 0), (x, y), bubble_radius, 2)
        # Speech pointer
        points = [
            (x, y + bubble_radius - 2),
            (x - bubble_radius//2, y + bubble_radius + bubble_radius//2),
            (x + bubble_radius//4, y + bubble_radius + bubble_radius//4)
        ]
        pygame.draw.polygon(screen, self.marker_color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 2) 