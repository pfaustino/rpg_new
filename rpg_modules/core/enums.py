"""
Enumerations for the RPG game.
"""

from enum import Enum, auto

class Direction(Enum):
    """Direction enum for movement and animations."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class AnimationState(Enum):
    """Animation state for entities."""
    IDLE = auto()
    WALKING = auto()
    ATTACKING = auto()
    HURT = auto()
    DYING = auto()

class MonsterType(Enum):
    """Types of monsters in the game."""
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
    
    # Elemental Spirits
    FIRE_SPIRIT = "fire_spirit"
    WATER_SPIRIT = "water_spirit"
    EARTH_SPIRIT = "earth_spirit"
    AIR_SPIRIT = "air_spirit"

class TileType(Enum):
    """Types of tiles in the game map."""
    GRASS = "grass"
    DIRT = "dirt"
    STONE = "stone"
    SAND = "sand"
    WATER = "water"
    LAVA = "lava"
    ICE = "ice"
    SNOW = "snow"
    
    # Decorations and walls
    TREE = "tree"
    ROCK = "rock"
    BUSH = "bush"
    FLOWERS = "flowers"
    STONE_WALL = "stone_wall"
    WOOD_WALL = "wood_wall"
    
    # Special tiles
    PORTAL = "portal"
    CHEST = "chest"
    DOOR = "door"
    STAIRS_UP = "stairs_up"
    STAIRS_DOWN = "stairs_down" 