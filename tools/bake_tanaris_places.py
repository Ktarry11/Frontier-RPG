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
from tools.bake_durotar_caves import M, dim

#: bake_spec() resolves its build function off BD.C, which is bound to the Durotar caves module.
#: Each zone here lives in its own module, so C is swapped per bake - the same thing
#: tools/bake_return_voyage.py does for the seven ship zones.
MODULES = {"steamwheedle": STW, "drownbell": DB}

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
