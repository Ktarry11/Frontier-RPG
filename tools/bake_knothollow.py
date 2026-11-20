"""
Bake The Knothollow (tools/handbuilt_knothollow.py).

    PYTHONPATH=. python3 tools/bake_knothollow.py [--preview DIR]

Kyle's sheet W1 (docs/worldtree_art_prompts.md): inside the trunk. Rotting bark in the knot where the wood went soft,
grooved bark where the borers have eaten their galleries, glowing gold sap in the Sapwell (it lights the chamber), and
honey-gold heartwood at the bottom of the heartward bore. The walls are the trunk's own bark.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_knothollow as KH
from tools.bake_durotar_caves import M

WT = "worldtree/ground/"


def _room(rname, pad=0):
    x, y, w, h = KH.ROOM_NAMES[rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec():
    KH.build_knothollow_baked()
    cx, cy, rx, ry = KH.SAPWELL
    hx, hy, hrx, hry = KH.HEART
    kx, ky, krx, kry = KH.KNOT
    return dict(
        build="build_knothollow_baked", seed=4451, slug="knothollow",
        materials={"floor": M(WT + "wt_carved_bark"), "rot_f": M(WT + "wt_rot_bark"),
                   "shade_f": M(WT + "wt_shade_bark"), "sap_f": M(WT + "wt_sap_pool"),
                   "seep_f": M(WT + "wt_sap_seep"), "heart_f": M(WT + "wt_heartwood_floor"),
                   "wall": M(WT + "wt_trunk_wall"), "moss_w": M(WT + "wt_trunk_moss_wall"),
                   "rot_w": M(WT + "wt_rot_mushrooms")},
        floor_keys=["floor", "rot_f", "shade_f", "sap_f", "seep_f", "heart_f"],
        wall_keys=["wall", "moss_w", "rot_w"],
        floors={"rot_f": [(kx, ky, krx + 1, kry + 1)], "shade_f": [(22, 40, 14, 16), (62, 36, 8, 6)],
                "sap_f": [(cx, cy + 1, rx - 6, ry - 4)], "seep_f": [(cx, cy, rx + 2, ry + 2), (60, 80, 5, 8)],
                "heart_f": [(hx, hy, hrx + 2, hry + 2)]},
        walls={"moss_w": [(40, 6, 14, 8)], "rot_w": [(kx, ky, krx + 5, kry + 4)]},
        pools=[],
        glow_floors=["sap_f", "heart_f"],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.85, 0.68, 0.36), deep_dark=0.48,
                 foam_col=(220, 200, 150),
                 glows=[("d_sap_f", (230, 168, 40), 3.2, 0.8), ("d_heart_f", (210, 150, 60), 2.8, 0.55)]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"knothollow": s}
    BD.C = types.SimpleNamespace(BAKED=KH.BAKED, build_knothollow_baked=KH.build_knothollow_baked)
    BD.bake_spec("knothollow", pv)
