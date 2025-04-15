"""
Event system for handling game events.
"""

from enum import Enum, auto
from typing import Dict, List, Callable, Any


class EventType(Enum):
    """Event types for game events."""
    # Core gameplay events
    PLAYER_MOVE = auto()
    INTERACT = auto()
    DUNGEON_LOADED = auto()
    
    # Puzzle-related events
    PUZZLE_STATE_CHANGED = auto()
    RITUAL_CHAMBER_UNLOCKED = auto()
    ENTERED_PUZZLE_ROOM = auto()
    
    # Quest-related events
    QUEST_STARTED = auto()
    QUEST_UPDATED = auto()
    QUEST_COMPLETED = auto()
    ITEM_COLLECTED = auto()
    MONSTER_KILLED = auto()
    PLAYER_LEVEL_UP = auto()
    
    # Inventory events
    ITEM_ADDED = auto()
    ITEM_REMOVED = auto()
    ITEM_USED = auto()
    EQUIPMENT_CHANGED = auto()
    
    # Combat events
    COMBAT_STARTED = auto()
    COMBAT_ENDED = auto()
    PLAYER_DAMAGED = auto()
    PLAYER_HEALED = auto()
    ENEMY_DAMAGED = auto()
    ENEMY_KILLED = auto()
    
    # Dialog events
    DIALOG_STARTED = auto()
    DIALOG_ENDED = auto()
    DIALOG_OPTION_SELECTED = auto()


class GameEvent:
    """
    Game event data container.
    """
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        """
        Initialize a game event.
        
        Args:
            event_type: The type of the event
            data: Additional data associated with the event
        """
        self.event_type = event_type
        self.data = data or {}


class EventSystem:
    """
    Event system for handling game events.
    
    The event system allows game components to register for events and receive
    callbacks when those events occur.
    """
    
    def __init__(self):
        """Initialize the event system."""
        self._handlers: Dict[EventType, List[Callable[[GameEvent], None]]] = {}
        
    def register_handler(self, event_type: EventType, handler: Callable[[GameEvent], None]) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: The type of event to register for
            handler: The callback function to invoke when the event occurs
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
    
    def unregister_handler(self, event_type: EventType, handler: Callable[[GameEvent], None]) -> None:
        """
        Unregister a handler for a specific event type.
        
        Args:
            event_type: The type of event to unregister from
            handler: The callback function to remove
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
    
    def trigger_event(self, event: GameEvent) -> None:
        """
        Trigger an event, notifying all registered handlers.
        
        Args:
            event: The event to trigger
        """
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                handler(event)
                
    def clear_handlers(self, event_type: EventType = None) -> None:
        """
        Clear all handlers for a specific event type or all handlers if no event type is specified.
        
        Args:
            event_type: The event type to clear handlers for, or None to clear all handlers
        """
        if event_type is None:
            self._handlers.clear()
        elif event_type in self._handlers:
            self._handlers[event_type] = [] 