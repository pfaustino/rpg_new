"""
Player entity class for RPG games.
"""

import pygame
from typing import Optional, Dict, List, Any, Tuple
from ..items import Item, Inventory, Equipment
from ..quests import QuestLog
from ..core.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from ..animations.base import PlayerIcon

class Player:
    """Class representing the player character."""
    
    def __init__(self, x: float, y: float):
        """Initialize the player."""
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.speed = 200
        self.animation = PlayerIcon()
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.experience = 0
        self.gold = 0
        self.inventory = []  # List of items
        self.equipment = {}  # Dictionary of equipped items
        self.quest_log = []  # List of active quests
        self.size = TILE_SIZE  # Default size for player icon
        
        # Movement and collision
        # Make collision box slightly smaller than tile size
        collision_margin = 4  # pixels smaller on each side
        self.rect = pygame.Rect(
            self.x + collision_margin,  # Use self.x which is already in pixel coordinates
            self.y + collision_margin,  # Use self.y which is already in pixel coordinates
            TILE_SIZE - (collision_margin * 2),
            TILE_SIZE - (collision_margin * 2)
        )
        
    def handle_input(self, keys: pygame.key.ScancodeWrapper, walls: List[pygame.Rect]) -> None:
        """
        Handle player input and movement.
        
        Args:
            keys: The current state of keyboard keys
            walls: List of wall rectangles for collision detection
        """
        # Calculate target velocity based on input
        target_dx = 0
        target_dy = 0
        
        # Handle movement input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_dx = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_dx = self.speed
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_dy = -self.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_dy = self.speed
            
        # Smooth acceleration
        acceleration = 2000  # Pixels per second squared
        deceleration = 1500  # Slightly slower deceleration for smoother stops
        
        # Update velocity with acceleration
        if target_dx != 0:
            # Accelerate towards target velocity
            if self.dx < target_dx:
                self.dx = min(self.dx + acceleration * 0.016, target_dx)  # 0.016 is roughly one frame at 60fps
            elif self.dx > target_dx:
                self.dx = max(self.dx - acceleration * 0.016, target_dx)
        else:
            # Decelerate to stop
            if self.dx > 0:
                self.dx = max(0, self.dx - deceleration * 0.016)
            elif self.dx < 0:
                self.dx = min(0, self.dx + deceleration * 0.016)
                
        if target_dy != 0:
            # Accelerate towards target velocity
            if self.dy < target_dy:
                self.dy = min(self.dy + acceleration * 0.016, target_dy)
            elif self.dy > target_dy:
                self.dy = max(self.dy - acceleration * 0.016, target_dy)
        else:
            # Decelerate to stop
            if self.dy > 0:
                self.dy = max(0, self.dy - deceleration * 0.016)
            elif self.dy < 0:
                self.dy = min(0, self.dy + deceleration * 0.016)
            
    def update(self, dt: float):
        """Update player state."""
        # Move based on current velocity
        if self.dx != 0 or self.dy != 0:
            # Calculate movement for this frame
            move_x = self.dx * dt
            move_y = self.dy * dt
            
            # Apply movement with collision check
            self.move(move_x, move_y, [])  # We'll handle wall collisions in move()
            
        # Update animation
        self.animation.update(dt)
        
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Draw the player on the screen.
        
        Args:
            screen: The pygame surface to draw on
            camera: The camera object tracking the player
        """
        # Calculate screen position
        screen_x = int(self.x + camera.x)
        screen_y = int(self.y + camera.y)
        
        # Draw player using animation system
        self.animation.draw(screen, (screen_x, screen_y), TILE_SIZE)
        
        # Draw debug info if needed
        if hasattr(self, 'DEBUG') and self.DEBUG:
            # Draw hitbox
            pygame.draw.rect(screen, (255, 0, 0), 
                            (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
            # Draw coordinates
            font = pygame.font.Font(None, 24)
            text = font.render(f"({int(self.x)}, {int(self.y)})", True, (255, 255, 255))
            screen.blit(text, (screen_x, screen_y - 20))
        
    def move(self, dx: int, dy: int, walls: List[pygame.Rect]) -> None:
        """
        Move the player by the given delta, checking for collisions.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            walls: List of wall rectangles to check for collisions
        """
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Map boundary constraints
        # Keep player within map bounds (assuming map is 50x50 tiles)
        map_width = 50 * TILE_SIZE
        map_height = 50 * TILE_SIZE
        
        # Constrain x position
        if new_x < 0:
            new_x = 0
        elif new_x > map_width - TILE_SIZE:
            new_x = map_width - TILE_SIZE
            
        # Constrain y position
        if new_y < 0:
            new_y = 0
        elif new_y > map_height - TILE_SIZE:
            new_y = map_height - TILE_SIZE
            
        # Update position
        self.x = new_x
        self.y = new_y
        
        # Update collision rectangle with margin
        collision_margin = 4
        self.rect.x = self.x + collision_margin
        self.rect.y = self.y + collision_margin
        
        # Check for collisions and revert if needed
        if self._check_collision(walls):
            self.x -= dx
            self.y -= dy
            self.rect.x = self.x + collision_margin
            self.rect.y = self.y + collision_margin
            
    def _check_collision(self, walls: List[pygame.Rect]) -> bool:
        """
        Check if the player collides with any walls.
        
        Args:
            walls: List of wall rectangles to check against
            
        Returns:
            True if there is a collision, False otherwise
        """
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False
        
    def add_item(self, item: Item) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: The item to add
            
        Returns:
            True if the item was added successfully, False if inventory is full
        """
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                return True
        return False
        
    def equip_item(self, inventory_index: int) -> bool:
        """
        Equip an item from the inventory.
        
        Args:
            inventory_index: Index of the item in inventory to equip
            
        Returns:
            True if the item was equipped successfully
        """
        if not (0 <= inventory_index < len(self.inventory)):
            return False
            
        item = self.inventory[inventory_index]
        if item is None:
            return False
            
        # Determine equipment slot based on item type
        slot = None
        if isinstance(item, Item):
            if hasattr(item, 'weapon_type'):
                slot = 'weapon'
            elif hasattr(item, 'armor_type'):
                slot = item.armor_type
                
        if slot and slot in self.equipment:
            # Unequip current item if any
            current_item = self.equipment[slot]
            if current_item:
                self.inventory[inventory_index] = current_item
                
            # Equip new item
            self.equipment[slot] = item
            self.inventory[inventory_index] = None
            return True
            
        return False
        
    def add_experience(self, amount: int) -> None:
        """
        Add experience points to the player.
        
        Args:
            amount: Amount of experience to add
        """
        self.experience += amount
        # TODO: Add level up logic based on experience thresholds
        
    def add_gold(self, amount: int) -> None:
        """
        Add gold to the player's currency.
        
        Args:
            amount: Amount of gold to add
        """
        self.gold += amount
        
    def get_center_position(self) -> Tuple[int, int]:
        """Get the center position of the player for camera tracking."""
        return (self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert player state to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "speed": self.speed,
            "level": self.level,
            "experience": self.experience,
            "gold": self.gold,
            "inventory": [
                item.to_dict() if item else None
                for item in self.inventory
            ],
            "equipment": {
                slot: item.to_dict() if item else None
                for slot, item in self.equipment.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a player from dictionary data."""
        player = cls(data["x"], data["y"])
        player.speed = data["speed"]
        player.level = data.get("level", 1)
        player.experience = data.get("experience", 0)
        player.gold = data.get("gold", 0)
        
        # Restore inventory
        for i, item_data in enumerate(data["inventory"]):
            if item_data:
                player.inventory[i] = Item.from_dict(item_data)
                
        # Restore equipment
        for slot, item_data in data["equipment"].items():
            if item_data:
                player.equipment[slot] = Item.from_dict(item_data)
                
        return player 