import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("RPG Game - Test")

# Create a simple game state class with the refresh_inventory_ui method
class GameState:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.paused = False
        print("Game state initialized")
        
    def refresh_inventory_ui(self):
        """Update the inventory UI to reflect current inventory state."""
        print("Inventory UI refreshed")
        
    def update(self, dt):
        # Basic update logic
        pass
        
    def draw(self):
        # Fill screen with black
        self.screen.fill((0, 0, 0))
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render("Game is running with refresh_inventory_ui method", True, (255, 255, 255))
        self.screen.blit(text, (100, 250))

# Create game state
game_state = GameState(screen)

# Main game loop
clock = pygame.time.Clock()
while game_state.running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state.running = False
            elif event.key == pygame.K_r:
                # Test the refresh method
                game_state.refresh_inventory_ui()
                
    # Update game state
    dt = clock.tick(60) / 1000.0
    game_state.update(dt)
    
    # Draw everything
    game_state.draw()
    pygame.display.flip()

# Clean up
pygame.quit()
print("Game exited cleanly")
sys.exit(0) 