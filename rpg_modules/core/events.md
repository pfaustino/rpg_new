# Event System Documentation

The event system allows game components to communicate with each other through events without direct dependencies. This helps maintain a clean and modular codebase.

## Key Components

### EventType

An enumeration of all possible event types in the game. Events are categorized by their functionality:

- **Core gameplay events**: Player movements, interactions, dungeon loading, etc.
- **Puzzle-related events**: Puzzle state changes, room unlocks, etc.
- **Quest-related events**: Quest progress, item collection, monster kills, etc.
- **Inventory events**: Item addition/removal, equipment changes, etc.
- **Combat events**: Damage, healing, combat state changes, etc.
- **Dialog events**: Dialog interactions, etc.

### GameEvent

A container class for event data with:
- `event_type`: The type of the event (an EventType enum value)
- `data`: A dictionary containing any additional data relevant to the event

### EventSystem

The main system for registering, triggering, and handling events:

- `register_handler(event_type, handler)`: Register a handler function for a specific event type
- `unregister_handler(event_type, handler)`: Remove a handler function for a specific event type
- `trigger_event(event)`: Trigger an event, calling all registered handlers
- `clear_handlers(event_type=None)`: Clear all handlers for a specific event type or all handlers

## Usage Examples

### Registering an Event Handler

```python
from rpg_modules.core.events import EventSystem, EventType, GameEvent

# Create an event system
event_system = EventSystem()

# Define a handler function
def on_player_move(event):
    new_position = event.data.get('position')
    print(f"Player moved to {new_position}")

# Register the handler
event_system.register_handler(EventType.PLAYER_MOVE, on_player_move)
```

### Triggering an Event

```python
# Create and trigger a player move event
event_system.trigger_event(
    GameEvent(EventType.PLAYER_MOVE, {
        'position': (10, 15)
    })
)
```

### Unregistering a Handler

```python
# Remove a handler when it's no longer needed
event_system.unregister_handler(EventType.PLAYER_MOVE, on_player_move)
```

## Best Practices

1. **Keep event data simple**: Include only the necessary data in the event
2. **Use typed dictionaries**: Document the expected structure of the event data
3. **Handle exceptions in handlers**: Ensure one bad handler doesn't break the chain
4. **Avoid circular event triggering**: Be careful not to create infinite loops
5. **Unregister handlers**: Clean up handlers when components are destroyed

## Integration with Other Systems

### Quest System

```python
# Register quest handlers with the event system
def register_quest_handlers(quest_manager, event_system):
    event_system.register_handler(EventType.MONSTER_KILLED, quest_manager.on_monster_killed)
    event_system.register_handler(EventType.ITEM_COLLECTED, quest_manager.on_item_collected)
    # ... other quest-related events
```

### UI Updates

```python
# Register UI update handlers
event_system.register_handler(EventType.PLAYER_DAMAGED, ui_manager.update_health_display)
event_system.register_handler(EventType.ITEM_ADDED, ui_manager.update_inventory)
```

### Save System

Events can be used to trigger auto-saves:

```python
event_system.register_handler(EventType.QUEST_COMPLETED, save_manager.auto_save)
event_system.register_handler(EventType.PLAYER_LEVEL_UP, save_manager.auto_save)
``` 