"""
Bake the Hillsbrad interiors. Azurelode Mine: quarried rock, a blue-violet silver vein at the face, and a
standing sump of water filling the middle of the map.

    PYTHONPATH=. python3 tools/bake_hillsbrad_caves.py [azurelode_mine|durnholde_keep ...] [--preview DIR]

No new art. The mine reuses Boulder Lode's quarried floor/wall and - the happy accident that named the place -
its blue-violet CRYSTAL floor/wall for the Silver Face, which is exactly what an "Azure-lode" should look like.
The water comes from the Valley of Trials cluster's cave water.

`tile_water` rather than analytic `pools`: Azurelode's sump is not a painted blob, it is derived from the room
in handbuilt_azurelode._flood_sump and written straight onto the tiles, so the baker has to read the tiles back
rather than re-deriving a shape that could drift out of step with what the player can actually walk on.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import bake_nb_caves as NB
from tools import handbuilt_azurelode as AZ
from tools import handbuilt_durnholde as DK
from tools.bake_durotar_caves import M, VC


def spec_azurelode():
    # Boulder Lode's textures are tall and not seamless; make_seamless caches 256px seamless copies next to them.
    f = NB.make_seamless("boulder_lode_mine", "floor")
    fc = NB.make_seamless("boulder_lode_mine", "floor_crystal")
    w = NB.make_seamless("boulder_lode_mine", "wall")
    wc = NB.make_seamless("boulder_lode_mine", "wall_crystal")
    sx, sy = 56, 22                       # the Silver Face
    px, py = 33, 40                       # the Pump House
    return dict(
        build="build_azurelode_baked", seed=419, slug="azurelode_mine",
        materials={
            "floor": M(f), "crystal_f": M(fc), "wall": M(w), "crystal_w": M(wc),
            "water_s": M(VC + "vot_water_shallow"), "water_d": M(VC + "vot_water_deep"),
        },
        floor_keys=["floor", "crystal_f"],
        wall_keys=["wall", "crystal_w"],
        # The vein is richest at the face and bleeds a little into the pump house workings.
        floors={"crystal_f": [(sx, sy, 24, 14), (px, py, 10, 7)]},
        walls={"crystal_w": [(sx, sy, 30, 18)]},
        pools=[],
        tile_water=True,
        cfg=dict(ao=0.48, depth=0.86, lip=20, lip_col=(0.74, 0.70, 0.62), deep_dark=0.46,
                 foam_col=(196, 206, 214), glows=[]),
    )


def spec_durnholde():
    """Durnholde is built, not dug: flagstone and keep wall, with the undercroft going dark."""
    CS = "caves/seamless/"
    ux, uy = 70, 28                       # the undercroft
    hx, hy = 70, 46                       # the Lord's Hall
    return dict(
        build="build_durnholde_baked", seed=523, slug="durnholde_keep",
        materials={
            "floor": M(CS + "keep_floor_a"), "hall_f": M(CS + "castle_floor_b_a"),
            "wall": M(CS + "keep_wall_a"), "dark_w": M(CS + "castle_wall_dark_a"),
        },
        floor_keys=["floor", "hall_f"],
        wall_keys=["wall", "dark_w"],
        # The hall keeps its better flagstone; the undercroft's walls go black, which is the whole
        # reason the Syndicate stopped going down there.
        floors={"hall_f": [(hx, hy, 22, 13)]},
        walls={"dark_w": [(ux, uy, 30, 16)]},
        pools=[],
        cfg=dict(ao=0.52, depth=0.88, lip=22, lip_col=(0.70, 0.68, 0.64), deep_dark=0.5,
                 foam_col=(200, 200, 205), glows=[]),
    )


MODULES = {"azurelode_mine": AZ, "durnholde_keep": DK}
SPECS = {"azurelode_mine": spec_azurelode, "durnholde_keep": spec_durnholde}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
