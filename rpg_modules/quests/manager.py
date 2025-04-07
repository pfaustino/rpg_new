"""
Quest management system.
"""

from typing import Dict, List, Optional, Any
from .base import Quest, QuestStatus, QuestType

class QuestLog:
    """Manages all quests in the game."""
    
    def __init__(self):
        """Initialize the quest manager."""
        self.available_quests: Dict[str, Quest] = {}  # All quests in the game
        self.active_quests: Dict[str, Quest] = {}    # Currently active quests
        self.completed_quests: Dict[str, Quest] = {} # Completed and turned in quests
        
    def add_quest(self, quest: Quest) -> bool:
        """
        Add a new quest to the available quests.
        
        Args:
            quest: The quest to add
            
        Returns:
            bool: True if quest was added successfully
        """
        if quest.id in self.available_quests:
            return False
            
        self.available_quests[quest.id] = quest
        return True
        
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by its ID."""
        return (
            self.active_quests.get(quest_id) or
            self.completed_quests.get(quest_id) or
            self.available_quests.get(quest_id)
        )
        
    def get_available_quests(self, player) -> List[Quest]:
        """Get all quests available to the player."""
        return [
            quest for quest in self.available_quests.values()
            if quest.is_available(player)
        ]
        
    def get_active_quests(self) -> List[Quest]:
        """Get all currently active quests."""
        return list(self.active_quests.values())
        
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return list(self.completed_quests.values())
        
    def start_quest(self, quest_id: str, player) -> bool:
        """
        Start a quest if it's available.
        
        Args:
            quest_id: ID of the quest to start
            player: The player starting the quest
            
        Returns:
            bool: True if quest was started successfully
        """
        quest = self.available_quests.get(quest_id)
        if not quest or not quest.is_available(player):
            return False
            
        if quest.start():
            self.active_quests[quest_id] = quest
            del self.available_quests[quest_id]
            return True
        return False
        
    def complete_quest(self, quest_id: str, player) -> bool:
        """
        Complete a quest and grant rewards.
        
        Args:
            quest_id: ID of the quest to complete
            player: The player completing the quest
            
        Returns:
            bool: True if quest was completed successfully
        """
        quest = self.active_quests.get(quest_id)
        if not quest or quest.status != QuestStatus.COMPLETED:
            return False
            
        if quest.turn_in(player):
            self.completed_quests[quest_id] = quest
            del self.active_quests[quest_id]
            return True
        return False
        
    def update_quests(self, event_data: Dict[str, Any]) -> List[str]:
        """
        Update all active quests based on an event.
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            List[str]: IDs of quests that were updated
        """
        updated_quests = []
        for quest in self.active_quests.values():
            if quest.update_objectives(event_data):
                updated_quests.append(quest.id)
        return updated_quests
        
    def get_quests_by_type(self, quest_type: QuestType) -> List[Quest]:
        """Get all quests of a specific type."""
        all_quests = {
            **self.available_quests,
            **self.active_quests,
            **self.completed_quests
        }
        return [
            quest for quest in all_quests.values()
            if quest.quest_type == quest_type
        ]
        
    def get_quest_chain(self, quest_id: str) -> List[Quest]:
        """
        Get a quest and all its prerequisites in order.
        
        Args:
            quest_id: ID of the final quest in the chain
            
        Returns:
            List[Quest]: List of quests in prerequisite order
        """
        quest_chain = []
        current_quest = self.get_quest(quest_id)
        
        if not current_quest:
            return []
            
        # Build chain backwards
        while current_quest:
            quest_chain.insert(0, current_quest)
            if not current_quest.prerequisites:
                break
                
            # Get the first incomplete prerequisite
            for prereq_id in current_quest.prerequisites:
                prereq = self.get_quest(prereq_id)
                if prereq and prereq.status != QuestStatus.TURNED_IN:
                    current_quest = prereq
                    break
            else:
                break
                
        return quest_chain 