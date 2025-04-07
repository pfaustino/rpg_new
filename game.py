import pygame
import random
import math
import os
from typing import Dict, List, Tuple, Optional, Union
from rpg_modules.items import ItemGenerator, Item, Weapon, Armor, Hands, Consumable
from rpg_modules.ui import InventoryUI, EquipmentUI, ItemGeneratorUI, QuestUI
from rpg_modules.entities import Player
from rpg_modules.quests import QuestGenerator, QuestType, QuestLog
from rpg_modules.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    WHITE, BLACK, RED, GREEN, BLUE, GRAY,
    QUALITY_COLORS
)

# Player stats
PLAYER_HP = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5

# Monster stats
MONSTER_HP = 50
MONSTER_ATTACK = 5
MONSTER_DEFENSE = 2

# Asset paths
ASSET_PATH = "assets"
FLOOR_IMAGE = "floor.png"
WALL_IMAGE = "wall.png"
PLAYER_IMAGE = "player.png"
MONSTER_IMAGE = "monster.png"

def load_assets():
    """Load all game assets"""
    assets = {}
    
    # Create placeholder assets if they don't exist
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
    
    # Load or create floor image
    floor_path = os.path.join(ASSET_PATH, FLOOR_IMAGE)
    if not os.path.exists(floor_path):
        floor_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        floor_surface.fill((200, 200, 200))
        pygame.image.save(floor_surface, floor_path)
    assets['floor'] = pygame.image.load(floor_path)
    
    # Load or create wall image
    wall_path = os.path.join(ASSET_PATH, WALL_IMAGE)
    if not os.path.exists(wall_path):
        wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_surface.fill((100, 100, 100))
        pygame.image.save(wall_surface, wall_path)
    assets['wall'] = pygame.image.load(wall_path)
    
    # Load or create player image
    player_path = os.path.join(ASSET_PATH, PLAYER_IMAGE)
    if not os.path.exists(player_path):
        player_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        player_surface.fill(BLUE)
        pygame.image.save(player_surface, player_path)
    assets['player'] = pygame.image.load(player_path)
    
    # Load or create monster image
    monster_path = os.path.join(ASSET_PATH, MONSTER_IMAGE)
    if not os.path.exists(monster_path):
        monster_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        monster_surface.fill(RED)
        pygame.image.save(monster_surface, monster_path)
    assets['monster'] = pygame.image.load(monster_path)
    
    return assets

