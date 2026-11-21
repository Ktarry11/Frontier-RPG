"""Which pool sprite a fishing spot shows, by zone.

A fishing spot is a node on a shore tile; what the player SEES is a patch of disturbed water on
the tile beside it (assets/gathering_nodes/fishing_pools/, sliced from Kyle's sheet by
tools/slice_fishing_pools.py). Each zone lists the pools that suit its water; a spot picks one
when it is placed. A zone not listed here gets DEFAULT.

The eighteen FISH pools are picked here. The junk and salvage sprites (crates, barrels, bottles, the
sunken chest) are dealt out by world/gathering_manager._populate_fishing, now and then in place of a fish
pool, and their catches are world/harvest_finds.py's.
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
    "south_felwood": ("pool_moonlit", "pool_river"),     # Ashenvale's water, running out of Felwood
    "stonetalon_east": ("pool_river", "pool_reeds"),     # Ashfall Creek, grey with silt off the volcano
    "stonetalon_west": ("pool_river", "pool_moonlit"),   # Mistfall Creek and the crater lake
    "north_felwood": ("pool_bubbling", "pool_plagued"),
    "western_plaguelands_south": ("pool_plagued", "pool_fresh"),     # Darrowmere and the creek, plague in both
    "western_plaguelands_north": ("pool_river", "pool_plagued"),     # the Thondroril
    "eastern_plaguelands_west": ("pool_plagued", "pool_bubbling"),
    "eastern_plaguelands_east": ("pool_plagued", "pool_coast"),       # Blackwood Lake and the coast at Tyr's Hand  # the Bloodvenom: poisoned water
    "ashen_reach": ("pool_lava", "pool_bubbling"),
    "west_azshara": ("pool_river", "pool_fresh"),        # the autumn woods' streams
    "central_azshara": ("pool_river", "pool_reeds"),
    "east_azshara": ("pool_coast", "pool_deep_sea"),     # the drowned coast
    "deadwind_west": ("pool_plagued", "pool_swamp"),     # the Black Tarn and the Sickwater
    "deadwind_east": ("pool_river", "pool_glowing"),     # the gorge's river and the seep's glow
    "moonwell_hollow": ("pool_moonlit", "pool_glowing"),
    "rootwater_isle": ("pool_coast", "pool_jungle"),       # the World Tree's reef and its lagoons (19 Nov 2026)
    "lower_boughs": ("pool_river", "pool_jungle"),         # the river down the Great Bough (20 Nov 2026)
    "middle_boughs": ("pool_fresh",),                      # rain held in hollows of the bark (20 Nov 2026)
    "upper_boughs": ("pool_fresh",),                       # rain caught in the forks (20 Nov 2026)
    "sunward_crown": ("pool_fresh",),                      # dew pools in the golden canopy (20 Nov 2026)
    "celestial_expanse": ("pool_fresh",),                  # the great sky river and its pools (20 Nov 2026)
    "anchorfields": ("pool_fresh",),                       # the Estates' pool, the coolant pond, Tiltside's spring
    "ascendant_bastions": ("pool_fresh",),                 # the fort's cistern, the Proving Grounds' pool, the rain basin
    "fading_firmament": ("pool_fresh",),                   # the last wellstone pools: Lastlight, the Gardens, the Forge, the Breaking
    "raincatch": ("pool_fresh", "pool_reeds"),
    "kapok_crowns": ("pool_river", "pool_jungle"),
    "high_wilderness": ("pool_river", "pool_fresh"),       # Feralas's east arm: forest rivers and pools
    "forgotten_coast": ("pool_coast", "pool_deep_sea"),    # Feralas's coast and the sound off Feathermoon
    "twin_colossals": ("pool_river", "pool_reeds"),        # the falls under the Colossals and the fog groves' fens
    "aspen_wilderness": ("pool_river", "pool_reeds"),
    "crystalline_underdark": ("pool_glowing", "pool_cave"),
    "drowning_floor": ("pool_deep_sea", "pool_cave"),
    "weeping_ice": ("pool_ice_hole",),
    "thunder_ridge": ("pool_storm", "pool_bubbling"),
    "black_strand": ("pool_cave", "pool_glowing"),
    # hidden open maps (data/world/hidden_zones.json)
    "saltgrave": ("pool_brine", "pool_coast"),
    "glasswaste": ("pool_oasis", "pool_bubbling"),
    "weeping_pines": ("pool_moonlit", "pool_fresh"),
    "tanglewood_shoals": ("pool_jungle", "pool_coast"),
    "drowned_idols": ("pool_jungle", "pool_glowing"),
    "buried_caravan": ("pool_oasis", "pool_brine"),
    "sunken_kraal": ("pool_swamp", "pool_reeds"),
    "moonless_glade": ("pool_moonlit", "pool_glowing"),
    "stormcrag": ("pool_storm", "pool_river"),
    "ashen_orchard": ("pool_plagued", "pool_bubbling"),
    "painted_springs": ("pool_bubbling", "pool_river"),
    "coal_forest": ("pool_swamp", "pool_reeds"),
    "lanternmere": ("pool_swamp", "pool_reeds"),
    "long_winter": ("pool_ice_hole", "pool_river"),
    "sunward_waystation": ("pool_moonlit", "pool_fresh"),
}


def pools_for(zone_key):
    """The pool sprites this zone may show, only those whose art is on disk."""
    names = ZONE_POOLS.get(zone_key or "", DEFAULT)
    return [n for n in names if (ART_DIR / f"{n}.png").exists()]
