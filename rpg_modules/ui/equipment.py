"""
Equipment UI component for RPG games.
"""

import pygame
from typing import Optional, Dict, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES
)
from ..items import Item, Weapon, Armor, Hands, Consumable

class EquipmentUI:
    """A reusable equipment UI component for pygame games."""
    
    def __init__(self, x: int, y: int, width: int = 300, height: int = 500):
        """
        Initialize the equipment UI.
        
        Args:
            x: X position of the equipment panel
            y: Y position of the equipment panel
            width: Width of the equipment panel
            height: Height of the equipment panel
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Initialize tooltip
        self.hovered_slot = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, 300, 300)
        
        # Define equipment slots in a mannequin-like layout
        slot_size = 70  # Slightly smaller slots to fit better
        center_x = x + (width - slot_size) // 2
        
        # Adjust vertical spacing for better distribution
        self.slots = {
            'head': pygame.Rect(center_x, y + 40, slot_size, slot_size),
            'chest': pygame.Rect(center_x, y + 130, slot_size, slot_size),
            'hands': pygame.Rect(center_x - 90, y + 130, slot_size, slot_size),
            'weapon': pygame.Rect(center_x + 90, y + 130, slot_size, slot_size),
            'legs': pygame.Rect(center_x, y + 220, slot_size, slot_size),
            'feet': pygame.Rect(center_x, y + 310, slot_size, slot_size)
        }
        
        # Define label positions relative to slots
        self.label_positions = {
            'head': ('above', 5),
            'chest': ('above', 5),
            'hands': ('above', 5),
            'weapon': ('above', 5),
            'legs': ('above', 5),
            'feet': ('above', 5)
        }
        
    def get_slot_at_pos(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Get the equipment slot at the given mouse position."""
        if not self.rect.collidepoint(mouse_pos):
            return None
            
        for slot_name, slot_rect in self.slots.items():
            if slot_rect.collidepoint(mouse_pos):
                return slot_name
        return None
        
    def handle_event(self, event: pygame.event.Event, player) -> bool:
        """Handle mouse events for equipment interaction."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            slot_name = self.get_slot_at_pos(event.pos)
            if slot_name:
                item = player.unequip_item(slot_name)
                if item:
                    player.inventory.add_item(item)
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_slot = self.get_slot_at_pos(event.pos)
            if self.hovered_slot:
                self.hover_timer = 0
                self.tooltip_visible = False
            else:
                self.tooltip_visible = False
                
        return False
        
    def update(self):
        """Update tooltip visibility."""
        if self.hovered_slot:
            self.hover_timer += 1
            if self.hover_timer > 30:  # Show tooltip after 0.5 seconds
                self.tooltip_visible = True
                
    def draw(self, screen: pygame.Surface, player):
        """Draw the equipment UI and any visible tooltips."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Equipment", True, (255, 255, 255))
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw slots
        for slot_name, slot_rect in self.slots.items():
            # Draw slot background
            pygame.draw.rect(screen, (30, 30, 30), slot_rect)
            
            # Draw slot name
            name_text = self.small_font.render(slot_name.capitalize(), True, (255, 255, 255))
            text_x = slot_rect.centerx - name_text.get_width() // 2
            text_y = slot_rect.y - name_text.get_height() - 5
            screen.blit(name_text, (text_x, text_y))
            
            # Draw equipped item if any
            item = player.equipment.get_equipped_item(slot_name)
            if item:
                # Draw item sprite
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (slot_rect.width - 20, slot_rect.height - 20))
                screen.blit(scaled_sprite, (slot_rect.x + 10, slot_rect.y + 10))
                
                # Draw quality-colored border
                border_color = QUALITY_COLORS.get(item.quality, QUALITY_COLORS['Common'])
                pygame.draw.rect(screen, border_color, slot_rect, 3)
            else:
                # Draw empty slot border
                pygame.draw.rect(screen, (255, 255, 255), slot_rect, 1)
                
        # Draw tooltip if visible
        if self.tooltip_visible and self.hovered_slot:
            item = player.equipment.get_equipped_item(self.hovered_slot)
            if item:
                self._draw_tooltip(screen, item, pygame.mouse.get_pos())
                
    def _draw_tooltip(self, screen: pygame.Surface, item, mouse_pos: Tuple[int, int]):
        """Draw a tooltip for the given item."""
        # Position tooltip near mouse cursor
        tooltip_x = mouse_pos[0] + 20  # Offset from mouse cursor
        tooltip_y = mouse_pos[1] - 50   # Position above mouse cursor
        
        # Get screen dimensions
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        # Create tooltip rectangle
        tooltip_rect = pygame.Rect(
            tooltip_x,
            tooltip_y,
            300,  # Width
            300   # Height
        )
        
        # Adjust if tooltip would go off screen
        if tooltip_x + tooltip_rect.width > screen_width:
            tooltip_x = screen_width - tooltip_rect.width - 10
        if tooltip_y + tooltip_rect.height > screen_height:
            tooltip_y = screen_height - tooltip_rect.height - 10
        if tooltip_y < 10:
            tooltip_y = 10
            
        # Update tooltip position
        tooltip_rect.topleft = (tooltip_x, tooltip_y)
        
        # Draw tooltip background
        pygame.draw.rect(screen, (30, 30, 30), tooltip_rect)
        
        # Draw quality-colored border
        border_color = QUALITY_COLORS.get(item.quality, QUALITY_COLORS['Common'])
        pygame.draw.rect(screen, border_color, tooltip_rect, 3)
        
        # Draw item sprite with border
        sprite = item.get_equipment_sprite()
        scaled_sprite = pygame.transform.scale(sprite, (128, 128))
        sprite_rect = pygame.Rect(tooltip_rect.x + 10, tooltip_rect.y + 10, 134, 134)
        pygame.draw.rect(screen, border_color, sprite_rect, 3)
        screen.blit(scaled_sprite, (tooltip_rect.x + 13, tooltip_rect.y + 13))
        
        # Draw item name
        name_text = self.font.render(item.display_name, True, (255, 255, 255))
        screen.blit(name_text, (tooltip_rect.x + 10, tooltip_rect.y + 150))
        
        # Draw item stats
        y_offset = 180
        stats = self._get_item_stats(item)
        for stat in stats:
            stat_text = self.small_font.render(stat, True, (255, 255, 255))
            screen.blit(stat_text, (tooltip_rect.x + 10, tooltip_rect.y + y_offset))
            y_offset += 20
            
    def _get_item_stats(self, item) -> List[str]:
        """Get a list of stat strings for the given item."""
        stats = []
        
        # Add type-specific stats
        if isinstance(item, Weapon):
            stats = [
                f"Type: {item.weapon_type}",
                f"Attack: {item.attack_power}",
                f"Material: {item.material}",
                f"Quality: {item.quality}"
            ]
        elif isinstance(item, Hands):
            stats = [
                "Type: Gauntlets",
                f"Defense: {item.defense}",
                f"Dexterity: {item.dexterity}",
                f"Material: {item.material}",
                f"Quality: {item.quality}"
            ]
        elif isinstance(item, Consumable):
            stats = [
                f"Type: {item.consumable_type}",
                f"Effect Value: {item.effect_value}",
                f"Quality: {item.quality}"
            ]
        elif isinstance(item, Armor):
            stats = [
                f"Type: {item.armor_type}",
                f"Defense: {item.defense}",
                f"Material: {item.material}",
                f"Quality: {item.quality}"
            ]
            
        if item.prefix:
            stats.insert(1, f"Effect: {item.prefix}")
            
        return stats 