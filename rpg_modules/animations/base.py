import pygame
import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Optional

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

    def _draw_particles(self, surface: pygame.Surface):
        """Draw all active particles."""
        for particle in self._particles:
            alpha = int(255 * (particle.life / 1.0))
            pygame.draw.circle(surface, (*particle.color, alpha),
                             (int(particle.x), int(particle.y)), 
                             particle.size)

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
    def __init__(self, monster_type: str):
        super().__init__()
        self.monster_type = monster_type.lower()
        self._time = 0
        self._particles = []

    def draw(self, surface: pygame.Surface, position: Tuple[int, int], size: int):
        """
        Draw the monster icon at the specified position.
        
        Args:
            surface: The pygame surface to draw on
            position: (x, y) position to draw at
            size: Size of the icon in pixels
        """
        # Create a surface for the monster icon
        icon_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        self.render(icon_surface, size)
        
        # Draw at position
        surface.blit(icon_surface, position)

    def render(self, surface: pygame.Surface, size: int):
        """Render a monster icon with animations based on its type."""
        anim = self._get_animation_values()
        
        # Get base color for the monster
        color = self._get_monster_color()
        
        # Draw base shape
        self._draw_shadow(surface, "circle", color, size)
        
        # Draw main body
        if "elemental" in self.monster_type:
            self._render_elemental(surface, size, color, anim)
        elif "spirit" in self.monster_type:
            self._render_spirit(surface, size, color, anim)
        elif "crystal" in self.monster_type or "gem" in self.monster_type:
            self._render_crystal(surface, size, color, anim)
        elif "undead" in self.monster_type or "wraith" in self.monster_type:
            self._render_undead(surface, size, color, anim)
        else:
            self._render_default(surface, size, color, anim)
        
        # Add particles
        self._update_particles()
        self._draw_particles(surface)

    def _render_elemental(self, surface, size, color, anim):
        """Render elemental-type monsters."""
        # Pulsing core
        core_size = int(size//3 * (0.8 + 0.2 * anim['pulse']))
        pygame.draw.circle(surface, color, (size//2, size//2), core_size)
        
        # Orbiting particles
        for i in range(8):
            angle = math.radians(i * 45 + self._time * 90)
            orbit_x = size//2 + int(math.cos(angle) * size//3)
            orbit_y = size//2 + int(math.sin(angle) * size//3)
            pygame.draw.circle(surface, color, (orbit_x, orbit_y), size//8)

    def _render_spirit(self, surface, size, color, anim):
        """Render spirit-type monsters."""
        # Ethereal body
        alpha = int(128 + 64 * anim['pulse'])
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Wavy bottom
        points = [(size//4, size*2//3)]
        for i in range(5):
            x = size//4 + (i * size//4)
            y = size*2//3 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        points.append((size*3//4, size*2//3))
        
        pygame.draw.polygon(ghost_surface, (*color, alpha), points)
        surface.blit(ghost_surface, (0, 0))

    def _render_crystal(self, surface, size, color, anim):
        """Render crystal-type monsters."""
        # Crystal facets
        points = []
        center = (size//2, size//2)
        for i in range(6):
            angle = math.radians(i * 60 + self._time * 45)  # Rotating effect
            radius = size//3 * (0.8 + 0.2 * anim['pulse'])  # Pulsing effect
            x = center[0] + int(math.cos(angle) * radius)
            y = center[1] + int(math.sin(angle) * radius)
            points.append((x, y))
        
        # Draw with slight transparency for crystal effect
        crystal_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(crystal_surface, (*color, 180), points)
        surface.blit(crystal_surface, (0, 0))

    def _render_undead(self, surface, size, color, anim):
        """Render undead-type monsters."""
        # Semi-transparent body
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surface, (*color, 180), (size//2, size//2), size//3)
        
        # Glowing eyes
        eye_color = (255, 0, 0, int(200 + 55 * anim['pulse']))
        eye_size = size//8
        pygame.draw.circle(ghost_surface, eye_color, (size//3, size//2), eye_size)
        pygame.draw.circle(ghost_surface, eye_color, (size*2//3, size//2), eye_size)
        
        surface.blit(ghost_surface, (0, 0))

    def _render_default(self, surface, size, color, anim):
        """Default rendering for other monster types."""
        # Basic body
        pygame.draw.circle(surface, color, (size//2, size//2), size//3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0), anim['eye_blink'])
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0), anim['eye_blink'])

    def _get_monster_color(self):
        """Get base color for monster based on its type."""
        # This will use the same color mapping as MonsterAnimation
        from . import MonsterAnimation
        dummy_animation = MonsterAnimation(self.monster_type)
        return dummy_animation._get_fallback_color()

    def _update_particles(self):
        """Update particle effects."""
        # Add new particles based on monster type
        if random.random() < 0.2:
            if "elemental" in self.monster_type:
                self._add_elemental_particles()
            elif "spirit" in self.monster_type:
                self._add_spirit_particles()
            elif "crystal" in self.monster_type:
                self._add_crystal_particles()
        
        # Update existing particles
        super().update(0.016)  # Approximately 60 FPS

    def _add_elemental_particles(self):
        """Add elemental-specific particles."""
        color = self._get_monster_color()
        center = self.size//2
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            self._particles.append(Particle(
                x=center, y=center,
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed,
                color=color,
                life=random.uniform(0.3, 0.8),
                size=random.uniform(self.size/32, self.size/10)
            ))

    def _add_spirit_particles(self):
        """Add spirit-specific particles."""
        color = self._get_monster_color()
        self._particles.append(Particle(
            x=random.uniform(self.size/4, self.size*3/4),
            y=random.uniform(self.size/4, self.size*3/4),
            dx=0, dy=-0.5,
            color=color,
            life=random.uniform(0.5, 1.0),
            size=random.uniform(self.size/32, self.size/16)
        ))

    def _add_crystal_particles(self):
        """Add crystal-specific particles."""
        color = self._get_monster_color()
        angle = random.uniform(0, math.pi * 2)
        center = self.size//2
        radius = self.size//4
        self._particles.append(Particle(
            x=center + math.cos(angle) * radius,
            y=center + math.sin(angle) * radius,
            dx=math.cos(angle) * 0.5,
            dy=math.sin(angle) * 0.5,
            color=color,
            life=random.uniform(0.3, 0.6),
            size=random.uniform(self.size/32, self.size/16)
        )) 