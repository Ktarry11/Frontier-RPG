"""Which pool sprite a fishing spot shows, by zone.

A fishing spot is a node on a shore tile; what the player SEES is a patch of disturbed water on
the tile beside it (assets/gathering_nodes/fishing_pools/, sliced from Kyle's sheet by
tools/slice_fishing_pools.py). Each zone lists the pools that suit its water; a spot picks one
when it is placed. A zone not listed here gets DEFAULT.

Only the eighteen FISH pools are used so far. The junk and salvage sprites (crates, barrels,
bottles, the sunken chest) are on disk and waiting for their own catch table, which is not built.
"""
from pathlib import Path

ART_DIR = Path(__file__).parent.parent / "assets" / "gathering_nodes" / "fishing_pools"
FOLDER = "fishing_pools"
DEFAULT = ("pool_fresh", "pool_bubbling")

ZONE_POOLS = {
    "valley_of_trials": ("pool_oasis", "pool_fresh"),
    "durotar": ("pool_coast", "pool_oasis"),
    "echo_isles": ("pool_coast", "pool_jungle"),
    "deathknell": ("pool_plagued", "pool_fresh"),
    "eastern_tirisfal": ("pool_plagued", "pool_fresh", "pool_reeds"),
    "western_tirisfal": ("pool_plagued", "pool_coast"),
    "northern_barrens": ("pool_oasis", "pool_reeds"),
    "central_barrens": ("pool_oasis", "pool_reeds"),
    "southern_barrens": ("pool_oasis", "pool_bubbling"),
    "silverpine_north": ("pool_fresh", "pool_moonlit"),
    "silverpine_south": ("pool_fresh", "pool_coast"),
    "fenris_isle": ("pool_fresh", "pool_moonlit"),
    "ashenvale_west": ("pool_moonlit", "pool_river"),
    "ashenvale_east": ("pool_moonlit", "pool_river"),
    "western_hillsbrad": ("pool_river", "pool_coast"),
    "eastern_hillsbrad": ("pool_river", "pool_coast"),
    "southern_thousand_needles": ("pool_brine", "pool_oasis"),
    "northern_stranglethorn": ("pool_jungle", "pool_river"),
    "central_stranglethorn": ("pool_jungle", "pool_swamp"),
    "southern_stranglethorn": ("pool_jungle", "pool_coast"),
    "northern_tanaris": ("pool_oasis", "pool_coast"),
    "glittervein": ("pool_cave", "pool_glowing"),
    "arathi_west": ("pool_river", "pool_reeds"),
    "arathi_central": ("pool_river", "pool_reeds"),
    "arathi_east": ("pool_coast", "pool_storm"),
    "tempest_shallows": ("pool_storm", "pool_whirlpool"),
    "ashen_reach": ("pool_lava", "pool_bubbling"),
    "moonwell_hollow": ("pool_moonlit", "pool_glowing"),
    "aspen_wilderness": ("pool_river", "pool_reeds"),
    "crystalline_underdark": ("pool_glowing", "pool_cave"),
    "drowning_floor": ("pool_deep_sea", "pool_cave"),
    "weeping_ice": ("pool_ice_hole",),
    "thunder_ridge": ("pool_storm", "pool_bubbling"),
    "black_strand": ("pool_cave", "pool_glowing"),
}


def pools_for(zone_key):
    """The pool sprites this zone may show, only those whose art is on disk."""
    names = ZONE_POOLS.get(zone_key or "", DEFAULT)
    return [n for n in names if (ART_DIR / f"{n}.png").exists()]
