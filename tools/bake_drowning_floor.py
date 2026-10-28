"""
Bake The Drowning Floor.

    PYTHONPATH=. python3 tools/bake_drowning_floor.py [--preview DIR]

Paints from the Southern Thousand Needles set, because this cave is the INSIDE OF THE SAME ROCK the
mesas are made of. Reusing the surface tiles is not a shortcut here, it is the point: a player who has
walked the canyon floor should recognise the stone over their head.

THE FLOOR IS PAINTED AS A TIDE RECORD, which is the whole idea of the place.

Everything in this cave drowns once a year and then dries out for eleven months, and the ground keeps the
receipt. So the palette is banded by DISTANCE FROM THE WATER THAT IS STILL HERE:

    at the water   wet sand and silt, moss on the stone, reeds in the shallows
    just above it  SALT CRUST - evaporite, the white ring a drying pool leaves, and the single most
                   legible way to say "this was under water and is not now"
    the dry floor  cracked mud, curled and lifted, which is what mud does after a year of drying
    the aisle      scoured to gravel and bare rock, because that is where the flood runs hardest

sn_undercut finally earns its place. It was dropped from field use in the surface baker for reading as a
scene rather than a texture - a shadowed overhang. Down here every wall IS a shadowed overhang, so it
goes on the walls and looks like what it is.

ao 0.46 / depth 0.82 - the darkest cave bake in the project. The Underdark glows and the Weeping Ice has
daylight down its shaft; this one has a hole in the roof and then a very long way of not having one.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_drowning_floor as DF
from tools.bake_durotar_caves import M

SN = "southern_needles/materials/"


def spec_drowning_floor():
    return dict(
        build="build_drowning_floor_baked", seed=404, slug="drowning_floor",
        materials={
            # base: the dry floor. Cracked mud that has had a year to curl.
            "dry":     M(SN + "sn_dry_mud", SN + "sn_cracked_clay"),
            "silt":    M(SN + "sn_wet_sand", SN + "sn_damp_soil"),
            "salt":    M(SN + "sn_salt_crust", SN + "sn_salt_rime"),
            "gravel":  M(SN + "sn_wash_gravel", SN + "sn_gravel_scatter"),
            "stone":   M(SN + "sn_polished_shelf", SN + "sn_stone_cracks"),
            "moss":    M(SN + "sn_mossy_stone", SN + "sn_spring_grass"),
            "rock_w":  M(SN + "sn_layered_stone"),
            "under_w": M(SN + "sn_undercut", SN + "sn_iron_banded"),
            "rub_w":   M(SN + "sn_rubble_base", SN + "sn_scree"),
        },
        floor_keys=["dry", "silt", "salt", "gravel", "stone", "moss"],
        wall_keys=["rock_w", "under_w", "rub_w"],
        floors={
            # (cx, cy, rx, ry) - the tide record, outward from the water that is still here
            "moss":   [(32, 30, 12, 10), (70, 75, 8, 5)],
            "silt":   [(32, 30, 18, 14), (70, 75, 13, 8)],
            "salt":   [(32, 30, 26, 19), (70, 75, 19, 12), (60, 47, 16, 11)],
            # the aisle is scoured: the flood runs hardest down the middle and leaves nothing fine
            "gravel": [(68, 60, 24, 28), (62, 90, 12, 10), (110, 42, 8, 16), (95, 88, 10, 7)],
            "stone":  [(68, 62, 13, 18), (24, 67, 11, 14), (107, 57, 10, 13), (108, 27, 9, 8), (80, 21, 13, 7)],
        },
        walls={
            # every wall in a bedding plane is an undercut, so the tile that was wrong on the surface is
            # right here. Rubble where the roof came down and made the bays in the first place.
            "under_w": [(66, 58, 50, 46)],
            "rub_w":   [(68, 84, 28, 14), (62, 36, 26, 12)],
        },
        pools=[DF.DF_POOLS],
        cfg=dict(ao=0.46, depth=0.82, lip=15, lip_col=(0.88, 0.80, 0.66), deep_dark=0.48,
                 foam_col=(214, 206, 180), glows=[]),
    )


MODULES = {"drowning_floor": DF}
SPECS = {"drowning_floor": spec_drowning_floor}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
