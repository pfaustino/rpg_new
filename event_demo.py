"""
Event system demonstration for the RPG game.
"""

from rpg_modules.core.events import EventSystem, EventType, GameEvent

def main():
    # Create the event system
    event_system = EventSystem()
    
    # Define event handlers
    def on_player_move(event):
        print(f"Player moved to position: {event.data.get('position')}")
        
    def on_item_collected(event):
        item = event.data.get('item')
        print(f"Player collected item: {item.get('name')} (worth {item.get('value')} gold)")
        
    def on_monster_killed(event):
        monster = event.data.get('monster')
        position = event.data.get('position')
        print(f"Player killed a {monster.get('type')} at position {position}")
        print(f"Gained {monster.get('xp')} experience points!")
    
    # Register the event handlers
    event_system.register_handler(EventType.PLAYER_MOVE, on_player_move)
    event_system.register_handler(EventType.ITEM_COLLECTED, on_item_collected)
    event_system.register_handler(EventType.MONSTER_KILLED, on_monster_killed)
    
    # Simulate some game events
    print("=== Starting event simulation ===")
    
    # Player movement event
    event_system.trigger_event(
        GameEvent(EventType.PLAYER_MOVE, {
            'position': (10, 15)
        })
    )
    
    # Item collection event
    event_system.trigger_event(
        GameEvent(EventType.ITEM_COLLECTED, {
            'item': {
                'name': 'Healing Potion',
                'value': 25,
                'type': 'consumable'
            }
        })
    )
    
    # Monster kill event
    event_system.trigger_event(
        GameEvent(EventType.MONSTER_KILLED, {
            'monster': {
                'type': 'SKELETON',
                'level': 3,
                'xp': 50
            },
            'position': (12, 18)
        })
    )
    
    print("=== Event simulation complete ===")
    
    # Unregister an event handler
    print("\nUnregistering monster kill handler...")
    event_system.unregister_handler(EventType.MONSTER_KILLED, on_monster_killed)
    
    # Try triggering the event again
    print("\nKilling another monster (should not trigger handler):")
    event_system.trigger_event(
        GameEvent(EventType.MONSTER_KILLED, {
            'monster': {
                'type': 'SLIME',
                'level': 1,
                'xp': 20
            },
            'position': (8, 5)
        })
    )
    
    # Clear all handlers for a specific event
    print("\nClearing all player move handlers...")
    event_system.clear_handlers(EventType.PLAYER_MOVE)
    
    # Try triggering the event again
    print("\nMoving player (should not trigger handler):")
    event_system.trigger_event(
        GameEvent(EventType.PLAYER_MOVE, {
            'position': (20, 25)
        })
    )

if __name__ == "__main__":
    main() 