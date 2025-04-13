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
        self.height = 350
        
        # Position in center of screen
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Create the main rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, FONT_SIZES['large'])
        self.font = pygame.font.Font(None, FONT_SIZES['medium'])
        
        # Menu options
        self.options = [
            "Resume Game",
            "Save Game",
            "Load Game",
            "New Game",
            "Quit Game"
        ]
        
        # Button rects
        self.button_height = 50
        self.button_spacing = 10
        self.buttons = []
        
        # Set up button callbacks
        self.callbacks = {option: None for option in self.options}
        
        # Hovered and selected options
        self.hovered_option = None
        self.selected_option = None
        
        # Create button rects
        self._create_buttons()
        
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
            
    def set_callback(self, option: str, callback: Callable[[], None]):
        """Set callback function for a menu option."""
        if option in self.callbacks:
            self.callbacks[option] = callback
            
    def toggle(self):
        """Toggle visibility of the system menu."""
        self.visible = not self.visible
        # Reset selection state when toggling
        if self.visible:
            self.hovered_option = None
            self.selected_option = None
            
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