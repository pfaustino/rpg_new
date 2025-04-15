"""
NPC Manager for loading and managing NPCs in the game.
"""

import os
import json
import pygame
from typing import Dict, List, Optional, Tuple, Any
from .npc import NPC
from ..core.constants import TILE_SIZE

class NPCManager:
    """Class for managing NPCs in the game world."""
    
    def __init__(self, asset_path: str = "assets/npcs"):
        """Initialize the NPC manager."""
        self.npcs: Dict[str, NPC] = {}
        self.asset_path = asset_path
        self.sprites: Dict[str, pygame.Surface] = {}
        
    def load_npcs(self, npc_data_path: str = "data/npcs.json") -> bool:
        """Load NPCs from a JSON data file."""
        if not os.path.exists(npc_data_path):
            print(f"NPC data file not found: {npc_data_path}")
            # Create a default NPC file if it doesn't exist
            self._create_default_npc_file(npc_data_path)
            
        try:
            with open(npc_data_path, 'r') as file:
                data = json.load(file)
                
            # Load NPC sprites first
            if "sprite_sheets" in data:
                for sprite_id, sprite_info in data["sprite_sheets"].items():
                    sprite_path = os.path.join(self.asset_path, sprite_info.get("file", ""))
                    if os.path.exists(sprite_path):
                        self.sprites[sprite_id] = pygame.image.load(sprite_path).convert_alpha()
                    
            # Load NPC data
            if "npcs" in data:
                for npc_data in data["npcs"]:
                    npc = NPC.from_dict(npc_data)
                    
                    # Assign sprite if specified
                    sprite_id = npc_data.get("sprite_id")
                    if sprite_id and sprite_id in self.sprites:
                        npc.set_sprite(self.sprites[sprite_id])
                        
                    self.npcs[npc.npc_id] = npc
                    
            return True
            
        except Exception as e:
            print(f"Error loading NPCs: {e}")
            return False
    
    def save_npcs(self, npc_data_path: str = "data/npcs.json") -> bool:
        """Save NPCs to a JSON data file."""
        try:
            data = {
                "sprite_sheets": {},
                "npcs": []
            }
            
            # Save sprite sheet references
            for sprite_id, sprite in self.sprites.items():
                data["sprite_sheets"][sprite_id] = {
                    "file": f"{sprite_id}.png"
                }
            
            # Save NPC data
            for npc_id, npc in self.npcs.items():
                npc_data = npc.to_dict()
                
                # Add sprite reference if NPC has one
                for sprite_id, sprite in self.sprites.items():
                    if npc.sprite is sprite:
                        npc_data["sprite_id"] = sprite_id
                        break
                        
                data["npcs"].append(npc_data)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(npc_data_path), exist_ok=True)
            
            # Write data to file
            with open(npc_data_path, 'w') as file:
                json.dump(data, file, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving NPCs: {e}")
            return False
    
    def add_npc(self, npc: NPC) -> bool:
        """Add an NPC to the manager."""
        if npc.npc_id in self.npcs:
            print(f"NPC with ID {npc.npc_id} already exists.")
            return False
            
        self.npcs[npc.npc_id] = npc
        return True
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by ID."""
        return self.npcs.get(npc_id)
    
    def remove_npc(self, npc_id: str) -> bool:
        """Remove an NPC by ID."""
        if npc_id in self.npcs:
            del self.npcs[npc_id]
            return True
        return False
    
    def update_npcs(self, dt: float, player_x: float, player_y: float):
        """Update all NPCs."""
        for npc in self.npcs.values():
            npc.update(dt, player_x, player_y)
    
    def draw_npcs(self, screen: pygame.Surface, camera_x: int, camera_y: int, zoom: float = 1.0):
        """Draw all NPCs."""
        # Sort NPCs by Y position for proper depth
        sorted_npcs = sorted(self.npcs.values(), key=lambda npc: npc.y)
        
        for npc in sorted_npcs:
            npc.draw(screen, camera_x, camera_y, zoom)
    
    def get_npc_at(self, world_x: float, world_y: float, interaction_radius: float = None) -> Optional[NPC]:
        """Get the NPC at the given world coordinates, within the interaction radius."""
        for npc_id, npc in self.npcs.items():
            npc_dist_x = abs(npc.x * TILE_SIZE - world_x)
            npc_dist_y = abs(npc.y * TILE_SIZE - world_y)
            
            # Use NPC's interaction radius if none specified
            radius = interaction_radius if interaction_radius is not None else npc.interaction_radius * TILE_SIZE
            
            if npc_dist_x <= radius and npc_dist_y <= radius:
                return npc
                
        return None
    
    def _create_default_npc_file(self, npc_data_path: str):
        """Create a default NPC file with sample NPCs."""
        sample_data = {
            "sprite_sheets": {
                "villager_male": {
                    "file": "villager_male.png"
                },
                "villager_female": {
                    "file": "villager_female.png"
                },
                "guard": {
                    "file": "guard.png"
                }
            },
            "npcs": [
                {
                    "npc_id": "captain_thorne",
                    "name": "Captain Thorne",
                    "title": "Guard Captain",
                    "x": 10,
                    "y": 10,
                    "direction": "south",
                    "dialog_id": "thorne_report",
                    "sprite_id": "guard",
                    "movement_pattern": "stationary",
                    "interaction_radius": 3,
                    "quest_giver": True
                },
                {
                    "npc_id": "seren",
                    "name": "Seren",
                    "title": "Royal Scholar",
                    "x": 15,
                    "y": 8,
                    "direction": "west",
                    "dialog_id": "seren_interrogation",
                    "sprite_id": "villager_female",
                    "movement_pattern": "patrol",
                    "patrol_points": [[15, 8], [15, 12], [18, 12], [18, 8]],
                    "interaction_radius": 2
                },
                {
                    "npc_id": "bram",
                    "name": "Bram",
                    "title": "City Guard",
                    "x": 20,
                    "y": 10,
                    "direction": "south",
                    "dialog_id": "bram_interrogation",
                    "sprite_id": "guard",
                    "movement_pattern": "stationary",
                    "interaction_radius": 2
                },
                {
                    "npc_id": "lysa",
                    "name": "Lysa",
                    "title": "Merchant",
                    "x": 25,
                    "y": 15,
                    "direction": "east",
                    "dialog_id": "lysa_interrogation",
                    "sprite_id": "villager_female",
                    "movement_pattern": "wander",
                    "wander_radius": 3,
                    "interaction_radius": 2,
                    "merchant": True
                }
            ]
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(npc_data_path), exist_ok=True)
        
        # Write data to file
        with open(npc_data_path, 'w') as file:
            json.dump(sample_data, file, indent=2)
            
        print(f"Created default NPC file at {npc_data_path}")
        
    def register_sprite(self, sprite_id: str, sprite_sheet: pygame.Surface):
        """Register a sprite sheet with a given ID."""
        self.sprites[sprite_id] = sprite_sheet
        
    def create_npc(self, npc_id: str, name: str, x: float, y: float, 
                  title: str = "", dialog_id: str = None, 
                  sprite_id: str = None, npc_type: str = None):
        """
        Create an NPC and add it to the manager.
        
        Args:
            npc_id: Unique identifier for the NPC
            name: NPC's display name
            x: X position (in tiles)
            y: Y position (in tiles)
            title: NPC's title (optional)
            dialog_id: ID for the NPC's dialog (optional)
            sprite_id: ID for the NPC's sprite (optional)
            npc_type: Type of NPC (quest_giver, merchant, etc.) (optional)
            
        Returns:
            The created NPC instance
        """
        # Create the NPC
        npc = NPC(x, y, npc_id, name, title, dialog_id)
        
        # Set sprite if specified
        if sprite_id and sprite_id in self.sprites:
            npc.set_sprite(self.sprites[sprite_id])
            
        # Set type-specific attributes
        if npc_type:
            if npc_type.lower() == "quest_giver":
                npc.quest_giver = True
            elif npc_type.lower() == "merchant":
                npc.merchant = True
                
        # Add NPC to manager
        self.add_npc(npc)
        
        return npc 