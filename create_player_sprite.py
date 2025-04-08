"""
Script to create a simple player sprite sheet for testing.
"""

import pygame
import os

def create_player_sprite_sheet():
    """Create a placeholder sprite sheet for the player."""
    # Initialize Pygame
    pygame.init()
    
    # Create sprite sheet surface (4 frames x 4 directions)
    sprite_sheet = pygame.Surface((32 * 4, 32 * 4), pygame.SRCALPHA)
    
    # Colors for different parts
    body_color = (50, 50, 150)  # Blue
    head_color = (255, 220, 180)  # Skin tone
    hair_color = (139, 69, 19)  # Brown
    cape_color = (150, 0, 0)  # Red
    
    # Create frames for each direction
    for direction in range(4):  # DOWN, LEFT, RIGHT, UP
        for frame in range(4):
            # Position in sprite sheet
            x = frame * 32
            y = direction * 32
            
            # Draw player frame
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            
            # Cape (moves with frame)
            cape_offset = 2 if frame % 2 == 0 else -2
            cape_points = [
                (16, 12),  # Top
                (16 + cape_offset, 20),  # Middle
                (16 + cape_offset * 2, 28),  # Bottom
                (20 + cape_offset * 2, 28),  # Bottom right
                (20, 12)  # Top right
            ]
            pygame.draw.polygon(surface, cape_color, cape_points)
            
            # Body (moves slightly with frame)
            body_offset = 1 if frame % 2 == 0 else -1
            pygame.draw.ellipse(surface, body_color,
                              (12, 12 + body_offset, 8, 16))
            
            # Head
            pygame.draw.circle(surface, head_color, (16, 10), 6)
            
            # Hair (different style based on direction)
            if direction == 0:  # DOWN
                hair_points = [
                    (10, 8), (16, 4), (22, 8),  # Top curve
                    (22, 12), (10, 12)  # Bottom
                ]
            elif direction == 1:  # LEFT
                hair_points = [
                    (13, 8), (16, 4), (19, 8),  # Top curve
                    (19, 12), (13, 12)  # Bottom
                ]
            elif direction == 2:  # RIGHT
                hair_points = [
                    (13, 8), (16, 4), (19, 8),  # Top curve
                    (19, 12), (13, 12)  # Bottom
                ]
            else:  # UP
                hair_points = [
                    (10, 12), (16, 4), (22, 12)  # Simple triangle
                ]
            pygame.draw.polygon(surface, hair_color, hair_points)
            
            # Eyes (blink on frame 2)
            eye_height = 2 if frame != 2 else 1
            pygame.draw.ellipse(surface, (255, 255, 255),
                              (13, 9, 2, eye_height))  # Left eye
            pygame.draw.ellipse(surface, (255, 255, 255),
                              (17, 9, 2, eye_height))  # Right eye
            
            # Add frame to sprite sheet
            sprite_sheet.blit(surface, (x, y))
    
    # Ensure the assets/animations directory exists
    os.makedirs(os.path.join("assets", "animations"), exist_ok=True)
    
    # Save the sprite sheet
    pygame.image.save(sprite_sheet, os.path.join("assets", "animations", "player.png"))
    print("Player sprite sheet created successfully!")

if __name__ == "__main__":
    create_player_sprite_sheet() 