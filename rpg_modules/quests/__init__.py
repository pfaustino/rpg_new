"""
Quest system for the RPG game.
"""

from .base import Quest, QuestType, QuestDifficulty, QuestObjective, QuestReward, QuestStatus
from .objectives import KillObjective, CollectObjective, ExploreObjective, DeliverObjective
from .rewards import GoldReward, ExperienceReward, ItemReward, MultiReward
from .generator import QuestGenerator
from .log import QuestLog
from .loader import QuestLoader, add_quest_to_file, add_quest_chain_to_file
from .main_quest_handler import MainQuestHandler
from .manager import QuestManager
from .init_main_quests import initialize_main_quest_system, register_quest_event_handlers

__all__ = [
    'Quest',
    'QuestType',
    'QuestDifficulty',
    'QuestStatus',
    'QuestObjective',
    'QuestReward',
    'KillObjective',
    'CollectObjective',
    'ExploreObjective',
    'DeliverObjective',
    'GoldReward',
    'ExperienceReward',
    'ItemReward',
    'MultiReward',
    'QuestGenerator',
    'QuestLog',
    'QuestLoader',
    'QuestManager',
    'add_quest_to_file',
    'add_quest_chain_to_file',
    'MainQuestHandler',
    'initialize_main_quest_system',
    'register_quest_event_handlers'
] 