import pygame
import random
import math
import os
from typing import Dict, List, Tuple, Optional, Union

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# Player stats
PLAYER_HP = 100
PLAYER_ATTACK = 10
PLAYER_DEFENSE = 5

# Monster stats
MONSTER_HP = 50
MONSTER_ATTACK = 5
MONSTER_DEFENSE = 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
SILVER = (192, 192, 192)  # Common
GREEN = (0, 255, 0)       # Uncommon
BLUE = (0, 0, 255)        # Rare
PURPLE = (128, 0, 128)    # Epic
GOLD = (255, 215, 0)      # Mythic

# Asset paths
ASSET_PATH = "assets"
FLOOR_IMAGE = "floor.png"
WALL_IMAGE = "wall.png"
PLAYER_IMAGE = "player.png"
MONSTER_IMAGE = "monster.png"

# Item generation constants
WEAPON_TYPES = ['Sword', 'Axe', 'Mace', 'Dagger', 'Staff']
ARMOR_TYPES = ['Head', 'Chest', 'Legs', 'Feet']
MATERIALS = ['Iron', 'Steel', 'Silver', 'Gold', 'Mithril']
QUALITIES = ['Standard', 'Polished', 'Masterwork', 'Legendary']
PREFIXES = {
    'common': ['Sharp', 'Sturdy', 'Balanced'],
    'uncommon': ['Vicious', 'Reinforced', 'Precise'],
    'rare': ['Soulbound', 'Ethereal', 'Celestial']
}

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
    def __init__(self):
        self.running = True
        self.player = None
        self.camera = None
        self.map_grid = None
        self.assets = {}

    def load_assets(self):
        """Load game assets"""
        try:
            # Load images
            self.assets['floor'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.assets['floor'].fill(GRAY)
            
            self.assets['wall'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.assets['wall'].fill(BLACK)
            
            # Load sounds
            pygame.mixer.init()
            self.assets['silent_sound'] = pygame.mixer.Sound(buffer=bytearray(0))
            
            print("Assets loaded successfully")
        except Exception as e:
            print(f"Error loading assets: {e}")

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

class Item:
    def __init__(self, name: str, rarity: str = "Common"):
        self.name = name
        self.rarity = rarity
        self.icon = None
        self.description = ""
        self.value = 0

    def get_icon(self) -> pygame.Surface:
        if not self.icon:
            self.icon = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.icon.fill(GRAY)
        return self.icon

class Weapon(Item):
    def __init__(self, name: str, weapon_type: str, material: str, quality: str, 
                 attack_power: int, prefix: str = None):
        super().__init__(name)
        self.weapon_type = weapon_type
        self.material = material
        self.quality = quality
        self.attack_power = attack_power
        self.prefix = prefix
        self.value = attack_power * 10  # Calculate value after attack_power is set

    def get_equipment_sprite(self) -> pygame.Surface:
        # Create a colored surface based on material
        sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base color based on material
        if self.material == "Iron":
            color = (192, 192, 192)  # Silver
        elif self.material == "Steel":
            color = (160, 160, 160)  # Darker silver
        elif self.material == "Mithril":
            color = (173, 216, 230)  # Light blue
        else:
            color = (192, 192, 192)  # Default silver
            
        sprite.fill(color)
        
        # Add quality overlay
        if self.quality == "Crude":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            sprite.blit(overlay, (0, 0))
        elif self.quality == "Fine":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 64))  # Semi-transparent white
            sprite.blit(overlay, (0, 0))
            
        return sprite

class Armor(Item):
    def __init__(self, name: str, armor_type: str, material: str, quality: str, 
                 defense: int, prefix: str = None):
        super().__init__(name)
        self.armor_type = armor_type
        self.material = material
        self.quality = quality
        self.defense = defense
        self.prefix = prefix
        self.value = defense * 10

    def get_equipment_sprite(self) -> pygame.Surface:
        # Create a colored surface based on material
        sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base color based on material
        if self.material == "Iron":
            color = (192, 192, 192)  # Silver
        elif self.material == "Steel":
            color = (160, 160, 160)  # Darker silver
        elif self.material == "Mithril":
            color = (173, 216, 230)  # Light blue
        else:
            color = (192, 192, 192)  # Default silver
            
        sprite.fill(color)
        
        # Add quality overlay
        if self.quality == "Crude":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            sprite.blit(overlay, (0, 0))
        elif self.quality == "Fine":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 64))  # Semi-transparent white
            sprite.blit(overlay, (0, 0))
            
        return sprite

