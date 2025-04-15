# Main Quest System

This directory contains JSON files that define the main quest line "Shadow of the Artifact" for the game. These files were created based on the documentation in `mainquestline.MD`.

## Files Overview

- **main_quests.json** - Contains the detailed definitions of all 6 main quests with their objectives, rewards, and prerequisites
- **main_quest_chain.json** - Defines the overall quest chain structure with completion rewards
- **dialogs/main_quest_dialogs.json** - Contains dialog scripts for key NPC conversations

## Integration with the Game

To integrate these quests with the game, use the `initialize_main_quest_system()` function from `rpg_modules.quests`:

```python
from rpg_modules.quests import initialize_main_quest_system

# Initialize the quest system
quest_manager, main_quest_handler = initialize_main_quest_system(game_state)

# To start the first quest in the main quest line:
main_quest_handler.start_initial_quest(player)
```

## Story Flags

The main quest line uses several story flags to track player choices:

- `trusted_suspect` - Records which suspect the player chooses to trust (values: "seren", "bram", "lysa")
- `bram_fate` - Records the player's decision about Bram's fate (values: "mercy", "justice")

## Handling Dialog and Flags

When a player interacts with NPCs, dialog choices may set story flags that affect quest progression:

```python
# Handle a flag being set during dialog
main_quest_handler.handle_flag_set("trusted_suspect=seren")

# Update quest state when a dialog completes
main_quest_handler.update_quest_state_from_dialog("bram_confrontation", "mercy_choice")
```

## Side Quests

The main quest line unlocks different side quests based on player choices:

- Choosing "mercy" for Bram unlocks the "Redemption's Price" side quest
- Choosing "justice" for Bram unlocks the "Shadows Unleashed" side quest

## Testing

A test script `test_main_quest.py` is provided to demonstrate the main quest system functionality:

```bash
python test_main_quest.py
```

## Quest Structure

Each quest in the main quest line follows this progression:

1. **Mysterious Arrival** - Investigate strange energy in the town square
2. **First Investigation** - Explore the temple ruins and find the artifact fragment
3. **Suspects Trail** - Question three suspects about the artifact
4. **Truth Revealed** - Follow a lead to uncover the artifact's connection to an ancient order
5. **Confrontation** - Confront Bram at the ancient shrine
6. **Final Choice** - Decide Bram's fate and deal with the artifact 