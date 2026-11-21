"""
Bake The Keel (tools/handbuilt_keel.py), the root of the Anchorfields' third anchor.

    PYTHONPATH=. python3 tools/bake_keel.py [--preview DIR]

Inside the shelf's own stone: engraved Aetherian slabs down the stair and round the Chainwell, the shaft in its middle
open to the sky below (read off the map's water tiles: the lip is torn sky at the edge, the core the void), quarried
granite in the Ballast Halls, the lost wardens' marble in their post, and in the Crystal Keel the crystal's light
running through cracks in the floor, lighting the hall. Bronze-banded walls round the keel, the old block walls
elsewhere.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_keel as KL
from tools.bake_durotar_caves import M

SK = "sky/ground/"


def spec():
    KL.build_keel_baked()
    kx, ky, krx, kry = KL.KEEL
    bx, by, brx, bry = KL.BALLAST
    px, py, prx, pry = KL.POST
    return dict(
        build="build_keel_baked", seed=5401, slug="keel", tile_water=True,
        materials={"floor": M(SK + "ae_engraved_stone"), "granite_f": M(SK + "kh_quartz_granite"),
                   "marble_f": M(SK + "ae_marble_cobbles"), "ring_f": M(SK + "sk_broken_inlay"),
                   "bolt_f": M(SK + "ae_rune_floor"),
                   "water_s": M(SK + "ff_torn_sky"), "water_d": M(SK + "ff_void"),
                   "wall": M(SK + "sk_ancient_wall"), "dark_w": M(SK + "kh_bronze_wall")},
        floor_keys=["floor", "granite_f", "marble_f", "ring_f", "bolt_f"],
        wall_keys=["wall", "dark_w"],
        floors={"granite_f": [(bx, by, brx + 1, bry + 1)],
                "marble_f": [(px, py, prx + 1, pry + 1)],
                "ring_f": [(kx, ky, krx + 1, kry + 1)],
                "bolt_f": [(kx, ky + 1, krx - 8, kry - 5)]},
        walls={"dark_w": [(kx, ky, krx + 6, kry + 5)]},
        pools=[],
        glow_floors=["bolt_f"],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.70, 0.72, 0.80), deep_dark=0.50,
                 foam_col=(220, 200, 170),
                 glows=[("d_bolt_f", (170, 200, 255), 3.0, 0.65)]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"keel": s}
    BD.C = types.SimpleNamespace(BAKED=KL.BAKED, build_keel_baked=KL.build_keel_baked)
    BD.bake_spec("keel", pv)
