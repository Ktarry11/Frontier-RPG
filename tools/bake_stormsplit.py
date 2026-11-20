"""
Bake The Stormsplit (tools/handbuilt_stormsplit.py).

    PYTHONPATH=. python3 tools/bake_stormsplit.py [--preview DIR]

Inside the trunk where the lightning went: storm-black bark down the split, burned bark at the kink, the old wyvern's
litter in the side split, and lightning still crawling across the floor of Thunder Hall, lighting it. The walls are
the trunk's own pale high bark.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_stormsplit as SS
from tools.bake_durotar_caves import M

WT = "worldtree/ground/"
SK = "sky/ground/"


def _room(rname, pad=0):
    x, y, w, h = SS.ROOM_NAMES[rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec():
    SS.build_stormsplit_baked()
    hx, hy, hrx, hry = SS.HALL
    nx, ny, nrx, nry = SS.NEST
    b1 = SS.BEND1
    return dict(
        build="build_stormsplit_baked", seed=4851, slug="stormsplit",
        materials={"floor": M(WT + "wt_storm_bark"), "burn_f": M(WT + "wt_scorched_bark"),
                   "nest_f": M(WT + "wt_nest_litter"), "bolt_f": M(SK + "sk_lightning_rock"),
                   "wall": M(WT + "wt_high_trunk_wall"), "dark_w": M(WT + "wt_trunk_wall")},
        floor_keys=["floor", "burn_f", "nest_f", "bolt_f"],
        wall_keys=["wall", "dark_w"],
        floors={"burn_f": [(b1[0], b1[1], b1[2] + 1, b1[3] + 1), (28, 56, 6, 4)],
                "nest_f": [(nx, ny, nrx + 1, nry + 1)],
                "bolt_f": [(hx, hy, hrx - 3, hry - 2)]},
        walls={"dark_w": [(hx, hy, hrx + 6, hry + 5), (b1[0], b1[1], 14, 10)]},
        pools=[],
        glow_floors=["bolt_f"],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.70, 0.72, 0.80), deep_dark=0.50,
                 foam_col=(200, 205, 230),
                 glows=[("d_bolt_f", (170, 150, 255), 3.0, 0.65)]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"stormsplit": s}
    BD.C = types.SimpleNamespace(BAKED=SS.BAKED, build_stormsplit_baked=SS.build_stormsplit_baked)
    BD.bake_spec("stormsplit", pv)
