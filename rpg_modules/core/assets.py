"""
Asset loading and management for the RPG game.
"""

import os
import pygame
from typing import Dict
from .constants import TILE_SIZE
from .map import TileType
import random
import math

def load_assets() -> Dict[str, pygame.Surface]:
    """Load all game assets."""
    assets = {}
    
    # First attempt to load tile textures from files
    load_tile_textures(assets)
    
    # Define base colors for different tile types (used as fallback)
    TILE_COLORS = {
        # Base tiles
        TileType.GRASS: (34, 139, 34),    # Forest green
        TileType.DIRT: (139, 69, 19),     # Saddle brown
        TileType.SAND: (238, 214, 175),   # Tan
        TileType.WATER: (0, 105, 148),    # Deep blue
        TileType.STONE: (128, 128, 128),  # Gray
        # Decorative tiles
        TileType.FLOWER: (255, 192, 203), # Pink
        TileType.TREE: (0, 100, 0),       # Dark green
        TileType.BUSH: (0, 120, 0),       # Medium green
        TileType.ROCK: (169, 169, 169),   # Dark gray
        TileType.REED: (205, 133, 63),    # Peru brown
        # Structure tiles
        TileType.STONE_WALL: (90, 90, 90),  # Dark gray for stone walls
    }
    
    # Create procedural surfaces for any missing tile type
    for tile_type in TileType:
        # Skip if already loaded from file
        if tile_type.value in assets:
            continue
            
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        color = TILE_COLORS.get(tile_type, (128, 128, 128))  # Default to gray
        surface.fill(color)
        
        # Add texture/pattern based on tile type
        if tile_type == TileType.GRASS:
            # Add grass texture with small random dots
            for _ in range(10):
                x = random.randint(0, TILE_SIZE-2)
                y = random.randint(0, TILE_SIZE-2)
                pygame.draw.circle(surface, (45, 160, 45), (x, y), 1)
        
        elif tile_type == TileType.WATER:
            # Add water ripple effect
            for i in range(3):
                y = TILE_SIZE // 4 + i * (TILE_SIZE // 4)
                pygame.draw.line(surface, (0, 120, 160), (0, y), (TILE_SIZE, y), 1)
        
        elif tile_type == TileType.SAND:
            # Create a more distinctive sand texture
            surface.fill((255, 223, 128))  # Brighter yellow/tan color
            # Add sand texture with tiny dots and patterns
            for _ in range(30):  # More dots for more texture
                x = random.randint(0, TILE_SIZE-1)
                y = random.randint(0, TILE_SIZE-1)
                # Vary the dot colors for a more sandy appearance
                dot_color = (
                    random.randint(220, 255), 
                    random.randint(200, 223), 
                    random.randint(100, 150)
                )
                pygame.draw.circle(surface, dot_color, (x, y), random.randint(1, 2))
            
            # Add some sand ripple lines
            for i in range(2):
                y = TILE_SIZE // 3 + i * (TILE_SIZE // 3)
                wave_points = []
                for x in range(0, TILE_SIZE, 4):
                    offset = math.sin(x * 0.2) * 2
                    wave_points.append((x, y + offset))
                if len(wave_points) > 1:
                    pygame.draw.lines(surface, (220, 190, 100), False, wave_points, 1)
        
        elif tile_type == TileType.STONE:
            # Create a more distinctive stone texture
            base_color = (120, 120, 120)  # Medium gray
            surface.fill(base_color)
            
            # Add stone texture with varied gray shades for a rocky appearance
            for _ in range(20):
                x = random.randint(0, TILE_SIZE-1)
                y = random.randint(0, TILE_SIZE-1)
                size = random.randint(2, 5)
                shade = random.randint(100, 150)
                stone_color = (shade, shade, shade)
                pygame.draw.circle(surface, stone_color, (x, y), size)
            
            # Add cracks for more stone-like appearance
            for _ in range(3):
                start_x = random.randint(0, TILE_SIZE)
                start_y = random.randint(0, TILE_SIZE)
                end_x = start_x + random.randint(-10, 10)
                end_y = start_y + random.randint(-10, 10)
                pygame.draw.line(surface, (90, 90, 90), (start_x, start_y), (end_x, end_y), 1)
        
        elif tile_type == TileType.DIRT:
            # Enhance dirt texture
            surface.fill((139, 69, 19))  # Brown
            # Add dirt specks
            for _ in range(20):
                x = random.randint(0, TILE_SIZE-1)
                y = random.randint(0, TILE_SIZE-1)
                size = random.randint(1, 3)
                # Vary between lighter and darker browns
                if random.random() < 0.5:
                    speck_color = (160, 82, 45)  # Lighter brown
                else:
                    speck_color = (101, 67, 33)  # Darker brown
                pygame.draw.circle(surface, speck_color, (x, y), size)
        
        elif tile_type == TileType.FLOWER:
            # Draw a simple flower
            center = (TILE_SIZE//2, TILE_SIZE//2)
            pygame.draw.circle(surface, (255, 255, 0), center, 3)  # Center
            for angle in range(0, 360, 72):  # 5 petals
                x = center[0] + int(math.cos(math.radians(angle)) * 5)
                y = center[1] + int(math.sin(math.radians(angle)) * 5)
                pygame.draw.circle(surface, (255, 192, 203), (x, y), 3)
        
        elif tile_type == TileType.TREE:
            # Draw a simple tree
            trunk_color = (139, 69, 19)  # Brown
            leaves_color = (0, 100, 0)   # Dark green
            # Trunk
            pygame.draw.rect(surface, trunk_color, 
                           (TILE_SIZE//2 - 2, TILE_SIZE//2, 4, TILE_SIZE//2))
            # Leaves
            pygame.draw.circle(surface, leaves_color, 
                             (TILE_SIZE//2, TILE_SIZE//3), TILE_SIZE//3)
        
        elif tile_type == TileType.BUSH:
            # Draw a simple bush
            for _ in range(5):
                x = random.randint(TILE_SIZE//4, 3*TILE_SIZE//4)
                y = random.randint(TILE_SIZE//4, 3*TILE_SIZE//4)
                pygame.draw.circle(surface, (0, 120, 0), (x, y), TILE_SIZE//6)
        
        elif tile_type == TileType.ROCK:
            # Draw a rock with some shading
            points = [
                (TILE_SIZE//4, 3*TILE_SIZE//4),
                (TILE_SIZE//4, TILE_SIZE//2),
                (TILE_SIZE//2, TILE_SIZE//4),
                (3*TILE_SIZE//4, TILE_SIZE//2),
                (3*TILE_SIZE//4, 3*TILE_SIZE//4)
            ]
            pygame.draw.polygon(surface, (169, 169, 169), points)
            # Add highlight
            pygame.draw.line(surface, (192, 192, 192),
                           points[1], points[2], 2)
        
        elif tile_type == TileType.REED:
            # Draw some reeds
            for i in range(3):
                x = TILE_SIZE//4 + i * (TILE_SIZE//4)
                pygame.draw.line(surface, (205, 133, 63),
                               (x, TILE_SIZE), (x, TILE_SIZE//3), 2)
                # Add reed head
                pygame.draw.ellipse(surface, (139, 69, 19),
                                  (x-2, TILE_SIZE//3-4, 4, 8))
        
        elif tile_type == TileType.STONE_WALL:
            # Create a stone wall texture with bricks
            wall_base_color = (90, 90, 90)  # Dark gray base
            surface.fill(wall_base_color)
            
            # Draw brick pattern
            brick_color = (70, 70, 70)  # Slightly darker for contrast
            highlight_color = (120, 120, 120)  # Lighter for top/side highlights
            
            # Brick dimensions
            brick_height = 6
            brick_rows = TILE_SIZE // brick_height
            
            # Draw brick rows with alternating offsets
            for row in range(brick_rows):
                offset = 0 if row % 2 == 0 else TILE_SIZE // 4
                y = row * brick_height
                
                # Draw horizontal mortar line
                pygame.draw.line(surface, (130, 130, 130), 
                               (0, y), (TILE_SIZE, y), 1)
                
                # Draw bricks in this row
                for brick_start in range(offset, TILE_SIZE, TILE_SIZE // 2):
                    # Draw brick
                    brick_width = min(TILE_SIZE // 2 - 2, TILE_SIZE - brick_start)
                    brick_rect = pygame.Rect(brick_start, y + 1, brick_width, brick_height - 1)
                    pygame.draw.rect(surface, brick_color, brick_rect)
                    
                    # Draw highlight on top/left edges
                    pygame.draw.line(surface, highlight_color, 
                                   (brick_start, y + 1), 
                                   (brick_start + brick_width, y + 1), 1)
                    pygame.draw.line(surface, highlight_color, 
                                   (brick_start, y + 1), 
                                   (brick_start, y + brick_height - 1), 1)
        
        assets[tile_type.value] = surface
    
    # Load or create other required assets
    wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_surface.fill((100, 100, 100))  # Gray for walls
    pygame.draw.rect(wall_surface, (80, 80, 80),  # Darker border
                    (0, 0, TILE_SIZE, TILE_SIZE), 2)
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

def load_tile_textures(assets: Dict[str, pygame.Surface]) -> None:
    """Load tile textures from files."""
    print("\n" + "="*50)
    print("LOADING TILE TEXTURES")
    print("Current working directory:", os.getcwd())
    print("="*50 + "\n")
    
    # Check for grass texture
    grass_texture_path = os.path.join('assets', 'images', 'tiles', 'tile_floor_grass.png')
    print(f"Looking for grass texture at: {os.path.abspath(grass_texture_path)}")
    if os.path.exists(grass_texture_path):
        try:
            print(f"FOUND! Loading grass texture from: {grass_texture_path}")
            grass_surface = pygame.image.load(grass_texture_path).convert_alpha()
            assets[TileType.GRASS.value] = grass_surface
            print(f"Successfully loaded grass texture, size: {grass_surface.get_size()}")
        except Exception as e:
            print(f"ERROR loading grass texture: {e}")
    else:
        print(f"Grass texture file NOT FOUND at: {grass_texture_path}")
        print("Available files in assets directory:")
        try:
            base_path = os.path.join('assets', 'images', 'tiles')
            if os.path.exists(base_path):
                for file in os.listdir(base_path):
                    print(f"  - {file}")
            else:
                print(f"  Directory {base_path} does not exist")
        except Exception as e:
            print(f"  Error listing directory: {e}")
    
    # Check for flower texture 
    print("\nLooking for flower textures in assets directory:")
    base_path = os.path.join('assets', 'images', 'tiles')
    if os.path.exists(base_path):
        print("Files in tiles directory:")
        for file in os.listdir(base_path):
            print(f"  - {file}")
    
    # Try multiple possible flower file names
    flower_file_found = False
    
    # First try: tile_deco_flower.png
    flower_texture_path = os.path.join('assets', 'images', 'tiles', 'tile_deco_flower.png')
    print(f"\nTrying to load flower texture from: {os.path.abspath(flower_texture_path)}")
    if os.path.exists(flower_texture_path):
        try:
            print(f"FOUND! Loading flower texture from: {flower_texture_path}")
            flower_surface = pygame.image.load(flower_texture_path).convert_alpha()
            # Scale the flower image to the expected tile size
            original_size = flower_surface.get_size()
            print(f"Original flower texture size: {original_size}")
            scaled_flower = pygame.transform.scale(flower_surface, (TILE_SIZE, TILE_SIZE))
            assets[TileType.FLOWER.value] = scaled_flower
            print(f"Successfully loaded and scaled flower texture to {TILE_SIZE}x{TILE_SIZE}")
            flower_file_found = True
        except Exception as e:
            print(f"ERROR loading flower texture: {e}")
    else:
        print(f"Flower texture file NOT FOUND at: {flower_texture_path}")
    
    # Second try: tile_floor_grass_flowers.png
    if not flower_file_found:
        flower_texture_path = os.path.join('assets', 'images', 'tiles', 'tile_floor_grass_flowers.png')
        print(f"\nTrying alternate file: {os.path.abspath(flower_texture_path)}")
        if os.path.exists(flower_texture_path):
            try:
                print(f"FOUND! Loading flower texture from: {flower_texture_path}")
                flower_surface = pygame.image.load(flower_texture_path).convert_alpha()
                # Scale the flower image to the expected tile size
                original_size = flower_surface.get_size()
                print(f"Original flower texture size: {original_size}")
                scaled_flower = pygame.transform.scale(flower_surface, (TILE_SIZE, TILE_SIZE))
                assets[TileType.FLOWER.value] = scaled_flower
                print(f"Successfully loaded and scaled flower texture to {TILE_SIZE}x{TILE_SIZE}")
                flower_file_found = True
            except Exception as e:
                print(f"ERROR loading flower texture: {e}")
        else:
            print(f"Alternate flower texture file NOT FOUND at: {flower_texture_path}")
    
    # Third try: tile_flower.png
    if not flower_file_found:
        alt_flower_path = os.path.join('assets', 'images', 'tiles', 'tile_flower.png')
        print(f"\nTrying another alternate file: {os.path.abspath(alt_flower_path)}")
        if os.path.exists(alt_flower_path):
            try:
                print(f"FOUND! Loading flower texture from: {alt_flower_path}")
                flower_surface = pygame.image.load(alt_flower_path).convert_alpha()
                # Scale the flower image to the expected tile size
                original_size = flower_surface.get_size()
                print(f"Original alternate flower texture size: {original_size}")
                scaled_flower = pygame.transform.scale(flower_surface, (TILE_SIZE, TILE_SIZE))
                assets[TileType.FLOWER.value] = scaled_flower
                print(f"Successfully loaded and scaled alternate flower texture to {TILE_SIZE}x{TILE_SIZE}")
                flower_file_found = True
            except Exception as e:
                print(f"ERROR loading alternate flower texture: {e}")
        else:
            print(f"Alternate flower texture file NOT FOUND at: {alt_flower_path}")
    
    # If none of the files were found, use procedural generation fallback
    if not flower_file_found:
        print("\nNo flower texture files found, using procedural generation fallback.")

    # Add more tile textures here when available 