"""
Test file for dialog system.
"""

import pygame
import sys
import os
import json

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GAME_TITLE = "Dialog Test"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)

class SimpleDialog:
    """A simplified dialog UI for testing."""
    
    # Constants for UI layout
    PANEL_WIDTH = 800
    PANEL_HEIGHT = 250
    PADDING = 20
    CHOICE_SPACING = 10
    CHOICE_HEIGHT = 40
    TEXT_MARGIN = 15
    PORTRAIT_SIZE = 130
    
    def __init__(self, screen):
        """Initialize the dialog UI."""
        self.screen = screen
        self.visible = False
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.choice_font = pygame.font.Font(None, 20)
        
        # Dialog state
        self.current_dialog = None
        self.current_node_id = None
        self.npc_name = ""
        self.npc_title = ""
        self.dialog_text = []
        self.choices = []
        
        # Calculate positions
        self.x = (SCREEN_WIDTH - self.PANEL_WIDTH) // 2
        self.y = SCREEN_HEIGHT - self.PANEL_HEIGHT - 20
        
        # Choice selection
        self.hovered_choice = -1
        self.selected_choice = -1
        
    def load_dialog(self, dialog_path, dialog_id):
        """Load a dialog by ID from a JSON file."""
        try:
            with open(dialog_path, 'r') as file:
                data = json.load(file)
                
            # Check if the dialog exists
            if dialog_id in data:
                dialog_data = data[dialog_id]
                self.npc_name = dialog_data.get("character", "NPC")
                self.current_dialog = dialog_data
                
                # Start with the initial dialog node
                if "text" in dialog_data:
                    # Simple dialog format
                    self.dialog_text = [dialog_data["text"]] if isinstance(dialog_data["text"], str) else dialog_data["text"]
                    self.choices = dialog_data.get("choices", [])
                    self.current_node_id = "initial"
                    self.visible = True
                    return True
                else:
                    # Try to find dialogs array and initial node
                    initial_node = None
                    if "dialogs" in dialog_data:
                        for node in dialog_data["dialogs"]:
                            if node.get("id") == "initial":
                                initial_node = node
                                break
                    
                    if initial_node:
                        self.dialog_text = [initial_node["text"]] if isinstance(initial_node["text"], str) else initial_node["text"]
                        self.choices = initial_node.get("choices", [])
                        self.current_node_id = "initial"
                        self.visible = True
                        return True
                
            print(f"Dialog {dialog_id} not found in file")
            return False
                
        except Exception as e:
            print(f"Error loading dialog: {e}")
            return False
            
    def show_dialog_node(self, node_id):
        """Display a specific dialog node."""
        if not self.current_dialog:
            return False
            
        # Simple dialog format
        if "text" in self.current_dialog and "choices" in self.current_dialog:
            self.dialog_text = [self.current_dialog["text"]] if isinstance(self.current_dialog["text"], str) else self.current_dialog["text"]
            self.choices = self.current_dialog.get("choices", [])
            self.current_node_id = node_id
            self.visible = True
            return True
            
        # Dialog with nodes format
        if "dialogs" in self.current_dialog:
            for node in self.current_dialog["dialogs"]:
                if node.get("id") == node_id:
                    self.dialog_text = [node["text"]] if isinstance(node["text"], str) else node["text"]
                    self.choices = node.get("choices", [])
                    self.current_node_id = node_id
                    self.visible = True
                    return True
                    
        # Check if this is a special node
        if node_id == "exit":
            self.visible = False
            return True
            
        print(f"Dialog node {node_id} not found")
        return False
        
    def handle_event(self, event):
        """Handle UI events."""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # If no choices are available, any click advances/closes the dialog
                if not self.choices:
                    self.visible = False
                    return True
                
                # Check for choice clicks
                for i, choice in enumerate(self.choices):
                    choice_rect = self._get_choice_rect(i)
                    if choice_rect.collidepoint(mouse_pos):
                        self.selected_choice = i
                        next_node = choice.get("next", None)
                        
                        # If there's a next node, show it, otherwise close dialog
                        if next_node:
                            self.show_dialog_node(next_node)
                        else:
                            self.visible = False
                        
                        return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.choices:
                mouse_pos = pygame.mouse.get_pos()
                prev_hovered = self.hovered_choice
                
                # Check for choice hover
                self.hovered_choice = -1
                for i, _ in enumerate(self.choices):
                    choice_rect = self._get_choice_rect(i)
                    if choice_rect.collidepoint(mouse_pos):
                        self.hovered_choice = i
                        break
        
        return False
        
    def draw(self):
        """Draw the dialog UI."""
        if not self.visible:
            return
            
        # Draw dialog panel background
        dialog_rect = pygame.Rect(self.x, self.y, self.PANEL_WIDTH, self.PANEL_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, dialog_rect)
        pygame.draw.rect(self.screen, WHITE, dialog_rect, 2)
        
        # Draw NPC name
        if self.npc_name:
            name_text = self.title_font.render(self.npc_name, True, WHITE)
            self.screen.blit(name_text, (self.x + self.PADDING, self.y + self.PADDING))
        
        # Draw dialog text
        text_x = self.x + self.PADDING
        text_y = self.y + self.PADDING + 40  # Below name
        
        wrapped_lines = []
        for paragraph in self.dialog_text:
            # Wrap text to fit panel width
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                test_width = self.font.size(test_line)[0]
                if test_width < self.PANEL_WIDTH - self.PADDING * 2:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word + " "
            wrapped_lines.append(line)
            
        for i, line in enumerate(wrapped_lines):
            text_surface = self.font.render(line, True, WHITE)
            self.screen.blit(text_surface, (text_x, text_y + i * 25))
        
        # Draw choices if available
        if self.choices:
            self._draw_choices()
            
    def _draw_choices(self):
        """Draw dialog choices."""
        if not self.choices:
            return
            
        choice_area_height = len(self.choices) * (self.CHOICE_HEIGHT + self.CHOICE_SPACING)
        start_y = self.y + self.PANEL_HEIGHT - self.PADDING - choice_area_height
        
        for i, choice in enumerate(self.choices):
            choice_rect = self._get_choice_rect(i)
            
            # Determine background color based on hover/selection state
            bg_color = DARK_GRAY
            if i == self.selected_choice:
                bg_color = BLUE
            elif i == self.hovered_choice:
                bg_color = GRAY
                
            # Draw choice background
            pygame.draw.rect(self.screen, bg_color, choice_rect)
            pygame.draw.rect(self.screen, WHITE, choice_rect, 1)
            
            # Draw choice text
            text = choice.get("text", "")
            text_surface = self.choice_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=choice_rect.center)
            self.screen.blit(text_surface, text_rect)
            
    def _get_choice_rect(self, index):
        """Get the rectangle for a choice button."""
        choice_area_height = len(self.choices) * (self.CHOICE_HEIGHT + self.CHOICE_SPACING)
        start_y = self.y + self.PANEL_HEIGHT - self.PADDING - choice_area_height
        
        return pygame.Rect(
            self.x + self.PADDING,
            start_y + index * (self.CHOICE_HEIGHT + self.CHOICE_SPACING),
            self.PANEL_WIDTH - self.PADDING * 2,
            self.CHOICE_HEIGHT
        )

