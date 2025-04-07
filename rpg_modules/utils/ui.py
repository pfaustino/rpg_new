"""
Common UI drawing utilities.
"""

import pygame
from typing import Tuple, Optional

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              color: Tuple[int, int, int], x: int, y: int,
              align: str = "left", center: bool = False) -> None:
    """
    Draw text on a surface with various alignment options.
    
    Args:
        surface: The surface to draw on
        text: The text to draw
        font: The font to use
        color: The color of the text (RGB tuple)
        x: The x position
        y: The y position
        align: Text alignment ("left", "center", or "right")
        center: Whether to center the text vertically
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "right":
        text_rect.right = x
    elif align == "center":
        text_rect.centerx = x
    else:  # left align
        text_rect.left = x
    
    if center:
        text_rect.centery = y
    else:
        text_rect.top = y
    
    surface.blit(text_surface, text_rect)

def draw_rect_with_border(surface: pygame.Surface, rect: Tuple[int, int, int, int],
                         color: Tuple[int, int, int], border_color: Tuple[int, int, int],
                         border_width: int = 1) -> None:
    """
    Draw a rectangle with a border.
    
    Args:
        surface: The surface to draw on
        rect: The rectangle dimensions (x, y, width, height)
        color: The fill color (RGB tuple)
        border_color: The border color (RGB tuple)
        border_width: The width of the border
    """
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width) 