class Consumable(Item):
    def __init__(self, consumable_type: str, quality: str, effect_value: int, prefix: str = None):
        name = f"{quality} {consumable_type}"
        if prefix:
            name = f"{prefix} {name}"
        super().__init__(name)
        self.consumable_type = consumable_type
        self.quality = quality
        self.effect_value = effect_value
        self.prefix = prefix
        self.value = effect_value * 5

    def get_equipment_sprite(self) -> pygame.Surface:
        # Create a colored surface based on consumable type
        sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base color based on type
        if "Health" in self.consumable_type:
            color = (255, 0, 0)  # Red for health potions
        elif "Mana" in self.consumable_type:
            color = (0, 0, 255)  # Blue for mana potions
        else:
            color = (0, 255, 0)  # Green for stamina potions
            
        sprite.fill(color)
        
        # Add quality overlay
        if self.quality == "Rusty":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            sprite.blit(overlay, (0, 0))
        elif self.quality == "Legendary":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 64))  # Semi-transparent gold
            sprite.blit(overlay, (0, 0))
            
        return sprite

class Equipment:
    def __init__(self):
        self.slots = {
            'weapon': None,
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'hands': None  # Adding hands slot
        }

    def get_equipped_item(self, slot: str) -> Optional[Item]:
        return self.slots.get(slot)

    def equip_item(self, item: Item) -> bool:
        if isinstance(item, Weapon):
            if self.slots['weapon'] is None:
                self.slots['weapon'] = item
                return True
        elif isinstance(item, Armor):
            slot = item.armor_type.lower()
            if self.slots[slot] is None:
                self.slots[slot] = item
                return True
        return False

    def unequip_item(self, slot: str) -> Optional[Item]:
        item = self.slots[slot]
        if item:
            self.slots[slot] = None
        return item

class Inventory:
    def __init__(self, capacity: int = 40):  # Changed from 32 to 40 to match 5x8 grid
        self.items = []
        self.capacity = capacity

    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item: Item) -> bool:
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def get_item_at(self, index: int) -> Optional[Item]:
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

