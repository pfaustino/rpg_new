# Main Quest System Integration Guide

This guide explains how to integrate the "Shadow of the Artifact" main quest line into the game.

## Step 1: Add Quest Initialization to Game Startup

Find the game's main initialization sequence (likely in `rpg_modules/game.py`) and add quest initialization:

```python
from rpg_modules.quests import initialize_main_quest_system

class Game:
    def __init__(self):
        # ... existing initialization code ...
        
        # Initialize the quest system
        self.quest_manager, self.main_quest_handler = initialize_main_quest_system(self)
        
        # ... more initialization code ...
```

## Step 2: Connect Quest Events to Game Events

Connect the quest system to your game's event system so that quest objectives can be updated:

```python
from rpg_modules.quests import register_quest_event_handlers

class Game:
    def initialize_systems(self):
        # ... other system initialization ...
        
        # Register quest event handlers
        register_quest_event_handlers(self.quest_manager, self.event_system)
```

## Step 3: Integrate with Dialog System

Update your dialog system to report dialog state changes to the quest system:

```python
class DialogSystem:
    def complete_dialog(self, dialog_id, node_id):
        # ... existing dialog completion code ...
        
        # Update quest state based on dialog
        self.game.main_quest_handler.update_quest_state_from_dialog(dialog_id, node_id)
        
    def handle_dialog_choice(self, dialog_id, flag):
        # ... existing dialog choice code ...
        
        # If the choice sets a story flag
        if flag:
            self.game.main_quest_handler.handle_flag_set(flag)
```

## Step 4: Start First Quest for New Players

When a new game is started, trigger the first quest in the main quest line:

```python
class Game:
    def new_game(self):
        # ... existing new game code ...
        
        # Start the initial quest for the main quest line
        self.main_quest_handler.start_initial_quest(self.player)
```

## Step 5: Save/Load Quest State

Add quest state to your game's save/load system:

```python
class SaveSystem:
    def save_game(self, filename):
        # ... existing save code ...
        
        # Save quest state
        save_data["quest_log"] = self.game.quest_manager.quest_log.save_state()
        save_data["main_quest"] = self.game.main_quest_handler.save_state()
        
    def load_game(self, filename):
        # ... existing load code ...
        
        # Load quest state
        if "quest_log" in save_data:
            self.game.quest_manager.quest_log.load_state(save_data["quest_log"])
        
        if "main_quest" in save_data:
            self.game.main_quest_handler.load_state(save_data["main_quest"])
```

## Step 6: Add Quest UI Elements

Update the UI to display quest information:

```python
class QuestUI:
    def update(self):
        # Get current main quest
        main_quest = self.game.main_quest_handler.get_current_main_quest()
        
        if main_quest:
            # Update the UI with quest information
            self.quest_title.text = main_quest.title
            self.quest_description.text = main_quest.description
            
            # Update objective list
            self.objectives_list.clear()
            for obj in main_quest.objectives:
                status = "✓" if obj.is_complete() else "○"
                self.objectives_list.add_item(f"{status} {obj.description}")
```

## Step 7: Test the Main Quest Line

Run the test script to verify that the quest system is working properly:

```bash
python test_main_quest.py
```

## Additional Notes

1. **NPC Placement**: Ensure that all NPCs referenced in the quest dialogs (Captain Thorne, Seren, Bram, Lysa) are placed in the game world.

2. **Location Setup**: Create all locations needed for the quest chain (town square, temple ruins, hidden chamber, ancient shrine, etc.).

3. **Item Definitions**: Define all items referenced in the quests (artifact fragment, sealed artifact, etc.) in your item system.

4. **Enemy Setup**: Create the "corrupted guardian" and "corrupted ally" enemy types referenced in the combat objectives.

## Troubleshooting

- **Missing Quests**: If quests don't appear, check that the JSON files were correctly copied to the `data/quests` directory.

- **Dialog Issues**: Verify that dialog IDs in your dialog system match those referenced in the quest JSON files.

- **Quest Not Advancing**: Make sure event handlers are properly registered and firing when game events occur. 