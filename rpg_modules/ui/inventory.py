"""
Grid-based inventory UI component for RPG games.
"""

import pygame
from typing import Optional, Tuple, List, Callable
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, SCREEN_WIDTH, SCREEN_HEIGHT, GRAY
)
from ..items import Item, Weapon, Armor, Hands, Consumable
import sys
import importlib
import traceback

print("DEBUG: Loading rpg_modules.ui.inventory module")

# Import the main game module - we'll do this once at module load
# and retry during handle_event if needed
game_module = None
equip_function = None

def import_game_module():
    """Import the game module and set up the equip function."""
    global game_module, equip_function
    
    try:
        # Direct import - not using importlib to avoid caching issues
        import game
        game_module = game
        
        # Get the equip function directly
        if hasattr(game_module, 'equip_item_from_inventory'):
            equip_function = game_module.equip_item_from_inventory
            print(f"DEBUG: Successfully imported equip_function: {equip_function}")
            
            # Test if we can access game_state
            if hasattr(game_module, 'game_state'):
                print(f"DEBUG: game_state in module is: {game_module.game_state}")
                if game_module.game_state is None:
                    print("WARNING: game_state is None - equipment functionality may not work yet")
                else:
                    print(f"DEBUG: game_state is initialized: {type(game_module.game_state).__name__}")
            else:
                print("WARNING: game_state not found in game module")
        else:
            print("WARNING: equip_item_from_inventory not found in game module")
    except Exception as e:
        print(f"ERROR importing game module: {e}")
        traceback.print_exc()
        game_module = None
        equip_function = None

# Try to import the game module right away
import_game_module()

