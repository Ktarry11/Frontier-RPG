"""
Bake Rocky Pass.

    PYTHONPATH=. python3 tools/bake_rocky_pass.py [--preview DIR]

Paints from the Aspen Wilderness set, because this IS the Aspen Wilderness - the top of the range
the zone sits under. A player who has walked the Rim should recognise the granite above it. Kyle:
"We should have lots of aspen props already and also the dungeon (since it's 'outside' themed)
should use similar tiles to what we already have."

THE PALETTE IS ALTITUDE, which is the whole idea of the place. Kyle: "So for the tiles lets start
with rocks gradually going into snow as we 'climb' the dungeon." So the floor regions are not
rooms, they are BANDS ACROSS THE MAP, stacked south to north and overlapping generously so the
change is a gradient rather than four stripes:

    the mouth    granite and lichen, grey gravel between
    the middle   scree and bedrock, scoured
    high up      stone under frost, then patchy snow
    the summit   packed snow, and the walls go white too

LIGHTING TOOK THREE PASSES AND IT IS WORTH SAYING WHY. depth is how hard the baker darkens INTO
rock from the open floor, and every other bake in this project is a cave, where that is exactly
right. At the cave default of 0.60 this came out a black warren - correct for a tunnel, absurd for
somewhere with sky over it. At 0.18 the canyons stopped reading at all: with no shading into the
walls, the ribbon of floor and the rock beside it were the same brightness and the switchback
vanished. 0.40 keeps the canyon walls legible as walls while leaving the place obviously outdoors.
ao is low (0.26) for the same reason - there is no roof to occlude anything.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_rocky_pass as RP
from tools.bake_durotar_caves import M

ASP = "aspen/materials/"


def spec_rocky_pass():
    return dict(
        build="build_rocky_pass_baked", seed=3416, slug="rocky_pass",
        materials={
            # base: the rock the whole range is made of
            "rock":   M(ASP + "asp_granite", ASP + "asp_granite_lichen"),
            "gravel": M(ASP + "asp_grey_gravel", ASP + "asp_gravel_shoulder"),
            "scree":  M(ASP + "asp_scree", ASP + "asp_bedrock"),
            "frost":  M(ASP + "asp_stone_frost", ASP + "asp_wet_stone"),
            "patch":  M(ASP + "asp_snow_patch", ASP + "asp_stone_frost"),
            "snow":   M(ASP + "asp_snow_packed", ASP + "asp_snow_patch"),
            "rock_w": M(ASP + "asp_granite", ASP + "asp_talus"),
            "frost_w": M(ASP + "asp_stone_frost", ASP + "asp_granite"),
            "snow_w": M(ASP + "asp_snow_packed", ASP + "asp_snow_patch"),
        },
        floor_keys=["rock", "gravel", "scree", "frost", "patch", "snow"],
        wall_keys=["rock_w", "frost_w", "snow_w"],
        floors={
            # BANDS, south (low) to north (high), overlapping so the change is gradual
            "gravel": [(60, 172, 76, 30), (60, 150, 72, 26)],
            "scree":  [(60, 128, 74, 32), (60, 100, 70, 26)],
            "frost":  [(60, 74, 70, 28), (60, 56, 64, 22)],
            "patch":  [(62, 42, 60, 22)],
            "snow":   [(62, 26, 52, 20)],
        },
        walls={
            "frost_w": [(60, 62, 76, 36)],
            "snow_w": [(62, 28, 60, 26)],
        },
        pools=[],
        cfg=dict(ao=0.26, depth=0.40, lip=12, lip_col=(0.86, 0.90, 0.96), deep_dark=0.30,
                 foam_col=(226, 236, 246), glows=[]),
    )


MODULES = {"rocky_pass": RP}
SPECS = {"rocky_pass": spec_rocky_pass}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
