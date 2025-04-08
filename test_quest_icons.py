import pygame
import sys
from rpg_modules.quests.base import QuestReward

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Quest Icons Test")
clock = pygame.time.Clock()

# Create test rewards
test_rewards = [
    # Monster icons with different types
    QuestReward("Slay the Dragon", icon="monster_dragon"),
    QuestReward("Hunt Goblins", icon="monster_goblin"),
    QuestReward("Defeat Skeletons", icon="monster_skeleton"),
    QuestReward("Catch Slimes", icon="monster_slime"),
    
    # Basic reward icons
    QuestReward("1000 Gold", icon="gold"),
    QuestReward("Magic Sword", icon="item", icon_color=(0, 255, 255)),  # Cyan for magic items
    QuestReward("Experience", icon="exp"),
]

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

    # Clear screen
    screen.fill((40, 40, 40))  # Dark gray background

    # Draw icons in a grid
    icon_size = 64  # Larger size for better visibility
    spacing = 100
    start_x = 100
    start_y = 100

    # Draw icons with labels
    font = pygame.font.Font(None, 24)
    for i, reward in enumerate(test_rewards):
        x = start_x + (i % 4) * spacing
        y = start_y + (i // 4) * spacing

        # Draw icon
        icon_surface = reward.get_icon_surface(icon_size)
        screen.blit(icon_surface, (x, y))

        # Draw label
        text = font.render(reward.description, True, (255, 255, 255))
        screen.blit(text, (x, y + icon_size + 10))

    # Draw instructions
    instructions = [
        "Quest Icons Test",
        "Press ESC to exit",
        "",
        "Features:",
        "- Dragon: Breathing fire animation",
        "- Skeleton: Glowing eyes",
        "- Slime: Bouncing animation",
        "- Gold: Rotating shine",
        "- Item: Pulsing glow",
        "- Experience: Rotating star"
    ]

    y = 400
    for line in instructions:
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (50, y))
        y += 25

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Cleanup
pygame.quit()
sys.exit() 