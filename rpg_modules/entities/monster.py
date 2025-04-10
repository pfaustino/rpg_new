from ..animations import MonsterAnimation, Direction, AnimationState
import pygame
from typing import Tuple, Optional, List
from enum import Enum
import random
import math
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from ..utils.logging import logger

class MonsterType(Enum):
    # Original monsters
    DRAGON = "dragon"
    SPIDER = "spider"
    GHOST = "ghost"
    SKELETON = "skeleton"
    SLIME = "slime"
    
    # Elemental creatures
    FIRE_ELEMENTAL = "fire_elemental"
    ICE_ELEMENTAL = "ice_elemental"
    STORM_ELEMENTAL = "storm_elemental"
    EARTH_GOLEM = "earth_golem"
    
    # Undead
    ZOMBIE = "zombie"
    WRAITH = "wraith"
    VAMPIRE = "vampire"
    LICH = "lich"
    
    # Magical creatures
    PIXIE = "pixie"
    PHOENIX = "phoenix"
    UNICORN = "unicorn"
    GRIFFIN = "griffin"
    
    # Forest creatures
    TREANT = "treant"
    WOLF = "wolf"
    BEAR = "bear"
    DRYAD = "dryad"
    
    # Dark creatures
    DEMON = "demon"
    SHADOW_STALKER = "shadow_stalker"
    NIGHTMARE = "nightmare"
    DARK_WIZARD = "dark_wizard"
    
    # Aquatic creatures
    MERFOLK = "merfolk"
    KRAKEN = "kraken"
    SIREN = "siren"
    LEVIATHAN = "leviathan"
    
    # Insectoids
    GIANT_ANT = "giant_ant"
    SCORPION = "scorpion"
    MANTIS = "mantis"
    BEETLE = "beetle"
    
    # Celestial beings
    ANGEL = "angel"
    COSMIC_WYRM = "cosmic_wyrm"
    VOID_WALKER = "void_walker"
    
    # Constructs
    CLOCKWORK_KNIGHT = "clockwork_knight"
    STEAM_GOLEM = "steam_golem"
    ARCANE_TURRET = "arcane_turret"
    LIVING_ARMOR = "living_armor"
    
    # Plant creatures
    VENUS_TRAP = "venus_trap"
    MUSHROOM_KING = "mushroom_king"
    THORN_ELEMENTAL = "thorn_elemental"
    ANCIENT_VINE = "ancient_vine"
    
    # Desert dwellers
    SAND_WURM = "sand_wurm"
    MUMMY_LORD = "mummy_lord"
    DUST_DJINN = "dust_djinn"
    SCARAB_SWARM = "scarab_swarm"
    
    # Mountain dwellers
    ROCK_GIANT = "rock_giant"
    HARPY = "harpy"
    FROST_TITAN = "frost_titan"
    THUNDER_BIRD = "thunder_bird"
    
    # Swamp creatures
    BOG_WITCH = "bog_witch"
    HYDRA = "hydra"
    MUSHROOM_ZOMBIE = "mushroom_zombie"
    WILL_O_WISP = "will_o_wisp"
    
    # Cosmic Horrors
    ELDER_BEING = "elder_being"
    MIND_FLAYER = "mind_flayer"
    CHAOS_SPAWN = "chaos_spawn"
    VOID_HORROR = "void_horror"
    
    # Mechanical Beasts
    MECHA_DRAGON = "mecha_dragon"
    LASER_HOUND = "laser_hound"
    NANO_SWARM = "nano_swarm"
    WAR_GOLEM = "war_golem"
    
    # Crystal Creatures
    CRYSTAL_GOLEM = "crystal_golem"
    PRISM_ELEMENTAL = "prism_elemental"
    GEM_BASILISK = "gem_basilisk"
    DIAMOND_PHOENIX = "diamond_phoenix"
    
    # Netherworldly
    SOUL_REAPER = "soul_reaper"
    CHAOS_DEMON = "chaos_demon"
    HELL_KNIGHT = "hell_knight"
    PLAGUE_BEARER = "plague_bearer"
    
    # Time Entities
    CHRONO_WRAITH = "chrono_wraith"
    TEMPORAL_TITAN = "temporal_titan"
    EPOCH_SPHINX = "epoch_sphinx"
    TIME_WEAVER = "time_weaver"
    
    # Dream Creatures
    NIGHTMARE_WEAVER = "nightmare_weaver"
    DREAM_EATER = "dream_eater"
    SLEEP_WALKER = "sleep_walker"
    MORPHEUS_SPAWN = "morpheus_spawn"
    
    # Astral Beings
    CONSTELLATION_AVATAR = "constellation_avatar"
    METEOR_RIDER = "meteor_rider"
    NEBULA_WEAVER = "nebula_weaver"
    SOLAR_PHOENIX = "solar_phoenix"
    
    # Primal Forces
    ANCIENT_TITAN = "ancient_titan"
    PRIMORDIAL_WYRM = "primordial_wyrm"
    GENESIS_SPIRIT = "genesis_spirit"
    ETERNAL_FLAME = "eternal_flame"
    
    # Quantum Entities
    SCHRODINGER_BEAST = "schrodinger_beast"
    QUANTUM_SHIFTER = "quantum_shifter"
    PROBABILITY_WEAVER = "probability_weaver"
    ENTANGLED_HORROR = "entangled_horror"
    
    # Mythic Beasts
    CHIMERA_LORD = "chimera_lord"
    WORLD_SERPENT = "world_serpent"
    GOLDEN_GUARDIAN = "golden_guardian"
    FATE_SPHINX = "fate_sphinx"
    
    # Psychic Anomalies
    THOUGHT_DEVOURER = "thought_devourer"
    MEMORY_PHANTOM = "memory_phantom"
    PSYCHIC_HYDRA = "psychic_hydra"
    MIND_COLOSSUS = "mind_colossus"
    
    # Void Entities
    NULL_WALKER = "null_walker"
    ENTROPY_BEAST = "entropy_beast"
    VOID_LEVIATHAN = "void_leviathan"
    COSMIC_HORROR = "cosmic_horror"
    
    # Astral Beings
    NEBULA_PHANTOM = "nebula_phantom"
    COSMIC_GUARDIAN = "cosmic_guardian"
    ASTRAL_WALKER = "astral_walker"
    
    # Elemental Spirits
    FIRE_SPIRIT = "fire_spirit"
    WATER_SPIRIT = "water_spirit"
    EARTH_SPIRIT = "earth_spirit"
    AIR_SPIRIT = "air_spirit"
    
    # Nature Spirits
    FOREST_GUARDIAN = "forest_guardian"
    VINE_WEAVER = "vine_weaver"
    MOSS_BEAST = "moss_beast"
    BLOOM_SPIRIT = "bloom_spirit"

