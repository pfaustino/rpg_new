"""
Item Generator UI component for RPG games.
"""

import pygame
import random
from typing import Optional, Dict, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, WEAPON_TYPES, ARMOR_TYPES, QUALITIES
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

    def update(self):
        """Update UI state."""
        pass  # No tooltip functionality needed for item generator

    def handle_event(self, event: pygame.event.Event, player) -> bool:
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle type dropdown
            if self.type_dropdown.collidepoint(mouse_pos):
                self.type_expanded = not self.type_expanded
                self.quality_expanded = False
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
                        return True
            
            # Handle quality dropdown
            if self.quality_dropdown.collidepoint(mouse_pos):
                self.quality_expanded = not self.quality_expanded
                self.type_expanded = False
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
                        return True
            
            # Handle generate button
            if self.generate_button.collidepoint(mouse_pos):
                # Determine type if random
                item_type = self.selected_type
                if item_type == 'Random':
                    item_type = random.choice(['Weapon', 'Armor', 'Consumable'])
                
                # Determine quality if random
                quality = self.selected_quality
                if quality == 'Random':
                    quality = random.choice(QUALITIES)
                
                # Generate the item
                self.preview_item = self.item_generator.generate_item(item_type.lower(), quality)
                
                # Add to player's inventory
                if self.preview_item and player.inventory.add_item(self.preview_item):
                    return True
        return False

    def draw(self, screen: pygame.Surface, player):
        """Draw the generator UI."""
        if not self.visible:
            return
            
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
        
        # Draw expanded type options
        if self.type_expanded:
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
        
        # Draw quality dropdown
        pygame.draw.rect(screen, UI_COLORS['cell_background'], self.quality_dropdown)
        pygame.draw.rect(screen, UI_COLORS['border'], self.quality_dropdown, 2)
        quality_text = self.font.render(f"Quality: {self.selected_quality}", True, UI_COLORS['text'])
        screen.blit(quality_text, (self.quality_dropdown.x + 10, self.quality_dropdown.y + 10))
        
        # Draw expanded quality options
        if self.quality_expanded:
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
            
            # Draw quality-colored border
            border_color = QUALITY_COLORS.get(self.preview_item.quality, QUALITY_COLORS['Common'])
            pygame.draw.rect(screen, border_color, self.preview_rect, 3)
            
            # Draw item sprite
            sprite = self.preview_item.get_equipment_sprite()
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
            
            # Draw item stats
            stats = self.preview_item.get_stats_display()
            for i, stat in enumerate(stats, 1):
                stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
                screen.blit(stat_text, (info_x, info_y + i * 25)) 