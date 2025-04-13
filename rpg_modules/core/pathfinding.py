"""
Pathfinding utilities for the RPG game.
This module provides A* pathfinding functionality to help monsters navigate the game world.
"""

import heapq
import math
from typing import List, Tuple, Dict, Set, Optional

# Import game map-related constants
from rpg_modules.core.constants import TILE_SIZE

class Node:
    """A node in the A* pathfinding grid."""
    
    def __init__(self, x: int, y: int, walkable: bool = True):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.parent = None
        self.g = 0  # Cost from start to current node
        self.h = 0  # Heuristic (estimated cost from current to goal)
        self.f = 0  # Total cost (g + h)
        
    def __lt__(self, other):
        # For heap comparison
        return self.f < other.f
        
    def __eq__(self, other):
        # For comparison in closed set
        return self.x == other.x and self.y == other.y
        
    def __hash__(self):
        # For use in sets
        return hash((self.x, self.y))

def find_path(game_map, start_pos: Tuple[int, int], target_pos: Tuple[int, int], 
              max_distance: int = 20) -> Optional[List[Tuple[int, int]]]:
    """
    Find a path from start to target using A* algorithm.
    
    Args:
        game_map: The game map object with is_walkable method
        start_pos: Starting position in pixels (x, y)
        target_pos: Target position in pixels (x, y)
        max_distance: Maximum path length to search (in tiles)
        
    Returns:
        List of positions (x, y) in pixels forming the path, or None if no path is found
    """
    # Add debug print statements
    print(f"DEBUG: Pathfinding from pixel ({start_pos[0]}, {start_pos[1]}) to ({target_pos[0]}, {target_pos[1]})")
    
    # Convert pixel coordinates to tile coordinates
    start_tile_x, start_tile_y = int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE)
    target_tile_x, target_tile_y = int(target_pos[0] // TILE_SIZE), int(target_pos[1] // TILE_SIZE)
    
    print(f"DEBUG: Pathfinding from tile ({start_tile_x}, {start_tile_y}) to ({target_tile_x}, {target_tile_y})")
    
    # Check if target is unreachable (e.g., wall)
    target_walkable = game_map.is_walkable(target_tile_x, target_tile_y)
    print(f"DEBUG: Target tile walkable: {target_walkable}")
    
    if not target_walkable:
        print(f"DEBUG: Target tile is not walkable, searching for nearest walkable tile")
        # Find nearest walkable tile near the target
        nearest_walkable_found = False
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = target_tile_x + dx, target_tile_y + dy
                if game_map.is_walkable(check_x, check_y):
                    print(f"DEBUG: Found walkable tile at ({check_x}, {check_y})")
                    target_tile_x, target_tile_y = check_x, check_y
                    nearest_walkable_found = True
                    break
            if nearest_walkable_found:
                break
        if not nearest_walkable_found:
            print(f"DEBUG: No walkable tiles found near target, pathfinding failed")
            return None
    
    # Check if we're already at the target
    if start_tile_x == target_tile_x and start_tile_y == target_tile_y:
        print(f"DEBUG: Already at target tile, returning simple path")
        return [(start_pos[0], start_pos[1])]
    
    # Initialize open and closed sets
    open_set = []
    closed_set = set()
    
    # Create start and end nodes
    start_node = Node(start_tile_x, start_tile_y)
    target_node = Node(target_tile_x, target_tile_y)
    
    # Add start node to open set
    heapq.heappush(open_set, start_node)
    
    # Node lookup dictionary for faster retrieval
    nodes = {(start_node.x, start_node.y): start_node}
    
    # Define directions (including diagonals)
    directions = [
        (0, -1),  # Up
        (1, -1),  # Up-right
        (1, 0),   # Right
        (1, 1),   # Down-right
        (0, 1),   # Down
        (-1, 1),  # Down-left
        (-1, 0),  # Left
        (-1, -1)  # Up-left
    ]
    
    # Main A* loop
    steps = 0
    max_steps = 500
    print(f"DEBUG: Starting A* pathfinding with max {max_steps} steps")
    
    while open_set and steps < max_steps:  # Limit steps to prevent infinite loops
        steps += 1
        
        # Get node with lowest f score
        current = heapq.heappop(open_set)
        
        # Check if we reached the target
        if current.x == target_node.x and current.y == target_node.y:
            # Reconstruct path
            path = []
            path_length = 0
            while current:
                # Convert tile coordinates back to pixel coordinates (centered in tile)
                pixel_x = current.x * TILE_SIZE + TILE_SIZE // 2
                pixel_y = current.y * TILE_SIZE + TILE_SIZE // 2
                path.append((pixel_x, pixel_y))
                path_length += 1
                current = current.parent
            
            # Reverse path (from start to end)
            path.reverse()
            
            # Limit path length if needed
            if len(path) > max_distance:
                print(f"DEBUG: Path found with {len(path)} nodes, limiting to {max_distance}")
                path = path[:max_distance]
            else:
                print(f"DEBUG: Path found with {len(path)} nodes")
                
            return path
        
        # Add current to closed set
        closed_set.add((current.x, current.y))
        
        # Check neighbors
        for dx, dy in directions:
            neighbor_x, neighbor_y = current.x + dx, current.y + dy
            
            # Skip if neighbor is in closed set
            if (neighbor_x, neighbor_y) in closed_set:
                continue
            
            # Skip if neighbor is not walkable
            if not game_map.is_walkable(neighbor_x, neighbor_y):
                continue
            
            # Calculate distances between current node and the neighbor
            # For diagonal movement, use Euclidean distance
            if dx != 0 and dy != 0:
                # Check if we can move diagonally (both adjacent cells must be walkable)
                if (not game_map.is_walkable(current.x + dx, current.y) or 
                    not game_map.is_walkable(current.x, current.y + dy)):
                    continue
                movement_cost = 1.414  # sqrt(2)
            else:
                movement_cost = 1.0
            
            # Get or create neighbor node
            if (neighbor_x, neighbor_y) in nodes:
                neighbor = nodes[(neighbor_x, neighbor_y)]
            else:
                neighbor = Node(neighbor_x, neighbor_y)
                nodes[(neighbor_x, neighbor_y)] = neighbor
            
            # Calculate tentative g score
            tentative_g = current.g + movement_cost
            
            # Check if this path is better than any previous one
            if neighbor in [n for n in open_set] and tentative_g >= neighbor.g:
                continue
            
            # This path is the best so far, record it
            neighbor.parent = current
            neighbor.g = tentative_g
            neighbor.h = heuristic(neighbor, target_node)
            neighbor.f = neighbor.g + neighbor.h
            
            # Add to open set if not already in
            if neighbor not in [n for n in open_set]:
                heapq.heappush(open_set, neighbor)
    
    # No path found
    print(f"DEBUG: No path found after {steps} steps")
    return None

def heuristic(a: Node, b: Node) -> float:
    """Calculate the heuristic value (estimated distance) between two nodes."""
    # Using Euclidean distance for better results with diagonal movement
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def simplify_path(path: List[Tuple[int, int]], tolerance: float = 1.0) -> List[Tuple[int, int]]:
    """
    Simplify a path by removing unnecessary points.
    Uses a line-of-sight technique to reduce path complexity.
    
    Args:
        path: List of (x, y) positions
        tolerance: Higher values create more simplification
        
    Returns:
        Simplified path
    """
    if not path or len(path) <= 2:
        return path
    
    simplified = [path[0]]
    current_index = 0
    
    while current_index < len(path) - 1:
        # Look for the furthest point that maintains line of sight
        furthest_visible = current_index + 1
        
        for i in range(current_index + 2, len(path)):
            # Calculate distances (using simplified version for performance)
            d1 = math.sqrt((path[i][0] - path[current_index][0]) ** 2 + 
                          (path[i][1] - path[current_index][1]) ** 2)
            d2 = math.sqrt((path[furthest_visible][0] - path[current_index][0]) ** 2 + 
                          (path[furthest_visible][1] - path[current_index][1]) ** 2)
            
            # If this point is further and within tolerance, update furthest visible
            if d1 > d2 + tolerance:
                furthest_visible = i
        
        # Add this point to simplified path
        if furthest_visible < len(path):
            simplified.append(path[furthest_visible])
        
        # Move to this point
        current_index = furthest_visible
    
    return simplified 