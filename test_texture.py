import os
import sys
import pygame

def test_texture_loading():
    # Initialize pygame
    pygame.init()
    
    # Create a small display
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Texture Test")
    
    # Current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Try to load grass texture
    grass_path = os.path.join('assets', 'images', 'tiles', 'tile_floor_grass.png')
    print(f"Looking for grass texture at: {os.path.abspath(grass_path)}")
    
    # Check if file exists
    if os.path.exists(grass_path):
        print(f"Grass texture file found at: {grass_path}")
        try:
            # Load texture
            grass_texture = pygame.image.load(grass_path).convert_alpha()
            print(f"Texture size: {grass_texture.get_size()}")
            
            # Display texture
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                # Clear screen and display texture
                screen.fill((0, 0, 0))
                screen.blit(grass_texture, (100, 100))
                pygame.display.flip()
                
        except Exception as e:
            print(f"Error loading texture: {e}")
    else:
        print(f"Grass texture file NOT FOUND at: {grass_path}")
        print("Available files in assets directory:")
        try:
            base_path = os.path.join('assets', 'images', 'tiles')
            if os.path.exists(base_path):
                print(f"Directory {base_path} exists")
                files = os.listdir(base_path)
                if files:
                    for file in files:
                        print(f"  - {file}")
                else:
                    print("  (directory is empty)")
            else:
                print(f"Directory {base_path} does not exist")
                
                # Check if parent directories exist
                parent_path = os.path.join('assets', 'images')
                if os.path.exists(parent_path):
                    print(f"Directory {parent_path} exists")
                    for file in os.listdir(parent_path):
                        print(f"  - {file}")
                else:
                    print(f"Directory {parent_path} does not exist")
                    
                    # Check if assets directory exists
                    asset_path = 'assets'
                    if os.path.exists(asset_path):
                        print(f"Directory {asset_path} exists")
                        for file in os.listdir(asset_path):
                            print(f"  - {file}")
                    else:
                        print(f"Directory {asset_path} does not exist")
                        
                        # List contents of current directory
                        print("Contents of current directory:")
                        for file in os.listdir('.'):
                            print(f"  - {file}")
                        
        except Exception as e:
            print(f"Error listing directory: {e}")
    
    pygame.quit()

if __name__ == "__main__":
    test_texture_loading() 