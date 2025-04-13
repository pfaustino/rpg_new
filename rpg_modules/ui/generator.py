"""
Item Generator UI component for RPG games.
"""

import pygame
import random
from typing import Optional, Dict, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, WEAPON_TYPES, ARMOR_TYPES, QUALITIES,
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from ..items import Item, Weapon, Armor, Hands, Consumable
from ..items.generator import ItemGenerator

class ItemGeneratorUI:
    """A reusable item generator UI component for pygame games."""
    
    def __init__(self, x: int, y: int, width: int = 400, height: int = 500):
        """
        Initialize the item generator UI.
        
        Args:
            x: X position of the generator panel
            y: Y position of the generator panel
            width: Width of the generator panel
            height: Height of the generator panel
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        
        # Initialize fonts
        self.font = pygame.font.Font(None, FONT_SIZES['medium'])
        self.small_font = pygame.font.Font(None, FONT_SIZES['small'])
        
        # Create type dropdown
        self.type_dropdown = pygame.Rect(x + 10, y + 50, width - 20, 40)
        self.type_options = ['Random', 'Weapon', 'Armor', 'Consumable']
        self.selected_type = 'Random'
        self.type_expanded = False
        
        # Create quality dropdown
        self.quality_dropdown = pygame.Rect(x + 10, y + 120, width - 20, 40)
        self.quality_options = ['Random'] + QUALITIES
        self.selected_quality = 'Random'
        self.quality_expanded = False
        
        # Create generate button
        self.generate_button = pygame.Rect(x + 10, y + 190, width - 20, 40)
        
        # Create preview area (positioned below the generate button)
        self.preview_rect = pygame.Rect(x + 10, y + 250, width - 20, 200)
        
        # Initialize preview item
        self.preview_item = None
        
        # Initialize item generator
        self.item_generator = ItemGenerator()
        
    def toggle(self):
        """Toggle visibility of the generator UI."""
        self.visible = not self.visible
        if not self.visible:
            self.preview_item = None
            self.type_expanded = False
            self.quality_expanded = False
        else:
            # When showing the generator UI, add some test items to the inventory
            try:
                print("\nAdding test items to inventory when generator UI is shown...")
                import game
                if hasattr(game, 'game_state') and game.game_state:
                    player = game.game_state.player
                    
                    # Force reset inventory
                    capacity = 40  # 8 rows x 5 cols
                    player.inventory.items = [None] * capacity
                    print(f"Reset inventory to {capacity} empty slots")
                    
                    # Add 5 test items directly to the first slots
                    for i in range(5):
                        item = self.item_generator.generate_item()
                        if item:
                            player.inventory.items[i] = item
                            print(f"Added test item directly to inventory slot {i}: {item.display_name}")
                    
                    # Refresh inventory UI
                    if hasattr(game.game_state, 'refresh_inventory_ui'):
                        game.game_state.refresh_inventory_ui()
                        print("Refreshed inventory UI")
                    else:
                        print("Could not refresh inventory UI - method not found")
                    
                    # Debug info
                    filled_slots = sum(1 for item in player.inventory.items if item is not None)
                    print(f"Inventory now has {filled_slots}/{len(player.inventory.items)} items")
            except Exception as e:
                print(f"Error adding test items when showing generator UI: {e}")
                import traceback
                traceback.print_exc()

    def update(self):
        """Update UI state."""
        pass  # No tooltip functionality needed for item generator

    def handle_event(self, event: pygame.event.Event, player) -> bool:
        """Handle UI events."""
        if not self.visible:
            print("ItemGeneratorUI is not visible. Ignoring event.")
            return False
            
        print(f"Handling event: {event}")
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            print(f"Mouse position: {mouse_pos}")
            
            # Handle type dropdown
            if self.type_dropdown.collidepoint(mouse_pos):
                self.type_expanded = not self.type_expanded
                self.quality_expanded = False
                print(f"Toggled type dropdown: {self.type_expanded}")
                return True
            elif self.type_expanded:
                for i, option in enumerate(self.type_options):
                    option_rect = pygame.Rect(
                        self.type_dropdown.x,
                        self.type_dropdown.y + (i + 1) * 40,
                        self.type_dropdown.width,
                        40
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_type = option
                        self.type_expanded = False
                        print(f"Selected type: {self.selected_type}")
                        return True
            
            # Handle quality dropdown
            if self.quality_dropdown.collidepoint(mouse_pos):
                self.quality_expanded = not self.quality_expanded
                self.type_expanded = False
                print(f"Toggled quality dropdown: {self.quality_expanded}")
                return True
            elif self.quality_expanded:
                for i, option in enumerate(self.quality_options):
                    option_rect = pygame.Rect(
                        self.quality_dropdown.x,
                        self.quality_dropdown.y + (i + 1) * 40,
                        self.quality_dropdown.width,
                        40
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_quality = option
                        self.quality_expanded = False
                        print(f"Selected quality: {self.selected_quality}")
                        return True
            
            # Handle generate button
            if self.generate_button.collidepoint(mouse_pos):
                print("Generate button clicked.")
                try:
                    # Determine type if random
                    item_type = self.selected_type
                    if item_type == 'Random':
                        item_type = random.choice(['Weapon', 'Armor', 'Consumable'])
                    
                    # Determine quality if random
                    quality = self.selected_quality
                    if quality == 'Random':
                        quality = random.choice(QUALITIES)
                    
                    # Generate the item
                    print(f"\nGenerating new {quality} {item_type}...")
                    self.preview_item = self.item_generator.generate_item(item_type.lower(), quality)
                    
                    if self.preview_item:
                        print(f"Successfully generated: {self.preview_item.display_name}")
                        # Debug info about the item
                        if hasattr(self.preview_item, 'weapon_type'):
                            print(f"Weapon Type: {self.preview_item.weapon_type}, Attack: {self.preview_item.attack_power}")
                        elif hasattr(self.preview_item, 'armor_type'):
                            print(f"Armor Type: {self.preview_item.armor_type}, Defense: {self.preview_item.defense}")
                        elif hasattr(self.preview_item, 'consumable_type'):
                            print(f"Consumable Type: {self.preview_item.consumable_type}, Effect: {self.preview_item.effect_value}")
                            
                        # Add to player's inventory if successful
                        print("Attempting to add item to inventory...")
                        
                        # Debug check if player is None
                        if player is None:
                            print("DEBUG: Error - Player object is None")
                            return True
                            
                        # Debug inventory state before adding item
                        try:
                            filled_slots = sum(1 for item in player.inventory.items if item is not None)
                            total_slots = len(player.inventory.items)
                            print(f"DEBUG: Current inventory state: {filled_slots}/{total_slots} slots filled")
                            
                            # Check if inventory is full
                            if filled_slots >= total_slots:
                                print("DEBUG: Inventory appears to be full!")
                            
                            # Try to add item and catch any exceptions
                            try:
                                success = player.inventory.add_item(self.preview_item)
                                print(f"DEBUG: Result of add_item: {success}")
                                
                                if success:
                                    print(f"Item successfully added to inventory")
                                    # Check inventory state after adding
                                    filled_slots_after = sum(1 for item in player.inventory.items if item is not None)
                                    print(f"DEBUG: Inventory after add: {filled_slots_after}/{total_slots} slots filled")
                                    
                                    # Attempt to refresh the inventory UI through GameState
                                    try:
                                        # First try to get it from the global game module
                                        import game
                                        if hasattr(game, 'game_state') and game.game_state:
                                            if hasattr(game.game_state, 'refresh_inventory_ui'):
                                                game.game_state.refresh_inventory_ui()
                                                print("Successfully refreshed inventory UI through game_state")
                                            else:
                                                print("game_state exists but has no refresh_inventory_ui method")
                                                # Fallback: Try to directly update the inventory UI
                                                if hasattr(game.game_state, 'inventory_ui'):
                                                    game.game_state.inventory_ui.inventory = player.inventory.items
                                                    print("Directly updated inventory UI reference")
                                        else:
                                            print("game_state not available for refreshing UI")
                                    except Exception as refresh_err:
                                        print(f"Could not refresh inventory UI: {refresh_err}")
                                else:
                                    print(f"DEBUG: Failed to add item - inventory may be full or add_item returned False")
                            except Exception as add_error:
                                print(f"DEBUG: Exception occurred during add_item: {str(add_error)}")
                                import traceback
                                traceback.print_exc()
                        except Exception as inventory_error:
                            print(f"DEBUG: Exception accessing player inventory: {str(inventory_error)}")
                            import traceback
                            traceback.print_exc()
                            
                        return True
                    else:
                        print("Failed to generate item - item generator returned None")
                except Exception as e:
                    print(f"Error generating item: {str(e)}")
                    import traceback
                    traceback.print_exc()
        return False

    def draw(self, screen: pygame.Surface, player):
        """Draw the generator UI."""
        if not self.visible:
            return
        
        # Update rect and UI element positions if x,y coordinates have changed
        if (self.rect.x, self.rect.y) != (self.rect.topleft):
            self.rect.topleft = (self.rect.x, self.rect.y)
            
            # Update dropdown positions
            self.type_dropdown.x = self.rect.x + 10
            self.type_dropdown.y = self.rect.y + 50
            
            self.quality_dropdown.x = self.rect.x + 10
            self.quality_dropdown.y = self.rect.y + 120
            
            self.generate_button.x = self.rect.x + 10
            self.generate_button.y = self.rect.y + 190
            
            self.preview_rect.x = self.rect.x + 10
            self.preview_rect.y = self.rect.y + 250
        
        # Draw background
        pygame.draw.rect(screen, UI_COLORS['background'], self.rect)
        pygame.draw.rect(screen, UI_COLORS['border'], self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Item Generator", True, UI_COLORS['text'])
        header_rect = header_text.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(header_text, header_rect)
        
        # Draw type dropdown
        pygame.draw.rect(screen, UI_COLORS['cell_background'], self.type_dropdown)
        pygame.draw.rect(screen, UI_COLORS['border'], self.type_dropdown, 2)
        type_text = self.font.render(f"Type: {self.selected_type}", True, UI_COLORS['text'])
        screen.blit(type_text, (self.type_dropdown.x + 10, self.type_dropdown.y + 10))
        
        # Draw quality dropdown
        pygame.draw.rect(screen, UI_COLORS['cell_background'], self.quality_dropdown)
        pygame.draw.rect(screen, UI_COLORS['border'], self.quality_dropdown, 2)
        quality_text = self.font.render(f"Quality: {self.selected_quality}", True, UI_COLORS['text'])
        screen.blit(quality_text, (self.quality_dropdown.x + 10, self.quality_dropdown.y + 10))
        
        # Draw generate button
        pygame.draw.rect(screen, UI_COLORS['cell_background'], self.generate_button)
        pygame.draw.rect(screen, UI_COLORS['border'], self.generate_button, 2)
        generate_text = self.font.render("Generate Item", True, UI_COLORS['text'])
        text_rect = generate_text.get_rect(center=self.generate_button.center)
        screen.blit(generate_text, text_rect)
        
        # Draw preview area if there's an item
        if self.preview_item:
            # Draw preview background
            pygame.draw.rect(screen, UI_COLORS['cell_background'], self.preview_rect)
            
            # Draw quality-colored border with debug output
            quality = getattr(self.preview_item, 'quality', 'Common')
            print(f"DEBUG: Item quality: {quality}, Type: {type(quality)}")
            border_color = QUALITY_COLORS.get(quality, QUALITY_COLORS['Common'])
            print(f"DEBUG: Border color: {border_color}, Available colors: {list(QUALITY_COLORS.keys())}")
            pygame.draw.rect(screen, border_color, self.preview_rect, 3)
            
            try:
                # Try to get the item sprite with fallback for missing sprites
                try:
                    sprite = self.preview_item.get_equipment_sprite()
                except (FileNotFoundError, pygame.error):
                    # Create a placeholder sprite
                    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
                    # Draw based on item type
                    if hasattr(self.preview_item, 'weapon_type'):
                        # Weapon placeholder (sword shape)
                        color = QUALITY_COLORS.get(quality, (200, 200, 200))
                        pygame.draw.polygon(sprite, color, [(20, 10), (44, 10), (44, 54), (32, 54), (20, 40)])
                        pygame.draw.rect(sprite, (100, 100, 100), (25, 10, 14, 25))  # handle
                    elif hasattr(self.preview_item, 'armor_type'):
                        # Armor placeholder (shield/chest shape)
                        color = QUALITY_COLORS.get(quality, (200, 200, 200))
                        pygame.draw.ellipse(sprite, color, (10, 10, 44, 44))
                        pygame.draw.ellipse(sprite, (100, 100, 100), (15, 15, 34, 34), 2)
                    else:
                        # Consumable placeholder (potion shape)
                        color = (200, 50, 50) if self.preview_item.consumable_type == 'health' else \
                               (50, 50, 200) if self.preview_item.consumable_type == 'mana' else \
                               (50, 200, 50)  # stamina
                        pygame.draw.rect(sprite, (200, 200, 200), (25, 15, 14, 35))
                        pygame.draw.rect(sprite, color, (20, 25, 24, 25))
                        pygame.draw.ellipse(sprite, (200, 200, 200), (20, 10, 24, 20))
                
                # Scale the sprite
                scaled_sprite = pygame.transform.scale(sprite, (100, 100))
                sprite_x = self.preview_rect.x + 10
                sprite_y = self.preview_rect.y + 10
                screen.blit(scaled_sprite, (sprite_x, sprite_y))
                
                # Draw item info
                info_x = sprite_x + 120
                info_y = sprite_y
                
                # Draw item name
                name_text = self.font.render(self.preview_item.display_name, True, UI_COLORS['text'])
                screen.blit(name_text, (info_x, info_y))
                
                # Debug print of item attributes
                print(f"DEBUG: Item attributes: {dir(self.preview_item)}")
                
                # Draw item stats with better error handling
                try:
                    # Try to get stats display from the item
                    stats = self.preview_item.get_stats_display()
                    print(f"DEBUG: Item stats: {stats}")
                    
                    # Add missing stats if not included
                    if hasattr(self.preview_item, 'attack_power') and not any('Attack' in s for s in stats):
                        stats.append(f"Attack: {self.preview_item.attack_power}")
                    if hasattr(self.preview_item, 'defense') and not any('Defense' in s for s in stats):
                        stats.append(f"Defense: {self.preview_item.defense}")
                    if hasattr(self.preview_item, 'dexterity') and not any('Dexterity' in s for s in stats):
                        stats.append(f"Dexterity: {self.preview_item.dexterity}")
                    if hasattr(self.preview_item, 'effect_value') and not any('Effect Value' in s for s in stats):
                        stats.append(f"Effect Value: {self.preview_item.effect_value}")
                        
                    for i, stat in enumerate(stats, 1):
                        stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
                        screen.blit(stat_text, (info_x, info_y + i * 25))
                except Exception as e:
                    print(f"DEBUG: Error getting stats: {str(e)}")
                    # Fallback to showing basic attributes
                    attributes = []
                    if hasattr(self.preview_item, 'quality'):
                        attributes.append(f"Quality: {self.preview_item.quality}")
                    if hasattr(self.preview_item, 'weapon_type'):
                        attributes.append(f"Type: {self.preview_item.weapon_type}")
                    if hasattr(self.preview_item, 'armor_type'):
                        attributes.append(f"Type: {self.preview_item.armor_type}")
                    if hasattr(self.preview_item, 'attack_power'):
                        attributes.append(f"Attack: {self.preview_item.attack_power}")
                    if hasattr(self.preview_item, 'defense'):
                        attributes.append(f"Defense: {self.preview_item.defense}")
                    if hasattr(self.preview_item, 'consumable_type'):
                        attributes.append(f"Type: {self.preview_item.consumable_type}")
                    if hasattr(self.preview_item, 'effect_value'):
                        attributes.append(f"Effect: {self.preview_item.effect_value}")
                        
                    for i, attr in enumerate(attributes, 1):
                        attr_text = self.small_font.render(attr, True, UI_COLORS['text'])
                        screen.blit(attr_text, (info_x, info_y + i * 25))
            except Exception as e:
                # If any error occurs, display error message
                error_text = self.small_font.render(f"Error displaying item: {str(e)}", True, (255, 50, 50))
                screen.blit(error_text, (self.preview_rect.x + 10, self.preview_rect.y + 10))
        
        # Draw expanded dropdown options AFTER everything else to ensure they're on top
        # Draw expanded type options
        if self.type_expanded:
            # Draw a semitransparent overlay to make dropdown stand out
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            screen.blit(overlay, (0, 0))
            
            for i, option in enumerate(self.type_options):
                option_rect = pygame.Rect(
                    self.type_dropdown.x,
                    self.type_dropdown.y + (i + 1) * 40,
                    self.type_dropdown.width,
                    40
                )
                pygame.draw.rect(screen, UI_COLORS['cell_background'], option_rect)
                pygame.draw.rect(screen, UI_COLORS['border'], option_rect, 1)
                option_text = self.font.render(option, True, UI_COLORS['text'])
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10))
        
        # Draw expanded quality options
        if self.quality_expanded:
            # Draw a semitransparent overlay if not already drawn
            if not self.type_expanded:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
                screen.blit(overlay, (0, 0))
                
            for i, option in enumerate(self.quality_options):
                option_rect = pygame.Rect(
                    self.quality_dropdown.x,
                    self.quality_dropdown.y + (i + 1) * 40,
                    self.quality_dropdown.width,
                    40
                )
                pygame.draw.rect(screen, UI_COLORS['cell_background'], option_rect)
                border_color = QUALITY_COLORS.get(option, UI_COLORS['border'])
                pygame.draw.rect(screen, border_color, option_rect, 2)
                option_text = self.font.render(option, True, UI_COLORS['text'])
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10)) 