class Monster:
    """Class representing a monster in the game."""
    
    def __init__(self, x, y, monster_type):
        self.x = x
        self.y = y
        # Ensure monster_type is a MonsterType enum
        if isinstance(monster_type, str):
            try:
                self.monster_type = MonsterType[monster_type.upper()]
            except KeyError:
                logger.error(f"Invalid monster type: {monster_type}")
                self.monster_type = MonsterType.SLIME  # Default to slime if invalid
        else:
            self.monster_type = monster_type
        
        self.animation = MonsterAnimation(self.monster_type)
        self.direction = Direction.DOWN
        self.moving = False
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.size = 32  # For slime splitting
        self.attack_range = 1.5  # In tiles
        self.attack_damage = 10
        self.attack_cooldown = 1000  # milliseconds
        self.last_attack_time = 0
        self.chase_range = 5  # Added for the new update method
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
        return current_time - self.last_attack_time >= self.attack_cooldown

    def attack(self):
        """Perform an attack and return damage value."""
        self.last_attack_time = pygame.time.get_ticks()
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
        
    def get_stats(self) -> dict:
        """Get the monster's stats."""
        return {
            "type": self.monster_type,
            "position": self.get_position(),
            "health": self.health,
            "max_health": self.max_health,
            "attack_damage": self.attack_damage,
            "speed": self.speed
        }
        
    def get_type(self) -> MonsterType:
        """Get the monster's type."""
        return self.monster_type