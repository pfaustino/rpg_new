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
            print(f"DEBUG: Inventory UI received mouse click event at {pygame.mouse.get_pos()}")
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                print(f"DEBUG: Click is within inventory rect {self.rect}")
                cell_index = self.get_cell_at_pos(mouse_pos)
                print(f"DEBUG: Cell index at position: {cell_index}")
                if cell_index is not None and cell_index < len(self.inventory):
                    item = self.inventory[cell_index]
                    print(f"DEBUG: Item at cell index {cell_index}: {item}")
                    if item:
                        print(f"DEBUG: Inventory: Clicked on item: {item.display_name} in slot {cell_index}")
                        print(f"DEBUG: Item type: {type(item).__name__}")
                        print(f"DEBUG: Item attributes: {dir(item)}")
                        if hasattr(item, 'get_stats_display'):
                            print(f"DEBUG: Item stats: {item.get_stats_display()}")
                        
                        # For armor, check armor_type attribute
                        if hasattr(item, 'armor_type'):
                            print(f"DEBUG: Item is armor with type: {item.armor_type}")
                        
                        # For hands item
                        if hasattr(item, 'is_hands'):
                            print(f"DEBUG: Item is a hands item: {item.is_hands}")
                        
                        # For weapon, check weapon_type
                        if hasattr(item, 'weapon_type'):
                            print(f"DEBUG: Item is a weapon with type: {item.weapon_type}")
                            
                        self.selected_item = item
                        
                        # Use the global GameState object to equip the item
                        import sys
                        game_state = None
                        # First try __main__ - this is the most common case when running "python game.py"
                        if '__main__' in sys.modules:
                            main_module = sys.modules['__main__']
                            print(f"DEBUG: Found __main__ module: {main_module}")
                            if hasattr(main_module, 'game_state'):
                                game_state = main_module.game_state
                                print(f"DEBUG: Found game_state in __main__ module: {game_state}")
                                
                        # Next try 'game' module
                        if game_state is None and 'game' in sys.modules:
                            game_module = sys.modules.get('game')
                            print(f"DEBUG: Found game module: {game_module}")
                            
                            # Try different ways to access game_state
                            if hasattr(game_module, 'game_state'):
                                game_state = game_module.game_state
                                print(f"DEBUG: Accessed game_state directly: {game_state}")
                            
                        # Last resort - try to find it in any module
                        if game_state is None:
                            # Try to find the game state in any module
                            print("DEBUG: Could not find game_state in expected modules, searching all modules...")
                            modules_to_check = []
                            
                            # Add modules in this order of priority
                            for name in list(sys.modules.keys()):
                                # First check main and directly imported modules
                                if name in ['__main__', 'game', 'rpg']:
                                    modules_to_check.insert(0, name)
                                # Then check RPG-related modules
                                elif 'game' in name.lower() or 'rpg' in name.lower():
                                    modules_to_check.append(name)
                            
                            print(f"DEBUG: Modules to check (priority order): {modules_to_check}")
                            
                            # Now check the modules
                            for name in modules_to_check:
                                module = sys.modules.get(name)
                                if module and hasattr(module, 'game_state'):
                                    print(f"DEBUG: Found game_state in module: {name}")
                                    game_state = module.game_state
                                    break
                                    
                            # Look for player directly 
                            if game_state is None:
                                print("DEBUG: Looking for player object directly...")
                                for name in modules_to_check:
                                    module = sys.modules.get(name)
                                    if module and hasattr(module, 'player'):
                                        print(f"DEBUG: Found player in module: {name}")
                                        player = module.player
                                        inventory_index = cell_index
                                        item = self.inventory[inventory_index] 
                                        
                                        # Directly manipulate player inventory/equipment
                                        print(f"DEBUG: Attempting direct equipment manipulation")
                                        slot = None
                                        
                                        # Determine slot based on item type
                                        if hasattr(item, 'weapon_type'):
                                            slot = 'weapon'
                                        elif hasattr(item, 'armor_type'):
                                            slot = item.armor_type.lower()
                                        elif hasattr(item, 'is_hands'):
                                            slot = 'hands'
                                            
                                        if slot and hasattr(player, 'equipment') and slot in player.equipment.slots:
                                            # Save currently equipped item
                                            current_item = player.equipment.slots[slot]
                                            
                                            # Equip new item
                                            player.equipment.slots[slot] = item
                                            
                                            # Replace inventory slot with previously equipped item
                                            self.inventory[inventory_index] = current_item
                                            
                                            print(f"DEBUG: Directly equipped {item.display_name} in slot {slot}")
                                            return True
                            
                            if game_state is None:
                                print("DEBUG: Could not find game_state in any module")
                                print("DEBUG: Available modules: ", [name for name in sys.modules.keys() if 'game' in name.lower() or 'rpg' in name.lower() or name == '__main__'])
                                return True
                            
                        # If we have a game_state, try to equip the item
                        if game_state:
                            # Try to equip the item
                            print(f"DEBUG: Attempting to call equip_item_from_inventory({cell_index})")
                            success = game_state.equip_item_from_inventory(cell_index)
                            print(f"DEBUG: equip_item_from_inventory returned: {success}")
                            if success:
                                print(f"DEBUG: Successfully equipped {item.display_name}")
                            else:
                                print(f"DEBUG: Failed to equip {item.display_name}")
                        else:
                            print("DEBUG: Could not find game_state in game module")
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
                    
                if hasattr(self.hovered_item, 'prefix') and self.hovered_item.prefix:
                    stats.insert(1, f"Effect: {self.hovered_item.prefix}")
                    
                for stat in stats:
                    stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
                    self.screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
                    y_offset += 20
            except Exception as e:
                # Handle errors when drawing tooltip
                error_text = self.small_font.render(f"Error displaying item: {str(e)}", True, (255, 100, 100))
                self.screen.blit(error_text, (tooltip_x + 10, tooltip_y + 150))
                print(f"Error drawing tooltip: {e}")
        
    def draw(self, screen: pygame.Surface):
        """Draw the inventory UI."""
        if not self.visible:
            return
            
        # Update rect position based on current x,y
        self.rect.topleft = (self.x, self.y)
        
        # Recalculate grid cell positions based on updated UI position
        grid_width = self.grid_cols * self.cell_size
        grid_height = self.grid_rows * self.cell_size
        grid_x = self.x + (self.width - grid_width) // 2
        grid_y = self.y + 50  # Leave space for header
        
        # Update grid cells
        self.grid_cells = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = grid_x + col * self.cell_size
                cell_y = grid_y + row * self.cell_size
                self.grid_cells.append(pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size))
            
        # Draw background
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw title
        title = self.font.render("Inventory", True, UI_COLORS['text'])
        title_x = self.x + (self.width - title.get_width()) // 2
        screen.blit(title, (title_x, self.y + 10))
        
        # Draw grid
        for i, cell in enumerate(self.grid_cells):
            # Draw cell background
            pygame.draw.rect(screen, UI_COLORS['cell_background'], cell)
            # Draw border
            pygame.draw.rect(screen, UI_COLORS['border'], cell, 1)
            
            # Draw item if present
            if i < len(self.inventory) and self.inventory[i]:
                try:
                    item = self.inventory[i]
                    
                    # Create placeholder sprite if item sprite can't be loaded
                    try:
                        sprite = item.get_equipment_sprite()
                    except (FileNotFoundError, pygame.error, AttributeError) as e:
                        # Create a fallback sprite based on item type
                        sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
                        
                        # Determine item type and set appropriate color
                        if hasattr(item, 'weapon_type'):
                            # Weapon placeholder (sword shape)
                            color = QUALITY_COLORS.get(item.quality, (200, 200, 200))
                            pygame.draw.polygon(sprite, color, [(20, 10), (44, 10), (44, 54), (32, 54), (20, 40)])
                            pygame.draw.rect(sprite, (100, 100, 100), (25, 10, 14, 25))  # handle
                        elif hasattr(item, 'armor_type'):
                            # Armor placeholder (shield/chest shape)
                            color = QUALITY_COLORS.get(item.quality, (200, 200, 200))
                            pygame.draw.ellipse(sprite, color, (10, 10, 44, 44))
                            pygame.draw.ellipse(sprite, (100, 100, 100), (15, 15, 34, 34), 2)
                        else:
                            # Consumable placeholder (potion shape)
                            color = (200, 50, 50) if item.consumable_type == 'health' else \
                                   (50, 50, 200) if item.consumable_type == 'mana' else \
                                   (50, 200, 50)  # stamina
                            pygame.draw.rect(sprite, (200, 200, 200), (25, 15, 14, 35))
                            pygame.draw.rect(sprite, color, (20, 25, 24, 25))
                            pygame.draw.ellipse(sprite, (200, 200, 200), (20, 10, 24, 20))
                    
                    # Scale and draw the sprite
                    scaled_sprite = pygame.transform.scale(sprite, (cell.width - 8, cell.height - 8))
                    screen.blit(scaled_sprite, (cell.x + 4, cell.y + 4))
                    
                    # Draw a quality-colored border around the item
                    border_color = QUALITY_COLORS.get(item.quality, QUALITY_COLORS['Common'])
                    inner_rect = pygame.Rect(cell.x + 3, cell.y + 3, cell.width - 6, cell.height - 6)
                    pygame.draw.rect(screen, border_color, inner_rect, 2)
                    
                except Exception as e:
                    # Draw a placeholder for error cases
                    error_surface = pygame.Surface((cell.width - 8, cell.height - 8))
                    error_surface.fill((100, 0, 0))  # Red color for error
                    screen.blit(error_surface, (cell.x + 4, cell.y + 4))
                    print(f"Error drawing inventory item: {e}")
                    
        # Draw tooltip
        if self.tooltip_visible:
            self.draw_tooltip() 