"""
Base classes for the quest system.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from ..items import Item
import pygame
import math

class QuestStatus(Enum):
    """Possible states of a quest."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TURNED_IN = auto()

class QuestType(Enum):
    """Types of quests available in the game."""
    MAIN = auto()      # Main story quests
    SIDE = auto()      # Optional side quests
    DAILY = auto()     # Daily repeatable quests
    WORLD = auto()     # World events/quests
    HIDDEN = auto()    # Secret/hidden quests

class QuestDifficulty(Enum):
    """Difficulty levels for quests."""
    TRIVIAL = auto()    # Very easy, good for new players
    EASY = auto()       # Standard difficulty
    MEDIUM = auto()     # Challenging but doable
    HARD = auto()       # Difficult, requires preparation
    EPIC = auto()       # Very challenging, requires a group or high level

@dataclass
class QuestObjective(ABC):
    """Base class for quest objectives."""
    description: str = field(init=False)
    required_progress: int = field(init=False)
    quest: Optional['Quest'] = field(default=None, init=False)  # Reference to parent quest
    marker_color: Tuple[int, int, int] = field(default=(255, 255, 0), init=False)  # Default yellow
    marker_shape: str = field(default="circle", init=False)  # circle, square, triangle
    marker_size: int = field(default=8, init=False)
    tooltip_text: str = field(default="", init=False)  # Text to show in tooltip
    icon: str = field(default="", init=False)  # Icon to display
    current_progress: int = field(default=0, init=False)
    completed: bool = field(default=False, init=False)
    tooltip_alpha: int = field(default=0, init=False)  # For fade animation
    tooltip_scale: float = field(default=0.8, init=False)  # For scale animation

    @abstractmethod
    def check_progress(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if an event contributes to the objective's progress.
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            bool: True if progress was made, False otherwise
        """
        pass

    def update_progress(self, amount: int = 1) -> bool:
        """
        Update the objective's progress.
        
        Args:
            amount: Amount to increase progress by
            
        Returns:
            bool: True if objective was completed by this update
        """
        if self.completed:
            return False
            
        self.current_progress = min(self.current_progress + amount, self.required_progress)
        if self.current_progress >= self.required_progress:
            self.completed = True
            return True
        return False

    def draw_marker(self, screen: pygame.Surface, x: int, y: int):
        """
        Draw the objective's marker on the screen.
        
        Args:
            screen: The pygame surface to draw on
            x: Screen x coordinate
            y: Screen y coordinate
        """
        if self.marker_shape == "circle":
            pygame.draw.circle(screen, self.marker_color, (x, y), self.marker_size)
        elif self.marker_shape == "square":
            rect = pygame.Rect(x - self.marker_size, y - self.marker_size, 
                             self.marker_size * 2, self.marker_size * 2)
            pygame.draw.rect(screen, self.marker_color, rect)
        elif self.marker_shape == "triangle":
            points = [
                (x, y - self.marker_size),  # Top point
                (x - self.marker_size, y + self.marker_size),  # Bottom left
                (x + self.marker_size, y + self.marker_size)   # Bottom right
            ]
            pygame.draw.polygon(screen, self.marker_color, points)

    def get_tooltip(self) -> str:
        """Get the tooltip text for this objective."""
        if not self.quest:
            return self.tooltip_text or f"{self.description}\nProgress: {self.current_progress}/{self.required_progress}"
            
        # Build detailed tooltip
        tooltip_lines = [
            f"Quest: {self.quest.title}",
            f"Level: {self.quest.level_requirement}",
            f"Difficulty: {self.quest.difficulty.name}",
            "",
            f"Objective: {self.description}",
            f"Progress: {self.current_progress}/{self.required_progress}",
            "",
            "Rewards:"
        ]
        
        # Add rewards
        for reward in self.quest.rewards:
            tooltip_lines.append(f"- {reward.description}")
            
        return "\n".join(tooltip_lines)

    def is_mouse_over(self, mouse_pos: Tuple[int, int], marker_pos: Tuple[int, int]) -> bool:
        """
        Check if the mouse is over this marker.
        
        Args:
            mouse_pos: Current mouse position (x, y)
            marker_pos: Marker position (x, y)
            
        Returns:
            bool: True if mouse is over the marker
        """
        mx, my = mouse_pos
        x, y = marker_pos
        
        if self.marker_shape == "circle":
            distance = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5
            return distance <= self.marker_size
        elif self.marker_shape == "square":
            return (abs(mx - x) <= self.marker_size and 
                   abs(my - y) <= self.marker_size)
        elif self.marker_shape == "triangle":
            # Simple bounding box check for triangle
            return (abs(mx - x) <= self.marker_size and 
                   abs(my - y) <= self.marker_size)
        elif self.marker_shape == "diamond":
            # Simple bounding box check for diamond
            return (abs(mx - x) <= self.marker_size and 
                   abs(my - y) <= self.marker_size)
        return False

    def update_tooltip_animation(self, dt: float):
        """Update tooltip animation state."""
        if self.is_mouse_over(pygame.mouse.get_pos(), self.last_marker_pos):
            # Fade in and scale up
            self.tooltip_alpha = min(255, self.tooltip_alpha + int(500 * dt))
            self.tooltip_scale = min(1.0, self.tooltip_scale + 2.0 * dt)
        else:
            # Fade out and scale down
            self.tooltip_alpha = max(0, self.tooltip_alpha - int(500 * dt))
            self.tooltip_scale = max(0.8, self.tooltip_scale - 2.0 * dt)

    def draw_tooltip(self, screen: pygame.Surface, mouse_pos: Tuple[int, int], marker_pos: Tuple[int, int]):
        """
        Draw the tooltip if mouse is over the marker.
        
        Args:
            screen: The pygame surface to draw on
            mouse_pos: Current mouse position
            marker_pos: Marker position
        """
        self.last_marker_pos = marker_pos
        if not self.is_mouse_over(mouse_pos, marker_pos) and self.tooltip_alpha == 0:
            return
            
        # Get tooltip text
        text = self.get_tooltip()
        if not text:
            return
            
        # Create font
        font = pygame.font.Font(None, 24)
        
        # Split text into lines and render each line
        lines = text.split('\n')
        line_height = font.get_linesize()
        total_height = len(lines) * line_height
        max_width = max(font.size(line)[0] for line in lines)
        
        # Calculate tooltip position
        text_rect = pygame.Rect(0, 0, max_width, total_height)
        
        # Position tooltip to avoid screen edges
        screen_width, screen_height = screen.get_size()
        if marker_pos[0] + max_width//2 > screen_width:
            text_rect.right = marker_pos[0] - self.marker_size - 5
        else:
            text_rect.left = marker_pos[0] + self.marker_size + 5
            
        if marker_pos[1] - total_height < 0:
            text_rect.top = marker_pos[1] + self.marker_size + 5
        else:
            text_rect.bottom = marker_pos[1] - self.marker_size - 5
        
        # Create tooltip surface with alpha
        tooltip_surface = pygame.Surface((max_width + 40, total_height + 40), pygame.SRCALPHA)
        
        # Draw background with alpha
        bg_rect = pygame.Rect(0, 0, max_width + 40, total_height + 40)
        pygame.draw.rect(tooltip_surface, (0, 0, 0, self.tooltip_alpha), bg_rect)
        pygame.draw.rect(tooltip_surface, (255, 255, 255, self.tooltip_alpha), bg_rect, 1)
        
        # Draw each line of text
        y = 20
        for line in lines:
            if line.startswith("Quest:"):
                text_surface = font.render(line, True, (255, 255, 0, self.tooltip_alpha))
            elif line.startswith("Level:"):
                text_surface = font.render(line, True, (0, 255, 0, self.tooltip_alpha))
            elif line.startswith("Difficulty:"):
                color = self.quest.get_difficulty_color() if self.quest else (255, 255, 255)
                text_surface = font.render(line, True, (*color, self.tooltip_alpha))
            elif line.startswith("Rewards:"):
                text_surface = font.render(line, True, (255, 215, 0, self.tooltip_alpha))
            elif line.startswith("-"):
                # Draw reward icon and text
                icon_size = 16
                icon = self.quest.rewards[len([l for l in lines[:lines.index(line)] if l.startswith("-")])].get_icon_surface(icon_size)
                tooltip_surface.blit(icon, (20, y))
                text_surface = font.render(line, True, (255, 255, 255, self.tooltip_alpha))
                text_rect = text_surface.get_rect()
                text_rect.left = 20 + icon_size + 5
                text_rect.top = y
                tooltip_surface.blit(text_surface, text_rect)
                y += line_height
                continue
            else:
                text_surface = font.render(line, True, (255, 255, 255, self.tooltip_alpha))
                
            text_rect = text_surface.get_rect()
            text_rect.centerx = tooltip_surface.get_width() // 2
            text_rect.top = y
            tooltip_surface.blit(text_surface, text_rect)
            y += line_height
            
        # Scale and draw the tooltip
        if self.tooltip_scale != 1.0:
            scaled_size = (int(tooltip_surface.get_width() * self.tooltip_scale),
                         int(tooltip_surface.get_height() * self.tooltip_scale))
            tooltip_surface = pygame.transform.scale(tooltip_surface, scaled_size)
            
        screen.blit(tooltip_surface, text_rect)

@dataclass
class QuestReward(ABC):
    """Base class for quest rewards."""
    description: str = field(default="")
    icon: str = field(default="")
    icon_color: Tuple[int, int, int] = field(default=(255, 255, 255))

    @abstractmethod
    def grant(self, player) -> bool:
        """
        Grant the reward to the player.
        
        Args:
            player: The player to receive the reward
            
        Returns:
            bool: True if reward was granted successfully
        """
        pass

    def get_icon_surface(self, size: int = 16) -> pygame.Surface:
        """
        Get the icon surface for this reward.
        
        Args:
            size: Size of the icon in pixels
            
        Returns:
            pygame.Surface: The icon surface
        """
        # Create a surface for the icon
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Get animation time for pulsing effects
        time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        pulse = (math.sin(time * 2) + 1) / 2  # 0 to 1
        rotation = time * 45  # 45 degrees per second
        
        def draw_shadow(surface, shape, color, offset=(1, 1), alpha=64):
            """Draw a shadow for the given shape."""
            shadow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            if shape == "circle":
                pygame.draw.circle(shadow_surface, (*color[:3], alpha), 
                                 (size//2 + offset[0], size//2 + offset[1]), size//2)
            elif shape == "rect":
                pygame.draw.rect(shadow_surface, (*color[:3], alpha),
                               (size//4 + offset[0], size//4 + offset[1], size//2, size//2))
            surface.blit(shadow_surface, (0, 0))
            
        def draw_highlight(surface, shape, color, offset=(-1, -1), alpha=128):
            """Draw a highlight for the given shape."""
            highlight_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            if shape == "circle":
                pygame.draw.circle(highlight_surface, (*color[:3], alpha),
                                 (size//2 + offset[0], size//2 + offset[1]), size//4)
            elif shape == "rect":
                pygame.draw.rect(highlight_surface, (*color[:3], alpha),
                               (size//4 + offset[0], size//4 + offset[1], size//4, size//4))
            surface.blit(highlight_surface, (0, 0))
            
        def draw_monster(surface, monster_type: str, color: Tuple[int, int, int]):
            """Draw a monster icon based on type."""
            if monster_type == "dragon":
                # Dragon head
                draw_shadow(surface, "circle", color)
                pygame.draw.circle(surface, color, (size//2, size//2), size//3)
                # Horns
                points = [
                    (size//4, size//3),
                    (size//2, size//4),
                    (size*3//4, size//3)
                ]
                pygame.draw.polygon(surface, color, points)
                # Eyes
                pygame.draw.circle(surface, (255, 0, 0), (size//3, size//2), size//8)
                pygame.draw.circle(surface, (255, 0, 0), (size*2//3, size//2), size//8)
                # Fire breath animation
                if pulse > 0.5:
                    flame_points = [
                        (size//2, size*2//3),
                        (size//3, size*3//4),
                        (size//2, size*4//5),
                        (size*2//3, size*3//4)
                    ]
                    flame_color = (255, int(100 + 155 * pulse), 0)
                    pygame.draw.polygon(surface, flame_color, flame_points)
                    
            elif monster_type == "goblin":
                # Goblin head
                draw_shadow(surface, "circle", color)
                pygame.draw.circle(surface, color, (size//2, size//2), size//3)
                # Ears
                pygame.draw.circle(surface, color, (size//4, size//3), size//6)
                pygame.draw.circle(surface, color, (size*3//4, size//3), size//6)
                # Eyes
                pygame.draw.circle(surface, (0, 0, 0), (size//3, size//2), size//8)
                pygame.draw.circle(surface, (0, 0, 0), (size*2//3, size//2), size//8)
                # Teeth
                pygame.draw.rect(surface, (255, 255, 255), (size//3, size*2//3, size//3, size//6))
                
            elif monster_type == "skeleton":
                # Skull
                draw_shadow(surface, "circle", color)
                pygame.draw.circle(surface, color, (size//2, size//2), size//3)
                # Eye sockets
                pygame.draw.circle(surface, (0, 0, 0), (size//3, size//2), size//8)
                pygame.draw.circle(surface, (0, 0, 0), (size*2//3, size//2), size//8)
                # Jaw
                points = [
                    (size//3, size*2//3),
                    (size//2, size*3//4),
                    (size*2//3, size*2//3)
                ]
                pygame.draw.polygon(surface, color, points)
                # Glowing eyes animation
                if pulse > 0.5:
                    pygame.draw.circle(surface, (255, 255, 255, int(255 * pulse)), 
                                     (size//3, size//2), size//10)
                    pygame.draw.circle(surface, (255, 255, 255, int(255 * pulse)), 
                                     (size*2//3, size//2), size//10)
                    
            elif monster_type == "slime":
                # Slime body
                draw_shadow(surface, "circle", color)
                pygame.draw.ellipse(surface, color, (size//4, size//3, size//2, size//2))
                # Eyes
                pygame.draw.circle(surface, (255, 255, 255), (size//3, size//2), size//8)
                pygame.draw.circle(surface, (255, 255, 255), (size*2//3, size//2), size//8)
                pygame.draw.circle(surface, (0, 0, 0), (size//3, size//2), size//12)
                pygame.draw.circle(surface, (0, 0, 0), (size*2//3, size//2), size//12)
                # Bounce animation
                bounce_offset = int(2 * math.sin(time * 4))
                surface.blit(surface, (0, bounce_offset))
                
        # Draw different icons based on reward type
        if self.icon == "gold":
            # Gold coin with shine
            draw_shadow(surface, "circle", (255, 215, 0))
            pygame.draw.circle(surface, (255, 215, 0), (size//2, size//2), size//2)
            pygame.draw.circle(surface, (255, 255, 0), (size//2, size//2), size//3)
            # Rotating shine effect
            shine_angle = math.radians(rotation)
            shine_x = size//2 + int(size//3 * math.cos(shine_angle))
            shine_y = size//2 + int(size//3 * math.sin(shine_angle))
            draw_highlight(surface, "circle", (255, 255, 255, int(128 * pulse)), 
                         (shine_x - size//2, shine_y - size//2))
            
        elif self.icon == "item":
            # Item icon (chest with lid)
            draw_shadow(surface, "rect", self.icon_color)
            # Base
            pygame.draw.rect(surface, self.icon_color, (size//4, size//2, size//2, size//3))
            # Lid
            pygame.draw.rect(surface, self.icon_color, (size//4, size//3, size//2, size//6))
            # Lock
            pygame.draw.circle(surface, (255, 215, 0), (size//2, size//2), size//8)
            # Outline
            pygame.draw.rect(surface, (0, 0, 0), (size//4, size//2, size//2, size//3), 1)
            pygame.draw.rect(surface, (0, 0, 0), (size//4, size//3, size//2, size//6), 1)
            # Pulsing glow
            if pulse > 0.5:
                glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*self.icon_color[:3], int(64 * pulse)), 
                               (size//4, size//2, size//2, size//3))
                surface.blit(glow_surface, (0, 0))
            
        elif self.icon == "exp":
            # Experience icon (shining star)
            draw_shadow(surface, "circle", (0, 255, 0))
            # Star points
            points = []
            for i in range(5):
                angle = math.radians(72 * i + rotation)
                x = size//2 + int(size//2 * math.cos(angle))
                y = size//2 + int(size//2 * math.sin(angle))
                points.append((x, y))
            pygame.draw.polygon(surface, (0, 255, 0), points)
            # Inner star
            inner_points = []
            for i in range(5):
                angle = math.radians(72 * i + rotation + 36)
                x = size//2 + int(size//3 * math.cos(angle))
                y = size//2 + int(size//3 * math.sin(angle))
                inner_points.append((x, y))
            pygame.draw.polygon(surface, (0, 200, 0), inner_points)
            # Pulsing shine effect
            if pulse > 0.5:
                draw_highlight(surface, "circle", (255, 255, 255, int(128 * pulse)))
            
        elif self.icon.startswith("monster_"):
            # Monster icons with type
            monster_type = self.icon.split("_")[1]
            monster_color = {
                "dragon": (255, 0, 0),
                "goblin": (0, 255, 0),
                "skeleton": (200, 200, 200),
                "slime": (0, 255, 255)
            }.get(monster_type, (255, 255, 255))
            draw_monster(surface, monster_type, monster_color)
            
        else:
            # Default icon (circle with pattern)
            draw_shadow(surface, "circle", self.icon_color)
            pygame.draw.circle(surface, self.icon_color, (size//2, size//2), size//2)
            # Add a rotating pattern
            angle = math.radians(rotation)
            x1 = size//2 + int(size//3 * math.cos(angle))
            y1 = size//2 + int(size//3 * math.sin(angle))
            x2 = size//2 - int(size//3 * math.cos(angle))
            y2 = size//2 - int(size//3 * math.sin(angle))
            pygame.draw.line(surface, (0, 0, 0), (x1, y1), (x2, y2), 1)
            
        return surface

@dataclass
class Quest:
    """Represents a quest in the game."""
    id: str
    title: str
    description: str
    quest_type: QuestType
    level_requirement: int = 1
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: List[QuestReward] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    status: QuestStatus = QuestStatus.NOT_STARTED
    difficulty: QuestDifficulty = QuestDifficulty.EASY
    
    # Optional quest properties
    giver_id: Optional[str] = None
    turn_in_id: Optional[str] = None
    time_limit: Optional[int] = None
    expiry_time: Optional[float] = None
    chain_id: Optional[str] = None
    chain_position: Optional[int] = None
    next_quest_id: Optional[str] = None
    
    # Location properties
    location_id: Optional[str] = None
    location_coords: Optional[Tuple[int, int]] = None
    location_radius: int = 5  # Default radius for objective area
    
    def __post_init__(self):
        """Set quest reference for all objectives after initialization."""
        if not self.objectives:
            self.objectives = []
        if not self.rewards:
            self.rewards = []
        if not self.prerequisites:
            self.prerequisites = []
            
        for objective in self.objectives:
            objective.quest = self
            
    def is_available(self, player) -> bool:
        """Check if the quest is available to the player."""
        if self.status != QuestStatus.NOT_STARTED:
            return False
            
        if player.level < self.level_requirement:
            return False
            
        # Check prerequisites
        for quest_id in self.prerequisites:
            prereq_quest = player.quest_log.get_quest(quest_id)
            if not prereq_quest or prereq_quest.status != QuestStatus.TURNED_IN:
                return False
                
        return True
        
    def start(self) -> bool:
        """Start the quest if it's available."""
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.IN_PROGRESS
            return True
        return False
        
    def update_objectives(self, event_data: Dict[str, Any]) -> bool:
        """Update quest objectives based on an event."""
        if self.status != QuestStatus.IN_PROGRESS:
            return False
            
        updated = False
        for objective in self.objectives:
            if objective.check_progress(event_data):
                updated = True
                
        # Check if all objectives are complete
        if all(obj.is_complete() for obj in self.objectives):
            self.status = QuestStatus.COMPLETED
            
        return updated
        
    def turn_in(self, player) -> bool:
        """Turn in the quest and grant rewards."""
        if self.status != QuestStatus.COMPLETED:
            return False
            
        # Grant all rewards
        for reward in self.rewards:
            reward.grant(player)
            
        self.status = QuestStatus.TURNED_IN
        return True
        
    def get_navigation_hint(self, player_pos: Tuple[int, int], quest_navigation) -> str:
        """Get a navigation hint for the quest's location."""
        if not self.location_id:
            return "No location specified"
            
        return quest_navigation.get_navigation_hint(player_pos, self.location_id)
        
    def get_objective_markers(self, quest_navigation) -> List[Tuple[int, int]]:
        """Get markers for all objectives in the quest."""
        markers = []
        for objective in self.objectives:
            if isinstance(objective, ExploreObjective):
                markers.extend(objective.get_markers(quest_navigation))
        return markers
        
    def get_difficulty_color(self) -> Tuple[int, int, int]:
        """Get the color associated with this quest's difficulty."""
        return {
            QuestDifficulty.TRIVIAL: (128, 128, 128),  # Gray
            QuestDifficulty.EASY: (0, 255, 0),         # Green
            QuestDifficulty.MEDIUM: (255, 255, 0),     # Yellow
            QuestDifficulty.HARD: (255, 128, 0),       # Orange
            QuestDifficulty.EPIC: (255, 0, 0)          # Red
        }[self.difficulty]
        
    def get_completion_percentage(self) -> float:
        """Get the overall completion percentage of the quest."""
        if not self.objectives:
            return 0.0
            
        total_progress = sum(obj.current_progress for obj in self.objectives)
        total_required = sum(obj.required_progress for obj in self.objectives)
        return (total_progress / total_required) * 100 if total_required > 0 else 0.0 