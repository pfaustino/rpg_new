"""
Grid-based inventory UI component for RPG games.
"""

import pygame
from typing import Optional, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES
)
from ..items import Item, Weapon, Armor, Hands, Consumable

class InventoryUI:
    """A reusable inventory UI component for pygame games."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int = 300,
        height: int = 500,
        rows: int = 8,
        cols: int = 5
    ):
        """
        Initialize the inventory UI.
        
        Args:
            x: X position of the inventory
            y: Y position of the inventory
            width: Width of the inventory panel
            height: Height of the inventory panel
            rows: Number of rows in the grid
            cols: Number of columns in the grid
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.grid_rows = rows
        self.grid_cols = cols
        
        # Initialize UI elements
        self.cell_size = min(
            (width - 40) // cols,  # Account for padding
            (height - 80) // rows   # Account for header and padding
        )
        
        # Calculate grid position
        grid_width = cols * self.cell_size
        grid_height = rows * self.cell_size
        grid_x = x + (width - grid_width) // 2
        grid_y = y + 50  # Leave space for header
        
        # Create grid cells
        self.grid_cells = []
        for row in range(rows):
            for col in range(cols):
                cell_x = grid_x + col * self.cell_size
                cell_y = grid_y + row * self.cell_size
                self.grid_cells.append(pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size))
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Initialize tooltip
        self.hovered_item = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, 300, 300)
        
        # Initialize selection
        self.selected_item = None
        
    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the cell index at the given position."""
        for i, cell in enumerate(self.grid_cells):
            if cell.collidepoint(pos):
                return i
        return None
        
    def handle_event(self, event: pygame.event.Event, player) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(player.inventory.items):
                    item = player.inventory.items[cell_index]
                    if item:
                        # Try to equip the item
                        if player.equip_item(item):
                            player.inventory.items[cell_index] = None
                            return True
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # Reset tooltip state by default
            new_hovered_item = None
            
            # Check if mouse is over inventory
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(player.inventory.items):
                    new_hovered_item = player.inventory.items[cell_index]
            
            # Update tooltip state
            if new_hovered_item != self.hovered_item:
                self.hovered_item = new_hovered_item
                self.hover_timer = 0
                self.tooltip_visible = False
            
        return False
        
    def update(self):
        """Update tooltip visibility."""
        if self.hovered_item:
            self.hover_timer += 1
            if self.hover_timer > 15:  # Show tooltip after 0.25 seconds (assuming 60 FPS)
                self.tooltip_visible = True
        else:
            self.hover_timer = 0
            self.tooltip_visible = False
        
    def draw_tooltip(self, screen: pygame.Surface):
        """Draw the tooltip for the currently hovered item."""
        if self.tooltip_visible and self.hovered_item:
            # Position tooltip to avoid screen edges
            mouse_pos = pygame.mouse.get_pos()
            tooltip_x = mouse_pos[0] + 20  # Offset from mouse cursor
            tooltip_y = mouse_pos[1] - 50   # Position above mouse cursor
            
            # Adjust if tooltip would go off screen
            screen_width = pygame.display.get_surface().get_width()
            screen_height = pygame.display.get_surface().get_height()
            
            if tooltip_x + self.tooltip_rect.width > screen_width:
                tooltip_x = screen_width - self.tooltip_rect.width - 10
            if tooltip_y + self.tooltip_rect.height > screen_height:
                tooltip_y = screen_height - self.tooltip_rect.height - 10
            if tooltip_y < 10:
                tooltip_y = 10
            
            # Draw tooltip background
            self.tooltip_rect.topleft = (tooltip_x, tooltip_y)
            pygame.draw.rect(screen, (30, 30, 30), self.tooltip_rect)
            
            # Draw quality-colored border
            border_color = QUALITY_COLORS.get(self.hovered_item.quality, QUALITY_COLORS['Common'])
            pygame.draw.rect(screen, border_color, self.tooltip_rect, 3)
            
            # Draw item sprite
            sprite = self.hovered_item.get_equipment_sprite()
            scaled_sprite = pygame.transform.scale(sprite, (128, 128))
            screen.blit(scaled_sprite, (tooltip_x + 10, tooltip_y + 10))
            
            # Draw item name
            name_text = self.font.render(self.hovered_item.display_name, True, (255, 255, 255))
            screen.blit(name_text, (tooltip_x + 10, tooltip_y + 150))
            
            # Draw item stats
            y_offset = 180
            stats = []
            
            if isinstance(self.hovered_item, Weapon):
                stats = [
                    f"Type: {self.hovered_item.weapon_type}",
                    f"Attack: {self.hovered_item.attack_power}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
            elif isinstance(self.hovered_item, Hands):
                stats = [
                    "Type: Gauntlets",
                    f"Defense: {self.hovered_item.defense}",
                    f"Dexterity: {self.hovered_item.dexterity}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
            elif isinstance(self.hovered_item, Consumable):
                stats = [
                    f"Type: {self.hovered_item.consumable_type}",
                    f"Effect Value: {self.hovered_item.effect_value}",
                    f"Quality: {self.hovered_item.quality}"
                ]
            elif isinstance(self.hovered_item, Armor):
                stats = [
                    f"Type: {self.hovered_item.armor_type}",
                    f"Defense: {self.hovered_item.defense}",
                    f"Material: {self.hovered_item.material}",
                    f"Quality: {self.hovered_item.quality}"
                ]
                
            if self.hovered_item.prefix:
                stats.insert(1, f"Effect: {self.hovered_item.prefix}")
                
            for stat in stats:
                stat_text = self.small_font.render(stat, True, (255, 255, 255))
                screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
                y_offset += 20

    def draw(self, screen: pygame.Surface, player):
        """Draw the inventory UI."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Inventory", True, (255, 255, 255))
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw grid cells
        for i, cell in enumerate(self.grid_cells):
            # Draw cell background
            pygame.draw.rect(screen, (30, 30, 30), cell)
            pygame.draw.rect(screen, (255, 255, 255), cell, 1)
            
            # Draw item if one exists at this index
            if i < len(player.inventory.items):
                item = player.inventory.items[i]
                if item:
                    # Draw item sprite
                    sprite = item.get_equipment_sprite()
                    scaled_sprite = pygame.transform.scale(sprite, (self.cell_size - 10, self.cell_size - 10))
                    screen.blit(scaled_sprite, (cell.x + 5, cell.y + 5))
                    
                    # Draw quality-colored border
                    border_color = QUALITY_COLORS.get(item.quality, QUALITY_COLORS['Common'])
                    pygame.draw.rect(screen, border_color, cell, 3)
                    
                    # Draw item name
                    name = item.display_name.split()[0]  # Get first word
                    name_text = self.small_font.render(name, True, (255, 255, 255))
                    screen.blit(name_text, (cell.x + 5, cell.y + 5))
                    
                    # Draw item stats
                    if isinstance(item, Weapon):
                        stat_text = self.small_font.render(f"ATK:{item.attack_power}", True, (255, 255, 255))
                    elif isinstance(item, Hands):
                        stat_text = self.small_font.render(f"DEF:{item.defense}", True, (255, 255, 255))
                    elif isinstance(item, Consumable):
                        stat_text = self.small_font.render(f"POT:{item.effect_value}", True, (255, 255, 255))
                    elif isinstance(item, Armor):
                        stat_text = self.small_font.render(f"DEF:{item.defense}", True, (255, 255, 255))
                    else:
                        stat_text = None
                        
                    if stat_text:
                        screen.blit(stat_text, (cell.right - 40, cell.bottom - 15))
        
        # Draw tooltip
        self.draw_tooltip(screen) 