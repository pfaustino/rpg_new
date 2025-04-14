"""
Player entity class for RPG games.
"""

import pygame
from typing import Optional, Dict, List, Any, Tuple
from ..items import Item, Inventory, Equipment
from ..quests import QuestLog
from ..core.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from ..animations.base import PlayerIcon
import random

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
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.stamina = 100
        self.max_stamina = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.experience = 0
        self.gold = 0
        self.direction = 'south'  # Default facing direction: north, east, south, west
        
        # Combat attributes
        self.attack_range = 1.5 * TILE_SIZE  # Attack range in pixels
        self.attack_cooldown = 500  # Cooldown in milliseconds
        self.last_attack_time = 0  # Last attack timestamp
        self.attack_type = 1  # Current attack type (1-4)
        
        # Create proper inventory and equipment objects
        self.inventory = Inventory(40)  # Inventory with 40 slots
        self.equipment = Equipment()    # Equipment with slots for different item types
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
        # Store the walls list for use in update and move methods
        self.walls = walls
        
        # Calculate target velocity based on input
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
            # Attempt to attack if cooldown has passed
            self.try_attack()
            
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
            self.move(move_x, move_y, self.walls)  # Use the walls list stored from handle_input
            
        # Update animation
        self.animation.update(dt)
        
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Draw the player on the screen.
        
        Args:
            screen: The pygame surface to draw on
            camera: The camera object tracking the player
        """
        # Get zoom level
        zoom = camera.get_zoom()
        
        # Calculate screen position with zoom
        screen_x = int((self.x + camera.x) * zoom)
        screen_y = int((self.y + camera.y) * zoom)
        
        # Scale the size based on zoom
        scaled_size = int(TILE_SIZE * zoom)
        
        # Draw player using animation system
        self.animation.draw(screen, (screen_x, screen_y), scaled_size)
        
        # Draw health bar above the player
        bar_width = scaled_size
        bar_height = max(4, int(6 * zoom))
        health_percent = self.health / self.max_health
        
        # Position the health bar above the player
        bar_x = screen_x
        bar_y = screen_y - int(15 * zoom)
        
        # Draw health bar background (dark red)
        pygame.draw.rect(screen, (100, 0, 0), 
                         (bar_x, bar_y, bar_width, bar_height))
        
        # Draw health bar fill (bright green/yellow/red based on health)
        if health_percent > 0:
            # Change color from green to red as health decreases
            if health_percent > 0.7:
                fill_color = (0, 200, 0)  # Green for high health
            elif health_percent > 0.3:
                fill_color = (200, 200, 0)  # Yellow for medium health
            else:
                fill_color = (200, 0, 0)  # Red for low health
            
            fill_width = int(bar_width * health_percent)
            pygame.draw.rect(screen, fill_color, 
                            (bar_x, bar_y, fill_width, bar_height))
        
        # Draw player level above health bar if not in debug mode
        if not hasattr(self, 'DEBUG') or not self.DEBUG:
            font_size = max(10, int(20 * zoom))
            font = pygame.font.Font(None, font_size)
            level_text = f"Player lvl {self.level}"
            level_surface = font.render(level_text, True, (255, 255, 255))
            level_x = screen_x + (scaled_size - level_surface.get_width()) // 2
            level_y = screen_y - int(35 * zoom)
            screen.blit(level_surface, (level_x, level_y))
        
        # Draw debug info if needed
        if hasattr(self, 'DEBUG') and self.DEBUG:
            # Draw hitbox
            pygame.draw.rect(screen, (255, 0, 0), 
                            (screen_x, screen_y, scaled_size, scaled_size), 1)
            # Draw coordinates
            font = pygame.font.Font(None, int(24 * zoom))
            text = font.render(f"({int(self.x)}, {int(self.y)})", True, (255, 255, 255))
            screen.blit(text, (screen_x, screen_y - int(20 * zoom)))
        
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
        # Only print wall count every 100 frames to reduce console spam
        if random.random() < 0.01:
            print(f"DEBUG: Checking collision with {len(walls)} walls")
            
        for wall in walls:
            if self.rect.colliderect(wall):
                # Only print collision detection occasionally to reduce console spam
                if random.random() < 0.05:
                    print(f"DEBUG: Collision detected with wall at ({wall.x/64:.1f}, {wall.y/64:.1f})")
                return True
        return False
        
    def add_item(self, item: Item) -> bool:
        """Add an item to the player's inventory."""
        if not item:
            print("WARNING: Attempted to add None item to inventory")
            return False
            
        # Try to add item to inventory
        success = self.inventory.add_item(item)
        
        # Print debug information about inventory status
        filled_slots = sum(1 for i in self.inventory.items if i is not None)
        total_slots = len(self.inventory.items)
        print(f"DEBUG: Inventory status after add attempt: {filled_slots}/{total_slots} slots filled")
        
        if success:
            print(f"Added {item.display_name} to inventory")
            # Try to refresh inventory UI through game_state
            try:
                import game
                if hasattr(game, 'game_state') and game.game_state:
                    if hasattr(game.game_state, 'refresh_inventory_ui'):
                        game.game_state.refresh_inventory_ui()
            except Exception as e:
                print(f"Could not refresh inventory UI from player: {e}")
        else:
            print(f"Inventory full, couldn't add {item.display_name}")
            
        return success
        
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
        
        # Check for level up
        # Simple formula: next level requires current_level * 100 XP
        xp_needed = self.level * 100
        
        if self.experience >= xp_needed:
            # Level up!
            self.level += 1
            self.experience -= xp_needed  # Subtract XP needed for level up
            
            # Increase stats
            self.max_health += 10
            self.health = self.max_health  # Heal to full on level up
            self.max_mana += 5
            self.mana = self.max_mana  # Restore mana on level up
            self.max_stamina += 5
            self.stamina = self.max_stamina  # Restore stamina on level up
            self.attack += 2
            self.defense += 1
            
            print(f"LEVEL UP! Player is now level {self.level}!")
            print(f"Health: {self.max_health}, Mana: {self.max_mana}, Attack: {self.attack}, Defense: {self.defense}")
            
            # Signal that a level-up occurred
            self.on_level_up()
        
    def on_level_up(self):
        """Called when player levels up - can be used to play sounds or show effects."""
        # This method is meant to be used by GameState to play sounds
        # It doesn't directly play sounds to maintain separation of concerns
        pass
        
    def add_gold(self, amount: int) -> None:
        """
        Add gold to the player's currency.
        
        Args:
            amount: Amount of gold to add
        """
        self.gold += amount
        
    def take_damage(self, damage: int) -> None:
        """
        Handle player taking damage from attacks.
        
        Args:
            damage: Amount of damage to take
        """
        # Apply defense reduction (simple formula: damage - defense/2)
        actual_damage = max(1, damage - (self.defense // 2))
        
        # Apply damage
        self.health -= actual_damage
        
        # Ensure health doesn't go below 0
        self.health = max(0, self.health)
        
        # Check if player died
        if self.health <= 0:
            self._handle_death()
            
    def _handle_death(self) -> None:
        """Handle player death."""
        # Reset health to 25% of max
        self.health = self.max_health // 4
        
        # Respawn at center of map (simple respawn logic)
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

    def try_attack(self) -> bool:
        """
        Attempt to perform an attack. Returns True if attack was performed.
        """
        current_time = pygame.time.get_ticks()
        
        # Check if cooldown has passed
        if current_time - self.last_attack_time < self.attack_cooldown:
            return False
            
        # Check resource requirements based on attack type
        if self.attack_type == 2 and self.stamina < 15:  # Heavy attack requires stamina
            print("Not enough stamina for Heavy attack!")
            return False
            
        if self.attack_type == 3 and self.mana < 20:  # Magic attack requires mana
            print("Not enough mana for Magic attack!")
            return False
            
        # Reset attack timer
        self.last_attack_time = current_time
        
        # Signal that attack was successful (actual target hit detection happens in GameState)
        return True
        
    def can_attack(self) -> bool:
        """Check if player can attack (cooldown has passed)."""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack_time >= self.attack_cooldown
        
    def get_attack_damage(self) -> int:
        """Get the player's attack damage, accounting for equipment and attack type."""
        base_damage = self.attack
        
        # Add weapon damage if equipped
        weapon = self.equipment.get_equipped_item('weapon') if hasattr(self.equipment, 'get_equipped_item') else None
        if weapon and hasattr(weapon, 'attack_power'):
            base_damage += weapon.attack_power
        
        # Apply modifiers based on attack type
        if self.attack_type == 1:
            # Regular attack - standard damage
            multiplier = 1.0
        elif self.attack_type == 2:
            # Heavy attack - more damage but uses stamina
            multiplier = 1.5
            # We've already checked in try_attack that stamina is sufficient
            self.stamina = max(0, self.stamina - 15)  # Cost: 15 stamina
            print(f"Used 15 stamina. Remaining: {self.stamina}/{self.max_stamina}")
        elif self.attack_type == 3:
            # Magic attack - uses mana
            multiplier = 2.0
            # We've already checked in try_attack that mana is sufficient
            self.mana = max(0, self.mana - 20)  # Cost: 20 mana
            print(f"Used 20 mana. Remaining: {self.mana}/{self.max_mana}")
        elif self.attack_type == 4:
            # Quick attack - less damage but faster cooldown
            multiplier = 0.7
            self.last_attack_time -= 200  # 200ms less cooldown
        else:
            multiplier = 1.0
            
        # Random variation (±10%)
        variation = random.uniform(0.9, 1.1)
        
        # Return final damage as integer
        return max(1, int(base_damage * multiplier * variation))
    
    def get_attack_type_name(self) -> str:
        """Get the name of the current attack type."""
        if self.attack_type == 1:
            return "Regular"
        elif self.attack_type == 2:
            return "Heavy"
        elif self.attack_type == 3:
            return "Magic"
        elif self.attack_type == 4:
            return "Quick"
        else:
            return "Unknown"
    
    def get_attack_range(self) -> float:
        """Get attack range, which may be modified by attack type."""
        base_range = self.attack_range
        
        # Magic attacks have longer range
        if self.attack_type == 3:
            return base_range * 1.5
        
        # Heavy attacks have slightly shorter range
        if self.attack_type == 2:
            return base_range * 0.8
            
        return base_range
    
    def switch_attack_type(self, new_type: int) -> bool:
        """
        Switch to a different attack type.
        
        Args:
            new_type: The attack type to switch to (1-4)
            
        Returns:
            True if the switch was successful, False otherwise
        """
        if not (1 <= new_type <= 4):
            return False
            
        # Check resource requirements
        if new_type == 2 and self.stamina < 15:  # Heavy attack
            return False
        if new_type == 3 and self.mana < 20:  # Magic attack
            return False
            
        self.attack_type = new_type
        return True 