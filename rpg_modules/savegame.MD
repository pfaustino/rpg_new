# Save Game System Documentation

## Overview
The save game system allows players to save their progress in the RPG and resume gameplay later. The system stores player data, inventory, equipment, and map information in a JSON file. This document outlines the implementation details, file structure, and usage of the save game system.

## Implementation Details

### File Structure
- **Save Directory**: `save/`
- **Save File**: `savegame.json`
- **Format**: JSON

### Data Structure
The save file contains the following key data:

```json
{
  "player": {
    "x": [player_x_position],
    "y": [player_y_position],
    "health": [current_health],
    "max_health": [maximum_health],
    "mana": [current_mana],
    "max_mana": [maximum_mana],
    "stamina": [current_stamina],
    "max_stamina": [maximum_stamina],
    "attack_type": [current_attack_type],
    "xp": [experience_points],
    "level": [player_level],
    "inventory": [array_of_item_data],
    "equipment": {
      [slot_name]: [item_data],
      ...
    }
  },
  "map": {
    "current_map": [map_name],
    "player_visited": [array_of_visited_locations]
  }
}
```

### Item Data Structure
Items are stored with their specific attributes:

#### Weapons
```json
{
  "type": "Weapon",
  "weapon_type": "Sword",
  "attack_power": 10,
  "quality": "Legendary",
  "material": "Steel",
  "prefix": "Soulbound"
}
```

#### Armor
```json
{
  "type": "Armor",
  "armor_type": "Chest",
  "defense": 15,
  "quality": "Masterwork",
  "material": "Iron",
  "prefix": "Reinforced"
}
```

#### Consumables
```json
{
  "type": "Consumable",
  "consumable_type": "health",
  "effect_value": 50,
  "quality": "Standard"
}
```

## Core Functions

### Saving Game State
The `save_game()` function:
1. Collects player position, stats, inventory, and equipment data
2. Creates the save directory if it doesn't exist
3. Writes the data to `save/savegame.json` in JSON format
4. Toggles the system menu if it's visible
5. Unpauses the game

### Loading Game State
The `load_game()` function:
1. Checks if a save file exists
2. Loads the JSON data
3. Applies player position and stats
4. Clears and reloads inventory items
5. Clears and reloads equipped items
6. Updates UI components
7. Toggles the system menu if it's visible

### Item Creation
The `create_item_from_data()` function:
1. Determines the item type (Weapon, Armor, Hands, Consumable)
2. Creates appropriate object with saved attributes
3. Returns the constructed item object

## Usage in Game

### System Menu Integration
The save/load functions are integrated with the system menu:
- **Save Game**: Called when the player selects "Save Game" from the system menu
- **Load Game**: Called when the player selects "Load Game" from the system menu
- **Auto-save**: Game state is saved when quitting the game

### UI Considerations
- The system menu is automatically toggled after a successful save or load operation
- Inventory and equipment UIs are refreshed after loading to reflect current state

## Compatibility Handling
The code includes several compatibility measures:
- Graceful handling of missing attributes using `getattr()`
- Field fallbacks with default values
- Support for different property names (e.g., `health`/`hp`, `xp`/`experience`)

## Error Handling
- File operations are wrapped in try/except blocks
- Errors during save/load are logged to console
- Game continues running even if save/load operations fail

## TODO
- ✅ 1.0 Implement Resume Game and Load Game so that Inventory and Equipped items are loaded and populated from save game - *Fixed loading of inventory and equipment items by preserving item positions and ensuring proper UI updates*
- 1.2 Add support for saving quest progress and active quests
- 2 Implement multiple save slots for different playthroughs
- 3 Add save file timestamps and metadata
- 4 Support for saving monster states and positions
- 5 Compress save files to reduce size
- 6 Add autosave functionality at key points (level up, quest completion)
- 7 Include game settings in save data

<!-- Edit this section to provide further instructions --> 