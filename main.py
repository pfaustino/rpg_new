"""
Main entry point for the RPG game.
"""

import pygame
import sys
import os

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Veilmaster's Fortress"

# Define fallback UI colors
UI_COLORS = {
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

def draw_text(screen, text, font, color, x, y, align="center", center=False, max_width=None):
    """Helper function to draw text with alignment options."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center" or center:
        text_rect.centerx = x
    elif align == "right":
        text_rect.right = x
    else:  # left
        text_rect.left = x
        
    if center:
        text_rect.centery = y
    else:
        text_rect.top = y
        
    screen.blit(text_surface, text_rect)

def draw_rect_with_border(screen, rect, color, border_color, border_width):
    """Helper function to draw a rectangle with a border."""
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, border_color, rect, border_width)

class SimpleCharacterSelect:
    """A simplified character select UI for debugging."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 40)
        self.visible = True
        
    def update(self, dt):
        """Update the UI."""
        pass
        
    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.KEYDOWN:
            # Press any key to exit
            return True
        return False
        
    def draw(self):
        """Draw the UI."""
        if not self.visible:
            return
            
        # Clear the screen with black
        self.screen.fill((0, 0, 0))
        
        # Draw title
        title = self.title_font.render(GAME_TITLE, True, UI_COLORS['text'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw character selection UI
        ui_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 100,
            300,
            200
        )
        draw_rect_with_border(
            self.screen,
            ui_rect,
            UI_COLORS['menu_bg'],
            UI_COLORS['border'],
            2
        )
        
        # Draw text
        draw_text(
            self.screen,
            "Character Selection",
            self.font,
            UI_COLORS['text'],
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 80,
            center=True
        )
        
        # Draw test character option
        character_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 120,
            SCREEN_HEIGHT // 2 - 30,
            240,
            50
        )
        draw_rect_with_border(
            self.screen,
            character_rect,
            UI_COLORS['button'],
            UI_COLORS['border'],
            2
        )
        
        draw_text(
            self.screen,
            "Test Character",
            self.font,
            UI_COLORS['text'],
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 15,
            center=True
        )
        
        # Draw instructions
        draw_text(
            self.screen,
            "Press any key to start",
            self.font,
            UI_COLORS['text_secondary'],
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            center=True
        )

def main():
    """Main entry point for the game."""
    # Initialize pygame
    pygame.init()
    
    # Setup screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    
    # Setup clock
    clock = pygame.time.Clock()
    
    # Create UI
    character_select = SimpleCharacterSelect(screen)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to UI
            if character_select.visible and character_select.handle_event(event):
                # When character is selected, display a basic game screen
                character_select.visible = False
            
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Update and draw UI
        if character_select.visible:
            character_select.update(dt)
            character_select.draw()
        else:
            # Draw a basic game screen when character is selected
            # Draw background
            screen.fill((20, 40, 60))
            
            # Draw player placeholder
            pygame.draw.circle(screen, (255, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 20)
            
            # Draw text
            font = pygame.font.Font(None, 32)
            text_surface = font.render("Game Started - Press ESC to exit", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(text_surface, text_rect)
            
            # Check for ESC key to exit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                running = False
        
        # Update display
        pygame.display.flip()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/quests", exist_ok=True)
    os.makedirs("data/quests/dialogs", exist_ok=True)
    
    # Start the game
    main() 