"""
Quest manager module for managing quests in the game.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from .base import Quest, QuestStatus, QuestType
from .log import QuestLog
from .loader import QuestLoader, add_quest_to_file, add_quest_chain_to_file

class QuestManager:
    """Manages all quest-related functionality in the game."""
    
    def __init__(self, quest_data_path: str = "data/quests"):
        """Initialize the quest manager."""
        self.quest_data_path = quest_data_path
        self.loader = QuestLoader(quest_data_path)
        self.quest_log = QuestLog()
        self.all_quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: Dict[str, Quest] = {}
        self.available_quests: Dict[str, Quest] = {}
        
        # Ensure quest data directory exists
        os.makedirs(quest_data_path, exist_ok=True)
        
        # Track event handlers
        self.event_listeners = []
    
    def initialize(self, player=None):
        """Initialize the quest system."""
        # Load all quests
        self.all_quests = self.loader.load_all_quests()
        
        # Update quest availability based on player
        if player:
            self.update_quest_availability(player)
    
    def update_quest_availability(self, player):
        """Update which quests are available to the player."""
        self.available_quests = {}
        
        for quest_id, quest in self.all_quests.items():
            # Skip quests already in the quest log
            if self.quest_log.has_quest(quest) or self.quest_log.has_completed_quest(quest):
                continue
                
            # Check if quest is available to the player
            if quest.is_available(player):
                self.available_quests[quest_id] = quest
    
    def start_quest(self, quest_id: str, player=None) -> bool:
        """Start a quest by ID."""
        quest = self.all_quests.get(quest_id)
        if not quest:
            print(f"Quest not found: {quest_id}")
            return False
            
        # Check if quest is available to the player
        if player and not quest.is_available(player):
            print(f"Quest {quest_id} is not available to the player")
            return False
            
        # Start the quest
        if quest.start():
            # Add to quest log
            self.quest_log.add_quest(quest)
            self.active_quests[quest_id] = quest
            
            print(f"Started quest: {quest.title}")
            return True
            
        return False
    
    def complete_quest(self, quest_id: str, player=None) -> bool:
        """Mark a quest as completed."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            print(f"Active quest not found: {quest_id}")
            return False
            
        # Check if all objectives are complete
        if not all(obj.is_complete() for obj in quest.objectives):
            print(f"Cannot complete quest {quest_id}: not all objectives are complete")
            return False
            
        # Complete the quest
        quest.status = QuestStatus.COMPLETED
        
        print(f"Completed quest: {quest.title}")
        return True
    
    def turn_in_quest(self, quest_id: str, player) -> bool:
        """Turn in a completed quest to receive rewards."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            print(f"Active quest not found: {quest_id}")
            return False
            
        # Check if quest is completed
        if quest.status != QuestStatus.COMPLETED:
            print(f"Cannot turn in quest {quest_id}: quest is not completed")
            return False
            
        # Turn in the quest
        if quest.turn_in(player):
            # Move to completed quests
            self.completed_quests[quest_id] = quest
            self.quest_log.complete_quest(quest)
            self.active_quests.pop(quest_id, None)
            
            # Check for next quest in chain
            if quest.next_quest_id and quest.next_quest_id in self.all_quests:
                print(f"Next quest in chain available: {self.all_quests[quest.next_quest_id].title}")
                self.update_quest_availability(player)
                
            print(f"Turned in quest: {quest.title}")
            return True
            
        return False
    
    def fail_quest(self, quest_id: str) -> bool:
        """Mark a quest as failed."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            print(f"Active quest not found: {quest_id}")
            return False
            
        # Fail the quest
        quest.status = QuestStatus.FAILED
        
        # Remove from active quests
        self.active_quests.pop(quest_id, None)
        
        print(f"Failed quest: {quest.title}")
        return True
    
    def abandon_quest(self, quest_id: str) -> bool:
        """Abandon a quest."""
        quest = self.active_quests.get(quest_id)
        if not quest:
            print(f"Active quest not found: {quest_id}")
            return False
            
        # Remove from quest log
        if self.quest_log.has_quest(quest):
            # Remove from active quests
            self.active_quests.pop(quest_id, None)
            
            # Reset quest status
            quest.status = QuestStatus.NOT_STARTED
            
            print(f"Abandoned quest: {quest.title}")
            return True
            
        return False
    
    def process_event(self, event_data: Dict[str, Any], player=None) -> List[str]:
        """Process game events and update quest progress."""
        updated_quests = []
        
        for quest_id, quest in self.active_quests.items():
            if quest.status == QuestStatus.IN_PROGRESS:
                if quest.update_objectives(event_data):
                    updated_quests.append(quest_id)
                    
                    # Check if quest is now complete
                    if quest.status == QuestStatus.COMPLETED:
                        print(f"Quest completed: {quest.title}")
        
        # Update quest availability based on event
        if player:
            self.update_quest_availability(player)
            
        return updated_quests
    
    def get_available_quests(self) -> Dict[str, Quest]:
        """Get quests that are available to the player."""
        return self.available_quests
    
    def get_active_quests(self) -> Dict[str, Quest]:
        """Get quests that are currently active."""
        return self.active_quests
    
    def get_completed_quests(self) -> Dict[str, Quest]:
        """Get quests that have been completed."""
        return self.completed_quests
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.all_quests.get(quest_id)
    
    def save_all_quests(self, file_path: str = None) -> bool:
        """Save all quests to a file."""
        if file_path is None:
            file_path = os.path.join(self.quest_data_path, "quests.json")
            
        try:
            data = {"quests": []}
            
            # Convert quests to dict and add to data
            for quest in self.all_quests.values():
                quest_dict = self.loader._quest_to_dict(quest)
                data["quests"].append(quest_dict)
            
            # Save to file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
                
            print(f"Saved {len(self.all_quests)} quests to {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving quests to {file_path}: {e}")
            return False
    
    def add_quest(self, quest_data: Dict[str, Any], save_to_file: bool = True) -> Optional[Quest]:
        """Add a new quest from data."""
        # Create quest object
        quest = self.loader._create_quest_from_data(quest_data)
        if not quest:
            return None
            
        # Add to all quests
        self.all_quests[quest.id] = quest
        
        # Save to file if requested
        if save_to_file:
            file_path = os.path.join(self.quest_data_path, f"{quest.quest_type.name.lower()}_quests.json")
            self.loader.save_quest_to_file(quest, file_path)
            
        return quest
    
    def add_quest_chain(self, chain_id: str, chain_data: Dict[str, Any], save_to_file: bool = True) -> bool:
        """Add a new quest chain."""
        try:
            # Add chain to loader
            if "quests" in chain_data:
                self.loader.quest_chains[chain_id] = chain_data["quests"]
                
                # Set chain references on quests
                for i, quest_id in enumerate(chain_data["quests"]):
                    if quest_id in self.all_quests:
                        quest = self.all_quests[quest_id]
                        quest.chain_id = chain_id
                        quest.chain_position = i + 1
                        
                        # Set next quest reference if not the last quest
                        if i < len(chain_data["quests"]) - 1:
                            quest.next_quest_id = chain_data["quests"][i + 1]
            
            # Save to file if requested
            if save_to_file:
                file_path = os.path.join(self.quest_data_path, "quest_chains.json")
                add_quest_chain_to_file(chain_id, chain_data, file_path)
                
            return True
            
        except Exception as e:
            print(f"Error adding quest chain {chain_id}: {e}")
            return False
    
    def get_quest_chain(self, chain_id: str) -> List[str]:
        """Get a quest chain by ID."""
        return self.loader.get_quest_chain(chain_id)
    
    def get_all_quest_chains(self) -> Dict[str, Any]:
        """Get all quest chains."""
        return self.loader.get_all_quest_chains()
    
    def register_event_listener(self, listener):
        """Register an event listener."""
        self.event_listeners.append(listener)
    
    def unregister_event_listener(self, listener):
        """Unregister an event listener."""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
    
    def _notify_listeners(self, event_type: str, quest_id: str):
        """Notify event listeners of a quest event."""
        for listener in self.event_listeners:
            listener(event_type, quest_id) 