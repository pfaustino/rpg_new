from ..animations import MonsterAnimation, Direction, AnimationState
import pygame
from typing import Tuple, Optional, List, Dict, Any
from enum import Enum
import random
import math
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from ..utils.logging import logger

class MonsterType(Enum):
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
        self.value = name
        self.base_health = base_health
        self.base_damage = base_damage
        self.base_speed = base_speed
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown

class Monster:
    """Class representing a monster in the game."""
    
    def __init__(self, x: float, y: float, monster_type: MonsterType):
        """Initialize a monster at the given position."""
        self.x = x
        self.y = y
        self.monster_type = monster_type
        
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
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If player is within chase range, move towards them
        if distance < self.chase_range * TILE_SIZE:  # Convert chase range to pixels
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance
            
            # Move in the direction with larger component
            if abs(dx) > abs(dy):
                self.x += dx * self.speed * dt
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.y += dy * self.speed * dt
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
            
            self.moving = True
        else:
            # Random movement when not chasing
            if random.random() < 0.02:  # 2% chance to change direction each frame
                self.direction = random.choice(list(Direction))
            
            # Move in current direction
            if self.direction == Direction.UP:
                self.y -= self.speed * dt
            elif self.direction == Direction.DOWN:
                self.y += self.speed * dt
            elif self.direction == Direction.LEFT:
                self.x -= self.speed * dt
            elif self.direction == Direction.RIGHT:
                self.x += self.speed * dt
            
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
            
            # Draw monster type text above monster
            font_size = max(10, int(20 * zoom))
            font = pygame.font.Font(None, font_size)
            text = self.monster_type.name
            text_surface = font.render(text, True, (255, 255, 255))
            text_x = screen_x + (scaled_size - text_surface.get_width()) // 2
            text_y = screen_y - int(20 * zoom)
            screen.blit(text_surface, (text_x, text_y))

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