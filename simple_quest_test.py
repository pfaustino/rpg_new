import pygame
import sys
import json
import os
import random
import time

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "Simple Quest System Test"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GOLD = (218, 165, 32)

class QuestPanel:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        
        # Set up clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.normal_font = pygame.font.SysFont("Arial", 18)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Quest data
        self.quest_file_path = "data/quests/side_quests.json"
        self.quests = self.load_quests()
        self.active_quest = None if not self.quests else self.quests[0]
        
        # Player dummy data
        self.inventory = {
            "moonlight_flower": 0,
            "crystal_shard": 0
        }
        self.kills = {
            "corrupted_guardian": 0,
            "crystal_guardian": 0
        }
        self.visited_locations = set()
        self.dialog_complete = set()
        
        # UI state
        self.message = ""
        self.message_timer = 0
        self.completed_objectives = set()
        
        # Item use cooldowns
        self.item_cooldowns = {}
    
    def load_quests(self):
        """Load quests from a JSON file."""
        try:
            with open(self.quest_file_path, 'r') as f:
                data = json.load(f)
                return data.get("quests", [])
        except Exception as e:
            print(f"Error loading quests: {e}")
            return []
    
    def draw(self):
        # Clear the screen
        self.screen.fill(DARK_GRAY)
        
        # Draw title
        title_text = self.title_font.render("Quest System Test", True, WHITE)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        # Draw active quest info
        if self.active_quest:
            # Quest title
            quest_title = self.title_font.render(self.active_quest["title"], True, GOLD)
            self.screen.blit(quest_title, (30, 70))
            
            # Quest description
            desc_text = self.normal_font.render(self.active_quest["description"], True, WHITE)
            self.screen.blit(desc_text, (30, 100))
            
            # Objectives
            objective_y = 150
            for i, objective in enumerate(self.active_quest["objectives"]):
                obj_color = GREEN if i in self.completed_objectives else WHITE
                
                # Objective type icon/marker
                marker_color = self.get_objective_marker_color(objective["type"])
                objective_rect = pygame.Rect(30, objective_y, 20, 20)
                
                if objective["type"] == "kill":
                    # Triangle for kill objectives
                    points = [
                        (objective_rect.left + 10, objective_rect.top),
                        (objective_rect.left, objective_rect.bottom),
                        (objective_rect.right, objective_rect.bottom)
                    ]
                    pygame.draw.polygon(self.screen, marker_color, points)
                elif objective["type"] == "collect":
                    # Circle for collect objectives
                    pygame.draw.circle(self.screen, marker_color, 
                                     (objective_rect.centerx, objective_rect.centery), 10)
                elif objective["type"] == "explore":
                    # Square for explore objectives
                    pygame.draw.rect(self.screen, marker_color, objective_rect)
                elif objective["type"] == "dialog":
                    # Diamond for dialog objectives
                    points = [
                        (objective_rect.centerx, objective_rect.top),
                        (objective_rect.right, objective_rect.centery),
                        (objective_rect.centerx, objective_rect.bottom),
                        (objective_rect.left, objective_rect.centery)
                    ]
                    pygame.draw.polygon(self.screen, marker_color, points)
                else:
                    # Default square for other objectives
                    pygame.draw.rect(self.screen, marker_color, objective_rect)
                
                # Objective description
                obj_text = self.normal_font.render(objective["description"], True, obj_color)
                self.screen.blit(obj_text, (60, objective_y))
                
                # Progress for kill and collect objectives
                if objective["type"] == "kill":
                    monster_id = objective["target_monster"]
                    current = self.kills.get(monster_id, 0)
                    required = objective["amount"]
                    progress_text = self.small_font.render(f"Progress: {current}/{required}", True, obj_color)
                    self.screen.blit(progress_text, (60, objective_y + 25))
                elif objective["type"] == "collect":
                    item_id = objective["target_item"]
                    current = self.inventory.get(item_id, 0)
                    required = objective["amount"]
                    progress_text = self.small_font.render(f"Progress: {current}/{required}", True, obj_color)
                    self.screen.blit(progress_text, (60, objective_y + 25))
                    
                objective_y += 60
            
            # Draw rewards section
            rewards_y = objective_y + 20
            rewards_title = self.title_font.render("Rewards:", True, GOLD)
            self.screen.blit(rewards_title, (30, rewards_y))
            
            rewards_y += 35
            rewards = self.active_quest["rewards"]
            
            # XP and gold rewards
            xp_text = self.normal_font.render(f"XP: {rewards['xp']}", True, WHITE)
            self.screen.blit(xp_text, (50, rewards_y))
            
            gold_text = self.normal_font.render(f"Gold: {rewards['gold']}", True, GOLD)
            self.screen.blit(gold_text, (50, rewards_y + 30))
            
            # Item rewards
            item_y = rewards_y + 60
            if "items" in rewards and rewards["items"]:
                items_title = self.normal_font.render("Items:", True, WHITE)
                self.screen.blit(items_title, (50, item_y))
                
                for i, item in enumerate(rewards["items"]):
                    item_text = self.normal_font.render(f"- {item['name']} (x{item['amount']})", True, WHITE)
                    self.screen.blit(item_text, (70, item_y + 30 + (i * 25)))
            
            # Draw Complete Quest button if all objectives are completed
            if self.all_objectives_completed():
                complete_quest_rect = pygame.Rect(WIDTH - 250, HEIGHT - 70, 200, 50)
                pygame.draw.rect(self.screen, GOLD, complete_quest_rect)
                complete_quest_text = self.normal_font.render("Complete Quest", True, BLACK)
                self.screen.blit(complete_quest_text, (complete_quest_rect.centerx - complete_quest_text.get_width()//2,
                                             complete_quest_rect.centery - complete_quest_text.get_height()//2))
        
        # Draw inventory section
        inventory_x = WIDTH - 250
        inventory_title = self.title_font.render("Inventory", True, WHITE)
        self.screen.blit(inventory_title, (inventory_x, 70))
        
        inventory_y = 110
        if self.inventory:
            # Create a copy of the inventory items to avoid modification during iteration
            inventory_items = list(self.inventory.items())
            for i, (item_id, count) in enumerate(inventory_items):
                item_rect = pygame.Rect(inventory_x, inventory_y + (i * 40), 220, 35)
                pygame.draw.rect(self.screen, LIGHT_GRAY, item_rect)
                pygame.draw.rect(self.screen, GRAY, item_rect, 2)
                
                # Format item name from item_id
                item_name = item_id.replace("_", " ").title()
                item_text = self.normal_font.render(f"{item_name} x{count}", True, BLACK)
                self.screen.blit(item_text, (inventory_x + 10, inventory_y + 8 + (i * 40)))
                
                # Add "Use" button for consumable items
                if count > 0:
                    use_rect = pygame.Rect(inventory_x + 170, inventory_y + 5 + (i * 40), 40, 25)
                    
                    # Change button color if on cooldown
                    button_color = GREEN
                    if item_id in self.item_cooldowns:
                        current_time = time.time()
                        if current_time < self.item_cooldowns[item_id]:
                            button_color = GRAY  # Gray out if on cooldown
                    
                    pygame.draw.rect(self.screen, button_color, use_rect)
                    use_text = self.small_font.render("Use", True, BLACK)
                    self.screen.blit(use_text, (use_rect.centerx - use_text.get_width()//2, 
                                               use_rect.centery - use_text.get_height()//2))
        else:
            empty_text = self.normal_font.render("Inventory is empty", True, WHITE)
            self.screen.blit(empty_text, (inventory_x, inventory_y))
        
        # Draw test buttons
        button_y = HEIGHT - 150
        button_width = 180
        button_height = 40
        button_margin = 20
        
        # Add Item button
        add_item_rect = pygame.Rect(30, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, BLUE, add_item_rect)
        add_item_text = self.normal_font.render("Add Quest Item", True, WHITE)
        self.screen.blit(add_item_text, (add_item_rect.centerx - add_item_text.get_width()//2,
                                         add_item_rect.centery - add_item_text.get_height()//2))
        
        # Add Kill button
        add_kill_rect = pygame.Rect(30, button_y + button_height + button_margin, button_width, button_height)
        pygame.draw.rect(self.screen, RED, add_kill_rect)
        add_kill_text = self.normal_font.render("Add Monster Kill", True, WHITE)
        self.screen.blit(add_kill_text, (add_kill_rect.centerx - add_kill_text.get_width()//2,
                                         add_kill_rect.centery - add_kill_text.get_height()//2))
        
        # Complete Dialog button
        dialog_rect = pygame.Rect(30 + button_width + button_margin, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, PURPLE, dialog_rect)
        dialog_text = self.normal_font.render("Complete Dialog", True, WHITE)
        self.screen.blit(dialog_text, (dialog_rect.centerx - dialog_text.get_width()//2,
                                      dialog_rect.centery - dialog_text.get_height()//2))
        
        # Explore Location button
        explore_rect = pygame.Rect(30 + button_width + button_margin, 
                                  button_y + button_height + button_margin, 
                                  button_width, button_height)
        pygame.draw.rect(self.screen, GREEN, explore_rect)
        explore_text = self.normal_font.render("Explore Location", True, BLACK)
        self.screen.blit(explore_text, (explore_rect.centerx - explore_text.get_width()//2,
                                       explore_rect.centery - explore_text.get_height()//2))
        
        # Draw status message
        if self.message and self.message_timer > 0:
            message_text = self.normal_font.render(self.message, True, YELLOW)
            self.screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT - 40))
        
        # Update the display
        pygame.display.flip()
    
    def get_objective_marker_color(self, objective_type):
        """Get the color for objective markers based on type."""
        if objective_type == "kill":
            return RED
        elif objective_type == "collect":
            return BLUE
        elif objective_type == "explore":
            return GREEN
        elif objective_type == "dialog":
            return PURPLE
        else:
            return WHITE
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check for button clicks
                    button_y = HEIGHT - 150
                    button_width = 180
                    button_height = 40
                    button_margin = 20
                    
                    # Add Item button
                    add_item_rect = pygame.Rect(30, button_y, button_width, button_height)
                    if add_item_rect.collidepoint(mouse_pos):
                        self.add_quest_item()
                    
                    # Add Kill button
                    add_kill_rect = pygame.Rect(30, button_y + button_height + button_margin, button_width, button_height)
                    if add_kill_rect.collidepoint(mouse_pos):
                        self.add_monster_kill()
                    
                    # Complete Dialog button
                    dialog_rect = pygame.Rect(30 + button_width + button_margin, button_y, button_width, button_height)
                    if dialog_rect.collidepoint(mouse_pos):
                        self.complete_dialog()
                    
                    # Explore Location button
                    explore_rect = pygame.Rect(30 + button_width + button_margin, 
                                            button_y + button_height + button_margin, 
                                            button_width, button_height)
                    if explore_rect.collidepoint(mouse_pos):
                        self.explore_location()
                    
                    # Complete Quest button
                    if self.all_objectives_completed() and self.active_quest:
                        complete_quest_rect = pygame.Rect(WIDTH - 250, HEIGHT - 70, 200, 50)
                        if complete_quest_rect.collidepoint(mouse_pos):
                            self.complete_quest()
                    
                    # Check for item use buttons
                    inventory_x = WIDTH - 250
                    inventory_y = 110
                    if self.inventory:
                        # Create a copy of the inventory items to avoid modification during iteration
                        inventory_items = list(self.inventory.items())
                        for i, (item_id, count) in enumerate(inventory_items):
                            if count > 0:
                                use_rect = pygame.Rect(inventory_x + 170, inventory_y + 5 + (i * 40), 40, 25)
                                if use_rect.collidepoint(mouse_pos):
                                    self.use_consumable(item_id)
        
        return True
    
    def update(self):
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= self.clock.get_time()
        
        # Update item cooldowns
        current_time = time.time()
        for item_id in list(self.item_cooldowns.keys()):
            if current_time >= self.item_cooldowns[item_id]:
                del self.item_cooldowns[item_id]
        
        # Check quest objectives
        if self.active_quest:
            for i, objective in enumerate(self.active_quest["objectives"]):
                if i in self.completed_objectives:
                    continue
                
                completed = False
                if objective["type"] == "kill":
                    monster_id = objective["target_monster"]
                    required = objective["amount"]
                    if self.kills.get(monster_id, 0) >= required:
                        completed = True
                
                elif objective["type"] == "collect":
                    item_id = objective["target_item"]
                    required = objective["amount"]
                    if self.inventory.get(item_id, 0) >= required:
                        completed = True
                
                elif objective["type"] == "explore":
                    location_id = objective["target_location"]
                    if location_id in self.visited_locations:
                        completed = True
                
                elif objective["type"] == "dialog":
                    dialog_id = objective["dialog_id"]
                    if dialog_id in self.dialog_complete:
                        completed = True
                
                if completed:
                    self.completed_objectives.add(i)
                    self.show_message(f"Completed objective: {objective['description']}")
    
    def add_quest_item(self):
        if not self.active_quest:
            self.show_message("No active quest")
            return
        
        # Find a collect objective if any
        for objective in self.active_quest["objectives"]:
            if objective["type"] == "collect":
                item_id = objective["target_item"]
                self.inventory[item_id] = self.inventory.get(item_id, 0) + 1
                self.show_message(f"Added 1 {item_id.replace('_', ' ').title()} to inventory")
                return
        
        self.show_message("No collect objectives in this quest")
    
    def add_monster_kill(self):
        if not self.active_quest:
            self.show_message("No active quest")
            return
        
        # First check if there are incomplete kill objectives
        incomplete_kill_objectives = []
        for i, objective in enumerate(self.active_quest["objectives"]):
            if objective["type"] == "kill" and i not in self.completed_objectives:
                incomplete_kill_objectives.append((i, objective))
        
        if not incomplete_kill_objectives:
            self.show_message("No incomplete kill objectives in this quest")
            return
            
        # Take the first incomplete kill objective
        idx, objective = incomplete_kill_objectives[0]
        monster_id = objective["target_monster"]
        self.kills[monster_id] = self.kills.get(monster_id, 0) + 1
        self.show_message(f"Killed 1 {monster_id.replace('_', ' ').title()}")
    
    def complete_dialog(self):
        if not self.active_quest:
            self.show_message("No active quest")
            return
        
        # Find dialog objectives that haven't been completed yet
        incomplete_dialogs = []
        for i, objective in enumerate(self.active_quest["objectives"]):
            if objective["type"] == "dialog" and i not in self.completed_objectives:
                incomplete_dialogs.append((i, objective))
        
        if not incomplete_dialogs:
            self.show_message("No remaining dialog objectives in this quest")
            return
            
        # Complete the first incomplete dialog objective found
        idx, objective = incomplete_dialogs[0]
        dialog_id = objective["dialog_id"]
        self.dialog_complete.add(dialog_id)
        self.show_message(f"Completed dialog: {dialog_id}")
        
        # Mark this objective as completed
        self.completed_objectives.add(idx)
    
    def explore_location(self):
        if not self.active_quest:
            self.show_message("No active quest")
            return
        
        # Find an explore objective if any
        for objective in self.active_quest["objectives"]:
            if objective["type"] == "explore":
                location_id = objective["target_location"]
                self.visited_locations.add(location_id)
                self.show_message(f"Explored location: {location_id.replace('_', ' ').title()}")
                return
        
        self.show_message("No explore objectives in this quest")
    
    def use_consumable(self, item_id):
        """Use a consumable item from the inventory."""
        # Check if item exists in inventory
        if item_id not in self.inventory or self.inventory[item_id] <= 0:
            self.show_message(f"You don't have any {item_id.replace('_', ' ').title()}")
            return
        
        # Check if item is on cooldown
        current_time = time.time()
        if item_id in self.item_cooldowns and current_time < self.item_cooldowns[item_id]:
            remaining = int(self.item_cooldowns[item_id] - current_time)
            self.show_message(f"Item on cooldown ({remaining}s remaining)")
            return
        
        # Use the item
        self.inventory[item_id] -= 1
        if self.inventory[item_id] <= 0:
            del self.inventory[item_id]
        
        # Apply effects based on item type
        if item_id == "moonlight_flower":
            self.show_message("Used Moonlight Flower: Magic energy flows through you!")
            # Set cooldown (5 seconds)
            self.item_cooldowns[item_id] = current_time + 5
        elif item_id == "crystal_shard":
            self.show_message("Used Crystal Shard: You feel empowered by crystalline energy!")
            # Set cooldown (8 seconds)
            self.item_cooldowns[item_id] = current_time + 8
        else:
            self.show_message(f"Used {item_id.replace('_', ' ').title()}")
            # Generic cooldown (3 seconds)
            self.item_cooldowns[item_id] = current_time + 3
    
    def show_message(self, message, duration=3000):
        self.message = message
        self.message_timer = duration
    
    def all_objectives_completed(self):
        """Check if all objectives in the active quest are completed."""
        if not self.active_quest:
            return False
            
        return len(self.completed_objectives) == len(self.active_quest["objectives"])
    
    def complete_quest(self):
        """Complete the active quest and give rewards."""
        if not self.active_quest or not self.all_objectives_completed():
            return
            
        rewards = self.active_quest["rewards"]
        
        # Display reward message
        reward_message = f"Quest complete! Earned {rewards['xp']} XP and {rewards['gold']} gold"
        
        if "items" in rewards and rewards["items"]:
            item_names = [f"{item['name']} (x{item['amount']})" for item in rewards["items"]]
            reward_message += f" and items: {', '.join(item_names)}"
            
            # Add items to inventory
            for item in rewards["items"]:
                item_id = item["item_id"] if "item_id" in item else item["name"].lower().replace(" ", "_")
                amount = item["amount"]
                self.inventory[item_id] = self.inventory.get(item_id, 0) + amount
        
        self.show_message(reward_message, 5000)
        
        # Reset quest (in real game would move to next quest)
        for i in range(len(self.quests)):
            if self.quests[i] == self.active_quest:
                if i + 1 < len(self.quests):
                    self.active_quest = self.quests[i + 1]
                else:
                    self.active_quest = None
                break
                
        # Reset completed objectives for new quest
        self.completed_objectives = set()
    
    def run(self):
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update()
            
            # Draw
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    panel = QuestPanel()
    panel.run() 