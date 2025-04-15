from ..animations import MonsterAnimation, Direction, AnimationState
import pygame
from typing import Tuple, Optional, List, Dict, Any
from enum import Enum
import random
import math
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from ..utils.logging import logger
from ..core.settings import GameSettings
from rpg_modules.core.pathfinding import find_path

class MonsterType(Enum):
    # Format: (name, base_health, base_damage, base_speed, attack_range, attack_cooldown)
    
    # Original monsters
    DRAGON = ("dragon", 150, 20, 2.5, 2, 1500)
    SPIDER = ("spider", 60, 8, 3.0, 1, 800)
    GHOST = ("ghost", 50, 10, 2.0, 1, 1200)
    SKELETON = ("skeleton", 70, 12, 1.5, 1, 1000)
    SLIME = ("slime", 40, 5, 1.0, 1, 1500)
    
    # Elemental creatures
    FIRE_ELEMENTAL = ("fire_elemental", 90, 15, 2.0, 2, 1000)
    ICE_ELEMENTAL = ("ice_elemental", 85, 13, 1.8, 2, 1200)
    STORM_ELEMENTAL = ("storm_elemental", 80, 12, 2.5, 3, 1000)
    EARTH_GOLEM = ("earth_golem", 120, 18, 1.0, 1, 2000)
    
    # Undead
    ZOMBIE = ("zombie", 85, 10, 1.0, 1, 1500)
    WRAITH = ("wraith", 70, 15, 2.2, 1, 1200)
    VAMPIRE = ("vampire", 100, 14, 2.0, 1, 1000)
    LICH = ("lich", 130, 20, 1.5, 3, 1800)
    
    # Magical creatures
    PIXIE = ("pixie", 40, 8, 3.5, 1, 700)
    PHOENIX = ("phoenix", 110, 16, 2.8, 2, 1200)
    UNICORN = ("unicorn", 95, 12, 3.0, 1, 1000)
    GRIFFIN = ("griffin", 105, 15, 2.7, 1, 1100)
    
    # Forest creatures
    TREANT = ("treant", 120, 16, 1.0, 1, 1800)
    WOLF = ("wolf", 65, 9, 3.2, 1, 900)
    BEAR = ("bear", 100, 14, 2.0, 1, 1300)
    DRYAD = ("dryad", 75, 10, 2.5, 2, 1200)
    
    # Dark creatures
    DEMON = ("demon", 130, 18, 2.0, 2, 1300)
    SHADOW_STALKER = ("shadow_stalker", 90, 14, 2.4, 1, 1100)
    NIGHTMARE = ("nightmare", 100, 15, 2.8, 1, 1200)
    DARK_WIZARD = ("dark_wizard", 85, 17, 1.5, 3, 1500)
    
    # Aquatic creatures
    MERFOLK = ("merfolk", 80, 12, 2.5, 1, 1000)
    KRAKEN = ("kraken", 140, 19, 1.0, 3, 1700)
    SIREN = ("siren", 70, 15, 2.2, 2, 1100)
    LEVIATHAN = ("leviathan", 180, 22, 1.5, 2, 2000)
    
    # Insectoids
    GIANT_ANT = ("giant_ant", 60, 8, 3.0, 1, 800)
    SCORPION = ("scorpion", 75, 12, 2.0, 1, 1200)
    MANTIS = ("mantis", 70, 14, 2.5, 1, 1000)
    BEETLE = ("beetle", 90, 10, 1.5, 1, 1300)
    
    # Celestial beings
    ANGEL = ("angel", 120, 18, 2.5, 2, 1300)
    COSMIC_WYRM = ("cosmic_wyrm", 140, 20, 2.0, 2, 1500)
    VOID_WALKER = ("void_walker", 100, 15, 2.2, 1, 1200)
    
    # Constructs
    CLOCKWORK_KNIGHT = ("clockwork_knight", 100, 15, 2.0, 1, 1100)
    STEAM_GOLEM = ("steam_golem", 130, 17, 1.5, 1, 1600)
    ARCANE_TURRET = ("arcane_turret", 80, 16, 0.5, 4, 1200)
    LIVING_ARMOR = ("living_armor", 110, 14, 1.2, 1, 1400)
    
    # Plant creatures
    VENUS_TRAP = ("venus_trap", 80, 14, 0.5, 2, 1100)
    MUSHROOM_KING = ("mushroom_king", 100, 12, 1.0, 2, 1300)
    THORN_ELEMENTAL = ("thorn_elemental", 90, 15, 1.2, 1, 1200)
    ANCIENT_VINE = ("ancient_vine", 110, 13, 0.8, 3, 1500)
    
    # Desert dwellers
    SAND_WURM = ("sand_wurm", 120, 16, 1.5, 1, 1400)
    MUMMY_LORD = ("mummy_lord", 95, 13, 1.0, 1, 1300)
    DUST_DJINN = ("dust_djinn", 85, 14, 2.5, 2, 1100)
    SCARAB_SWARM = ("scarab_swarm", 70, 10, 3.0, 1, 900)
    
    # Mountain dwellers
    ROCK_GIANT = ("rock_giant", 150, 20, 1.0, 1, 1800)
    HARPY = ("harpy", 75, 12, 3.0, 1, 1000)
    FROST_TITAN = ("frost_titan", 140, 18, 1.2, 2, 1600)
    THUNDER_BIRD = ("thunder_bird", 90, 15, 3.2, 1, 1100)
    
    # Swamp creatures
    BOG_WITCH = ("bog_witch", 85, 16, 1.5, 2, 1300)
    HYDRA = ("hydra", 130, 17, 1.3, 2, 1500)
    MUSHROOM_ZOMBIE = ("mushroom_zombie", 75, 11, 1.0, 1, 1200)
    WILL_O_WISP = ("will_o_wisp", 50, 10, 3.5, 1, 800)
    
    # Cosmic Horrors
    ELDER_BEING = ("elder_being", 160, 22, 1.0, 3, 1800)
    MIND_FLAYER = ("mind_flayer", 110, 18, 1.5, 2, 1400)
    CHAOS_SPAWN = ("chaos_spawn", 120, 16, 2.0, 1, 1300)
    VOID_HORROR = ("void_horror", 140, 20, 1.2, 2, 1600)
    
    # Mechanical Beasts
    MECHA_DRAGON = ("mecha_dragon", 150, 19, 1.8, 2, 1500)
    LASER_HOUND = ("laser_hound", 80, 14, 3.0, 2, 1000)
    NANO_SWARM = ("nano_swarm", 70, 12, 3.5, 1, 800)
    WAR_GOLEM = ("war_golem", 140, 18, 1.0, 1, 1700)
    
    # Crystal Creatures
    CRYSTAL_GOLEM = ("crystal_golem", 120, 15, 1.2, 1, 1500)
    PRISM_ELEMENTAL = ("prism_elemental", 90, 16, 2.0, 2, 1200)
    GEM_BASILISK = ("gem_basilisk", 110, 17, 1.5, 1, 1400)
    DIAMOND_PHOENIX = ("diamond_phoenix", 130, 18, 2.2, 2, 1300)
    
    # Netherworldly
    SOUL_REAPER = ("soul_reaper", 110, 19, 2.0, 1, 1300)
    CHAOS_DEMON = ("chaos_demon", 125, 17, 1.8, 2, 1400)
    HELL_KNIGHT = ("hell_knight", 115, 16, 1.5, 1, 1300)
    PLAGUE_BEARER = ("plague_bearer", 100, 15, 1.2, 2, 1500)
    
    # Time Entities
    CHRONO_WRAITH = ("chrono_wraith", 100, 18, 2.5, 1, 1200)
    TEMPORAL_TITAN = ("temporal_titan", 140, 20, 1.5, 2, 1600)
    EPOCH_SPHINX = ("epoch_sphinx", 120, 17, 1.0, 3, 1800)
    TIME_WEAVER = ("time_weaver", 90, 16, 2.2, 2, 1300)
    
    # Dream Creatures
    NIGHTMARE_WEAVER = ("nightmare_weaver", 95, 17, 2.0, 2, 1300)
    DREAM_EATER = ("dream_eater", 105, 18, 1.8, 1, 1400)
    SLEEP_WALKER = ("sleep_walker", 80, 13, 1.5, 1, 1200)
    MORPHEUS_SPAWN = ("morpheus_spawn", 100, 15, 2.0, 2, 1300)
    
    # Astral Beings
    CONSTELLATION_AVATAR = ("constellation_avatar", 120, 16, 1.8, 2, 1500)
    METEOR_RIDER = ("meteor_rider", 105, 15, 2.5, 1, 1200)
    NEBULA_WEAVER = ("nebula_weaver", 110, 17, 2.0, 2, 1400)
    SOLAR_PHOENIX = ("solar_phoenix", 125, 18, 2.2, 2, 1300)
    
    # Primal Forces
    ANCIENT_TITAN = ("ancient_titan", 160, 21, 1.0, 2, 2000)
    PRIMORDIAL_WYRM = ("primordial_wyrm", 150, 19, 1.5, 2, 1800)
    GENESIS_SPIRIT = ("genesis_spirit", 120, 17, 2.0, 3, 1500)
    ETERNAL_FLAME = ("eternal_flame", 130, 18, 1.8, 2, 1600)
    
    # Quantum Entities
    SCHRODINGER_BEAST = ("schrodinger_beast", 100, 16, 2.5, 1, 1300)
    QUANTUM_SHIFTER = ("quantum_shifter", 95, 15, 3.0, 1, 1100)
    PROBABILITY_WEAVER = ("probability_weaver", 110, 17, 2.0, 2, 1400)
    ENTANGLED_HORROR = ("entangled_horror", 120, 18, 1.8, 2, 1500)
    
    # Mythic Beasts
    CHIMERA_LORD = ("chimera_lord", 140, 19, 2.0, 2, 1600)
    WORLD_SERPENT = ("world_serpent", 170, 22, 1.2, 2, 2000)
    GOLDEN_GUARDIAN = ("golden_guardian", 150, 20, 1.5, 2, 1800)
    FATE_SPHINX = ("fate_sphinx", 130, 18, 1.0, 3, 1700)
    
    # Psychic Anomalies
    THOUGHT_DEVOURER = ("thought_devourer", 110, 17, 2.0, 2, 1400)
    MEMORY_PHANTOM = ("memory_phantom", 95, 15, 2.5, 1, 1200)
    PSYCHIC_HYDRA = ("psychic_hydra", 125, 19, 1.5, 2, 1600)
    MIND_COLOSSUS = ("mind_colossus", 140, 20, 1.0, 3, 1800)
    
    # Void Entities
    NULL_WALKER = ("null_walker", 120, 18, 1.8, 2, 1500)
    ENTROPY_BEAST = ("entropy_beast", 130, 19, 1.5, 2, 1600)
    VOID_LEVIATHAN = ("void_leviathan", 160, 21, 1.0, 3, 2000)
    COSMIC_HORROR = ("cosmic_horror", 150, 20, 1.2, 3, 1800)
    
    # Astral Beings
    NEBULA_PHANTOM = ("nebula_phantom", 110, 17, 2.2, 2, 1400)
    COSMIC_GUARDIAN = ("cosmic_guardian", 130, 19, 1.8, 2, 1600)
    ASTRAL_WALKER = ("astral_walker", 120, 18, 2.0, 2, 1500)
    
    # Elemental Spirits
    FIRE_SPIRIT = ("fire_spirit", 90, 16, 2.5, 2, 1200)
    WATER_SPIRIT = ("water_spirit", 85, 15, 2.2, 2, 1300)
    EARTH_SPIRIT = ("earth_spirit", 100, 17, 1.5, 2, 1400)
    AIR_SPIRIT = ("air_spirit", 80, 14, 3.0, 2, 1100)
    
    # Nature Spirits
    FOREST_GUARDIAN = ("forest_guardian", 110, 16, 1.8, 2, 1500)
    VINE_WEAVER = ("vine_weaver", 95, 15, 2.0, 2, 1300)
    MOSS_BEAST = ("moss_beast", 105, 16, 1.5, 1, 1400)
    BLOOM_SPIRIT = ("bloom_spirit", 90, 14, 2.2, 2, 1200)
    
    def __init__(self, name, base_health, base_damage, base_speed, attack_range, attack_cooldown):
        # The first value is used as the enum value
        self._value_ = name
        self.base_health = base_health
        self.base_damage = base_damage
        self.base_speed = base_speed
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown

