"""
Quest UI module for displaying and managing quests.
"""

import pygame
from typing import List, Dict, Optional, Tuple
from ..quests.base import Quest, QuestType, QuestDifficulty, QuestObjective, QuestReward
from ..utils.colors import *
from ..utils.fonts import get_font
from ..utils.ui import draw_text, draw_rect_with_border

class QuestUI:
    """UI component for displaying and managing quests."""
    
    # Constants for UI layout
    PANEL_WIDTH = 800
    PANEL_HEIGHT = 600
    QUEST_LIST_WIDTH = 300
    QUEST_LIST_HEIGHT = 500
    QUEST_ITEM_HEIGHT = 60
    TAB_HEIGHT = 40
    PADDING = 10
    SCROLL_SPEED = 20
    
    # Colors for different quest difficulties
    DIFFICULTY_COLORS = {
        QuestDifficulty.TRIVIAL: GRAY,
        QuestDifficulty.EASY: GREEN,
        QuestDifficulty.MEDIUM: BLUE,
        QuestDifficulty.HARD: PURPLE,
        QuestDifficulty.EPIC: GOLD
    }
    
    def __init__(self, screen: pygame.Surface, quest_log):
        """Initialize the quest UI."""
        self.screen = screen
        self.quest_log = quest_log
        self.visible = False
        self.selected_tab = QuestType.MAIN
        self.selected_quest: Optional[Quest] = None
        self.hovered_quest: Optional[Quest] = None
        self.scroll_offset = 0
        self.max_scroll = 0
        self.font = get_font(16)
        self.title_font = get_font(20)
        self.small_font = get_font(14)
        
        # Calculate positions
        screen_width, screen_height = screen.get_size()
        self.x = (screen_width - self.PANEL_WIDTH) // 2
        self.y = (screen_height - self.PANEL_HEIGHT) // 2
        
        # Quest list panel
        self.quest_list_x = self.x + self.PADDING
        self.quest_list_y = self.y + self.TAB_HEIGHT + self.PADDING
        
        # Details panel
        self.details_x = self.quest_list_x + self.QUEST_LIST_WIDTH + self.PADDING
        self.details_y = self.quest_list_y
        self.details_width = self.PANEL_WIDTH - self.QUEST_LIST_WIDTH - self.PADDING * 3
        self.details_height = self.QUEST_LIST_HEIGHT
    
    def toggle(self):
        """Toggle the visibility of the quest UI."""
        self.visible = not self.visible
        if self.visible:
            self.update_scroll_limits()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check for tab clicks
            tab_y = self.y + self.PADDING
            tab_width = self.QUEST_LIST_WIDTH // 3
            for i, quest_type in enumerate(QuestType):
                tab_x = self.quest_list_x + i * tab_width
                if tab_x <= mouse_x < tab_x + tab_width and tab_y <= mouse_y < tab_y + self.TAB_HEIGHT:
                    self.selected_tab = quest_type
                    self.scroll_offset = 0
                    self.update_scroll_limits()
                    return True
            
            # Check for quest list clicks
            if (self.quest_list_x <= mouse_x < self.quest_list_x + self.QUEST_LIST_WIDTH and
                self.quest_list_y <= mouse_y < self.quest_list_y + self.QUEST_LIST_HEIGHT):
                clicked_index = (mouse_y - self.quest_list_y + self.scroll_offset) // self.QUEST_ITEM_HEIGHT
                quests = self.quest_log.get_quests_by_type(self.selected_tab)
                if 0 <= clicked_index < len(quests):
                    self.selected_quest = quests[clicked_index]
                    return True
            
            # Check for scroll wheel
            if event.button in (4, 5):  # 4 is scroll up, 5 is scroll down
                scroll_amount = -self.SCROLL_SPEED if event.button == 4 else self.SCROLL_SPEED
                self.scroll_offset = max(0, min(self.scroll_offset + scroll_amount, self.max_scroll))
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Update hovered quest
            if (self.quest_list_x <= mouse_x < self.quest_list_x + self.QUEST_LIST_WIDTH and
                self.quest_list_y <= mouse_y < self.quest_list_y + self.QUEST_LIST_HEIGHT):
                hovered_index = (mouse_y - self.quest_list_y + self.scroll_offset) // self.QUEST_ITEM_HEIGHT
                quests = self.quest_log.get_quests_by_type(self.selected_tab)
                self.hovered_quest = quests[hovered_index] if 0 <= hovered_index < len(quests) else None
            else:
                self.hovered_quest = None
        
        return False
    
    def update(self):
        """Update the quest UI state."""
        if not self.visible:
            return
        
        # Update scroll limits
        self.update_scroll_limits()
    
    def update_scroll_limits(self):
        """Update the maximum scroll offset based on quest list content."""
        quests = self.quest_log.get_quests_by_type(self.selected_tab)
        content_height = len(quests) * self.QUEST_ITEM_HEIGHT
        self.max_scroll = max(0, content_height - self.QUEST_LIST_HEIGHT)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)
    
    def draw(self, screen: pygame.Surface):
        """Draw the quest UI."""
        if not self.visible:
            return
        
        # Draw main panel background
        draw_rect_with_border(
            screen,  # Use the passed screen
            (self.x, self.y, self.PANEL_WIDTH, self.PANEL_HEIGHT),
            DARK_GRAY,
            WHITE
        )
        
        # Draw tabs
        self._draw_tabs()
        
        # Draw quest list panel
        draw_rect_with_border(
            screen,  # Use the passed screen
            (self.quest_list_x, self.quest_list_y, self.QUEST_LIST_WIDTH, self.QUEST_LIST_HEIGHT),
            BLACK,
            WHITE
        )
        
        # Draw quest list
        self._draw_quest_list()
        
        # Draw details panel
        draw_rect_with_border(
            screen,  # Use the passed screen
            (self.details_x, self.details_y, self.details_width, self.details_height),
            BLACK,
            WHITE
        )
        
        # Draw quest details if a quest is selected
        if self.selected_quest:
            self._draw_quest_details()
    
    def _draw_tabs(self):
        """Draw quest type tabs."""
        tab_width = self.QUEST_LIST_WIDTH // 3
        tab_y = self.y + self.PADDING
        
        for i, quest_type in enumerate(QuestType):
            tab_x = self.quest_list_x + i * tab_width
            tab_color = LIGHT_GRAY if quest_type == self.selected_tab else DARK_GRAY
            
            # Draw tab background
            draw_rect_with_border(
                self.screen,
                (tab_x, tab_y, tab_width, self.TAB_HEIGHT),
                tab_color,
                WHITE
            )
            
            # Draw tab text
            quests = self.quest_log.get_quests_by_type(quest_type)
            tab_text = f"{quest_type.name} ({len(quests)})"
            draw_text(
                self.screen,
                tab_text,
                self.small_font,
                WHITE,
                tab_x + tab_width // 2,
                tab_y + self.TAB_HEIGHT // 2,
                center=True
            )
    
    def _draw_quest_list(self):
        """Draw the list of quests for the selected type."""
        quests = self.quest_log.get_quests_by_type(self.selected_tab)
        
        # Create a surface for the quest list with clipping
        list_surface = pygame.Surface((self.QUEST_LIST_WIDTH, self.QUEST_LIST_HEIGHT))
        list_surface.fill(BLACK)
        
        for i, quest in enumerate(quests):
            y = i * self.QUEST_ITEM_HEIGHT - self.scroll_offset
            
            # Skip if outside visible area
            if y + self.QUEST_ITEM_HEIGHT < 0 or y > self.QUEST_LIST_HEIGHT:
                continue
            
            # Draw quest item background
            item_color = LIGHT_GRAY if quest == self.selected_quest else (
                GRAY if quest == self.hovered_quest else BLACK
            )
            draw_rect_with_border(
                list_surface,
                (0, y, self.QUEST_LIST_WIDTH, self.QUEST_ITEM_HEIGHT),
                item_color,
                WHITE if quest == self.selected_quest else GRAY
            )
            
            # Draw difficulty indicator
            difficulty_color = self.DIFFICULTY_COLORS.get(quest.difficulty, WHITE)
            pygame.draw.rect(
                list_surface,
                difficulty_color,
                (5, y + 5, 4, self.QUEST_ITEM_HEIGHT - 10)
            )
            
            # Draw quest title
            title_color = WHITE if quest == self.selected_quest else LIGHT_GRAY
            draw_text(
                list_surface,
                quest.title,
                self.font,
                title_color,
                15,
                y + 10
            )
            
            # Draw chain indicator if part of a chain
            if quest.chain_id:
                chain_text = f"Chain {quest.chain_position}/3"
                draw_text(
                    list_surface,
                    chain_text,
                    self.small_font,
                    GOLD,
                    15,
                    y + 35
                )
            
            # Draw completion status
            status_text = "Complete" if quest.is_complete else f"{quest.get_progress()}% Complete"
            status_color = GREEN if quest.is_complete else LIGHT_GRAY
            draw_text(
                list_surface,
                status_text,
                self.small_font,
                status_color,
                self.QUEST_LIST_WIDTH - 10,
                y + self.QUEST_ITEM_HEIGHT // 2,
                align="right"
            )
        
        # Draw the list surface to the screen
        self.screen.blit(list_surface, (self.quest_list_x, self.quest_list_y))
    
    def _draw_quest_details(self):
        """Draw detailed information about the selected quest."""
        x = self.details_x + self.PADDING
        y = self.details_y + self.PADDING
        width = self.details_width - self.PADDING * 2
        
        # Draw quest title
        draw_text(
            self.screen,
            self.selected_quest.title,
            self.title_font,
            WHITE,
            x,
            y
        )
        y += 30
        
        # Draw difficulty
        difficulty_color = self.DIFFICULTY_COLORS.get(self.selected_quest.difficulty, WHITE)
        draw_text(
            self.screen,
            f"Difficulty: {self.selected_quest.difficulty.name}",
            self.font,
            difficulty_color,
            x,
            y
        )
        y += 25
        
        # Draw chain information if part of a chain
        if self.selected_quest.chain_id:
            chain_text = f"Quest Chain: {self.selected_quest.chain_position}/3"
            draw_text(
                self.screen,
                chain_text,
                self.font,
                GOLD,
                x,
                y
            )
            y += 25
        
        # Draw prerequisites if any
        if self.selected_quest.prerequisites:
            prereq_quests = [
                self.quest_log.get_quest(quest_id)
                for quest_id in self.selected_quest.prerequisites
            ]
            prereq_text = "Prerequisites: " + ", ".join(
                quest.title for quest in prereq_quests if quest
            )
            draw_text(
                self.screen,
                prereq_text,
                self.small_font,
                LIGHT_GRAY,
                x,
                y
            )
            y += 25
        
        # Draw description
        y = self._draw_wrapped_text(
            self.selected_quest.description,
            self.font,
            LIGHT_GRAY,
            x,
            y,
            width
        ) + 20
        
        # Draw objectives header
        draw_text(
            self.screen,
            "Objectives:",
            self.font,
            WHITE,
            x,
            y
        )
        y += 25
        
        # Draw objectives
        for objective in self.selected_quest.objectives:
            status_color = GREEN if objective.is_complete else LIGHT_GRAY
            progress_text = f"{objective.description} ({objective.progress}/{objective.required_progress})"
            draw_text(
                self.screen,
                progress_text,
                self.font,
                status_color,
                x + 20,
                y
            )
            y += 25
        
        y += 10
        
        # Draw rewards header
        draw_text(
            self.screen,
            "Rewards:",
            self.font,
            WHITE,
            x,
            y
        )
        y += 25
        
        # Draw rewards
        for reward in self.selected_quest.rewards:
            draw_text(
                self.screen,
                reward.description,
                self.font,
                GOLD,
                x + 20,
                y
            )
            y += 25
    
    def _draw_wrapped_text(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int],
                          x: int, y: int, max_width: int) -> int:
        """Draw text wrapped to fit within max_width. Returns the new y position."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        for line in lines:
            draw_text(self.screen, line, font, color, x, y)
            y += font.get_height()
        
        return y 