"""
DEPRECATED - DO NOT USE
=====================

This file is deprecated and should not be used.
The current monster implementation is in monster.py.

If you're looking to:
1. Add new monster types -> Use monster.py
2. Modify monster behavior -> Use monster.py
3. Change monster stats -> Use monster.py
4. Add monster animations -> Use rpg_modules/animations/base.py

This file is kept only for reference and will be removed in a future update.
"""

import warnings

warnings.warn(
    "monster_2.py is deprecated. Use monster.py instead.",
    DeprecationWarning,
    stacklevel=2
)

import pygame
import math
import random
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum
from ..utils.logging import logger

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
    def __init__(self, monster_type: str):
        super().__init__()
        self.monster_type = monster_type
        self._time = 0
        self._particles = []

    def render(self, surface: pygame.Surface, size: int):
        """Render a monster icon with animations based on its type."""
        anim = self._get_animation_values()
        
        # Get the render method based on monster type
        method_name = f'_render_{self.monster_type}'
        logger.log(f"[RENDER DEBUG] Attempting to render monster type: {self.monster_type}")
        logger.log(f"[RENDER DEBUG] Looking for method: {method_name}")
        
        # List all available render methods
        render_methods = [m for m in dir(self) if m.startswith('_render_')]
        logger.log(f"[RENDER DEBUG] Available render methods: {render_methods}")
        
        render_method = getattr(self, method_name, None)
        if render_method:
            logger.log(f"[RENDER DEBUG] Successfully found render method for {self.monster_type}")
            try:
                render_method(surface, size, anim)
                logger.log(f"[RENDER DEBUG] Successfully rendered {self.monster_type}")
            except Exception as e:
                logger.log(f"[RENDER DEBUG] Error during rendering: {str(e)}")
                self._render_default(surface, size, anim)
        else:
            logger.log(f"[RENDER DEBUG] No render method found for {self.monster_type}, using default")
            self._render_default(surface, size, anim)

    def _render_default(self, surface: pygame.Surface, size: int, anim: dict):
        """Default rendering for unknown monster types."""
        # Draw a simple circle with eyes as fallback
        pygame.draw.circle(surface, (200, 0, 0), (size//2, size//2), size//3)
        self._draw_animated_eyes(surface, size//2 - size//8, size//2, size, (255, 255, 255))
        self._draw_animated_eyes(surface, size//2 + size//8, size//2, size, (255, 255, 255))

    def _render_dragon(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dragon with fire breath and animated wings."""
        # Body
        self._draw_shadow(surface, "circle", (255, 0, 0), size)
        pygame.draw.circle(surface, (255, 0, 0), (size//2, size//2), size//3)
        
        # Wings
        wing_color = (200, 0, 0)
        wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 - int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        surface.blit(wing_surface, (0, 0))
        
        # Tail
        tail_points = [(size//2, size//2)]
        for i in range(3):
            angle = math.radians(180 + math.sin(self._time * 2 + i) * 20)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            tail_points.append((x, y))
        pygame.draw.lines(surface, (255, 0, 0), False, tail_points, 3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        
        # Fire breath particles
        if random.random() < 0.2:
            for _ in range(3):
                angle = math.radians(random.uniform(-30, 30))
                speed = random.uniform(1, 3)
                self._particles.append(Particle(
                    x=size//2, y=size*2//3,
                    dx=math.cos(angle) * speed,
                    dy=math.sin(angle) * speed,
                    color=(255, random.randint(100, 255), 0),
                    life=random.uniform(0.3, 0.8),
                    size=random.uniform(1, 3)
                ))
        
        self._draw_particles(surface)

    def _render_phoenix(self, surface: pygame.Surface, size: int, anim: dict):
        """Render phoenix with flame effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 100, 0), size)
        pygame.draw.circle(surface, (255, 100, 0), (size//2, size//2), size//3)
        
        # Wings
        wing_color = (255, 200, 0)
        wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 - int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        surface.blit(wing_surface, (0, 0))
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        
        # Flame particles
        if random.random() < 0.3:
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 3)
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=math.cos(angle) * speed,
                    dy=math.sin(angle) * speed,
                    color=(255, random.randint(100, 255), 0),
                    life=random.uniform(0.3, 0.8),
                    size=random.uniform(1, 3)
                ))
        
        self._draw_particles(surface)

    def _render_unicorn(self, surface: pygame.Surface, size: int, anim: dict):
        """Render unicorn with magical effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 255, 255), size)
        pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), size//3)
        
        # Horn
        horn_color = (255, 200, 255)
        base_y = size//3
        base_width = 20
        point_y = size//6
        points = [
            (size//2 - base_width//2, base_y),
            (size//2 + base_width//2, base_y),
            (size//2, point_y)
        ]
        pygame.draw.polygon(surface, horn_color, points)
        
        # Horn glow
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        glow_color = (*horn_color, 128)
        glow_points = [
            (size//2 - base_width//2 - 2, base_y - 2),
            (size//2 + base_width//2 + 2, base_y - 2),
            (size//2, point_y - 2)
        ]
        pygame.draw.polygon(glow_surface, glow_color, glow_points)
        surface.blit(glow_surface, (0, 0))
        
        # Mane
        mane_color = (255, 200, 255)
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.line(surface, mane_color,
                           (size//2, size//2), (x, y), 2)
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (255, 200, 255))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (255, 200, 255))
        
        # Magical particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
            # Horn sparkles
            self._particles.append(Particle(
                x=size//2, y=point_y,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(255, 255, 255),
                life=random.uniform(0.3, 0.6),
                size=random.uniform(1, 1.5)
            ))
        
        self._draw_particles(surface)

    def _render_nightmare(self, surface: pygame.Surface, size: int, anim: dict):
        """Render nightmare with dark horse form and fire mane."""
        # Body
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        pygame.draw.circle(surface, (0, 0, 0), (size//2, size//2), size//3)
        
        # Head
        head_color = (50, 50, 50)
        pygame.draw.ellipse(surface, head_color,
                          (size//2 - size//4, size//3 - size//8,
                           size//2, size//4))
        
        # Ears
        ear_color = (50, 50, 50)
        # Left ear
        points = [(size//2 - size//8, size//3),
                 (size//2 - size//4, size//4),
                 (size//2 - size//6, size//3)]
        pygame.draw.polygon(surface, ear_color, points)
        # Right ear
        points = [(size//2 + size//8, size//3),
                 (size//2 + size//4, size//4),
                 (size//2 + size//6, size//3)]
        pygame.draw.polygon(surface, ear_color, points)
        
        # Glowing red eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        
        # Fire mane particles
        if random.random() < 0.3:
            for _ in range(3):
                angle = random.uniform(0, math.pi)
                speed = random.uniform(1, 3)
                self._particles.append(Particle(
                    x=size//2, y=size//3,
                    dx=math.cos(angle) * speed,
                    dy=math.sin(angle) * speed,
                    color=(255, random.randint(100, 255), 0),
                    life=random.uniform(0.3, 0.8),
                    size=random.uniform(1, 3)
                ))
        
        self._draw_particles(surface)

    def _render_frost_titan(self, surface: pygame.Surface, size: int, anim: dict):
        """Render frost titan with ice effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 220, 255), size)
        pygame.draw.circle(surface, (200, 220, 255), (size//2, size//2), size//3)
        
        # Ice formations
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            ice_x = size//2 + int(size//3 * math.cos(angle))
            ice_y = size//2 + int(size//3 * math.sin(angle))
            # Draw ice crystal
            points = []
            for j in range(6):
                crystal_angle = math.radians(j * 60)
                points.append((
                    ice_x + int(size//8 * math.cos(crystal_angle)),
                    ice_y + int(size//8 * math.sin(crystal_angle))
                ))
            pygame.draw.polygon(surface, (220, 240, 255), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (200, 220, 255))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (200, 220, 255))
        
        # Ice particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 240, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def update(self, dt: float):
        """Update animation state."""
        self._time += dt
        
        # Update particles
        for particle in self._particles[:]:
            particle.update(dt)
            if particle.is_dead():
                self._particles.remove(particle) 