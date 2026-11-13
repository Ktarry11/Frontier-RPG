#!/usr/bin/env python3
"""
Bake Steamwheedle Port and The Drownbell.

    PYTHONPATH=. python3 tools/bake_tanaris_places.py [steamwheedle|drownbell] [--preview OUT.png]

Both are CaveLayout zones (a standalone town and a cave), so both go through bake_durotar_caves'
SPEC pipeline rather than the open-zone Painter.

TWO PLACES THAT SHOULD NOT LOOK ALIKE, and they share a region and a tile set, so the separation has
to be deliberate:

  STEAMWHEEDLE is DRY AND BRIGHT. Sand and stone quay, warm, and the sea as the one cool thing in
  it. The town that won should feel like somewhere you would stand around in.
  THE DROWNBELL is WET AND DARK. The same desert stone with the light taken out of it and water on
  the floor at the far end. A sea cave under a headland has no sky in it.

THE WALL TILE IS WHAT CARRIES THAT. Steamwheedle's walls are its own cliffs - bright sandstone
rubble, seen in daylight. The Drownbell's are the same rock dimmed hard, because it is the same
rock, and the only honest difference between a cliff outside and a cliff inside is the light.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_steamwheedle_port as STW
from tools import handbuilt_drownbell as DB
from tools import handbuilt_dry_deep as DD
from tools import handbuilt_black_strand as BS
from tools.bake_durotar_caves import M, dim

#: bake_spec() resolves its build function off BD.C, which is bound to the Durotar caves module.
#: Each zone here lives in its own module, so C is swapped per bake - the same thing
#: tools/bake_return_voyage.py does for the seven ship zones.
MODULES = {"steamwheedle": STW, "drownbell": DB, "dry_deep": DD, "black_strand": BS}

SF = "shimmering_flats/materials/"

# LESS IS MORE (13 Nov 2026): one texture per material, no cross-faded pairs - see bake_shimmering_flats.
SPECS = {}

SPECS["steamwheedle"] = lambda: dict(
    build="build_steamwheedle_baked", seed=771, slug="steamwheedle_port",
    materials={
        "floor":   M(SF + "tan_sand_pebble", None, 1.5),
        "quay":    M(SF + "tan_paving_carved"),
        "yard":    M(SF + "tan_sand_pebble", None, 1.5),
        "tar":     M(SF + "tan_quay_tarred"),
        "water_s": M(SF + "cen_water_shallow"),
        "water_d": M(SF + "cen_water_deep"),
        "wall":    M(SF + "tan_sandstone_floor", None, 2.0),
    },
    floor_keys=["floor", "quay", "yard", "tar"],
    wall_keys=["wall"],
    floors={
        # the quay is paved and the upper yard is not, which is the two-town split in one line
        "quay": [(34, 42, 26, 20), (20, 30, 14, 12)],
        "yard": [(80, 54, 32, 26), (66, 44, 18, 14)],
        "tar":  [(30, 25, 40, 5)],      # the wet strip right along the water
    },
    walls={},
    pools=[],
    # A TOWN IN THE SUN. Low ao and shallow depth: the walls here are open cliffs with daylight on
    # them, and a cave's deep shading would make a seafront look like a cellar.
    cfg=dict(ao=0.22, depth=0.26, lip=14, lip_col=(1.0, 0.94, 0.78), deep_dark=0.22,
             foam_col=(215, 240, 240), glows=[]),
)

SPECS["drownbell"] = lambda: dict(
    build="build_drownbell_baked", seed=772, slug="drownbell",
    materials={
        "floor":   M(dim(SF + "tan_wadi_gravel", 0.62)),
        "dry":     M(dim(SF + "tan_wadi_gravel", 0.62)),
        "wet":     M(dim(SF + "sf_mud_curled", 0.58)),
        "deck":    M(dim(SF + "tan_plank_bleached", 0.60)),
        "water_s": M(dim(SF + "cen_water_shallow", 0.78)),
        "water_d": M(dim(SF + "cen_water_deep", 0.70)),
        "wall":    M(dim(SF + "tan_sandstone_floor", 0.50), None, 2.0),
    },
    floor_keys=["floor", "dry", "wet", "deck"],
    wall_keys=["wall"],
    floors={
        "dry":  [(34, 22, 24, 18), (16, 14, 18, 14)],        # the mouth and the dry gallery
        "wet":  [(62, 44, 26, 20), (76, 64, 26, 22)],        # the wet end
        "deck": [(44, 58, 24, 18)],                          # the careenage, planked over
    },
    walls={},
    pools=[],
    # A CAVE UNDER A HEADLAND. High ao, deep shading, a cold lip - no sky gets in here.
    cfg=dict(ao=0.44, depth=0.82, lip=24, lip_col=(0.72, 0.86, 1.0), deep_dark=0.40,
             foam_col=(170, 210, 215), glows=[]),
)

SPECS["dry_deep"] = lambda: dict(
    build="build_dry_deep_baked", seed=773, slug="dry_deep",
    materials={
        # THREE THINGS: the dry bed of a sea, the pale dust under each shaft where daylight and
        # sand come down, and rock. See bake_shimmering_flats for why not more.
        "floor":   M(dim(SF + "sf_mud_curled", 0.62), None, 1.5),
        "light":   M(dim(SF + "tan_sand_gold", 0.80), None, 1.5),
        "wall":    M(dim(SF + "tan_sandstone_floor", 0.46), None, 2.0),
    },
    floor_keys=["floor", "light"],
    wall_keys=["wall"],
    floors={
        "light": [(x, y, 7, 6) for (x, y) in DD.PORTALS],
    },
    walls={},
    pools=[],
    cfg=dict(ao=0.42, depth=0.78, lip=22, lip_col=(1.0, 0.90, 0.70), deep_dark=0.40,
             foam_col=(170, 210, 215), glows=[]),
)


def _dots(pts, r=1.8, step=2.0):
    """A polyline as a chain of small ellipses - the only region shape the cave baker has."""
    import numpy as _np
    out = []
    for (p, q) in zip(pts, pts[1:]):
        n = max(1, int(_np.hypot(q[0] - p[0], q[1] - p[1]) / step))
        for i in range(n + 1):
            t = i / n
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, r, r))
    return out


def _room(name, k=1.0):
    _n, cx, cy, rx, ry = BS.CHAMBERS[BS.IDX[name]]
    return (cx, cy, rx * k, ry * k)


UD = "underdark/materials/"
BR = "broodspiral/materials/"
TM = "tempest/materials/"

# THE BLACK STRAND. Kyle, 13 Nov 2026: "a gorgeous mix of dark sand, fungi, and silithid".
# BLACK SAND IS THE GROUND EVERYWHERE and it is one quiet texture, so that the two things growing
# on it can be loud: the fungi light it teal, the hive lights it amber, and the only other colour
# is the red of the Dark Iron road. Each of those is ONE floor, placed, not blended - the mix is
# in where they are, and the light each throws is what joins them up.
SPECS["black_strand"] = lambda: dict(
    build="build_black_strand_baked", seed=5053, slug="black_strand",
    materials={
        "sand":    M("black_strand/materials/bs_black_sand", None, 1.5),
        "myc":     M(dim(UD + "ud_myc_threads", 0.62), None, 1.5),     # the wood's floor
        "glow":    M(UD + "ud_spore_moss", None, 1.5),                 # where the fungi are thickest
        "hive":    M(dim(SF + "sf_hive_floor", 0.80), None, 1.5),
        "resin":   M(dim(BR + "resin_floor", 0.85), None, 1.5),        # the hive's own light
        "slag":    M(dim(TM + "tmp_basalt", 0.70), None, 1.5),         # the Diggings' spoil
        "road":    M(dim(TM + "kv_flagstone", 1.25), None, 1.0),
        "water_s": M(dim(UD + "ud_lumen_shallow", 0.62)),
        "water_d": M(dim(UD + "ud_pool_deep", 0.60)),
        "wall":    M(dim(UD + "ud_rock_wall", 0.80), None, 2.0),
    },
    floor_keys=["sand", "myc", "glow", "hive", "resin", "slag", "road"],
    wall_keys=["wall"],
    floors={
        "myc":   [_room("The Lantern Wood", 0.95), _room("The Last Water", 1.05)],
        "glow":  [(27, 84, 6, 5), (41, 80, 5, 4), (33, 95, 5, 4), (22, 72, 4, 3), (46, 92, 4, 3),
                  (64, 98, 4, 3), (90, 100, 4, 3), (76, 92, 5, 2.5),
                  # and a few caps' worth out on the open sand, so the dunes are not unlit
                  (40, 28, 2.5, 2), (62, 44, 2.5, 2), (70, 30, 2, 2), (24, 26, 2, 2),
                  (52, 58, 2.5, 2), (46, 62, 2, 2), (66, 74, 2.5, 2), (58, 96, 2.5, 2),
                  (92, 44, 2, 2), (74, 54, 2, 1.6), (30, 44, 2.5, 2), (112, 50, 2, 2)],
        "hive":  [_room("The Chitin Reach", 1.0), _room("The Royal Cell", 1.2), (104, 67, 8, 4),
                  (100, 85, 8, 4)],
        "resin": [(121, 80, 6, 6), (136, 108, 5, 4), (112, 70, 3, 2.5), (128, 92, 3, 3),
                  (105, 67, 2.5, 2), (99, 85, 2.5, 2), (92, 88, 2, 1.6)],
        "slag":  [_room("The Castout Diggings", 0.9)],
        "road":  [d for (pts, _hw) in BS.ROADS for d in _dots(pts)] + [(84, 60, 7, 5)],
    },
    walls={},
    pools=[],
    tile_water=True,
    glow_floors=("glow", "resin"),
    # NO SKY AT ALL. Deep shading and a cold lip, and then the two lights do the rest.
    cfg=dict(ao=0.46, depth=0.80, lip=20, lip_col=(0.62, 0.78, 1.0), deep_dark=0.45,
             foam_col=(120, 220, 215),
             glows=[("d_glow", (20, 120, 118), 3.4, 0.85), ("d_resin", (150, 84, 14), 3.0, 0.80)]),
)


def main():
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
