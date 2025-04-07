"""
Quest generator for procedurally generating quests.
"""

import random
from typing import List, Optional, Dict, Tuple
from .base import Quest, QuestType, QuestDifficulty
from .objectives import KillObjective, CollectObjective, ExploreObjective
from .rewards import GoldReward, ExperienceReward, ItemReward
from ..items import ItemGenerator

class QuestGenerator:
    """Generates procedural quests based on templates and parameters."""
    
    # Quest templates with placeholders
    QUEST_TEMPLATES = {
        QuestType.MAIN: [
            # Dragon Slayer Chain
            [
                {
                    "title": "Dragon Signs",
                    "description": "Reports of a {adjective} dragon have been coming in. Scout the {location} for signs of its presence.",
                    "objectives": [
                        {
                            "type": "explore",
                            "target": "{location}",
                            "unique": True
                        },
                        {
                            "type": "collect",
                            "target": "dragon scale",
                            "unique": True
                        }
                    ],
                    "rewards": ["gold", "experience"],
                    "difficulty": QuestDifficulty.EASY
                },
                {
                    "title": "The Dragon's Prey",
                    "description": "The {adjective} dragon has been hunting in the area. Clear out its minions to draw it out.",
                    "objectives": [
                        {
                            "type": "kill",
                            "target": "dragon cultist",
                            "unique": False
                        },
                        {
                            "type": "collect",
                            "target": "dragon totem",
                            "unique": True
                        }
                    ],
                    "rewards": ["gold", "experience", "item"],
                    "difficulty": QuestDifficulty.MEDIUM
                },
                {
                    "title": "The {adjective} Dragon",
                    "description": "The time has come to face the {adjective} dragon. Defeat it and claim its power.",
                    "objectives": [
                        {
                            "type": "kill",
                            "target": "{adjective} dragon",
                            "unique": True
                        },
                        {
                            "type": "collect",
                            "target": "dragon heart",
                            "unique": True
                        }
                    ],
                    "rewards": ["gold", "experience", "item"],
                    "difficulty": QuestDifficulty.EPIC
                }
            ]
        ],
        QuestType.SIDE: [
            {
                "title": "Hunting {creatures}",
                "description": "Local hunters need help controlling the {creatures} population and gathering resources.",
                "objectives": [
                    {
                        "type": "kill",
                        "target": "{creatures}",
                        "unique": False
                    },
                    {
                        "type": "collect",
                        "target": "{creatures} hide",
                        "unique": False
                    }
                ],
                "rewards": ["gold", "experience"],
                "difficulty": QuestDifficulty.EASY
            },
            {
                "title": "Gathering {resources}",
                "description": "The town needs {resources} for its supplies. Clear the area of threats first.",
                "objectives": [
                    {
                        "type": "kill",
                        "target": "hostile creatures",
                        "unique": False
                    },
                    {
                        "type": "collect",
                        "target": "{resources}",
                        "unique": False
                    }
                ],
                "rewards": ["gold"],
                "difficulty": QuestDifficulty.EASY
            },
            {
                "title": "Explore the {location}",
                "description": "Map out the dangerous {location} and document the threats within.",
                "objectives": [
                    {
                        "type": "explore",
                        "target": "{location}",
                        "unique": True
                    },
                    {
                        "type": "kill",
                        "target": "dangerous beasts",
                        "unique": False
                    }
                ],
                "rewards": ["experience"],
                "difficulty": QuestDifficulty.MEDIUM
            }
        ],
        QuestType.DAILY: [
            {
                "title": "Daily {activity}",
                "description": "Complete today's {activity} for rewards.",
                "objectives": [
                    {
                        "type": "kill",
                        "target": "{creatures}",
                        "unique": False
                    }
                ],
                "rewards": ["gold"],
                "difficulty": QuestDifficulty.TRIVIAL
            },
            {
                "title": "Resource Run",
                "description": "Gather daily resources from the {location}.",
                "objectives": [
                    {
                        "type": "collect",
                        "target": "{resources}",
                        "unique": False
                    }
                ],
                "rewards": ["gold", "item"],
                "difficulty": QuestDifficulty.TRIVIAL
            }
        ]
    }
    
    # Word lists for template filling
    WORDS = {
        "adjective": ["fearsome", "ancient", "cursed", "mysterious", "dark", "corrupted", "legendary"],
        "threat": ["dragon", "necromancer", "demon lord", "witch king", "giant", "kraken"],
        "artifact": ["crown", "sword", "orb", "scepter", "tome", "crystal"],
        "location": ["dungeon", "cave", "ruins", "temple", "fortress", "catacombs", "forest"],
        "creatures": ["wolves", "bandits", "goblins", "skeletons", "spiders", "slimes"],
        "resources": ["herbs", "ores", "crystals", "wood", "leather", "cloth"],
        "activity": ["monster hunt", "resource gathering", "exploration", "training"]
    }
    
    def __init__(self, item_generator: ItemGenerator):
        """Initialize the quest generator."""
        self.item_generator = item_generator
        self.quest_chains: Dict[str, List[Quest]] = {}
    
    def generate_quest_chain(self, chain_id: str, quest_type: QuestType) -> List[Quest]:
        """Generate a chain of related quests."""
        # Get chain template
        chain_template = random.choice([t for t in self.QUEST_TEMPLATES[quest_type] if isinstance(t, list)])
        
        # Store replaced words to maintain consistency across the chain
        replaced_words = {}
        quests = []
        
        # Generate each quest in the chain
        for i, template in enumerate(chain_template, 1):
            title = template["title"]
            description = template["description"]
            
            # Replace placeholders with random words
            for key, word_list in self.WORDS.items():
                placeholder = "{" + key + "}"
                if placeholder in title or placeholder in description:
                    if key in replaced_words:
                        word = replaced_words[key]
                    else:
                        word = random.choice(word_list)
                        replaced_words[key] = word
                    title = title.replace(placeholder, word)
                    description = description.replace(placeholder, word)
            
            # Generate objectives
            objectives = []
            for obj_template in template["objectives"]:
                target = obj_template["target"]
                for key, word in replaced_words.items():
                    target = target.replace("{" + key + "}", word)
                
                if obj_template["type"] == "kill":
                    target_count = 1 if obj_template.get("unique", False) else random.randint(3, 10)
                    objectives.append(KillObjective(
                        description=f"Defeat {target_count} {target}",
                        required_progress=target_count,
                        target_type=target
                    ))
                elif obj_template["type"] == "collect":
                    item_count = 1 if obj_template.get("unique", False) else random.randint(5, 15)
                    objectives.append(CollectObjective(
                        description=f"Collect {item_count} {target}",
                        required_progress=item_count,
                        item_type=target
                    ))
                elif obj_template["type"] == "explore":
                    area_count = 1 if obj_template.get("unique", False) else random.randint(3, 6)
                    objectives.append(ExploreObjective(
                        description=f"Explore {area_count} areas in the {target}",
                        required_progress=area_count,
                        location_id=target,
                        area_name=target
                    ))
            
            # Generate rewards
            rewards = []
            for reward_type in template["rewards"]:
                if reward_type == "gold":
                    gold_amount = random.randint(50, 200) * (
                        3 if quest_type == QuestType.MAIN
                        else 2 if quest_type == QuestType.SIDE
                        else 1
                    )
                    rewards.append(GoldReward(
                        description=f"Receive {gold_amount} gold",
                        amount=gold_amount
                    ))
                elif reward_type == "experience":
                    xp_amount = random.randint(100, 400) * (
                        3 if quest_type == QuestType.MAIN
                        else 2 if quest_type == QuestType.SIDE
                        else 1
                    )
                    rewards.append(ExperienceReward(
                        description=f"Gain {xp_amount} experience",
                        amount=xp_amount
                    ))
                elif reward_type == "item":
                    item = self.item_generator.generate_item()
                    rewards.append(ItemReward(
                        description=f"Receive {item.display_name}",
                        item=item
                    ))
            
            # Create the quest
            quest_id = f"quest_{quest_type.name.lower()}_{chain_id}_{i}"
            quest = Quest(
                id=quest_id,
                title=title,
                description=description,
                quest_type=quest_type,
                objectives=objectives,
                rewards=rewards,
                difficulty=template["difficulty"],
                chain_id=chain_id,
                chain_position=i
            )
            
            # Set prerequisites for all but the first quest
            if i > 1:
                quest.prerequisites = [quests[-1].id]
            
            quests.append(quest)
        
        # Link quests in the chain
        for i in range(len(quests) - 1):
            quests[i].next_quest_id = quests[i + 1].id
        
        # Store the chain
        self.quest_chains[chain_id] = quests
        return quests
    
    def generate_quest(self, quest_type: Optional[QuestType] = None) -> Quest:
        """Generate a new quest of the specified type."""
        if quest_type is None:
            quest_type = random.choice(list(QuestType))
            
        # For main quests, sometimes generate a chain instead of a single quest
        if quest_type == QuestType.MAIN and random.random() < 0.5:
            chain_id = f"chain_{random.randint(1000, 9999)}"
            return self.generate_quest_chain(chain_id, quest_type)[0]
        
        # Select a random template for the quest type
        template = random.choice([t for t in self.QUEST_TEMPLATES[quest_type] if not isinstance(t, list)])
        
        # Fill in the template placeholders
        title = template["title"]
        description = template["description"]
        
        # Store replaced words to maintain consistency
        replaced_words = {}
        
        # Replace placeholders with random words
        for key, word_list in self.WORDS.items():
            placeholder = "{" + key + "}"
            if placeholder in title or placeholder in description:
                if key in replaced_words:
                    word = replaced_words[key]
                else:
                    word = random.choice(word_list)
                    replaced_words[key] = word
                title = title.replace(placeholder, word)
                description = description.replace(placeholder, word)
        
        # Generate objectives
        objectives = []
        for obj_template in template["objectives"]:
            target = obj_template["target"]
            for key, word in replaced_words.items():
                target = target.replace("{" + key + "}", word)
            
            if obj_template["type"] == "kill":
                target_count = 1 if obj_template.get("unique", False) else random.randint(3, 10)
                objectives.append(KillObjective(
                    description=f"Defeat {target_count} {target}",
                    required_progress=target_count,
                    target_type=target
                ))
            elif obj_template["type"] == "collect":
                item_count = 1 if obj_template.get("unique", False) else random.randint(5, 15)
                objectives.append(CollectObjective(
                    description=f"Collect {item_count} {target}",
                    required_progress=item_count,
                    item_type=target
                ))
            elif obj_template["type"] == "explore":
                area_count = 1 if obj_template.get("unique", False) else random.randint(3, 6)
                objectives.append(ExploreObjective(
                    description=f"Explore {area_count} areas in the {target}",
                    required_progress=area_count,
                    location_id=target,
                    area_name=target
                ))
        
        # Generate rewards
        rewards = []
        for reward_type in template["rewards"]:
            if reward_type == "gold":
                gold_amount = random.randint(50, 200) * (
                    3 if quest_type == QuestType.MAIN
                    else 2 if quest_type == QuestType.SIDE
                    else 1
                )
                rewards.append(GoldReward(
                    description=f"Receive {gold_amount} gold",
                    amount=gold_amount
                ))
            elif reward_type == "experience":
                xp_amount = random.randint(100, 400) * (
                    3 if quest_type == QuestType.MAIN
                    else 2 if quest_type == QuestType.SIDE
                    else 1
                )
                rewards.append(ExperienceReward(
                    description=f"Gain {xp_amount} experience",
                    amount=xp_amount
                ))
            elif reward_type == "item":
                item = self.item_generator.generate_item()
                rewards.append(ItemReward(
                    description=f"Receive {item.display_name}",
                    item=item
                ))
        
        # Create and return the quest
        return Quest(
            id=f"quest_{quest_type.name.lower()}_{random.randint(1000, 9999)}",
            title=title,
            description=description,
            quest_type=quest_type,
            objectives=objectives,
            rewards=rewards,
            difficulty=template["difficulty"]
        ) 