class Monster:
    """Class representing a monster in the game."""
    
    def __init__(self, x: float, y: float, monster_type: MonsterType, game_map=None):
        """Initialize a monster at the given position."""
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.game_map = game_map
        
        # Set default attributes based on type
        self.max_health = monster_type.base_health
        self.health = self.max_health
        self.attack_damage = monster_type.base_damage
        self.speed = monster_type.base_speed
        self.attack_range = monster_type.attack_range
        self.attack_cooldown = monster_type.attack_cooldown
        self.attack_timer = 0
        self.size = 32  # Default size for rendering
        self.direction = random.randint(0, 3)  # Random initial direction
        self.move_timer = 0
        self.chasing = False
        self.chase_range = 200
        self.level = 1  # Initialize monster level
        
        # Animation state
        self.animation_timer = 0
        self.frame = 0
        self.moving = False
        self.facing = 'down'
        
        self.animation = MonsterAnimation(self.monster_type)
        logger.log(f"Created {self.monster_type.name} monster at ({x}, {y})")

    def update(self, dt, player_pos):
        """Update monster state and position."""
        # Import game settings
        from rpg_modules.core.settings import GameSettings
        
        # Get the current monster speed multiplier
        monster_speed_multiplier = GameSettings.instance().monster_speed_multiplier
        
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Path to follow
        self.path = None
        
        # If player is within chase range, use pathfinding to move towards them
        if distance < self.chase_range * TILE_SIZE:  # Convert chase range to pixels
            # Use A* pathfinding to find a path to the player
            if hasattr(self, 'game_map') and self.game_map:
                # Only calculate a new path every so often to save performance
                if not hasattr(self, 'path_timer') or self.path_timer <= 0:
                    self.path = find_path(
                        self.game_map,
                        (self.x, self.y),
                        player_pos,
                        max_distance=20,
                        wall_clearance=1.0  # Lower clearance for monsters
                    )
                    # Set a timer for recalculating the path (every 1 second)
                    self.path_timer = 1.0
                else:
                    self.path_timer -= dt
                    
            # If we have a valid path, follow it
            if self.path and len(self.path) > 1:
                # Get the next point in the path
                next_pos = self.path[1]  # Skip the first point which is our current position
                
                # Calculate direction to the next point
                dx = next_pos[0] - self.x
                dy = next_pos[1] - self.y
                
                # Normalize direction
                path_distance = math.sqrt(dx * dx + dy * dy)
                if path_distance > 0:
                    dx /= path_distance
                    dy /= path_distance
                    
                    # Store current position for collision check
                    old_x = self.x
                    old_y = self.y
                    
                    # Move toward the next point
                    self.x += dx * self.speed * monster_speed_multiplier * dt
                    self.y += dy * self.speed * monster_speed_multiplier * dt
                    
                    # Update visual direction
                    if abs(dx) > abs(dy):
                        self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                    else:
                        self.direction = Direction.DOWN if dy > 0 else Direction.UP
                    
                    # Check for collisions
                    is_collision = False
                    if hasattr(self, 'game_map') and self.game_map:
                        # Get the tile coordinates for the monster's center
                        center_tile_x = int(self.x // TILE_SIZE)
                        center_tile_y = int(self.y // TILE_SIZE)
                        
                        # Check if the tile at that position is walkable
                        if not self.game_map.is_walkable(center_tile_x, center_tile_y):
                            is_collision = True
                    
                    # If there's a collision, revert to old position
                    if is_collision:
                        self.x = old_x
                        self.y = old_y
                        # Force path recalculation on next update
                        self.path_timer = 0
                    
                    self.moving = True
                    
                # If we're close to the next path point, remove it
                if path_distance < (self.speed * monster_speed_multiplier * dt):
                    # We've reached this point, remove it from the path
                    if len(self.path) > 1:
                        self.path.pop(0)
            else:
                # If pathfinding failed but player is in range, fall back to direct movement
                # Normalize direction vector
                if distance > 0:
                    dx = player_pos[0] - self.x
                    dy = player_pos[1] - self.y
                    dx /= distance
                    dy /= distance
                
                # Store current position for collision check
                old_x = self.x
                old_y = self.y
                
                # Move in the direction with larger component
                if abs(dx) > abs(dy):
                    self.x += dx * self.speed * monster_speed_multiplier * dt
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.y += dy * self.speed * monster_speed_multiplier * dt
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
                
                # Check for collisions
                is_collision = False
                if hasattr(self, 'game_map') and self.game_map:
                    center_tile_x = int(self.x // TILE_SIZE)
                    center_tile_y = int(self.y // TILE_SIZE)
                    
                    if not self.game_map.is_walkable(center_tile_x, center_tile_y):
                        is_collision = True
                
                # If there's a collision, revert to old position
                if is_collision:
                    self.x = old_x
                    self.y = old_y
                
                self.moving = True
        else:
            # Random movement when not chasing
            if random.random() < 0.02:  # 2% chance to change direction each frame
                self.direction = random.choice(list(Direction))
            
            # Store current position to check for collisions
            old_x = self.x
            old_y = self.y
            
            # Move in current direction
            if self.direction == Direction.UP:
                self.y -= self.speed * monster_speed_multiplier * dt
            elif self.direction == Direction.DOWN:
                self.y += self.speed * monster_speed_multiplier * dt
            elif self.direction == Direction.LEFT:
                self.x -= self.speed * monster_speed_multiplier * dt
            elif self.direction == Direction.RIGHT:
                self.x += self.speed * monster_speed_multiplier * dt
            
            # Simple collision detection
            is_collision = False
            if hasattr(self, 'game_map') and self.game_map:
                center_tile_x = int(self.x // TILE_SIZE)
                center_tile_y = int(self.y // TILE_SIZE)
                
                if not self.game_map.is_walkable(center_tile_x, center_tile_y):
                    is_collision = True
            
            # If there's a collision, revert to old position
            if is_collision:
                self.x = old_x
                self.y = old_y
            
            self.moving = True
        
        # Update animation state
        self.animation.update(self.moving)

    def draw(self, screen, camera):
        """Draw the monster on the screen."""
        # Get camera zoom level
        zoom = camera.get_zoom()
        
        # Calculate screen position with zoom
        screen_x = int((self.x + camera.x) * zoom)
        screen_y = int((self.y + camera.y) * zoom)
        
        # Calculate scaled size
        scaled_size = int(TILE_SIZE * zoom)
        
        # Only draw if on screen (with margin)
        if -scaled_size <= screen_x <= SCREEN_WIDTH and -scaled_size <= screen_y <= SCREEN_HEIGHT:
            # Draw the monster using its animation system
            self.animation.draw(screen, 
                               screen_x + scaled_size // 2, 
                               screen_y + scaled_size // 2, 
                               self.direction,
                               size=scaled_size)
            
            # Draw the path if debug visualization is enabled
            if GameSettings.instance().debug_visualization and hasattr(self, 'path') and self.path:
                for i in range(len(self.path) - 1):
                    # Convert path points to screen coordinates
                    start_x = int((self.path[i][0] + camera.x) * zoom)
                    start_y = int((self.path[i][1] + camera.y) * zoom)
                    end_x = int((self.path[i+1][0] + camera.x) * zoom)
                    end_y = int((self.path[i+1][1] + camera.y) * zoom)
                    
                    # Draw path segment as a line
                    pygame.draw.line(screen, (255, 0, 255), (start_x, start_y), (end_x, end_y), 2)
            
            # Draw health bar above the monster
            bar_width = scaled_size
            bar_height = max(4, int(6 * zoom))
            health_percent = self.health / self.max_health
            
            # Position the health bar above the monster and its name
            bar_x = screen_x
            bar_y = screen_y - int(28 * zoom)
            
            # Draw health bar background (dark red)
            pygame.draw.rect(screen, (100, 0, 0), 
                            (bar_x, bar_y, bar_width, bar_height))
            
            # Draw health bar fill (bright red/green based on health)
            if health_percent > 0:
                # Change color from green to red as health decreases
                green = int(200 * health_percent)
                red = int(200 * (1 - health_percent) + 55)
                fill_color = (red, green, 0)
                
                fill_width = int(bar_width * health_percent)
                pygame.draw.rect(screen, fill_color, 
                               (bar_x, bar_y, fill_width, bar_height))
            
            # Draw monster type text above health bar
            font_size = max(10, int(20 * zoom))
            font = pygame.font.Font(None, font_size)
            text = f"{self.monster_type.name} lvl {self.level}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_x = screen_x + (scaled_size - text_surface.get_width()) // 2
            text_y = screen_y - int(45 * zoom)
            screen.blit(text_surface, (text_x, text_y))
            
            # Only draw debug visualization if enabled in settings
            if GameSettings.instance().debug_visualization:
                # Draw center point (red circle)
                center_x = int((self.x + camera.x) * zoom)
                center_y = int((self.y + camera.y) * zoom)
                pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), 4)
                
                # Draw the collision detection points (the 75% sized box)
                detect_size = int(self.size * 0.75)
                half_detect = detect_size // 2
                scaled_half = int(half_detect * zoom)
                
                # Draw the detection box (blue rectangle)
                detect_rect = pygame.Rect(
                    center_x - scaled_half,
                    center_y - scaled_half,
                    scaled_half * 2,
                    scaled_half * 2
                )
                pygame.draw.rect(screen, (0, 0, 255), detect_rect, 2)
                
                # Draw the detection points (yellow circles)
                points = [
                    (center_x - scaled_half, center_y),  # Left
                    (center_x + scaled_half, center_y),  # Right
                    (center_x, center_y - scaled_half),  # Top
                    (center_x, center_y + scaled_half)   # Bottom
                ]
                for point in points:
                    pygame.draw.circle(screen, (255, 255, 0), point, 3)
                
                # Draw the current tile grid position (green rectangle)
                tile_x = int(self.x // TILE_SIZE)
                tile_y = int(self.y // TILE_SIZE)
                tile_screen_x = int((tile_x * TILE_SIZE + camera.x) * zoom)
                tile_screen_y = int((tile_y * TILE_SIZE + camera.y) * zoom)
                tile_rect = pygame.Rect(
                    tile_screen_x,
                    tile_screen_y,
                    int(TILE_SIZE * zoom),
                    int(TILE_SIZE * zoom)
                )
                pygame.draw.rect(screen, (0, 255, 0), tile_rect, 2)

    def _get_monster_color(self):
        """Get color based on monster type."""
        colors = {
            MonsterType.SLIME: (0, 255, 0),      # Green
            MonsterType.SPIDER: (139, 69, 19),   # Brown
            MonsterType.WOLF: (128, 128, 128),   # Gray
            MonsterType.GHOST: (200, 200, 255),  # Light blue
            MonsterType.SKELETON: (255, 255, 240) # Off-white
        }
        return colors.get(self.monster_type, (255, 0, 0))  # Default to red

    def can_attack(self):
        """Check if the monster can attack based on cooldown."""
        current_time = pygame.time.get_ticks()
        return current_time - self.attack_timer >= self.attack_cooldown

    def attack(self):
        """Perform an attack and return damage value."""
        self.attack_timer = pygame.time.get_ticks()
        return self.attack_damage

    def get_rect(self) -> pygame.Rect:
        """Get the monster's collision rectangle."""
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        
    def get_center(self) -> Tuple[int, int]:
        """Get the center position of the monster."""
        return (self.x, self.y)
        
    def get_position(self) -> Tuple[int, int]:
        """Get the position of the monster."""
        return (self.x, self.y)
        
    def get_stats(self):
        """Get monster stats for display."""
        return {
            'name': self.monster_type.name,
            'level': self.level,
            'health': self.health,
            'max_health': self.max_health,
            'attack': self.attack_damage,
            'speed': self.speed,
            'attack_range': self.attack_range
        }
        
    def get_type(self) -> MonsterType:
        """Get the monster's type."""
        return self.monster_type