"""
Save game functionality for RPG game.
"""

import os
import json
import glob
import time
from .items.weapon import Weapon
from .items.armor import Armor
from .items.hands import Hands
from .items.consumable import Consumable

# File to store the last played character info
LAST_PLAYED_FILE = "save/last_played.json"

def get_last_played_save():
    """
    Get the save file for the most recently played character.
    
    Returns:
        Path to the most recent save file, or None if no saves exist.
    """
    try:
        if os.path.exists(LAST_PLAYED_FILE):
            with open(LAST_PLAYED_FILE, 'r') as f:
                last_played = json.load(f)
                save_file = last_played.get('save_file')
                
                # Verify the save file actually exists
                if save_file and os.path.exists(save_file):
                    print(f"Found last played save: {save_file}")
                    return save_file
                else:
                    print("Last played save file not found, using latest save.")
    except Exception as e:
        print(f"Error reading last played file: {e}")
    
    # Fallback to most recent modified save file
    save_files = get_save_files_by_time()
    return save_files[0]['filename'] if save_files else None

def get_save_files_by_time():
    """
    Get save files sorted by modification time (most recent first).
    
    Returns:
        List of save files with metadata, sorted by last modified time.
    """
    save_files = get_save_files()
    
    # Add modification time
    for save_file in save_files:
        try:
            save_file['modified'] = os.path.getmtime(save_file['filename'])
        except:
            save_file['modified'] = 0
    
    # Sort by modification time (newest first)
    save_files.sort(key=lambda x: x['modified'], reverse=True)
    return save_files

def update_last_played(save_file):
    """
    Update the record of the last played character.
    
    Args:
        save_file: Path to the save file that was just used
    """
    # Create save directory if it doesn't exist
    os.makedirs('save', exist_ok=True)
    
    # Record last played info
    last_played = {
        'save_file': save_file,
        'timestamp': time.time()
    }
    
    try:
        with open(LAST_PLAYED_FILE, 'w') as f:
            json.dump(last_played, f)
        print(f"Updated last played record: {save_file}")
    except Exception as e:
        print(f"Error updating last played file: {e}")

def get_save_files():
    """
    Get a list of available save files with character information.
    
    Returns:
        List of dictionaries containing character information from save files.
    """
    save_files = []
    
    # Create save directory if it doesn't exist
    os.makedirs('save', exist_ok=True)
    
    # Get all JSON files in the save directory
    save_pattern = os.path.join('save', '*_savegame.json')
    for save_path in glob.glob(save_pattern):
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
                
                # Extract player data
                player_data = save_data.get('player', {})
                character_info = {
                    'filename': save_path,
                    'name': player_data.get('name', 'Unknown'),
                    'level': player_data.get('level', 1),
                    'health': player_data.get('health', 0),
                    'max_health': player_data.get('max_health', 0),
                    'xp': player_data.get('xp', 0),
                }
                save_files.append(character_info)
        except Exception as e:
            print(f"Error reading save file {save_path}: {e}")
    
    # Sort by level (descending) then by name
    save_files.sort(key=lambda x: (-x['level'], x['name']))
    return save_files

def load_character_select():
    """
    Display character selection menu and return the chosen save file.
    
    Returns:
        Selected save file path or None if cancelled.
    """
    save_files = get_save_files()
    
    if not save_files:
        print("No save files found.")
        return None
    
    # Display available character saves
    print("\nAvailable Characters:")
    for i, character in enumerate(save_files):
        print(f"{i+1}. {character['name']} (Level {character['level']}) - HP: {character['health']}/{character['max_health']}")
    
    print("\n0. Cancel")
    
    # Get user selection
    while True:
        try:
            choice = input("\nSelect a character (0-{}): ".format(len(save_files)))
            if choice == '0':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(save_files):
                return save_files[choice_idx]['filename']
            else:
                print("Invalid selection. Please choose a valid option.")
        except ValueError:
            print("Please enter a number.")
    
    return None

