"""
Pathfinding utilities for the RPG game.
This module provides A* pathfinding functionality with wall avoidance and path smoothing.
"""

import heapq
import math
import random
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
        self.wall_penalty = 0  # Additional cost for being near walls
        self.is_doorway = False  # Whether this is a doorway tile
        
    def __lt__(self, other):
        # For heap comparison
        return self.f < other.f
        
    def __eq__(self, other):
        # For comparison in closed set
        return self.x == other.x and self.y == other.y
        
    def __hash__(self):
        # For use in sets
        return hash((self.x, self.y))

def is_doorway(game_map, x: int, y: int) -> bool:
    """Check if a tile is part of a doorway."""
    # A doorway is a walkable tile with walls on opposite sides
    if not game_map.is_walkable(x, y):
        return False
        
    # Check for walls on opposite sides
    horizontal_door = (not game_map.is_walkable(x-1, y) and not game_map.is_walkable(x+1, y))
    vertical_door = (not game_map.is_walkable(x, y-1) and not game_map.is_walkable(x, y+1))
    
    return horizontal_door or vertical_door

def calculate_wall_penalty(game_map, x: int, y: int, radius: int = 2) -> float:
    """Calculate penalty for being close to walls."""
    penalty = 0
    is_door = is_doorway(game_map, x, y)
    
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            check_x, check_y = x + dx, y + dy
            if not game_map.is_walkable(check_x, check_y):
                # Penalty decreases with distance
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < 1:  # Directly adjacent
                    # Reduce penalty for doorways
                    if is_door:
                        penalty += 0.5
                    else:
                        penalty += 2.0
                else:
                    penalty += 1.0 / distance
    return penalty

def is_stuck(game_map, x: int, y: int, stuck_threshold: int = 3) -> bool:
    """Check if a position is stuck (surrounded by walls)."""
    wall_count = 0
    walkable_neighbors = []
    
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            if not game_map.is_walkable(x + dx, y + dy):
                wall_count += 1
            else:
                walkable_neighbors.append((x + dx, y + dy))
    
    # Check if we're in a corner (two adjacent walls)
    corner_stuck = False
    if len(walkable_neighbors) >= 1:
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            if (not game_map.is_walkable(x + dx, y) and 
                not game_map.is_walkable(x, y + dy)):
                corner_stuck = True
                break
    
    return wall_count >= stuck_threshold or corner_stuck

