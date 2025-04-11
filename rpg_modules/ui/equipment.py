"""
Equipment UI component for RPG games.
"""

import pygame
from typing import Optional, Dict
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT
)
from ..items import Item

class EquipmentUI:
    """A reusable equipment UI component for pygame games."""
    
    def __init__(
        self,
        screen: pygame.Surface,
        equipment: Optional[Dict[str, Optional[Item]]] = None
    ):
        """
        Initialize the equipment UI.
        
        Args:
            screen: The pygame surface to draw on
            equipment: Dictionary of equipped items (defaults to empty dict)
        """
        self.screen = screen
        self.equipment = equipment if equipment is not None else {}
        self.visible = False
        
        # Calculate dimensions
        self.width = UI_DIMENSIONS['equipment_width']
        self.height = UI_DIMENSIONS['equipment_height']
        self.x = SCREEN_WIDTH - self.width - 10
        self.y = 10
        
        # Create the main rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Initialize fonts
        self.font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.small_font = pygame.font.Font(None, FONT_SIZES['small'])
        
        # Initialize tooltip
        self.hovered_item = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, UI_DIMENSIONS['tooltip_width'], UI_DIMENSIONS['tooltip_height'])
        
        # Create equipment slots
        self.slots = {
            'weapon': pygame.Rect(self.x + 10, self.y + 50, 40, 40),
            'head': pygame.Rect(self.x + 60, self.y + 50, 40, 40),
            'chest': pygame.Rect(self.x + 10, self.y + 100, 40, 40),
            'legs': pygame.Rect(self.x + 60, self.y + 100, 40, 40),
            'feet': pygame.Rect(self.x + 10, self.y + 150, 40, 40),
            'hands': pygame.Rect(self.x + 60, self.y + 150, 40, 40)
        }
        
    def toggle(self):
        """Toggle visibility of the equipment UI."""
        self.visible = not self.visible
        if not self.visible:
            self.hovered_item = None
            self.tooltip_visible = False
            
    def draw(self, screen: pygame.Surface):
        """Draw the equipment UI."""
        if not self.visible:
            return
        
        # Update rect position based on current x,y
        self.rect.topleft = (self.x, self.y)
        
        # Recalculate slot positions based on new UI position
        slot_size = 40
        slot_spacing = 10
        self.slots = {
            'weapon': pygame.Rect(self.x + slot_spacing, self.y + 50, slot_size, slot_size),
            'head': pygame.Rect(self.x + slot_size + slot_spacing*2, self.y + 50, slot_size, slot_size),
            'chest': pygame.Rect(self.x + slot_spacing, self.y + 100, slot_size, slot_size),
            'legs': pygame.Rect(self.x + slot_size + slot_spacing*2, self.y + 100, slot_size, slot_size),
            'feet': pygame.Rect(self.x + slot_spacing, self.y + 150, slot_size, slot_size),
            'hands': pygame.Rect(self.x + slot_size + slot_spacing*2, self.y + 150, slot_size, slot_size)
        }
            
        # Draw main panel
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw title
        title = self.font.render("Equipment", True, UI_COLORS['text'])
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 10))
        
        # Draw equipment slots
        for slot_name, slot_rect in self.slots.items():
            # Draw slot background
            pygame.draw.rect(screen, UI_COLORS['cell_background'], slot_rect)
            pygame.draw.rect(screen, UI_COLORS['border'], slot_rect, 1)
            
            # Draw slot label
            label = self.small_font.render(slot_name.capitalize(), True, UI_COLORS['text'])
            label_x = slot_rect.x + (slot_rect.width - label.get_width()) // 2
            label_y = slot_rect.y - 20
            screen.blit(label, (label_x, label_y))
            
            # Draw equipped item if present
            if slot_name in self.equipment and self.equipment[slot_name]:
                item = self.equipment[slot_name]
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (36, 36))
                screen.blit(scaled_sprite, (slot_rect.x + 2, slot_rect.y + 2))
                
        # Draw tooltip if needed
        if self.tooltip_visible and self.hovered_item:
            self.draw_tooltip()
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check if clicking on equipment slots
            for slot_name, slot_rect in self.slots.items():
                if slot_rect.collidepoint(mouse_pos):
                    if slot_name in self.equipment and self.equipment[slot_name]:
                        # Get the equipped item
                        item = self.equipment[slot_name]
                        print(f"Equipment: Clicked on equipped item: {item.display_name} in slot {slot_name}")
                        
                        # Use the global GameState object to unequip the item
                        import sys
                        if 'game' in sys.modules:
                            game_module = sys.modules.get('game')
                            if hasattr(game_module, 'game_state'):
                                game_state = game_module.game_state
                                print(f"Found global game_state: {game_state}")
                                
                                # Try to unequip the item
                                success = game_state.unequip_item(slot_name)
                                if success:
                                    print(f"Successfully unequipped {item.display_name} from {slot_name}")
                                else:
                                    print(f"Failed to unequip {item.display_name} - inventory may be full")
                            else:
                                print("Could not find game_state in game module")
                        else:
                            print("Could not find game module")
                        
                        return True
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # Reset tooltip state by default
            new_hovered_item = None
            
            # Check if mouse is over equipment slots
            for slot_name, slot_rect in self.slots.items():
                if slot_rect.collidepoint(mouse_pos):
                    if slot_name in self.equipment:
                        new_hovered_item = self.equipment[slot_name]
                    break
            
            # Update tooltip state
            if new_hovered_item != self.hovered_item:
                self.hovered_item = new_hovered_item
                self.hover_timer = 0
                self.tooltip_visible = False
            
        return False
        
    def update(self):
        """Update tooltip visibility."""
        if not self.visible:
            return
            
        if self.hovered_item:
            self.hover_timer += 1
            if self.hover_timer > 15:  # Show tooltip after 0.25 seconds (assuming 60 FPS)
                self.tooltip_visible = True
        else:
            self.hover_timer = 0
            self.tooltip_visible = False
            
    def draw_tooltip(self):
        """Draw the tooltip for the currently hovered item."""
        if not self.tooltip_visible or not self.hovered_item:
            return
            
        # Position tooltip to avoid screen edges
        mouse_pos = pygame.mouse.get_pos()
        tooltip_x = mouse_pos[0] + 20  # Offset from mouse cursor
        tooltip_y = mouse_pos[1] - 50   # Position above mouse cursor
        
        # Adjust if tooltip would go off screen
        if tooltip_x + self.tooltip_rect.width > SCREEN_WIDTH:
            tooltip_x = SCREEN_WIDTH - self.tooltip_rect.width - 10
        if tooltip_y + self.tooltip_rect.height > SCREEN_HEIGHT:
            tooltip_y = SCREEN_HEIGHT - self.tooltip_rect.height - 10
        if tooltip_y < 10:
            tooltip_y = 10
        
        # Draw tooltip background
        self.tooltip_rect.topleft = (tooltip_x, tooltip_y)
        pygame.draw.rect(self.screen, UI_COLORS['background'], self.tooltip_rect)
        pygame.draw.rect(self.screen, UI_COLORS['border'], self.tooltip_rect, 2)
        
        # Draw item name
        name_text = self.font.render(self.hovered_item.display_name, True, UI_COLORS['text'])
        self.screen.blit(name_text, (tooltip_x + 10, tooltip_y + 10))
        
        # Draw item stats
        y_offset = 40
        stats = self.hovered_item.get_stats_text()
        for stat in stats:
            stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
            self.screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
            y_offset += 20 