def save_game(game_state):
    """
    Save the game state to a file.
    
    Args:
        game_state: The current GameState object
    """
    print("Saving game...")
    # Save the game state to a file
    save_data = {
        'player': {
            'name': game_state.player.name,
            'x': game_state.player.x,
            'y': game_state.player.y,
            'health': game_state.player.health,
            'max_health': game_state.player.max_health,
            'mana': getattr(game_state.player, 'mana', 0),
            'max_mana': getattr(game_state.player, 'max_mana', 0),
            'stamina': getattr(game_state.player, 'stamina', 0),
            'max_stamina': getattr(game_state.player, 'max_stamina', 0),
            'attack_type': getattr(game_state.player, 'attack_type', 1),
            'xp': getattr(game_state.player, 'xp', getattr(game_state.player, 'experience', 0)),
            'level': game_state.player.level,
            'inventory': [item.to_dict() if item is not None else None for item in game_state.player.inventory.items],
            'equipment': {slot: item.to_dict() for slot, item in game_state.player.equipment.slots.items() if item is not None}
        },
        'map': {
            'current_map': getattr(game_state.map, 'name', 'default_map'),
            'player_visited': list(game_state.player_visited) if hasattr(game_state, 'player_visited') else []
        }
    }
    
    # Create save directory if it doesn't exist
    os.makedirs('save', exist_ok=True)
    
    # Use player name in save file path, replace spaces with underscores
    save_filename = f"save/{game_state.player.name.replace(' ', '_')}_savegame.json"
    
    with open(save_filename, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"Game saved to {save_filename}")
    
    # Update the last played record
    update_last_played(save_filename)
    
    try:
        # Only close the system menu if it's currently visible
        if game_state.system_menu_ui.visible:
            game_state.system_menu_ui.toggle()
    except Exception as e:
        print(f"Error saving game: {e}")
    game_state.paused = False

def load_game(game_state):
    """
    Load the game state from a file if it exists.
    
    Args:
        game_state: The current GameState object
    """
    print("Loading game...")
    
    try:
        # If game has a UI character select, let it handle character selection
        if hasattr(game_state, 'character_select_ui') and game_state.character_select_ui:
            # Character selection will be handled via the UI
            # The UI's callback will process the save file when user selects a character
            game_state.character_select_ui.refresh_character_list()
            game_state.character_select_ui.show()
            return True
        
        # Otherwise, use console-based character selection
        save_filename = load_character_select()
        if not save_filename:
            print("Character selection cancelled.")
            return False
        
        print(f"Loading game from file: {save_filename}")
        return _process_save_file(game_state, save_filename)
    except Exception as e:
        print(f"Error in load_game: {e}")
        import traceback
        traceback.print_exc()
        return False
            
