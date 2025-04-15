"""
System menu UI component for RPG games.
"""

import pygame
from typing import Callable, Dict, List, Tuple, Optional
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT
)

class SystemMenuUI:
    """A reusable system menu UI component for pygame games."""
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the system menu UI.
        
        Args:
            screen: The pygame surface to draw on
        """
        self.screen = screen
        self.visible = False
        
        # Calculate dimensions
        self.width = 400
        self.height = 500  # Increased height to accommodate settings
        
        # Position in center of screen
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Create the main rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, FONT_SIZES['large'])
        self.font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.settings_font = pygame.font.Font(None, FONT_SIZES['small'])
        
        # Menu options
        self.options = [
            "Resume Game",
            "Save Game",
            "Load Game",
            "New Game",
            "Quit Game"
        ]
        
        # Game settings
        self.difficulty_levels = ["Easy", "Medium", "Hard"]
        self.current_difficulty = 1  # Default to Medium (index 1)
        
        # Button rects
        self.button_height = 50
        self.button_spacing = 10
        self.buttons = []
        
        # Settings controls
        self.settings_section_y = 0  # Will be calculated in _create_buttons
        self.difficulty_label_rect = None
        self.difficulty_decrease_rect = None
        self.difficulty_value_rect = None
        self.difficulty_increase_rect = None
        
        # Set up button callbacks
        self.callbacks = {option: None for option in self.options}
        
        # Hovered and selected options
        self.hovered_option = None
        self.selected_option = None
        
        # Create button rects
        self._create_buttons()
        
        # Update settings from current game settings
        self._sync_with_game_settings()
        
    def _sync_with_game_settings(self):
        """Synchronize UI with current game settings."""
        try:
            from ..core.settings import GameSettings
            settings = GameSettings.instance()
            self.current_difficulty = settings.difficulty_level - 1  # Convert 1-based to 0-based
        except (ImportError, AttributeError):
            # Default if settings not available
            self.current_difficulty = 1  # Medium
        
    def _create_buttons(self):
        """Create button rectangles for each menu option."""
        self.buttons = []
        button_y = self.y + 80  # Start below title
        button_width = self.width - 40  # Margin on each side
        button_x = self.x + 20
        
        for option in self.options:
            button_rect = pygame.Rect(button_x, button_y, button_width, self.button_height)
            self.buttons.append(button_rect)
            button_y += self.button_height + self.button_spacing
        
        # Calculate settings section position
        self.settings_section_y = button_y + 20
        
        # Create difficulty setting controls
        label_width = 120
        control_width = 30
        value_width = 80
        control_height = 30
        
        # Label rect
        self.difficulty_label_rect = pygame.Rect(
            button_x, self.settings_section_y, 
            label_width, control_height
        )
        
        # Decrease button (-) rect
        self.difficulty_decrease_rect = pygame.Rect(
            button_x + label_width + 10, self.settings_section_y,
            control_width, control_height
        )
        
        # Value display rect
        self.difficulty_value_rect = pygame.Rect(
            button_x + label_width + control_width + 20, self.settings_section_y,
            value_width, control_height
        )
        
        # Increase button (+) rect
        self.difficulty_increase_rect = pygame.Rect(
            button_x + label_width + control_width + value_width + 30, self.settings_section_y,
            control_width, control_height
        )
            
    def set_callback(self, option: str, callback: Callable[[], None]):
        """Set callback function for a menu option."""
        if option in self.callbacks:
            self.callbacks[option] = callback
            
    def toggle(self):
        """Toggle the visibility of the menu."""
        self.visible = not self.visible
        # Reset selection state when toggling
        if self.visible:
            self._sync_with_game_settings()
            self.hovered_option = None
            self.selected_option = None
            
            # Position any connected UI elements
            try:
                # Get game_state reference from main module
                import sys
                if 'game' in sys.modules:
                    main_module = sys.modules['game']
                    if hasattr(main_module, 'game_state') and main_module.game_state:
                        # Position character select UI to the right of system menu
                        if hasattr(main_module.game_state, 'character_select_ui'):
                            char_select = main_module.game_state.character_select_ui
                            # Position to the right of the system menu with a small gap
                            char_select.set_position(self.x + self.width + 20, self.y)
                            print("Character select UI positioned to the right of system menu")
            except Exception as e:
                print(f"Error positioning character select UI: {e}")
                
            # Try global_game_state if available
            try:
                from __main__ import global_game_state
                if global_game_state and hasattr(global_game_state, 'character_select_ui'):
                    # Position character select UI to the right of system menu
                    char_select = global_game_state.character_select_ui
                    char_select.set_position(self.x + self.width + 20, self.y)
            except (ImportError, AttributeError):
                pass
            
    def hide(self):
        """Hide the system menu."""
        self.visible = False
        
    def _change_difficulty(self, increment):
        """Change difficulty level by the given increment."""
        new_difficulty = max(0, min(len(self.difficulty_levels) - 1, self.current_difficulty + increment))
        if new_difficulty != self.current_difficulty:
            self.current_difficulty = new_difficulty
            # Update game settings
            try:
                from ..core.settings import GameSettings
                # Convert 0-based index to 1-based difficulty level
                GameSettings.instance().adjust_difficulty(self.current_difficulty + 1)
                print(f"Difficulty changed to {self.difficulty_levels[self.current_difficulty]}")
            except (ImportError, AttributeError) as e:
                print(f"Error updating game settings: {e}")
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if clicked on a button
            for i, button in enumerate(self.buttons):
                if button.collidepoint(mouse_pos):
                    option = self.options[i]
                    self.selected_option = option
                    
                    # Call the callback if available
                    if self.callbacks[option]:
                        self.callbacks[option]()
                    
                    return True
            
            # Check if clicked on difficulty controls
            if self.difficulty_decrease_rect and self.difficulty_decrease_rect.collidepoint(mouse_pos):
                self._change_difficulty(-1)  # Decrease difficulty
                return True
                
            if self.difficulty_increase_rect and self.difficulty_increase_rect.collidepoint(mouse_pos):
                self._change_difficulty(1)   # Increase difficulty
                return True
                    
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if mouse is over a button
            self.hovered_option = None
            for i, button in enumerate(self.buttons):
                if button.collidepoint(mouse_pos):
                    self.hovered_option = self.options[i]
                    break
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Toggle off menu with escape key
                self.toggle()
                return True
                
        return False
        
    def update(self):
        """Update the system menu UI."""
        pass  # No animation or state changes needed yet
        
    def draw(self, screen: pygame.Surface):
        """Draw the system menu UI."""
        if not self.visible:
            return
            
        # Update position if needed
        self.rect.topleft = (self.x, self.y)
        self._create_buttons()  # Recreate buttons to match position
        
        # Semi-transparent dark overlay for entire screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw menu background
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw title
        title = self.title_font.render("System Menu", True, UI_COLORS['text'])
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 20))
        
        # Draw buttons
        for i, button in enumerate(self.buttons):
            option = self.options[i]
            
            # Determine button color
            if option == self.selected_option:
                button_color = (100, 100, 200)  # Selected color
            elif option == self.hovered_option:
                button_color = (80, 80, 150)    # Hover color
            else:
                button_color = (50, 50, 80)     # Default color
                
            # Draw button
            pygame.draw.rect(screen, button_color, button, border_radius=5)
            pygame.draw.rect(screen, UI_COLORS['border'], button, 2, border_radius=5)
            
            # Draw option text
            text = self.font.render(option, True, UI_COLORS['text'])
            text_x = button.x + (button.width - text.get_width()) // 2
            text_y = button.y + (button.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))
        
        # Draw settings section header
        settings_header = self.font.render("Game Settings", True, UI_COLORS['text'])
        settings_x = self.x + 20
        settings_y = self.settings_section_y - 30
        screen.blit(settings_header, (settings_x, settings_y))
        
        # Draw settings divider line
        pygame.draw.line(
            screen, 
            UI_COLORS['border'], 
            (self.x + 20, settings_y + 25), 
            (self.x + self.width - 20, settings_y + 25),
            1
        )
        
        # Draw difficulty controls
        # Label
        difficulty_label = self.settings_font.render("Difficulty:", True, UI_COLORS['text'])
        screen.blit(difficulty_label, (self.difficulty_label_rect.x, self.difficulty_label_rect.y + 5))
        
        # Decrease button (-)
        pygame.draw.rect(screen, (70, 70, 100), self.difficulty_decrease_rect, border_radius=3)
        pygame.draw.rect(screen, UI_COLORS['border'], self.difficulty_decrease_rect, 1, border_radius=3)
        minus_text = self.font.render("-", True, UI_COLORS['text'])
        minus_x = self.difficulty_decrease_rect.x + (self.difficulty_decrease_rect.width - minus_text.get_width()) // 2
        minus_y = self.difficulty_decrease_rect.y + (self.difficulty_decrease_rect.height - minus_text.get_height()) // 2
        screen.blit(minus_text, (minus_x, minus_y))
        
        # Value
        pygame.draw.rect(screen, (60, 60, 80), self.difficulty_value_rect, border_radius=3)
        pygame.draw.rect(screen, UI_COLORS['border'], self.difficulty_value_rect, 1, border_radius=3)
        difficulty_text = self.settings_font.render(self.difficulty_levels[self.current_difficulty], True, UI_COLORS['text'])
        value_x = self.difficulty_value_rect.x + (self.difficulty_value_rect.width - difficulty_text.get_width()) // 2
        value_y = self.difficulty_value_rect.y + (self.difficulty_value_rect.height - difficulty_text.get_height()) // 2
        screen.blit(difficulty_text, (value_x, value_y))
        
        # Increase button (+)
        pygame.draw.rect(screen, (70, 70, 100), self.difficulty_increase_rect, border_radius=3)
        pygame.draw.rect(screen, UI_COLORS['border'], self.difficulty_increase_rect, 1, border_radius=3)
        plus_text = self.font.render("+", True, UI_COLORS['text'])
        plus_x = self.difficulty_increase_rect.x + (self.difficulty_increase_rect.width - plus_text.get_width()) // 2
        plus_y = self.difficulty_increase_rect.y + (self.difficulty_increase_rect.height - plus_text.get_height()) // 2
        screen.blit(plus_text, (plus_x, plus_y)) 