import pygame
import math
import random
import sys
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

    def render(self, surface: pygame.Surface, size: int):
        """Render a monster icon with animations based on its type."""
        anim = self._get_animation_values()
        
        if self.monster_type == "dragon":
            self._render_dragon(surface, size, anim)
        elif self.monster_type == "spider":
            self._render_spider(surface, size, anim)
        elif self.monster_type == "ghost":
            self._render_ghost(surface, size, anim)
        elif self.monster_type == "skeleton":
            self._render_skeleton(surface, size, anim)
        elif self.monster_type == "slime":
            self._render_slime(surface, size, anim)
        elif self.monster_type == "thought_devourer":
            self._render_thought_devourer(surface, size, anim)
        elif self.monster_type == "memory_phantom":
            self._render_memory_phantom(surface, size, anim)
        elif self.monster_type == "psychic_hydra":
            self._render_psychic_hydra(surface, size, anim)
        elif self.monster_type == "mind_colossus":
            self._render_mind_colossus(surface, size, anim)
        elif self.monster_type == "fire_elemental":
            self._render_fire_elemental(surface, size, anim)
        elif self.monster_type == "ice_elemental":
            self._render_ice_elemental(surface, size, anim)
        elif self.monster_type == "storm_elemental":
            self._render_storm_elemental(surface, size, anim)
        elif self.monster_type == "earth_golem":
            self._render_earth_golem(surface, size, anim)
        elif self.monster_type == "zombie":
            self._render_zombie(surface, size, anim)
        elif self.monster_type == "wraith":
            self._render_wraith(surface, size, anim)
        elif self.monster_type == "vampire":
            self._render_vampire(surface, size, anim)
        elif self.monster_type == "lich":
            self._render_lich(surface, size, anim)
        elif self.monster_type == "pixie":
            self._render_pixie(surface, size, anim)
        elif self.monster_type == "phoenix":
            self._render_phoenix(surface, size, anim)
        elif self.monster_type == "unicorn":
            self._render_unicorn(surface, size, anim)
        elif self.monster_type == "griffin":
            self._render_griffin(surface, size, anim)
        elif self.monster_type == "treant":
            self._render_treant(surface, size, anim)
        elif self.monster_type == "wolf":
            self._render_wolf(surface, size, anim)
        elif self.monster_type == "bear":
            self._render_bear(surface, size, anim)
        elif self.monster_type == "dryad":
            self._render_dryad(surface, size, anim)
        elif self.monster_type == "demon":
            self._render_demon(surface, size, anim)
        elif self.monster_type == "shadow_stalker":
            self._render_shadow_stalker(surface, size, anim)
        elif self.monster_type == "nightmare":
            self._render_nightmare(surface, size, anim)
        elif self.monster_type == "dark_wizard":
            self._render_dark_wizard(surface, size, anim)
        elif self.monster_type == "kraken":
            self._render_kraken(surface, size, anim)
        elif self.monster_type == "mermaid":
            self._render_mermaid(surface, size, anim)
        elif self.monster_type == "leviathan":
            self._render_leviathan(surface, size, anim)
        elif self.monster_type == "siren":
            self._render_siren(surface, size, anim)
        elif self.monster_type == "mantis":
            self._render_mantis(surface, size, anim)
        elif self.monster_type == "beetle":
            self._render_beetle(surface, size, anim)
        elif self.monster_type == "scorpion":
            self._render_scorpion(surface, size, anim)
        elif self.monster_type == "wasp":
            self._render_wasp(surface, size, anim)
        elif self.monster_type == "clockwork_golem":
            self._render_clockwork_golem(surface, size, anim)
        elif self.monster_type == "automaton":
            self._render_automaton(surface, size, anim)
        elif self.monster_type == "steam_knight":
            self._render_steam_knight(surface, size, anim)
        elif self.monster_type == "tesla_guardian":
            self._render_tesla_guardian(surface, size, anim)
        elif self.monster_type == "crystal_golem":
            self._render_crystal_golem(surface, size, anim)
        elif self.monster_type == "prism_elemental":
            self._render_prism_elemental(surface, size, anim)
        elif self.monster_type == "geode_guardian":
            self._render_geode_guardian(surface, size, anim)
        elif self.monster_type == "diamond_sentinel":
            self._render_diamond_sentinel(surface, size, anim)
        elif self.monster_type == "myconid":
            self._render_myconid(surface, size, anim)
        elif self.monster_type == "spore_beast":
            self._render_spore_beast(surface, size, anim)
        elif self.monster_type == "mold_horror":
            self._render_mold_horror(surface, size, anim)
        elif self.monster_type == "fungal_colossus":
            self._render_fungal_colossus(surface, size, anim)
        elif self.monster_type == "void_walker":
            self._render_void_walker(surface, size, anim)
        elif self.monster_type == "shade":
            self._render_shade(surface, size, anim)
        elif self.monster_type == "dark_phantom":
            self._render_dark_phantom(surface, size, anim)
        elif self.monster_type == "umbra_beast":
            self._render_umbra_beast(surface, size, anim)
        elif self.monster_type == "star_seraph":
            self._render_star_seraph(surface, size, anim)
        elif self.monster_type == "moon_guardian":
            self._render_moon_guardian(surface, size, anim)
        elif self.monster_type == "solar_phoenix":
            self._render_solar_phoenix(surface, size, anim)
        elif self.monster_type == "cosmic_watcher":
            self._render_cosmic_watcher(surface, size, anim)
        elif self.monster_type == "chronomancer":
            self._render_chronomancer(surface, size, anim)
        elif self.monster_type == "temporal_wraith":
            self._render_temporal_wraith(surface, size, anim)
        elif self.monster_type == "hourglass_golem":
            self._render_hourglass_golem(surface, size, anim)
        elif self.monster_type == "future_seer":
            self._render_future_seer(surface, size, anim)
        elif self.monster_type == "forest_nymph":
            self._render_forest_nymph(surface, size, anim)
        elif self.monster_type == "river_spirit":
            self._render_river_spirit(surface, size, anim)
        elif self.monster_type == "mountain_guardian":
            self._render_mountain_guardian(surface, size, anim)
        elif self.monster_type == "wind_dancer":
            self._render_wind_dancer(surface, size, anim)
        elif self.monster_type == "rune_golem":
            self._render_rune_golem(surface, size, anim)
        elif self.monster_type == "arcane_sentinel":
            self._render_arcane_sentinel(surface, size, anim)
        elif self.monster_type == "spell_weaver":
            self._render_spell_weaver(surface, size, anim)
        elif self.monster_type == "mana_elemental":
            self._render_mana_elemental(surface, size, anim)
        elif self.monster_type == "sand_wurm":
            self._render_sand_wurm(surface, size, anim)
        elif self.monster_type == "mummy_lord":
            self._render_mummy_lord(surface, size, anim)
        elif self.monster_type == "dust_djinn":
            self._render_dust_djinn(surface, size, anim)
        elif self.monster_type == "scarab_swarm":
            self._render_scarab_swarm(surface, size, anim)
        elif self.monster_type == "rock_giant":
            self._render_rock_giant(surface, size, anim)
        elif self.monster_type == "harpy":
            self._render_harpy(surface, size, anim)
        elif self.monster_type == "frost_titan":
            self._render_frost_titan(surface, size, anim)
        elif self.monster_type == "thunder_bird":
            self._render_thunder_bird(surface, size, anim)
        elif self.monster_type == "bog_witch":
            self._render_bog_witch(surface, size, anim)
        elif self.monster_type == "hydra":
            self._render_hydra(surface, size, anim)
        elif self.monster_type == "mushroom_zombie":
            self._render_mushroom_zombie(surface, size, anim)
        elif self.monster_type == "will_o_wisp":
            self._render_will_o_wisp(surface, size, anim)
        elif self.monster_type == "nightmare_weaver":
            self._render_nightmare_weaver(surface, size, anim)
        elif self.monster_type == "dream_eater":
            self._render_dream_eater(surface, size, anim)
        elif self.monster_type == "sleep_walker":
            self._render_sleep_walker(surface, size, anim)
        elif self.monster_type == "morpheus_spawn":
            self._render_morpheus_spawn(surface, size, anim)
        elif self.monster_type == "ancient_titan":
            self._render_ancient_titan(surface, size, anim)
        elif self.monster_type == "primordial_wyrm":
            self._render_primordial_wyrm(surface, size, anim)
        elif self.monster_type == "genesis_spirit":
            self._render_genesis_spirit(surface, size, anim)
        elif self.monster_type == "eternal_flame":
            self._render_eternal_flame(surface, size, anim)
        elif self.monster_type == "schrodinger_beast":
            self._render_schrodinger_beast(surface, size, anim)
        elif self.monster_type == "quantum_shifter":
            self._render_quantum_shifter(surface, size, anim)
        elif self.monster_type == "probability_weaver":
            self._render_probability_weaver(surface, size, anim)
        elif self.monster_type == "entangled_horror":
            self._render_entangled_horror(surface, size, anim)
        elif self.monster_type == "chimera_lord":
            self._render_chimera_lord(surface, size, anim)
        elif self.monster_type == "world_serpent":
            self._render_world_serpent(surface, size, anim)
        elif self.monster_type == "golden_guardian":
            self._render_golden_guardian(surface, size, anim)
        elif self.monster_type == "fate_sphinx":
            self._render_fate_sphinx(surface, size, anim)
        elif self.monster_type == "fire_spirit":
            self._render_fire_spirit(surface, size, anim)
        elif self.monster_type == "water_spirit":
            self._render_water_spirit(surface, size, anim)
        elif self.monster_type == "earth_spirit":
            self._render_earth_spirit(surface, size, anim)
        elif self.monster_type == "air_spirit":
            self._render_air_spirit(surface, size, anim)
        elif self.monster_type == "forest_guardian":
            self._render_forest_guardian(surface, size, anim)
        elif self.monster_type == "vine_weaver":
            self._render_vine_weaver(surface, size, anim)
        elif self.monster_type == "moss_beast":
            self._render_moss_beast(surface, size, anim)
        elif self.monster_type == "bloom_spirit":
            self._render_bloom_spirit(surface, size, anim)

    def _render_dragon(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dragon with fire breath and animated wings."""
        # Body
        self._draw_shadow(surface, "circle", (255, 0, 0), size)
        pygame.draw.circle(surface, (255, 0, 0), (size//2, size//2), size//3)
        
        # Wings
        wing_color = (200, 0, 0)
        wing_angle = math.sin(self._time * 3) * 0.3
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(4):
            angle = math.radians(-45 - i * 20) + wing_angle
            x = size//2 + int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(4):
            angle = math.radians(45 + i * 20) - wing_angle
            x = size//2 + int(size//2 * math.cos(angle))
            y = size//2 + int(size//2 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(surface, wing_color, points)
        
        # Horns
        horn_color = (150, 0, 0)
        # Left horn
        points = [(size//3, size//3), (size//4, size//4), (size//3 - size//8, size//3)]
        pygame.draw.polygon(surface, horn_color, points)
        # Right horn
        points = [(size*2//3, size//3), (size*3//4, size//4), (size*2//3 + size//8, size//3)]
        pygame.draw.polygon(surface, horn_color, points)
        
        # Tail
        tail_points = []
        for i in range(5):
            angle = math.radians(180 + i * 15 + math.sin(self._time * 2) * 20)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            tail_points.append((x, y))
        pygame.draw.lines(surface, (255, 0, 0), False, tail_points, 4)
        # Tail tip
        pygame.draw.polygon(surface, (255, 0, 0),
                          [(tail_points[-1][0], tail_points[-1][1]),
                           (tail_points[-1][0] - size//16, tail_points[-1][1] - size//16),
                           (tail_points[-1][0] + size//16, tail_points[-1][1] - size//16)])
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (255, 0, 0))
        
        # Fire breath
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

    def _render_spider(self, surface: pygame.Surface, size: int, anim: dict):
        """Render spider with moving legs and web."""
        # Body segments
        self._draw_shadow(surface, "circle", (64, 0, 64), size)
        # Rear segment (abdomen)
        pygame.draw.circle(surface, (64, 0, 64), 
                         (size//2, size//2 + size//8), size//3)
        # Front segment (cephalothorax)
        pygame.draw.circle(surface, (48, 0, 48),
                         (size//2, size//2 - size//8), size//4)
        
        # Animated legs (4 pairs)
        leg_color = (64, 0, 64)
        for i in range(8):
            # Base angle for each leg pair
            base_angle = math.radians(i * 45 + 22.5)
            # Add walking animation
            leg_angle = base_angle + math.sin(self._time * 4 + i) * 0.2
            
            # Each leg has two segments
            mid_x = size//2 + int(size//3 * math.cos(leg_angle))
            mid_y = size//2 + int(size//3 * math.sin(leg_angle))
            
            end_angle = leg_angle + math.sin(self._time * 4 + i + math.pi) * 0.3
            end_x = mid_x + int(size//4 * math.cos(end_angle))
            end_y = mid_y + int(size//4 * math.sin(end_angle))
            
            # Draw leg segments
            pygame.draw.line(surface, leg_color,
                           (size//2, size//2), (mid_x, mid_y), 2)
            pygame.draw.line(surface, leg_color,
                           (mid_x, mid_y), (end_x, end_y), 2)
        
        # Eyes in two rows
        eye_positions = [
            (size//3, size*3//8), (size//2, size*3//8), (size*2//3, size*3//8),
            (size*3//8, size*4//7), (size*5//8, size*4//7)
        ]
        for x, y in eye_positions:
            self._draw_animated_eyes(surface, x, y, size,
                                  (255, 0, 0), (0, 0, 0))
        
        # Mandibles
        mandible_color = (48, 0, 48)
        mandible_angle = math.sin(self._time * 3) * 0.2
        for side in [-1, 1]:
            start_x = size//2 + side * size//8
            start_y = size//2
            end_x = start_x + int(side * size//8 * math.cos(mandible_angle))
            end_y = start_y + int(size//8 * math.sin(mandible_angle))
            pygame.draw.line(surface, mandible_color,
                           (start_x, start_y), (end_x, end_y), 3)
        
        # Web particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(200, 200, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_ghost(self, surface: pygame.Surface, size: int, anim: dict):
        """Render ghost with ethereal effects."""
        # Ghost body with transparency
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surface, (200, 200, 255, 128), (size//2, size//2), size//3)
        
        # Wavy bottom
        points = []
        for i in range(8):
            x = size//4 + (i * size//4)
            y = size//2 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        pygame.draw.polygon(ghost_surface, (200, 200, 255, 128), points)
        
        surface.blit(ghost_surface, (0, 0))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Ethereal particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_skeleton(self, surface: pygame.Surface, size: int, anim: dict):
        """Render skeleton with rattling bones."""
        # Skull
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//3), size//4)
        
        # Jaw movement
        jaw_y = size//3 + int(math.sin(self._time * 4) * size//20)
        pygame.draw.arc(surface, (200, 200, 200),
                       (size//2 - size//8, jaw_y - size//16, size//4, size//8),
                       0, math.pi, 2)
        
        # Spine
        pygame.draw.line(surface, (200, 200, 200),
                        (size//2, size//3 + size//4),
                        (size//2, size*2//3), 2)
        
        # Ribs
        for i in range(4):
            y = size//2 + i * size//8
            pygame.draw.line(surface, (200, 200, 200),
                           (size//2 - size//8, y),
                           (size//2 + size//8, y), 2)
        
        # Arms
        arm_angle = math.sin(self._time * 3) * 0.2
        pygame.draw.line(surface, (200, 200, 200),
                        (size//2, size//2),
                        (size//2 - int(size//3 * math.cos(arm_angle)),
                         size//2 + int(size//3 * math.sin(arm_angle))), 2)
        pygame.draw.line(surface, (200, 200, 200),
                        (size//2, size//2),
                        (size//2 + int(size//3 * math.cos(arm_angle)),
                         size//2 + int(size//3 * math.sin(arm_angle))), 2)
        
        # Legs
        leg_angle = math.sin(self._time * 3 + math.pi) * 0.2
        pygame.draw.line(surface, (200, 200, 200),
                        (size//2, size*2//3),
                        (size//2 - int(size//3 * math.cos(leg_angle)),
                         size*2//3 + int(size//3 * math.sin(leg_angle))), 2)
        pygame.draw.line(surface, (200, 200, 200),
                        (size//2, size*2//3),
                        (size//2 + int(size//3 * math.cos(leg_angle)),
                         size*2//3 + int(size//3 * math.sin(leg_angle))), 2)
        
        # Eye sockets
        pygame.draw.circle(surface, (0, 0, 0), (size//3, size//3), size//16)
        pygame.draw.circle(surface, (0, 0, 0), (size*2//3, size//3), size//16)

    def _render_slime(self, surface: pygame.Surface, size: int, anim: dict):
        """Render slime with bouncing animation."""
        # Slime body with squish effect
        squish = 1.0 + math.sin(self._time * 3) * 0.1
        pygame.draw.ellipse(surface, (0, 255, 0),
                          (size//4, size//3,
                           size//2, int(size//2 * squish)))
        
        # Eyes
        eye_y = size//3 + int(math.sin(self._time * 3) * size//20)
        self._draw_animated_eyes(surface, size//3, eye_y, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, eye_y, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Bubbles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=random.randint(size//4, size*3//4),
                y=size*2//3,
                dx=0,
                dy=-random.uniform(1, 2),
                color=(0, 255, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 3)
            ))
        
        self._draw_particles(surface)

    def _render_thought_devourer(self, surface: pygame.Surface, size: int, anim: dict):
        """Render thought devourer with psychic effects."""
        # Main body
        self._draw_shadow(surface, "circle", (128, 0, 128), size)
        pygame.draw.circle(surface, (128, 0, 128), (size//2, size//2), size//3)
        
        # Tentacles
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            tentacle_x = size//2 + int(size//2 * math.cos(angle))
            tentacle_y = size//2 + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, (128, 0, 128),
                           (size//2, size//2), (tentacle_x, tentacle_y), 2)
        
        # Central eye
        self._draw_animated_eyes(surface, size//2, size//2, size,
                               (255, 255, 255), (128, 0, 128))
        
        # Psychic energy particles
        if random.random() < 0.2:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(size//3, size//2)
            self._particles.append(Particle(
                x=size//2 + math.cos(angle) * dist,
                y=size//2 + math.sin(angle) * dist,
                dx=math.cos(angle) * -0.5,
                dy=math.sin(angle) * -0.5,
                color=(128, 0, 128),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_memory_phantom(self, surface: pygame.Surface, size: int, anim: dict):
        """Render memory phantom with shifting form."""
        # Shifting body
        shift = math.sin(self._time * 2) * size//8
        points = [
            (size//2, size//4),
            (size//4 + shift, size//2),
            (size//2, size*3//4),
            (size*3//4 - shift, size//2)
        ]
        pygame.draw.polygon(surface, (0, 128, 255), points)
        
        # Glowing eyes
        glow_intensity = (math.sin(self._time * 3) + 1) / 2
        eye_color = (int(255 * glow_intensity), int(255 * glow_intensity), 255)
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               eye_color, (0, 0, 255))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               eye_color, (0, 0, 255))
        
        # Memory fragments
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 128, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_psychic_hydra(self, surface: pygame.Surface, size: int, anim: dict):
        """Render psychic hydra with multiple heads."""
        # Body
        self._draw_shadow(surface, "circle", (255, 0, 255), size)
        pygame.draw.circle(surface, (255, 0, 255), (size//2, size//2), size//4)
        
        # Heads
        for i in range(3):
            angle = math.radians(i * 120 + math.sin(self._time * 2) * 10)
            head_x = size//2 + int(size//3 * math.cos(angle))
            head_y = size//2 + int(size//3 * math.sin(angle))
            
            # Head
            pygame.draw.circle(surface, (255, 0, 255),
                             (head_x, head_y), size//6)
            
            # Eyes
            eye_offset = size//12
            self._draw_animated_eyes(surface, head_x - eye_offset, head_y, size,
                                   (255, 255, 255), (255, 0, 255))
            self._draw_animated_eyes(surface, head_x + eye_offset, head_y, size,
                                   (255, 255, 255), (255, 0, 255))
        
        # Psychic energy
        if random.random() < 0.2:
            for i in range(3):
                angle = math.radians(i * 120 + random.uniform(-10, 10))
                self._particles.append(Particle(
                    x=size//2 + math.cos(angle) * size//3,
                    y=size//2 + math.sin(angle) * size//3,
                    dx=math.cos(angle) * -0.5,
                    dy=math.sin(angle) * -0.5,
                    color=(255, 0, 255),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_mind_colossus(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mind colossus with massive psychic presence."""
        # Main body
        self._draw_shadow(surface, "circle", (0, 0, 128), size)
        pygame.draw.circle(surface, (0, 0, 128), (size//2, size//2), size//2)
        
        # Central eye
        eye_size = int(size//3 * (1 + math.sin(self._time * 2) * 0.1))
        pygame.draw.circle(surface, (255, 255, 255),
                         (size//2, size//2), eye_size)
        pygame.draw.circle(surface, (0, 0, 0),
                         (size//2, size//2), eye_size//2)
        
        # Psychic aura
        if random.random() < 0.2:
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(size//4, size//2)
                self._particles.append(Particle(
                    x=size//2 + math.cos(angle) * dist,
                    y=size//2 + math.sin(angle) * dist,
                    dx=math.cos(angle) * -0.5,
                    dy=math.sin(angle) * -0.5,
                    color=(0, 0, 128),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(2, 4)
                ))
        
        self._draw_particles(surface)

    def _render_fire_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render fire elemental with flickering flames."""
        # Fire body
        self._draw_shadow(surface, "circle", (255, 100, 0), size)
        pygame.draw.circle(surface, (255, 100, 0), (size//2, size//2), size//3)
        
        # Flames
        flame_height = int(size//3 * (1 + math.sin(self._time * 4) * 0.2))
        points = [(size//2, size//2 - flame_height)]
        for i in range(5):
            angle = math.radians(i * 72 + math.sin(self._time * 3) * 20)
            x = size//2 + int(size//4 * math.cos(angle))
            y = size//2 - int(flame_height * 0.8)
            points.append((x, y))
        pygame.draw.polygon(surface, (255, 200, 0), points)
        
        # Fire particles
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

    def _render_ice_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render ice elemental with crystalline structure."""
        # Ice body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Crystalline structure
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.line(surface, (255, 255, 255),
                           (size//2, size//2), (x, y), 2)
        
        # Glowing core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 255, 255),
                         (size//2, size//2), core_size)
        
        # Ice particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_storm_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render storm elemental with swirling clouds."""
        # Cloud body
        self._draw_shadow(surface, "circle", (100, 100, 150), size)
        pygame.draw.circle(surface, (100, 100, 150), (size//2, size//2), size//3)
        
        # Swirling clouds
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 3) * 20)
            cloud_x = size//2 + int(size//3 * math.cos(angle))
            cloud_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (150, 150, 200),
                             (cloud_x, cloud_y), size//8)
        
        # Lightning
        if random.random() < 0.1:
            points = [(size//2, size//4)]
            for i in range(3):
                x = size//2 + random.randint(-size//8, size//8)
                y = size//4 + (i + 1) * size//8
                points.append((x, y))
            pygame.draw.lines(surface, (255, 255, 0), False, points, 2)
        
        # Storm particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 150),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_earth_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render earth golem with rocky texture and beefy arms."""
        # Rocky body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Rock texture
        for _ in range(10):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            rock_size = random.randint(2, 4)
            pygame.draw.circle(surface, (150, 100, 50), (x, y), rock_size)
        
        # Beefy spherical arms
        arm_color = (120, 60, 0)
        # Left arm
        arm_angle = math.sin(self._time * 0.4) * 0.2  # Slowed down arm movement
        shoulder_x = size//3
        shoulder_y = size//2
        elbow_x = shoulder_x - int(size//4 * math.cos(arm_angle))
        elbow_y = shoulder_y + int(size//4 * math.sin(arm_angle))
        
        # Upper arm sphere
        pygame.draw.circle(surface, arm_color, (shoulder_x, shoulder_y), size//6)
        # Forearm sphere
        pygame.draw.circle(surface, arm_color, (elbow_x, elbow_y), size//8)
        
        # Right arm (mirrored)
        shoulder_x = size*2//3
        elbow_x = shoulder_x + int(size//4 * math.cos(arm_angle))
        
        # Upper arm sphere
        pygame.draw.circle(surface, arm_color, (shoulder_x, shoulder_y), size//6)
        # Forearm sphere
        pygame.draw.circle(surface, arm_color, (elbow_x, elbow_y), size//8)
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        
        # Rock cracks with lava
        for _ in range(3):
            start_x = random.randint(size//3, size*2//3)
            start_y = random.randint(size//3, size*2//3)
            end_x = start_x + random.randint(-size//8, size//8)
            end_y = start_y + random.randint(-size//8, size//8)
            pygame.draw.line(surface, (255, 100, 0), 
                           (start_x, start_y), (end_x, end_y), 2)
        
        # Dust and ember particles (slowed down)
        if random.random() < 0.04:  # Reduced from 0.2 to 0.04 (5x slower)
            particle_type = random.choice(['dust', 'ember'])
            if particle_type == 'dust':
                color = (80, 40, 0)  # Darker dust color
                size_range = (1, 2)
                life_range = (2.5, 5.0)  # Increased from (0.5, 1.0)
            else:
                color = (255, 150, 0)  # Fixed ember color
                size_range = (1, 1.5)
                life_range = (1.5, 3.0)  # Increased from (0.3, 0.6)
                
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.1, 0.1),  # Slowed down movement
                dy=random.uniform(-0.1, 0.1),  # Slowed down movement
                color=color,
                life=random.uniform(*life_range),
                size=random.uniform(*size_range)
            ))
        
        self._draw_particles(surface)

    def _render_zombie(self, surface: pygame.Surface, size: int, anim: dict):
        """Render zombie with decay effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        pygame.draw.circle(surface, (0, 100, 0), (size//2, size//2), size//3)
        
        # Decaying flesh
        for _ in range(5):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            decay_size = random.randint(2, 4)
            pygame.draw.circle(surface, (0, 150, 0), (x, y), decay_size)
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        
        # Decay particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(0, 100, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render wraith with ethereal form."""
        # Ethereal body
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surface, (100, 100, 100, 128),
                         (size//2, size//2), size//3)
        
        # Wavy form
        points = []
        for i in range(8):
            x = size//4 + (i * size//4)
            y = size//2 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        pygame.draw.polygon(ghost_surface, (100, 100, 100, 128), points)
        
        surface.blit(ghost_surface, (0, 0))
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Dark energy particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 100),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_vampire(self, surface: pygame.Surface, size: int, anim: dict):
        """Render vampire with dark aura."""
        # Body
        self._draw_shadow(surface, "circle", (50, 0, 0), size)
        pygame.draw.circle(surface, (50, 0, 0), (size//2, size//2), size//3)
        
        # Cape
        cape_points = [(size//2, size//3)]
        for i in range(4):
            x = size//2 + int(math.cos(self._time * 2 + i) * size//6)
            y = size//3 + (i * size//8)
            cape_points.append((x, y))
        pygame.draw.polygon(surface, (100, 0, 0), cape_points)
        
        # Glowing red eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        
        # Dark aura particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 0, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_lich(self, surface: pygame.Surface, size: int, anim: dict):
        """Render lich with necrotic energy."""
        # Robed body
        self._draw_shadow(surface, "circle", (0, 50, 0), size)
        pygame.draw.circle(surface, (0, 50, 0), (size//2, size//2), size//3)
        
        # Staff
        staff_y = size//2 - int(size//3 * math.sin(self._time * 2) * 0.1)
        pygame.draw.line(surface, (100, 100, 100),
                        (size//2, size//2),
                        (size//2, staff_y), 3)
        
        # Skull head
        pygame.draw.circle(surface, (200, 200, 200),
                         (size//2, size//3), size//6)
        
        # Eye sockets
        self._draw_animated_eyes(surface, size//3, size//3, size,
                               (0, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//3, size,
                               (0, 255, 0), (0, 0, 0))
        
        # Necrotic energy particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 255, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_pixie(self, surface: pygame.Surface, size: int, anim: dict):
        """Render pixie with magical sparkles."""
        # Body
        self._draw_shadow(surface, "circle", (255, 200, 255), size)
        pygame.draw.circle(surface, (255, 200, 255), (size//2, size//2), size//4)
        
        # Wings
        wing_color = (255, 255, 255, 128)
        wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 - int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        surface.blit(wing_surface, (0, 0))
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (255, 200, 255))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (255, 200, 255))
        
        # Sparkle particles
        if random.random() < 0.3:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
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
        # Calculate horn points
        base_y = size//3  # Top of the white circle
        base_width = 20
        point_y = size//6  # Point of the horn
        points = [
            (size//2 - base_width//2, base_y),  # Left base point
            (size//2 + base_width//2, base_y),  # Right base point
            (size//2, point_y)  # Point
        ]
        # Main horn triangle
        pygame.draw.polygon(surface, horn_color, points)
        # Horn glow
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        glow_color = (*horn_color, 128)
        # Draw a slightly larger triangle for the glow
        glow_points = [
            (size//2 - base_width//2 - 2, base_y - 2),
            (size//2 + base_width//2 + 2, base_y - 2),
            (size//2, point_y - 2)
        ]
        pygame.draw.polygon(glow_surface, glow_color, glow_points)
        surface.blit(glow_surface, (0, 0))
        
        # Horn spiral
        spiral_points = []
        for i in range(5):
            angle = math.radians(i * 30)
            x = size//2 + int(size//20 * math.cos(angle))
            y = base_y - int(i * size//15)
            spiral_points.append((x, y))
        pygame.draw.lines(surface, (255, 255, 255), False, spiral_points, 1)
        
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
            # Regular magical particles
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

    def _render_griffin(self, surface: pygame.Surface, size: int, anim: dict):
        """Render griffin with majestic effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 0), size)
        pygame.draw.circle(surface, (200, 200, 0), (size//2, size//2), size//3)
        
        # Wings
        wing_color = (255, 255, 200)
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
        
        # Beak
        beak_color = (255, 200, 0)
        points = [(size//2, size//3), (size//2 + size//6, size//3)]
        pygame.draw.lines(surface, beak_color, False, points, 3)
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Feather particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_treant(self, surface: pygame.Surface, size: int, anim: dict):
        """Render treant with bark texture and leaves."""
        # Body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Bark texture
        for _ in range(10):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            bark_size = random.randint(2, 4)
            pygame.draw.circle(surface, (150, 100, 50), (x, y), bark_size)
        
        # Face
        face_y = size//3
        # Eyes
        self._draw_animated_eyes(surface, size//3, face_y, size,
                               (0, 100, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, face_y, size,
                               (0, 100, 0), (0, 0, 0))
        # Mouth (simple line)
        pygame.draw.line(surface, (0, 100, 0),
                        (size//2 - size//8, face_y + size//8),
                        (size//2 + size//8, face_y + size//8), 2)
        
        # Branches
        for i in range(4):
            angle = math.radians(i * 90 + math.sin(self._time * 2) * 10)
            branch_x = size//2 + int(size//3 * math.cos(angle))
            branch_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.line(surface, (100, 50, 0),
                           (size//2, size//2), (branch_x, branch_y), 3)
            # Leaves
            leaf_color = (0, 200, 0)
            for j in range(3):
                leaf_angle = angle + math.radians(j * 30)
                leaf_x = branch_x + int(size//8 * math.cos(leaf_angle))
                leaf_y = branch_y + int(size//8 * math.sin(leaf_angle))
                pygame.draw.circle(surface, leaf_color, (leaf_x, leaf_y), size//12)
        
        # Leaf particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 200, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_wolf(self, surface: pygame.Surface, size: int, anim: dict):
        """Render wolf with glowing eyes and fur texture."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Fur texture
        for _ in range(15):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            fur_size = random.randint(1, 3)
            pygame.draw.circle(surface, (150, 150, 150), (x, y), fur_size)
        
        # Snout
        snout_color = (80, 80, 80)
        pygame.draw.ellipse(surface, snout_color,
                          (size//2 - size//8, size//2 - size//8,
                           size//4, size//4))
        
        # Ears
        ear_color = (80, 80, 80)
        # Left ear
        points = [(size//3, size//3), (size//3 - size//8, size//4), (size//3, size//4)]
        pygame.draw.polygon(surface, ear_color, points)
        # Right ear
        points = [(size*2//3, size//3), (size*2//3 + size//8, size//4), (size*2//3, size//4)]
        pygame.draw.polygon(surface, ear_color, points)
        
        # Glowing eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Fur particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(150, 150, 150),
                life=random.uniform(0.3, 0.6),
                size=random.uniform(1, 1.5)
            ))
        
        self._draw_particles(surface)

    def _render_bear(self, surface: pygame.Surface, size: int, anim: dict):
        """Render bear with claws and fur texture."""
        # Body
        self._draw_shadow(surface, "circle", (139, 69, 19), size)
        pygame.draw.circle(surface, (139, 69, 19), (size//2, size//2), size//3)
        
        # Fur texture
        for _ in range(20):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            fur_size = random.randint(2, 4)
            pygame.draw.circle(surface, (160, 82, 45), (x, y), fur_size)
        
        # Snout
        snout_color = (101, 67, 33)
        pygame.draw.ellipse(surface, snout_color,
                          (size//2 - size//8, size//2 - size//8,
                           size//4, size//4))
        
        # Ears
        ear_color = (101, 67, 33)
        # Left ear
        pygame.draw.circle(surface, ear_color,
                         (size//3, size//3), size//8)
        # Right ear
        pygame.draw.circle(surface, ear_color,
                         (size*2//3, size//3), size//8)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Claws
        claw_color = (255, 255, 255)
        for i in range(4):
            angle = math.radians(i * 90 + math.sin(self._time * 2) * 10)
            claw_x = size//2 + int(size//2 * math.cos(angle))
            claw_y = size//2 + int(size//2 * math.sin(angle))
            pygame.draw.line(surface, claw_color,
                           (size//2, size//2), (claw_x, claw_y), 2)
        
        # Fur particles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(160, 82, 45),
                life=random.uniform(0.3, 0.6),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dryad(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dryad with nature effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        pygame.draw.circle(surface, (0, 100, 0), (size//2, size//2), size//3)
        
        # Face
        face_y = size//3
        # Eyes
        self._draw_animated_eyes(surface, size//3, face_y, size,
                               (255, 255, 255), (0, 100, 0))
        self._draw_animated_eyes(surface, size*2//3, face_y, size,
                               (255, 255, 255), (0, 100, 0))
        
        # Hair (vines)
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            vine_x = size//2 + int(size//3 * math.cos(angle))
            vine_y = size//3 + int(size//3 * math.sin(angle))
            pygame.draw.line(surface, (0, 150, 0),
                           (size//2, size//3), (vine_x, vine_y), 2)
            # Leaves on vines
            leaf_color = (0, 200, 0)
            for j in range(2):
                leaf_angle = angle + math.radians(j * 30)
                leaf_x = vine_x + int(size//8 * math.cos(leaf_angle))
                leaf_y = vine_y + int(size//8 * math.sin(leaf_angle))
                pygame.draw.circle(surface, leaf_color, (leaf_x, leaf_y), size//12)
        
        # Nature particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 200, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_demon(self, surface: pygame.Surface, size: int, anim: dict):
        """Render demon with horns and fire effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        pygame.draw.circle(surface, (100, 0, 0), (size//2, size//2), size//3)
        
        # Horns
        horn_color = (50, 0, 0)
        # Left horn
        points = [(size//3, size//3), (size//3 - size//8, size//4), (size//3 - size//16, size//3)]
        pygame.draw.polygon(surface, horn_color, points)
        # Right horn
        points = [(size*2//3, size//3), (size*2//3 + size//8, size//4), (size*2//3 + size//16, size//3)]
        pygame.draw.polygon(surface, horn_color, points)
        
        # Glowing red eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        
        # Fire particles
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

    def _render_shadow_stalker(self, surface: pygame.Surface, size: int, anim: dict):
        """Render shadow stalker with ethereal dark form."""
        # Ethereal body
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surface, (0, 0, 0, 128),
                         (size//2, size//2), size//3)
        
        # Wavy form
        points = []
        for i in range(8):
            x = size//4 + (i * size//4)
            y = size//2 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        pygame.draw.polygon(ghost_surface, (0, 0, 0, 128), points)
        
        surface.blit(ghost_surface, (0, 0))
        
        # Glowing purple eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (128, 0, 128), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (128, 0, 128), (0, 0, 0))
        
        # Dark energy particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 0, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
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
        points = [(size//2 - size//8, size//3), (size//2 - size//4, size//4), (size//2 - size//6, size//3)]
        pygame.draw.polygon(surface, ear_color, points)
        # Right ear
        points = [(size//2 + size//8, size//3), (size//2 + size//4, size//4), (size//2 + size//6, size//3)]
        pygame.draw.polygon(surface, ear_color, points)
        
        # Glowing red eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 0), (0, 0, 0))
        
        # Fire mane
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

    def _render_dark_wizard(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dark wizard with staff and dark aura."""
        # Robed body
        self._draw_shadow(surface, "circle", (50, 0, 50), size)
        pygame.draw.circle(surface, (50, 0, 50), (size//2, size//2), size//3)
        
        # Hood
        hood_color = (25, 0, 25)
        points = [(size//2, size//3), (size//3, size//2), (size*2//3, size//2)]
        pygame.draw.polygon(surface, hood_color, points)
        
        # Staff
        staff_y = size//2 - int(size//3 * math.sin(self._time * 2) * 0.1)
        pygame.draw.line(surface, (100, 100, 100),
                        (size//2, size//2),
                        (size//2, staff_y), 3)
        # Staff orb
        pygame.draw.circle(surface, (128, 0, 128),
                         (size//2, staff_y), size//12)
        
        # Glowing purple eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (128, 0, 128), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (128, 0, 128), (0, 0, 0))
        
        # Dark aura particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 0, 50),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_kraken(self, surface: pygame.Surface, size: int, anim: dict):
        """Render kraken with animated tentacles."""
        # Body
        self._draw_shadow(surface, "circle", (0, 0, 100), size)
        pygame.draw.circle(surface, (0, 0, 100), (size//2, size//2), size//3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Tentacles
        tentacle_color = (0, 0, 150)
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2 + i) * 20)
            start_x = size//2 + int(size//4 * math.cos(angle))
            start_y = size//2 + int(size//4 * math.sin(angle))
            end_x = start_x + int(size//3 * math.cos(angle + math.sin(self._time * 3 + i) * 0.5))
            end_y = start_y + int(size//3 * math.sin(angle + math.sin(self._time * 3 + i) * 0.5))
            pygame.draw.line(surface, tentacle_color, (start_x, start_y), (end_x, end_y), 3)
        
        # Bubbles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_mermaid(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mermaid with flowing tail."""
        # Upper body
        self._draw_shadow(surface, "circle", (0, 100, 150), size)
        pygame.draw.circle(surface, (0, 100, 150), (size//2, size//2), size//4)
        
        # Tail
        tail_color = (0, 150, 200)
        points = [(size//2, size//2 + size//4)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 2) * 10)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + size//4 + i * size//8
            points.append((x, y))
        pygame.draw.polygon(surface, tail_color, points)
        
        # Hair
        hair_color = (255, 200, 150)
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//4 * math.cos(angle))
            y = size//2 - size//4 + int(size//4 * math.sin(angle))
            pygame.draw.line(surface, hair_color,
                           (size//2, size//2 - size//4), (x, y), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Bubbles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_leviathan(self, surface: pygame.Surface, size: int, anim: dict):
        """Render leviathan with serpentine body."""
        # Head
        self._draw_shadow(surface, "circle", (0, 50, 100), size)
        pygame.draw.circle(surface, (0, 50, 100), (size//2, size//3), size//4)
        
        # Body segments
        for i in range(3):
            segment_x = size//2 + int(math.sin(self._time * 2 + i) * size//8)
            segment_y = size//3 + i * size//6
            pygame.draw.circle(surface, (0, 50, 100),
                             (segment_x, segment_y), size//6)
        
        # Fins
        fin_color = (0, 100, 150)
        for i in range(3):
            angle = math.radians(i * 120 + math.sin(self._time * 3) * 20)
            fin_x = size//2 + int(size//3 * math.cos(angle))
            fin_y = size//2 + int(size//3 * math.sin(angle))
            points = [(fin_x, fin_y),
                     (fin_x + int(size//8 * math.cos(angle + math.pi/2)),
                      fin_y + int(size//8 * math.sin(angle + math.pi/2))),
                     (fin_x + int(size//8 * math.cos(angle - math.pi/2)),
                      fin_y + int(size//8 * math.sin(angle - math.pi/2)))]
            pygame.draw.polygon(surface, fin_color, points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//3, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//3, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Bubbles
        if random.random() < 0.1:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-0.5, 0.5),
                dy=random.uniform(-0.5, 0.5),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_siren(self, surface: pygame.Surface, size: int, anim: dict):
        """Render siren with enchanting effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 0, 150), size)
        pygame.draw.circle(surface, (150, 0, 150), (size//2, size//2), size//3)
        
        # Wings
        wing_color = (200, 0, 200, 128)
        wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 - int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 3) * 10)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        surface.blit(wing_surface, (0, 0))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (150, 0, 150))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (150, 0, 150))
        
        # Enchanting particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 0, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_mantis(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mantis with praying arms."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        pygame.draw.circle(surface, (0, 100, 0), (size//2, size//2), size//4)
        
        # Praying arms
        arm_color = (0, 150, 0)
        for i in range(2):
            angle = math.radians(i * 180 + math.sin(self._time * 2) * 30)
            start_x = size//2 + int(size//4 * math.cos(angle))
            start_y = size//2 + int(size//4 * math.sin(angle))
            end_x = start_x + int(size//3 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//3 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, arm_color, (start_x, start_y), (end_x, end_y), 3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Antennae
        for i in range(2):
            angle = math.radians(i * 180 + math.sin(self._time * 3) * 20)
            start_x = size//2 + int(size//6 * math.cos(angle))
            start_y = size//2 - size//4
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/6))
            end_y = start_y - int(size//4 * math.sin(angle + math.pi/6))
            pygame.draw.line(surface, arm_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Legs
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2 + i) * 20)
            start_x = size//2 + int(size//4 * math.cos(angle))
            start_y = size//2 + int(size//4 * math.sin(angle))
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//4 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, arm_color, (start_x, start_y), (end_x, end_y), 2)
        
        self._draw_particles(surface)

    def _render_beetle(self, surface: pygame.Surface, size: int, anim: dict):
        """Render beetle with armored shell."""
        # Shell
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        pygame.draw.circle(surface, (50, 50, 50), (size//2, size//2), size//3)
        
        # Shell segments
        for i in range(6):
            angle = math.radians(i * 60)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (100, 100, 100), (x, y), size//8)
        
        # Head
        head_color = (100, 100, 100)
        pygame.draw.circle(surface, head_color, (size//2, size//3), size//6)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//3, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//3, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Antennae
        for i in range(2):
            angle = math.radians(i * 180 + math.sin(self._time * 3) * 20)
            start_x = size//2 + int(size//6 * math.cos(angle))
            start_y = size//3
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/6))
            end_y = start_y - int(size//4 * math.sin(angle + math.pi/6))
            pygame.draw.line(surface, head_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Legs
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2 + i) * 20)
            start_x = size//2 + int(size//3 * math.cos(angle))
            start_y = size//2 + int(size//3 * math.sin(angle))
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//4 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, head_color, (start_x, start_y), (end_x, end_y), 2)
        
        self._draw_particles(surface)

    def _render_scorpion(self, surface: pygame.Surface, size: int, anim: dict):
        """Render scorpion with stinger tail."""
        # Body
        self._draw_shadow(surface, "circle", (100, 0, 0), size)
        pygame.draw.circle(surface, (100, 0, 0), (size//2, size//2), size//4)
        
        # Tail segments
        tail_color = (150, 0, 0)
        points = [(size//2, size//2)]
        for i in range(4):
            angle = math.radians(180 + math.sin(self._time * 2 + i) * 20)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.lines(surface, tail_color, False, points, 3)
        
        # Stinger
        stinger_points = [
            (points[-1][0], points[-1][1]),
            (points[-1][0] - size//8, points[-1][1] - size//8),
            (points[-1][0] + size//8, points[-1][1] - size//8)
        ]
        pygame.draw.polygon(surface, tail_color, stinger_points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Pincers
        for i in range(2):
            angle = math.radians(i * 180 + math.sin(self._time * 2) * 30)
            start_x = size//2 + int(size//4 * math.cos(angle))
            start_y = size//2 + int(size//4 * math.sin(angle))
            end_x = start_x + int(size//3 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//3 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, tail_color, (start_x, start_y), (end_x, end_y), 3)
        
        # Legs
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2 + i) * 20)
            start_x = size//2 + int(size//3 * math.cos(angle))
            start_y = size//2 + int(size//3 * math.sin(angle))
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//4 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, tail_color, (start_x, start_y), (end_x, end_y), 2)
        
        self._draw_particles(surface)

    def _render_wasp(self, surface: pygame.Surface, size: int, anim: dict):
        """Render wasp with buzzing wings."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 0), size)
        pygame.draw.circle(surface, (200, 200, 0), (size//2, size//2), size//4)
        
        # Stripes
        for i in range(3):
            y = size//2 - size//4 + i * size//6
            pygame.draw.line(surface, (0, 0, 0),
                           (size//2 - size//4, y),
                           (size//2 + size//4, y), 3)
        
        # Wings
        wing_color = (255, 255, 255, 128)
        wing_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Left wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 4) * 20)
            x = size//2 - int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        # Right wing
        points = [(size//2, size//2)]
        for i in range(5):
            angle = math.radians(i * 30 + math.sin(self._time * 4) * 20)
            x = size//2 + int(size//3 * math.cos(angle))
            y = size//2 + int(size//3 * math.sin(angle))
            points.append((x, y))
        pygame.draw.polygon(wing_surface, wing_color, points)
        
        surface.blit(wing_surface, (0, 0))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Antennae
        for i in range(2):
            angle = math.radians(i * 180 + math.sin(self._time * 3) * 20)
            start_x = size//2 + int(size//6 * math.cos(angle))
            start_y = size//2 - size//4
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/6))
            end_y = start_y - int(size//4 * math.sin(angle + math.pi/6))
            pygame.draw.line(surface, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)
        
        # Stinger
        stinger_points = [
            (size//2, size//2 + size//4),
            (size//2 - size//8, size//2 + size//3),
            (size//2 + size//8, size//2 + size//3)
        ]
        pygame.draw.polygon(surface, (0, 0, 0), stinger_points)
        
        # Legs
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2 + i) * 20)
            start_x = size//2 + int(size//3 * math.cos(angle))
            start_y = size//2 + int(size//3 * math.sin(angle))
            end_x = start_x + int(size//4 * math.cos(angle + math.pi/4))
            end_y = start_y + int(size//4 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, (0, 0, 0), (start_x, start_y), (end_x, end_y), 2)
        
        self._draw_particles(surface)

    def _render_clockwork_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render clockwork golem with gears and steam effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Gears
        gear_color = (150, 150, 150)
        for i in range(3):
            angle = math.radians(i * 120 + math.sin(self._time * 2) * 10)
            gear_x = size//2 + int(size//3 * math.cos(angle))
            gear_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, gear_color, (gear_x, gear_y), size//8)
            # Gear teeth
            for j in range(8):
                tooth_angle = math.radians(j * 45 + math.sin(self._time * 2) * 10)
                tooth_x = gear_x + int(size//8 * math.cos(tooth_angle))
                tooth_y = gear_y + int(size//8 * math.sin(tooth_angle))
                pygame.draw.line(surface, gear_color, (gear_x, gear_y), (tooth_x, tooth_y), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        
        # Steam vents
        if random.random() < 0.2:
            for i in range(3):
                angle = math.radians(i * 120 + random.uniform(-10, 10))
                self._particles.append(Particle(
                    x=size//2 + math.cos(angle) * size//3,
                    y=size//2 + math.sin(angle) * size//3,
                    dx=math.cos(angle) * 0.5,
                    dy=math.sin(angle) * 0.5,
                    color=(200, 200, 200),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_automaton(self, surface: pygame.Surface, size: int, anim: dict):
        """Render automaton with glowing circuits."""
        # Body
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        pygame.draw.circle(surface, (50, 50, 50), (size//2, size//2), size//3)
        
        # Circuit patterns
        circuit_color = (0, 200, 255)
        for i in range(4):
            angle = math.radians(i * 90 + math.sin(self._time * 2) * 10)
            start_x = size//2 + int(size//4 * math.cos(angle))
            start_y = size//2 + int(size//4 * math.sin(angle))
            end_x = size//2 + int(size//3 * math.cos(angle + math.pi/4))
            end_y = size//2 + int(size//3 * math.sin(angle + math.pi/4))
            pygame.draw.line(surface, circuit_color, (start_x, start_y), (end_x, end_y), 2)
        
        # Glowing core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, circuit_color, (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        
        # Circuit particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=circuit_color,
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_steam_knight(self, surface: pygame.Surface, size: int, anim: dict):
        """Render steam knight with armored plates and steam vents."""
        # Body
        self._draw_shadow(surface, "circle", (80, 80, 80), size)
        pygame.draw.circle(surface, (80, 80, 80), (size//2, size//2), size//3)
        
        # Armor plates
        plate_color = (100, 100, 100)
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            plate_x = size//2 + int(size//3 * math.cos(angle))
            plate_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, plate_color, (plate_x, plate_y), size//8)
        
        # Steam vents
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                self._particles.append(Particle(
                    x=size//2 + math.cos(angle) * size//3,
                    y=size//2 + math.sin(angle) * size//3,
                    dx=math.cos(angle) * 0.5,
                    dy=math.sin(angle) * 0.5,
                    color=(200, 200, 200),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        
        self._draw_particles(surface)

    def _render_tesla_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render tesla guardian with electrical effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 200), size)
        pygame.draw.circle(surface, (0, 100, 200), (size//2, size//2), size//3)
        
        # Electrical arcs
        if random.random() < 0.2:
            for i in range(3):
                start_angle = random.uniform(0, math.pi * 2)
                end_angle = start_angle + random.uniform(-math.pi/4, math.pi/4)
                start_x = size//2 + int(size//3 * math.cos(start_angle))
                start_y = size//2 + int(size//3 * math.sin(start_angle))
                end_x = size//2 + int(size//2 * math.cos(end_angle))
                end_y = size//2 + int(size//2 * math.sin(end_angle))
                points = [(start_x, start_y)]
                for j in range(3):
                    mid_x = start_x + (end_x - start_x) * (j + 1) / 4 + random.uniform(-10, 10)
                    mid_y = start_y + (end_y - start_y) * (j + 1) / 4 + random.uniform(-10, 10)
                    points.append((mid_x, mid_y))
                points.append((end_x, end_y))
                pygame.draw.lines(surface, (0, 200, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (0, 200, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        
        # Electrical particles
        if random.random() < 0.3:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 200, 255),
                life=random.uniform(0.3, 0.6),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_crystal_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render crystal golem with prismatic effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Crystal facets
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            facet_x = size//2 + int(size//3 * math.cos(angle))
            facet_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.polygon(surface, (220, 220, 255), [
                (size//2, size//2),
                (facet_x, facet_y),
                (size//2 + int(size//3 * math.cos(angle + math.pi/3)),
                 size//2 + int(size//3 * math.sin(angle + math.pi/3)))
            ])
        
        # Glowing core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Prismatic particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(random.randint(200, 255), random.randint(200, 255), 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_prism_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render prism elemental with light-bending effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 255, 255), size)
        pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), size//3)
        
        # Prism facets
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            facet_x = size//2 + int(size//3 * math.cos(angle))
            facet_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.polygon(surface, (random.randint(200, 255), random.randint(200, 255), 255), [
                (size//2, size//2),
                (facet_x, facet_y),
                (size//2 + int(size//3 * math.cos(angle + math.pi/4)),
                 size//2 + int(size//3 * math.sin(angle + math.pi/4)))
            ])
        
        # Light beams
        if random.random() < 0.2:
            for i in range(3):
                angle = math.radians(i * 120 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 255, 255), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Light particles
        if random.random() < 0.3:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(random.randint(200, 255), random.randint(200, 255), 255),
                life=random.uniform(0.3, 0.6),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_geode_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render geode guardian with crystal formations."""
        # Body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Crystal formations
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            crystal_x = size//2 + int(size//3 * math.cos(angle))
            crystal_y = size//2 + int(size//3 * math.sin(angle))
            crystal_size = random.randint(size//12, size//8)
            pygame.draw.polygon(surface, (random.randint(200, 255), random.randint(200, 255), 255), [
                (crystal_x, crystal_y),
                (crystal_x + crystal_size, crystal_y + crystal_size),
                (crystal_x, crystal_y + crystal_size * 2),
                (crystal_x - crystal_size, crystal_y + crystal_size)
            ])
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Crystal particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(random.randint(200, 255), random.randint(200, 255), 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_diamond_sentinel(self, surface: pygame.Surface, size: int, anim: dict):
        """Render diamond sentinel with faceted body."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Diamond facets
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            facet_x = size//2 + int(size//3 * math.cos(angle))
            facet_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.polygon(surface, (220, 220, 255), [
                (size//2, size//2),
                (facet_x, facet_y),
                (size//2 + int(size//3 * math.cos(angle + math.pi/3)),
                 size//2 + int(size//3 * math.sin(angle + math.pi/3)))
            ])
        
        # Glowing core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Light particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_myconid(self, surface: pygame.Surface, size: int, anim: dict):
        """Render myconid with mushroom features."""
        # Body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Mushroom cap
        cap_color = (150, 0, 0)
        pygame.draw.ellipse(surface, cap_color,
                          (size//2 - size//3, size//2 - size//3,
                           size//1.5, size//3))
        
        # Spots on cap
        for _ in range(5):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size//2)
            pygame.draw.circle(surface, (200, 200, 200), (x, y), size//16)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Spore particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_spore_beast(self, surface: pygame.Surface, size: int, anim: dict):
        """Render spore beast with fungal features and spore clouds."""
        # Body
        self._draw_shadow(surface, "circle", (50, 100, 0), size)
        pygame.draw.circle(surface, (50, 100, 0), (size//2, size//2), size//3)
        
        # Fungal growths
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            growth_x = size//2 + int(size//3 * math.cos(angle))
            growth_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (100, 150, 0), (growth_x, growth_y), size//8)
        
        # Spore clouds
        if random.random() < 0.3:
            for i in range(3):
                angle = math.radians(i * 120 + random.uniform(-10, 10))
                cloud_x = size//2 + int(size//3 * math.cos(angle))
                cloud_y = size//2 + int(size//3 * math.sin(angle))
                pygame.draw.circle(surface, (200, 200, 200, 128), (cloud_x, cloud_y), size//6)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Spore particles
        if random.random() < 0.3:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_mold_horror(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mold horror with creeping mold effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        pygame.draw.circle(surface, (0, 100, 0), (size//2, size//2), size//3)
        
        # Mold patches
        for _ in range(8):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size*3//4)
            patch_size = random.randint(size//12, size//8)
            pygame.draw.circle(surface, (0, 150, 0), (x, y), patch_size)
        
        # Creeping tendrils
        if random.random() < 0.2:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (0, 150, 0), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Mold particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(0, 150, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_fungal_colossus(self, surface: pygame.Surface, size: int, anim: dict):
        """Render fungal colossus with massive mushroom features."""
        # Body
        self._draw_shadow(surface, "circle", (50, 50, 0), size)
        pygame.draw.circle(surface, (50, 50, 0), (size//2, size//2), size//3)
        
        # Giant mushroom cap
        cap_color = (100, 0, 0)
        pygame.draw.ellipse(surface, cap_color,
                          (size//2 - size//2, size//2 - size//2,
                           size, size//2))
        
        # Spots on cap
        for _ in range(8):
            x = random.randint(size//4, size*3//4)
            y = random.randint(size//4, size//2)
            pygame.draw.circle(surface, (200, 200, 200), (x, y), size//12)
        
        # Fungal growths
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            growth_x = size//2 + int(size//3 * math.cos(angle))
            growth_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (100, 100, 0), (growth_x, growth_y), size//8)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Spore particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(200, 200, 200),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_void_walker(self, surface: pygame.Surface, size: int, anim: dict):
        """Render void walker with pure darkness effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        pygame.draw.circle(surface, (0, 0, 0), (size//2, size//2), size//3)
        
        # Void tendrils
        if random.random() < 0.2:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (50, 50, 50), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Void particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 50, 50),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_shade(self, surface: pygame.Surface, size: int, anim: dict):
        """Render shade with shadowy form."""
        # Body
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        pygame.draw.circle(surface, (50, 50, 50), (size//2, size//2), size//3)
        
        # Wavy form
        points = []
        for i in range(8):
            x = size//4 + (i * size//4)
            y = size//2 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        pygame.draw.polygon(surface, (50, 50, 50), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Shadow particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 50, 50),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dark_phantom(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dark phantom with ghostly shadow effects."""
        # Body
        self._draw_shadow(surface, "circle", (25, 25, 25), size)
        pygame.draw.circle(surface, (25, 25, 25), (size//2, size//2), size//3)
        
        # Ethereal form
        ghost_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(ghost_surface, (25, 25, 25, 128),
                         (size//2, size//2), size//3)
        
        # Wavy bottom
        points = []
        for i in range(8):
            x = size//4 + (i * size//4)
            y = size//2 + int(math.sin(self._time * 3 + i) * size//8)
            points.append((x, y))
        pygame.draw.polygon(ghost_surface, (25, 25, 25, 128), points)
        
        surface.blit(ghost_surface, (0, 0))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Shadow particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(25, 25, 25),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_umbra_beast(self, surface: pygame.Surface, size: int, anim: dict):
        """Render umbra beast with shadow-formed body."""
        # Body
        self._draw_shadow(surface, "circle", (0, 0, 0), size)
        pygame.draw.circle(surface, (0, 0, 0), (size//2, size//2), size//3)
        
        # Shadow tendrils
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            tendril_x = size//2 + int(size//3 * math.cos(angle))
            tendril_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.line(surface, (50, 50, 50),
                           (size//2, size//2), (tendril_x, tendril_y), 3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Shadow particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(50, 50, 50),
                    life=random.uniform(0.5, 1.0),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_star_seraph(self, surface: pygame.Surface, size: int, anim: dict):
        """Render star seraph with radiant star patterns."""
        # Body
        self._draw_shadow(surface, "circle", (255, 255, 200), size)
        pygame.draw.circle(surface, (255, 255, 200), (size//2, size//2), size//3)
        
        # Star patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            star_x = size//2 + int(size//3 * math.cos(angle))
            star_y = size//2 + int(size//3 * math.sin(angle))
            # Draw star
            points = []
            for j in range(5):
                star_angle = math.radians(j * 72 + math.sin(self._time * 2) * 10)
                points.append((
                    star_x + int(size//8 * math.cos(star_angle)),
                    star_y + int(size//8 * math.sin(star_angle))
                ))
            pygame.draw.polygon(surface, (255, 255, 0), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Radiant particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_moon_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render moon guardian with crescent effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Crescent moon
        crescent_color = (255, 255, 255)
        pygame.draw.arc(surface, crescent_color,
                       (size//2 - size//3, size//2 - size//3,
                        size//1.5, size//1.5),
                       math.pi/4, math.pi*3/4, 3)
        
        # Moon phases
        if random.random() < 0.2:
            phase = random.randint(0, 3)
            if phase == 0:  # New moon
                pygame.draw.circle(surface, (50, 50, 50),
                                 (size//2, size//2), size//4)
            elif phase == 1:  # First quarter
                pygame.draw.arc(surface, crescent_color,
                              (size//2 - size//3, size//2 - size//3,
                               size//1.5, size//1.5),
                               math.pi/4, math.pi*3/4, 3)
            elif phase == 2:  # Full moon
                pygame.draw.circle(surface, crescent_color,
                                 (size//2, size//2), size//4)
            else:  # Last quarter
                pygame.draw.arc(surface, crescent_color,
                              (size//2 - size//3, size//2 - size//3,
                               size//1.5, size//1.5),
                               math.pi*5/4, math.pi*7/4, 3)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Lunar particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(255, 255, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_solar_phoenix(self, surface: pygame.Surface, size: int, anim: dict):
        """Render solar phoenix with solar flare effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 200, 0), size)
        pygame.draw.circle(surface, (255, 200, 0), (size//2, size//2), size//3)
        
        # Solar flares
        if random.random() < 0.3:
            for i in range(6):
                angle = math.radians(i * 60 + random.uniform(-10, 10))
                flare_length = random.uniform(size//4, size//2)
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(flare_length * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(flare_length * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 100, 0), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 255, 0), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Solar particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, random.randint(100, 200), 0),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_cosmic_watcher(self, surface: pygame.Surface, size: int, anim: dict):
        """Render cosmic watcher with cosmic patterns."""
        # Body
        self._draw_shadow(surface, "circle", (50, 50, 100), size)
        pygame.draw.circle(surface, (50, 50, 100), (size//2, size//2), size//3)
        
        # Cosmic patterns
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw galaxy-like pattern
            points = []
            for j in range(5):
                pattern_angle = math.radians(j * 72 + math.sin(self._time * 2) * 10)
                points.append((
                    pattern_x + int(size//8 * math.cos(pattern_angle)),
                    pattern_y + int(size//8 * math.sin(pattern_angle))
                ))
            pygame.draw.polygon(surface, (100, 100, 255), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (100, 100, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (100, 100, 255), (0, 0, 0))
        
        # Cosmic particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_chronomancer(self, surface: pygame.Surface, size: int, anim: dict):
        """Render chronomancer with clock effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Clock face
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//2), size//4)
        
        # Clock hands
        hour_angle = math.radians((self._time * 30) % 360)
        minute_angle = math.radians((self._time * 360) % 360)
        
        # Hour hand
        hour_x = size//2 + int(size//6 * math.cos(hour_angle))
        hour_y = size//2 + int(size//6 * math.sin(hour_angle))
        pygame.draw.line(surface, (0, 0, 0),
                       (size//2, size//2), (hour_x, hour_y), 3)
        
        # Minute hand
        minute_x = size//2 + int(size//4 * math.cos(minute_angle))
        minute_y = size//2 + int(size//4 * math.sin(minute_angle))
        pygame.draw.line(surface, (0, 0, 0),
                       (size//2, size//2), (minute_x, minute_y), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Time particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 200),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_temporal_wraith(self, surface: pygame.Surface, size: int, anim: dict):
        """Render temporal wraith with time distortion effects."""
        # Body
        self._draw_shadow(surface, "circle", (50, 50, 50), size)
        pygame.draw.circle(surface, (50, 50, 50), (size//2, size//2), size//3)
        
        # Time distortion
        if random.random() < 0.2:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (100, 100, 100), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Time particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(100, 100, 100),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_hourglass_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render hourglass golem with sand effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 100), size)
        pygame.draw.circle(surface, (200, 200, 100), (size//2, size//2), size//3)
        
        # Hourglass shape
        pygame.draw.polygon(surface, (150, 150, 50), [
            (size//2 - size//4, size//2 - size//3),
            (size//2 + size//4, size//2 - size//3),
            (size//2 + size//6, size//2),
            (size//2 - size//6, size//2)
        ])
        pygame.draw.polygon(surface, (150, 150, 50), [
            (size//2 - size//4, size//2 + size//3),
            (size//2 + size//4, size//2 + size//3),
            (size//2 + size//6, size//2),
            (size//2 - size//6, size//2)
        ])
        
        # Sand particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(200, 200, 100),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        self._draw_particles(surface)

    def _render_future_seer(self, surface: pygame.Surface, size: int, anim: dict):
        """Render future seer with time vision effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 200), size)
        pygame.draw.circle(surface, (100, 100, 200), (size//2, size//2), size//3)
        
        # Vision orb
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//4)
        
        # Time patterns
        if random.random() < 0.2:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (200, 200, 255), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Vision particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(200, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_forest_nymph(self, surface: pygame.Surface, size: int, anim: dict):
        """Render forest nymph with leaf effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 150, 100), size)
        pygame.draw.circle(surface, (100, 150, 100), (size//2, size//2), size//3)
        
        # Leaf patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            leaf_x = size//2 + int(size//3 * math.cos(angle))
            leaf_y = size//2 + int(size//3 * math.sin(angle))
            # Draw leaf
            points = [
                (leaf_x, leaf_y),
                (leaf_x + size//8, leaf_y + size//8),
                (leaf_x, leaf_y + size//4),
                (leaf_x - size//8, leaf_y + size//8)
            ]
            pygame.draw.polygon(surface, (50, 100, 50), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Leaf particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(50, 100, 50),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_river_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render river spirit with flowing water effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 150, 255), size)
        pygame.draw.circle(surface, (100, 150, 255), (size//2, size//2), size//3)
        
        # Water waves
        if random.random() < 0.2:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (150, 200, 255), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Water particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 200, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_mountain_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mountain guardian with rocky features."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Rocky formations
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            rock_x = size//2 + int(size//3 * math.cos(angle))
            rock_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.polygon(surface, (150, 150, 150), [
                (rock_x, rock_y),
                (rock_x + size//8, rock_y + size//8),
                (rock_x, rock_y + size//4),
                (rock_x - size//8, rock_y + size//8)
            ])
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Rock particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 150, 150),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_wind_dancer(self, surface: pygame.Surface, size: int, anim: dict):
        """Render wind dancer with air effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Wind patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 255, 255), False, points, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Wind particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, 255, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_rune_golem(self, surface: pygame.Surface, size: int, anim: dict):
        """Render rune golem with glowing runes."""
        # Body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Runes
        rune_color = (255, 200, 0)
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            rune_x = size//2 + int(size//3 * math.cos(angle))
            rune_y = size//2 + int(size//3 * math.sin(angle))
            # Draw simple rune pattern
            pygame.draw.line(surface, rune_color,
                           (rune_x - size//16, rune_y - size//16),
                           (rune_x + size//16, rune_y + size//16), 2)
            pygame.draw.line(surface, rune_color,
                           (rune_x - size//16, rune_y + size//16),
                           (rune_x + size//16, rune_y - size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        
        # Rune particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=rune_color,
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_arcane_sentinel(self, surface: pygame.Surface, size: int, anim: dict):
        """Render arcane sentinel with magical patterns."""
        # Body
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        pygame.draw.circle(surface, (100, 0, 100), (size//2, size//2), size//3)
        
        # Magical patterns
        pattern_color = (200, 0, 200)
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw magical symbol
            pygame.draw.circle(surface, pattern_color,
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, pattern_color,
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, pattern_color,
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (200, 0, 200), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (200, 0, 200), (0, 0, 0))
        
        # Magical particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=pattern_color,
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_spell_weaver(self, surface: pygame.Surface, size: int, anim: dict):
        """Render spell weaver with magical effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 200), size)
        pygame.draw.circle(surface, (0, 100, 200), (size//2, size//2), size//3)
        
        # Spell patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (0, 200, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (0, 200, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 200, 255), (0, 0, 0))
        
        # Spell particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(0, 200, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_mana_elemental(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mana elemental with energy effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 100), size)
        pygame.draw.circle(surface, (0, 100, 100), (size//2, size//2), size//3)
        
        # Energy patterns
        if random.random() < 0.2:
            for i in range(6):
                angle = math.radians(i * 60 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (0, 200, 200), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (0, 200, 200), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 200, 200), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 200, 200), (0, 0, 0))
        
        # Energy particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(0, 200, 200),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_sand_wurm(self, surface: pygame.Surface, size: int, anim: dict):
        """Render sand wurm with sand effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 180, 100), size)
        pygame.draw.circle(surface, (200, 180, 100), (size//2, size//2), size//3)
        
        # Sand patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            sand_x = size//2 + int(size//3 * math.cos(angle))
            sand_y = size//2 + int(size//3 * math.sin(angle))
            # Draw sand ripple
            pygame.draw.arc(surface, (180, 160, 80),
                          (sand_x - size//8, sand_y - size//8,
                           size//4, size//4),
                          math.pi/4, math.pi*3/4, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Sand particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(200, 180, 100),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_mummy_lord(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mummy lord with bandage effects."""
        # Body
        self._draw_shadow(surface, "circle", (180, 160, 120), size)
        pygame.draw.circle(surface, (180, 160, 120), (size//2, size//2), size//3)
        
        # Bandage patterns
        for i in range(8):
            angle = math.radians(i * 45 + math.sin(self._time * 2) * 10)
            bandage_x = size//2 + int(size//3 * math.cos(angle))
            bandage_y = size//2 + int(size//3 * math.sin(angle))
            # Draw bandage
            pygame.draw.line(surface, (200, 180, 140),
                           (bandage_x - size//8, bandage_y),
                           (bandage_x + size//8, bandage_y), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        
        # Dust particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(180, 160, 120),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dust_djinn(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dust djinn with swirling dust effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 180, 150), size)
        pygame.draw.circle(surface, (200, 180, 150), (size//2, size//2), size//3)
        
        # Dust swirls
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (220, 200, 170), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (220, 200, 170), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Dust particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(220, 200, 170),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_scarab_swarm(self, surface: pygame.Surface, size: int, anim: dict):
        """Render scarab swarm with multiple scarab effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 100, 50), size)
        pygame.draw.circle(surface, (150, 100, 50), (size//2, size//2), size//3)
        
        # Scarab patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            scarab_x = size//2 + int(size//3 * math.cos(angle))
            scarab_y = size//2 + int(size//3 * math.sin(angle))
            # Draw scarab
            pygame.draw.ellipse(surface, (180, 130, 70),
                              (scarab_x - size//12, scarab_y - size//16,
                               size//6, size//8))
            # Draw wings
            pygame.draw.arc(surface, (200, 150, 100),
                          (scarab_x - size//8, scarab_y - size//8,
                           size//4, size//4),
                          math.pi/4, math.pi*3/4, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Swarm particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(180, 130, 70),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_rock_giant(self, surface: pygame.Surface, size: int, anim: dict):
        """Render rock giant with rocky features."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Rocky formations
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            rock_x = size//2 + int(size//3 * math.cos(angle))
            rock_y = size//2 + int(size//3 * math.sin(angle))
            # Draw rock formation
            pygame.draw.polygon(surface, (120, 120, 120), [
                (rock_x, rock_y),
                (rock_x + size//8, rock_y + size//8),
                (rock_x, rock_y + size//4),
                (rock_x - size//8, rock_y + size//8)
            ])
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Rock particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(120, 120, 120),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_harpy(self, surface: pygame.Surface, size: int, anim: dict):
        """Render harpy with feather effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 200), size)
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//2), size//3)
        
        # Feather patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            feather_x = size//2 + int(size//3 * math.cos(angle))
            feather_y = size//2 + int(size//3 * math.sin(angle))
            # Draw feather
            points = [
                (feather_x, feather_y),
                (feather_x + size//8, feather_y + size//8),
                (feather_x, feather_y + size//4),
                (feather_x - size//8, feather_y + size//8)
            ]
            pygame.draw.polygon(surface, (220, 220, 220), points)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Feather particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 220, 220),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
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
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
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

    def _render_thunder_bird(self, surface: pygame.Surface, size: int, anim: dict):
        """Render thunder bird with lightning effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 255), size)
        pygame.draw.circle(surface, (100, 100, 255), (size//2, size//2), size//3)
        
        # Lightning patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (150, 150, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (150, 150, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Lightning particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(150, 150, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_bog_witch(self, surface: pygame.Surface, size: int, anim: dict):
        """Render bog witch with swamp effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 150, 100), size)
        pygame.draw.circle(surface, (100, 150, 100), (size//2, size//2), size//3)
        
        # Swamp patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw swamp symbol
            pygame.draw.circle(surface, (120, 170, 120),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (120, 170, 120),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (120, 170, 120),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        
        # Swamp particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(120, 170, 120),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_hydra(self, surface: pygame.Surface, size: int, anim: dict):
        """Render hydra with multiple heads."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Hydra heads
        for i in range(3):
            angle = math.radians(i * 120 + math.sin(self._time * 2) * 10)
            head_x = size//2 + int(size//2 * math.cos(angle))
            head_y = size//2 + int(size//2 * math.sin(angle))
            # Draw head
            pygame.draw.circle(surface, (120, 120, 120),
                             (head_x, head_y), size//6)
            # Draw eyes
            self._draw_animated_eyes(surface, head_x, head_y, size//3,
                                   (255, 0, 0), (0, 0, 0))
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (120, 120, 120), (size//2, size//2), core_size)
        
        # Swamp particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(120, 120, 120),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_mushroom_zombie(self, surface: pygame.Surface, size: int, anim: dict):
        """Render mushroom zombie with fungal effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Mushroom cap
        pygame.draw.circle(surface, (200, 50, 50),
                         (size//2, size//2 - size//6), size//4)
        
        # Spore patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            spore_x = size//2 + int(size//3 * math.cos(angle))
            spore_y = size//2 + int(size//3 * math.sin(angle))
            pygame.draw.circle(surface, (200, 50, 50),
                             (spore_x, spore_y), size//16)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (0, 255, 0), (0, 0, 0))
        
        # Spore particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(200, 50, 50),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_will_o_wisp(self, surface: pygame.Surface, size: int, anim: dict):
        """Render will o wisp with ghostly light effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Light patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (220, 220, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (220, 220, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Light particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(220, 220, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_nightmare_weaver(self, surface: pygame.Surface, size: int, anim: dict):
        """Render nightmare weaver with dream distortion effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        pygame.draw.circle(surface, (100, 0, 100), (size//2, size//2), size//3)
        
        # Dream patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw dream symbol
            pygame.draw.circle(surface, (150, 0, 150),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (150, 0, 150),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (150, 0, 150),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 255), (0, 0, 0))
        
        # Dream particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 0, 150),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_dream_eater(self, surface: pygame.Surface, size: int, anim: dict):
        """Render dream eater with ethereal effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Ethereal patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (220, 220, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (220, 220, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Ethereal particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(220, 220, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_sleep_walker(self, surface: pygame.Surface, size: int, anim: dict):
        """Render sleep walker with dream trail effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 150, 200), size)
        pygame.draw.circle(surface, (150, 150, 200), (size//2, size//2), size//3)
        
        # Dream trail
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            trail_x = size//2 + int(size//3 * math.cos(angle))
            trail_y = size//2 + int(size//3 * math.sin(angle))
            # Draw dream trail
            pygame.draw.arc(surface, (180, 180, 220),
                          (trail_x - size//8, trail_y - size//8,
                           size//4, size//4),
                          math.pi/4, math.pi*3/4, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Dream trail particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(180, 180, 220),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_morpheus_spawn(self, surface: pygame.Surface, size: int, anim: dict):
        """Render morpheus spawn with dream realm effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 255), size)
        pygame.draw.circle(surface, (100, 100, 255), (size//2, size//2), size//3)
        
        # Dream realm patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw dream realm symbol
            pygame.draw.circle(surface, (150, 150, 255),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (150, 150, 255),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (150, 150, 255),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Dream realm particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 150, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_ancient_titan(self, surface: pygame.Surface, size: int, anim: dict):
        """Render ancient titan with primordial effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Primordial patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw primordial symbol
            pygame.draw.circle(surface, (120, 120, 120),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (120, 120, 120),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (120, 120, 120),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Primordial particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(120, 120, 120),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_primordial_wyrm(self, surface: pygame.Surface, size: int, anim: dict):
        """Render primordial wyrm with ancient effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 100, 50), size)
        pygame.draw.circle(surface, (150, 100, 50), (size//2, size//2), size//3)
        
        # Ancient patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw ancient symbol
            pygame.draw.circle(surface, (180, 130, 70),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (180, 130, 70),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (180, 130, 70),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Ancient particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(180, 130, 70),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_genesis_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render genesis spirit with creation effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 200), size)
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//2), size//3)
        
        # Creation patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw creation symbol
            pygame.draw.circle(surface, (220, 220, 220),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (220, 220, 220),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (220, 220, 220),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Creation particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 220, 220),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_eternal_flame(self, surface: pygame.Surface, size: int, anim: dict):
        """Render eternal flame with everlasting fire effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 100, 0), size)
        pygame.draw.circle(surface, (255, 100, 0), (size//2, size//2), size//3)
        
        # Fire patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 150, 0), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 150, 0), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Fire particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, 150, 0),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_schrodinger_beast(self, surface: pygame.Surface, size: int, anim: dict):
        """Render schrodinger beast with quantum superposition effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 255), size)
        pygame.draw.circle(surface, (100, 100, 255), (size//2, size//2), size//3)
        
        # Quantum patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (150, 150, 255), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (150, 150, 255), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Quantum particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(150, 150, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_quantum_shifter(self, surface: pygame.Surface, size: int, anim: dict):
        """Render quantum shifter with phase shift effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Phase patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw phase symbol
            pygame.draw.circle(surface, (220, 220, 255),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (220, 220, 255),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (220, 220, 255),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Phase particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 220, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_probability_weaver(self, surface: pygame.Surface, size: int, anim: dict):
        """Render probability weaver with wave function effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 150, 200), size)
        pygame.draw.circle(surface, (150, 150, 200), (size//2, size//2), size//3)
        
        # Wave patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            wave_x = size//2 + int(size//3 * math.cos(angle))
            wave_y = size//2 + int(size//3 * math.sin(angle))
            # Draw wave function
            pygame.draw.arc(surface, (180, 180, 220),
                          (wave_x - size//8, wave_y - size//8,
                           size//4, size//4),
                          math.pi/4, math.pi*3/4, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Wave particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(180, 180, 220),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_entangled_horror(self, surface: pygame.Surface, size: int, anim: dict):
        """Render entangled horror with quantum entanglement effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 0, 100), size)
        pygame.draw.circle(surface, (100, 0, 100), (size//2, size//2), size//3)
        
        # Entanglement patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw entanglement symbol
            pygame.draw.circle(surface, (150, 0, 150),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (150, 0, 150),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (150, 0, 150),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 0, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 0, 255), (0, 0, 0))
        
        # Entanglement particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 0, 150),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_chimera_lord(self, surface: pygame.Surface, size: int, anim: dict):
        """Render chimera lord with multiple creature effects."""
        # Body
        self._draw_shadow(surface, "circle", (150, 100, 50), size)
        pygame.draw.circle(surface, (150, 100, 50), (size//2, size//2), size//3)
        
        # Creature patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw creature symbol
            pygame.draw.circle(surface, (180, 130, 70),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (180, 130, 70),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (180, 130, 70),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Creature particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(180, 130, 70),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_world_serpent(self, surface: pygame.Surface, size: int, anim: dict):
        """Render world serpent with cosmic effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 100, 100), size)
        pygame.draw.circle(surface, (100, 100, 100), (size//2, size//2), size//3)
        
        # Cosmic patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw cosmic symbol
            pygame.draw.circle(surface, (120, 120, 120),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (120, 120, 120),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (120, 120, 120),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Cosmic particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(120, 120, 120),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_golden_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render golden guardian with divine effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 215, 0), size)
        pygame.draw.circle(surface, (255, 215, 0), (size//2, size//2), size//3)
        
        # Divine patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 255, 0), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 255, 0), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Divine particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, 255, 0),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_fate_sphinx(self, surface: pygame.Surface, size: int, anim: dict):
        """Render fate sphinx with destiny effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 200), size)
        pygame.draw.circle(surface, (200, 200, 200), (size//2, size//2), size//3)
        
        # Destiny patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw destiny symbol
            pygame.draw.circle(surface, (220, 220, 220),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (220, 220, 220),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (220, 220, 220),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Destiny particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 220, 220),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_fire_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render fire spirit with flame effects."""
        # Body
        self._draw_shadow(surface, "circle", (255, 100, 0), size)
        pygame.draw.circle(surface, (255, 100, 0), (size//2, size//2), size//3)
        
        # Flame patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
                    y = size//2 + int(size//2 * math.sin(angle + j * math.pi/6))
                    points.append((x, y))
                pygame.draw.lines(surface, (255, 150, 0), False, points, 2)
        
        # Core
        core_size = int(size//6 * (1 + math.sin(self._time * 3) * 0.1))
        pygame.draw.circle(surface, (255, 150, 0), (size//2, size//2), core_size)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 0), (0, 0, 0))
        
        # Flame particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(255, 150, 0),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_water_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render water spirit with wave effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 255), size)
        pygame.draw.circle(surface, (0, 100, 255), (size//2, size//2), size//3)
        
        # Wave patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            wave_x = size//2 + int(size//3 * math.cos(angle))
            wave_y = size//2 + int(size//3 * math.sin(angle))
            # Draw wave
            pygame.draw.arc(surface, (0, 150, 255),
                          (wave_x - size//8, wave_y - size//8,
                           size//4, size//4),
                          math.pi/4, math.pi*3/4, 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Wave particles
        if random.random() < 0.3:
            for _ in range(3):
                self._particles.append(Particle(
                    x=size//2, y=size//2,
                    dx=random.uniform(-1, 1),
                    dy=random.uniform(-1, 1),
                    color=(0, 150, 255),
                    life=random.uniform(0.3, 0.6),
                    size=random.uniform(1, 2)
                ))
        
        self._draw_particles(surface)

    def _render_earth_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render earth spirit with rock effects."""
        # Body
        self._draw_shadow(surface, "circle", (100, 50, 0), size)
        pygame.draw.circle(surface, (100, 50, 0), (size//2, size//2), size//3)
        
        # Rock patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw rock symbol
            pygame.draw.circle(surface, (150, 75, 0),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (150, 75, 0),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (150, 75, 0),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 200, 0), (0, 0, 0))
        
        # Rock particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(150, 75, 0),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_air_spirit(self, surface: pygame.Surface, size: int, anim: dict):
        """Render air spirit with wind effects."""
        # Body
        self._draw_shadow(surface, "circle", (200, 200, 255), size)
        pygame.draw.circle(surface, (200, 200, 255), (size//2, size//2), size//3)
        
        # Wind patterns
        for i in range(6):
            angle = math.radians(i * 60 + math.sin(self._time * 2) * 10)
            pattern_x = size//2 + int(size//3 * math.cos(angle))
            pattern_y = size//2 + int(size//3 * math.sin(angle))
            # Draw wind symbol
            pygame.draw.circle(surface, (220, 220, 255),
                             (pattern_x, pattern_y), size//16)
            pygame.draw.line(surface, (220, 220, 255),
                           (pattern_x - size//16, pattern_y),
                           (pattern_x + size//16, pattern_y), 2)
            pygame.draw.line(surface, (220, 220, 255),
                           (pattern_x, pattern_y - size//16),
                           (pattern_x, pattern_y + size//16), 2)
        
        # Eyes
        self._draw_animated_eyes(surface, size//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        self._draw_animated_eyes(surface, size*2//3, size//2, size,
                               (255, 255, 255), (0, 0, 0))
        
        # Wind particles
        if random.random() < 0.2:
            self._particles.append(Particle(
                x=size//2, y=size//2,
                dx=random.uniform(-1, 1),
                dy=random.uniform(-1, 1),
                color=(220, 220, 255),
                life=random.uniform(0.5, 1.0),
                size=random.uniform(1, 2)
            ))
        
        self._draw_particles(surface)

    def _render_forest_guardian(self, surface: pygame.Surface, size: int, anim: dict):
        """Render forest guardian with nature effects."""
        # Body
        self._draw_shadow(surface, "circle", (0, 100, 0), size)
        pygame.draw.circle(surface, (0, 100, 0), (size//2, size//2), size//3)
        
        # Nature patterns
        if random.random() < 0.3:
            for i in range(4):
                angle = math.radians(i * 90 + random.uniform(-10, 10))
                points = [(size//2, size//2)]
                for j in range(3):
                    x = size//2 + int(size//2 * math.cos(angle + j * math.pi/6))
# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = (1280, 800)  # Wider window
GRID_COLS = 7  # More columns
GRID_ROWS = 5  # Keep rows the same
ICON_SIZE = 160  # Slightly larger icons
PADDING = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
SCROLLBAR_COLOR = (100, 100, 100)
SCROLLBAR_HOVER_COLOR = (150, 150, 150)

# Create window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Monster Icon Test")

# List of monster types to display
monster_types = [
    # Original monsters
    "dragon", "spider", "ghost", "skeleton", "slime",
    # Psychic Anomalies
    "thought_devourer", "memory_phantom", "psychic_hydra", "mind_colossus",
    # Elemental creatures
    "fire_elemental", "ice_elemental", "storm_elemental", "earth_golem",
    # Undead
    "zombie", "wraith", "vampire", "lich",
    # Magical creatures
    "pixie", "phoenix", "unicorn", "griffin",
    # Forest creatures
    "treant", "wolf", "bear", "dryad",
    # Dark creatures
    "demon", "shadow_stalker", "nightmare", "dark_wizard",
    # Aquatic creatures
    "kraken", "mermaid", "leviathan", "siren",
    # Insectoids
    "mantis", "beetle", "scorpion", "wasp",
    # Mechanical
    "clockwork_golem", "automaton", "steam_knight", "tesla_guardian",
    # Crystal
    "crystal_golem", "prism_elemental", "geode_guardian", "diamond_sentinel",
    # Fungi
    "myconid", "spore_beast", "mold_horror", "fungal_colossus",
    # Shadow
    "void_walker", "shade", "dark_phantom", "umbra_beast",
    # Celestial
    "star_seraph", "moon_guardian", "solar_phoenix", "cosmic_watcher",
    # Time
    "chronomancer", "temporal_wraith", "hourglass_golem", "future_seer",
    # Nature
    "forest_nymph", "river_spirit", "mountain_guardian", "wind_dancer",
    # Arcane
    "rune_golem", "arcane_sentinel", "spell_weaver", "mana_elemental",
    # Desert
    "sand_wurm", "mummy_lord", "dust_djinn", "scarab_swarm",
    # Mountain
    "rock_giant", "harpy", "frost_titan", "thunder_bird",
    # Swamp
    "bog_witch", "hydra", "mushroom_zombie", "will_o_wisp",
    # Dream
    "nightmare_weaver", "dream_eater", "sleep_walker", "morpheus_spawn",
    # Primal
    "ancient_titan", "primordial_wyrm", "genesis_spirit", "eternal_flame",
    # Quantum
    "schrodinger_beast", "quantum_shifter", "probability_weaver", "entangled_horror",
    # Mythic
    "chimera_lord", "world_serpent", "golden_guardian", "fate_sphinx"
]

# Create monster icons
monster_icons = {monster_type: MonsterIcon(monster_type) for monster_type in monster_types}

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Scroll state
scroll_y = 0
scroll_speed = 20
scrollbar_width = 20
scrollbar_height = 100
scrollbar_dragging = False
scrollbar_y = 0

def draw_grid():
    """Draw the grid of monster icons."""
    screen.fill(GRAY)
    
    # Calculate total content height
    total_rows = (len(monster_types) + GRID_COLS - 1) // GRID_COLS
    content_height = total_rows * (ICON_SIZE + PADDING) + PADDING
    
    # Calculate visible area
    visible_height = WINDOW_SIZE[1]
    
    # Draw grid
    for i, monster_type in enumerate(monster_types):
        row = i // GRID_COLS
        col = i % GRID_COLS
        
        # Calculate position
        x = col * (ICON_SIZE + PADDING) + PADDING
        y = row * (ICON_SIZE + PADDING) + PADDING - scroll_y
        
        # Only draw if visible
        if y + ICON_SIZE > 0 and y < visible_height:
            # Create surface for icon
            icon_surface = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
            
            # Draw icon
            monster_icons[monster_type].render(icon_surface, ICON_SIZE)
            
            # Draw icon to screen
            screen.blit(icon_surface, (x, y))
            
            # Draw monster type name
            font = pygame.font.Font(None, 24)
            text = font.render(monster_type.replace('_', ' ').title(), True, WHITE)
            text_rect = text.get_rect(center=(x + ICON_SIZE//2, y + ICON_SIZE + 15))
            screen.blit(text, text_rect)
    
    # Draw scrollbar
    if content_height > visible_height:
        # Calculate scrollbar position and size
        scrollbar_x = WINDOW_SIZE[0] - scrollbar_width
        scrollbar_height = max(50, int(visible_height * (visible_height / content_height)))
        scrollbar_y = int((scroll_y / (content_height - visible_height)) * (visible_height - scrollbar_height))
        
        # Draw scrollbar track
        pygame.draw.rect(screen, SCROLLBAR_COLOR, 
                        (scrollbar_x, 0, scrollbar_width, visible_height))
        
        # Draw scrollbar thumb
        pygame.draw.rect(screen, SCROLLBAR_HOVER_COLOR if scrollbar_dragging else SCROLLBAR_COLOR,
                        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))

def main():
    global scroll_y, scrollbar_dragging
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.key == pygame.K_DOWN:
                    total_rows = (len(monster_types) + GRID_COLS - 1) // GRID_COLS
                    content_height = total_rows * (ICON_SIZE + PADDING) + PADDING
                    max_scroll = max(0, content_height - WINDOW_SIZE[1])
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.button == 5:  # Scroll down
                    total_rows = (len(monster_types) + GRID_COLS - 1) // GRID_COLS
                    content_height = total_rows * (ICON_SIZE + PADDING) + PADDING
                    max_scroll = max(0, content_height - WINDOW_SIZE[1])
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
                elif event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if mouse_x >= WINDOW_SIZE[0] - scrollbar_width:
                        scrollbar_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    scrollbar_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if scrollbar_dragging:
                    mouse_y = event.pos[1]
                    total_rows = (len(monster_types) + GRID_COLS - 1) // GRID_COLS
                    content_height = total_rows * (ICON_SIZE + PADDING) + PADDING
                    visible_height = WINDOW_SIZE[1]
                    scrollbar_height = max(50, int(visible_height * (visible_height / content_height)))
                    scroll_y = int((mouse_y / (visible_height - scrollbar_height)) * (content_height - visible_height))
                    scroll_y = max(0, min(scroll_y, content_height - visible_height))
        
        # Update icons
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        for icon in monster_icons.values():
            icon.update(dt)
        
        # Draw everything
        draw_grid()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 