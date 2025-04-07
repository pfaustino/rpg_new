"""
Font loading and management utilities.
"""

import pygame
from typing import Dict

# Cache for loaded fonts
_font_cache: Dict[int, pygame.font.Font] = {}

def get_font(size: int) -> pygame.font.Font:
    """Get a font of the specified size, using caching for efficiency."""
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size] 