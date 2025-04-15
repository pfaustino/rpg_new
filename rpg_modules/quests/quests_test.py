#!/usr/bin/env python3
"""
Test module for the quest system.
This file tests various quest functionality including dialog-based quests.
"""

import os
import sys
import unittest
import json
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rpg_modules.quests import (
    Quest, QuestType, QuestStatus, QuestDifficulty,
    KillObjective, CollectObjective,
    GoldReward, ExperienceReward, ItemReward,
    QuestManager, QuestLog, QuestLoader
)
from rpg_modules.quests.objectives import DialogObjective

# Add is_complete method to QuestObjective classes for compatibility
def patch_objective_classes():
    """Patch objective classes with is_complete method if it doesn't exist."""
    from rpg_modules.quests.base import QuestObjective
    
    # Add is_complete method if it doesn't exist
    if not hasattr(QuestObjective, 'is_complete'):
        QuestObjective.is_complete = lambda self: self.completed

# Apply patches
patch_objective_classes()

# Mock Item class for testing
class MockItem:
    """Mock Item class for testing item rewards."""
    def __init__(self, item_id, name):
        self.id = item_id
        self.name = name
        self.display_name = name
        self.quality_color = (255, 255, 255)

# Mock Inventory class
class MockInventory:
    """Mock inventory for testing."""
    def __init__(self):
        self.items = []
        
    def add_item(self, item, quantity=1):
        """Add an item to the inventory."""
        self.items.append({"id": item.id, "name": item.name, "quantity": quantity})
        return True
        
    def remove_item(self, item_id, quantity=1):
        """Remove an item from the inventory."""
        for item in self.items:
            if item["id"] == item_id:
                item["quantity"] -= quantity
                if item["quantity"] <= 0:
                    self.items.remove(item)
                return True
        return False
        
class MockPlayer:
    """Mock player class for testing quests."""
    def __init__(self, level=1):
        self.level = level
        self.inventory = MockInventory()
        self.gold = 0
        self.experience = 0
        self.quest_log = QuestLog()
        
    def add_gold(self, amount):
        """Add gold to the player."""
        self.gold += amount
        
    def add_experience(self, amount):
        """Add experience to the player."""
        self.experience += amount


