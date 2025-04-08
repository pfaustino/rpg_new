from typing import List, Dict, Tuple, Optional
import random
from .monster import Monster
from .monster_factory import monster_factory

class MonsterSpawner:
    """Handles monster spawning in the game world."""
    
    def __init__(self):
        self._spawn_points: List[Tuple[int, int]] = []
        self._spawn_templates: Dict[str, Dict] = {}
        self._active_monsters: List[Monster] = []
        self._spawn_timer: float = 0
        self._spawn_interval: float = 10.0  # seconds
        
    def add_spawn_point(self, x: int, y: int) -> None:
        """Add a new spawn point."""
        self._spawn_points.append((x, y))
        
    def remove_spawn_point(self, x: int, y: int) -> None:
        """Remove a spawn point."""
        if (x, y) in self._spawn_points:
            self._spawn_points.remove((x, y))
            
    def register_spawn_template(self, template_name: str, template: Dict) -> None:
        """Register a new spawn template."""
        self._spawn_templates[template_name] = template
        
    def update(self, dt: float) -> None:
        """Update the spawner state."""
        self._spawn_timer += dt
        
        # Check if it's time to spawn new monsters
        if self._spawn_timer >= self._spawn_interval:
            self._spawn_timer = 0
            self._try_spawn_monsters()
            
        # Update active monsters
        for monster in self._active_monsters[:]:
            monster.update(dt)
            if not monster.is_alive():
                self._active_monsters.remove(monster)
                
    def _try_spawn_monsters(self) -> None:
        """Attempt to spawn new monsters."""
        if not self._spawn_points or not self._spawn_templates:
            return
            
        # Select a random spawn template
        template_name = random.choice(list(self._spawn_templates.keys()))
        template = self._spawn_templates[template_name]
        
        # Check spawn chance
        if random.random() > template.get("spawn_chance", 0.5):
            return
            
        # Select a random spawn point
        spawn_point = random.choice(self._spawn_points)
        
        # Create and spawn the monster
        monster_type = template["monster_type"]
        level = template.get("level", 1)
        
        monster = monster_factory.create_monster(monster_type, level)
        monster.set_position(spawn_point[0], spawn_point[1])
        
        self._active_monsters.append(monster)
        
    def get_active_monsters(self) -> List[Monster]:
        """Get the list of active monsters."""
        return self._active_monsters
        
    def clear_monsters(self) -> None:
        """Clear all active monsters."""
        self._active_monsters.clear()

# Create a global instance
monster_spawner = MonsterSpawner() 