def _process_save_file(game_state, save_filename):
    """Process a save file and load the data into the game state."""
    try:
        with open(save_filename, 'r') as f:
            save_data = json.load(f)
            print("Save data loaded successfully.")
        
        # Load player data
        player_data = save_data.get('player', {})
        
        # Set player name from save data
        game_state.player.name = player_data.get('name', game_state.player.name)
        
        game_state.player.x = player_data.get('x', game_state.player.x)
        game_state.player.y = player_data.get('y', game_state.player.y)
        game_state.player.level = player_data.get('level', game_state.player.level)
        if hasattr(game_state.player, 'xp'):
            game_state.player.xp = player_data.get('xp', getattr(game_state.player, 'xp', 0))
        elif hasattr(game_state.player, 'experience'):
            game_state.player.experience = player_data.get('xp', getattr(game_state.player, 'experience', 0))
        if hasattr(game_state.player, 'gold'):
            game_state.player.gold = player_data.get('gold', getattr(game_state.player, 'gold', 0))
        if hasattr(game_state.player, 'health'):
            game_state.player.health = player_data.get('health', getattr(game_state.player, 'health', 0))
        elif hasattr(game_state.player, 'hp'):
            game_state.player.hp = player_data.get('health', getattr(game_state.player, 'hp', 0))
        if hasattr(game_state.player, 'max_health'):
            game_state.player.max_health = player_data.get('max_health', getattr(game_state.player, 'max_health', 0))
        elif hasattr(game_state.player, 'max_hp'):
            game_state.player.max_hp = player_data.get('max_health', getattr(game_state.player, 'max_hp', 0))
        if hasattr(game_state.player, 'mana'):
            game_state.player.mana = player_data.get('mana', getattr(game_state.player, 'mana', 0))
        if hasattr(game_state.player, 'max_mana'):
            game_state.player.max_mana = player_data.get('max_mana', getattr(game_state.player, 'max_mana', 0))
        if hasattr(game_state.player, 'stamina'):
            game_state.player.stamina = player_data.get('stamina', getattr(game_state.player, 'stamina', 0))
        if hasattr(game_state.player, 'max_stamina'):
            game_state.player.max_stamina = player_data.get('max_stamina', getattr(game_state.player, 'max_stamina', 0))
        if hasattr(game_state.player, 'attack_type'):
            game_state.player.attack_type = player_data.get('attack_type', getattr(game_state.player, 'attack_type', 1))
        if hasattr(game_state.player, 'base_attack'):
            game_state.player.base_attack = player_data.get('base_attack', getattr(game_state.player, 'base_attack', 0))
        if hasattr(game_state.player, 'defense'):
            game_state.player.defense = player_data.get('defense', getattr(game_state.player, 'defense', 0))
        if hasattr(game_state.player, 'dexterity'):
            game_state.player.dexterity = player_data.get('dexterity', getattr(game_state.player, 'dexterity', 0))
        print("Player data applied.")
        
        # Reset inventory with proper capacity
        inventory_capacity = len(game_state.player.inventory.items)
        game_state.player.inventory.items = [None] * inventory_capacity
        print(f"Reset inventory with capacity {inventory_capacity}.")
        
        # Load inventory items
        for i, item_data in enumerate(player_data.get('inventory', [])):
            if item_data:  # Only process non-None items
                item = create_item_from_data(item_data)
                if item:
                    # Add directly to inventory slot instead of using add_item
                    # This preserves the exact item positions from the save file
                    if i < inventory_capacity:
                        game_state.player.inventory.items[i] = item
        print(f"Loaded {sum(1 for item in game_state.player.inventory.items if item is not None)} items into inventory.")
        
        # Clear current equipment
        for slot in game_state.player.equipment.slots:
            game_state.player.equipment.unequip_item(slot)
        print("Current equipment cleared.")
        
        # Load equipped items
        for slot, item_data in player_data.get('equipment', {}).items():
            item = create_item_from_data(item_data)
            if item:
                game_state.player.equipment.equip_item(item)
        print(f"Loaded {len(player_data.get('equipment', {}))} equipped items.")
        
        # Make sure the inventory UI is updated with the new inventory
        game_state.refresh_inventory_ui()
        
        # Update equipment UI with player's equipment
        game_state.equipment_ui.equipment = game_state.player.equipment.slots
        game_state.equipment_ui.set_player(game_state.player)
        
        # Force a complete UI refresh
        if hasattr(game_state.inventory_ui, 'rebuild'):
            game_state.inventory_ui.rebuild()
        if hasattr(game_state.equipment_ui, 'rebuild'):
            game_state.equipment_ui.rebuild()
        
        print("Refreshed inventory and equipment UI after loading.")
        
        print(f"Successfully loaded game for {game_state.player.name}")
        # Only close the system menu if it's currently visible
        if game_state.system_menu_ui.visible:
            game_state.system_menu_ui.toggle()
        
        return True
    except Exception as e:
        print(f"Error loading game: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def resume_game(game_state):
    """
    Resume the game by hiding the system menu and loading the last played character.
    
    Args:
        game_state: The current GameState object
    """
    print("Resuming game with last played character...")
    
    # First, try to find the last played save file
    save_file = get_last_played_save()
    
    if save_file:
        # Process the save file to load the character
        success = _process_save_file(game_state, save_file)
        if success:
            print(f"Successfully resumed last played character")
        else:
            print("Failed to load last played character, just hiding menu")
            # Just hide the menu
            game_state.system_menu_ui.toggle()
    else:
        print("No saved games found to resume")
        # Just hide the menu
        game_state.system_menu_ui.toggle()
    
    # Unpause the game
    game_state.paused = False

def create_item_from_data(item_data):
    """
    Create an item object from saved data.
    
    Args:
        item_data: Dictionary with item properties
        
    Returns:
        An item object (Weapon, Armor, Hands, or Consumable)
    """
    if not item_data:
        return None
    
    quality = item_data.get('quality', 'Common')
    if item_data.get('weapon_type'):
        return Weapon(
            weapon_type=item_data.get('weapon_type', 'Sword'),
            attack_power=item_data.get('attack_power', 5),
            quality=quality,
            material=item_data.get('material', 'Iron'),
            prefix=item_data.get('prefix', None)
        )
    elif item_data.get('armor_type'):
        if item_data.get('armor_type') == 'hands':
            return Hands(
                defense=item_data.get('defense', 3),
                dexterity=item_data.get('dexterity', 1),
                quality=quality,
                material=item_data.get('material', 'Leather'),
                prefix=item_data.get('prefix', None)
            )
        else:
            return Armor(
                armor_type=item_data.get('armor_type', 'Chest'),
                defense=item_data.get('defense', 5),
                quality=quality,
                material=item_data.get('material', 'Iron'),
                prefix=item_data.get('prefix', None)
            )
    elif item_data.get('consumable_type'):
        return Consumable(
            consumable_type=item_data.get('consumable_type', 'health'),
            effect_value=item_data.get('effect_value', 20),
            quality=quality
        )
    return None 