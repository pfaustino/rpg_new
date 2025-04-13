from typing import Tuple, Optional, Dict, Any, List
import pygame
from ..core.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from ..items.base import Inventory
from ..animations.base import PlayerIcon

class Player:
    """Class representing the player character."""
    
    def __init__(self, x: float, y: float, assets: Dict[str, pygame.Surface]):
        """Initialize the player."""
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.speed = 200
        self.animation = PlayerIcon()
        self.hp = 100
        self.max_hp = 100
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.stamina = 100
        self.max_stamina = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.xp = 0
        self.experience = 0
        self.gold = 0
        self.direction = 'south'  # Default facing direction: north, east, south, west
        self.assets = assets
        
        # Combat attributes
        self.attack_range = 1.5 * TILE_SIZE  # Attack range in pixels
        self.attack_cooldown = 500  # Cooldown in milliseconds
        self.last_attack_time = 0  # Last attack timestamp
        self.attack_type = 1  # Current attack type (1-4)
        self.base_attack = 10
        self.dexterity = 10
        
        # Create proper inventory and equipment objects
        self.inventory = Inventory(40)  # Inventory with 40 slots
        self.equipment = None  # Will be set to EquipmentManager in game.py
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
        
        # Load sprite
        self.sprite = assets.get('player', self._create_default_sprite())
        
    def handle_input(self, keys: pygame.key.ScancodeWrapper, walls: List[pygame.Rect]) -> None:
        """
        Handle player input for movement and actions.
        
        Args:
            keys: Current state of keyboard input
            walls: List of wall rectangles to check for collisions
        """
        # Store walls for collision in update
        self.walls = walls
        
        # Set target velocity based on input
        target_dx = 0
        target_dy = 0
        
        # Handle movement input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_dx = -self.speed
            self.direction = 'west'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_dx = self.speed
            self.direction = 'east'
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_dy = -self.speed
            # Only set north direction if not also moving horizontally
            if target_dx == 0:
                self.direction = 'north'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_dy = self.speed
            # Only set south direction if not also moving horizontally
            if target_dx == 0:
                self.direction = 'south'
            
        # Handle attack input (spacebar)
        if keys[pygame.K_SPACE]:
            self.attack()
        
        # Apply acceleration and deceleration for smoother movement
        acceleration = 800  # Units per second^2
        deceleration = 1200  # Units per second^2
        
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
            self.move(move_x, move_y, self.walls)  # Use the walls list stored from handle_input
            
        # Update animation
        self.animation.update(dt)
            
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Draw the player on the screen.
        
        Args:
            screen: The pygame surface to draw on
            camera: The camera object for position calculations
        """
        # Get zoom level from camera
        zoom = camera.zoom
        
        # Calculate screen position with zoom
        screen_x = int((self.x + camera.x) * zoom)
        screen_y = int((self.y + camera.y) * zoom)
        
        # Scale the size based on zoom
        scaled_size = int(TILE_SIZE * zoom)
        
        # Draw player using animation system
        self.animation.draw(screen, (screen_x, screen_y), scaled_size)
        
        # Draw health bar above the player
        bar_height = int(5 * zoom)
        bar_width = int(TILE_SIZE * zoom)
        bar_y = screen_y - int(10 * zoom)
        
        # Background (black)
        pygame.draw.rect(screen, (0, 0, 0), (screen_x, bar_y, bar_width, bar_height))
        
        # Health foreground (red)
        health_percent = self.health / self.max_health
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(screen, (255, 0, 0), (screen_x, bar_y, health_width, bar_height))
        
        # Debug info
        if True:  # Change to False in production
            # Draw coordinates
            font = pygame.font.Font(None, int(24 * zoom))
            text = font.render(f"({int(self.x)}, {int(self.y)})", True, (255, 255, 255))
            screen.blit(text, (screen_x, screen_y - int(20 * zoom)))
        
    def move(self, dx: float, dy: float, walls: List[pygame.Rect]) -> None:
        """
        Move the player while checking for collisions.
        
        Args:
            dx: Change in x position
            dy: Change in y position
            walls: List of wall rectangles to check for collisions
        """
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Map boundary constraints
        map_width = 50 * TILE_SIZE
        map_height = 50 * TILE_SIZE
        
        # Keep player within map boundaries
        if new_x < 0:
            new_x = 0
        elif new_x > map_width - TILE_SIZE:
            new_x = map_width - TILE_SIZE
            
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
        Check if player is colliding with any walls.
        
        Args:
            walls: List of wall rectangles
            
        Returns:
            True if there is a collision, False otherwise
        """
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def attack(self) -> None:
        """Perform attack action."""
        # Check attack cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return  # Still cooling down
            
        # Update last attack time
        self.last_attack_time = current_time
        print(f"Player attacked in direction: {self.direction}")
        
    def add_gold(self, amount: int) -> None:
        """Add gold to player's purse."""
        if amount <= 0:
            return
        self.gold += amount
        print(f"Added {amount} gold. Total: {self.gold}")

    def add_xp(self, amount: int) -> None:
        """
        Add experience points and check for level up.
        
        Args:
            amount: Amount of experience to add
        """
        self.xp += amount
        self.experience += amount
        
        # Check for level up
        # Simple formula: next level requires current_level * 100 XP
        xp_needed = self.level * 100
        
        if self.xp >= xp_needed:
            # Level up!
            self.level += 1
            self.xp -= xp_needed  # Subtract XP needed for level up
            
            # Increase stats
            self.max_health += 10
            self.health = self.max_health  # Fully heal on level up
            self.max_mana += 5
            self.mana = self.max_mana  # Fully restore mana
            self.attack += 2
            self.defense += 1
            
            print(f"LEVEL UP! Now level {self.level}")
        
    def take_damage(self, amount: int) -> None:
        """Take damage and check if dead."""
        if amount <= 0:
            return
            
        # Apply defense reduction
        actual_damage = max(1, amount - self.defense // 2)
        self.health -= actual_damage
        print(f"Player took {actual_damage} damage. Health: {self.health}/{self.max_health}")
        
        # Check if dead
        if self.health <= 0:
            self.die()
            
    def heal(self, amount: int) -> None:
        """Heal the player."""
        if amount <= 0:
            return
            
        self.health = min(self.health + amount, self.max_health)
        print(f"Player healed {amount}. Health: {self.health}/{self.max_health}")
        
    def die(self) -> None:
        """Handle player death."""
        # Respawn at center of map
        self.health = self.max_health // 2  # Respawn with half health
        
        # Reset position to center of map
        map_width = 50 * TILE_SIZE
        map_height = 50 * TILE_SIZE
        self.x = map_width // 2
        self.y = map_height // 2
        
        print("Player died and respawned!")
        
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
            "experience": self.xp,
            "gold": self.gold,
            "inventory": [
                item.to_dict() if item else None 
                for item in self.inventory.items
            ] if hasattr(self.inventory, 'items') else [],
            "health": self.health,
            "max_health": self.max_health,
            "mana": self.mana,
            "max_mana": self.max_mana
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a Player instance from serialized data."""
        player = cls(data["x"], data["y"])
        player.speed = data["speed"]
        player.level = data.get("level", 1)
        player.xp = data.get("experience", 0)
        player.gold = data.get("gold", 0)
        
        # Load health and mana if available
        if "health" in data:
            player.health = data["health"]
        if "max_health" in data:
            player.max_health = data["max_health"]
        if "mana" in data:
            player.mana = data["mana"]
        if "max_mana" in data:
            player.max_mana = data["max_mana"]
            
        return player
    
    def _create_default_sprite(self) -> pygame.Surface:
        """Create a default sprite if none is provided."""
        sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Draw player as a blue circle
        pygame.draw.circle(sprite, (0, 0, 255), (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 2 - 2)
        return sprite 