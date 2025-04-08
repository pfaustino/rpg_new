import pygame
import sys
from rpg_modules.animations import MonsterIcon

# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
GRID_COLS = 4
GRID_ROWS = 4
ICON_SIZE = 100
PADDING = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Monster Icon Test")

# List of monster types to display
monster_types = [
    # Original monsters
    "dragon", "spider", "ghost", "skeleton", "slime",
    # Psychic Anomalies
    "thought_devourer", "memory_phantom", "psychic_hydra", "mind_colossus",
    # Elemental creatures
    "fire_elemental", "ice_elemental", "storm_elemental", "earth_golem",
    # Undead
    "zombie", "wraith", "vampire", "lich"
]

# Create monster icons
monster_icons = {monster_type: MonsterIcon(monster_type) for monster_type in monster_types}

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_grid():
    """Draw the grid of monster icons."""
    screen.fill(GRAY)
    
    for i, monster_type in enumerate(monster_types):
        row = i // GRID_COLS
        col = i % GRID_COLS
        
        # Calculate position
        x = col * (ICON_SIZE + PADDING) + PADDING
        y = row * (ICON_SIZE + PADDING) + PADDING
        
        # Create surface for icon
        icon_surface = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
        
        # Draw icon
        monster_icons[monster_type].render(icon_surface, ICON_SIZE)
        
        # Draw icon to screen
        screen.blit(icon_surface, (x, y))
        
        # Draw monster type name
        font = pygame.font.Font(None, 24)
        text = font.render(monster_type.replace('_', ' ').title(), True, WHITE)
        text_rect = text.get_rect(center=(x + ICON_SIZE//2, y + ICON_SIZE + 15))
        screen.blit(text, text_rect)

def main():
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update icons
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        for icon in monster_icons.values():
            icon.update(dt)
        
        # Draw everything
        draw_grid()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 