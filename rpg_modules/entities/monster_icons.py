import pygame
import math
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from rpg_modules.entities.monster import MonsterType

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
                          pupil_color: Tuple[int, int, int] = (0, 0, 0)):
        """Draw animated eyes with movement."""
        # Eye white
        pygame.draw.ellipse(surface, eye_color, 
                          (x - size//8, y - size//8, 
                           size//4, size//4))
        # Pupil movement
        pupil_x = x + int(size//16 * math.sin(self._time * 2))
        pupil_y = y + int(size//16 * math.sin(self._time * 1.5))
        pygame.draw.circle(surface, pupil_color, (pupil_x, pupil_y), size//12)

    def _draw_particles(self, surface: pygame.Surface):
        """Draw all active particles."""
        for particle in self._particles:
            pygame.draw.circle(surface, particle.color,
                             (int(particle.x), int(particle.y)), 
                             int(particle.size))

class MonsterIcon(AnimatedIcon):
    def __init__(self, monster_type: MonsterType):
        super().__init__()
        self.monster_type = monster_type

    def render(self, surface: pygame.Surface, size: int):
        """Render a monster icon with animations based on its type."""
        anim = self._get_animation_values()
        
        # Call the appropriate render method based on monster type
        render_method = getattr(self, f"_render_{self.monster_type.name.lower()}", None)
        if render_method:
            render_method(surface, size, anim)
        else:
            # Default rendering for unknown monster types
            self._render_default(surface, size, anim)

    def _render_default(self, surface: pygame.Surface, size: int, anim: dict):
        """Default rendering for unknown monster types."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (150, 150, 150), (size//2, size//2), size//3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Default particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 150, 150),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    # Add all the monster-specific render methods here
    # (These will be moved from monster_icon_test.py)
    def _render_dragon(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a dragon monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        
        # Body
        body_color = (200, 0, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wings
        wing_color = (150, 0, 0)
        wing_size = size//2
        wing_angle = math.sin(self._time * 2) * 15
        pygame.draw.ellipse(surface, wing_color,
                          (size//4, size//4, wing_size, wing_size//2),
                          int(wing_angle))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Fire particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-2, -1),
                color=(255, 100, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_spider(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a spider monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (100, 100, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//4)
        
        # Legs
        leg_color = (80, 80, 80)
        for i in range(8):
            angle = i * math.pi / 4 + math.sin(self._time * 2) * 0.2
            leg_length = size//3
            start_x = size//2
            start_y = size//2
            end_x = start_x + math.cos(angle) * leg_length
            end_y = start_y + math.sin(angle) * leg_length
            pygame.draw.line(surface, leg_color,
                           (start_x, start_y), (end_x, end_y), 2)
        
        # Eyes
        eye_positions = [
            (size//3, size//3),
            (size*2//3, size//3),
            (size//3, size*2//3),
            (size*2//3, size*2//3)
        ]
        for x, y in eye_positions:
            self._draw_animated_eyes(surface, x, y, size//4,
                                   (255, 255, 255), (0, 0, 0))
        
        # Web particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(200, 200, 200),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_ghost(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a ghost monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (200, 200, 200)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wavy bottom
        wavy_color = (150, 150, 150)
        for i in range(4):
            angle = i * (math.pi / 2) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + size//3
            pygame.draw.circle(surface, wavy_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Ectoplasm particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 200, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_skeleton(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a skeleton monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Skull
        skull_color = (200, 200, 200)
        pygame.draw.circle(surface, skull_color, (size//2, size//2), size//3)
        
        # Jaw
        jaw_color = (150, 150, 150)
        jaw_y = size//2 + size//6
        pygame.draw.arc(surface, jaw_color,
                       (size//2 - size//4, jaw_y - size//8,
                        size//2, size//4),
                       0, math.pi, 2)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Ribs
        rib_color = (150, 150, 150)
        for i in range(4):
            x = size//2 + (i * 2 - 3) * size//8
            y = size//2 + size//4
            pygame.draw.circle(surface, rib_color, (x, y), size//8)
        
        # Arms
        arm_color = (150, 150, 150)
        for i in range(2):
            angle = i * math.pi + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.line(surface, arm_color,
                           (size//2, size//2),
                           (x, y), 2)
        
        # Bone particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 200, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_slime(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a slime monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 50, 0), size)
        
        # Body
        body_color = (0, 200, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wavy surface
        wavy_color = (0, 150, 0)
        for i in range(4):
            angle = i * (math.pi / 2) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + size//3
            pygame.draw.circle(surface, wavy_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 100, 0))
        
        # Slime particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 200, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_thought_devourer(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a thought devourer monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (100, 0, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Brain texture
        brain_color = (150, 0, 150)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, brain_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 0, 100))
        
        # Thought particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_memory_phantom(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a memory phantom monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (100, 0, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Memory fragments
        fragment_color = (150, 0, 150)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, fragment_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 0, 100))
        
        # Memory particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_psychic_hydra(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a psychic hydra monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (100, 0, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Heads
        head_color = (150, 0, 150)
        for i in range(3):
            angle = i * (2 * math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.circle(surface, head_color, (x, y), size//4)
            
            # Necks
            neck_color = (100, 0, 100)
            pygame.draw.line(surface, neck_color,
                           (size//2, size//2),
                           (x, y), 2)
            
            # Eyes
            eye_color = (255, 255, 255)
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 0, 100))
        
        # Psychic particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_mind_colossus(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a mind colossus monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (100, 0, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Mind patterns
        pattern_color = (150, 0, 150)
        for i in range(8):
            angle = i * (math.pi / 4) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 0, 100))
        
        # Mind particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_fire_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a fire elemental monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 0), size)
        
        # Body
        body_color = (255, 100, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Flame patterns
        flame_color = (255, 150, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, flame_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 0, 0))
        
        # Fire particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 100, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_ice_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an ice elemental monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 50), size)
        
        # Body
        body_color = (150, 200, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Ice crystals
        crystal_color = (200, 230, 255)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, crystal_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 255))
        
        # Ice particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 200, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_storm_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a storm elemental monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 50), size)
        
        # Body
        body_color = (100, 100, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Lightning patterns
        lightning_color = (150, 150, 255)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, lightning_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 255))
        
        # Storm particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_earth_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an earth golem monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 25, 0), size)
        
        # Body
        body_color = (150, 75, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Rock patterns
        rock_color = (100, 50, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, rock_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (150, 75, 0))
        
        # Earth particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 75, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_zombie(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a zombie monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 0), size)
        
        # Body
        body_color = (100, 100, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Rotting patches
        patch_color = (150, 150, 0)
        for i in range(4):
            angle = i * (math.pi / 2) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, patch_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Rot particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (100, 100, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Ethereal patterns
        pattern_color = (150, 150, 150)
        for i in range(4):
            angle = i * (math.pi / 2) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Ethereal particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_vampire(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a vampire monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        
        # Body
        body_color = (200, 0, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Blood patterns
        pattern_color = (255, 0, 0)
        for i in range(4):
            angle = i * (math.pi / 2) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 0, 0))
        
        # Blood particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 0, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_lich(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a lich monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (100, 0, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Arcane patterns
        pattern_color = (150, 0, 150)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 0, 100))
        
        # Arcane particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_forest_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a forest guardian monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 50, 0), size)
        
        # Body
        body_color = (0, 200, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Nature patterns
        nature_color = (0, 150, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, nature_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 200, 0))
        
        # Nature particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 200, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_vine_weaver(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a vine weaver monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 50, 0), size)
        
        # Body
        body_color = (0, 150, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Vine patterns
        vine_color = (0, 100, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, vine_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 150, 0))
        
        # Vine particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 150, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_moss_beast(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a moss beast monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 50, 0), size)
        
        # Body
        body_color = (100, 150, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Moss patterns
        moss_color = (50, 100, 50)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, moss_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 150, 100))
        
        # Moss particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 150, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_bloom_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a bloom spirit monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (255, 100, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Flower patterns
        flower_color = (200, 50, 200)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, flower_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 100, 255))
        
        # Bloom particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_pixie(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a pixie monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body
        body_color = (255, 100, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wings
        wing_color = (200, 100, 200)
        for i in range(2):
            angle = i * math.pi + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.circle(surface, wing_color, (x, y), size//4)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 100, 255))
        
        # Magic particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_phoenix(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a phoenix monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 0), size)
        
        # Body
        body_color = (255, 100, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wings
        wing_color = (255, 200, 0)
        for i in range(2):
            angle = i * math.pi + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.circle(surface, wing_color, (x, y), size//4)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 0, 0))
        
        # Fire particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 100, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_unicorn(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a unicorn monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (255, 255, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Horn
        horn_color = (100, 100, 255)
        pygame.draw.line(surface, horn_color,
                        (size//2, size//2 - size//3),
                        (size//2, size//2 - size//2), 2)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 100, 255))
        
        # Magic particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_griffin(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a griffin monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 0), size)
        
        # Body
        body_color = (255, 200, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wings
        wing_color = (255, 150, 0)
        for i in range(2):
            angle = i * math.pi + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.circle(surface, wing_color, (x, y), size//4)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 150, 0))
        
        # Feather particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 200, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_chimera_lord(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a chimera lord monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 0), size)
        
        # Body
        body_color = (255, 200, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Heads
        head_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for i, color in enumerate(head_colors):
            angle = i * (2 * math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//3
            y = size//2 + math.sin(angle) * size//3
            pygame.draw.circle(surface, color, (x, y), size//4)
            
            # Necks
            neck_color = (255, 200, 0)
            pygame.draw.line(surface, neck_color,
                           (size//2, size//2),
                           (x, y), 2)
            
            # Eyes
            eye_color = (255, 255, 255)
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Golden particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 200, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_world_serpent(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a world serpent monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (100, 100, 100)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Cosmic patterns
        cosmic_color = (150, 150, 150)
        for i in range(8):
            angle = i * (math.pi / 4) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, cosmic_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 100, 100))
        
        # Cosmic particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 100, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_golden_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a golden guardian monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 0), size)
        
        # Body
        body_color = (255, 200, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Divine patterns
        divine_color = (255, 150, 0)
        for i in range(8):
            angle = i * (math.pi / 4) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, divine_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 150, 0))
        
        # Divine particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 200, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_fate_sphinx(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a fate sphinx monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (255, 255, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Destiny patterns
        destiny_color = (200, 200, 200)
        for i in range(8):
            angle = i * (math.pi / 4) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, destiny_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (200, 200, 200))
        
        # Destiny particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_air_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an air spirit monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (200, 200, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wind patterns
        wind_color = (150, 150, 255)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, wind_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (200, 200, 255))
        
        # Air particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_water_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a water spirit monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 50), size)
        
        # Body
        body_color = (100, 100, 255)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Wave patterns
        wave_color = (50, 50, 255)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, wave_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (100, 100, 255))
        
        # Water particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_earth_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an earth spirit monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 25, 0), size)
        
        # Body
        body_color = (150, 75, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Rock patterns
        rock_color = (100, 50, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, rock_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (150, 75, 0))
        
        # Earth particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 75, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_fire_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a fire spirit monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 0), size)
        
        # Body
        body_color = (255, 100, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Flame patterns
        flame_color = (255, 150, 0)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, flame_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (255, 0, 0))
        
        # Fire particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 100, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_shadow_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a shadow wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (50, 50, 50)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Shadow patterns
        shadow_color = (25, 25, 25)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, shadow_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Shadow particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 50, 50, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_void_walker(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a void walker monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (0, 0, 0)
        pygame.draw.circle(surface, body_color, (size//2, size//2), size//3)
        
        # Void patterns
        void_color = (25, 0, 25)
        for i in range(6):
            angle = i * (math.pi / 3) + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, void_color, (x, y), size//8)
        
        # Eyes
        eye_color = (255, 255, 255)
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//4
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//4,
                                   eye_color, (0, 0, 0))
        
        # Void particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 0, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_nightmare(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a nightmare monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        
        # Body
        body_color = (100, 0, 100)  # Dark purple
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Nightmare patterns
        pattern_color = (50, 0, 50)  # Darker purple
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 255)  # Magenta
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Nightmare particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dream_eater(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a dream eater monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 100, 255), size)
        
        # Body
        body_color = (100, 100, 255)  # Light blue
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Dream patterns
        pattern_color = (50, 50, 255)  # Darker blue
        for i in range(6):
            angle = i * math.pi/3 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Dream particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 255, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_time_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a time wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 100, 0), size)
        
        # Body
        body_color = (100, 100, 0)  # Yellow-green
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Time patterns
        pattern_color = (50, 50, 0)  # Darker yellow-green
        for i in range(12):
            angle = i * math.pi/6 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 255, 0)  # Yellow
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Time particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_space_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a space wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 100), size)
        
        # Body
        body_color = (0, 0, 100)  # Dark blue
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Space patterns
        pattern_color = (0, 0, 50)  # Darker blue
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (0, 0, 255)  # Blue
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Space particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 100, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_reality_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a reality wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        
        # Body
        body_color = (100, 0, 0)  # Dark red
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Reality patterns
        pattern_color = (50, 0, 0)  # Darker red
        for i in range(6):
            angle = i * math.pi/3 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Reality particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dimension_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a dimension wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        
        # Body
        body_color = (100, 0, 100)  # Dark purple
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Dimension patterns
        pattern_color = (50, 0, 50)  # Darker purple
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 255)  # Magenta
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Dimension particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 100, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_chaos_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a chaos wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        
        # Body
        body_color = (100, 0, 0)  # Dark red
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Chaos patterns
        pattern_color = (50, 0, 0)  # Darker red
        for i in range(6):
            angle = i * math.pi/3 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Chaos particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_order_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an order wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        
        # Body
        body_color = (0, 100, 0)  # Dark green
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Order patterns
        pattern_color = (0, 50, 0)  # Darker green
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (0, 255, 0)  # Green
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Order particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 100, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_entropy_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an entropy wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        
        # Body
        body_color = (100, 0, 0)  # Dark red
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Entropy patterns
        pattern_color = (50, 0, 0)  # Darker red
        for i in range(6):
            angle = i * math.pi/3 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Entropy particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_balance_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a balance wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        
        # Body
        body_color = (100, 100, 100)  # Gray
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Balance patterns
        pattern_color = (50, 50, 50)  # Darker gray
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Balance particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 100, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_light_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a light wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (255, 255, 0), size)
        
        # Body
        body_color = (255, 255, 0)  # Yellow
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Light patterns
        pattern_color = (200, 200, 0)  # Darker yellow
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Light particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dark_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a dark wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (0, 0, 0)  # Black
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Dark patterns
        pattern_color = (50, 50, 50)  # Gray
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Dark particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_life_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a life wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        
        # Body
        body_color = (0, 100, 0)  # Dark green
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Life patterns
        pattern_color = (0, 50, 0)  # Darker green
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (0, 255, 0)  # Green
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Life particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 100, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_death_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a death wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (0, 0, 0)  # Black
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Death patterns
        pattern_color = (50, 50, 50)  # Gray
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Death particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_void_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a void wraith monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (0, 0, 0)  # Black
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Void patterns
        pattern_color = (25, 0, 25)  # Dark purple
        for i in range(8):
            angle = i * math.pi/4 + self._time
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            pygame.draw.circle(surface, pattern_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 0, 255)  # Magenta
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Void particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_shadow_stalker(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a shadow stalker monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        
        # Body
        body_color = (20, 20, 20)  # Very dark gray
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Shadow tendrils
        tendril_color = (40, 40, 40)  # Dark gray
        for i in range(4):
            angle = i * math.pi / 2 + self._time
            start_x = size//2
            start_y = size//2
            end_x = start_x + math.cos(angle) * size//2
            end_y = start_y + math.sin(angle) * size//2
            pygame.draw.line(surface, tendril_color,
                           (start_x, start_y), (end_x, end_y), 3)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (20, 20, 20))
        
        # Shadow particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(20, 20, 20, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_dark_wizard(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a dark wizard monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        
        # Body (robe)
        robe_color = (75, 0, 130)  # Indigo
        pygame.draw.polygon(surface, robe_color, [
            (size//3, size//3),  # Top left
            (size*2//3, size//3),  # Top right
            (size*3//4, size*3//4),  # Bottom right
            (size//4, size*3//4)  # Bottom left
        ])
        
        # Hood
        hood_color = (50, 0, 80)  # Darker indigo
        pygame.draw.circle(surface, hood_color,
                         (size//2, size//3), size//6)
        
        # Staff
        staff_color = (139, 69, 19)  # Brown
        pygame.draw.line(surface, staff_color,
                        (size*3//4, size//3),
                        (size*3//4, size*3//4), 3)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//12
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (0, 0, 0))
        
        # Magic particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size*3//4, y=size//3,  # From staff tip
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(128, 0, 128, 128),  # Purple
                life=random.uniform(0.5, 1.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_kraken(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a kraken monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 100), size)
        
        # Body
        body_color = (0, 100, 100)  # Teal
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Tentacles
        tentacle_color = (0, 80, 80)  # Darker teal
        for i in range(8):
            angle = i * math.pi / 4 + math.sin(self._time * 2) * 0.2
            start_x = size//2
            start_y = size//2
            end_x = start_x + math.cos(angle) * size//2
            end_y = start_y + math.sin(angle) * size//2
            
            # Draw curved tentacle
            points = []
            for t in range(5):
                t = t / 4
                x = start_x + (end_x - start_x) * t
                y = start_y + (end_y - start_y) * t
                offset = math.sin(t * math.pi + self._time * 3) * size//8
                x += math.cos(angle + math.pi/2) * offset
                y += math.sin(angle + math.pi/2) * offset
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(surface, tentacle_color, False, points, 3)
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Water particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=random.randint(0, size),
                y=random.randint(0, size),
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(0, 150, 255, 64),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_mermaid(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a mermaid monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 100, 100), size)
        
        # Tail
        tail_color = (0, 150, 150)  # Teal
        points = []
        for i in range(8):
            angle = i * math.pi / 4 + math.sin(self._time * 2) * 0.2
            x = size//2 + math.cos(angle) * size//3
            y = size*2//3 + math.sin(angle) * size//4
            points.append((x, y))
        pygame.draw.polygon(surface, tail_color, points)
        
        # Upper body
        body_color = (200, 150, 150)  # Flesh tone
        pygame.draw.circle(surface, body_color,
                         (size//2, size//3), size//4)
        
        # Hair
        hair_color = (218, 165, 32)  # Golden
        for i in range(6):
            angle = i * math.pi / 3 + math.sin(self._time) * 0.1
            start_x = size//2
            start_y = size//3
            end_x = start_x + math.cos(angle) * size//3
            end_y = start_y + math.sin(angle) * size//3
            pygame.draw.line(surface, hair_color,
                           (start_x, start_y), (end_x, end_y), 3)
        
        # Eyes
        eye_color = (0, 150, 150)  # Teal
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (0, 0, 0))
        
        # Water particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=random.randint(size//4, size*3//4),
                y=random.randint(size//2, size*3//4),
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-1, 0),
                color=(0, 150, 255, 64),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_leviathan(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a leviathan monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 0, 100), size)
        
        # Body segments
        body_color = (0, 50, 100)  # Dark blue
        segments = 5
        for i in range(segments):
            offset = math.sin(self._time * 2 + i) * size//8
            x = size//2 + offset
            y = size//4 + (i * size//segments)
            pygame.draw.circle(surface, body_color,
                             (int(x), int(y)), size//4)
        
        # Head
        head_color = (0, 75, 150)  # Slightly lighter blue
        head_x = size//2 + math.sin(self._time * 2) * size//8
        pygame.draw.circle(surface, head_color,
                         (int(head_x), size//4), size//3)
        
        # Fins
        fin_color = (0, 100, 200)  # Light blue
        for i in range(2):
            angle = math.pi/4 + i * math.pi/2 + math.sin(self._time)
            fin_x = head_x + math.cos(angle) * size//3
            fin_y = size//4 + math.sin(angle) * size//3
            pygame.draw.polygon(surface, fin_color,
                              [(head_x, size//4),
                               (fin_x, fin_y),
                               (head_x + (fin_x - head_x)//2,
                                size//4 + (fin_y - size//4)//2)])
        
        # Eyes
        eye_color = (255, 255, 255)  # White
        for i in range(2):
            x = head_x + (i * 2 - 1) * size//6
            y = size//4
            self._draw_animated_eyes(surface, x, y, size//5,
                                   eye_color, (0, 0, 100))
        
        # Water particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=random.randint(0, size),
                y=random.randint(0, size),
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 100, 255, 64),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(3, 6)
            ))
        
        self._draw_particles(surface)

    def _render_siren(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a siren monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        
        # Body
        body_color = (200, 100, 200)  # Purple
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Wings
        wing_color = (150, 75, 150)  # Darker purple
        for i in range(2):
            angle = math.pi/6 + i * math.pi*2/3 + math.sin(self._time) * 0.2
            wing_x = size//2 + math.cos(angle) * size//2
            wing_y = size//2 + math.sin(angle) * size//2
            pygame.draw.polygon(surface, wing_color,
                              [(size//2, size//2),
                               (wing_x, wing_y),
                               (size//2 + (wing_x - size//2)//2,
                                size//2 + (wing_y - size//2)//2)])
        
        # Hair
        hair_color = (100, 50, 100)  # Even darker purple
        for i in range(6):
            angle = i * math.pi/3 + math.sin(self._time * 1.5) * 0.1
            start_x = size//2
            start_y = size//2
            end_x = start_x + math.cos(angle) * size//3
            end_y = start_y + math.sin(angle) * size//3
            pygame.draw.line(surface, hair_color,
                           (start_x, start_y), (end_x, end_y), 3)
        
        # Eyes
        eye_color = (255, 0, 255)  # Bright purple
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (100, 0, 100))
        
        # Magic particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 100, 255, 128),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_mantis(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a mantis monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        
        # Body
        body_color = (0, 150, 0)  # Green
        pygame.draw.ellipse(surface, body_color,
                          (size//3, size//3, size//3, size//2))
        
        # Head
        head_color = (0, 130, 0)  # Slightly darker green
        pygame.draw.circle(surface, head_color,
                         (size//2, size//3), size//6)
        
        # Scythes
        scythe_color = (0, 100, 0)  # Even darker green
        for i in range(2):
            angle = math.pi/4 + i * math.pi/2 + math.sin(self._time * 2) * 0.3
            scythe_x = size//2 + math.cos(angle) * size//2
            scythe_y = size//2 + math.sin(angle) * size//2
            pygame.draw.line(surface, scythe_color,
                           (size//2, size//2),
                           (scythe_x, scythe_y), 4)
            pygame.draw.line(surface, scythe_color,
                           (scythe_x, scythe_y),
                           (scythe_x + size//8, scythe_y - size//8), 4)
        
        # Eyes
        eye_color = (255, 255, 0)  # Yellow
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (0, 100, 0))
        
        # Particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(0, 255, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_beetle(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a beetle monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 25, 0), size)
        
        # Body
        body_color = (139, 69, 19)  # Brown
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Shell
        shell_color = (101, 67, 33)  # Darker brown
        shell_rect = pygame.Rect(size//3, size//3, size//3, size//2)
        pygame.draw.ellipse(surface, shell_color, shell_rect)
        
        # Shell pattern
        pattern_color = (82, 54, 27)  # Even darker brown
        for i in range(3):
            y = size//3 + (i * size//6)
            pygame.draw.line(surface, pattern_color,
                           (size//3, y), (size*2//3, y), 2)
        
        # Legs
        leg_color = (139, 69, 19)  # Brown
        for i in range(6):
            angle = i * math.pi/3 + math.sin(self._time * 2 + i) * 0.2
            start_x = size//2
            start_y = size//2
            end_x = start_x + math.cos(angle) * size//3
            end_y = start_y + math.sin(angle) * size//3
            pygame.draw.line(surface, leg_color,
                           (start_x, start_y), (end_x, end_y), 2)
        
        # Eyes
        eye_color = (0, 0, 0)  # Black
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (139, 69, 19))
        
        # Shell shine particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=random.randint(size//3, size*2//3),
                y=random.randint(size//3, size*5//6),
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(255, 255, 255, 32),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_scorpion(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a scorpion monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 25, 0), size)
        
        # Body
        body_color = (139, 69, 19)  # Brown
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//4)
        
        # Tail segments
        tail_color = (101, 67, 33)  # Darker brown
        segments = 5
        tail_points = []
        for i in range(segments):
            angle = math.pi/4 + math.sin(self._time * 2) * 0.3
            x = size//2 + math.cos(angle) * (i * size//8)
            y = size//2 - math.sin(angle) * (i * size//8)
            tail_points.append((x, y))
            pygame.draw.circle(surface, tail_color,
                            (int(x), int(y)), size//12)
        
        # Stinger
        stinger_color = (82, 54, 27)  # Even darker brown
        if len(tail_points) > 0:
            last_point = tail_points[-1]
            stinger_x = last_point[0] + math.cos(math.pi/4) * size//8
            stinger_y = last_point[1] - math.sin(math.pi/4) * size//8
            pygame.draw.line(surface, stinger_color,
                           last_point, (stinger_x, stinger_y), 3)
        
        # Claws
        claw_color = (139, 69, 19)  # Brown
        for i in range(2):
            angle = math.pi/6 + i * math.pi*5/6 + math.sin(self._time) * 0.2
            claw_x = size//2 + math.cos(angle) * size//2
            claw_y = size//2 + math.sin(angle) * size//2
            pygame.draw.line(surface, claw_color,
                           (size//2, size//2),
                           (claw_x, claw_y), 3)
            # Pincers
            pincer_angle = angle + (i * 2 - 1) * math.pi/6
            pincer_x = claw_x + math.cos(pincer_angle) * size//8
            pincer_y = claw_y + math.sin(pincer_angle) * size//8
            pygame.draw.line(surface, claw_color,
                           (claw_x, claw_y),
                           (pincer_x, pincer_y), 3)
        
        # Eyes
        eye_color = (0, 0, 0)  # Black
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (139, 69, 19))
        
        # Sand particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=random.randint(0, size),
                y=size*3//4,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-1, -0.5),
                color=(210, 180, 140, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_wasp(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a wasp monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 100, 0), size)
        
        # Body segments
        body_color = (255, 200, 0)  # Yellow
        stripe_color = (0, 0, 0)  # Black
        segments = 3
        for i in range(segments):
            x = size//2
            y = size//3 + (i * size//4)
            pygame.draw.circle(surface, body_color,
                            (x, y), size//5)
            # Stripes
            stripe_y = y - size//10
            pygame.draw.line(surface, stripe_color,
                           (x - size//5, stripe_y),
                           (x + size//5, stripe_y), 2)
        
        # Wings
        wing_color = (200, 200, 200, 128)  # Translucent gray
        for i in range(2):
            angle = math.pi/6 + i * math.pi*2/3 + math.sin(self._time * 10) * 0.2
            wing_x = size//2 + math.cos(angle) * size//2
            wing_y = size//2 + math.sin(angle) * size//2
            pygame.draw.ellipse(surface, wing_color,
                              (size//4 + i * size//2, size//4,
                               size//4, size//2))
        
        # Stinger
        stinger_color = (0, 0, 0)  # Black
        stinger_start = (size//2, size*3//4)
        stinger_end = (size//2, size*7//8)
        pygame.draw.line(surface, stinger_color,
                        stinger_start, stinger_end, 2)
        
        # Eyes
        eye_color = (255, 0, 0)  # Red
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (0, 0, 0))
        
        # Particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-0.5, 0.5),
                color=(255, 255, 0, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_clockwork_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a clockwork golem monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        
        # Body
        body_color = (205, 127, 50)  # Bronze
        pygame.draw.circle(surface, body_color,
                         (size//2, size//2), size//3)
        
        # Gears
        gear_color = (218, 165, 32)  # Golden
        for i in range(4):
            angle = i * math.pi/2 + self._time * (i % 2 * 2 - 1)
            x = size//2 + math.cos(angle) * size//4
            y = size//2 + math.sin(angle) * size//4
            # Gear teeth
            for j in range(8):
                tooth_angle = j * math.pi/4 + angle
                inner_x = x + math.cos(tooth_angle) * size//12
                inner_y = y + math.sin(tooth_angle) * size//12
                outer_x = x + math.cos(tooth_angle) * size//8
                outer_y = y + math.sin(tooth_angle) * size//8
                pygame.draw.line(surface, gear_color,
                               (inner_x, inner_y),
                               (outer_x, outer_y), 2)
            pygame.draw.circle(surface, gear_color,
                            (int(x), int(y)), size//12)
        
        # Eyes
        eye_color = (255, 215, 0)  # Gold
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//6
            y = size//2
            self._draw_animated_eyes(surface, x, y, size//6,
                                   eye_color, (139, 69, 19))
        
        # Steam particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//3,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-2, -1),
                color=(200, 200, 200, 64),
                life=random.uniform(1.0, 2.0),
                size=random.uniform(2, 4)
            ))
        
        self._draw_particles(surface)

    def _render_automaton(self, surface: pygame.Surface, size: int, anim: dict):
        """Render an automaton monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        
        # Body
        body_color = (192, 192, 192)  # Silver
        pygame.draw.rect(surface, body_color,
                        (size//3, size//3, size//3, size//2))
        
        # Head
        head_color = (169, 169, 169)  # Dark gray
        pygame.draw.rect(surface, head_color,
                        (size*3//8, size//4, size//4, size//4))
        
        # Joints
        joint_color = (128, 128, 128)  # Gray
        joint_positions = [
            (size//3, size//2),
            (size*2//3, size//2),
            (size//3, size*3//4),
            (size*2//3, size*3//4)
        ]
        for x, y in joint_positions:
            pygame.draw.circle(surface, joint_color,
                            (x, y), size//16)
        
        # Eyes
        eye_color = (0, 255, 255)  # Cyan
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size//3
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (0, 0, 0))
        
        # Energy particles
        if random.random() < 0.15:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 255, 255, 64),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_steam_knight(self, surface: pygame.Surface, size: int, anim: dict):
        """Render a steam knight monster."""
        # Shadow
        self._draw_shadow(surface, "circle", (50, 25, 0), size)
        
        # Body (armor)
        armor_color = (139, 69, 19)  # Brown
        pygame.draw.rect(surface, armor_color,
                        (size//3, size//3, size//3, size//2))
        
        # Helmet
        helmet_color = (101, 67, 33)  # Darker brown
        helmet_points = [
            (size*3//8, size//3),  # Top left
            (size*5//8, size//3),  # Top right
            (size*2//3, size//2),  # Bottom right
            (size//3, size//2)     # Bottom left
        ]
        pygame.draw.polygon(surface, helmet_color, helmet_points)
        
        # Steam pipes
        pipe_color = (82, 54, 27)  # Even darker brown
        pipe_positions = [
            (size//3, size//2),
            (size*2//3, size//2)
        ]
        for x, y in pipe_positions:
            pygame.draw.rect(surface, pipe_color,
                           (x - size//16, y, size//8, size//4))
        
        # Eyes (visor)
        eye_color = (255, 69, 0)  # Red-orange
        for i in range(2):
            x = size//2 + (i * 2 - 1) * size//8
            y = size*2//5
            self._draw_animated_eyes(surface, x, y, size//8,
                                   eye_color, (0, 0, 0))
        
        # Steam particles
        for x, y in pipe_positions:
            if random.random() < 0.2:
                self._particles.append(Particle(
                    x=x, y=y + size//4,
                    dx=random.uniform(-0.5, 0.5),
                    dy=random.uniform(-2, -1),
                    color=(200, 200, 200, 64),
                    life=random.uniform(1.0, 2.0),
                    size=random.uniform(2, 4)
                ))
        
        self._draw_particles(surface)