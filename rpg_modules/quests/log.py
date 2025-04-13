"""
Quest log module for managing player quests.
"""

from typing import List, Dict, Optional
from .base import Quest, QuestType

class QuestLog:
    """Manages the player's active and completed quests."""
    
    def __init__(self):
        """Initialize an empty quest log."""
        self.active_quests: Dict[QuestType, List[Quest]] = {
            QuestType.MAIN: [],
            QuestType.SIDE: [],
            QuestType.DAILY: [],
            QuestType.WORLD: [],
            QuestType.HIDDEN: []
        }
        self.completed_quests: List[Quest] = []
    
    def add_quest(self, quest: Quest) -> bool:
        """Add a quest to the quest log."""
        if quest not in self.active_quests[quest.quest_type]:
            self.active_quests[quest.quest_type].append(quest)
            return True
        return False
    
    def complete_quest(self, quest: Quest) -> bool:
        """Mark a quest as completed and move it to completed_quests."""
        if quest in self.active_quests[quest.quest_type]:
            self.active_quests[quest.quest_type].remove(quest)
            self.completed_quests.append(quest)
            return True
        return False
    
    def get_quests_by_type(self, quest_type: QuestType) -> List[Quest]:
        """Get all active quests of a specific type."""
        return self.active_quests[quest_type]
    
    def get_all_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        all_quests = []
        for quests in self.active_quests.values():
            all_quests.extend(quests)
        return all_quests
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests."""
        return self.completed_quests
    
    def has_quest(self, quest: Quest) -> bool:
        """Check if a quest is in the active quests."""
        return quest in self.active_quests[quest.quest_type]
    
    def has_completed_quest(self, quest: Quest) -> bool:
        """Check if a quest has been completed."""
        return quest in self.completed_quests 