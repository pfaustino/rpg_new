"""
Monster Type Definitions
======================

This file contains the MonsterType enum used throughout the game.
Separated from monster.py to avoid circular dependencies.
"""

from enum import Enum, auto

class MonsterType(Enum):
    # Original monsters
    DRAGON = auto()
    SPIDER = auto()
    GHOST = auto()
    SKELETON = auto()
    SLIME = auto()
    
    # Elemental creatures
    FIRE_ELEMENTAL = auto()
    ICE_ELEMENTAL = auto()
    STORM_ELEMENTAL = auto()
    EARTH_GOLEM = auto()
    
    # Undead
    ZOMBIE = auto()
    WRAITH = auto()
    VAMPIRE = auto()
    LICH = auto()
    
    # Magical creatures
    PIXIE = auto()
    PHOENIX = auto()
    UNICORN = auto()
    GRIFFIN = auto()
    
    # Forest creatures
    TREANT = auto()
    WOLF = auto()
    BEAR = auto()
    DRYAD = auto()
    
    # Dark creatures
    DEMON = auto()
    SHADOW_STALKER = auto()
    NIGHTMARE = auto()
    DARK_WIZARD = auto()
    
    # Aquatic creatures
    MERFOLK = auto()
    KRAKEN = auto()
    SIREN = auto()
    LEVIATHAN = auto()
    
    # Insectoids
    GIANT_ANT = auto()
    SCORPION = auto()
    MANTIS = auto()
    BEETLE = auto()
    
    # Celestial beings
    ANGEL = auto()
    COSMIC_WYRM = auto()
    VOID_WALKER = auto()
    
    # Constructs
    CLOCKWORK_KNIGHT = auto()
    STEAM_GOLEM = auto()
    ARCANE_TURRET = auto()
    LIVING_ARMOR = auto()
    
    # Plant creatures
    VENUS_TRAP = auto()
    MUSHROOM_KING = auto()
    THORN_ELEMENTAL = auto()
    ANCIENT_VINE = auto()
    
    # Desert dwellers
    SAND_WURM = auto()
    MUMMY_LORD = auto()
    DUST_DJINN = auto()
    SCARAB_SWARM = auto()
    
    # Mountain dwellers
    ROCK_GIANT = auto()
    HARPY = auto()
    FROST_TITAN = auto()
    THUNDER_BIRD = auto()
    
    # Swamp creatures
    BOG_WITCH = auto()
    HYDRA = auto()
    MUSHROOM_ZOMBIE = auto()
    WILL_O_WISP = auto()
    
    # Cosmic Horrors
    ELDER_BEING = auto()
    MIND_FLAYER = auto()
    CHAOS_SPAWN = auto()
    VOID_HORROR = auto()
    
    # Mechanical Beasts
    MECHA_DRAGON = auto()
    LASER_HOUND = auto()
    NANO_SWARM = auto()
    WAR_GOLEM = auto()
    
    # Crystal Creatures
    CRYSTAL_GOLEM = auto()
    PRISM_ELEMENTAL = auto()
    GEM_BASILISK = auto()
    DIAMOND_PHOENIX = auto()
    
    # Netherworldly
    SOUL_REAPER = auto()
    CHAOS_DEMON = auto()
    HELL_KNIGHT = auto()
    PLAGUE_BEARER = auto()
    
    # Time Entities
    CHRONO_WRAITH = auto()
    TEMPORAL_TITAN = auto()
    EPOCH_SPHINX = auto()
    TIME_WEAVER = auto()
    
    # Dream Creatures
    NIGHTMARE_WEAVER = auto()
    DREAM_EATER = auto()
    SLEEP_WALKER = auto()
    MORPHEUS_SPAWN = auto()
    
    # Astral Beings
    CONSTELLATION_AVATAR = auto()
    METEOR_RIDER = auto()
    NEBULA_WEAVER = auto()
    SOLAR_PHOENIX = auto()
    
    # Primal Forces
    ANCIENT_TITAN = auto()
    PRIMORDIAL_WYRM = auto()
    GENESIS_SPIRIT = auto()
    ETERNAL_FLAME = auto()
    
    # Quantum Entities
    SCHRODINGER_BEAST = auto()
    QUANTUM_SHIFTER = auto()
    PROBABILITY_WEAVER = auto()
    ENTANGLED_HORROR = auto()
    
    # Mythic Beasts
    CHIMERA_LORD = auto()
    WORLD_SERPENT = auto()
    GOLDEN_GUARDIAN = auto()
    FATE_SPHINX = auto()
    
    # Psychic Anomalies
    THOUGHT_DEVOURER = auto()
    MEMORY_PHANTOM = auto()
    PSYCHIC_HYDRA = auto()
    MIND_COLOSSUS = auto()
    
    # Void Entities
    NULL_WALKER = auto()
    ENTROPY_BEAST = auto()
    VOID_LEVIATHAN = auto()
    COSMIC_HORROR = auto()
    
    # Astral Beings
    NEBULA_PHANTOM = auto()
    COSMIC_GUARDIAN = auto()
    ASTRAL_WALKER = auto()
    
    # Elemental Spirits
    FIRE_SPIRIT = auto()
    WATER_SPIRIT = auto()
    EARTH_SPIRIT = auto()
    AIR_SPIRIT = auto()
    
    # Nature Spirits
    FOREST_GUARDIAN = auto()
    VINE_WEAVER = auto()
    MOSS_BEAST = auto()
    BLOOM_SPIRIT = auto()
    
    # New additions
    GOBLIN = auto()
    ORC = auto()
    TROLL = auto() 