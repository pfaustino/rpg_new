"""
Base classes for the quest system.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from ..items import Item

class QuestStatus(Enum):
    """Possible states of a quest."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TURNED_IN = auto()

class QuestType(Enum):
    """Types of quests available in the game."""
    MAIN = auto()      # Main story quests
    SIDE = auto()      # Optional side quests
    DAILY = auto()     # Daily repeatable quests
    WORLD = auto()     # World events/quests
    HIDDEN = auto()    # Secret/hidden quests

class QuestDifficulty(Enum):
    """Difficulty levels for quests."""
    TRIVIAL = auto()    # Very easy, good for new players
    EASY = auto()       # Standard difficulty
    MEDIUM = auto()     # Challenging but doable
    HARD = auto()       # Difficult, requires preparation
    EPIC = auto()       # Very challenging, requires a group or high level

@dataclass
class QuestObjective(ABC):
    """Base class for quest objectives."""
    description: str
    required_progress: int
    current_progress: int = field(default=0, init=False)
    completed: bool = field(default=False, init=False)

    @abstractmethod
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if an event contributes to the objective's progress.
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            bool: True if progress was made, False otherwise
        """
        pass

    def update_progress(self, amount: int = 1) -> bool:
        """
        Update the objective's progress.
        
        Args:
            amount: Amount to increase progress by
            
        Returns:
            bool: True if objective was completed by this update
        """
        if self.completed:
            return False
            
        self.current_progress = min(self.current_progress + amount, self.required_progress)
        if self.current_progress >= self.required_progress:
            self.completed = True
            return True
        return False

@dataclass
class QuestReward(ABC):
    """Base class for quest rewards."""
    description: str

    @abstractmethod
    def grant(self, player) -> bool:
        """
        Grant the reward to the player.
        
        Args:
            player: The player to receive the reward
            
        Returns:
            bool: True if reward was granted successfully
        """
        pass

@dataclass
class Quest:
    """Represents a quest in the game."""
    id: str
    title: str
    description: str
    quest_type: QuestType
    level_requirement: int = 1
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # List of quest IDs that must be completed first
    status: QuestStatus = QuestStatus.NOT_STARTED
    difficulty: QuestDifficulty = QuestDifficulty.EASY  # Default to EASY difficulty
    
    # Optional quest properties
    giver_id: Optional[str] = None  # NPC or entity that gives the quest
    turn_in_id: Optional[str] = None  # NPC or entity to turn in the quest to
    time_limit: Optional[int] = None  # Time limit in seconds (if applicable)
    expiry_time: Optional[float] = None  # When the quest expires (for daily/timed quests)
    chain_id: Optional[str] = None  # ID of the quest chain this quest belongs to
    chain_position: Optional[int] = None  # Position in the quest chain (1-based)
    next_quest_id: Optional[str] = None  # ID of the next quest in the chain
    
    def is_available(self, player) -> bool:
        """Check if the quest is available to the player."""
        if self.status != QuestStatus.NOT_STARTED:
            return False
            
        if player.level < self.level_requirement:
            return False
            
        # Check prerequisites
        for quest_id in self.prerequisites:
            prereq_quest = player.quest_log.get_quest(quest_id)
            if not prereq_quest or prereq_quest.status != QuestStatus.TURNED_IN:
                return False
                
        return True
    
    def start(self) -> bool:
        """Start the quest if it's available."""
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.IN_PROGRESS
            return True
        return False
    
    def check_completion(self) -> bool:
        """Check if all objectives are completed."""
        if self.status != QuestStatus.IN_PROGRESS:
            return False
            
        if all(objective.completed for objective in self.objectives):
            self.status = QuestStatus.COMPLETED
            return True
        return False
    
    def turn_in(self, player) -> bool:
        """
        Turn in a completed quest and grant rewards.
        
        Args:
            player: The player turning in the quest
            
        Returns:
            bool: True if quest was successfully turned in
        """
        if self.status != QuestStatus.COMPLETED:
            return False
            
        # Grant all rewards
        all_rewards_granted = True
        for reward in self.rewards:
            if not reward.grant(player):
                all_rewards_granted = False
                
        if all_rewards_granted:
            self.status = QuestStatus.TURNED_IN
            return True
        return False
    
    def update_objectives(self, event_data: Dict[str, Any]) -> bool:
        """
        Update quest objectives based on an event.
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            bool: True if any objectives were updated
        """
        if self.status != QuestStatus.IN_PROGRESS:
            return False
            
        progress_made = False
        for objective in self.objectives:
            if not objective.completed and objective.check_progress(event_data):
                progress_made = True
                
        if progress_made:
            self.check_completion()
            
        return progress_made
        
    def get_difficulty_color(self) -> Tuple[int, int, int]:
        """Get the color associated with this quest's difficulty."""
        return {
            QuestDifficulty.TRIVIAL: (128, 128, 128),  # Gray
            QuestDifficulty.EASY: (255, 255, 255),     # White
            QuestDifficulty.MEDIUM: (0, 255, 0),       # Green
            QuestDifficulty.HARD: (0, 0, 255),         # Blue
            QuestDifficulty.EPIC: (255, 128, 0)        # Orange
        }[self.difficulty]
        
    def get_completion_percentage(self) -> float:
        """Get the overall completion percentage of the quest."""
        if not self.objectives:
            return 0.0
            
        total_progress = sum(obj.current_progress for obj in self.objectives)
        total_required = sum(obj.required_progress for obj in self.objectives)
        return (total_progress / total_required) * 100 if total_required > 0 else 0.0 