class InventoryUI:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 300, 500)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.visible = False
        self.selected_item = None
        self.hovered_item = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, 300, 300)

        # Grid configuration
        self.grid_margin = 10  # Margin around the grid
        self.cell_size = 50    # Size of each cell
        self.cell_padding = 5  # Padding within cells
        self.grid_cols = 5     # Number of columns
        self.grid_rows = 8     # Number of rows
        
        # Calculate grid positions
        self.grid_start_x = x + self.grid_margin
        self.grid_start_y = y + 40  # Leave space for header
        
        # Create grid cells
        self.grid_cells = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = self.grid_start_x + col * (self.cell_size + self.cell_padding)
                cell_y = self.grid_start_y + row * (self.cell_size + self.cell_padding)
                self.grid_cells.append(pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size))

    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the cell index at the given position"""
        for i, cell in enumerate(self.grid_cells):
            if cell.collidepoint(pos):
                return i
        return None

    def handle_event(self, event: pygame.event.Event, player: Player) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(player.inventory.items):
                    self.selected_item = player.inventory.items[cell_index]
                    
                    # Try to equip the item
                    if player.equip_item(self.selected_item):
                        player.inventory.remove_item(self.selected_item)
                        self.selected_item = None
                    return True
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(player.inventory.items):
                    self.hovered_item = player.inventory.items[cell_index]
                    self.hover_timer = 0
                    self.tooltip_visible = False
                else:
                    self.hovered_item = None
                    self.tooltip_visible = False
            else:
                self.hovered_item = None
                self.tooltip_visible = False
        return False

    def draw(self, screen: pygame.Surface, player: Player):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Inventory", True, WHITE)
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw grid cells
        for i, cell in enumerate(self.grid_cells):
            # Draw cell background
            pygame.draw.rect(screen, (30, 30, 30), cell)
            
            # Draw item if one exists at this index
            if i < len(player.inventory.items):
                item = player.inventory.items[i]
                
                # Determine border color based on quality
                border_color = SILVER  # Default to common
                if "Legendary" in item.quality:
                    border_color = GOLD
                elif "Masterwork" in item.quality:
                    border_color = PURPLE
                elif "Polished" in item.quality:
                    border_color = BLUE
                elif "Standard" in item.quality:
                    border_color = GREEN
                
                # Draw cell with quality-colored border
                pygame.draw.rect(screen, border_color, cell, 2)
                
                # Draw item sprite
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (self.cell_size - 10, self.cell_size - 10))
                screen.blit(scaled_sprite, (cell.x + 5, cell.y + 5))
                
                # Draw single-word name overlaid on the sprite
                name = item.name.split()[0]  # Get first word of the name
                name_text = self.small_font.render(name, True, WHITE)
                # Create a semi-transparent background for the name
                name_bg = pygame.Surface((name_text.get_width() + 4, name_text.get_height() + 4), pygame.SRCALPHA)
                name_bg.fill((0, 0, 0, 128))  # Semi-transparent black
                screen.blit(name_bg, (cell.x + 5, cell.y + 5))
                screen.blit(name_text, (cell.x + 7, cell.y + 7))
                
                # Draw small stat indicator in the corner
                if isinstance(item, Weapon):
                    stat_text = self.small_font.render(f"ATK:{item.attack_power}", True, WHITE)
                elif isinstance(item, Hands):
                    stat_text = self.small_font.render(f"DEF:{item.defense}", True, WHITE)
                elif isinstance(item, Consumable):
                    stat_text = self.small_font.render(f"POT:{item.effect_value}", True, WHITE)
                else:  # Regular armor
                    stat_text = self.small_font.render(f"DEF:{item.defense}", True, WHITE)
                screen.blit(stat_text, (cell.right - 40, cell.bottom - 15))
            else:
                # Draw empty cell with white border
                pygame.draw.rect(screen, WHITE, cell, 1)

        # Draw tooltip if visible
        if self.tooltip_visible and self.hovered_item:
            # Position tooltip above the equipment window
            tooltip_x = SCREEN_WIDTH - 700  # Position to the left of equipment window
            tooltip_y = 50  # Same vertical position as inventory
            self.tooltip_rect.x = tooltip_x
            self.tooltip_rect.y = tooltip_y
            
            # Draw tooltip background
            pygame.draw.rect(screen, (30, 30, 30), self.tooltip_rect)
            pygame.draw.rect(screen, WHITE, self.tooltip_rect, 2)
            
            # Determine border color based on quality
            border_color = SILVER  # Default to common
            if "Legendary" in self.hovered_item.quality:
                border_color = GOLD
            elif "Masterwork" in self.hovered_item.quality:
                border_color = PURPLE
            elif "Polished" in self.hovered_item.quality:
                border_color = BLUE
            elif "Standard" in self.hovered_item.quality:
                border_color = GREEN
            
            # Draw item sprite with colored border
            sprite = self.hovered_item.get_equipment_sprite()
            scaled_sprite = pygame.transform.scale(sprite, (128, 128))
            # Draw the border first
            border_rect = pygame.Rect(tooltip_x + 7, tooltip_y + 7, 134, 134)
            pygame.draw.rect(screen, border_color, border_rect, 3)
            # Then draw the sprite
            screen.blit(scaled_sprite, (tooltip_x + 10, tooltip_y + 10))
            
            # Draw item name
            name_text = self.font.render(self.hovered_item.name, True, WHITE)
            screen.blit(name_text, (tooltip_x + 10, tooltip_y + 150))
            
            # Draw item stats
            y_offset = 180
            if isinstance(self.hovered_item, Weapon):
                stats = [
                    f"Type: {self.hovered_item.weapon_type}",
                    f"Attack: {self.hovered_item.attack_power}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
                if self.hovered_item.prefix:
                    stats.insert(1, f"Effect: {self.hovered_item.prefix}")
            elif isinstance(self.hovered_item, Hands):
                stats = [
                    "Type: Gauntlets",
                    f"Defense: {self.hovered_item.defense}",
                    f"Dexterity: {self.hovered_item.dexterity}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
                if self.hovered_item.prefix:
                    stats.insert(1, f"Effect: {self.hovered_item.prefix}")
            elif isinstance(self.hovered_item, Consumable):
                stats = [
                    f"Type: {self.hovered_item.consumable_type}",
                    f"Effect Value: {self.hovered_item.effect_value}",
                    f"Quality: {self.hovered_item.quality}"
                ]
                if self.hovered_item.prefix:
                    stats.insert(1, f"Effect: {self.hovered_item.prefix}")
            else:  # Regular armor
                stats = [
                    f"Type: {self.hovered_item.armor_type}",
                    f"Defense: {self.hovered_item.defense}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
                if self.hovered_item.prefix:
                    stats.insert(1, f"Effect: {self.hovered_item.prefix}")
            
            for stat in stats:
                stat_text = self.small_font.render(stat, True, WHITE)
                screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
                y_offset += 20

    def update(self):
        if self.hovered_item:
            self.hover_timer += 1
            if self.hover_timer > 30:  # Show tooltip after 0.5 seconds
                self.tooltip_visible = True

class Hands(Item):
    def __init__(self, name: str, material: str, quality: str, 
                 defense: int, dexterity: int, prefix: str = None):
        super().__init__(name)
        self.material = material
        self.quality = quality
        self.defense = defense
        self.dexterity = dexterity  # Bonus to attack speed or precision
        self.prefix = prefix
        self.value = (defense + dexterity) * 5

    def get_equipment_sprite(self) -> pygame.Surface:
        # Create a colored surface based on material
        sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Base color based on material
        if self.material == "Iron":
            color = (192, 192, 192)  # Silver
        elif self.material == "Steel":
            color = (160, 160, 160)  # Darker silver
        elif self.material == "Mithril":
            color = (173, 216, 230)  # Light blue
        else:
            color = (192, 192, 192)  # Default silver
            
        sprite.fill(color)
        
        # Add quality overlay
        if self.quality == "Crude":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            sprite.blit(overlay, (0, 0))
        elif self.quality == "Fine":
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 64))  # Semi-transparent white
            sprite.blit(overlay, (0, 0))
            
        return sprite

class EquipmentUI:
    def __init__(self, x: int, y: int):
        # Increase height to accommodate all slots
        self.rect = pygame.Rect(x, y, 300, 500)  # Changed height from 400 to 500
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.visible = False
        self.selected_slot = None
        self.hovered_slot = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, 300, 300)
        
        # Define equipment slots in a mannequin-like layout
        slot_size = 70  # Slightly smaller slots to fit better
        center_x = x + (self.rect.width - slot_size) // 2
        
        # Adjust vertical spacing for better distribution
        self.slots = {
            # Head slot at the top
            'head': pygame.Rect(center_x, y + 40, slot_size, slot_size),
            # Chest slot below head
            'chest': pygame.Rect(center_x, y + 130, slot_size, slot_size),
            # Hands slot to the left of chest
            'hands': pygame.Rect(center_x - 90, y + 130, slot_size, slot_size),
            # Weapon slot to the right of chest
            'weapon': pygame.Rect(center_x + 90, y + 130, slot_size, slot_size),
            # Legs slot below chest
            'legs': pygame.Rect(center_x, y + 220, slot_size, slot_size),
            # Feet slot below legs with more space above bottom
            'feet': pygame.Rect(center_x, y + 310, slot_size, slot_size)
        }

    def handle_event(self, event: pygame.event.Event, player: Player) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for slot_name, slot_rect in self.slots.items():
                if slot_rect.collidepoint(mouse_pos):
                    # Try to unequip the item
                    item = player.unequip_item(slot_name)
                    if item:
                        player.inventory.add_item(item)
                    return True
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for slot_name, slot_rect in self.slots.items():
                if slot_rect.collidepoint(mouse_pos):
                    self.hovered_slot = slot_name
                    self.hover_timer = 0
                    self.tooltip_visible = False
                    break
            else:
                self.hovered_slot = None
                self.tooltip_visible = False
        return False

    def update(self):
        if self.hovered_slot:
            self.hover_timer += 1
            if self.hover_timer > 30:  # Show tooltip after 0.5 seconds
                self.tooltip_visible = True
                # Position tooltip to the right of the equipment UI
                self.tooltip_rect.x = self.rect.right + 10
                self.tooltip_rect.y = self.rect.y

    def draw(self, screen: pygame.Surface, player: Player):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Equipment", True, WHITE)
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw slots
        for slot_name, slot_rect in self.slots.items():
            # Draw slot background
            pygame.draw.rect(screen, (30, 30, 30), slot_rect)
            pygame.draw.rect(screen, WHITE, slot_rect, 2)
            
            # Draw slot name
            name_text = self.small_font.render(slot_name.capitalize(), True, WHITE)
            screen.blit(name_text, (slot_rect.x + 5, slot_rect.y - 20))
            
            # Draw equipped item if any
            item = player.equipment.get_equipped_item(slot_name)
            if item:
                # Draw item sprite
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (slot_rect.width - 20, slot_rect.height - 20))
                screen.blit(scaled_sprite, (slot_rect.x + 10, slot_rect.y + 10))

        # Draw tooltip if visible
        if self.tooltip_visible and self.hovered_slot:
            item = player.equipment.get_equipped_item(self.hovered_slot)
            if item:
                # Draw tooltip background
                pygame.draw.rect(screen, (30, 30, 30), self.tooltip_rect)
                pygame.draw.rect(screen, WHITE, self.tooltip_rect, 2)
                
                # Draw item sprite (larger - 128x128)
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (128, 128))
                screen.blit(scaled_sprite, (self.tooltip_rect.x + 10, self.tooltip_rect.y + 10))
                
                # Draw item name
                name_text = self.font.render(item.name, True, WHITE)
                screen.blit(name_text, (self.tooltip_rect.x + 10, self.tooltip_rect.y + 150))
                
                # Draw item stats
                y_offset = 180
                if isinstance(item, Weapon):
                    stats = [
                        f"Type: {item.weapon_type}",
                        f"Attack: {item.attack_power}",
                        f"Material: {item.material}",
                        f"Quality: {item.quality}"
                    ]
                    if item.prefix:
                        stats.insert(1, f"Effect: {item.prefix}")
                else:
                    stats = [
                        f"Type: {item.armor_type}",
                        f"Defense: {item.defense}",
                        f"Material: {item.material}",
                        f"Quality: {item.quality}"
                    ]
                    if item.prefix:
                        stats.insert(1, f"Effect: {item.prefix}")
                
                for stat in stats:
                    stat_text = self.small_font.render(stat, True, WHITE)
                    screen.blit(stat_text, (self.tooltip_rect.x + 10, self.tooltip_rect.y + y_offset))
                    y_offset += 20

class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class ItemGeneratorUI:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 400, 500)  # Increased height for preview
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.visible = False
        
        # Dropdown options
        self.type_options = ['Random', 'Weapon', 'Armor', 'Consumable']
        self.quality_options = ['Random', 'Standard', 'Polished', 'Masterwork', 'Legendary']
        self.quality_colors = {
            'Random': SILVER,
            'Standard': GREEN,
            'Polished': BLUE,
            'Masterwork': PURPLE,
            'Legendary': GOLD
        }
        
        # Dropdown rectangles
        self.type_dropdown = pygame.Rect(x + 20, y + 60, 360, 40)
        self.quality_dropdown = pygame.Rect(x + 20, y + 120, 360, 40)
        self.generate_button = pygame.Rect(x + 20, y + 180, 360, 40)
        self.preview_rect = pygame.Rect(x + 20, y + 240, 360, 200)
        
        # Dropdown states
        self.type_expanded = False
        self.quality_expanded = False
        self.selected_type = 'Random'
        self.selected_quality = 'Random'
        
        # Preview item
        self.preview_item = None

    def handle_event(self, event: pygame.event.Event, player: Player) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle type dropdown
            if self.type_dropdown.collidepoint(mouse_pos):
                self.type_expanded = not self.type_expanded
                return True
            elif self.type_expanded:
                for i, option in enumerate(self.type_options):
                    option_rect = pygame.Rect(
                        self.type_dropdown.x,
                        self.type_dropdown.y + (i + 1) * 40,
                        self.type_dropdown.width,
                        40
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_type = option
                        self.type_expanded = False
                        return True
            
            # Handle quality dropdown
            if self.quality_dropdown.collidepoint(mouse_pos):
                self.quality_expanded = not self.quality_expanded
                return True
            elif self.quality_expanded:
                for i, option in enumerate(self.quality_options):
                    option_rect = pygame.Rect(
                        self.quality_dropdown.x,
                        self.quality_dropdown.y + (i + 1) * 40,
                        self.quality_dropdown.width,
                        40
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_quality = option
                        self.quality_expanded = False
                        return True
            
            # Handle generate button
            if self.generate_button.collidepoint(mouse_pos):
                # Determine type if random
                item_type = self.selected_type
                if item_type == 'Random':
                    item_type = random.choice(['Weapon', 'Armor', 'Consumable'])
                
                # Determine quality if random
                quality = self.selected_quality
                if quality == 'Random':
                    quality = random.choice(['Standard', 'Polished', 'Masterwork', 'Legendary'])
                
                # Generate the item
                if item_type == 'Weapon':
                    self.preview_item = generate_weapon(quality)
                elif item_type == 'Armor':
                    self.preview_item = generate_armor(quality)
                else:  # Consumable
                    self.preview_item = generate_consumable(quality)
                
                # Add to player's inventory
                if self.preview_item and player.inventory.add_item(self.preview_item):
                    return True
        return False

    def draw(self, screen: pygame.Surface, player: Player):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Item Generator", True, WHITE)
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw type dropdown base
        pygame.draw.rect(screen, (30, 30, 30), self.type_dropdown)
        pygame.draw.rect(screen, WHITE, self.type_dropdown, 2)
        type_text = self.small_font.render(f"Type: {self.selected_type}", True, WHITE)
        screen.blit(type_text, (self.type_dropdown.x + 10, self.type_dropdown.y + 10))
        
        # Draw quality dropdown base
        pygame.draw.rect(screen, (30, 30, 30), self.quality_dropdown)
        pygame.draw.rect(screen, self.quality_colors[self.selected_quality], self.quality_dropdown, 2)
        quality_text = self.small_font.render(f"Quality: {self.selected_quality}", True, WHITE)
        screen.blit(quality_text, (self.quality_dropdown.x + 10, self.quality_dropdown.y + 10))
        
        # Draw generate button
        pygame.draw.rect(screen, (70, 70, 70), self.generate_button)
        pygame.draw.rect(screen, WHITE, self.generate_button, 2)
        generate_text = self.font.render("Generate Item", True, WHITE)
        text_rect = generate_text.get_rect(center=self.generate_button.center)
        screen.blit(generate_text, text_rect)
        
        # Draw preview area
        pygame.draw.rect(screen, (30, 30, 30), self.preview_rect)
        if self.preview_item:
            # Determine border color based on quality
            border_color = self.quality_colors[self.preview_item.quality]
            pygame.draw.rect(screen, border_color, self.preview_rect, 3)
            
            # Calculate layout dimensions
            padding = 10
            sprite_size = 128  # Increased sprite size
            
            # Draw item sprite
            sprite = self.preview_item.get_equipment_sprite()
            scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
            sprite_x = self.preview_rect.x + padding
            sprite_y = self.preview_rect.y + (self.preview_rect.height - sprite_size) // 2  # Center vertically
            screen.blit(scaled_sprite, (sprite_x, sprite_y))
            
            # Calculate text start position (to the right of sprite)
            text_x = sprite_x + sprite_size + padding * 2
            text_y = self.preview_rect.y + padding
            text_spacing = 25  # Increased spacing between lines
            
            # Draw item name
            name_text = self.font.render(self.preview_item.name, True, WHITE)
            screen.blit(name_text, (text_x, text_y))
            
            # Draw item stats
            if isinstance(self.preview_item, Weapon):
                stats = [
                    f"Type: {self.preview_item.weapon_type}",
                    f"Attack: {self.preview_item.attack_power}",
                    f"Material: {self.preview_item.material}",
                    f"Quality: {self.preview_item.quality}"
                ]
                if self.preview_item.prefix:
                    stats.insert(1, f"Effect: {self.preview_item.prefix}")
            elif isinstance(self.preview_item, Hands):
                stats = [
                    "Type: Gauntlets",
                    f"Defense: {self.preview_item.defense}",
                    f"Dexterity: {self.preview_item.dexterity}",
                    f"Material: {self.preview_item.material}",
                    f"Quality: {self.preview_item.quality}"
                ]
                if self.preview_item.prefix:
                    stats.insert(1, f"Effect: {self.preview_item.prefix}")
            elif isinstance(self.preview_item, Consumable):
                stats = [
                    f"Type: {self.preview_item.consumable_type}",
                    f"Effect Value: {self.preview_item.effect_value}",
                    f"Quality: {self.preview_item.quality}"
                ]
                if self.preview_item.prefix:
                    stats.insert(1, f"Effect: {self.preview_item.prefix}")
            else:  # Regular armor
                stats = [
                    f"Type: {self.preview_item.armor_type}",
                    f"Defense: {self.preview_item.defense}",
                    f"Material: {self.preview_item.material}",
                    f"Quality: {self.preview_item.quality}"
                ]
                if self.preview_item.prefix:
                    stats.insert(1, f"Effect: {self.preview_item.prefix}")
            
            # Draw stats with proper spacing
            for i, stat in enumerate(stats):
                stat_text = self.small_font.render(stat, True, WHITE)
                screen.blit(stat_text, (text_x, text_y + text_spacing + i * text_spacing))
        else:
            pygame.draw.rect(screen, WHITE, self.preview_rect, 2)
            preview_text = self.small_font.render("Generated item will appear here", True, WHITE)
            text_rect = preview_text.get_rect(center=self.preview_rect.center)
            screen.blit(preview_text, text_rect)

        # Draw expanded dropdowns last so they appear on top
        if self.type_expanded:
            for i, option in enumerate(self.type_options):
                option_rect = pygame.Rect(
                    self.type_dropdown.x,
                    self.type_dropdown.y + (i + 1) * 40,
                    self.type_dropdown.width,
                    40
                )
                pygame.draw.rect(screen, (30, 30, 30), option_rect)
                pygame.draw.rect(screen, WHITE, option_rect, 1)
                option_text = self.small_font.render(option, True, WHITE)
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10))
        
        if self.quality_expanded:
            for i, option in enumerate(self.quality_options):
                option_rect = pygame.Rect(
                    self.quality_dropdown.x,
                    self.quality_dropdown.y + (i + 1) * 40,
                    self.quality_dropdown.width,
                    40
                )
                pygame.draw.rect(screen, (30, 30, 30), option_rect)
                pygame.draw.rect(screen, self.quality_colors[option], option_rect, 2)
                option_text = self.small_font.render(option, True, WHITE)
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10))

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

def generate_weapon(quality: str) -> Weapon:
    """Generate a weapon with random attributes based on quality"""
    weapon_type = random.choice(WEAPON_TYPES)
    material = random.choice(MATERIALS)
    
    # Base stats
    attack_power = random.randint(5, 15)
    
    # Apply quality modifiers
    if quality == 'Polished':
        attack_power += 5
        prefix = random.choice(PREFIXES['common'])
    elif quality == 'Masterwork':
        attack_power += 10
        prefix = random.choice(PREFIXES['uncommon'])
    elif quality == 'Legendary':
        attack_power += 15
        prefix = random.choice(PREFIXES['rare'])
    else:  # Standard
        prefix = None
    
    # Create the weapon name
    name = f"{quality} {material} {weapon_type}"
    if prefix:
        name = f"{prefix} {name}"
    
    return Weapon(name, weapon_type, material, quality, attack_power, prefix)

def generate_armor(quality: str) -> Union[Armor, Hands]:
    """Generate a piece of armor with random attributes based on quality"""
    # Randomly select armor type with equal probability
    armor_type = random.choice(['head', 'chest', 'legs', 'feet', 'hands'])
    material = random.choice(MATERIALS)
    
    # Base stats
    defense = random.randint(2, 8)
    
    # Apply quality modifiers
    if quality == 'Polished':
        defense += 3
        prefix = random.choice(PREFIXES['common'])
    elif quality == 'Masterwork':
        defense += 6
        prefix = random.choice(PREFIXES['uncommon'])
    elif quality == 'Legendary':
        defense += 9
        prefix = random.choice(PREFIXES['rare'])
    else:  # Standard
        prefix = None
    
    # Create the armor name
    name = f"{quality} {material} {armor_type.capitalize()}"
    if prefix:
        name = f"{prefix} {name}"
    
    if armor_type == 'hands':
        # Generate hands with dexterity bonus
        dexterity = random.randint(1, 4)
        if quality == 'Polished':
            dexterity += 2
        elif quality == 'Masterwork':
            dexterity += 4
        elif quality == 'Legendary':
            dexterity += 6
        return Hands(name, material, quality, defense, dexterity, prefix)
    else:
        return Armor(name, armor_type, material, quality, defense, prefix)

def generate_hands(rarity: str) -> Hands:
    """Generate a pair of hands equipment with random attributes based on rarity"""
    material = random.choice(MATERIALS)
    quality = random.choice(QUALITIES)
    
    # Base stats
    defense = random.randint(1, 4)
    dexterity = random.randint(1, 4)
    
    # Apply rarity modifiers
    if rarity == 'uncommon':
        defense += 2
        dexterity += 2
        prefix = random.choice(PREFIXES['common'])
    elif rarity == 'rare':
        defense += 4
        dexterity += 4
        prefix = random.choice(PREFIXES['uncommon'])
    else:
        prefix = None
    
    # Create the hands name
    name = f"{quality} {material} Gauntlets"
    if prefix:
        name = f"{prefix} {name}"
    
    return Hands(name, material, quality, defense, dexterity, prefix)

def generate_consumable(quality: str) -> Consumable:
    """Generate a consumable item with random attributes based on quality"""
    consumable_type = random.choice(['Health Potion', 'Mana Potion', 'Stamina Potion'])
    
    # Base stats
    effect_value = random.randint(10, 30)
    
    # Apply quality modifiers
    if quality == 'Polished':
        effect_value += 15
        prefix = random.choice(PREFIXES['common'])
    elif quality == 'Masterwork':
        effect_value += 30
        prefix = random.choice(PREFIXES['uncommon'])
    elif quality == 'Legendary':
        effect_value += 45
        prefix = random.choice(PREFIXES['rare'])
    else:  # Standard
        prefix = None
    
    return Consumable(consumable_type, quality, effect_value, prefix)

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
    spacing = 20  # Reduced spacing between windows (was 50)
    
    # Center both windows with proper spacing
    total_width = inventory_width + spacing + equipment_width
    start_x = (SCREEN_WIDTH - total_width) // 2
    
    # Create UI elements with calculated positions
    inventory_ui = InventoryUI(start_x, 50)  # Left side
    equipment_ui = EquipmentUI(start_x + inventory_width + spacing, 50)  # Right side with reduced spacing
    item_generator = ItemGeneratorUI(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200)
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    # Toggle both inventory and equipment UI
                    inventory_ui.visible = not inventory_ui.visible
                    equipment_ui.visible = inventory_ui.visible  # Keep them in sync
                elif event.key == pygame.K_g:
                    item_generator.visible = not item_generator.visible
            
            # Handle UI events
            if inventory_ui.handle_event(event, player):
                continue
            if equipment_ui.handle_event(event, player):
                continue
            if item_generator.handle_event(event, player):
                continue
            
            # Handle player movement
            if not (inventory_ui.visible or item_generator.visible):
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
        inventory_ui.update()
        
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
        
        # Draw UI elements if visible
        if inventory_ui.visible:
            inventory_ui.draw(screen, player)
        if equipment_ui.visible:
            equipment_ui.draw(screen, player)
        if item_generator.visible:
            item_generator.draw(screen, player)
            
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main() 