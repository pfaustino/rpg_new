import pygame
from typing import Callable, Dict, List, Optional
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT
)
from ..savegame import get_save_files

class CharacterSelectUI:
    def __init__(self, screen: pygame.Surface, on_select: Callable[[str], None], on_cancel: Callable[[], None]):
        self.screen = screen
        self.visible = False
        self.width = 350  # Match system menu width
        self.height = 450
        
        # Default position - will be updated when SystemMenuUI positions it
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT // 2 - self.height // 2
        
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
        
        self.refresh_character_list()

    def draw(self, screen: pygame.Surface):
        """Draw the character selection menu."""
        if not self.visible:
            return
        
        # Draw semi-transparent background overlay for the whole screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
            
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
                pygame.draw.rect(screen, (30, 30, 30), scrollbar_bg)
                
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
        
        # Load button
        load_button = pygame.Rect(self.x + 20, button_y, 120, 40)
        if self.characters and self.selected_index >= 0:
            pygame.draw.rect(screen, UI_COLORS['button_positive'], load_button)
        else:
            pygame.draw.rect(screen, UI_COLORS['button_disabled'], load_button)
        pygame.draw.rect(screen, UI_COLORS['border'], load_button, 2)
        
        load_text = self.font.render("Load", True, UI_COLORS['text'])
        load_rect = load_text.get_rect(center=load_button.center)
        screen.blit(load_text, load_rect)
        
        # Cancel button
        cancel_button = pygame.Rect(self.x + self.width - 140, button_y, 120, 40)
        pygame.draw.rect(screen, UI_COLORS['button_negative'], cancel_button)
        pygame.draw.rect(screen, UI_COLORS['border'], cancel_button, 2)
        
        cancel_text = self.font.render("Cancel", True, UI_COLORS['text'])
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
        """Refresh the character list."""
        self.characters = get_save_files() 