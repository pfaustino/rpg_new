"""
Main quest initialization script.

This script initializes the main quest line from JSON files.
"""

import os
import shutil
from .manager import QuestManager
from .main_quest_handler import MainQuestHandler

def initialize_main_quest_system(game_state=None):
    """
    Initialize the main quest system by setting up the quest manager,
    main quest handler, and loading quests from JSON files.
    """
    print("Initializing main quest system...")
    
    # Create the quest manager
    quest_manager = QuestManager("data/quests")
    
    # Create main quest handler
    main_quest_handler = MainQuestHandler(quest_manager, game_state)
    
    # Initialize quest manager
    quest_manager.initialize()
    
    # Check if our files need to be copied to the data directory
    ensure_quest_files_exist()
    
    # Initialize main quests
    main_quest_handler.initialize_main_quests()
    
    print("Main quest system initialized")
    
    return quest_manager, main_quest_handler

def ensure_quest_files_exist():
    """
    Ensure that the required quest JSON files exist in the data directory.
    If they don't exist, copy them from our source files.
    """
    data_path = "data/quests"
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(os.path.join(data_path, "dialogs"), exist_ok=True)
    
    # List of files to check/copy
    files = [
        ("main_quests.json", os.path.join(data_path, "main_quests.json")),
        ("main_quest_chain.json", os.path.join(data_path, "main_quest_chain.json")),
        ("dialogs/main_quest_dialogs.json", os.path.join(data_path, "dialogs", "main_quest_dialogs.json"))
    ]
    
    for source_file, target_path in files:
        if not os.path.exists(target_path):
            try:
                # If the source file exists in data/quests, copy it to the target path
                if os.path.exists(os.path.join(data_path, source_file)):
                    shutil.copy2(os.path.join(data_path, source_file), target_path)
                    print(f"Copied {source_file} to {target_path}")
            except Exception as e:
                print(f"Error copying {source_file}: {e}")

def register_quest_event_handlers(quest_manager, event_system):
    """
    Register quest-related event handlers with the event system.
    """
    if event_system:
        # Register quest manager as a listener for relevant events
        for event_type in ["dialog_complete", "monster_killed", "item_collected", "location_visited"]:
            event_system.register_handler(event_type, quest_manager.process_event)
        
        print("Quest event handlers registered") 