import pygame
import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum
import time

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

@dataclass
class Particle:
    x: float
    y: float
    dx: float
    dy: float
    color: Tuple[int, int, int]
    life: float
    size: float

class AnimatedIcon:
    """Base class for animated icons in the game."""
    def __init__(self):
        self._particles: List[Particle] = []
        self._time = 0

    def update(self, dt: float):
        """Update animation state."""
        self._time += dt
        
        # Update particles
        for particle in self._particles[:]:
            particle.x += particle.dx
            particle.y += particle.dy
            particle.life -= dt
            if particle.life <= 0:
                self._particles.remove(particle)

    def _get_animation_values(self) -> dict:
        """Get common animation values used across different icons."""
        return {
            'pulse': (math.sin(self._time * 2) + 1) / 2,  # 0 to 1
            'rotation': self._time * 45,  # 45 degrees per second
            'eye_blink': max(0, math.sin(self._time * 1.5)),  # Slower blink animation
            'breath': math.sin(self._time * 2) * 0.1 + 1,  # Subtle breathing
        }

    def _draw_shadow(self, surface: pygame.Surface, shape: str, color: Tuple[int, int, int], 
                    size: int, offset=(1, 1), alpha=64):
        """Draw a shadow effect."""
        shadow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(shadow_surface, (*color[:3], alpha), 
                             (size//2 + offset[0], size//2 + offset[1]), size//2)
        elif shape == "rect":
            pygame.draw.rect(shadow_surface, (*color[:3], alpha),
                           (size//4 + offset[0], size//4 + offset[1], size//2, size//2))
        surface.blit(shadow_surface, (0, 0))

    def _draw_highlight(self, surface: pygame.Surface, shape: str, color: Tuple[int, int, int], 
                       size: int, offset=(-1, -1), alpha=128):
        """Draw a highlight effect."""
        highlight_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(highlight_surface, (*color[:3], alpha),
                             (size//2 + offset[0], size//2 + offset[1]), size//4)
        elif shape == "rect":
            pygame.draw.rect(highlight_surface, (*color[:3], alpha),
                           (size//4 + offset[0], size//4 + offset[1], size//4, size//4))
        surface.blit(highlight_surface, (0, 0))

    def _draw_animated_eyes(self, surface: pygame.Surface, x: int, y: int, size: int,
                          eye_color: Tuple[int, int, int], 
                          pupil_color: Tuple[int, int, int] = (0, 0, 0),
                          blink_amount: float = 1.0):
        """Draw animated eyes with blinking and movement."""
        # Eye white
        pygame.draw.ellipse(surface, eye_color, 
                          (x - size//8, y - int(size//8 * blink_amount), 
                           size//4, int(size//4 * blink_amount)))
        # Pupil movement
        if blink_amount > 0.2:
            pupil_x = x + int(size//16 * math.sin(self._time * 2))
            pupil_y = y + int(size//16 * math.sin(self._time * 1.5))
            pygame.draw.circle(surface, pupil_color, (pupil_x, pupil_y), size//12)

    def _draw_particles(self, surface: pygame.Surface, position=None, color=None, size=None):
        """Draw all active particles or a single particle if position is specified."""
        try:
            if position and color:
                # Single particle mode
                if isinstance(color, (tuple, list)) and len(color) >= 3:
                    particle_surface = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, color, (size, size), size)
                    surface.blit(particle_surface, (int(position[0]-size), int(position[1]-size)))
            else:
                # Draw all particles in the list
                for particle in self._particles:
                    if not isinstance(particle, Particle):
                        continue
                        
                    alpha = int(255 * (particle.life / 1.0))
                    if isinstance(particle.color, (tuple, list)):
                        # Handle both RGB and RGBA colors
                        if len(particle.color) == 3:
                            color = (*particle.color, alpha)
                        else:
                            color = (*particle.color[:3], min(particle.color[3], alpha))
                            
                        particle_surface = pygame.Surface((int(particle.size*2), int(particle.size*2)), pygame.SRCALPHA)
                        pygame.draw.circle(particle_surface, color, 
                                        (particle.size, particle.size), particle.size)
                        surface.blit(particle_surface, 
                                   (int(particle.x-particle.size), int(particle.y-particle.size)))
        except Exception as e:
            print(f"Error drawing particles: {str(e)}")

class PlayerIcon(AnimatedIcon):
    def draw(self, surface: pygame.Surface, position: Tuple[int, int], size: int):
        """
        Draw the player icon at the specified position.
        
        Args:
            surface: The pygame surface to draw on
            position: (x, y) position to draw at
            size: Size of the icon in pixels
        """
        # Create a surface for the player icon
        icon_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self.render(icon_surface, size)
        
        # Draw at position
        surface.blit(icon_surface, position)

    def render(self, surface: pygame.Surface, size: int):
        """Render the player icon with all animations."""
        anim = self._get_animation_values()
        
        # Base body shadow
        self._draw_shadow(surface, "circle", (50, 50, 150), size)
        
        # Cape animation
        cape_points = [(size//2, size//3)]
        wind_time = self._time * 2
        for i in range(4):
            x = size//2 + int(math.cos(wind_time + i) * size//6)
            y = size//3 + (i * size//8)
            cape_points.append((x, y))
        cape_points.append((x - size//4, y))
        cape_points.append((x + size//4, y))
        pygame.draw.polygon(surface, (150, 0, 0), cape_points)
        
        # Body with breathing
        body_height = int(size//2 * anim['breath'])
        pygame.draw.ellipse(surface, (50, 50, 150),
                          (size//3, size//3, size//3, body_height))
        
        # Head
        pygame.draw.circle(surface, (255, 220, 180),
                         (size//2, size//3), size//6)
        
        # Eyes
        self._draw_animated_eyes(surface, size//2 - size//8, size//3, size,
                               (255, 255, 255), (0, 100, 255), anim['eye_blink'])
        self._draw_animated_eyes(surface, size//2 + size//8, size//3, size,
                               (255, 255, 255), (0, 100, 255), anim['eye_blink'])
        
        # Animated hair
        hair_points = []
        for i in range(5):
            angle = math.radians(i * 45 - 90 + math.sin(self._time * 3) * 5)
            x = size//2 + int(math.cos(angle) * size//4)
            y = size//4 + int(math.sin(angle) * size//6)
            hair_points.append((x, y))
        pygame.draw.polygon(surface, (139, 69, 19), hair_points)
        
        # Aura particles
        if random.random() < 0.2:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(size//3, size//2)
            self._particles.append(Particle(
                x=size//2 + math.cos(angle) * dist,
                y=size//2 + math.sin(angle) * dist,
                dx=math.cos(angle) * -0.5,
                dy=math.sin(angle) * -0.5,
                color=(100, 150, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

class MonsterIcon(AnimatedIcon):
    def __init__(self, monster_type):
        """Initialize the monster icon with a type.
        
        Args:
            monster_type: Either a string or MonsterType enum
        """
        super().__init__()
        # If it's an enum, get its value, otherwise use the string
        if hasattr(monster_type, 'value'):
            self.monster_type = monster_type.value
        else:
            self.monster_type = str(monster_type).lower()
        self._particles = []
        self._animation_state = {
            'time': 0,
            'direction': Direction.DOWN,
            'state': 'idle'
        }

    def _update_particles(self, size: int):
        """Update particle positions and lifetimes."""
        try:
            for particle in self._particles[:]:
                particle.x += particle.dx
                particle.y += particle.dy
                particle.life -= 0.016  # Assuming 60 FPS
                
                # Remove particles that are out of bounds or have expired
                if (particle.life <= 0 or 
                    particle.x < 0 or particle.x > size or 
                    particle.y < 0 or particle.y > size):
                    self._particles.remove(particle)
        except Exception as e:
            print(f"Error updating particles: {e}")

    def _get_monster_color(self) -> tuple:
        """Get a color based on the monster type."""
        colors = {
            'goblin': (0, 128, 0),        # Green
            'orc': (0, 100, 0),           # Dark green
            'troll': (107, 142, 35),      # Olive green
            'imp': (255, 0, 0),           # Red
            'spider': (139, 69, 19),      # Brown
            'snake': (0, 100, 0),         # Dark green
            'wolf': (105, 105, 105),      # Gray
            'bear': (139, 69, 19),        # Brown
            'slime': (0, 255, 0),         # Bright green
            'bat': (47, 79, 79),          # Dark slate gray
            'skeleton': (211, 211, 211),  # Light gray
            'zombie': (124, 252, 0),      # Lawn green
            'ghost': (248, 248, 255),     # Ghost white
            'vampire': (139, 0, 0),       # Dark red
            'lich': (75, 0, 130),         # Indigo
            'demon': (139, 0, 0),         # Dark red
            'dragon': (255, 0, 0),        # Red
            'phoenix': (255, 69, 0),      # Red-orange
            'golem': (169, 169, 169),     # Dark gray
            'fire_elemental': (255, 69, 0),      # Red-orange
            'water_elemental': (0, 0, 255),      # Blue
            'earth_elemental': (139, 69, 19),    # Brown
            'air_elemental': (240, 248, 255),    # Alice blue
            'ice_elemental': (173, 216, 230),    # Light blue
            'lightning_elemental': (255, 255, 0), # Yellow
            'treant': (34, 139, 34),      # Forest green
            'dryad': (152, 251, 152),     # Pale green
            'unicorn': (255, 255, 255),   # White
            'pixie': (255, 182, 193),     # Light pink
            'arcane_turret': (138, 43, 226),   # Purple
            'void_walker': (75, 0, 130),       # Indigo
            'shadow': (47, 79, 79),            # Dark slate gray
            'crystal_golem': (64, 224, 208),   # Turquoise
        }
        
        # Add uppercase variants to the colors dictionary
        uppercase_colors = {k.upper(): v for k, v in colors.items()}
        colors.update(uppercase_colors)
        
        # Try to match the monster type with the colors dictionary
        original_type = str(self.monster_type)
        monster_type_str = original_type.lower().strip()
        enum_name = original_type.upper() if hasattr(original_type, 'upper') else original_type
        
        # Check for exact match with lowercase
        if monster_type_str in colors:
            return colors[monster_type_str]
        
        # Check for exact match with original case
        if original_type in colors:
            return colors[original_type]
        
        # Check for exact match with uppercase (for enum names)
        if enum_name in colors:
            return colors[enum_name]
            
        # Try with partial matching for lowercase
        for key, value in colors.items():
            if key.lower() in monster_type_str:
                return value
        
        # For monster types like 'TREANT', split by underscore and try each part
        if '_' in monster_type_str:
            parts = monster_type_str.split('_')
            for part in parts:
                if part in colors:
                    return colors[part]
        
        # If no match found, generate color from type name hash for consistency
        name_hash = sum(ord(c) for c in monster_type_str)
        r = (name_hash * 123) % 256
        g = (name_hash * 456) % 256
        b = (name_hash * 789) % 256
        return (r, g, b)

    def _sanitize_color(self, color) -> tuple:
        """Ensure color is a valid RGB tuple."""
        try:
            # Handle None input
            if color is None:
                return (255, 0, 0)
                
            # If color is already a tuple/list with at least 3 components
            if isinstance(color, (tuple, list)) and len(color) >= 3:
                # Ensure RGB values are within valid range (0-255)
                r = max(0, min(255, int(color[0])))
                g = max(0, min(255, int(color[1])))
                b = max(0, min(255, int(color[2])))
                return (r, g, b)
                
            # Handle string format '#RRGGBB'
            elif isinstance(color, str) and color.startswith('#') and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    return (r, g, b)
                except ValueError:
                    print(f"Warning: Invalid hex color format: {color}")
            
            # Handle pygame Color object
            elif hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b'):
                return (color.r, color.g, color.b)
                
            print(f"Warning: Invalid color format: {color}, returning default red")
            return (255, 0, 0)  # Default to red
            
        except Exception as e:
            print(f"Error sanitizing color: {e}, using default red")
            return (255, 0, 0)  # Default to red if any errors

    def _get_animation_values(self) -> dict:
        """Get current animation values."""
        return {
            'pulse': (math.sin(self._time * 2) + 1) / 2,  # 0 to 1
            'rotation': self._time * 45,  # 45 degrees per second
            'eye_blink': max(0, math.sin(self._time * 1.5)),  # Slower blink animation
            'breath': math.sin(self._time * 2) * 0.1 + 1,  # Subtle breathing
        }

    def _ensure_direction_compatibility(self, direction):
        """Ensure the direction is a valid Direction enum."""
        from . import Direction  # Import at function level to avoid circular imports
        
        # If already a Direction enum, return as is
        if isinstance(direction, Direction):
            return direction
            
        # If it's an integer, try to convert to Direction
        if isinstance(direction, int):
            try:
                return Direction(direction)
            except ValueError:
                print(f"Warning: Invalid direction value {direction}, defaulting to Direction.DOWN")
                return Direction.DOWN
                
        # If it's a string, try to convert to Direction
        if isinstance(direction, str):
            try:
                return Direction[direction.upper()]
            except KeyError:
                print(f"Warning: Invalid direction string {direction}, defaulting to Direction.DOWN")
                return Direction.DOWN
                
        # For any other type, default to DOWN
        print(f"Warning: Invalid direction type {type(direction)}, defaulting to Direction.DOWN")
        return Direction.DOWN

    def render(self, surface, size, direction=None):
        """Render the monster icon based on its type."""
        # Monster type is already stored as a lowercase string from __init__
        monster_parts = self.monster_type.split('_')
        anim = self._get_animation_values()
        direction = self._ensure_direction_compatibility(direction)
        
        try:
            # Check for specific monster types first
            if self.monster_type == 'clockwork_knight':
                self._render_clockwork_knight(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['ice', 'frost']):
                self._render_ice_elemental(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['fire', 'flame']):
                self._render_fire_elemental(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['phoenix', 'dragon']):
                self._render_dragon(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['prism', 'crystal', 'gem']):
                self._render_crystal(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['basilisk', 'snake']):
                self._render_basilisk(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['dryad', 'nature']):
                self._render_dryad(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['storm', 'lightning', 'thunder']):
                self._render_storm_elemental(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['earth', 'stone', 'rock']):
                self._render_earth_elemental(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['void', 'shade', 'phantom', 'shadow', 'stalker']):
                self._render_shadow(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['zombie', 'undead']):
                self._render_zombie(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['spider']):
                self._render_spider(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['unicorn']):
                self._render_unicorn(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['nightmare']):
                self._render_nightmare(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['demon']):
                self._render_demon(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['treant', 'tree']):
                self._render_treant(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['steam', 'golem', 'mechanical']):
                self._render_mechanical(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['slime', 'ooze']):
                self._render_slime(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['wraith', 'ghost', 'spirit']):
                self._render_spirit(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['wolf', 'bear']):
                self._render_bear(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['turret', 'arcane']):
                self._render_construct(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['vampire']):
                self._render_vampire(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['pixie']):
                self._render_pixie(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['merfolk', 'mermaid']):
                self._render_mermaid(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['kraken']):
                self._render_kraken(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['siren']):
                self._render_siren(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['leviathan']):
                self._render_leviathan(surface, size, direction, anim)
            elif any(x in monster_parts for x in ['water', 'spirit']):
                self._render_water_spirit(surface, size, direction, anim)
            else:
                print(f"No specific render method found for {self.monster_type}, using default")
                self._render_default(surface, size, direction, anim)
        except Exception as e:
            print(f"ERROR: Error rendering monster {self.monster_type}: {str(e)}")
            pygame.draw.circle(surface, (255, 0, 0), (size//2, size//2), size//3)
        
        self._update_particles(size)
        self._draw_particles(surface)

    def draw(self, surface, position, size, direction=None):
        """Draw the monster at the given position with the specified size."""
        temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self.render(temp_surface, size, direction)
        surface.blit(temp_surface, position)

    def _render_crystal(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render crystal-based monsters with geometric shapes and sparkle effects."""
        try:
            crystal_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            crystal_points = [
                (center[0], center[1] - size//3),
                (center[0] - size//3, center[1]),
                (center[0], center[1] + size//3),
                (center[0] + size//3, center[1]),
            ]
            
            pygame.draw.polygon(surface, crystal_color, crystal_points)
            
            highlight_color = self._sanitize_color((
                min(255, crystal_color[0] + 50),
                min(255, crystal_color[1] + 50),
                min(255, crystal_color[2] + 50)
            ))
            
            for i in range(len(crystal_points)):
                start = crystal_points[i]
                end = crystal_points[(i + 1) % len(crystal_points)]
                pygame.draw.line(surface, highlight_color, start, end, max(2, size//20))
            
            if random.random() < 0.2:
                for _ in range(3):
                    sparkle_pos = (
                        random.randint(center[0] - size//3, center[0] + size//3),
                        random.randint(center[1] - size//3, center[1] + size//3)
                    )
                    self._particles.append(Particle(
                        x=sparkle_pos[0],
                        y=sparkle_pos[1],
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-1, 1),
                        color=self._sanitize_color((255, 255, 255)),
                        life=random.uniform(0.2, 0.4),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_crystal: {e}")
            return False

    def _render_bear(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render bear/wolf monsters with distinctive features."""
        try:
            animal_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw main body
            body_pulse = 1 + anim['breath'] * 0.1
            pygame.draw.circle(surface, animal_color, center, int(size//3 * body_pulse))
            
            # Draw ears
            ear_size = size//8
            ear_positions = [
                (center[0] - size//4, center[1] - size//4),
                (center[0] + size//4, center[1] - size//4)
            ]
            for pos in ear_positions:
                pygame.draw.circle(surface, animal_color, pos, ear_size)
            
            # Draw snout
            snout_color = self._sanitize_color((
                max(0, animal_color[0] - 30),
                max(0, animal_color[1] - 30),
                max(0, animal_color[2] - 30)
            ))
            pygame.draw.ellipse(surface, snout_color,
                              (center[0] - size//8,
                               center[1] - size//8,
                               size//4,
                               size//4))
            
            # Draw eyes with blinking
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            return True
        except Exception as e:
            print(f"Error in _render_bear: {e}")
            return False

    def _render_demon(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render demon monsters with horns and glowing eyes."""
        try:
            demon_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw main body with pulsing effect
            body_pulse = 1 + anim['pulse'] * 0.2
            pygame.draw.circle(surface, demon_color, center, int(size//3 * body_pulse))
            
            # Draw horns
            horn_color = self._sanitize_color((
                max(0, demon_color[0] - 50),
                max(0, demon_color[1] - 50),
                max(0, demon_color[2] - 50)
            ))
            
            # Left horn
            left_horn_points = [
                (center[0] - size//4, center[1] - size//4),
                (center[0] - size//3, center[1] - size//2),
                (center[0] - size//6, center[1] - size//3)
            ]
            pygame.draw.polygon(surface, horn_color, left_horn_points)
            
            # Right horn
            right_horn_points = [
                (center[0] + size//4, center[1] - size//4),
                (center[0] + size//3, center[1] - size//2),
                (center[0] + size//6, center[1] - size//3)
            ]
            pygame.draw.polygon(surface, horn_color, right_horn_points)
            
            # Draw glowing eyes with pulsing effect
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                # Outer glow
                glow_radius = size//8 * (1 + anim['pulse'] * 0.3)
                pygame.draw.circle(surface, (255, 100, 0, 64), pos, glow_radius)
                # Inner glow
                pygame.draw.circle(surface, (255, 200, 0, 128), pos, size//12)
                # Core
                pygame.draw.circle(surface, (255, 255, 0), pos, size//16)
            
            # Add flame particles
            if random.random() < 0.3:
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(size//4, size//2)
                    self._particles.append(Particle(
                        x=center[0] + math.cos(angle) * distance,
                        y=center[1] + math.sin(angle) * distance,
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-2, -0.5),
                        color=(255, 100, 0, 150),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_demon: {e}")
            return False

    def _render_pixie(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render pixie monsters with wings and sparkle effects."""
        try:
            pixie_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw glowing aura
            aura_radius = int(size//3 * (1 + anim['pulse'] * 0.2))
            for r in range(aura_radius, aura_radius - size//6, -1):
                alpha = int(255 * (r - (aura_radius - size//6)) / (size//6))
                aura_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(aura_surface, (*pixie_color[:3], alpha), center, r)
                surface.blit(aura_surface, (0, 0))
            
            # Draw main body
            pygame.draw.circle(surface, pixie_color, center, size//6)
            
            # Draw wings
            wing_color = (255, 255, 255, 128)
            wing_angle = math.sin(self._time * 8) * 0.5  # Wing flapping animation
            
            for side in [-1, 1]:  # Left and right wings
                wing_points = [
                    center,
                    (center[0] + side * size//2 * math.cos(wing_angle),
                     center[1] - size//3),
                    (center[0] + side * size//2,
                     center[1])
                ]
                wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.polygon(wing_surface, wing_color, wing_points)
                surface.blit(wing_surface, (0, 0))
            
            # Add sparkle particles
            if random.random() < 0.3:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(size//6, size//3)
                self._particles.append(Particle(
                    x=center[0] + math.cos(angle) * distance,
                    y=center[1] + math.sin(angle) * distance,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, 255, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(2, 3)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_pixie: {e}")
            return False

    def _render_slime(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render slime monsters with bouncy, gelatinous effects."""
        try:
            slime_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Bouncing animation
            bounce = abs(math.sin(self._time * 4))
            squish = 1 - bounce * 0.3
            
            # Draw main body (squished circle)
            radius = size//3
            ellipse_rect = (
                center[0] - radius,
                center[1] - radius * squish,
                radius * 2,
                radius * 2 * squish
            )
            pygame.draw.ellipse(surface, slime_color, ellipse_rect)
            
            # Draw highlight
            highlight_color = self._sanitize_color((
                min(255, slime_color[0] + 50),
                min(255, slime_color[1] + 50),
                min(255, slime_color[2] + 50)
            ))
            highlight_radius = radius // 2
            highlight_pos = (
                center[0] - highlight_radius//2,
                center[1] - radius * squish//2,
                highlight_radius,
                highlight_radius * squish
            )
            pygame.draw.ellipse(surface, highlight_color, highlight_pos)
            
            # Draw eyes
            eye_color = (0, 0, 0)
            eye_spacing = radius // 2
            eye_y = center[1] - radius * squish//2
            eye_size = radius // 4
            
            for x_offset in [-eye_spacing//2, eye_spacing//2]:
                eye_x = center[0] + x_offset
                pygame.draw.circle(surface, eye_color, (eye_x, eye_y), eye_size)
            
            # Add drip particles
            if random.random() < 0.1:
                drip_x = center[0] + random.uniform(-radius, radius)
                self._particles.append(Particle(
                    x=drip_x,
                    y=center[1],
                    dx=0,
                    dy=2,
                    color=slime_color,
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_slime: {e}")
            return False

    def _render_mechanical(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render mechanical monsters like steam golems with gears and steam effects."""
        try:
            mechanical_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw main body (metallic cylinder)
            pygame.draw.rect(surface, mechanical_color,
                           (center[0] - size//3, center[1] - size//3,
                            2 * size//3, 2 * size//3))
            
            # Draw gear details
            gear_color = self._sanitize_color((
                min(255, mechanical_color[0] + 30),
                min(255, mechanical_color[1] + 30),
                min(255, mechanical_color[2] + 30)
            ))
            
            # Draw multiple gears that rotate
            gear_positions = [
                (center[0] - size//4, center[1] - size//4),
                (center[0] + size//4, center[1] - size//4),
                (center[0], center[1] + size//4)
            ]
            
            for i, pos in enumerate(gear_positions):
                # Rotate gears at different speeds
                rotation = self._time * (2 + i) * math.pi
                gear_radius = size//8
                
                # Draw gear teeth
                for j in range(8):
                    angle = rotation + j * math.pi/4
                    tooth_x = pos[0] + math.cos(angle) * (gear_radius + size//16)
                    tooth_y = pos[1] + math.sin(angle) * (gear_radius + size//16)
                    pygame.draw.line(surface, gear_color, pos, (tooth_x, tooth_y), max(2, size//20))
                
                # Draw gear body
                pygame.draw.circle(surface, gear_color, pos, gear_radius)
                pygame.draw.circle(surface, mechanical_color, pos, gear_radius - size//16)
            
            # Draw steam vents
            vent_positions = [
                (center[0] - size//3, center[1] - size//6),
                (center[0] + size//3, center[1] - size//6)
            ]
            
            for pos in vent_positions:
                pygame.draw.rect(surface, (50, 50, 50),
                               (pos[0], pos[1], size//6, size//12))
            
            # Add steam particle effects
            if random.random() < 0.3:
                for vent in vent_positions:
                    self._particles.append(Particle(
                        x=vent[0] + size//12,
                        y=vent[1],
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(-2, -1),
                        color=(200, 200, 200, 128),
                        life=random.uniform(0.5, 1.0),
                        size=random.uniform(4, 8)
                    ))
            
            # Draw glowing power core
            core_pulse = (math.sin(self._time * 4) + 1) / 2
            core_size = int(size//6 * (1 + core_pulse * 0.2))
            pygame.draw.circle(surface, (255, 200, 0), center, core_size)
            pygame.draw.circle(surface, (255, 255, 200), center, core_size//2)
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_mechanical: {e}")
            return False

    def _render_spirit(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render spirit/wraith monsters with ethereal effects."""
        try:
            spirit_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Create a pulsing, transparent form
            pulse = (math.sin(self._time * 2) + 1) / 2
            for i in range(3):
                alpha = int(128 * (1 - i/3) * (0.5 + pulse * 0.5))
                radius = size//3 * (1 + i * 0.2)
                ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(ghost_surface, (*spirit_color[:3], alpha), center, int(radius))
                surface.blit(ghost_surface, (0, 0))
            
            # Add floating movement
            float_y = math.sin(self._time * 3) * size//10
            
            # Draw main form
            main_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            main_points = [
                (center[0], center[1] - size//3 + float_y),
                (center[0] - size//3, center[1] + size//3 + float_y),
                (center[0] + size//3, center[1] + size//3 + float_y)
            ]
            pygame.draw.polygon(main_surface, (*spirit_color[:3], 192), main_points)
            surface.blit(main_surface, (0, 0))
            
            # Draw glowing eyes
            eye_color = (255, 255, 255)
            eye_spacing = size//6
            eye_y = center[1] - size//6 + float_y
            
            for x_offset in [-eye_spacing, eye_spacing]:
                eye_x = center[0] + x_offset
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 64), (eye_x, eye_y), size//10)
                # Inner glow
                pygame.draw.circle(surface, (*eye_color, 128), (eye_x, eye_y), size//16)
                # Core
                pygame.draw.circle(surface, eye_color, (eye_x, eye_y), size//24)
            
            # Add ethereal particles
            if random.random() < 0.2:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(size//6, size//3)
                self._particles.append(Particle(
                    x=center[0] + math.cos(angle) * distance,
                    y=center[1] + math.sin(angle) * distance + float_y,
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-0.5, 0.5),
                    color=(*spirit_color[:3], 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(3, 6)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_spirit: {e}")
            return False

    def _render_undead(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render undead monsters like vampires."""
        try:
            undead_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw main body with pale color
            body_color = (200, 200, 200)  # Pale color for undead
            pygame.draw.circle(surface, body_color, center, size//3)
            
            # Draw dark cape/cloak
            cape_color = (100, 0, 0)  # Dark red
            cape_points = [
                (center[0], center[1] - size//3),
                (center[0] - size//2, center[1] + size//3),
                (center[0] + size//2, center[1] + size//3)
            ]
            pygame.draw.polygon(surface, cape_color, cape_points)
            
            # Draw glowing red eyes
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                # Outer glow
                pygame.draw.circle(surface, (255, 0, 0, 64), pos, size//8)
                # Inner glow
                pygame.draw.circle(surface, (255, 0, 0, 128), pos, size//12)
                # Core
                pygame.draw.circle(surface, (255, 0, 0), pos, size//16)
            
            # Draw fangs
            fang_color = (255, 255, 255)
            fang_positions = [
                (center[0] - size//8, center[1] + size//6),
                (center[0] + size//8, center[1] + size//6)
            ]
            
            for pos in fang_positions:
                pygame.draw.polygon(surface, fang_color, [
                    pos,
                    (pos[0] - size//16, pos[1] + size//8),
                    (pos[0] + size//16, pos[1] + size//8)
                ])
            
            # Add mist effect
            if random.random() < 0.2:
                self._particles.append(Particle(
                    x=center[0] + random.uniform(-size//3, size//3),
                    y=center[1] + random.uniform(-size//3, size//3),
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-0.5, 0.5),
                    color=(200, 200, 200, 100),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(3, 5)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_undead: {e}")
            return False

    def _render_dragon(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render dragon/phoenix monsters with wings and flame effects."""
        try:
            phoenix_color = self._sanitize_color(self._get_monster_color())
            pygame.draw.circle(surface, phoenix_color, (size//2, size//2), size//3)
            
            wing_points_left = [
                (size//2 - size//6, size//2),
                (size//2 - size//2, size//2 - size//4),
                (size//2 - size//2, size//2 + size//4)
            ]
            
            wing_points_right = [
                (size//2 + size//6, size//2),
                (size//2 + size//2, size//2 - size//4),
                (size//2 + size//2, size//2 + size//4)
            ]
            
            pygame.draw.polygon(surface, phoenix_color, wing_points_left)
            pygame.draw.polygon(surface, phoenix_color, wing_points_right)
            
            if random.random() < 0.3:
                for _ in range(5):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(size//4, size//2)
                    self._particles.append(Particle(
                        x=size//2 + math.cos(angle) * distance,
                        y=size//2 + math.sin(angle) * distance,
                        dx=random.uniform(-2, 2),
                        dy=random.uniform(-2, 2),
                        color=self._sanitize_color((255, 165, 0)),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(3, 6)
                    ))
            
            eye_color = (255, 255, 0)
            eye_positions = [
                (size//2 - size//6, size//2 - size//8),
                (size//2 + size//6, size//2 - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_dragon: {e}")
            return False

    def _render_construct(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render construct-type monsters with mechanical features."""
        try:
            construct_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Main body
            pygame.draw.rect(surface, construct_color, 
                           (center[0] - size//4, center[1] - size//4,
                            size//2, size//2))
            
            # Mechanical details
            detail_color = self._sanitize_color((
                max(0, construct_color[0] - 50),
                max(0, construct_color[1] - 50),
                max(0, construct_color[2] - 50)
            ))
            
            # Draw mechanical plates
            plate_positions = [
                (center[0] - size//3, center[1] - size//3),
                (center[0] + size//6, center[1] - size//3),
                (center[0] - size//3, center[1] + size//6),
                (center[0] + size//6, center[1] + size//6)
            ]
            
            for pos in plate_positions:
                pygame.draw.rect(surface, detail_color,
                               (pos[0], pos[1], size//6, size//6))
            
            # Draw glowing core
            core_color = self._sanitize_color((255, 200, 0))
            pygame.draw.circle(surface, core_color, center, size//8)
            pygame.draw.circle(surface, (255, 255, 255), center, size//12)
            
            # Add mechanical particles
            if random.random() < 0.2:
                for _ in range(3):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(size//4, size//2)
                    self._particles.append(Particle(
                        x=center[0] + math.cos(angle) * distance,
                        y=center[1] + math.sin(angle) * distance,
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-1, 1),
                        color=self._sanitize_color((200, 200, 200)),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_construct: {e}")
            return False

    def _render_default(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Default render method for monsters without specific implementations."""
        try:
            monster_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw main body
            pygame.draw.circle(surface, monster_color, center, size//3)
            
            # Add eyes
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            # Add simple animation effect
            if random.random() < 0.1:
                self._particles.append(Particle(
                    x=center[0],
                    y=center[1],
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=self._sanitize_color(monster_color),
                    life=random.uniform(0.2, 0.4),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_default: {e}")
            return False

    def _render_fire_elemental(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render fire elemental monsters with dynamic flame effects."""
        try:
            # Base colors for fire gradient
            colors = [
                (255, 50, 0),    # Bright orange-red
                (255, 100, 0),   # Orange
                (255, 150, 0),   # Light orange
                (255, 200, 0)    # Yellow
            ]
            
            center = (size//2, size//2)
            
            # Create a pulsing effect
            pulse = abs(math.sin(self._time * 3)) * 0.3 + 0.7
            flame_size = int(size * pulse)
            
            # Draw main body (multiple layers of flame)
            for i, color in enumerate(colors):
                layer_size = flame_size * (1 - i * 0.15)  # Each layer slightly smaller
                points = []
                num_points = 12
                
                for j in range(num_points):
                    angle = 2 * math.pi * j / num_points
                    # Add waviness to the flame
                    wave = math.sin(self._time * 5 + j) * size * 0.1
                    radius = layer_size//2 + wave
                    x = center[0] + radius * math.cos(angle)
                    y = center[1] + radius * math.sin(angle)
                    points.append((x, y))
                
                pygame.draw.polygon(surface, color, points)
            
            # Draw eyes (glowing embers)
            eye_color = (255, 255, 0)  # Bright yellow
            eye_glow = (255, 100, 0)   # Orange glow
            eye_size = size//8
            
            # Left eye
            left_eye_pos = (center[0] - size//4, center[1])
            pygame.draw.circle(surface, eye_glow, left_eye_pos, eye_size * 1.5)  # Glow
            pygame.draw.circle(surface, eye_color, left_eye_pos, eye_size)       # Eye
            
            # Right eye
            right_eye_pos = (center[0] + size//4, center[1])
            pygame.draw.circle(surface, eye_glow, right_eye_pos, eye_size * 1.5) # Glow
            pygame.draw.circle(surface, eye_color, right_eye_pos, eye_size)      # Eye
            
            # Add flame particles
            for _ in range(3):  # Add multiple particles per frame
                if random.random() < 0.8:  # 80% chance to spawn a particle
                    # Randomize particle color
                    particle_color = random.choice([
                        (255, 200, 0, 200),  # Yellow
                        (255, 150, 0, 200),  # Light orange
                        (255, 100, 0, 200),  # Orange
                        (255, 50, 0, 200)    # Red
                    ])
                    
                    # Spawn particle from random point on the elemental's body
                    angle = random.uniform(0, 2 * math.pi)
                    spawn_radius = random.uniform(0, size//3)
                    spawn_x = center[0] + spawn_radius * math.cos(angle)
                    spawn_y = center[1] + spawn_radius * math.sin(angle)
                    
                    # Particle movement tends upward
                    self._particles.append(Particle(
                        x=spawn_x,
                        y=spawn_y,
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-2, -0.5),  # Upward movement
                        color=particle_color,
                        life=random.uniform(0.3, 0.8),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_fire_elemental: {e}")
            return False

    def _render_storm_elemental(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render storm elemental monsters with lightning and cloud effects."""
        try:
            storm_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw cloud body
            cloud_points = [
                (center[0] - size//3, center[1]),
                (center[0] - size//4, center[1] - size//4),
                (center[0], center[1] - size//3),
                (center[0] + size//4, center[1] - size//4),
                (center[0] + size//3, center[1]),
                (center[0] + size//4, center[1] + size//4),
                (center[0] - size//4, center[1] + size//4)
            ]
            
            # Draw multiple layers for cloud depth
            for i in range(3):
                offset = i * 2
                cloud_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                shifted_points = [(x + offset, y + offset) for x, y in cloud_points]
                pygame.draw.polygon(cloud_surface, (*storm_color[:3], 128), shifted_points)
                surface.blit(cloud_surface, (0, 0))
            
            # Draw lightning bolts
            if random.random() < 0.2:  # Random lightning flash
                bolt_start = (center[0] + random.uniform(-size//4, size//4), 
                            center[1] - size//4)
                bolt_points = [bolt_start]
                current_point = bolt_start
                
                for _ in range(3):  # Create a zigzag pattern
                    next_point = (
                        current_point[0] + random.uniform(-size//8, size//8),
                        current_point[1] + size//8
                    )
                    bolt_points.append(next_point)
                    current_point = next_point
                
                # Draw the lightning with a glow effect
                bolt_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                # Outer glow
                pygame.draw.lines(bolt_surface, (255, 255, 200, 64), False, bolt_points, 6)
                # Inner glow
                pygame.draw.lines(bolt_surface, (255, 255, 200, 128), False, bolt_points, 4)
                # Core
                pygame.draw.lines(bolt_surface, (255, 255, 255), False, bolt_points, 2)
                surface.blit(bolt_surface, (0, 0))
                
                # Add lightning particles
                for point in bolt_points:
                    for _ in range(2):
                        self._particles.append(Particle(
                            x=point[0],
                            y=point[1],
                            dx=random.uniform(-2, 2),
                            dy=random.uniform(-2, 2),
                            color=(255, 255, 200, random.randint(128, 255)),
                            life=random.uniform(0.1, 0.3),
                            size=random.uniform(2, 4)
                        ))
            
            # Draw glowing eyes
            eye_color = (255, 255, 200)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 64), pos, size//10)
                # Inner glow
                pygame.draw.circle(surface, (*eye_color, 128), pos, size//16)
                # Core
                pygame.draw.circle(surface, eye_color, pos, size//24)
            
            # Add rain particles
            if random.random() < 0.3:
                for _ in range(2):
                    start_x = random.uniform(center[0] - size//3, center[0] + size//3)
                    self._particles.append(Particle(
                        x=start_x,
                        y=center[1],
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(2, 4),
                        color=(100, 100, 255, 128),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_storm_elemental: {e}")
            return False

    def _render_treant(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render treant monsters with tree-like features and nature effects."""
        try:
            treant_color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Draw trunk
            trunk_width = size//3
            trunk_height = size//2
            trunk_rect = (
                center[0] - trunk_width//2,
                center[1] - trunk_height//2,
                trunk_width,
                trunk_height
            )
            pygame.draw.rect(surface, treant_color, trunk_rect)
            
            # Draw bark texture
            bark_color = self._sanitize_color((
                max(0, treant_color[0] - 30),
                max(0, treant_color[1] - 30),
                max(0, treant_color[2] - 30)
            ))
            
            # Add bark lines
            for i in range(3):
                y_offset = trunk_rect[1] + (i + 1) * trunk_height//4
                start_point = (trunk_rect[0], y_offset)
                end_point = (trunk_rect[0] + trunk_width, y_offset)
                pygame.draw.line(surface, bark_color, start_point, end_point, 2)
            
            # Draw foliage (crown)
            leaf_color = self._sanitize_color((34, 139, 34))  # Forest green
            crown_radius = size//3
            
            # Draw multiple layers of leaves
            for i in range(3):
                offset = i * size//12
                pygame.draw.circle(surface, leaf_color,
                                 (center[0], center[1] - crown_radius//2 + offset),
                                 crown_radius - offset)
            
            # Draw glowing eyes
            eye_color = (255, 255, 200)
            eye_spacing = size//6
            eye_y = center[1] - size//8
            
            for x_offset in [-eye_spacing//2, eye_spacing//2]:
                eye_x = center[0] + x_offset
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 64), (eye_x, eye_y), size//10)
                # Inner glow
                pygame.draw.circle(surface, (*eye_color, 128), (eye_x, eye_y), size//16)
                # Core
                pygame.draw.circle(surface, eye_color, (eye_x, eye_y), size//24)
            
            # Add falling leaf particles
            if random.random() < 0.2:
                leaf_start_x = center[0] + random.uniform(-crown_radius, crown_radius)
                leaf_start_y = center[1] - crown_radius
                
                self._particles.append(Particle(
                    x=leaf_start_x,
                    y=leaf_start_y,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(0.5, 1.5),
                    color=(0, 255, 0, 128),
                    life=random.uniform(1.0, 2.0),
                    size=random.uniform(2, 4)
                ))
            
            # Add occasional nature sparkle
            if random.random() < 0.1:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(size//4, size//2)
                sparkle_x = center[0] + math.cos(angle) * distance
                sparkle_y = center[1] + math.sin(angle) * distance
                
                self._particles.append(Particle(
                    x=sparkle_x,
                    y=sparkle_y,
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-0.5, 0.5),
                    color=(200, 255, 200, 192),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_treant: {e}")
            return False

    def _render_ice_elemental(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render an ice elemental with crystalline patterns and frost effects."""
        try:
            # Ice blue colors for gradient effect
            ice_colors = [
                (200, 230, 255),  # Light ice blue
                (150, 200, 255),  # Medium ice blue
                (100, 170, 255),  # Darker ice blue
                (50, 150, 255)    # Deep ice blue
            ]
            
            center = (size // 2, size // 2)
            base_radius = size // 3
            
            # Draw crystalline core with layered effect
            for i, color in enumerate(ice_colors):
                radius = base_radius * (1 - i * 0.15)
                pygame.draw.circle(surface, color, center, int(radius))
            
            # Draw ice crystal spikes with transparency
            spike_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            num_spikes = 8
            for i in range(num_spikes):
                angle = 2 * math.pi * i / num_spikes + self._time  # Rotating spikes
                spike_length = base_radius * 1.2
                
                # Calculate spike points
                tip_x = center[0] + math.cos(angle) * spike_length
                tip_y = center[1] + math.sin(angle) * spike_length
                base_left_x = center[0] + math.cos(angle - 0.2) * base_radius
                base_left_y = center[1] + math.sin(angle - 0.2) * base_radius
                base_right_x = center[0] + math.cos(angle + 0.2) * base_radius
                base_right_y = center[1] + math.sin(angle + 0.2) * base_radius
                
                # Draw spike
                points = [(base_left_x, base_left_y), (tip_x, tip_y), (base_right_x, base_right_y)]
                pygame.draw.polygon(spike_surface, (*ice_colors[1], 180), points)
            
            surface.blit(spike_surface, (0, 0))
            
            # Draw glowing eyes
            eye_color = (220, 240, 255)  # Bright ice blue
            eye_radius = size // 12
            left_eye = (center[0] - size//6, center[1] - size//8)
            right_eye = (center[0] + size//6, center[1] - size//8)
            
            # Eye glow effect
            for r in range(2):
                glow_radius = eye_radius + r * 2
                glow_alpha = 255 - r * 100
                eye_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(eye_surface, (*eye_color[:3], glow_alpha), left_eye, glow_radius)
                pygame.draw.circle(eye_surface, (*eye_color[:3], glow_alpha), right_eye, glow_radius)
                surface.blit(eye_surface, (0, 0))
            
            # Add frost particles
            if random.random() < 0.4:  # 40% chance to spawn particles
                for _ in range(3):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(base_radius * 0.5, base_radius * 1.5)
                    particle_x = center[0] + math.cos(angle) * distance
                    particle_y = center[1] + math.sin(angle) * distance
                    
                    self._particles.append(Particle(
                        x=particle_x,
                        y=particle_y,
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(-0.5, 0.5),
                        color=(*ice_colors[0], 150),  # Semi-transparent ice particles
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
            
        except Exception as e:
            print(f"Error rendering ice elemental: {str(e)}")
            return False

    def _render_spider(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render spider monsters with legs and web effects."""
        try:
            color = self._sanitize_color(self._get_monster_color())
            center = (size//2, size//2)
            
            # Define leg positions (8 legs, 4 on each side)
            leg_positions = []
            for i in range(8):
                angle = math.pi * i / 4 + (math.pi / 8)  # Offset by 22.5 degrees
                # Animate legs using sine wave
                leg_anim = math.sin(self._time * 4 + i) * 0.2
                x = center[0] + size//2 * math.cos(angle + leg_anim)
                y = center[1] + size//2 * math.sin(angle + leg_anim)
                leg_positions.append((x, y))
            
            # Draw legs
            for pos in leg_positions:
                # Draw each leg as a series of segments
                segment_points = [
                    center,
                    (
                        center[0] + (pos[0] - center[0]) * 0.5,
                        center[1] + (pos[1] - center[1]) * 0.5
                    ),
                    pos
                ]
                pygame.draw.lines(surface, color, False, segment_points, max(2, size//20))
            
            # Draw spider body (abdomen and cephalothorax)
            # Abdomen (rear part)
            abdomen_rect = pygame.Rect(
                center[0] - size//4,
                center[1] - size//6,
                size//2,
                size//3
            )
            pygame.draw.ellipse(surface, color, abdomen_rect)
            
            # Cephalothorax (front part)
            head_size = size//3
            pygame.draw.circle(surface, color, center, head_size//2)
            
            # Draw eyes (8 eyes in two rows)
            eye_color = (255, 0, 0)  # Red eyes
            eye_positions = [
                # Top row
                (center[0] - head_size//4, center[1] - head_size//4),
                (center[0] - head_size//8, center[1] - head_size//4),
                (center[0] + head_size//8, center[1] - head_size//4),
                (center[0] + head_size//4, center[1] - head_size//4),
                # Bottom row
                (center[0] - head_size//4, center[1] - head_size//8),
                (center[0] - head_size//8, center[1] - head_size//8),
                (center[0] + head_size//8, center[1] - head_size//8),
                (center[0] + head_size//4, center[1] - head_size//8)
            ]
            
            for pos in eye_positions:
                # Draw red eyes
                pygame.draw.circle(surface, eye_color, pos, size//20)
                # Add white shine to eyes
                shine_pos = (pos[0] - 1, pos[1] - 1)
                pygame.draw.circle(surface, (255, 255, 255), shine_pos, size//40)
            
            # Randomly add web particles
            if random.random() < 0.1:
                web_pos = (
                    random.randint(0, size),
                    random.randint(0, size)
                )
                self._particles.append(Particle(
                    x=web_pos[0],
                    y=web_pos[1],
                    dx=random.uniform(-0.2, 0.2),
                    dy=random.uniform(-0.2, 0.2),
                    color=(255, 255, 255, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_spider: {e}")
            return False

    def _render_prism_elemental(self, surface, size, direction=None):
        """Render a prism elemental with rainbow patterns and light effects."""
        try:
            # Rainbow colors for prismatic effect
            rainbow_colors = [
                (255, 0, 0),    # Red
                (255, 127, 0),  # Orange
                (255, 255, 0),  # Yellow
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (75, 0, 130),   # Indigo
                (148, 0, 211)   # Violet
            ]
            
            center = (size // 2, size // 2)
            base_radius = size // 3
            
            # Draw prismatic core with rotating colors
            time_offset = int(time.time() * 2)  # Rotation speed
            for i in range(7):
                color_index = (i + time_offset) % len(rainbow_colors)
                angle = 2 * math.pi * i / 7
                
                # Calculate triangle points for each color segment
                point1 = (center[0], center[1])
                point2 = (
                    center[0] + math.cos(angle) * base_radius,
                    center[1] + math.sin(angle) * base_radius
                )
                point3 = (
                    center[0] + math.cos(angle + 2*math.pi/7) * base_radius,
                    center[1] + math.sin(angle + 2*math.pi/7) * base_radius
                )
                
                # Draw color segment
                pygame.draw.polygon(surface, rainbow_colors[color_index], 
                                 [point1, point2, point3])
            
            # Draw outer ring
            pygame.draw.circle(surface, (255, 255, 255), center, base_radius, 2)
            
            # Draw glowing white eyes
            eye_color = (255, 255, 255)
            eye_radius = size // 12
            left_eye = (center[0] - size//6, center[1] - size//8)
            right_eye = (center[0] + size//6, center[1] - size//8)
            
            # Draw eye glow
            for r in range(2):
                glow_radius = eye_radius + r * 2
                pygame.draw.circle(surface, eye_color, left_eye, glow_radius)
                pygame.draw.circle(surface, eye_color, right_eye, glow_radius)
            
            # Add rainbow particles with 50% chance
            if random.random() < 0.5:
                for _ in range(3):
                    pos = (random.randint(0, size), random.randint(0, size))
                    color = random.choice(rainbow_colors)
                    particle_size = random.randint(2, 4)
                    self._draw_particles(surface, pos, color, particle_size)
            
            return True
            
        except Exception as e:
            print(f"Error rendering prism elemental: {str(e)}")
            return False

    def _render_unicorn(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render unicorn monsters with a majestic appearance."""
        try:
            unicorn_color = self._sanitize_color((255, 255, 255))  # Pure white
            center = (size//2, size//2)
            
            # Draw main body (oval shape)
            body_rect = pygame.Rect(
                center[0] - size//2,
                center[1] - size//4,
                size * 3//4,
                size//2
            )
            pygame.draw.ellipse(surface, unicorn_color, body_rect)
            
            # Draw neck and head
            neck_points = [
                (center[0] - size//4, center[1]),
                (center[0] - size//3, center[1] - size//4),
                (center[0] - size//2, center[1] - size//3)
            ]
            pygame.draw.lines(surface, unicorn_color, False, neck_points, max(3, size//10))
            
            # Draw head
            head_center = (center[0] - size//2, center[1] - size//3)
            pygame.draw.circle(surface, unicorn_color, head_center, size//6)
            
            # Draw horn with rainbow gradient
            horn_colors = [
                (255, 200, 200),  # Pink
                (255, 255, 200),  # Yellow
                (200, 255, 200),  # Light green
                (200, 200, 255)   # Light blue
            ]
            
            horn_start = (head_center[0], head_center[1] - size//8)
            horn_end = (head_center[0] - size//4, head_center[1] - size//3)
            
            # Draw horn segments with gradient
            segments = len(horn_colors)
            for i in range(segments):
                start_pos = (
                    horn_start[0] + (horn_end[0] - horn_start[0]) * i / segments,
                    horn_start[1] + (horn_end[1] - horn_start[1]) * i / segments
                )
                end_pos = (
                    horn_start[0] + (horn_end[0] - horn_start[0]) * (i + 1) / segments,
                    horn_start[1] + (horn_end[1] - horn_start[1]) * (i + 1) / segments
                )
                pygame.draw.line(surface, horn_colors[i], start_pos, end_pos, max(2, size//20))
            
            # Draw flowing mane with slight animation
            mane_color = (255, 220, 180)  # Light golden
            mane_points = []
            for i in range(8):
                wave = math.sin(self._time * 3 + i) * size//16
                x = center[0] - size//3 + (i * size//16)
                y = center[1] - size//4 + wave
                mane_points.append((x, y))
            
            if len(mane_points) > 1:
                pygame.draw.lines(surface, mane_color, False, mane_points, max(2, size//15))
            
            # Draw eye
            eye_pos = (head_center[0] + size//12, head_center[1])
            pygame.draw.circle(surface, (100, 100, 255), eye_pos, size//20)  # Blue eyes
            pygame.draw.circle(surface, (255, 255, 255), eye_pos, size//40)  # Eye shine
            
            # Add sparkle particles
            if random.random() < 0.2:
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(size//4, size//2)
                    sparkle_pos = (
                        center[0] + math.cos(angle) * distance,
                        center[1] + math.sin(angle) * distance
                    )
                    self._particles.append(Particle(
                        x=sparkle_pos[0],
                        y=sparkle_pos[1],
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(-0.5, 0.5),
                        color=(255, 255, 255, 180),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 3)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_unicorn: {e}")
            return False

    def _render_shadow(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render shadow monsters with ethereal dark effects."""
        try:
            shadow_color = self._sanitize_color((20, 20, 30))  # Very dark blue-gray
            center = (size//2, size//2)
            
            # Create multiple layers of transparency for depth
            for i in range(4):
                alpha = 150 - i * 30  # Decreasing opacity for each layer
                shadow_size = size//2 - i * size//10
                
                # Create distorted circle with wave effect
                points = []
                num_points = 15
                for j in range(num_points):
                    angle = 2 * math.pi * j / num_points
                    # Add waviness based on time
                    wave = math.sin(self._time * 3 + j) * size//10
                    radius = shadow_size + wave
                    x = center[0] + radius * math.cos(angle)
                    y = center[1] + radius * math.sin(angle)
                    points.append((x, y))
                
                # Draw the shadow layer
                shadow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                if len(points) > 2:
                    pygame.draw.polygon(shadow_surface, (*shadow_color, alpha), points)
                surface.blit(shadow_surface, (0, 0))
            
            # Add glowing eyes
            eye_color = (255, 0, 0)  # Red eyes
            eye_size = size//8
            eye_spacing = size//4
            
            # Pulsing eye effect
            eye_pulse = (math.sin(self._time * 2) + 1) / 2
            current_eye_size = eye_size * (0.8 + eye_pulse * 0.4)
            
            # Draw eyes with glow effect
            for x_offset in [-eye_spacing//2, eye_spacing//2]:
                eye_pos = (center[0] + x_offset, center[1])
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 30), eye_pos, current_eye_size * 2)
                pygame.draw.circle(surface, (*eye_color, 60), eye_pos, current_eye_size * 1.5)
                # Inner eye
                pygame.draw.circle(surface, (*eye_color, 150), eye_pos, current_eye_size)
                pygame.draw.circle(surface, (255, 255, 255, 200), eye_pos, current_eye_size * 0.3)
            
            # Add shadow particles
            if random.random() < 0.3:
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(size//4, size//2)
                    particle_pos = (
                        center[0] + math.cos(angle) * distance,
                        center[1] + math.sin(angle) * distance
                    )
                    
                    self._particles.append(Particle(
                        x=particle_pos[0],
                        y=particle_pos[1],
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-1, 1),
                        color=(*shadow_color, 100),
                        life=random.uniform(0.5, 1.0),
                        size=random.uniform(3, 6)
                    ))
            
            # Add occasional dark tendrils
            if random.random() < 0.1:
                start_angle = random.uniform(0, math.pi * 2)
                tendril_points = [(center[0], center[1])]
                
                for i in range(3):
                    prev_point = tendril_points[-1]
                    angle = start_angle + random.uniform(-math.pi/4, math.pi/4)
                    length = random.uniform(size//8, size//4)
                    new_point = (
                        prev_point[0] + math.cos(angle) * length,
                        prev_point[1] + math.sin(angle) * length
                    )
                    tendril_points.append(new_point)
                
                if len(tendril_points) > 1:
                    tendril_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    pygame.draw.lines(tendril_surface, (*shadow_color, 100), False, tendril_points, max(2, size//20))
                    surface.blit(tendril_surface, (0, 0))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_shadow: {e}")
            return False

    def _render_zombie(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render zombie monsters with decaying undead features."""
        try:
            zombie_color = self._sanitize_color((124, 252, 0))  # Sickly green
            skin_color = self._sanitize_color((150, 170, 150))  # Grayish skin
            center = (size//2, size//2)
            
            # Draw decaying body with uneven shape
            body_points = []
            num_points = 8
            base_radius = size//3
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                # Add irregular bumps and deformities
                deformity = math.sin(self._time * 2 + i * 3) * size//10
                radius = base_radius + deformity
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                body_points.append((x, y))
            
            if len(body_points) > 2:
                pygame.draw.polygon(surface, skin_color, body_points)
            
            # Draw rotting patches
            for _ in range(3):
                patch_pos = (
                    center[0] + random.uniform(-size//4, size//4),
                    center[1] + random.uniform(-size//4, size//4)
                )
                patch_size = random.uniform(size//8, size//6)
                pygame.draw.circle(surface, zombie_color, patch_pos, patch_size)
            
            # Draw asymmetric eyes
            eye_color = (255, 255, 0)  # Yellow eyes
            
            # Left eye (larger)
            left_eye_pos = (center[0] - size//5, center[1] - size//8)
            pygame.draw.circle(surface, eye_color, left_eye_pos, size//8)
            pygame.draw.circle(surface, (0, 0, 0), left_eye_pos, size//16)
            
            # Right eye (smaller, showing decay)
            right_eye_pos = (center[0] + size//5, center[1] - size//10)
            pygame.draw.circle(surface, eye_color, right_eye_pos, size//10)
            pygame.draw.circle(surface, (0, 0, 0), right_eye_pos, size//20)
            
            # Draw jagged mouth
            mouth_points = []
            mouth_y = center[1] + size//6
            for i in range(5):
                x = center[0] - size//4 + (i * size//8)
                y = mouth_y + (math.sin(i * 2) * size//16)
                mouth_points.append((x, y))
            
            if len(mouth_points) > 1:
                pygame.draw.lines(surface, (100, 0, 0), False, mouth_points, max(2, size//20))
            
            # Add decay particles
            if random.random() < 0.2:
                particle_pos = (
                    center[0] + random.uniform(-size//3, size//3),
                    center[1] + random.uniform(-size//3, size//3)
                )
                self._particles.append(Particle(
                    x=particle_pos[0],
                    y=particle_pos[1],
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-1, -0.5),
                    color=(100, 150, 100, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_zombie: {e}")
            return False

    def _render_dryad(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render dryad monsters with nature and leaf effects."""
        try:
            dryad_color = self._sanitize_color((34, 139, 34))  # Forest green
            center = (size//2, size//2)
            
            # Draw main body with pulsing effect
            body_radius = int(size//3 * (1 + anim['pulse'] * 0.1))
            pygame.draw.circle(surface, dryad_color, center, body_radius)
            
            # Draw leaf patterns that rotate slowly
            num_leaves = 6
            leaf_color = (45, 160, 45)  # Slightly lighter green
            for i in range(num_leaves):
                angle = 2 * math.pi * i / num_leaves + self._time * 0.5
                leaf_distance = size//3
                leaf_pos = (
                    center[0] + math.cos(angle) * leaf_distance,
                    center[1] + math.sin(angle) * leaf_distance
                )
                leaf_size = size//6
                
                # Draw leaf
                leaf_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.ellipse(leaf_surface, (*leaf_color, 180),
                                 (leaf_pos[0] - leaf_size//2,
                                  leaf_pos[1] - leaf_size//2,
                                  leaf_size, leaf_size))
                surface.blit(leaf_surface, (0, 0))
            
            # Draw glowing eyes
            eye_color = (255, 255, 255)  # White
            eye_radius = size//10
            left_eye = (center[0] - size//6, center[1] - size//8)
            right_eye = (center[0] + size//6, center[1] - size//8)
            
            # Eye glow effect
            for r in range(2):
                glow_radius = eye_radius + r * 2
                glow_alpha = 255 - r * 100
                eye_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(eye_surface, (*eye_color, glow_alpha), left_eye, glow_radius)
                pygame.draw.circle(eye_surface, (*eye_color, glow_alpha), right_eye, glow_radius)
                surface.blit(eye_surface, (0, 0))
            
            # Add flower/leaf particles
            if random.random() < 0.3:
                particle_colors = [
                    (255, 192, 203, 150),  # Pink
                    (255, 182, 193, 150),  # Light pink
                    (152, 251, 152, 150)   # Pale green
                ]
                
                for _ in range(2):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(size//4, size//2)
                    particle_x = center[0] + math.cos(angle) * distance
                    particle_y = center[1] + math.sin(angle) * distance
                    
                    self._particles.append(Particle(
                        x=particle_x,
                        y=particle_y,
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(-0.5, 0.5),
                        color=random.choice(particle_colors),
                        life=random.uniform(0.5, 1.0),
                        size=random.uniform(3, 5)
                    ))
            
            self._draw_particles(surface)
            return True
            
        except Exception as e:
            print(f"Error rendering dryad: {str(e)}")
            return False

    def _render_nightmare(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render nightmare monsters with dark horse and shadow features."""
        try:
            nightmare_color = self._sanitize_color((75, 0, 130))  # Dark purple
            shadow_color = self._sanitize_color((20, 20, 30))    # Very dark blue-gray
            center = (size//2, size//2)
            
            # Create shadow effect base
            for i in range(3):
                alpha = 150 - i * 40
                shadow_radius = size//2 - i * size//8
                shadow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # Create distorted shadow circle
                points = []
                num_points = 12
                for j in range(num_points):
                    angle = 2 * math.pi * j / num_points
                    # Add waviness based on time
                    wave = math.sin(self._time * 3 + j) * size//12
                    radius = shadow_radius + wave
                    x = center[0] + radius * math.cos(angle)
                    y = center[1] + radius * math.sin(angle)
                    points.append((x, y))
                
                if len(points) > 2:
                    pygame.draw.polygon(shadow_surface, (*shadow_color, alpha), points)
                surface.blit(shadow_surface, (0, 0))
            
            # Draw horse-like body
            body_rect = pygame.Rect(
                center[0] - size//2,
                center[1] - size//4,
                size * 3//4,
                size//2
            )
            pygame.draw.ellipse(surface, nightmare_color, body_rect)
            
            # Draw flowing mane made of shadows
            mane_points = []
            num_mane_points = 8
            for i in range(num_mane_points):
                wave = math.sin(self._time * 4 + i) * size//8
                x = center[0] - size//4 + (i * size//16)
                y = center[1] - size//4 + wave
                mane_points.append((x, y))
            
            if len(mane_points) > 1:
                # Draw multiple layers of mane for ethereal effect
                for i in range(3):
                    mane_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                    offset_points = [(x + i*2, y + i*2) for x, y in mane_points]
                    pygame.draw.lines(mane_surface, (*shadow_color, 100), False, 
                                   offset_points, max(2, size//15))
                    surface.blit(mane_surface, (0, 0))
            
            # Draw glowing eyes
            eye_color = (255, 0, 0)  # Red
            eye_size = size//8
            eye_spacing = size//3
            
            # Pulsing eye effect
            eye_pulse = (math.sin(self._time * 2) + 1) / 2
            current_eye_size = eye_size * (0.8 + eye_pulse * 0.4)
            
            # Draw eyes with glow effect
            for x_offset in [-eye_spacing//2, eye_spacing//2]:
                eye_pos = (center[0] + x_offset, center[1] - size//8)
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 30), eye_pos, current_eye_size * 2)
                pygame.draw.circle(surface, (*eye_color, 60), eye_pos, current_eye_size * 1.5)
                # Inner eye
                pygame.draw.circle(surface, (*eye_color, 200), eye_pos, current_eye_size)
                pygame.draw.circle(surface, (255, 255, 255, 200), eye_pos, current_eye_size * 0.3)
            
            # Add shadow trail particles
            if random.random() < 0.3:
                for _ in range(2):
                    trail_pos = (
                        center[0] + random.uniform(-size//3, size//3),
                        center[1] + random.uniform(-size//3, size//3)
                    )
                    self._particles.append(Particle(
                        x=trail_pos[0],
                        y=trail_pos[1],
                        dx=random.uniform(-1, 1),
                        dy=random.uniform(-1, 1),
                        color=(*shadow_color, 100),
                        life=random.uniform(0.5, 1.0),
                        size=random.uniform(3, 6)
                    ))
            
            # Add occasional flame particles from hooves
            if random.random() < 0.2:
                hoof_positions = [
                    (center[0] - size//3, center[1] + size//4),
                    (center[0] + size//3, center[1] + size//4)
                ]
                for hoof_pos in hoof_positions:
                    self._particles.append(Particle(
                        x=hoof_pos[0],
                        y=hoof_pos[1],
                        dx=random.uniform(-0.5, 0.5),
                        dy=random.uniform(-2, -1),
                        color=(255, 0, 0, 150),
                        life=random.uniform(0.3, 0.6),
                        size=random.uniform(2, 4)
                    ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_nightmare: {e}")
            return False

    def _render_basilisk(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render basilisk monsters with snake-like features."""
        try:
            basilisk_color = self._sanitize_color((0, 180, 0))  # Green
            center = (size//2, size//2)
            
            # Draw snake-like body
            body_points = []
            num_segments = 8
            amplitude = size//6
            for i in range(num_segments):
                x = center[0] - size//3 + (i * size//num_segments)
                y = center[1] + math.sin(self._time * 4 + i) * amplitude
                body_points.append((x, y))
            
            # Draw body segments
            if len(body_points) > 1:
                pygame.draw.lines(surface, basilisk_color, False, body_points, max(3, size//8))
            
            # Draw head
            head_pos = body_points[0] if body_points else center
            pygame.draw.circle(surface, basilisk_color, head_pos, size//6)
            
            # Draw eyes with glow effect
            eye_color = (255, 255, 0)  # Yellow eyes
            eye_size = size//12
            eye_offset = size//16
            
            # Left eye
            left_eye = (head_pos[0] - eye_offset, head_pos[1] - eye_offset)
            pygame.draw.circle(surface, eye_color, left_eye, eye_size)
            pygame.draw.circle(surface, (255, 0, 0), left_eye, eye_size//2)  # Red center
            
            # Right eye
            right_eye = (head_pos[0] + eye_offset, head_pos[1] - eye_offset)
            pygame.draw.circle(surface, eye_color, right_eye, eye_size)
            pygame.draw.circle(surface, (255, 0, 0), right_eye, eye_size//2)  # Red center
            
            # Add scale particles
            if random.random() < 0.2:
                for point in body_points:
                    if random.random() < 0.3:
                        self._particles.append(Particle(
                            x=point[0],
                            y=point[1],
                            dx=random.uniform(-0.5, 0.5),
                            dy=random.uniform(-0.5, 0.5),
                            color=(0, 255, 0, 128),
                            life=random.uniform(0.3, 0.6),
                            size=random.uniform(2, 4)
                        ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_basilisk: {e}")
            return False

    def _render_clockwork_knight(self, surface: pygame.Surface, size: int, direction: Direction = None, anim: dict = None) -> bool:
        """Render a clockwork knight with mechanical details."""
        try:
            # Handle both integer and tuple sizes
            if isinstance(size, int):
                width = height = size
            else:
                width, height = size
            
            # Draw the base mechanical body
            self._render_mechanical(surface, size, direction, anim)
            
            # Add knight-specific details
            center_x = width // 2
            center_y = height // 2
            
            # Draw a helmet-like structure
            helmet_color = (100, 100, 100)  # Steel gray
            helmet_rect = pygame.Rect(
                center_x - width // 4,
                center_y - height // 3,
                width // 2,
                height // 4
            )
            pygame.draw.rect(surface, helmet_color, helmet_rect)
            
            # Draw a visor
            visor_color = (50, 50, 50)  # Dark gray
            visor_rect = pygame.Rect(
                center_x - width // 6,
                center_y - height // 4,
                width // 3,
                height // 8
            )
            pygame.draw.rect(surface, visor_color, visor_rect)
            
            # Add steam particles
            if random.random() < 0.3:  # 30% chance of steam
                particle_x = random.randint(width//4, 3*width//4)
                particle_y = random.randint(height//4, 3*height//4)
                particle_size = random.randint(2, 4)
                pygame.draw.circle(surface, (200, 200, 200, 150), (particle_x, particle_y), particle_size)
            
            return True
        except Exception as e:
            print(f"Error in clockwork knight render: {e}")
            return False

    def _render_vampire(self, surface: pygame.Surface, size: int, direction: Direction = None, anim: dict = None) -> bool:
        """Render a vampire monster."""
        try:
            # Draw dark body
            pygame.draw.circle(surface, (40, 0, 40), (size//2, size//2), size//2)
            
            # Draw cape
            cape_points = [
                (size//2, size//2),
                (size//2 - size//3, size//2 + size//3),
                (size//2 + size//3, size//2 + size//3)
            ]
            pygame.draw.polygon(surface, (20, 0, 20), cape_points)
            
            # Draw glowing red eyes
            eye_color = (255, 0, 0)
            eye_size = size//8
            left_eye = (size//2 - size//4, size//2 - size//6)
            right_eye = (size//2 + size//4, size//2 - size//6)
            pygame.draw.circle(surface, eye_color, left_eye, eye_size)
            pygame.draw.circle(surface, eye_color, right_eye, eye_size)
            
            # Add blood mist particles
            if random.random() < 0.2:  # 20% chance of blood mist
                particle_x = random.randint(size//4, 3*size//4)
                particle_y = random.randint(size//4, 3*size//4)
                particle_size = random.randint(2, 4)
                pygame.draw.circle(surface, (255, 0, 0, 100), (particle_x, particle_y), particle_size)
            
            return True
        except Exception as e:
            print(f"Error in vampire render: {e}")
            return False

    def _render_mermaid(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render mermaid monsters with aquatic features."""
        try:
            mermaid_color = self._sanitize_color((0, 100, 100))  # Teal
            center = (size//2, size//2)
            
            # Draw main body (fish-like)
            body_rect = pygame.Rect(
                center[0] - size//4,
                center[1] - size//6,
                size//2,
                size//3
            )
            pygame.draw.ellipse(surface, mermaid_color, body_rect)
            
            # Draw fins
            fin_color = (255, 255, 255, 128)
            for i in range(4):
                angle = math.pi * i / 4 + (math.pi / 8)  # Offset by 22.5 degrees
                fin_points = [
                    center,
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//12),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//6),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//4)
                ]
                pygame.draw.polygon(surface, fin_color, fin_points)
            
            # Draw eyes
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            # Add water splash particles
            if random.random() < 0.1:
                splash_pos = (
                    random.randint(center[0] - size//4, center[0] + size//4),
                    random.randint(center[1] - size//6, center[1] + size//6)
                )
                self._particles.append(Particle(
                    x=splash_pos[0],
                    y=splash_pos[1],
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(100, 150, 200, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_mermaid: {e}")
            return False

    def _render_kraken(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render kraken monsters with tentacle-like features."""
        try:
            kraken_color = self._sanitize_color((100, 100, 100))  # Gray
            center = (size//2, size//2)
            
            # Draw main body (cylinder)
            body_rect = pygame.Rect(
                center[0] - size//4,
                center[1] - size//6,
                size//2,
                size//3
            )
            pygame.draw.ellipse(surface, kraken_color, body_rect)
            
            # Draw tentacles
            tentacle_color = (255, 255, 255, 128)
            for i in range(6):
                angle = math.pi * i / 6 + (math.pi / 8)  # Offset by 22.5 degrees
                tentacle_points = [
                    center,
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//12),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//6),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//4)
                ]
                pygame.draw.polygon(surface, tentacle_color, tentacle_points)
            
            # Draw eyes
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            # Add water splash particles
            if random.random() < 0.1:
                splash_pos = (
                    random.randint(center[0] - size//4, center[0] + size//4),
                    random.randint(center[1] - size//6, center[1] + size//6)
                )
                self._particles.append(Particle(
                    x=splash_pos[0],
                    y=splash_pos[1],
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(100, 150, 200, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_kraken: {e}")
            return False

    def _render_siren(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render siren monsters with enchanting voice and aquatic features."""
        try:
            siren_color = self._sanitize_color((255, 100, 100))  # Pink
            center = (size//2, size//2)
            
            # Draw main body (fish-like)
            body_rect = pygame.Rect(
                center[0] - size//4,
                center[1] - size//6,
                size//2,
                size//3
            )
            pygame.draw.ellipse(surface, siren_color, body_rect)
            
            # Draw fins
            fin_color = (255, 255, 255, 128)
            for i in range(4):
                angle = math.pi * i / 4 + (math.pi / 8)  # Offset by 22.5 degrees
                fin_points = [
                    center,
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//12),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//6),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//4)
                ]
                pygame.draw.polygon(surface, fin_color, fin_points)
            
            # Draw eyes
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            # Add water splash particles
            if random.random() < 0.1:
                splash_pos = (
                    random.randint(center[0] - size//4, center[0] + size//4),
                    random.randint(center[1] - size//6, center[1] + size//6)
                )
                self._particles.append(Particle(
                    x=splash_pos[0],
                    y=splash_pos[1],
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(100, 150, 200, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_siren: {e}")
            return False

    def _render_leviathan(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render leviathan monsters with massive size and aquatic features."""
        try:
            leviathan_color = self._sanitize_color((100, 100, 100))  # Gray
            center = (size//2, size//2)
            
            # Draw main body (cylinder)
            body_rect = pygame.Rect(
                center[0] - size//4,
                center[1] - size//6,
                size//2,
                size//3
            )
            pygame.draw.ellipse(surface, leviathan_color, body_rect)
            
            # Draw tentacles
            tentacle_color = (255, 255, 255, 128)
            for i in range(6):
                angle = math.pi * i / 6 + (math.pi / 8)  # Offset by 22.5 degrees
                tentacle_points = [
                    center,
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//12),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//6),
                    (center[0] + size//4 * math.cos(angle),
                     center[1] - size//6 + size//4)
                ]
                pygame.draw.polygon(surface, tentacle_color, tentacle_points)
            
            # Draw eyes
            eye_color = (255, 255, 255)
            eye_positions = [
                (center[0] - size//6, center[1] - size//8),
                (center[0] + size//6, center[1] - size//8)
            ]
            
            for pos in eye_positions:
                pygame.draw.circle(surface, eye_color, pos, size//12)
                pygame.draw.circle(surface, (0, 0, 0), pos, size//16)
            
            # Add water splash particles
            if random.random() < 0.1:
                splash_pos = (
                    random.randint(center[0] - size//4, center[0] + size//4),
                    random.randint(center[1] - size//6, center[1] + size//6)
                )
                self._particles.append(Particle(
                    x=splash_pos[0],
                    y=splash_pos[1],
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(100, 150, 200, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_leviathan: {e}")
            return False

    def _render_water_spirit(self, surface: pygame.Surface, size: int, direction: Direction, anim: dict):
        """Render water spirit monsters with ethereal aquatic effects."""
        try:
            water_spirit_color = self._sanitize_color((0, 100, 100))  # Teal
            center = (size//2, size//2)
            
            # Create a pulsing, transparent form
            pulse = (math.sin(self._time * 2) + 1) / 2
            for i in range(3):
                alpha = int(128 * (1 - i/3) * (0.5 + pulse * 0.5))
                radius = size//3 * (1 + i * 0.2)
                ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(ghost_surface, (*water_spirit_color[:3], alpha), center, int(radius))
                surface.blit(ghost_surface, (0, 0))
            
            # Add floating movement
            float_y = math.sin(self._time * 3) * size//10
            
            # Draw main form
            main_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            main_points = [
                (center[0], center[1] - size//3 + float_y),
                (center[0] - size//3, center[1] + size//3 + float_y),
                (center[0] + size//3, center[1] + size//3 + float_y)
            ]
            pygame.draw.polygon(main_surface, (*water_spirit_color[:3], 192), main_points)
            surface.blit(main_surface, (0, 0))
            
            # Draw glowing eyes
            eye_color = (255, 255, 255)
            eye_spacing = size//6
            eye_y = center[1] - size//6 + float_y
            
            for x_offset in [-eye_spacing, eye_spacing]:
                eye_x = center[0] + x_offset
                # Outer glow
                pygame.draw.circle(surface, (*eye_color, 64), (eye_x, eye_y), size//10)
                # Inner glow
                pygame.draw.circle(surface, (*eye_color, 128), (eye_x, eye_y), size//16)
                # Core
                pygame.draw.circle(surface, eye_color, (eye_x, eye_y), size//24)
            
            # Add ethereal particles
            if random.random() < 0.2:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(size//6, size//3)
                self._particles.append(Particle(
                    x=center[0] + math.cos(angle) * distance,
                    y=center[1] + math.sin(angle) * distance + float_y,
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-0.5, 0.5),
                    color=(*water_spirit_color[:3], 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(3, 6)
                ))
            
            self._draw_particles(surface)
            return True
        except Exception as e:
            print(f"Error in _render_water_spirit: {e}")
            return False
