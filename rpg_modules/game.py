from rpg_modules.entities.monster import Monster, MonsterType

def _spawn_initial_monsters(self):
    """Spawn initial monsters on the map."""
    logging.log("=== Spawning Initial Monsters ===\n")
    
    # Define initial monster counts for each type
    initial_monsters = {
        MonsterType.SLIME: 5,
        MonsterType.SPIDER: 3,
        MonsterType.GHOST: 2,
        MonsterType.SKELETON: 3,
        MonsterType.DRAGON: 1
    }
    
    for monster_type, count in initial_monsters.items():
        logging.log(f"\nSpawning {monster_type.name} monsters...")
        for _ in range(count):
            # Get random position
            tile_x = random.randint(0, self.game_map.width - 1)
            tile_y = random.randint(0, self.game_map.height - 1)
            
            # Convert to pixel coordinates
            pixel_x = tile_x * TILE_SIZE
            pixel_y = tile_y * TILE_SIZE
            
            # Check distance from player
            dx = pixel_x - self.player.x
            dy = pixel_y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < MIN_SPAWN_DISTANCE:
                logging.log(f"Skip: Too close to player at ({tile_x}, {tile_y})")
                continue
                
            if not self.game_map.is_walkable(tile_x, tile_y):
                logging.log(f"Skip: Non-walkable tile at ({tile_x}, {tile_y})")
                continue
            
            # Create and add monster
            monster = Monster(pixel_x, pixel_y, monster_type)
            self.monsters.append(monster)
            logging.log(f"Spawned {monster_type.name} at ({tile_x}, {tile_y})")

# Monster spawn configuration
MONSTER_SPAWN_CONFIG = {
    MonsterType.DRAGON: {'min_distance': 200, 'spawn_chance': 0.005},
    MonsterType.SPIDER: {'min_distance': 100, 'spawn_chance': 0.02},
    MonsterType.GHOST: {'min_distance': 150, 'spawn_chance': 0.015},
    MonsterType.SKELETON: {'min_distance': 100, 'spawn_chance': 0.02},
    MonsterType.SLIME: {'min_distance': 80, 'spawn_chance': 0.03}
} 