"""
Game flow controller for managing transitions between different game states.
"""

import pygame
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from .town_map import TownMap
from .dungeon import Dungeon, RoomType
from .dungeon_handler import DungeonHandler
from .events import EventSystem, EventType, GameEvent
from ..quests import QuestManager, initialize_main_quest_system, register_quest_event_handlers
from ..entities import player as player_module
from ..ui.quest import QuestUI
import os
import json

class GameState(Enum):
    """Different states the game can be in."""
    CHARACTER_SELECT = 1
    TOWN = 2
    DUNGEON = 3
    COMBAT = 4
    DIALOG = 5
    INVENTORY = 6
    QUEST_LOG = 7
    GAME_MENU = 8

class GameFlow:
    """
    Controls the flow of the game, managing transitions between different states
    and coordinating systems like maps, quests, and NPCs.
    """
    
    def __init__(self, screen, audio_system=None):
        """Initialize the game flow controller."""
        self.screen = screen
        self.current_state = GameState.CHARACTER_SELECT
        self.previous_state = None
        self.screen_transition_alpha = 255  # For fade transitions
        self.transition_direction = 0  # -1 for fade out, 1 for fade in
        
        # Initialize core systems
        self.event_system = EventSystem()
        self.audio_system = audio_system
        
        # Initialize maps
        self.town_map = None
        self.dungeon = None
        self.current_map = None
        
        # Initialize game entities
        self.player = None
        self.npc_manager = None
        
        # Initialize quest system
        self.quest_manager = None
        self.main_quest_handler = None
        
        # UI components
        self.ui_components = {}
        
        # Key bindings
        self.key_bindings = {
            pygame.K_q: self._toggle_quest_ui,
            pygame.K_i: self._toggle_inventory,
            pygame.K_e: self._interact,
            pygame.K_f: self._enter_exit_dungeon,
            pygame.K_ESCAPE: self._toggle_game_menu
        }
        
        # Register for events
        self.event_system.register_handler(EventType.DUNGEON_LOADED, self._on_dungeon_loaded)
        self.event_system.register_handler(EventType.QUEST_STARTED, self._on_quest_started)
        self.event_system.register_handler(EventType.QUEST_UPDATED, self._on_quest_updated)
        self.event_system.register_handler(EventType.QUEST_COMPLETED, self._on_quest_completed)
        
    def initialize(self):
        """Initialize the game flow after all components are created."""
        # Create town map
        self.town_map = TownMap(100, 100)
        
        # Initialize player position in town
        spawn_x, spawn_y = self.town_map.get_spawn_position()
        
        # Create dungeon handler
        self.dungeon_handler = DungeonHandler(self)
        
        # Initialize quest system
        self.quest_manager, self.main_quest_handler = initialize_main_quest_system(self)
        
        # Add quest UI once quest system is initialized
        quest_ui = QuestUI(self.screen, self.quest_manager.quest_log)
        self.ui_components["quest"] = quest_ui
        
        # Register quest event handlers
        register_quest_event_handlers(self.quest_manager, self.event_system)
        
        # Set starting map to town
        self.current_map = self.town_map
        
        # Notification system
        self.notifications = []
        self.notification_duration = 3.0  # seconds
        
        print("Game flow initialized")
    
    def set_player(self, player):
        """Set the player character after character selection."""
        self.player = player
        
        # Set initial position in town
        spawn_x, spawn_y = self.town_map.get_spawn_position()
        self.player.set_position(spawn_x, spawn_y)
        
        # Transition to town
        self.transition_to(GameState.TOWN)
    
    def transition_to(self, new_state: GameState):
        """
        Transition from the current state to a new state.
        
        Args:
            new_state: The state to transition to
        """
        if new_state == self.current_state:
            return
            
        print(f"Transitioning from {self.current_state} to {new_state}")
        
        # Store previous state for back functionality
        self.previous_state = self.current_state
        
        # Perform state-specific setup
        if new_state == GameState.TOWN:
            if self.current_state == GameState.CHARACTER_SELECT:
                # First time entering town after character selection
                self._setup_town_first_time()
            else:
                # Returning to town
                self._return_to_town()
                
        elif new_state == GameState.DUNGEON:
            # Entering the dungeon
            self._enter_dungeon()
        
        # Update state
        self.current_state = new_state
        
        # Begin screen transition effect
        self.transition_direction = -1  # Fade out
        self.screen_transition_alpha = 0
    
    def update(self, dt: float, events: List[pygame.event.Event] = None):
        """
        Update the game flow state.
        
        Args:
            dt: Delta time since last update
            events: List of pygame events
        """
        # Handle screen transitions
        if self.transition_direction != 0:
            if self.transition_direction < 0:  # Fade out
                self.screen_transition_alpha += 510 * dt  # Fade out faster
                if self.screen_transition_alpha >= 255:
                    self.screen_transition_alpha = 255
                    self.transition_direction = 1  # Start fading in
            else:  # Fade in
                self.screen_transition_alpha -= 255 * dt
                if self.screen_transition_alpha <= 0:
                    self.screen_transition_alpha = 0
                    self.transition_direction = 0  # Transition complete
        
        # Process keyboard shortcuts for all states except dialog
        if events and self.current_state != GameState.DIALOG:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key in self.key_bindings:
                    self.key_bindings[event.key]()
        
        # Update based on current state
        if self.current_state == GameState.CHARACTER_SELECT:
            self._update_character_select(dt, events)
        elif self.current_state == GameState.TOWN:
            self._update_town(dt, events)
        elif self.current_state == GameState.DUNGEON:
            self._update_dungeon(dt, events)
        elif self.current_state == GameState.DIALOG:
            self._update_dialog(dt, events)
        elif self.current_state == GameState.QUEST_LOG:
            self._update_quest_log(dt, events)
        elif self.current_state == GameState.INVENTORY:
            self._update_inventory(dt, events)
        elif self.current_state == GameState.GAME_MENU:
            self._update_game_menu(dt, events)
    
    def draw(self):
        """Draw the current game state."""
        self.screen.fill((0, 0, 0))  # Clear screen
        
        # Draw based on current state
        if self.current_state == GameState.CHARACTER_SELECT:
            self._draw_character_select()
        elif self.current_state == GameState.TOWN:
            self._draw_town()
        elif self.current_state == GameState.DUNGEON:
            self._draw_dungeon()
        elif self.current_state == GameState.DIALOG:
            self._draw_dialog()
        elif self.current_state == GameState.QUEST_LOG:
            self._draw_quest_log()
        elif self.current_state == GameState.INVENTORY:
            self._draw_inventory()
        elif self.current_state == GameState.GAME_MENU:
            self._draw_game_menu()
        
        # Draw transition overlay
        if self.screen_transition_alpha > 0:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.screen_transition_alpha)))
            self.screen.blit(overlay, (0, 0))
            
        # Draw quest notification if needed
        self._draw_notifications()
    
    def _setup_town_first_time(self):
        """Set up the town map and NPCs when first entering the town."""
        # Initialize NPCs in town
        if self.npc_manager:
            self.npc_manager.populate_town(self.town_map)
            
        # Make quest givers available
        self._setup_quest_givers()
            
        # Set current map
        self.current_map = self.town_map
        
        # Play town music
        if self.audio_system:
            self.audio_system.play_music("town_theme")
    
    def _return_to_town(self):
        """Handle return to town from dungeon or other areas."""
        # Set current map
        self.current_map = self.town_map
        
        # Restore player position to town
        if self.player:
            # If coming from dungeon, position near dungeon entrance
            if self.previous_state == GameState.DUNGEON:
                entrance_pos = self.town_map.get_dungeon_entrance_position()
                if entrance_pos:
                    entrance_x, entrance_y = entrance_pos
                    # Position player slightly south of entrance
                    self.player.set_position(entrance_x, entrance_y + 3)
            
        # Play town music
        if self.audio_system:
            self.audio_system.play_music("town_theme")
    
    def _enter_dungeon(self):
        """Handle entering the dungeon from town."""
        # Create the dungeon if it doesn't exist
        if not self.dungeon:
            self.dungeon = self.dungeon_handler.create_dungeon(100, 100)
        
        # Set current map to dungeon
        self.current_map = self.dungeon
        
        # Position player at dungeon entrance
        if self.player:
            entrance_room = next((room for room in self.dungeon.rooms 
                                 if room.room_type == RoomType.ENTRANCE), None)
            if entrance_room:
                center_x, center_y = entrance_room.get_center()
                self.player.set_position(center_x, center_y)
                
        # Play dungeon music
        if self.audio_system:
            self.audio_system.play_music("dungeon_theme")
            
        # Trigger dungeon loaded event
        self.event_system.trigger_event(
            GameEvent(EventType.DUNGEON_LOADED, {"dungeon": self.dungeon})
        )
    
    def _setup_quest_givers(self):
        """Set up quest givers in the town."""
        if not self.npc_manager or not self.quest_manager:
            return
        
        # Get quest giver positions from town map
        quest_giver_positions = self.town_map.get_quest_givers()
        
        # Create Elder Malik NPC at the first position (specifically added there in town_map)
        if quest_giver_positions:
            elder_pos = quest_giver_positions[0]
            self.npc_manager.create_npc(
                "elder_malik",
                "Elder Malik",
                elder_pos[0],
                elder_pos[1],
                title="Village Elder",
                dialog_id="elder_malik_intro",
                sprite_id="elder_male",
                npc_type="quest_giver"
            )
            print(f"Elder Malik placed at position {elder_pos}")
            
            # Make sure the side quest is available from Elder Malik
            if self.quest_manager:
                # Load side quests if they're not already loaded
                side_quests_path = os.path.join(self.quest_manager.quest_data_path, "side_quests.json")
                if os.path.exists(side_quests_path):
                    try:
                        with open(side_quests_path, 'r') as f:
                            quest_data = json.load(f)
                            
                        # Make Elder Malik's quest available
                        for quest in quest_data.get("quests", []):
                            if quest.get("giver_id") == "elder_malik":
                                self.quest_manager.add_quest(quest)
                                print(f"Added quest '{quest.get('title')}' from Elder Malik")
                    except Exception as e:
                        print(f"Error loading side quests: {e}")
                else:
                    print(f"Side quests file not found: {side_quests_path}")
        
        # Create other quest givers (starting from the second position)
        for i, pos in enumerate(quest_giver_positions[1:], 1):
            npc_id = f"quest_giver_{i}"
            npc_name = f"Quest Giver {i}"
            
            self.npc_manager.create_npc(
                npc_id,
                npc_name,
                pos[0],
                pos[1],
                npc_type="quest_giver"
            )
    
    def _update_character_select(self, dt: float, events: List[pygame.event.Event]):
        """Update character selection screen."""
        character_select_ui = self.ui_components.get("character_select")
        if character_select_ui:
            character_select_ui.update(dt)
            
            # Handle events
            if events:
                for event in events:
                    if character_select_ui.handle_event(event):
                        # If character selected, transition to town
                        if character_select_ui.character_selected:
                            player = player_module.Player(
                                character_select_ui.selected_type,
                                character_select_ui.selected_name
                            )
                            self.set_player(player)
    
    def _update_town(self, dt: float, events: List[pygame.event.Event]):
        """Update town state."""
        # Update NPCs
        if self.npc_manager:
            self.npc_manager.update(dt)
            
        # Update player
        if self.player:
            old_x, old_y = self.player.get_position()
            self.player.update(dt, self.current_map)
            new_x, new_y = self.player.get_position()
            
            # Check for player movement
            if (old_x, old_y) != (new_x, new_y):
                self.event_system.trigger_event(
                    GameEvent(EventType.PLAYER_MOVE, {
                        "position": (new_x, new_y)
                    })
                )
                
            # Check for interaction with NPCs
            if events:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        # Interaction key pressed
                        self._check_npc_interaction()
                        
            # Check for entering dungeon
            dungeon_entrance = self.town_map.get_dungeon_entrance_position()
            if dungeon_entrance:
                entrance_x, entrance_y = dungeon_entrance
                player_x, player_y = self.player.get_position()
                
                # If player is close to entrance, allow entering
                if abs(player_x - entrance_x) <= 1 and abs(player_y - entrance_y) <= 1:
                    # Show dungeon entrance prompt
                    if events:
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                                # Enter dungeon
                                self.transition_to(GameState.DUNGEON)
    
    def _update_dungeon(self, dt: float, events: List[pygame.event.Event]):
        """Update dungeon state."""
        # Update player
        if self.player:
            old_x, old_y = self.player.get_position()
            self.player.update(dt, self.current_map)
            new_x, new_y = self.player.get_position()
            
            # Check for player movement
            if (old_x, old_y) != (new_x, new_y):
                self.event_system.trigger_event(
                    GameEvent(EventType.PLAYER_MOVE, {
                        "position": (new_x, new_y)
                    })
                )
                
            # Check for dungeon exit
            if events:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                        # Check if player is at entrance
                        entrance_room = next((room for room in self.dungeon.rooms 
                                             if room.room_type == RoomType.ENTRANCE), None)
                        if entrance_room:
                            player_x, player_y = self.player.get_position()
                            room_center_x, room_center_y = entrance_room.get_center()
                            
                            # If player is close to entrance, allow exiting
                            if abs(player_x - room_center_x) <= 3 and abs(player_y - room_center_y) <= 3:
                                # Exit dungeon to town
                                self.transition_to(GameState.TOWN)
    
    def _update_dialog(self, dt: float, events: List[pygame.event.Event]):
        """Update dialog state."""
        dialog_ui = self.ui_components.get("dialog")
        if dialog_ui:
            dialog_ui.update(dt)
            
            # Handle events
            if events:
                for event in events:
                    if dialog_ui.handle_event(event):
                        if dialog_ui.is_complete():
                            # Return to previous state
                            self.transition_to(self.previous_state)
    
    def _draw_character_select(self):
        """Draw character selection screen."""
        character_select_ui = self.ui_components.get("character_select")
        if character_select_ui:
            character_select_ui.draw(self.screen)
    
    def _draw_town(self):
        """Draw town state."""
        # Draw map
        if self.current_map:
            self.current_map.draw(self.screen, self.player)
            
        # Draw NPCs
        if self.npc_manager:
            self.npc_manager.draw(self.screen)
            
        # Draw player
        if self.player:
            self.player.draw(self.screen)
            
        # Draw UI components
        for ui in self.ui_components.values():
            if ui.visible:
                ui.draw(self.screen)
    
    def _draw_dungeon(self):
        """Draw dungeon state."""
        # Draw map
        if self.current_map:
            self.current_map.draw(self.screen, self.player)
            
        # Draw player
        if self.player:
            self.player.draw(self.screen)
            
        # Draw UI components
        for ui in self.ui_components.values():
            if ui.visible:
                ui.draw(self.screen)
    
    def _draw_dialog(self):
        """Draw dialog state."""
        # Draw background (town or dungeon)
        if self.previous_state == GameState.TOWN:
            self._draw_town()
        elif self.previous_state == GameState.DUNGEON:
            self._draw_dungeon()
            
        # Draw dialog UI on top
        dialog_ui = self.ui_components.get("dialog")
        if dialog_ui:
            dialog_ui.draw(self.screen)
    
    def _check_npc_interaction(self):
        """Check if player is near an NPC to interact with."""
        if not self.player or not self.npc_manager:
            return
            
        player_x, player_y = self.player.get_position()
        
        # Find the closest NPC within interaction range
        closest_npc = self.npc_manager.get_closest_npc(player_x, player_y, 2)
        
        if closest_npc:
            # Start dialog with NPC
            self._start_dialog(closest_npc)
    
    def _start_dialog(self, npc):
        """Start dialog with an NPC."""
        dialog_ui = self.ui_components.get("dialog")
        if dialog_ui:
            # Set dialog content based on NPC
            dialog_content = self._get_dialog_for_npc(npc)
            if dialog_content:
                dialog_ui.set_dialog(dialog_content, npc)
                dialog_ui.start()
                
                # Transition to dialog state
                self.transition_to(GameState.DIALOG)
    
    def _get_dialog_for_npc(self, npc):
        """Get dialog content for an NPC based on quests and state."""
        if not self.quest_manager:
            return None
            
        return self.quest_manager.get_dialog_for_npc(npc.id)
    
    def _on_dungeon_loaded(self, event: GameEvent):
        """Handle dungeon loaded event."""
        print("Dungeon loaded successfully")
    
    def _toggle_quest_ui(self):
        """Toggle the quest UI on and off."""
        if self.current_state == GameState.QUEST_LOG:
            # Return to previous state if already in quest log
            self.transition_to(self.previous_state)
        else:
            # Open quest log
            self.transition_to(GameState.QUEST_LOG)
    
    def _toggle_inventory(self):
        """Toggle the inventory UI on and off."""
        if self.current_state == GameState.INVENTORY:
            # Return to previous state if already in inventory
            self.transition_to(self.previous_state)
        else:
            # Open inventory
            self.transition_to(GameState.INVENTORY)
    
    def _toggle_game_menu(self):
        """Toggle the game menu on and off."""
        if self.current_state == GameState.GAME_MENU:
            # Return to previous state if already in game menu
            self.transition_to(self.previous_state)
        else:
            # Open game menu
            self.transition_to(GameState.GAME_MENU)
    
    def _interact(self):
        """Interact with objects or NPCs."""
        if self.current_state == GameState.TOWN or self.current_state == GameState.DUNGEON:
            self._check_npc_interaction()
    
    def _enter_exit_dungeon(self):
        """Enter or exit the dungeon based on current location."""
        if self.current_state == GameState.TOWN:
            # Check if player is near dungeon entrance
            dungeon_entrance = self.town_map.get_dungeon_entrance_position()
            if dungeon_entrance and self.player:
                entrance_x, entrance_y = dungeon_entrance
                player_x, player_y = self.player.get_position()
                
                # If player is close to entrance, enter dungeon
                if abs(player_x - entrance_x) <= 1 and abs(player_y - entrance_y) <= 1:
                    self.transition_to(GameState.DUNGEON)
                    
        elif self.current_state == GameState.DUNGEON:
            # Check if player is at entrance room
            if self.dungeon and self.player:
                entrance_room = next((room for room in self.dungeon.rooms 
                                     if room.room_type == RoomType.ENTRANCE), None)
                if entrance_room:
                    player_x, player_y = self.player.get_position()
                    room_center_x, room_center_y = entrance_room.get_center()
                    
                    # If player is close to entrance, exit dungeon
                    if abs(player_x - room_center_x) <= 3 and abs(player_y - room_center_y) <= 3:
                        self.transition_to(GameState.TOWN)
    
    def _update_quest_log(self, dt: float, events: List[pygame.event.Event]):
        """Update quest log state."""
        quest_ui = self.ui_components.get("quest")
        if quest_ui:
            quest_ui.update()
            
            # Handle events
            if events:
                for event in events:
                    quest_ui.handle_event(event)
                    
                    # Check for exit keys (ESC or Q)
                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                        self.transition_to(self.previous_state)
    
    def _update_inventory(self, dt: float, events: List[pygame.event.Event]):
        """Update inventory state."""
        inventory_ui = self.ui_components.get("inventory")
        if inventory_ui:
            inventory_ui.update()
            
            # Handle events
            if events:
                for event in events:
                    inventory_ui.handle_event(event)
                    
                    # Check for exit keys (ESC or I)
                    if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_i):
                        self.transition_to(self.previous_state)
    
    def _update_game_menu(self, dt: float, events: List[pygame.event.Event]):
        """Update game menu state."""
        game_menu_ui = self.ui_components.get("game_menu")
        if game_menu_ui:
            game_menu_ui.update()
            
            # Handle events
            if events:
                for event in events:
                    game_menu_ui.handle_event(event)
                    
                    # Check for exit key (ESC)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.transition_to(self.previous_state)
    
    def _draw_quest_log(self):
        """Draw quest log UI."""
        # Draw background (town or dungeon)
        if self.previous_state == GameState.TOWN:
            self._draw_town()
        elif self.previous_state == GameState.DUNGEON:
            self._draw_dungeon()
            
        # Draw quest UI on top
        quest_ui = self.ui_components.get("quest")
        if quest_ui:
            quest_ui.visible = True
            quest_ui.draw(self.screen)
    
    def _draw_inventory(self):
        """Draw inventory UI."""
        # Draw background (town or dungeon)
        if self.previous_state == GameState.TOWN:
            self._draw_town()
        elif self.previous_state == GameState.DUNGEON:
            self._draw_dungeon()
            
        # Draw inventory UI on top
        inventory_ui = self.ui_components.get("inventory")
        if inventory_ui:
            inventory_ui.visible = True
            inventory_ui.draw(self.screen)
    
    def _draw_game_menu(self):
        """Draw game menu UI."""
        # Dim background
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw game menu UI on top
        game_menu_ui = self.ui_components.get("game_menu")
        if game_menu_ui:
            game_menu_ui.draw(self.screen)
    
    def _on_quest_started(self, event: GameEvent):
        """Handle quest started event."""
        quest_id = event.data.get("quest_id")
        if quest_id and self.quest_manager:
            quest = self.quest_manager.quest_log.get_quest(quest_id)
            if quest:
                print(f"Quest started: {quest.title}")
                # Play quest accept sound
                if self.audio_system:
                    self.audio_system.play_sound("quest_accept")
                
                # Add notification
                self.add_notification(f"New Quest: {quest.title}", (255, 255, 0), self.notification_duration)
    
    def _on_quest_updated(self, event: GameEvent):
        """Handle quest updated event."""
        quest_id = event.data.get("quest_id")
        objective_index = event.data.get("objective_index")
        if quest_id and self.quest_manager and objective_index is not None:
            quest = self.quest_manager.quest_log.get_quest(quest_id)
            if quest and 0 <= objective_index < len(quest.objectives):
                objective = quest.objectives[objective_index]
                print(f"Quest objective updated: {objective.description}")
                
                # Play objective updated sound
                if self.audio_system:
                    self.audio_system.play_sound("objective_complete")
                
                # Add notification
                self.add_notification(f"Objective Completed: {objective.description}", (0, 255, 0), self.notification_duration)
    
    def _on_quest_completed(self, event: GameEvent):
        """Handle quest completed event."""
        quest_id = event.data.get("quest_id")
        if quest_id and self.quest_manager:
            quest = self.quest_manager.quest_log.get_quest(quest_id)
            if quest:
                print(f"Quest completed: {quest.title}")
                
                # Play quest complete sound
                if self.audio_system:
                    self.audio_system.play_sound("quest_complete")
                
                # Add notification
                self.add_notification(f"Quest Completed: {quest.title}", (255, 215, 0), self.notification_duration * 1.5)
    
    def add_notification(self, text: str, color: Tuple[int, int, int], duration: float):
        """Add a notification to be displayed."""
        self.notifications.append({
            "text": text,
            "color": color,
            "duration": duration,
            "remaining": duration,
            "alpha": 255,
            "y_offset": 0
        })
    
    def _update_notifications(self, dt: float):
        """Update notification timers and animations."""
        for notification in self.notifications[:]:
            notification["remaining"] -= dt
            
            # Fade out when near end of duration
            if notification["remaining"] < 1.0:
                notification["alpha"] = int(255 * notification["remaining"])
            
            # Move notification up as it ages
            notification["y_offset"] = int((notification["duration"] - notification["remaining"]) * 40)
            
            # Remove expired notifications
            if notification["remaining"] <= 0:
                self.notifications.remove(notification)
    
    def _draw_notifications(self):
        """Draw active notifications on screen."""
        if not self.notifications:
            return
            
        # Update notifications
        dt = 1/60  # Approximate if not known
        self._update_notifications(dt)
        
        # Get font
        font = pygame.font.Font(None, 28)
        
        # Draw notifications from bottom to top
        screen_width = self.screen.get_width()
        y_base = self.screen.get_height() - 100
        
        for i, notification in enumerate(self.notifications):
            text_surface = font.render(notification["text"], True, notification["color"])
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen_width // 2
            text_rect.y = y_base - (len(self.notifications) - i) * 30 - notification["y_offset"]
            
            # Draw with current alpha
            if notification["alpha"] < 255:
                temp_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                temp_surface.fill((255, 255, 255, notification["alpha"]))
                text_surface.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            self.screen.blit(text_surface, text_rect) 