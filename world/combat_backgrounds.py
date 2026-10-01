"""
Maps world biome_ids (world.tile_textures.ZONE_BIOME / CAVE_BIOME) to combat
background asset folders under assets/backgrounds/. The background pack only
covers 7 folders (desert, jungle, mountain, mossy_forest, dark_dungeon,
fire_dungeon, ice_dungeon) while the world defines ~19 biome tags, so every
biome not covered directly is nearest-matched onto one of the 7 rather than
falling back to one single generic image everywhere.

Three of the seven folders have Morning/Afternoon/Night or Dark/Normal
sub-variants; the other three (dark/fire/ice dungeon) are flat. Callers pass
a variant hint and get silently routed to the flat folder if the biome has
no variants.
"""

# Folders that have time-of-day (or Dark/Normal) subfolders vs. flat ones.
VARIANT_FOLDERS = {
    "desert": ("Morning", "Afternoon", "Night"),
    "jungle": ("Morning", "Afternoon", "Night"),
    "mountain": ("Morning", "Afternoon", "Night"),
    "mossy_forest": ("Normal", "Dark"),
}
FLAT_FOLDERS = ("dark_dungeon", "fire_dungeon", "ice_dungeon")

# Nearest-match: every ZONE_BIOME / CAVE_BIOME tag in world/tile_textures.py
# routed to whichever of the 7 available packs reads closest. Chosen by eye
# from the biome's actual visual character (see tile_textures.py's own
# comments on each), not just name similarity.
BIOME_TO_BACKGROUND = {
    # Direct/near-direct matches
    "desert": "desert",
    "desert_oasis": "desert",
    "tropical": "jungle",
    "mythical_forest": "jungle",
    "decayed_forest": "mossy_forest",
    "undead": "dark_dungeon",
    "orgrimmar": "desert",          # red-rock urban stone, closest to desert set
    "bael_modan": "mountain",

    # Savanna variants - Barrens is dry grassland/scrub, no savanna pack
    # exists so desert reads closest (open, sparse, warm-toned).
    "savanna": "desert",
    "savanna_bones": "desert",
    "savanna_cliff": "mountain",
    "savanna_pond": "jungle",
    "savanna_thornscrub": "desert",
    "barrens_fen": "jungle",

    # Cave variants -> the three dungeon packs by color temperature, per
    # tile_textures.py's own warm/cold/sick/dark/mossy descriptions.
    "cave_warm": "fire_dungeon",
    "cave_cold": "ice_dungeon",
    "cave_sick": "dark_dungeon",    # purple/wine reads closest to dark, not fire or ice
    "cave_dark": "dark_dungeon",
    "cave_mossy": "dark_dungeon",   # DampDungeons warm stone, but no green-cave pack exists
    "cave_swamp": "dark_dungeon",
    "cave_thornscrub": "dark_dungeon",

    # Fallback used by get_biome_for_zone() itself when a zone has no entry.
    "grassland": "mossy_forest",
}


def get_background_folder(biome_id):
    """Biome tag -> background folder name. Always returns something valid
    (falls back to mossy_forest, the least visually-specific pack, for any
    biome tag this table hasn't seen yet - new zones/biomes shouldn't have
    to touch this file just to get *a* background)."""
    return BIOME_TO_BACKGROUND.get(biome_id, "mossy_forest")


def get_variant_options(folder_name):
    """Return the sub-variant folder names for a background folder, or None
    if that folder is flat (no sub-variants)."""
    return VARIANT_FOLDERS.get(folder_name)
