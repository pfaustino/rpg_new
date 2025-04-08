"""
Asset loading and management for the RPG game.
"""

import os
import pygame
from typing import Dict
from .constants import TILE_SIZE

def load_assets() -> Dict[str, pygame.Surface]:
    """Load all game assets."""
    assets = {}
    
    # Create basic colored tiles if image assets don't exist
    wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_surface.fill((100, 100, 100))  # Gray for walls
    pygame.draw.rect(wall_surface, (80, 80, 80), 
                    (1, 1, TILE_SIZE-2, TILE_SIZE-2))  # Darker border
    assets['wall'] = wall_surface
    
    floor_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    floor_surface.fill((50, 30, 20))  # Brown for floor
    pygame.draw.rect(floor_surface, (60, 40, 30), 
                    (1, 1, TILE_SIZE-2, TILE_SIZE-2))  # Lighter border
    assets['floor'] = floor_surface
    
    # Create player sprite
    player_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    player_surface.fill((0, 0, 255))  # Blue for player
    pygame.draw.circle(player_surface, (0, 0, 200),
                      (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//3)
    assets['player'] = player_surface
    
    # Create monster sprites
    monster_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    monster_surface.fill((255, 0, 0))  # Red for monsters
    pygame.draw.circle(monster_surface, (200, 0, 0),
                      (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//3)
    assets['monster'] = monster_surface
    
    # Create UI elements
    ui_button = pygame.Surface((100, 30))
    ui_button.fill((80, 80, 80))
    pygame.draw.rect(ui_button, (100, 100, 100),
                    (1, 1, 98, 28))
    assets['ui_button'] = ui_button
    
    ui_panel = pygame.Surface((200, 300))
    ui_panel.fill((60, 60, 60))
    pygame.draw.rect(ui_panel, (80, 80, 80),
                    (1, 1, 198, 298))
    assets['ui_panel'] = ui_panel
    
    # Create item sprites
    item_surface = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2))
    item_surface.fill((255, 255, 0))  # Yellow for items
    pygame.draw.rect(item_surface, (200, 200, 0),
                    (1, 1, TILE_SIZE//2-2, TILE_SIZE//2-2))
    assets['item'] = item_surface
    
    return assets 