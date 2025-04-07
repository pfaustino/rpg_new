"""
Item generator UI component for RPG games.
"""

import pygame
import random
from typing import Optional, Tuple, List
from ..core.constants import (
    UI_COLORS, UI_DIMENSIONS, QUALITY_COLORS,
    FONT_SIZES, QUALITIES
)
from ..items import Item, Weapon, Armor, Hands, Consumable
from ..items.generator import generate_weapon, generate_armor, generate_consumable

class ItemGeneratorUI:
    def __init__(self, x: int, y: int, width: int = 400, height: int = 500):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        
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
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Initialize preview item
        self.preview_item = None

    def update(self):
        """Update UI state."""
        pass  # No tooltip functionality needed for item generator

    def handle_event(self, event: pygame.event.Event, player) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle type dropdown
            if self.type_dropdown.collidepoint(mouse_pos):
                self.type_expanded = not self.type_expanded
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
                if item_type == 'Weapon':
                    self.preview_item = generate_weapon(quality)
                elif item_type == 'Armor':
                    self.preview_item = generate_armor(quality)
                else:  # Consumable
                    self.preview_item = generate_consumable(quality)
                
                # Add to player's inventory
                if self.preview_item and player.inventory.add_item(self.preview_item):
                    return True
        return False

    def draw(self, screen: pygame.Surface, player):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw header
        header_text = self.font.render("Item Generator", True, (255, 255, 255))
        screen.blit(header_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw type dropdown
        pygame.draw.rect(screen, (30, 30, 30), self.type_dropdown)
        pygame.draw.rect(screen, (255, 255, 255), self.type_dropdown, 2)
        type_text = self.font.render(f"Type: {self.selected_type}", True, (255, 255, 255))
        screen.blit(type_text, (self.type_dropdown.x + 10, self.type_dropdown.y + 10))
        
        # Draw quality dropdown
        pygame.draw.rect(screen, (30, 30, 30), self.quality_dropdown)
        pygame.draw.rect(screen, (255, 255, 255), self.quality_dropdown, 2)
        quality_text = self.font.render(f"Quality: {self.selected_quality}", True, (255, 255, 255))
        screen.blit(quality_text, (self.quality_dropdown.x + 10, self.quality_dropdown.y + 10))
        
        # Draw generate button
        pygame.draw.rect(screen, (40, 40, 40), self.generate_button)
        pygame.draw.rect(screen, (255, 255, 255), self.generate_button, 2)
        generate_text = self.font.render("Generate Item", True, (255, 255, 255))
        text_rect = generate_text.get_rect(center=self.generate_button.center)
        screen.blit(generate_text, text_rect)
        
        # Draw preview area if there's an item
        if self.preview_item:
            # Draw preview background
            pygame.draw.rect(screen, (30, 30, 30), self.preview_rect)
            
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
            text_x = sprite_x + 120
            text_y = self.preview_rect.y + 10
            line_spacing = 25
            
            # Draw item name
            name_text = self.font.render(self.preview_item.display_name, True, (255, 255, 255))
            screen.blit(name_text, (text_x, text_y))
            
            # Draw item stats
            stats = []
            if isinstance(self.preview_item, Weapon):
                stats = [
                    f"Type: {self.preview_item.weapon_type}",
                    f"Attack: {self.preview_item.attack_power}",
                    f"Material: {self.preview_item.material}",
                    f"Quality: {self.preview_item.quality}"
                ]
            elif isinstance(self.preview_item, Armor):
                stats = [
                    f"Type: {self.preview_item.armor_type}",
                    f"Defense: {self.preview_item.defense}",
                    f"Material: {self.preview_item.material}",
                    f"Quality: {self.preview_item.quality}"
                ]
            elif isinstance(self.preview_item, Consumable):
                stats = [
                    f"Type: {self.preview_item.consumable_type}",
                    f"Effect: {self.preview_item.effect_value}",
                    f"Quality: {self.preview_item.quality}"
                ]
            
            for i, stat in enumerate(stats):
                stat_text = self.small_font.render(stat, True, (255, 255, 255))
                screen.blit(stat_text, (text_x, text_y + (i + 1) * line_spacing)) 