def create_test_dialog():
    """Create a test dialog file if none exists."""
    test_dialog = {
        "test_dialog": {
            "character": "Elder Malik",
            "text": "Welcome to the dialog test. This is a simple dialog system to test interactions.",
            "choices": [
                {
                    "text": "Tell me more about the dialog system.",
                    "next": "about_dialog"
                },
                {
                    "text": "How do I create dialogs?",
                    "next": "create_dialog"
                },
                {
                    "text": "Exit the conversation.",
                    "next": "exit"
                }
            ]
        },
        "about_dialog": {
            "character": "Elder Malik",
            "text": "The dialog system allows NPCs to talk with the player. It supports text display, choices, and branching conversations based on those choices.",
            "choices": [
                {
                    "text": "That's interesting. What else?",
                    "next": "dialog_features"
                },
                {
                    "text": "Go back to the main topics.",
                    "next": "test_dialog"
                }
            ]
        },
        "dialog_features": {
            "character": "Elder Malik",
            "text": "Dialogs can also trigger quests, set story flags, and be used to advance the plot of the game. They're a crucial part of the RPG experience.",
            "choices": [
                {
                    "text": "I understand now.",
                    "next": "test_dialog"
                }
            ]
        },
        "create_dialog": {
            "character": "Elder Malik",
            "text": "Dialogs are defined in JSON files. Each dialog has an ID, character name, text, and possible choices. Each choice can point to another dialog node.",
            "choices": [
                {
                    "text": "Where are these files stored?",
                    "next": "dialog_storage"
                },
                {
                    "text": "Go back to the main topics.",
                    "next": "test_dialog"
                }
            ]
        },
        "dialog_storage": {
            "character": "Elder Malik",
            "text": "Dialog files are stored in the data/quests/dialogs/ directory. They are organized by NPC or quest chain for easy management.",
            "choices": [
                {
                    "text": "That makes sense. Thanks!",
                    "next": "test_dialog"
                }
            ]
        }
    }
    
    os.makedirs("data/quests/dialogs", exist_ok=True)
    
    # Create the test dialog file
    with open("data/quests/dialogs/test_dialog.json", 'w') as file:
        json.dump(test_dialog, file, indent=2)
        
    return "data/quests/dialogs/test_dialog.json"

def main():
    """Main entry point for the dialog test."""
    # Initialize pygame
    pygame.init()
    
    # Setup screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    
    # Setup clock
    clock = pygame.time.Clock()
    
    # Create or ensure test dialog exists
    dialog_path = create_test_dialog()
    
    # Create dialog UI
    dialog = SimpleDialog(screen)
    
    # Load the test dialog
    dialog.load_dialog(dialog_path, "test_dialog")
    
    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Pass events to dialog
            dialog.handle_event(event)
        
        # Clear screen
        screen.fill((20, 20, 30))
        
        # Draw some background elements
        pygame.draw.rect(screen, (30, 30, 50), pygame.Rect(0, 0, SCREEN_WIDTH, 100))
        pygame.draw.line(screen, (50, 50, 70), (0, 100), (SCREEN_WIDTH, 100), 2)
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Dialog Test", True, WHITE)
        screen.blit(title_text, (20, 30))
        
        # Draw instructions if dialog not visible
        if not dialog.visible:
            font = pygame.font.Font(None, 36)
            text = font.render("Press SPACE to restart dialog, ESC to exit", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            # Check for SPACE key to restart dialog
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                dialog.load_dialog(dialog_path, "test_dialog")
        
        # Draw dialog
        dialog.draw()
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 