"""
Tile registry. Defines all tile types and their properties.
"""

# Tile ID to properties mapping
TILES = {
    # Base tiles (walkable terrain)
    "grass": {
        "id": "grass",
        "layer": "base",
        "color": (34, 139, 34),  # Forest green
        "walkable": True,
        "resource_node": None,
    },
    "stone": {
        "id": "stone",
        "layer": "base",
        "color": (105, 105, 105),  # Dim gray
        "walkable": True,
        "resource_node": None,
    },
    "sand": {
        "id": "sand",
        "layer": "base",
        "color": (210, 180, 140),  # Tan
        "walkable": True,
        "resource_node": None,
    },
    "dirt": {
        "id": "dirt",
        "layer": "base",
        "color": (139, 69, 19),  # Saddle brown
        "walkable": True,
        "resource_node": None,
    },
    "path": {
        "id": "path",
        "layer": "base",
        "color": (120, 85, 60),  # Worn dirt-brown fallback color
        "walkable": True,
        "resource_node": None,
    },
    "shallow_water": {
        "id": "shallow_water",
        "layer": "base",
        "color": (100, 149, 237),  # Cornflower blue
        "walkable": True,  # Can wade
        "resource_node": None,
    },
    "deep_water": {
        "id": "deep_water",
        "layer": "base",
        "color": (0, 51, 102),  # Dark blue
        "walkable": False,
        "resource_node": None,
    },
    "lava": {
        "id": "lava",
        "layer": "base",
        "color": (255, 69, 0),  # Red orange
        "walkable": False,
        "resource_node": None,
    },
    "ice": {
        "id": "ice",
        "layer": "base",
        "color": (173, 216, 230),  # Light blue
        "walkable": True,
        "resource_node": None,
    },
    
    # Visual tiles (decoration, non-blocking)
    "flowers": {
        "id": "flowers",
        "layer": "visual",
        "color": (255, 192, 203),  # Pink
        "walkable": True,
        "resource_node": None,
    },
    "small_rocks": {
        "id": "small_rocks",
        "layer": "visual",
        "color": (169, 169, 169),  # Dark gray
        "walkable": True,
        "resource_node": None,
    },
    "bushes": {
        "id": "bushes",
        "layer": "visual",
        "color": (50, 100, 50),  # Dark green
        "walkable": True,
        "resource_node": None,
    },
    "grass_tuft": {
        "id": "grass_tuft",
        "layer": "visual",
        "color": (46, 125, 50),  # Medium green
        "walkable": True,
        "resource_node": None,
    },
    "kodo_skull": {
        # Kodo Skull (real art, this session) - ground decoration, does
        # not block movement.
        "id": "kodo_skull",
        "layer": "visual",
        "color": (200, 190, 160),  # Bone
        "walkable": True,
        "resource_node": None,
    },
    "palm_tree": {
        # Registers a tile_id that zone_generator.py has called via
        # _scatter(zone, "palm_tree", 0.004) for Echo Isles all along -
        # it rendered correctly (texture lookup doesn't require tiles.py
        # registration) but was never formally in this registry, so its
        # walkability/fallback-color were riding on accidental defaults
        # rather than a real decision. _scatter places on the "visual"
        # layer specifically (not collision), so palm trees read as
        # walkable beach/shore decoration, same as grass_tuft/kodo_skull
        # - not a movement-blocking obstacle like the "tree"/"cactus"
        # collision tiles. Reused as-is for the Barrens oasis palm
        # placement this session (savanna_oasis biome) rather than
        # inventing a second, differently-behaved palm tile_id.
        "id": "palm_tree",
        "layer": "visual",
        "color": (60, 130, 70),  # Palm green
        "walkable": True,
        "resource_node": None,
    },
    
    # Collision tiles (blocking movement)
    "tree": {
        "id": "tree",
        "layer": "collision",
        "color": (34, 79, 34),  # Dark forest green
        "walkable": False,
        "resource_node": "wood",
    },
    "rock": {
        "id": "rock",
        "layer": "collision",
        "color": (70, 70, 70),  # Dark gray
        "walkable": False,
        "resource_node": "ore",
    },
    "cactus": {
        # Barrens Cactus (real art, this session) - blocks movement like
        # a tree, no wood/ore resource_node since it's flavor obstacle,
        # not a gatherable node.
        "id": "cactus",
        "layer": "collision",
        "color": (60, 110, 50),  # Cactus green
        "walkable": False,
        "resource_node": None,
    },
    "cliff": {
        "id": "cliff",
        "layer": "collision",
        "color": (50, 50, 50),  # Very dark gray
        "walkable": False,
        "resource_node": None,
    },
    "wall": {
        "id": "wall",
        "layer": "collision",
        "color": (139, 69, 19),  # Brown
        "walkable": False,
        "resource_node": None,
    },
    "landmark": {
        # Solid footprint tile for multi-tile decorative structures
        # (Tilemap.add_landmark) - cave-mouth entrance art, statues, etc.
        # Registered explicitly (not just relying on the "unregistered
        # tile_id defaults to unwalkable" fallback) so it has its own flat-
        # color fallback if a landmark's sprite ever fails to load.
        "id": "landmark",
        "layer": "collision",
        "color": (90, 80, 70),  # Neutral gray-brown stone
        "walkable": False,
        "resource_node": None,
    },
    "deep_forest": {
        "id": "deep_forest",
        "layer": "collision",
        "color": (25, 50, 25),  # Very dark green
        "walkable": False,
        "resource_node": None,
    },
    
    # Interaction tiles (NPCs, objects, quest markers)
    "chest": {
        "id": "chest",
        "layer": "interaction",
        "color": (184, 134, 11),  # Dark goldenrod
        "walkable": True,
        "resource_node": None,
        "interaction_type": "chest",
    },
    "npc": {
        "id": "npc",
        "layer": "interaction",
        "color": (255, 215, 0),  # Gold
        "walkable": True,
        "resource_node": None,
        "interaction_type": "npc",
    },
    "quest_marker": {
        "id": "quest_marker",
        "layer": "interaction",
        "color": (255, 255, 0),  # Yellow
        "walkable": True,
        "resource_node": None,
        "interaction_type": "quest",
    },
    "door": {
        "id": "door",
        "layer": "interaction",
        "color": (165, 42, 42),  # Brown
        "walkable": True,
        "resource_node": None,
        "interaction_type": "door",
    },
    "portal": {
        "id": "portal",
        "layer": "interaction",
        "color": (138, 43, 226),  # Magenta
        "walkable": True,
        "resource_node": None,
        "interaction_type": "portal",
    },
    "boat": {
        "id": "boat",
        "layer": "interaction",
        "color": (220, 20, 60),  # Crimson
        "walkable": True,
        "resource_node": None,
        "interaction_type": "boat",
    },
    "boss_marker": {
        "id": "boss_marker",
        "layer": "interaction",
        "color": (255, 0, 0),  # Bright red - unmistakable, distinct from
        # NPC gold and portal magenta so a boss room reads instantly on
        # sight rather than looking like just another trash mob tile.
        "walkable": True,
        "resource_node": None,
        "interaction_type": "boss_marker",
    },
}

def get_tile(tile_id):
    """Get tile properties by ID."""
    return TILES.get(tile_id)

def is_walkable(tile_id):
    """Check if a tile is walkable."""
    tile = get_tile(tile_id)
    return tile.get("walkable", False) if tile else False

def get_tile_color(tile_id):
    """Get display color for a tile."""
    tile = get_tile(tile_id)
    return tile.get("color", (128, 128, 128)) if tile else (128, 128, 128)