def find_escape_path(game_map, start_x: int, start_y: int, max_distance: int = 8) -> Optional[List[Tuple[int, int]]]:
    """Find a path to escape from a stuck position."""
    # Try to find the nearest open space
    open_spaces = []
    best_space = None
    best_score = float('inf')
    
    # Search in expanding circles
    for radius in range(1, max_distance + 1):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) != radius:  # Only check the perimeter
                    continue
                    
                check_x, check_y = start_x + dx, start_y + dy
                if game_map.is_walkable(check_x, check_y):
                    # Count walkable neighbors and walls
                    walkable_count = 0
                    wall_count = 0
                    for nx in range(-1, 2):
                        for ny in range(-1, 2):
                            if nx == 0 and ny == 0:
                                continue
                            if game_map.is_walkable(check_x + nx, check_y + ny):
                                walkable_count += 1
                            else:
                                wall_count += 1
                    
                    # Calculate a score (lower is better)
                    # Prefer spaces with more walkable neighbors and fewer walls
                    distance = abs(dx) + abs(dy)
                    score = distance + (wall_count * 0.5) - (walkable_count * 0.3)
                    
                    if score < best_score and not is_stuck(game_map, check_x, check_y):
                        best_score = score
                        best_space = (check_x, check_y)
                        
                    if walkable_count >= 5:  # Very open space
                        open_spaces.append((check_x, check_y))
    
    # If we found any very open spaces, use the closest one
    if open_spaces:
        # Sort by Manhattan distance
        open_spaces.sort(key=lambda pos: abs(pos[0] - start_x) + abs(pos[1] - start_y))
        target = open_spaces[0]
        return [
            (start_x * TILE_SIZE + TILE_SIZE//2, start_y * TILE_SIZE + TILE_SIZE//2),
            (target[0] * TILE_SIZE + TILE_SIZE//2, target[1] * TILE_SIZE + TILE_SIZE//2)
        ]
    
    # If no open spaces, try the best space we found
    if best_space:
        return [
            (start_x * TILE_SIZE + TILE_SIZE//2, start_y * TILE_SIZE + TILE_SIZE//2),
            (best_space[0] * TILE_SIZE + TILE_SIZE//2, best_space[1] * TILE_SIZE + TILE_SIZE//2)
        ]
            
    # Emergency escape - just try to move to any adjacent walkable tile
    for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
        check_x, check_y = start_x + dx, start_y + dy
        if game_map.is_walkable(check_x, check_y) and not is_stuck(game_map, check_x, check_y):
            return [
                (start_x * TILE_SIZE + TILE_SIZE//2, start_y * TILE_SIZE + TILE_SIZE//2),
                (check_x * TILE_SIZE + TILE_SIZE//2, check_y * TILE_SIZE + TILE_SIZE//2)
            ]
    
    return None

def find_path(game_map, start_pos: Tuple[int, int], target_pos: Tuple[int, int], 
              max_distance: int = 20, wall_clearance: float = 1.5) -> Optional[List[Tuple[int, int]]]:
    """
    Find a path from start to target using A* algorithm with wall avoidance.
    
    Args:
        game_map: The game map object with is_walkable method
        start_pos: Starting position in pixels (x, y)
        target_pos: Target position in pixels (x, y)
        max_distance: Maximum path length to search (in tiles)
        wall_clearance: How far to stay from walls (in tiles)
    """
    # Convert pixel coordinates to tile coordinates
    start_tile_x, start_tile_y = int(start_pos[0] // TILE_SIZE), int(start_pos[1] // TILE_SIZE)
    target_tile_x, target_tile_y = int(target_pos[0] // TILE_SIZE), int(target_pos[1] // TILE_SIZE)
    
    # Check if we're stuck
    if is_stuck(game_map, start_tile_x, start_tile_y):
        # Try to find an escape path
        escape_path = find_escape_path(game_map, start_tile_x, start_tile_y)
        if escape_path:
            return escape_path
    
    # Check if target is unreachable (e.g., wall)
    target_walkable = game_map.is_walkable(target_tile_x, target_tile_y)
    
    if not target_walkable:
        # Find nearest walkable tile near the target
        nearest_walkable_found = False
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = target_tile_x + dx, target_tile_y + dy
                if game_map.is_walkable(check_x, check_y):
                    target_tile_x, target_tile_y = check_x, check_y
                    nearest_walkable_found = True
                    break
            if nearest_walkable_found:
                break
        if not nearest_walkable_found:
            return None
    
    # Check if we're already at the target
    if start_tile_x == target_tile_x and start_tile_y == target_tile_y:
        return [(start_pos[0], start_pos[1])]
    
    # Initialize open and closed sets
    open_set = []
    closed_set = set()
    
    # Create start and end nodes
    start_node = Node(start_tile_x, start_tile_y)
    target_node = Node(target_tile_x, target_tile_y)
    
    # Calculate initial wall penalties
    start_node.wall_penalty = calculate_wall_penalty(game_map, start_tile_x, start_tile_y)
    start_node.is_doorway = is_doorway(game_map, start_tile_x, start_tile_y)
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
            
            # Optimize the path
            path = optimize_path(game_map, path, wall_clearance)
            
            # Limit path length if needed
            if len(path) > max_distance:
                path = path[:max_distance]
                
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
                neighbor.wall_penalty = calculate_wall_penalty(game_map, neighbor_x, neighbor_y)
                neighbor.is_doorway = is_doorway(game_map, neighbor_x, neighbor_y)
                nodes[(neighbor_x, neighbor_y)] = neighbor
            
            # Adjust wall clearance based on whether we're in a doorway
            effective_clearance = wall_clearance
            if neighbor.is_doorway or current.is_doorway:
                effective_clearance = 0.5  # Allow closer to walls in doorways
            
            # Calculate tentative g score
            tentative_g = current.g + movement_cost + (neighbor.wall_penalty * effective_clearance)
            
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
    return None

def heuristic(a: Node, b: Node) -> float:
    """Calculate the heuristic value (estimated distance) between two nodes."""
    # Using Euclidean distance for better results with diagonal movement
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def optimize_path(game_map, path: List[Tuple[int, int]], wall_clearance: float) -> List[Tuple[int, int]]:
    """
    Optimize the path by smoothing and ensuring wall clearance.
    """
    if len(path) <= 2:
        return path
    
    def is_clear_line(start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if there's a clear line between two points with wall clearance."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 1:
            return True
            
        steps = int(distance / (TILE_SIZE / 2))  # Check every half tile
        if steps < 2:
            steps = 2
            
        for i in range(steps + 1):
            t = i / steps
            x = int((start[0] + dx * t) / TILE_SIZE)
            y = int((start[1] + dy * t) / TILE_SIZE)
            
            # Check if this is a doorway
            is_door = is_doorway(game_map, x, y)
            effective_clearance = 0.5 if is_door else wall_clearance
            
            # Check surrounding tiles for wall clearance
            clear = True
            for cx in range(-1, 2):
                for cy in range(-1, 2):
                    check_x, check_y = x + cx, y + cy
                    if not game_map.is_walkable(check_x, check_y):
                        # Calculate distance to wall
                        wall_dist = math.sqrt(cx * cx + cy * cy)
                        if wall_dist < effective_clearance:
                            clear = False
                            break
                if not clear:
                    break
            
            if not clear:
                return False
        
        return True
    
    # Optimize the path
    result = [path[0]]
    current_point = 0
    
    while current_point < len(path) - 1:
        # Look ahead for furthest point we can move to directly
        furthest_visible = current_point + 1
        
        for i in range(current_point + 2, len(path)):
            if is_clear_line(path[current_point], path[i]):
                furthest_visible = i
        
        result.append(path[furthest_visible])
        current_point = furthest_visible
    
    return result

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