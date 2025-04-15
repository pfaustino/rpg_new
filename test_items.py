import pygame
import sys
import json
import os

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "RPG Item Test"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class ItemTest:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Set up clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.normal_font = pygame.font.SysFont("Arial", 18)
        
        # Load or create test items
        self.items = self.load_or_create_items()
        
        # Current selection
        self.selected_item = None
        
        # Message
        self.message = ""
        self.message_timer = 0
    
    def load_or_create_items(self):
        items = []
        items_dir = "data/items"
        
        # Check if items directory exists
        if not os.path.exists(items_dir):
            os.makedirs(items_dir)
            print(f"Created items directory: {items_dir}")
        
        # Try to load items.json if it exists
        items_path = os.path.join(items_dir, "items.json")
        if os.path.exists(items_path):
            try:
                with open(items_path, 'r') as f:
                    items_data = json.load(f)
                    items = items_data.get("items", [])
                    print(f"Loaded {len(items)} items from {items_path}")
            except Exception as e:
                print(f"Error loading items: {e}")
        
        # If no items were loaded, create test items
        if not items:
            items = [
                {
                    "id": "moonlight_flower",
                    "name": "Moonlight Flower",
                    "description": "A rare flower that glows under moonlight. Used in ancient rituals.",
                    "type": "quest_item",
                    "value": 50
                },
                {
                    "id": "crystal_shard",
                    "name": "Crystal Shard",
                    "description": "A fragment of a larger crystal formation. Pulsing with magical energy.",
                    "type": "quest_item",
                    "value": 75
                },
                {
                    "id": "cloak_of_night_whispers",
                    "name": "Cloak of Night Whispers",
                    "description": "A mystical cloak that grants stealth abilities under moonlight.",
                    "type": "armor",
                    "value": 500,
                    "stats": {
                        "defense": 5,
                        "magic_resistance": 10
                    }
                },
                {
                    "id": "crystal_amulet",
                    "name": "Crystal Amulet of Protection",
                    "description": "An amulet crafted from pure crystal. Provides magical protection.",
                    "type": "accessory",
                    "value": 750,
                    "stats": {
                        "magic_resistance": 15,
                        "max_mana": 25
                    }
                }
            ]
            
            # Save the test items
            self.save_items(items)
            print(f"Created and saved {len(items)} test items")
        
        return items
    
    def save_items(self, items):
        items_path = os.path.join("data/items", "items.json")
        try:
            with open(items_path, 'w') as f:
                json.dump({"items": items}, f, indent=2)
            self.show_message(f"Saved {len(items)} items to {items_path}")
        except Exception as e:
            self.show_message(f"Error saving items: {e}")
    
    def show_message(self, message, duration=3000):
        self.message = message
        self.message_timer = duration
    
    def draw(self):
        # Clear the screen
        self.screen.fill(WHITE)
        
        # Draw title
        title_text = self.title_font.render("RPG Item Test", True, BLACK)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        # Draw items list
        y_pos = 80
        for i, item in enumerate(self.items):
            # Item background
            item_rect = pygame.Rect(50, y_pos, WIDTH - 100, 60)
            pygame.draw.rect(self.screen, LIGHT_GRAY, item_rect)
            pygame.draw.rect(self.screen, GRAY, item_rect, 2)
            
            # Highlight selected item
            if self.selected_item == i:
                pygame.draw.rect(self.screen, BLUE, item_rect, 3)
            
            # Item name
            name_text = self.title_font.render(item["name"], True, BLACK)
            self.screen.blit(name_text, (60, y_pos + 5))
            
            # Item ID
            id_text = self.normal_font.render(f"ID: {item['id']}", True, GRAY)
            self.screen.blit(id_text, (60, y_pos + 30))
            
            # Item type
            type_text = self.normal_font.render(f"Type: {item['type']}", True, GRAY)
            self.screen.blit(type_text, (300, y_pos + 30))
            
            y_pos += 70
        
        # Draw message
        if self.message and self.message_timer > 0:
            message_text = self.normal_font.render(self.message, True, GREEN)
            self.screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT - 40))
        
        # Draw instructions
        instructions = self.normal_font.render("Click on an item to select it. Press [V] to verify quest items exist.", True, BLACK)
        self.screen.blit(instructions, (50, HEIGHT - 80))
        
        # Update the display
        pygame.display.flip()
    
    def verify_quest_items(self):
        # Load side quests
        try:
            with open("data/quests/side_quests.json", 'r') as f:
                quests_data = json.load(f)
                quests = quests_data.get("quests", [])
                
                # Extract all needed item IDs from quests
                needed_items = set()
                for quest in quests:
                    # Check objectives for collect objectives
                    for objective in quest.get("objectives", []):
                        if objective.get("type") == "collect":
                            needed_items.add(objective.get("target_item"))
                    
                    # Check rewards for reward items
                    for reward_item in quest.get("rewards", {}).get("items", []):
                        needed_items.add(reward_item.get("id"))
                
                # Remove None values
                needed_items.discard(None)
                
                # Check if all needed items exist
                item_ids = {item["id"] for item in self.items}
                missing_items = needed_items - item_ids
                
                if missing_items:
                    self.show_message(f"Missing quest items: {', '.join(missing_items)}")
                else:
                    self.show_message("All quest items exist! Quest system ready for testing.")
                
        except Exception as e:
            self.show_message(f"Error verifying quest items: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicked on an item
                    y_pos = 80
                    for i in range(len(self.items)):
                        item_rect = pygame.Rect(50, y_pos, WIDTH - 100, 60)
                        if item_rect.collidepoint(mouse_pos):
                            self.selected_item = i
                            self.show_message(f"Selected: {self.items[i]['name']}")
                            break
                        y_pos += 70
            
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.verify_quest_items()
        
        return True
    
    def update(self):
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= self.clock.get_time()
    
    def run(self):
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update()
            
            # Draw
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    item_test = ItemTest()
    item_test.run() 