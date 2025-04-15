"""
Quest loader module for loading quests from JSON files.
"""

import json
import os
from typing import Dict, List, Optional, Any, Union, Tuple
from .base import Quest, QuestStatus, QuestType, QuestDifficulty, QuestObjective, QuestReward
from .objectives import KillObjective, CollectObjective, ExploreObjective, DeliverObjective, DialogObjective
from .rewards import GoldReward, ExperienceReward, ItemReward, MultiReward
from ..items import Item, ItemGenerator

class QuestLoader:
    """Loads quest data from JSON files and creates quest objects."""
    
    def __init__(self, quest_data_path: str = "data/quests"):
        """Initialize the quest loader with the path to quest data files."""
        self.quest_data_path = quest_data_path
        self.loaded_quests: Dict[str, Quest] = {}
        self.quest_chains: Dict[str, List[str]] = {}
        self.item_generator = ItemGenerator()
    
    def load_all_quests(self) -> Dict[str, Quest]:
        """Load all quest data files in the quest data directory."""
        if not os.path.exists(self.quest_data_path):
            os.makedirs(self.quest_data_path)
            self._create_sample_quest_file()
            
        for filename in os.listdir(self.quest_data_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.quest_data_path, filename)
                self.load_quests_from_file(file_path)
                
        return self.loaded_quests
    
    def load_quests_from_file(self, file_path: str) -> List[Quest]:
        """Load quests from a specific JSON file."""
        if not os.path.exists(file_path):
            print(f"Quest file not found: {file_path}")
            return []
            
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
            loaded_quests = []
            
            # Load quests
            if "quests" in data:
                for quest_data in data["quests"]:
                    quest = self._create_quest_from_data(quest_data)
                    if quest:
                        self.loaded_quests[quest.id] = quest
                        loaded_quests.append(quest)
            
            # Load quest chains
            if "quest_chains" in data:
                for chain_id, chain_data in data["quest_chains"].items():
                    if "quests" in chain_data:
                        self.quest_chains[chain_id] = chain_data["quests"]
                        
                        # Set chain references on quests
                        for i, quest_id in enumerate(chain_data["quests"]):
                            if quest_id in self.loaded_quests:
                                quest = self.loaded_quests[quest_id]
                                quest.chain_id = chain_id
                                quest.chain_position = i + 1
                                
                                # Set next quest reference if not the last quest
                                if i < len(chain_data["quests"]) - 1:
                                    quest.next_quest_id = chain_data["quests"][i + 1]
            
            return loaded_quests
            
        except Exception as e:
            print(f"Error loading quests from {file_path}: {e}")
            return []
    
    def _create_quest_from_data(self, data: Dict[str, Any]) -> Optional[Quest]:
        """Create a Quest object from JSON data."""
        try:
            # Convert string enum values to their proper enum types
            quest_type = getattr(QuestType, data.get("quest_type", "SIDE"))
            difficulty = getattr(QuestDifficulty, data.get("difficulty", "EASY"))
            
            # Create objectives
            objectives = []
            for obj_data in data.get("objectives", []):
                objective = self._create_objective_from_data(obj_data)
                if objective:
                    objectives.append(objective)
            
            # Create rewards
            rewards = []
            for reward_data in data.get("rewards", []):
                reward = self._create_reward_from_data(reward_data)
                if reward:
                    rewards.append(reward)
            
            # Create the quest
            quest = Quest(
                id=data["id"],
                title=data["title"],
                description=data["description"],
                quest_type=quest_type,
                level_requirement=data.get("level_requirement", 1),
                objectives=objectives,
                rewards=rewards,
                prerequisites=data.get("prerequisites", []),
                status=QuestStatus.NOT_STARTED,
                difficulty=difficulty
            )
            
            # Set optional properties
            if "giver_id" in data:
                quest.giver_id = data["giver_id"]
                
            if "turn_in_id" in data:
                quest.turn_in_id = data["turn_in_id"]
                
            if "time_limit" in data:
                quest.time_limit = data["time_limit"]
                
            if "location" in data:
                loc = data["location"]
                quest.location_id = loc.get("id")
                
                if "coords" in loc and len(loc["coords"]) == 2:
                    quest.location_coords = (loc["coords"][0], loc["coords"][1])
                    
                if "radius" in loc:
                    quest.location_radius = loc["radius"]
            
            return quest
            
        except Exception as e:
            print(f"Error creating quest {data.get('id', 'unknown')}: {e}")
            return None
    
    def _create_objective_from_data(self, data: Dict[str, Any]) -> Optional[QuestObjective]:
        """Create a quest objective from JSON data."""
        try:
            obj_type = data.get("type", "").lower()
            description = data.get("description", "")
            required_progress = data.get("required_progress", 1)
            
            if obj_type == "kill":
                return KillObjective(
                    target_type=data.get("target_type", "unknown"),
                    description=description,
                    required_progress=required_progress
                )
                
            elif obj_type == "collect":
                return CollectObjective(
                    item_type=data.get("item_type", "unknown"),
                    description=description,
                    required_progress=required_progress
                )
                
            elif obj_type == "explore":
                return ExploreObjective(
                    location_id=data.get("location_id", "unknown"),
                    area_name=data.get("area_name", "unknown area"),
                    description=description,
                    required_progress=required_progress
                )
                
            elif obj_type == "deliver":
                return DeliverObjective(
                    item_id=data.get("item_id", "unknown"),
                    target_npc_id=data.get("target_npc_id", "unknown"),
                    description=description,
                    required_progress=required_progress
                )
                
            elif obj_type == "dialog":
                return DialogObjective(
                    dialog_id=data.get("dialog_id", "unknown"),
                    description=description,
                    required_progress=required_progress,
                    npc_id=data.get("npc_id")
                )
                
            return None
            
        except Exception as e:
            print(f"Error creating objective: {e}")
            return None
    
    def _create_reward_from_data(self, data: Dict[str, Any]) -> Optional[QuestReward]:
        """Create a quest reward from JSON data."""
        try:
            reward_type = data.get("type", "").lower()
            description = data.get("description", "")
            
            if reward_type == "gold":
                return GoldReward(
                    amount=data.get("amount", 10),
                    description=description
                )
                
            elif reward_type == "experience":
                return ExperienceReward(
                    amount=data.get("amount", 50),
                    description=description
                )
                
            elif reward_type == "item":
                # Create or load the item
                item = None
                if "item_id" in data:
                    # TODO: Load item from item database
                    item_name = data.get("item_name", "Mystery Item")
                    item = Item(data["item_id"], item_name)
                else:
                    # Generate a random item if no specific item is defined
                    item = self.item_generator.generate_random_item()
                    
                return ItemReward(
                    item=item,
                    description=description
                )
                
            elif reward_type == "multi":
                sub_rewards = []
                for sub_reward_data in data.get("rewards", []):
                    sub_reward = self._create_reward_from_data(sub_reward_data)
                    if sub_reward:
                        sub_rewards.append(sub_reward)
                        
                return MultiReward(
                    rewards=sub_rewards,
                    description=description
                )
                
            return None
            
        except Exception as e:
            print(f"Error creating reward: {e}")
            return None
    
    def save_quest_to_file(self, quest: Quest, file_path: str) -> bool:
        """Save a quest to a JSON file."""
        try:
            # Check if file exists
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    data = json.load(file)
            else:
                data = {"quests": []}
            
            # Convert quest to dict
            quest_data = self._quest_to_dict(quest)
            
            # Check if quest already exists in file
            for i, existing_quest in enumerate(data["quests"]):
                if existing_quest.get("id") == quest.id:
                    # Update existing quest
                    data["quests"][i] = quest_data
                    break
            else:
                # Add new quest
                data["quests"].append(quest_data)
            
            # Save to file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving quest {quest.id} to {file_path}: {e}")
            return False
    
    def _quest_to_dict(self, quest: Quest) -> Dict[str, Any]:
        """Convert a Quest object to a dictionary for JSON serialization."""
        quest_dict = {
            "id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "quest_type": quest.quest_type.name,
            "level_requirement": quest.level_requirement,
            "difficulty": quest.difficulty.name,
            "objectives": [],
            "rewards": [],
            "prerequisites": quest.prerequisites
        }
        
        # Add optional properties
        if quest.giver_id:
            quest_dict["giver_id"] = quest.giver_id
            
        if quest.turn_in_id:
            quest_dict["turn_in_id"] = quest.turn_in_id
            
        if quest.time_limit:
            quest_dict["time_limit"] = quest.time_limit
            
        if quest.chain_id:
            quest_dict["chain_id"] = quest.chain_id
            quest_dict["chain_position"] = quest.chain_position
            
        if quest.next_quest_id:
            quest_dict["next_quest_id"] = quest.next_quest_id
            
        if quest.location_id:
            quest_dict["location"] = {
                "id": quest.location_id,
                "name": quest.location_id.replace("_", " ").title(),
                "radius": quest.location_radius
            }
            
            if quest.location_coords:
                quest_dict["location"]["coords"] = list(quest.location_coords)
        
        # Add objectives
        for objective in quest.objectives:
            obj_dict = {
                "description": objective.description,
                "required_progress": objective.required_progress
            }
            
            if isinstance(objective, KillObjective):
                obj_dict["type"] = "kill"
                obj_dict["target_type"] = objective.target_type
                
            elif isinstance(objective, CollectObjective):
                obj_dict["type"] = "collect"
                obj_dict["item_type"] = objective.item_type
                
            elif isinstance(objective, ExploreObjective):
                obj_dict["type"] = "explore"
                obj_dict["location_id"] = objective.location_id
                obj_dict["area_name"] = objective.area_name
                
            elif isinstance(objective, DeliverObjective):
                obj_dict["type"] = "deliver"
                obj_dict["item_id"] = objective.item_id
                obj_dict["target_npc_id"] = objective.target_npc_id
                
            elif isinstance(objective, DialogObjective):
                obj_dict["type"] = "dialog"
                obj_dict["dialog_id"] = objective.dialog_id
                if objective.npc_id:
                    obj_dict["npc_id"] = objective.npc_id
            
            quest_dict["objectives"].append(obj_dict)
        
        # Add rewards
        for reward in quest.rewards:
            reward_dict = {
                "description": reward.description
            }
            
            if isinstance(reward, GoldReward):
                reward_dict["type"] = "gold"
                reward_dict["amount"] = reward.amount
                
            elif isinstance(reward, ExperienceReward):
                reward_dict["type"] = "experience"
                reward_dict["amount"] = reward.amount
                
            elif isinstance(reward, ItemReward):
                reward_dict["type"] = "item"
                if reward.item:
                    reward_dict["item_id"] = reward.item.id
                    reward_dict["item_name"] = reward.item.name
                    
            elif isinstance(reward, MultiReward):
                reward_dict["type"] = "multi"
                reward_dict["rewards"] = [
                    self._reward_to_dict(sub_reward) for sub_reward in reward.rewards
                ]
                
            quest_dict["rewards"].append(reward_dict)
        
        return quest_dict
    
    def _reward_to_dict(self, reward: QuestReward) -> Dict[str, Any]:
        """Convert a reward object to a dictionary."""
        reward_dict = {
            "description": reward.description
        }
        
        if isinstance(reward, GoldReward):
            reward_dict["type"] = "gold"
            reward_dict["amount"] = reward.amount
            
        elif isinstance(reward, ExperienceReward):
            reward_dict["type"] = "experience"
            reward_dict["amount"] = reward.amount
            
        elif isinstance(reward, ItemReward):
            reward_dict["type"] = "item"
            if reward.item:
                reward_dict["item_id"] = reward.item.id
                reward_dict["item_name"] = reward.item.name
                
        return reward_dict
    
    def _create_sample_quest_file(self):
        """Create a sample quest file if none exists."""
        sample_data = {
            "quests": [
                {
                    "id": "tutorial_shadows",
                    "title": "Shadows Awakening",
                    "description": "Investigate the strange shadows that have been appearing in the village.",
                    "quest_type": "MAIN",
                    "level_requirement": 1,
                    "difficulty": "EASY",
                    "objectives": [
                        {
                            "type": "explore",
                            "description": "Investigate the edge of the village",
                            "required_progress": 1,
                            "location_id": "village_edge",
                            "area_name": "Village Edge"
                        },
                        {
                            "type": "kill",
                            "description": "Defeat the shadow creatures",
                            "required_progress": 3,
                            "target_type": "shadow_creature"
                        }
                    ],
                    "rewards": [
                        {
                            "type": "experience",
                            "description": "Gain shadowbinding experience",
                            "amount": 100
                        },
                        {
                            "type": "gold",
                            "description": "Village elder's gratitude",
                            "amount": 50
                        }
                    ],
                    "giver_id": "village_elder",
                    "turn_in_id": "village_elder",
                    "location": {
                        "id": "village_edge",
                        "name": "Village Edge",
                        "description": "The border between the village and the dark forest",
                        "coords": [100, 100],
                        "radius": 5
                    },
                    "chain_id": "tutorial_chain",
                    "chain_position": 1
                }
            ],
            "quest_chains": {
                "tutorial_chain": {
                    "name": "Discovering Your Powers",
                    "description": "The beginning of your journey to understand your shadowbinding powers.",
                    "quests": ["tutorial_shadows"]
                }
            }
        }
        
        # Create the directory if it doesn't exist
        os.makedirs(self.quest_data_path, exist_ok=True)
        
        # Save the sample file
        sample_path = os.path.join(self.quest_data_path, "sample_quests.json")
        with open(sample_path, 'w') as file:
            json.dump(sample_data, file, indent=2)
            
        print(f"Created sample quest file at {sample_path}")

    def _reload_quests(self):
        """Reload all quests from data files."""
        self.all_quests = self.load_all_quests()
        
    def get_quest_chain(self, chain_id: str) -> List[str]:
        """Get a quest chain by ID."""
        # Find all quest chain files
        chain_files = []
        for filename in os.listdir(self.quest_data_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.quest_data_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if "quest_chains" in data and chain_id in data["quest_chains"]:
                            return data["quest_chains"][chain_id].get("quests", [])
                except Exception as e:
                    print(f"Error reading quest chain file {file_path}: {e}")
        
        return []
    
    def get_all_quest_chains(self) -> Dict[str, Any]:
        """Get all quest chains."""
        chains = {}
        # Find all quest chain files
        for filename in os.listdir(self.quest_data_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.quest_data_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if "quest_chains" in data:
                            chains.update(data["quest_chains"])
                except Exception as e:
                    print(f"Error reading quest chain file {file_path}: {e}")
        
        return chains

# Function to add a new quest to a JSON file
def add_quest_to_file(quest_data: Dict[str, Any], file_path: str) -> bool:
    """Add a new quest to a JSON file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {"quests": []}
        
        # Add or update quest
        for i, existing_quest in enumerate(data["quests"]):
            if existing_quest.get("id") == quest_data["id"]:
                # Update existing quest
                data["quests"][i] = quest_data
                break
        else:
            # Add new quest
            data["quests"].append(quest_data)
        
        # Save to file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Error adding quest to {file_path}: {e}")
        return False

# Function to add a quest chain to a JSON file
def add_quest_chain_to_file(chain_id: str, chain_data: Dict[str, Any], file_path: str) -> bool:
    """Add a new quest chain to a JSON file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
        else:
            data = {"quests": [], "quest_chains": {}}
        
        # Make sure quest_chains exists
        if "quest_chains" not in data:
            data["quest_chains"] = {}
            
        # Add or update chain
        data["quest_chains"][chain_id] = chain_data
        
        # Save to file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
            
        return True
        
    except Exception as e:
        print(f"Error adding quest chain to {file_path}: {e}")
        return False 