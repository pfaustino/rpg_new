"""
Grid-based inventory UI component for RPG games.
"""

import pygame
from typing import Optional, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT
)
from ..items import Item, Weapon, Armor, Hands, Consumable

class InventoryUI:
    """A reusable inventory UI component for pygame games."""
    
    def __init__(
        self,
        screen: pygame.Surface,
        inventory: Optional[List[Optional[Item]]] = None,
        rows: int = 8,
        cols: int = 5
    ):
        """
        Initialize the inventory UI.
        
        Args:
            screen: The pygame surface to draw on
            inventory: The inventory to display (defaults to empty list)
            rows: Number of rows in the grid
            cols: Number of columns in the grid
        """
        self.screen = screen
        self.inventory = inventory if inventory is not None else []
        self.visible = False
        self.grid_rows = rows
        self.grid_cols = cols
        
        # Calculate dimensions
        self.width = UI_DIMENSIONS['inventory_width']
        self.height = UI_DIMENSIONS['inventory_height']
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        
        # Create the main rect
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Initialize UI elements
        self.cell_size = min(
            (self.width - 40) // cols,  # Account for padding
            (self.height - 80) // rows   # Account for header and padding
        )
        
        # Calculate grid position
        grid_width = cols * self.cell_size
        grid_height = rows * self.cell_size
        grid_x = self.x + (self.width - grid_width) // 2
        grid_y = self.y + 50  # Leave space for header
        
        # Create grid cells
        self.grid_cells = []
        for row in range(rows):
            for col in range(cols):
                cell_x = grid_x + col * self.cell_size
                cell_y = grid_y + row * self.cell_size
                self.grid_cells.append(pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size))
        
        # Initialize fonts
        self.font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.small_font = pygame.font.Font(None, FONT_SIZES['small'])
        
        # Initialize tooltip
        self.hovered_item = None
        self.hover_timer = 0
        self.tooltip_visible = False
        self.tooltip_rect = pygame.Rect(0, 0, UI_DIMENSIONS['tooltip_width'], UI_DIMENSIONS['tooltip_height'])
        
        # Initialize selection
        self.selected_item = None
        
    def toggle(self):
        """Toggle visibility of the inventory UI."""
        self.visible = not self.visible
        if not self.visible:
            self.hovered_item = None
            self.tooltip_visible = False
        
    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        """Get the cell index at the given position."""
        for i, cell in enumerate(self.grid_cells):
            if cell.collidepoint(pos):
                return i
        return None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(self.inventory):
                    item = self.inventory[cell_index]
                    if item:
                        self.selected_item = item
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            # Reset tooltip state by default
            new_hovered_item = None
            
            # Check if mouse is over inventory
            if self.rect.collidepoint(mouse_pos):
                cell_index = self.get_cell_at_pos(mouse_pos)
                if cell_index is not None and cell_index < len(self.inventory):
                    new_hovered_item = self.inventory[cell_index]
            
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
        if self.tooltip_visible and self.hovered_item:
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
            
            # Draw quality-colored border
            border_color = QUALITY_COLORS.get(self.hovered_item.quality, QUALITY_COLORS['Common'])
            pygame.draw.rect(self.screen, border_color, self.tooltip_rect, 3)
            
            # Draw item sprite
            sprite = self.hovered_item.get_equipment_sprite()
            scaled_sprite = pygame.transform.scale(sprite, (128, 128))
            self.screen.blit(scaled_sprite, (tooltip_x + 10, tooltip_y + 10))
            
            # Draw item name
            name_text = self.font.render(self.hovered_item.display_name, True, UI_COLORS['text'])
            self.screen.blit(name_text, (tooltip_x + 10, tooltip_y + 150))
            
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
                stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
                self.screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
                y_offset += 20
        
    def draw(self, screen: pygame.Surface):
        """Draw the inventory UI."""
        if not self.visible:
            return
            
        # Draw main panel
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw title
        title = self.font.render("Inventory", True, UI_COLORS['text'])
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 10))
        
        # Draw grid cells
        for i, cell in enumerate(self.grid_cells):
            pygame.draw.rect(screen, UI_COLORS['cell_background'], cell)
            pygame.draw.rect(screen, UI_COLORS['cell_border'], cell, 1)
            
            # Draw item if present
            if i < len(self.inventory) and self.inventory[i]:
                item = self.inventory[i]
                # Draw item sprite centered in cell
                sprite = item.get_equipment_sprite()
                scaled_sprite = pygame.transform.scale(sprite, (self.cell_size - 4, self.cell_size - 4))
                screen.blit(scaled_sprite, (cell.x + 2, cell.y + 2))
        
        # Draw tooltip if needed
        if self.tooltip_visible:
            self.draw_tooltip() 