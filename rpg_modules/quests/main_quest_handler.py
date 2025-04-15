"""
Main quest handler module for integrating the main quest chain with the game.
"""

import os
import json
from typing import Dict, List, Optional, Any
from .manager import QuestManager
from .base import Quest, QuestType, QuestStatus

class MainQuestHandler:
    """
    Handles the main quest line functionality, including quest initialization,
    story flag tracking, and quest-specific event processing.
    """
    
    def __init__(self, quest_manager: QuestManager, game_state=None):
        """Initialize the main quest handler."""
        self.quest_manager = quest_manager
        self.game_state = game_state
        self.story_flags = {}
        self.active_quest_id = None
        
    def initialize_main_quests(self):
        """Initialize the main quest line in the quest manager."""
        # Define the main quest chain if not already defined
        if "main_story" not in self.quest_manager.get_all_quest_chains():
            chain_data = {
                "name": "Shadow of the Artifact",
                "description": "Uncover the secrets of the ancient artifact and stop the spreading corruption.",
                "quests": [
                    "mq_01_mysterious_arrival",
                    "mq_02_first_investigation", 
                    "mq_03_suspects_trail",
                    "mq_04_truth_revealed",
                    "mq_05_confrontation",
                    "mq_06_final_choice"
                ]
            }
            
            # Register the chain
            self.quest_manager.add_quest_chain("main_story", chain_data, save_to_file=True)
            print("Main quest chain initialized")
        
    def start_initial_quest(self, player=None):
        """Start the first quest in the main story chain for a new player."""
        # Get the first quest in the main chain
        chain_quests = self.quest_manager.get_quest_chain("main_story")
        if not chain_quests or len(chain_quests) == 0:
            print("No quests found in main story chain")
            return False
            
        first_quest_id = chain_quests[0]
        result = self.quest_manager.start_quest(first_quest_id, player)
        if result:
            self.active_quest_id = first_quest_id
            print(f"Started initial main quest: {first_quest_id}")
        return result
        
    def handle_flag_set(self, flag: str):
        """Handle a story flag being set during dialog."""
        if not flag or "=" not in flag:
            return False
            
        key, value = flag.split("=", 1)
        self.story_flags[key] = value
        print(f"Set story flag: {key}={value}")
        
        # Handle specific flag consequences
        if key == "trusted_suspect":
            self._handle_suspect_chosen(value)
        elif key == "bram_fate":
            self._handle_bram_fate(value)
            
        return True
        
    def _handle_suspect_chosen(self, suspect: str):
        """Handle the consequences of choosing a suspect to trust."""
        # This would update the next quest objectives or dialog options
        # based on the player's choice
        print(f"Player has decided to trust: {suspect}")
        
        # Get the next quest in the chain
        chain_quests = self.quest_manager.get_quest_chain("main_story")
        current_index = chain_quests.index(self.active_quest_id) if self.active_quest_id in chain_quests else -1
        
        if current_index >= 0 and current_index + 1 < len(chain_quests):
            next_quest_id = chain_quests[current_index + 1]
            # We might customize the next quest based on the choice
            # For now, just mark it as available
            print(f"Next quest {next_quest_id} will be affected by suspect choice")
            
    def _handle_bram_fate(self, fate: str):
        """Handle the consequences of the player's decision about Bram's fate."""
        print(f"Player has decided Bram's fate: {fate}")
        
        # This would unlock different side quests or change later quest content
        if fate == "mercy":
            # Could unlock a redemption side quest
            self._try_unlock_side_quest("sq_redemptions_price")
        elif fate == "justice":
            # Could unlock a consequence side quest
            self._try_unlock_side_quest("sq_shadows_unleashed")
            
    def _try_unlock_side_quest(self, quest_id: str):
        """Try to unlock a side quest if it exists."""
        if quest_id in self.quest_manager.all_quests:
            player = self.game_state.player if self.game_state else None
            self.quest_manager.start_quest(quest_id, player)
            print(f"Unlocked side quest: {quest_id}")
            
    def update_quest_state_from_dialog(self, dialog_id: str, node_id: str):
        """Update quest state based on dialog completion."""
        # Create an event data structure that DialogObjective can process
        event_data = {
            'type': 'dialog',
            'dialog_id': dialog_id,
            'dialog_state': node_id,
            'npc_id': None  # Would be set in a real implementation
        }
        
        # Update objectives for all active quests
        updated_quests = self.quest_manager.process_event(event_data)
        
        # Check if main story quest was updated
        for quest_id in updated_quests:
            if quest_id.startswith("mq_"):
                quest = self.quest_manager.get_quest(quest_id)
                if quest and quest.status == QuestStatus.COMPLETED:
                    print(f"Main quest {quest_id} completed through dialog")
                    
                    # Auto-advance to next quest if configured
                    if quest.next_quest_id:
                        self.quest_manager.start_quest(quest.next_quest_id)
                        self.active_quest_id = quest.next_quest_id
                        print(f"Auto-advanced to next quest: {quest.next_quest_id}")
        
        return len(updated_quests) > 0
    
    def get_story_flag(self, key: str, default=None) -> Any:
        """Get a story flag value."""
        return self.story_flags.get(key, default)
    
    def set_story_flag(self, key: str, value: Any):
        """Set a story flag value."""
        self.story_flags[key] = value
    
    def get_current_main_quest(self) -> Optional[Quest]:
        """Get the current active main quest."""
        if not self.active_quest_id:
            # Find the first incomplete main quest
            for quest_id, quest in self.quest_manager.active_quests.items():
                if quest_id.startswith("mq_"):
                    return quest
            return None
        
        return self.quest_manager.get_quest(self.active_quest_id)
    
    def save_state(self) -> Dict[str, Any]:
        """Save the state of the main quest handler."""
        return {
            "story_flags": self.story_flags,
            "active_quest_id": self.active_quest_id
        }
    
    def load_state(self, data: Dict[str, Any]):
        """Load the state of the main quest handler."""
        self.story_flags = data.get("story_flags", {})
        self.active_quest_id = data.get("active_quest_id")
        
    def set_game_state(self, game_state):
        """Set the game state reference."""
        self.game_state = game_state 