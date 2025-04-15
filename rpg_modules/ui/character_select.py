import pygame
from typing import Callable, Dict, List, Optional
import os

# Define fallback UI colors in case constants aren't available
FALLBACK_COLORS = {
    'menu_bg': (30, 30, 40),
    'border': (80, 80, 100),
    'button': (60, 60, 80),
    'button_positive': (60, 100, 60),
    'button_negative': (100, 60, 60),
    'button_disabled': (50, 50, 50),
    'text': (220, 220, 220),
    'text_secondary': (180, 180, 180),
    'hover': (70, 70, 90),
    'selected': (90, 110, 130),
    'cell_background': (40, 40, 50)
}

try:
    from ..core.constants import (
        UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
        FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT
    )
except ImportError:
    # Use fallback values if constants can't be imported
    UI_COLORS = FALLBACK_COLORS
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

try:
    from ..savegame import get_save_files
except ImportError:
    # Define a fallback if savegame module can't be imported
    def get_save_files():
        return []

class CharacterSelectUI:
    def __init__(self, screen: pygame.Surface, on_select: Callable[[str], None], on_cancel: Callable[[], None]):
        self.screen = screen
        self.visible = True  # Make visible by default for testing
        self.width = 300  # Width of character select menu
        self.height = 400  # Height of character select menu
        
        # Default position - will be updated when SystemMenuUI positions it
        self.x = (SCREEN_WIDTH - self.width) // 2  # Center horizontally
        self.y = (SCREEN_HEIGHT - self.height) // 2  # Center vertically
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.small_font = pygame.font.Font(None, 24)
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 40)
        
        self.characters = []
        self.selected_index = -1
        self.hovered_index = -1
        self.load_callback = on_select
        self.cancel_callback = on_cancel
        
        # Scroll for character list
        self.scroll_offset = 0
        self.max_visible_characters = 4
        
        # For testing purposes, add a placeholder character
        self.character_selected = False
        self.selected_type = "warrior"
        self.selected_name = "Test Character"
        
        # Add a test character to characters list for debugging
        self.characters = [
            {
                'name': 'Test Character',
                'level': 1,
                'health': 100,
                'max_health': 100,
                'filename': 'test_character'
            }
        ]
        
        self.refresh_character_list()
        
    def update(self, dt: float):
        """Update UI state with the given delta time."""
        # No time-based updates needed for this UI currently
        pass

    def draw(self, screen: pygame.Surface):
        """Draw the character selection menu."""
        if not self.visible:
            return
            
        # Debug background to make sure we're rendering
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw menu background with border
        pygame.draw.rect(screen, UI_COLORS['menu_bg'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw title
        title = self.title_font.render("Select Character", True, UI_COLORS['text'])
        title_rect = title.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        screen.blit(title, title_rect)
        
        # Draw character list
        if not self.characters:
            # No characters found message
            no_chars = self.font.render("No saved characters found", True, UI_COLORS['text'])
            no_chars_rect = no_chars.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2 - 40))
            screen.blit(no_chars, no_chars_rect)
            
            new_game = self.small_font.render("Start a new game to create a character", True, UI_COLORS['text_secondary'])
            new_game_rect = new_game.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(new_game, new_game_rect)
        else:
            # Calculate visible range based on scroll offset
            end_idx = min(len(self.characters), self.scroll_offset + self.max_visible_characters)
            visible_characters = self.characters[self.scroll_offset:end_idx]
            
            # Draw scrollbar if needed
            if len(self.characters) > self.max_visible_characters:
                # Scrollbar background
                scrollbar_bg = pygame.Rect(self.x + self.width - 20, self.y + 70, 10, 280)
                pygame.draw.rect(screen, UI_COLORS['cell_background'], scrollbar_bg)
                
                # Scrollbar handle
                handle_height = max(30, 280 * self.max_visible_characters / len(self.characters))
                handle_pos = 280 * self.scroll_offset / (len(self.characters) - self.max_visible_characters)
                scrollbar = pygame.Rect(self.x + self.width - 20, self.y + 70 + handle_pos, 10, handle_height)
                pygame.draw.rect(screen, UI_COLORS['button'], scrollbar)
            
            # Draw character entries
            y_offset = 70
            for i, character in enumerate(visible_characters):
                list_index = i + self.scroll_offset
                # Character entry background
                entry_rect = pygame.Rect(self.x + 20, self.y + y_offset, self.width - 50, 70)
                
                if list_index == self.selected_index:
                    color = UI_COLORS['selected']
                elif list_index == self.hovered_index:
                    color = UI_COLORS['hover']
                else:
                    color = UI_COLORS['button']
                    
                pygame.draw.rect(screen, color, entry_rect)
                pygame.draw.rect(screen, UI_COLORS['border'], entry_rect, 1)
                
                # Character name
                name = self.font.render(character['name'], True, UI_COLORS['text'])
                screen.blit(name, (self.x + 30, self.y + y_offset + 10))
                
                # Character details (level, health)
                details = f"Level {character['level']} - HP: {character['health']}/{character['max_health']}"
                details_text = self.small_font.render(details, True, UI_COLORS['text_secondary'])
                screen.blit(details_text, (self.x + 30, self.y + y_offset + 40))
                
                y_offset += 80
        
        # Draw buttons
        button_y = self.y + self.height - 60
        
        # Create new character button (middle)
        new_button = pygame.Rect(self.x + (self.width - 120) // 2, button_y, 120, 40)
        pygame.draw.rect(screen, UI_COLORS['button_positive'], new_button)
        pygame.draw.rect(screen, UI_COLORS['border'], new_button, 2)
        
        new_text = self.font.render("New", True, UI_COLORS['text'])
        new_rect = new_text.get_rect(center=new_button.center)
        screen.blit(new_text, new_rect)
        
        # Load button (left)
        load_button = pygame.Rect(self.x + 20, button_y, 80, 40)
        if self.characters and self.selected_index >= 0:
            pygame.draw.rect(screen, UI_COLORS['button'], load_button)
        else:
            pygame.draw.rect(screen, UI_COLORS['button_disabled'], load_button)
        pygame.draw.rect(screen, UI_COLORS['border'], load_button, 2)
        
        load_text = self.font.render("Load", True, UI_COLORS['text'])
        load_rect = load_text.get_rect(center=load_button.center)
        screen.blit(load_text, load_rect)
        
        # Cancel button (right)
        cancel_button = pygame.Rect(self.x + self.width - 100, button_y, 80, 40)
        pygame.draw.rect(screen, UI_COLORS['button_negative'], cancel_button)
        pygame.draw.rect(screen, UI_COLORS['border'], cancel_button, 2)
        
        cancel_text = self.font.render("Exit", True, UI_COLORS['text'])
        cancel_rect = cancel_text.get_rect(center=cancel_button.center)
        screen.blit(cancel_text, cancel_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the character selection menu."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Check character entries
            self.hovered_index = -1
            
            if self.characters:
                end_idx = min(len(self.characters), self.scroll_offset + self.max_visible_characters)
                y_offset = 70
                
                for i in range(self.scroll_offset, end_idx):
                    entry_rect = pygame.Rect(self.x + 20, self.y + y_offset, self.width - 50, 70)
                    if entry_rect.collidepoint(mouse_pos):
                        self.hovered_index = i
                        return True
                    y_offset += 80
            
            # Check scrollbar
            if len(self.characters) > self.max_visible_characters:
                scrollbar_bg = pygame.Rect(self.x + self.width - 20, self.y + 70, 10, 280)
                if scrollbar_bg.collidepoint(mouse_pos):
                    # Scroll based on mouse position
                    scroll_pos = mouse_pos[1] - (self.y + 70)
                    scroll_ratio = scroll_pos / 280
                    self.scroll_offset = min(len(self.characters) - self.max_visible_characters, 
                                           max(0, int(scroll_ratio * len(self.characters))))
                    return True
            
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check character entries
                if self.characters:
                    end_idx = min(len(self.characters), self.scroll_offset + self.max_visible_characters)
                    y_offset = 70
                    
                    for i in range(self.scroll_offset, end_idx):
                        entry_rect = pygame.Rect(self.x + 20, self.y + y_offset, self.width - 50, 70)
                        if entry_rect.collidepoint(mouse_pos):
                            self.selected_index = i
                            return True
                        y_offset += 80
                
                # Check Load button
                load_button = pygame.Rect(self.x + 20, self.y + self.height - 60, 120, 40)
                if load_button.collidepoint(mouse_pos) and self.selected_index >= 0 and self.characters:
                    if self.load_callback:
                        selected_character = self.characters[self.selected_index]
                        filename = selected_character.get('filename', "")
                        self.load_callback(filename)
                    return True
                
                # Check Cancel button
                cancel_button = pygame.Rect(self.x + self.width - 140, self.y + self.height - 60, 120, 40)
                if cancel_button.collidepoint(mouse_pos):
                    if self.cancel_callback:
                        self.cancel_callback()
                    else:
                        self.hide()
                    return True
            
            # Mouse wheel for scrolling
            elif event.button == 4:  # Scroll up
                if self.characters and len(self.characters) > self.max_visible_characters:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    return True
            elif event.button == 5:  # Scroll down
                if self.characters and len(self.characters) > self.max_visible_characters:
                    self.scroll_offset = min(len(self.characters) - self.max_visible_characters, 
                                          self.scroll_offset + 1)
                    return True
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.cancel_callback:
                    self.cancel_callback()
                else:
                    self.hide()
                return True
                
            # Arrow keys for navigation
            elif event.key == pygame.K_UP:
                if self.characters:
                    self.selected_index = max(0, self.selected_index - 1)
                    # Adjust scroll if needed
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                    return True
            elif event.key == pygame.K_DOWN:
                if self.characters:
                    self.selected_index = min(len(self.characters) - 1, self.selected_index + 1)
                    # Adjust scroll if needed
                    if self.selected_index >= self.scroll_offset + self.max_visible_characters:
                        self.scroll_offset = self.selected_index - self.max_visible_characters + 1
                    return True
            elif event.key == pygame.K_RETURN:
                if self.selected_index >= 0 and self.characters:
                    if self.load_callback:
                        selected_character = self.characters[self.selected_index]
                        filename = selected_character.get('filename', "")
                        self.load_callback(filename)
                    return True
                
        return True  # Consume the event to prevent it from going to other UI components
        
    def show(self):
        """Show the character selection menu."""
        self.visible = True
        self.refresh_character_list()
        self.selected_index = 0 if self.characters else -1
        self.hovered_index = -1
        self.scroll_offset = 0
        
    def hide(self):
        """Hide the character selection menu."""
        self.visible = False
        
    def set_position(self, x, y):
        """Set the position of the character select menu."""
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def refresh_character_list(self):
        """Refresh the list of available character save files."""
        self.characters = get_save_files()
        
        # Reset selection if no characters available
        if not self.characters:
            self.selected_index = -1
        elif self.selected_index < 0 and self.characters:
            # Default to first character if none selected
            self.selected_index = 0
        
        # Ensure selection is within bounds if characters were removed
        if self.characters and self.selected_index >= len(self.characters):
            self.selected_index = len(self.characters) - 1
        
        # Reset scroll to show selection
        if self.selected_index >= 0:
            self.scroll_offset = max(0, min(
                self.selected_index, 
                len(self.characters) - self.max_visible_characters
            ))
        else:
            self.scroll_offset = 0 

class NameInputDialog:
    """Dialog for entering a new hero name when starting a new game."""
    
    def __init__(self, screen: pygame.Surface, on_confirm: Callable[[str], None], on_cancel: Callable[[], None]):
        self.screen = screen
        self.visible = False
        self.width = 400
        self.height = 200
        
        # Center on screen
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 40)
        
        self.confirm_callback = on_confirm
        self.cancel_callback = on_cancel
        
        # Text input
        self.name_input = "Hero"  # Default value
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Input field rect
        self.input_rect = pygame.Rect(
            self.x + 50, 
            self.y + 80, 
            self.width - 100, 
            40
        )
        
        # Button rects
        self.confirm_button = pygame.Rect(
            self.x + 50,
            self.y + self.height - 60,
            120,
            40
        )
        
        self.cancel_button = pygame.Rect(
            self.x + self.width - 170,
            self.y + self.height - 60,
            120,
            40
        )
    
    def show(self):
        """Show the name input dialog."""
        self.visible = True
        self.active = True
        
    def hide(self):
        """Hide the name input dialog."""
        self.visible = False
        self.active = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the dialog."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check if clicked on input field
            if self.input_rect.collidepoint(mouse_pos):
                self.active = True
                return True
                
            # Check confirm button
            elif self.confirm_button.collidepoint(mouse_pos):
                if self.name_input.strip():  # Ensure name is not empty
                    self.confirm_callback(self.name_input)
                return True
                
            # Check cancel button
            elif self.cancel_button.collidepoint(mouse_pos):
                self.cancel_callback()
                return True
                
            else:
                self.active = False
        
        elif event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    if self.name_input.strip():  # Ensure name is not empty
                        self.confirm_callback(self.name_input)
                    return True
                    
                elif event.key == pygame.K_ESCAPE:
                    self.cancel_callback()
                    return True
                    
                elif event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                    return True
                    
                else:
                    # Only add valid characters - letters, numbers, and some symbols
                    if event.unicode.isalnum() or event.unicode in " -_'":
                        # Limit name length to reasonable size
                        if len(self.name_input) < 20:
                            self.name_input += event.unicode
                    return True
                    
        return True
    
    def update(self, dt):
        """Update the dialog state."""
        if not self.visible:
            return
            
        # Blink cursor every 500ms
        self.cursor_timer += dt * 1000
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the dialog."""
        if not self.visible:
            return
            
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay with alpha
        screen.blit(overlay, (0, 0))
        
        # Dialog background
        pygame.draw.rect(screen, UI_COLORS['menu_bg'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Title
        title = self.title_font.render("Enter Hero Name", True, UI_COLORS['text'])
        title_rect = title.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        screen.blit(title, title_rect)
        
        # Input field
        pygame.draw.rect(screen, UI_COLORS['cell_background'], self.input_rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.input_rect, 2)
        
        # Input text
        text_surface = self.font.render(self.name_input, True, UI_COLORS['text'])
        
        # Add cursor if active
        display_text = self.name_input
        if self.active and self.cursor_visible:
            display_text += "|"
            
        text_surface = self.font.render(display_text, True, UI_COLORS['text'])
        screen.blit(text_surface, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        # Confirm button
        pygame.draw.rect(screen, UI_COLORS['button_positive'], self.confirm_button)
        pygame.draw.rect(screen, UI_COLORS['border'], self.confirm_button, 2)
        
        confirm_text = self.font.render("Confirm", True, UI_COLORS['text'])
        confirm_rect = confirm_text.get_rect(center=self.confirm_button.center)
        screen.blit(confirm_text, confirm_rect)
        
        # Cancel button
        pygame.draw.rect(screen, UI_COLORS['button_negative'], self.cancel_button)
        pygame.draw.rect(screen, UI_COLORS['border'], self.cancel_button, 2)
        
        cancel_text = self.font.render("Cancel", True, UI_COLORS['text'])
        cancel_rect = cancel_text.get_rect(center=self.cancel_button.center)
        screen.blit(cancel_text, cancel_rect) 