class InventoryUI:
    """A reusable inventory UI component for pygame games."""
    
    def __init__(
        self,
        screen: pygame.Surface,
        inventory: Optional[List[Optional[Item]]] = None,
        rows: int = 8,
        cols: int = 5,
        equip_callback: Optional[Callable[[int], bool]] = None
    ):
        """
        Initialize the inventory UI.
        
        Args:
            screen: The pygame surface to draw on
            inventory: The inventory to display (defaults to empty list)
            rows: Number of rows in the grid
            cols: Number of columns in the grid
            equip_callback: Function to call when an item is clicked for equipping
        """
        self.screen = screen
        self.inventory = inventory if inventory is not None else []
        print(f"InventoryUI initialized with inventory: {id(self.inventory)}, length: {len(self.inventory) if self.inventory else 0}")
        self.visible = False
        self.grid_rows = rows
        self.grid_cols = cols
        self.equip_callback = equip_callback
        
        # Calculate dimensions
        self.width = UI_DIMENSIONS['inventory_width']
        self.height = UI_DIMENSIONS['inventory_height']
        
        # Position on left side of screen
        self.x = 10  # Left margin
        self.y = 10  # Top margin
        
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
        
    def set_equip_callback(self, callback: Callable[[int], bool]):
        """Set the equip callback function."""
        self.equip_callback = callback
        print(f"DEBUG: InventoryUI equip callback set to: {callback}")
        
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
                        print(f"Inventory: Clicked on item: {item.display_name} in slot {cell_index}")
                        self.selected_item = item
                        
                        # Call the equip callback if available
                        if self.equip_callback:
                            try:
                                print(f"DEBUG: Calling equip_callback({cell_index})")
                                success = self.equip_callback(cell_index)
                                if success:
                                    print(f"Successfully equipped {item.display_name}")
                                else:
                                    print(f"Failed to equip {item.display_name}")
                            except Exception as e:
                                print(f"ERROR calling equip_callback: {e}")
                                traceback.print_exc()
                        else:
                            print("WARNING: No equip callback set for inventory UI")
                        
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
            
            # Increase tooltip size for more information
            tooltip_width = UI_DIMENSIONS['tooltip_width'] + 50  # Make it wider
            tooltip_height = UI_DIMENSIONS['tooltip_height'] + 80  # Make it taller
            self.tooltip_rect = pygame.Rect(0, 0, tooltip_width, tooltip_height)
            
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
            
            try:
                # Try to get the item sprite with fallback for missing sprites
                try:
                    sprite = self.hovered_item.get_equipment_sprite()
                except (FileNotFoundError, pygame.error, AttributeError) as e:
                    # Create a fallback sprite based on item type
                    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
                    
                    # Determine item type and set appropriate color
                    if hasattr(self.hovered_item, 'weapon_type'):
                        # Weapon placeholder (sword shape)
                        color = QUALITY_COLORS.get(self.hovered_item.quality, (200, 200, 200))
                        pygame.draw.polygon(sprite, color, [(20, 10), (44, 10), (44, 54), (32, 54), (20, 40)])
                        pygame.draw.rect(sprite, (100, 100, 100), (25, 10, 14, 25))  # handle
                    elif hasattr(self.hovered_item, 'armor_type'):
                        # Armor placeholder (shield/chest shape)
                        color = QUALITY_COLORS.get(self.hovered_item.quality, (200, 200, 200))
                        pygame.draw.ellipse(sprite, color, (10, 10, 44, 44))
                        pygame.draw.ellipse(sprite, (100, 100, 100), (15, 15, 34, 34), 2)
                    else:
                        # Consumable placeholder (potion shape)
                        color = (200, 50, 50) if self.hovered_item.consumable_type == 'health' else \
                               (50, 50, 200) if self.hovered_item.consumable_type == 'mana' else \
                               (50, 200, 50)  # stamina
                        pygame.draw.rect(sprite, (200, 200, 200), (25, 15, 14, 35))
                        pygame.draw.rect(sprite, color, (20, 25, 24, 25))
                        pygame.draw.ellipse(sprite, (200, 200, 200), (20, 10, 24, 20))
                
                # Scale the sprite
                scaled_sprite = pygame.transform.scale(sprite, (128, 128))
                self.screen.blit(scaled_sprite, (tooltip_x + 10, tooltip_y + 10))
                
                # Draw item name with quality-colored text
                name_font = pygame.font.Font(None, FONT_SIZES['large'])
                name_text = name_font.render(self.hovered_item.display_name, True, border_color)
                name_shadow = name_font.render(self.hovered_item.display_name, True, (30, 30, 30))
                
                # Add text shadow for better visibility
                self.screen.blit(name_shadow, (tooltip_x + 151, tooltip_y + 16))
                self.screen.blit(name_text, (tooltip_x + 150, tooltip_y + 15))
                
                # Draw horizontal divider line
                pygame.draw.line(self.screen, border_color, 
                                (tooltip_x + 10, tooltip_y + 45), 
                                (tooltip_x + tooltip_width - 20, tooltip_y + 45), 2)
                
                # Get complete item stats using the item's built-in method
                if hasattr(self.hovered_item, 'get_stats_display'):
                    basic_stats = self.hovered_item.get_stats_display()
                else:
                    # Fallback for items without get_stats_display
                    basic_stats = []
                    
                # Add additional attributes if available
                additional_stats = []
                
                # Weight if available
                if hasattr(self.hovered_item, 'weight'):
                    additional_stats.append(f"Weight: {self.hovered_item.weight} kg")
                    
                # Durability if available
                if hasattr(self.hovered_item, 'durability') and hasattr(self.hovered_item, 'max_durability'):
                    durability_percent = int((self.hovered_item.durability / self.hovered_item.max_durability) * 100)
                    additional_stats.append(f"Durability: {durability_percent}%")
                    
                # Level requirement if available
                if hasattr(self.hovered_item, 'level_req'):
                    additional_stats.append(f"Required Level: {self.hovered_item.level_req}")
                
                # Combine all stats
                all_stats = basic_stats + additional_stats
                
                # Draw basic stats on left column
                y_offset = 60
                for i, stat in enumerate(all_stats):
                    # Check if we need to start a second column
                    if i == len(all_stats) // 2 + 1:
                        y_offset = 60  # Reset y position for second column
                        x_offset = tooltip_width // 2 + 10  # Start x position for second column
                    else:
                        x_offset = 20  # Default x position for first column
                        
                    # Determine text color based on stat content
                    if "Quality:" in stat:
                        text_color = QUALITY_COLORS.get(self.hovered_item.quality, UI_COLORS['text'])
                    elif "Effect:" in stat:
                        text_color = (220, 190, 100)  # Gold-ish for effects
                    elif "Attack:" in stat or "Damage:" in stat:
                        text_color = (220, 100, 100)  # Red for attack stats
                    elif "Defense:" in stat:
                        text_color = (100, 100, 220)  # Blue for defense stats
                    else:
                        text_color = UI_COLORS['text']
                        
                    stat_text = self.small_font.render(stat, True, text_color)
                    self.screen.blit(stat_text, (tooltip_x + x_offset, tooltip_y + y_offset))
                    y_offset += 22  # Slightly increased line spacing
                
                # Draw item description if available
                if hasattr(self.hovered_item, 'description') and self.hovered_item.description:
                    # Draw another divider
                    description_y = tooltip_y + tooltip_height - 60
                    pygame.draw.line(self.screen, border_color, 
                                    (tooltip_x + 10, description_y - 10), 
                                    (tooltip_x + tooltip_width - 20, description_y - 10), 1)
                                    
                    # Draw description with word wrapping
                    desc_font = pygame.font.Font(None, FONT_SIZES['small'] - 2)
                    lines = []
                    words = self.hovered_item.description.split()
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + word + " "
                        if desc_font.size(test_line)[0] < tooltip_width - 40:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word + " "
                    lines.append(current_line)  # Add the last line
                    
                    # Draw each line
                    for i, line in enumerate(lines):
                        if i < 3:  # Limit to 3 lines
                            desc_text = desc_font.render(line, True, (180, 180, 180))
                            self.screen.blit(desc_text, (tooltip_x + 20, description_y + i * 18))
                
            except Exception as e:
                # Handle errors when drawing tooltip
                error_text = self.small_font.render(f"Error displaying item: {str(e)}", True, (255, 100, 100))
                self.screen.blit(error_text, (tooltip_x + 10, tooltip_y + 150))
                print(f"Error drawing tooltip: {e}")
        
    def draw(self, screen: pygame.Surface):
        """Draw the inventory UI."""
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Inventory", True, UI_COLORS['text'])
        header_rect = header_text.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(header_text, header_rect)
        
        # DIAGNOSTIC: Draw a direct visual representation of inventory contents at the top
        filled_slots = sum(1 for item in self.inventory if item is not None)
        diagnostic_text = f"Items: {filled_slots}/{len(self.inventory) if self.inventory else 0} - ID: {id(self.inventory)}"
        diag_text = self.small_font.render(diagnostic_text, True, (255, 255, 0))
        screen.blit(diag_text, (self.rect.left + 10, self.rect.top + 35))
        
        # Draw an array visualization showing which slots have items
        if self.inventory:
            slot_width = 8
            slot_spacing = 2
            slot_total = slot_width + slot_spacing
            slots_per_row = min(len(self.inventory), 20)  # Max 20 slots per row
            
            for i, item in enumerate(self.inventory):
                row = i // slots_per_row
                col = i % slots_per_row
                x = self.rect.left + 10 + col * slot_total
                y = self.rect.top + 60 + row * slot_total
                
                # Draw slot representation
                color = (0, 200, 0) if item is not None else (100, 100, 100)
                pygame.draw.rect(screen, color, (x, y, slot_width, slot_width))
                
                # Add small number indicator for first few items
                if item is not None and i < 20:
                    tiny_font = pygame.font.Font(None, 10)
                    idx_text = tiny_font.render(str(i), True, (0, 0, 0))
                    screen.blit(idx_text, (x, y))
        
        # Draw each inventory slot
        # Debug print to check number of items
        print(f"\n===== INVENTORY UI DEBUG ====")
        print(f"Inventory reference: {id(self.inventory)}")
        print(f"Inventory type: {type(self.inventory)}")
        if self.inventory is None:
            print("ERROR: Inventory is None!")
            # Initialize with empty list to prevent errors
            self.inventory = []
        elif not isinstance(self.inventory, list):
            print(f"ERROR: Inventory is not a list! Type: {type(self.inventory)}")
            # Try to convert to list if possible, otherwise use empty list
            try:
                self.inventory = list(self.inventory)
            except:
                self.inventory = []
        else:
            print(f"Inventory length: {len(self.inventory)}")
            filled_slots = sum(1 for item in self.inventory if item is not None)
            print(f"Filled slots: {filled_slots}")
            print(f"First few items: {[str(item) if item else 'None' for item in self.inventory[:5]]}")
        print(f"===== END INVENTORY DEBUG ====\n")
        
        # Draw each cell in the grid
        for i, cell in enumerate(self.grid_cells):
            # Draw cell background
            pygame.draw.rect(screen, UI_COLORS['cell_background'], cell)
            
            # Draw cell border
            pygame.draw.rect(screen, UI_COLORS['border'], cell, 1)
            
            # Draw item in cell if it exists
            if self.inventory and i < len(self.inventory) and self.inventory[i] is not None:
                item = self.inventory[i]
                try:
                    # Try to render the item sprite
                    try:
                        sprite = item.get_equipment_sprite()
                        
                        # Scale to fit cell
                        scale_factor = min(cell.width / sprite.get_width(), 
                                         cell.height / sprite.get_height()) * 0.8
                        new_width = int(sprite.get_width() * scale_factor)
                        new_height = int(sprite.get_height() * scale_factor)
                        scaled_sprite = pygame.transform.scale(sprite, (new_width, new_height))
                        
                        # Calculate position to center in cell
                        sprite_x = cell.x + (cell.width - new_width) // 2
                        sprite_y = cell.y + (cell.height - new_height) // 2
                        
                        # Draw the sprite
                        screen.blit(scaled_sprite, (sprite_x, sprite_y))
                        
                        # Draw a colored border based on item quality
                        quality_color = item.quality_color
                        pygame.draw.rect(screen, quality_color, cell, 2)
                        
                    except (pygame.error, FileNotFoundError, AttributeError) as e:
                        # If sprite loading fails, draw a colored rectangle
                        quality_color = getattr(item, 'quality_color', GRAY)
                        
                        # Draw a smaller rectangle inside the cell
                        inner_rect = pygame.Rect(
                            cell.x + 5, cell.y + 5, 
                            cell.width - 10, cell.height - 10
                        )
                        pygame.draw.rect(screen, quality_color, inner_rect)
                        
                        # Add an icon based on item type
                        if hasattr(item, 'weapon_type'):
                            # Draw a simple sword icon
                            points = [
                                (cell.centerx, cell.y + 10),
                                (cell.centerx + 5, cell.centery),
                                (cell.centerx, cell.bottom - 10),
                                (cell.centerx - 5, cell.centery)
                            ]
                            pygame.draw.polygon(screen, (200, 200, 200), points)
                        elif hasattr(item, 'armor_type'):
                            # Draw a simple shield icon
                            pygame.draw.ellipse(
                                screen, (200, 200, 200),
                                pygame.Rect(cell.centerx - 10, cell.centery - 10, 20, 20),
                                3
                            )
                        elif hasattr(item, 'consumable_type'):
                            # Draw a simple potion icon
                            pygame.draw.rect(
                                screen, (200, 200, 200),
                                pygame.Rect(cell.centerx - 4, cell.centery - 8, 8, 16)
                            )
                        
                except Exception as e:
                    # If rendering fails for any reason, draw an X
                    pygame.draw.line(screen, (255, 0, 0), 
                                   (cell.x + 5, cell.y + 5), 
                                   (cell.x + cell.width - 5, cell.y + cell.height - 5), 2)
                    pygame.draw.line(screen, (255, 0, 0), 
                                   (cell.x + cell.width - 5, cell.y + 5), 
                                   (cell.x + 5, cell.y + cell.height - 5), 2)
                    
                    # Log error
                    print(f"Error rendering item in inventory: {e}")
        
        # Draw tooltip if visible
        if self.tooltip_visible:
            self.draw_tooltip()
            
        # Debug rect to show touch target
        if hasattr(self, 'DEBUG') and self.DEBUG:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 1) 