# Game states
class GameState:
    """Manages the global game state."""
    
    def __init__(self):
        """Initialize the game state."""
        self.assets = {}
        self.item_generator = ItemGenerator()
        self.quest_generator = QuestGenerator(self.item_generator)
        
        # Generate more quests
        self.quests = []
        
        # Generate main quests (5)
        for _ in range(5):
            self.quests.append(self.quest_generator.generate_quest(QuestType.MAIN))
            
        # Generate side quests (10)
        for _ in range(10):
            self.quests.append(self.quest_generator.generate_quest(QuestType.SIDE))
            
        # Generate daily quests (5)
        for _ in range(5):
            self.quests.append(self.quest_generator.generate_quest(QuestType.DAILY))
        
    def load_assets(self):
        """Load game assets."""
        self.assets['wall'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.assets['wall'].fill((100, 100, 100))
        
        self.assets['floor'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.assets['floor'].fill((50, 50, 50))
        
        self.assets['player'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.assets['player'].fill((0, 255, 0))
        
    def update(self):
        """Update game state."""
        # Update daily quests if needed
        pass
        
    def initialize_player_quests(self, player):
        """Add initial quests to the player's quest log."""
        for quest in self.quests:
            player.quest_log.add_quest(quest)

class Camera:
    def __init__(self, width: int, height: int):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(SCREEN_WIDTH / 2)
        y = -target.rect.y + int(SCREEN_HEIGHT / 2)
        
        # Limit scrolling to map size
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y

class Equipment:
    """Class to manage equipped items."""
    def __init__(self):
        self.slots = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None,
            'weapon': None
        }
        
    def get_equipped_item(self, slot: str) -> Optional[Item]:
        """Get the item equipped in the given slot."""
        return self.slots.get(slot)
        
    def equip_item(self, item: Item) -> bool:
        """
        Equip an item in its appropriate slot.
        Returns True if successful, False if no appropriate slot.
        """
        slot = None
        if isinstance(item, Weapon):
            slot = 'weapon'
        elif isinstance(item, Hands):
            slot = 'hands'
        elif isinstance(item, Armor):
            slot = item.armor_type.lower()
            
        if slot and slot in self.slots:
            self.slots[slot] = item
            return True
        return False
        
    def unequip_item(self, slot: str) -> Optional[Item]:
        """Unequip and return the item in the given slot."""
        if slot in self.slots:
            item = self.slots[slot]
            self.slots[slot] = None
            return item
        return None

class Inventory:
    """Class to manage the player's inventory."""
    def __init__(self, capacity: int = 40):  # Changed from 32 to 40 to match 5x8 grid
        self.items = [None] * capacity
        
    def add_item(self, item: Item) -> bool:
        """Add an item to the first empty slot. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is None:
                self.items[i] = item
                return True
        return False
        
    def remove_item(self, item: Item) -> bool:
        """Remove the first occurrence of an item. Returns True if successful."""
        for i in range(len(self.items)):
            if self.items[i] is item:
                self.items[i] = None
                return True
        return False
        
    def get_item_at(self, index: int) -> Optional[Item]:
        """Get the item at the given index."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        # Create a more visible player sprite
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        # Add a white border to make the player more visible
        pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.defense = 5
        self.inventory = Inventory()
        self.equipment = Equipment()
        self.quest_log = QuestLog()
        self.level = 1
        self.experience = 0
        self.gold = 0

    def update(self):
        """Update player state"""
        pass  # Add any necessary update logic here

    def attack(self):
        """Perform an attack"""
        print(f"Player attacks with power {self.attack_power}")

    def recalculate_stats(self):
        """Recalculate player stats based on equipped items"""
        base_attack = 10
        base_defense = 5
        
        # Add weapon attack power
        weapon = self.equipment.get_equipped_item('weapon')
        if weapon:
            base_attack += weapon.attack_power
            
        # Add armor defense
        for slot in ['head', 'chest', 'legs', 'feet']:
            armor = self.equipment.get_equipped_item(slot)
            if armor:
                base_defense += armor.defense
                
        self.attack_power = base_attack
        self.defense = base_defense

    def equip_item(self, item: Item) -> bool:
        if self.equipment.equip_item(item):
            self.recalculate_stats()
            return True
        return False

    def unequip_item(self, slot: str) -> Optional[Item]:
        item = self.equipment.unequip_item(slot)
        if item:
            self.recalculate_stats()
        return item

    def move(self, dx: int, dy: int, walls: pygame.sprite.Group):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # Check for collisions with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:  # Moving right
                    self.rect.right = wall.rect.left
                if dx < 0:  # Moving left
                    self.rect.left = wall.rect.right
                if dy > 0:  # Moving down
                    self.rect.bottom = wall.rect.top
                if dy < 0:  # Moving up
                    self.rect.top = wall.rect.bottom

    def draw(self, screen: pygame.Surface, camera: Camera):
        """Draw the player on the screen"""
        screen.blit(self.image, camera.apply(self))
        
    def add_experience(self, amount: int):
        """Add experience points to the player."""
        self.experience += amount
        # TODO: Add level up logic
        
    def add_gold(self, amount: int):
        """Add gold to the player's currency."""
        self.gold += amount

class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

def create_map(width: int, height: int) -> Tuple[pygame.sprite.Group, List[List[int]]]:
    """Create a simple map with walls around the edges"""
    walls = pygame.sprite.Group()
    map_grid = [[0 for _ in range(width)] for _ in range(height)]
    
    # Create walls around the edges
    for x in range(width):
        walls.add(Wall(x, 0))
        walls.add(Wall(x, height - 1))
        map_grid[0][x] = 1
        map_grid[height - 1][x] = 1
    
    for y in range(height):
        walls.add(Wall(0, y))
        walls.add(Wall(width - 1, y))
        map_grid[y][0] = 1
        map_grid[y][width - 1] = 1
    
    return walls, map_grid

def initialize_game():
    """Initialize the game state."""
    # ... existing code ...
    
    # Generate quests
    quest_generator = QuestGenerator(item_generator)
    
    # Generate main quest chains
    for _ in range(2):  # 2 main quest chains (6 quests total)
        chain_id = f"chain_{random.randint(1000, 9999)}"
        quests = quest_generator.generate_quest_chain(chain_id, QuestType.MAIN)
        for quest in quests:
            player.quest_log.add_quest(quest)
    
    # Generate individual main quests
    for _ in range(4):  # 4 individual main quests
        quest = quest_generator.generate_quest(QuestType.MAIN)
        player.quest_log.add_quest(quest)
    
    # Generate side quests
    for _ in range(6):  # 6 side quests
        quest = quest_generator.generate_quest(QuestType.SIDE)
        player.quest_log.add_quest(quest)
    
    # Generate daily quests
    for _ in range(4):  # 4 daily quests
        quest = quest_generator.generate_quest(QuestType.DAILY)
        player.quest_log.add_quest(quest)
    
    # ... existing code ...

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game")
    clock = pygame.time.Clock()
    
    # Initialize game state and load assets
    game_state = GameState()
    game_state.load_assets()
    
    # Create map
    map_width = 50
    map_height = 50
    walls, map_grid = create_map(map_width, map_height)
    
    # Create game objects
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Calculate UI positions
    inventory_width = 300
    equipment_width = 300
    quest_width = 400
    spacing = 20
    
    # Center windows with proper spacing
    total_width = inventory_width + spacing + equipment_width
    start_x = (SCREEN_WIDTH - total_width) // 2
    
    # Create UI elements with calculated positions
    inventory_ui = InventoryUI(start_x, 50)  # Left side
    equipment_ui = EquipmentUI(start_x + inventory_width + spacing, 50)  # Right side
    item_generator = ItemGeneratorUI(start_x + inventory_width + spacing, 50)  # Right side, same position as equipment
    quest_ui = QuestUI((SCREEN_WIDTH - quest_width) // 2, 50, width=quest_width)  # Centered
    
    # Set initial quests
    initialize_game()
    
    # Initialize mode
    current_mode = None  # None, "equip", "generate", or "quest"
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    if current_mode == "equip":
                        current_mode = None
                        inventory_ui.visible = False
                        equipment_ui.visible = False
                    else:
                        current_mode = "equip"
                        inventory_ui.visible = True
                        equipment_ui.visible = True
                        item_generator.visible = False
                        quest_ui.visible = False
                elif event.key == pygame.K_g:
                    if current_mode == "generate":
                        current_mode = None
                        inventory_ui.visible = False
                        item_generator.visible = False
                    else:
                        current_mode = "generate"
                        inventory_ui.visible = True
                        item_generator.visible = True
                        equipment_ui.visible = False
                        quest_ui.visible = False
                elif event.key == pygame.K_j:  # J for Journal
                    if current_mode == "quest":
                        current_mode = None
                        quest_ui.visible = False
                    else:
                        current_mode = "quest"
                        quest_ui.visible = True
                        inventory_ui.visible = False
                        equipment_ui.visible = False
                        item_generator.visible = False
                elif event.key == pygame.K_ESCAPE:
                    current_mode = None
                    inventory_ui.visible = False
                    equipment_ui.visible = False
                    item_generator.visible = False
                    quest_ui.visible = False
            
            # Handle UI events only if in a mode
            if current_mode:
                # Always handle inventory events first
                inventory_handled = inventory_ui.handle_event(event, player)
                
                if current_mode == "equip":
                    equipment_handled = equipment_ui.handle_event(event, player)
                    if inventory_handled or equipment_handled:
                        continue
                elif current_mode == "generate":
                    if inventory_handled or item_generator.handle_event(event, player):
                        continue
                elif current_mode == "quest":
                    if quest_ui.handle_event(event, player):
                        continue
            
            # Handle player movement only if not in any mode
            if not current_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move(-1, 0, walls)
                    elif event.key == pygame.K_RIGHT:
                        player.move(1, 0, walls)
                    elif event.key == pygame.K_UP:
                        player.move(0, -1, walls)
                    elif event.key == pygame.K_DOWN:
                        player.move(0, 1, walls)
                    elif event.key == pygame.K_SPACE:
                        player.attack()
        
        # Update game state
        player.update()
        camera.update(player)
        
        # Update UI elements based on current mode
        if current_mode:
            # Always update inventory UI first
            inventory_ui.update()
            if current_mode == "equip":
                equipment_ui.update()
            elif current_mode == "generate":
                item_generator.update()
            elif current_mode == "quest":
                quest_ui.update()
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw map
        for y, row in enumerate(map_grid):
            for x, cell in enumerate(row):
                if cell == 1:  # Wall
                    screen.blit(game_state.assets['wall'], (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y))
                else:  # Floor
                    screen.blit(game_state.assets['floor'], (x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y))
        
        # Draw player
        player.draw(screen, camera)
        
        # Draw UI elements based on current mode
        if current_mode:
            if current_mode == "equip":
                inventory_ui.draw(screen, player)
                equipment_ui.draw(screen, player)
            elif current_mode == "generate":
                inventory_ui.draw(screen, player)
                item_generator.draw(screen, player)
            elif current_mode == "quest":
                quest_ui.draw(screen, player)
            
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main() 