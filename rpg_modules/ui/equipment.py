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
        self.player = None  # Will be set from GameState
        
        # Calculate dimensions
        # Make the UI slightly taller to accommodate cross layout and stats
        self.width = UI_DIMENSIONS['equipment_width']
        self.height = UI_DIMENSIONS['equipment_height'] + 150  # Add extra height for cross layout and stats
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
        
        # Create equipment slots in a cross pattern
        slot_size = 40
        center_x = self.x + self.width // 2 - slot_size // 2
        center_y = self.y + 100  # Center position for the cross

        self.slots = {
            # Top position (head)
            'head': pygame.Rect(center_x, center_y - slot_size - 10, slot_size, slot_size),
            # Left position (weapon)
            'weapon': pygame.Rect(center_x - slot_size - 10, center_y, slot_size, slot_size),
            # Center position (chest)
            'chest': pygame.Rect(center_x, center_y, slot_size, slot_size),
            # Right position (hands)
            'hands': pygame.Rect(center_x + slot_size + 10, center_y, slot_size, slot_size),
            # Bottom-left position (legs)
            'legs': pygame.Rect(center_x - slot_size//2 - 5, center_y + slot_size + 10, slot_size, slot_size),
            # Bottom-right position (feet)
            'feet': pygame.Rect(center_x + slot_size//2 + 5, center_y + slot_size + 10, slot_size, slot_size)
        }
        
    def set_player(self, player):
        """Set the player reference for stat calculations."""
        self.player = player
        
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
        center_x = self.x + self.width // 2 - slot_size // 2
        center_y = self.y + 100  # Center position for the cross

        self.slots = {
            # Top position (head)
            'head': pygame.Rect(center_x, center_y - slot_size - 10, slot_size, slot_size),
            # Left position (weapon)
            'weapon': pygame.Rect(center_x - slot_size - 10, center_y, slot_size, slot_size),
            # Center position (chest)
            'chest': pygame.Rect(center_x, center_y, slot_size, slot_size),
            # Right position (hands)
            'hands': pygame.Rect(center_x + slot_size + 10, center_y, slot_size, slot_size),
            # Bottom-left position (legs)
            'legs': pygame.Rect(center_x - slot_size//2 - 5, center_y + slot_size + 10, slot_size, slot_size),
            # Bottom-right position (feet)
            'feet': pygame.Rect(center_x + slot_size//2 + 5, center_y + slot_size + 10, slot_size, slot_size)
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
            
            # Draw slot label based on position
            label = self.small_font.render(slot_name.capitalize(), True, UI_COLORS['text'])
            
            # Position labels differently based on slot position
            if slot_name == 'head':
                # Above the slot
                label_x = slot_rect.x + (slot_rect.width - label.get_width()) // 2
                label_y = slot_rect.y - 20
            elif slot_name == 'weapon':
                # Left of the slot
                label_x = slot_rect.x - 5 - label.get_width()
                label_y = slot_rect.y + (slot_rect.height - label.get_height()) // 2
            elif slot_name == 'chest':
                # Below the slot
                label_x = slot_rect.x + (slot_rect.width - label.get_width()) // 2
                label_y = slot_rect.y - 20
            elif slot_name == 'hands':
                # Right of the slot
                label_x = slot_rect.x + slot_rect.width + 5
                label_y = slot_rect.y + (slot_rect.height - label.get_height()) // 2
            else:
                # Below the slots for legs and feet
                label_x = slot_rect.x + (slot_rect.width - label.get_width()) // 2
                label_y = slot_rect.y + slot_rect.height + 5
                
            screen.blit(label, (label_x, label_y))
            
            # Draw equipped item if present
            if slot_name in self.equipment and self.equipment[slot_name]:
                item = self.equipment[slot_name]
                try:
                    sprite = item.get_equipment_sprite()
                except (FileNotFoundError, pygame.error, AttributeError) as e:
                    # Create a fallback sprite based on item type
                    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
                    
                    if hasattr(item, 'weapon_type'):
                        # Weapon placeholder (sword shape)
                        color = QUALITY_COLORS.get(item.quality, (200, 200, 200))
                        pygame.draw.polygon(sprite, color, [(20, 10), (44, 10), (44, 54), (32, 54), (20, 40)])
                        pygame.draw.rect(sprite, (100, 100, 100), (25, 10, 14, 25))  # handle
                    elif hasattr(item, 'armor_type'):
                        # Armor placeholder (shield shape)
                        color = QUALITY_COLORS.get(item.quality, (200, 200, 200))
                        pygame.draw.circle(sprite, color, (32, 32), 20)
                        pygame.draw.circle(sprite, (30, 30, 30), (32, 32), 20, 2)
                    else:
                        # Generic item placeholder (diamond shape)
                        pygame.draw.polygon(sprite, (180, 180, 180), [(32, 10), (54, 32), (32, 54), (10, 32)])
                
                # Scale sprite to fit the slot
                sprite = pygame.transform.scale(sprite, (slot_size, slot_size))
                
                # Draw item centered in the slot
                item_x = slot_rect.x + (slot_rect.width - sprite.get_width()) // 2
                item_y = slot_rect.y + (slot_rect.height - sprite.get_height()) // 2
                screen.blit(sprite, (item_x, item_y))
        
        # Draw character stats section
        self._draw_character_stats(screen)
        
        # Draw tooltip if needed
        if self.tooltip_visible and self.hovered_item:
            self.draw_tooltip()
            
    def _draw_character_stats(self, screen):
        """Draw the character stats section showing base stats and equipment bonuses."""
        # Skip if no player is available
        if not self.player:
            return
            
        # Create stats section header
        stats_title = self.font.render("Character Stats", True, UI_COLORS['text'])
        stats_title_x = self.x + (self.width - stats_title.get_width()) // 2
        stats_title_y = self.y + 180  # Position below equipment slots
        screen.blit(stats_title, (stats_title_x, stats_title_y))
        
        # Calculate equipment bonuses
        attack_bonus = self._calculate_attack_bonus()
        defense_bonus = self._calculate_defense_bonus()
        dexterity_bonus = self._calculate_dexterity_bonus()
        
        # Format stats with base + bonus
        stats = [
            f"Attack: {self.player.attack}+{attack_bonus}" if attack_bonus > 0 else f"Attack: {self.player.attack}",
            f"Defense: {self.player.defense}+{defense_bonus}" if defense_bonus > 0 else f"Defense: {self.player.defense}",
        ]
        
        # Add dexterity if bonus exists
        if hasattr(self.player, 'dexterity'):
            base_dex = getattr(self.player, 'dexterity', 0)
            stats.append(f"Dexterity: {base_dex}+{dexterity_bonus}" if dexterity_bonus > 0 else f"Dexterity: {base_dex}")
        
        # Draw stats list
        y_offset = stats_title_y + 30
        for stat in stats:
            stat_surface = self.small_font.render(stat, True, UI_COLORS['text'])
            stat_x = self.x + 20
            screen.blit(stat_surface, (stat_x, y_offset))
            y_offset += 25
            
    def _calculate_attack_bonus(self) -> int:
        """Calculate attack bonus from equipped items."""
        bonus = 0
        
        # Check weapon
        weapon = self.equipment.get('weapon')
        if weapon and hasattr(weapon, 'attack_power'):
            bonus += weapon.attack_power
            
        return bonus
        
    def _calculate_defense_bonus(self) -> int:
        """Calculate defense bonus from equipped armor."""
        bonus = 0
        
        # Check all armor slots
        armor_slots = ['head', 'chest', 'legs', 'feet', 'hands']
        for slot in armor_slots:
            item = self.equipment.get(slot)
            if item and hasattr(item, 'defense'):
                bonus += item.defense
                
        return bonus
        
    def _calculate_dexterity_bonus(self) -> int:
        """Calculate dexterity bonus from equipped items."""
        bonus = 0
        
        # Mainly from hands equipment
        hands = self.equipment.get('hands')
        if hands and hasattr(hands, 'dexterity'):
            bonus += hands.dexterity
            
        # Other equipment may also provide dexterity
        for slot, item in self.equipment.items():
            if item and hasattr(item, 'dexterity') and slot != 'hands':
                bonus += item.dexterity
                
        return bonus
    
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
        stats = self.hovered_item.get_stats_display()
        for stat in stats:
            stat_text = self.small_font.render(stat, True, UI_COLORS['text'])
            self.screen.blit(stat_text, (tooltip_x + 10, tooltip_y + y_offset))
            y_offset += 20 