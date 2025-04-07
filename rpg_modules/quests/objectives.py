"""
Specific quest objective implementations.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base import QuestObjective

@dataclass
class KillObjective(QuestObjective):
    """Objective to kill specific enemies."""
    target_type: str
    target_id: Optional[str] = None
    
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if a kill event matches this objective."""
        if event_data.get('type') != 'kill':
            return False
            
        killed_type = event_data.get('enemy_type')
        killed_id = event_data.get('enemy_id')
        
        # Check if killed enemy matches our target
        if killed_type != self.target_type:
            return False
            
        if self.target_id and killed_id != self.target_id:
            return False
            
        return self.update_progress()

@dataclass
class CollectObjective(QuestObjective):
    """Objective to collect specific items."""
    item_type: str
    item_id: Optional[str] = None
    
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if an item collection event matches this objective."""
        if event_data.get('type') != 'collect':
            return False
            
        collected_type = event_data.get('item_type')
        collected_id = event_data.get('item_id')
        
        # Check if collected item matches our target
        if collected_type != self.item_type:
            return False
            
        if self.item_id and collected_id != self.item_id:
            return False
            
        return self.update_progress(event_data.get('amount', 1))

@dataclass
class ExploreObjective(QuestObjective):
    """Objective to explore specific locations."""
    location_id: str
    area_name: str
    discovered: bool = False
    
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """Check if a location discovery event matches this objective."""
        if event_data.get('type') != 'explore':
            return False
            
        discovered_id = event_data.get('location_id')
        
        if discovered_id != self.location_id:
            return False
            
        if not self.discovered:
            self.discovered = True
            return self.update_progress()
            
        return False

@dataclass
class DeliverObjective(QuestObjective):
    """Objective to deliver items to NPCs."""
    item_id: str
    target_npc_id: str
    delivered: bool = False
    
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