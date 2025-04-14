"""
Save game functionality for RPG game.
"""

import os
import json
from .items.weapon import Weapon
from .items.armor import Armor
from .items.hands import Hands
from .items.consumable import Consumable

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
    os.makedirs('save', exist_ok=True)
    with open('save/savegame.json', 'w') as f:
        json.dump(save_data, f, indent=2)
    print("Game saved to save\\savegame.json")
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
    save_path = os.path.join(game_state.save_path, game_state.save_file)
    print(f"Attempting to load game from: {save_path}")
    if os.path.exists(save_path):
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
                print("Save data loaded successfully.")
            
            # Load player data
            player_data = save_data.get('player', {})
            game_state.player.rect.x = player_data.get('x', game_state.player.rect.x)
            game_state.player.rect.y = player_data.get('y', game_state.player.rect.y)
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
            
            print(f"Game loaded from {save_path}")
            # Only close the system menu if it's currently visible
            if game_state.system_menu_ui.visible:
                game_state.system_menu_ui.toggle()
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"No saved game found at {save_path}.")

def resume_game(game_state):
    """
    Resume the game by hiding the system menu.
    
    Args:
        game_state: The current GameState object
    """
    game_state.system_menu_ui.toggle()
    print("Game resumed")

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