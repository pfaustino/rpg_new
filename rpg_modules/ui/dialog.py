"""
Dialog UI module for displaying NPC conversations.
"""

import pygame
from typing import List, Dict, Optional, Any, Callable, Tuple
import json
import os
from ..utils.colors import *
from ..utils.fonts import get_font
from ..utils.ui import draw_text, draw_rect_with_border
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class DialogUI:
    """UI component for displaying and managing NPC dialog interactions."""
    
    # Constants for UI layout
    PANEL_WIDTH = 800
    PANEL_HEIGHT = 250
    PADDING = 20
    CHOICE_SPACING = 10
    CHOICE_HEIGHT = 40
    TEXT_MARGIN = 15
    PORTRAIT_SIZE = 130
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the dialog UI."""
        self.screen = screen
        self.visible = False
        self.font = get_font(18)
        self.title_font = get_font(24)
        self.choice_font = get_font(16)
        
        # Dialog state
        self.current_dialog = None
        self.current_node_id = None
        self.npc_name = ""
        self.npc_title = ""
        self.dialog_text = []
        self.choices = []
        self.clue = None
        self.flag = None
        self.portrait = None
        self.dialog_complete = False
        
        # Callbacks
        self.on_dialog_complete = None
        self.on_clue_discovered = None
        self.on_flag_set = None
        self.on_choice_selected = None
        
        # Calculate positions
        self.x = (SCREEN_WIDTH - self.PANEL_WIDTH) // 2
        self.y = SCREEN_HEIGHT - self.PANEL_HEIGHT - 20
        
        # Choice selection
        self.hovered_choice = -1
        self.selected_choice = -1
        
        # Loaded dialog data
        self.dialogs = {}
        
    def load_dialog(self, dialog_id: str) -> bool:
        """Load a dialog by ID from data files."""
        dialog_path = os.path.join("data", "quests", "dialogs")
        
        # Look in all JSON files in the dialog directory
        for filename in os.listdir(dialog_path):
            if not filename.endswith(".json"):
                continue
                
            try:
                with open(os.path.join(dialog_path, filename), 'r') as file:
                    data = json.load(file)
                    
                # Check if the dialog exists in this file
                if dialog_id in data:
                    self.current_dialog = data[dialog_id]
                    self.npc_name = self.current_dialog.get("npc_name", "NPC")
                    self.npc_title = self.current_dialog.get("npc_title", "")
                    # Start with the initial dialog node
                    self.show_dialog_node("initial")
                    return True
            except Exception as e:
                print(f"Error loading dialog {dialog_id} from {filename}: {e}")
        
        print(f"Dialog {dialog_id} not found in any file")
        return False
    
    def update(self, dt: float):
        """Update the dialog UI with the given delta time."""
        # Currently the dialog UI doesn't need time-based updates
        # But this method is required for compatibility with the game flow
        pass
        
    def set_dialog(self, dialog_content, npc=None):
        """Set the dialog content and NPC info."""
        self.current_dialog = dialog_content
        if npc:
            self.npc_name = npc.name
            self.npc_title = npc.title
            # Load NPC portrait if available
            if hasattr(npc, 'portrait_path') and npc.portrait_path:
                self.load_portrait(npc.portrait_path)
                
    def start(self):
        """Start the dialog sequence."""
        self.visible = True
        self.dialog_complete = False
        self.show_dialog_node("initial")
        
    def is_complete(self) -> bool:
        """Check if the dialog is complete."""
        return self.dialog_complete
        
    def show_dialog_node(self, node_id: str) -> bool:
        """Display a specific dialog node."""
        if not self.current_dialog or "dialogs" not in self.current_dialog:
            return False
            
        # Find the requested dialog node
        for node in self.current_dialog["dialogs"]:
            if node.get("id") == node_id:
                self.current_node_id = node_id
                self.dialog_text = node.get("text", [])
                self.choices = node.get("choices", [])
                self.clue = node.get("clue", None)
                self.flag = node.get("flag", None)
                
                # Reset selection state
                self.hovered_choice = -1
                self.selected_choice = -1
                
                # Show the dialog UI
                self.visible = True
                
                # Process clues and flags
                if self.clue and self.on_clue_discovered:
                    self.on_clue_discovered(self.clue)
                    
                if self.flag and self.on_flag_set:
                    self.on_flag_set(self.flag)
                
                return True
                
        print(f"Dialog node {node_id} not found")
        return False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # If no choices are available, any click advances/closes the dialog
                if not self.choices:
                    if self.on_dialog_complete:
                        self.on_dialog_complete(self.current_node_id)
                    self.visible = False
                    self.dialog_complete = True
                    return True
                
                # Check for choice clicks
                for i, choice in enumerate(self.choices):
                    choice_rect = self._get_choice_rect(i)
                    if choice_rect.collidepoint(mouse_pos):
                        self.selected_choice = i
                        next_node = choice.get("next", "conclusion")
                        
                        # Call the choice selected callback if set
                        if self.on_choice_selected:
                            self.on_choice_selected(self.current_node_id, i, choice.get("text", ""))
                        
                        # Check if this is an exit node
                        if next_node == "exit":
                            if self.on_dialog_complete:
                                self.on_dialog_complete(self.current_node_id)
                            self.visible = False
                            self.dialog_complete = True
                            return True
                            
                        # If there's a next node, show it, otherwise conclude dialog
                        if next_node:
                            self.show_dialog_node(next_node)
                        else:
                            if self.on_dialog_complete:
                                self.on_dialog_complete(self.current_node_id)
                            self.visible = False
                            self.dialog_complete = True
                        
                        return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.choices:
                mouse_pos = pygame.mouse.get_pos()
                prev_hovered = self.hovered_choice
                
                # Check for choice hover
                self.hovered_choice = -1
                for i, _ in enumerate(self.choices):
                    choice_rect = self._get_choice_rect(i)
                    if choice_rect.collidepoint(mouse_pos):
                        self.hovered_choice = i
                        break
                
                # Return True if the hover state changed
                return prev_hovered != self.hovered_choice
        
        return False
    
    def draw(self):
        """Draw the dialog UI."""
        if not self.visible:
            return
            
        # Draw dialog panel background
        dialog_rect = pygame.Rect(self.x, self.y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        draw_rect_with_border(self.screen, dialog_rect, DARK_GRAY, WHITE, 2)
        
        # Draw NPC portrait area (left side)
        portrait_rect = pygame.Rect(
            self.x + self.PADDING, 
            self.y + self.PADDING,
            self.PORTRAIT_SIZE,
            self.PORTRAIT_SIZE
        )
        draw_rect_with_border(self.screen, portrait_rect, BLACK, WHITE, 1)
        
        # If we have a portrait image, draw it
        if self.portrait:
            self.screen.blit(self.portrait, portrait_rect)
        else:
            # Draw placeholder silhouette
            pygame.draw.circle(
                self.screen, 
                GRAY, 
                (portrait_rect.centerx, portrait_rect.centery - 15),
                40  # Head radius
            )
            # Body
            pygame.draw.rect(
                self.screen,
                GRAY,
                pygame.Rect(
                    portrait_rect.centerx - 30,
                    portrait_rect.centery + 25,
                    60,
                    70
                ),
                border_radius=10
            )
        
        # Draw NPC name and title
        name_x = self.x + self.PADDING
        name_y = self.y + self.PADDING + self.PORTRAIT_SIZE + 10
        draw_text(
            self.screen,
            self.npc_name,
            self.title_font,
            WHITE,
            name_x,
            name_y,
            align="left"
        )
        
        if self.npc_title:
            title_y = name_y + self.title_font.get_height() + 5
            draw_text(
                self.screen,
                self.npc_title,
                self.font,
                LIGHT_GRAY,
                name_x,
                title_y,
                align="left"
            )
        
        # Draw dialog text
        text_x = self.x + self.PORTRAIT_SIZE + self.PADDING * 2
        text_y = self.y + self.PADDING
        text_width = self.PANEL_WIDTH - self.PORTRAIT_SIZE - self.PADDING * 3
        
        for i, line in enumerate(self.dialog_text):
            draw_text(
                self.screen,
                line,
                self.font,
                WHITE,
                text_x,
                text_y + i * (self.font.get_height() + 5),
                max_width=text_width,
                align="left"
            )
        
        # Draw choices if available
        if self.choices:
            self._draw_choices()
    
    def _draw_choices(self):
        """Draw dialog choices."""
        if not self.choices:
            return
            
        start_y = self.y + self.PANEL_HEIGHT - self.PADDING - len(self.choices) * (self.CHOICE_HEIGHT + self.CHOICE_SPACING)
        
        for i, choice in enumerate(self.choices):
            choice_rect = self._get_choice_rect(i)
            
            # Determine background color based on hover/selection state
            bg_color = DARK_GRAY
            if i == self.selected_choice:
                bg_color = BLUE
            elif i == self.hovered_choice:
                bg_color = GRAY
                
            # Draw choice background
            draw_rect_with_border(self.screen, choice_rect, bg_color, WHITE, 1)
            
            # Draw choice text
            text = choice.get("text", "")
            draw_text(
                self.screen,
                text,
                self.choice_font,
                WHITE,
                choice_rect.centerx,
                choice_rect.centery,
                max_width=choice_rect.width - 20,
                center=True
            )
    
    def _get_choice_rect(self, index: int) -> pygame.Rect:
        """Get the rectangle for a choice button."""
        choices_start_y = self.y + self.PANEL_HEIGHT - self.PADDING - len(self.choices) * (self.CHOICE_HEIGHT + self.CHOICE_SPACING)
        
        choice_y = choices_start_y + index * (self.CHOICE_HEIGHT + self.CHOICE_SPACING)
        choice_width = self.PANEL_WIDTH - self.PADDING * 2
        
        return pygame.Rect(
            self.x + self.PADDING,
            choice_y,
            choice_width,
            self.CHOICE_HEIGHT
        )
    
    def set_dialog_complete_callback(self, callback: Callable[[str], None]):
        """Set callback for when dialog completes."""
        self.on_dialog_complete = callback
    
    def set_clue_discovered_callback(self, callback: Callable[[str], None]):
        """Set callback for when a clue is discovered."""
        self.on_clue_discovered = callback
    
    def set_flag_set_callback(self, callback: Callable[[str], None]):
        """Set callback for when a flag is set."""
        self.on_flag_set = callback
    
    def set_choice_selected_callback(self, callback: Callable[[str, int, str], None]):
        """Set callback for when a choice is selected."""
        self.on_choice_selected = callback
    
    def load_portrait(self, portrait_path: str) -> bool:
        """Load a portrait image for the current NPC."""
        try:
            self.portrait = pygame.image.load(portrait_path)
            self.portrait = pygame.transform.scale(self.portrait, (self.PORTRAIT_SIZE, self.PORTRAIT_SIZE))
            return True
        except Exception as e:
            print(f"Error loading portrait from {portrait_path}: {e}")
            self.portrait = None
            return False
    
    def hide(self):
        """Hide the dialog UI."""
        self.visible = False
    
    def show(self):
        """Show the dialog UI."""
        self.visible = True 