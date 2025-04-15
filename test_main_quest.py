"""
Test script for the main quest system.

This script initializes the main quest system and demonstrates how to interact with it.
"""

import os
import sys
from rpg_modules.quests import initialize_main_quest_system

def main():
    """Main function to test the quest system."""
    print("===== Testing Main Quest System =====")
    
    # Ensure our data directories exist
    os.makedirs("data/quests/dialogs", exist_ok=True)
    
    # Copy our quest files to the data directory
    # (In a real game, these would be loaded from the game's data directory)
    copy_quest_files()
    
    # Initialize the quest system
    quest_manager, main_quest_handler = initialize_main_quest_system()
    
    # Print available quests
    print("\nAvailable quests:")
    for quest_id, quest in quest_manager.get_available_quests().items():
        print(f"- {quest_id}: {quest.title}")
    
    # Print quest chains
    print("\nQuest chains:")
    for chain_id, quests in quest_manager.get_all_quest_chains().items():
        print(f"- {chain_id}: {', '.join(quests)}")
    
    # Start the first quest
    print("\nStarting first quest...")
    first_quest_id = "mq_01_mysterious_arrival"
    if quest_manager.start_quest(first_quest_id):
        print(f"Started quest: {first_quest_id}")
        
        # Get the quest details
        quest = quest_manager.get_quest(first_quest_id)
        if quest:
            print(f"\nQuest details for {quest.title}:")
            print(f"- Description: {quest.description}")
            print(f"- Status: {quest.status.name}")
            print("\nObjectives:")
            for obj in quest.objectives:
                print(f"- {obj.description} (Completed: {obj.is_complete()})")
    else:
        print(f"Failed to start quest: {first_quest_id}")
    
    print("\n===== Main Quest System Test Complete =====")

def copy_quest_files():
    """Copy quest files from their created location to the data directory."""
    source_files = [
        ("data/quests/main_quests.json", "data/quests/main_quests.json"),
        ("data/quests/main_quest_chain.json", "data/quests/main_quest_chain.json"),
        ("data/quests/dialogs/main_quest_dialogs.json", "data/quests/dialogs/main_quest_dialogs.json")
    ]
    
    for source, dest in source_files:
        # Check if source exists
        if os.path.exists(source):
            try:
                # Copy the file
                with open(source, 'r') as src_file:
                    content = src_file.read()
                    
                with open(dest, 'w') as dst_file:
                    dst_file.write(content)
                    
                print(f"Copied {source} to {dest}")
            except Exception as e:
                print(f"Error copying {source} to {dest}: {e}")
        else:
            print(f"Source file not found: {source}")

if __name__ == "__main__":
    main() 