class TestQuestSystem(unittest.TestCase):
    """Test class for the quest system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test data directory if it doesn't exist
        self.test_data_dir = "test_data/quests"
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.test_data_dir, "dialogs"), exist_ok=True)
        
        # Create a test player
        self.player = MockPlayer(level=5)
        
        # Create a quest manager with the test data directory
        self.quest_manager = QuestManager(quest_data_path=self.test_data_dir)
        
        # Load dialog file for testing
        self.ensure_dialog_file_exists()
    
    def ensure_dialog_file_exists(self):
        """Ensure that dialog files exist for testing."""
        # Copy the Elder Malik dialog for testing
        dialog_path = os.path.join(self.test_data_dir, "dialogs", "elder_malik_dialogs.json")
        
        if not os.path.exists(dialog_path):
            # Check if there's a real dialog file to copy
            real_dialog_path = "data/quests/dialogs/elder_malik_dialogs.json"
            if os.path.exists(real_dialog_path):
                with open(real_dialog_path, 'r') as f:
                    dialog_data = json.load(f)
                
                with open(dialog_path, 'w') as f:
                    json.dump(dialog_data, f, indent=2)
            else:
                # Create a minimal test dialog
                test_dialog = {
                    "elder_malik_intro": {
                        "character": "Elder Malik",
                        "text": "Ah, young one. You seek knowledge and purpose.",
                        "choices": [
                            {
                                "text": "I was told you might have a task for me.",
                                "next": "elder_malik_quest_offer"
                            }
                        ]
                    },
                    "elder_malik_quest_offer": {
                        "character": "Elder Malik",
                        "text": "Our village needs your help.",
                        "choices": [
                            {
                                "text": "I'll help you.",
                                "next": "elder_malik_quest_acceptance"
                            }
                        ]
                    },
                    "elder_malik_quest_acceptance": {
                        "character": "Elder Malik",
                        "text": "Thank you, brave one.",
                        "choices": [
                            {
                                "text": "I'll get started right away.",
                                "next": "exit"
                            }
                        ]
                    }
                }
                
                with open(dialog_path, 'w') as f:
                    json.dump(test_dialog, f, indent=2)
    
    def test_create_quest(self):
        """Test creating a basic quest."""
        # Create a quest
        quest = Quest(
            id="test_quest_1",
            title="Test Quest",
            description="A test quest",
            quest_type=QuestType.SIDE,
            level_requirement=1
        )
        
        # Check quest properties
        self.assertEqual(quest.id, "test_quest_1")
        self.assertEqual(quest.title, "Test Quest")
        self.assertEqual(quest.description, "A test quest")
        self.assertEqual(quest.quest_type, QuestType.SIDE)
        self.assertEqual(quest.level_requirement, 1)
        self.assertEqual(quest.status, QuestStatus.NOT_STARTED)
    
    def test_add_objectives_to_quest(self):
        """Test adding objectives to a quest."""
        # Create a quest
        quest = Quest(
            id="test_quest_2",
            title="Collect and Kill Quest",
            description="Collect herbs and kill monsters",
            quest_type=QuestType.SIDE,
            level_requirement=1
        )
        
        # Add objectives
        collect_objective = CollectObjective(
            item_type="herb",
            description="Collect 5 herbs",
            required_progress=5
        )
        kill_objective = KillObjective(
            target_type="goblin",
            description="Kill 3 goblins",
            required_progress=3
        )
        
        quest.objectives = [collect_objective, kill_objective]
        
        # Manually set quest reference since __post_init__ may not be called on assignment
        for objective in quest.objectives:
            objective.quest = quest
        
        # Check objectives
        self.assertEqual(len(quest.objectives), 2)
        self.assertEqual(quest.objectives[0].description, "Collect 5 herbs")
        self.assertEqual(quest.objectives[1].description, "Kill 3 goblins")
        
        # Check objective properties
        self.assertEqual(quest.objectives[0].required_progress, 5)
        self.assertEqual(quest.objectives[1].required_progress, 3)
        
        # Check quest reference
        self.assertEqual(quest.objectives[0].quest, quest)
        self.assertEqual(quest.objectives[1].quest, quest)
    
    def test_quest_progress(self):
        """Test quest progress through events."""
        # Create a quest
        quest = Quest(
            id="test_quest_3",
            title="Collection Quest",
            description="Collect herbs",
            quest_type=QuestType.SIDE,
            level_requirement=1
        )
        
        # Add objective
        collect_objective = CollectObjective(
            item_type="herb",
            description="Collect 3 herbs",
            required_progress=3
        )
        
        quest.objectives = [collect_objective]
        collect_objective.quest = quest
        
        # Start quest
        self.assertTrue(quest.start())
        self.assertEqual(quest.status, QuestStatus.IN_PROGRESS)
        
        # Create event data for collecting an herb
        event_data = {
            "type": "collect",
            "item_type": "herb",
            "amount": 2
        }
        
        # Process event - don't assert on return value as it may be implementation-specific
        quest.update_objectives(event_data)
        
        # Check progress
        self.assertEqual(collect_objective.current_progress, 2)
        self.assertEqual(quest.status, QuestStatus.IN_PROGRESS)
        
        # Process another event to complete the objective
        event_data["amount"] = 1
        quest.update_objectives(event_data)
        
        # Check quest completion
        self.assertEqual(collect_objective.current_progress, 3)
        self.assertTrue(collect_objective.completed)
        self.assertEqual(quest.status, QuestStatus.COMPLETED)
    
    def test_dialog_objective_quest(self):
        """Test a quest with a dialog objective."""
        # Create a quest with a dialog objective
        quest = Quest(
            id="test_quest_4",
            title="Talk to Elder Malik",
            description="Speak with Elder Malik about the village's needs",
            quest_type=QuestType.MAIN,
            level_requirement=1
        )
        
        # Add a dialog objective
        dialog_objective = DialogObjective(
            dialog_id="elder_malik_quest_acceptance",
            description="Complete conversation with Elder Malik",
            required_progress=1,
            npc_id="elder_malik"
        )
        
        quest.objectives = [dialog_objective]
        dialog_objective.quest = quest
        quest.start()
        
        # Create event data for dialog completion
        event_data = {
            "type": "dialog",
            "dialog_id": "elder_malik_quest_acceptance",
            "dialog_state": "conclusion",
            "npc_id": "elder_malik"
        }
        
        # Process event - don't assert on return value
        quest.update_objectives(event_data)
        
        # Check quest completion
        self.assertTrue(dialog_objective.completed)
        self.assertEqual(quest.status, QuestStatus.COMPLETED)
    
    def test_quest_rewards(self):
        """Test quest rewards."""
        # Create a quest with rewards
        quest = Quest(
            id="test_quest_5",
            title="Rewarding Quest",
            description="A quest with rewards",
            quest_type=QuestType.SIDE,
            level_requirement=1
        )
        
        # Add a simple objective
        collect_objective = CollectObjective(
            item_type="gem",
            description="Collect a gem",
            required_progress=1
        )
        
        # Add rewards using the correct parameters
        gold_reward = GoldReward(amount=100)
        exp_reward = ExperienceReward(amount=500)
        
        # Create a mock item for the ItemReward
        mock_item = MockItem("magic_sword", "Magic Sword")
        item_reward = ItemReward(item=mock_item)
        
        quest.objectives = [collect_objective]
        collect_objective.quest = quest
        quest.rewards = [gold_reward, exp_reward, item_reward]
        
        # Start and complete the quest
        quest.start()
        event_data = {
            "type": "collect",
            "item_type": "gem",
            "amount": 1
        }
        quest.update_objectives(event_data)
        
        # Turn in quest to get rewards
        self.assertTrue(quest.turn_in(self.player))
        
        # Check player received rewards
        self.assertEqual(self.player.gold, 100)
        self.assertEqual(self.player.experience, 500)
        
        # Check inventory received the item
        self.assertEqual(len(self.player.inventory.items), 1)
        self.assertEqual(self.player.inventory.items[0]["id"], "magic_sword")
        self.assertEqual(self.player.inventory.items[0]["name"], "Magic Sword")
    
    def test_quest_manager_add_and_start_quest(self):
        """Test adding and starting a quest via QuestManager."""
        # Create quest data
        quest_data = {
            "id": "test_quest_6",
            "title": "Manager Test Quest",
            "description": "Testing the quest manager",
            "type": "SIDE",
            "level_requirement": 1,
            "objectives": [
                {
                    "type": "collect",
                    "item_type": "mushroom",
                    "description": "Collect mushrooms",
                    "required_progress": 3
                }
            ],
            "rewards": [
                {
                    "type": "gold",
                    "amount": 50
                }
            ]
        }
        
        # Add quest to manager
        quest = self.quest_manager.add_quest(quest_data, save_to_file=False)
        self.assertIsNotNone(quest)
        
        # Start quest
        self.assertTrue(self.quest_manager.start_quest("test_quest_6", self.player))
        
        # Check quest is in active quests
        self.assertIn("test_quest_6", self.quest_manager.active_quests)
        self.assertEqual(self.quest_manager.active_quests["test_quest_6"].status, QuestStatus.IN_PROGRESS)
    
    def test_quest_manager_complete_quest(self):
        """Test completing a quest via QuestManager."""
        # Create quest data
        quest_data = {
            "id": "test_quest_7",
            "title": "Complete Me Quest",
            "description": "A quest to be completed",
            "type": "SIDE",
            "level_requirement": 1,
            "objectives": [
                {
                    "type": "dialog",
                    "dialog_id": "elder_malik_quest_acceptance",
                    "description": "Talk to Elder Malik",
                    "required_progress": 1,
                    "npc_id": "elder_malik"
                }
            ],
            "rewards": [
                {
                    "type": "experience",
                    "amount": 100
                }
            ]
        }
        
        # Add and start quest
        quest = self.quest_manager.add_quest(quest_data, save_to_file=False)
        self.quest_manager.start_quest("test_quest_7", self.player)
        
        # Process dialog event
        event_data = {
            "type": "dialog",
            "dialog_id": "elder_malik_quest_acceptance",
            "dialog_state": "conclusion",
            "npc_id": "elder_malik"
        }
        
        # Update quest with event
        updated_quests = self.quest_manager.process_event(event_data, self.player)
        self.assertIn("test_quest_7", updated_quests)
        
        # Complete and turn in quest
        self.assertTrue(self.quest_manager.complete_quest("test_quest_7", self.player))
        self.assertTrue(self.quest_manager.turn_in_quest("test_quest_7", self.player))
        
        # Check quest moved to completed quests
        self.assertIn("test_quest_7", self.quest_manager.completed_quests)
        self.assertEqual(self.player.experience, 100)
    
    def test_load_and_validate_dialog_file(self):
        """Test loading and validating a dialog file."""
        dialog_path = os.path.join(self.test_data_dir, "dialogs", "elder_malik_dialogs.json")
        
        # Check file exists
        self.assertTrue(os.path.exists(dialog_path))
        
        # Load dialog data
        with open(dialog_path, 'r') as f:
            dialog_data = json.load(f)
        
        # Check for key dialog nodes
        self.assertIn("elder_malik_intro", dialog_data)
        self.assertIn("elder_malik_quest_offer", dialog_data)
        self.assertIn("elder_malik_quest_acceptance", dialog_data)
        
        # Check dialog structure
        intro_node = dialog_data["elder_malik_intro"]
        self.assertIn("character", intro_node)
        self.assertIn("text", intro_node)
        self.assertIn("choices", intro_node)
        self.assertTrue(isinstance(intro_node["choices"], list))
        
        # Check there's at least one choice
        self.assertGreaterEqual(len(intro_node["choices"]), 1)
        
        # Check choice structure
        choice = intro_node["choices"][0]
        self.assertIn("text", choice)
        self.assertIn("next", choice)
        
        # Validate dialog path exists
        current_node = "elder_malik_intro"
        visited_nodes = set()
        
        # Follow a path through the dialog
        while current_node != "exit" and current_node not in visited_nodes:
            visited_nodes.add(current_node)
            
            if current_node not in dialog_data:
                break
                
            node = dialog_data[current_node]
            if not node["choices"]:
                break
                
            # Follow first choice
            current_node = node["choices"][0]["next"]
        
        # Check we had a valid path
        self.assertGreaterEqual(len(visited_nodes), 3)

    def test_elder_malik_quest(self):
        """Test the Elder Malik quest specifically."""
        # Load the Elder Malik dialog file
        dialog_path = os.path.join(self.test_data_dir, "dialogs", "elder_malik_dialogs.json")
        with open(dialog_path, 'r') as f:
            dialog_data = json.load(f)
        
        # Create an Elder Malik quest
        quest_data = {
            "id": "elder_malik_moonlight",
            "title": "Ember of Serenity",
            "description": "Help Elder Malik restore the Ember of Serenity by collecting Moonlight Flowers.",
            "type": "SIDE",
            "level_requirement": 3,
            "objectives": [
                {
                    "type": "dialog",
                    "dialog_id": "elder_malik_quest_acceptance",
                    "description": "Accept Elder Malik's quest",
                    "required_progress": 1,
                    "npc_id": "elder_malik"
                },
                {
                    "type": "collect",
                    "item_type": "moonlight_flower",
                    "description": "Collect Moonlight Flowers",
                    "required_progress": 3
                },
                {
                    "type": "dialog",
                    "dialog_id": "elder_malik_restoration_ceremony",
                    "description": "Complete the restoration ceremony",
                    "required_progress": 1,
                    "npc_id": "elder_malik"
                }
            ],
            "rewards": [
                {
                    "type": "gold",
                    "amount": 150
                },
                {
                    "type": "experience",
                    "amount": 300
                }
            ],
            "giver_id": "elder_malik",
            "turn_in_id": "elder_malik"
        }
        
        # Add and start the quest
        quest = self.quest_manager.add_quest(quest_data, save_to_file=False)
        self.assertIsNotNone(quest)
        self.assertTrue(self.quest_manager.start_quest("elder_malik_moonlight", self.player))
        
        # Check that the quest was added and started
        self.assertIn("elder_malik_moonlight", self.quest_manager.active_quests)
        active_quest = self.quest_manager.active_quests["elder_malik_moonlight"]
        self.assertEqual(active_quest.status, QuestStatus.IN_PROGRESS)
        
        # Verify the quest has three objectives
        self.assertEqual(len(active_quest.objectives), 3)
        
        # First objective: Complete the dialog to accept the quest
        dialog_event = {
            "type": "dialog",
            "dialog_id": "elder_malik_quest_acceptance",
            "dialog_state": "conclusion",
            "npc_id": "elder_malik"
        }
        updated_quests = self.quest_manager.process_event(dialog_event, self.player)
        self.assertIn("elder_malik_moonlight", updated_quests)
        
        # Check that first objective is completed
        self.assertTrue(active_quest.objectives[0].completed)
        
        # Second objective: Collect Moonlight Flowers
        collect_event = {
            "type": "collect",
            "item_type": "moonlight_flower",
            "amount": 3
        }
        updated_quests = self.quest_manager.process_event(collect_event, self.player)
        self.assertIn("elder_malik_moonlight", updated_quests)
        
        # Check that second objective is completed
        self.assertTrue(active_quest.objectives[1].completed)
        
        # Third objective: Complete the restoration ceremony dialog
        ceremony_event = {
            "type": "dialog",
            "dialog_id": "elder_malik_restoration_ceremony",
            "dialog_state": "conclusion",
            "npc_id": "elder_malik"
        }
        updated_quests = self.quest_manager.process_event(ceremony_event, self.player)
        self.assertIn("elder_malik_moonlight", updated_quests)
        
        # Check that all objectives are completed and quest is completed
        self.assertTrue(all(obj.completed for obj in active_quest.objectives))
        self.assertEqual(active_quest.status, QuestStatus.COMPLETED)
        
        # Turn in the quest
        self.assertTrue(self.quest_manager.turn_in_quest("elder_malik_moonlight", self.player))
        
        # Verify rewards were given
        self.assertEqual(self.player.gold, 150)
        self.assertEqual(self.player.experience, 300)
        
        # Verify quest moved to completed quests
        self.assertIn("elder_malik_moonlight", self.quest_manager.completed_quests)
        self.assertEqual(self.quest_manager.completed_quests["elder_malik_moonlight"].status, QuestStatus.TURNED_IN)


if __name__ == "__main__":
    unittest.main() 