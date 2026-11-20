"""
Bake Shriekhollow (tools/handbuilt_shriekhollow.py).

    PYTHONPATH=. python3 tools/bake_shriekhollow.py [--preview DIR]

Kyle's sheet W1 (docs/worldtree_art_prompts.md): inside the trunk. Shaded bark on the Roost's ledges, the harpies'
litter of feathers and bone in the nests and the eyrie, carved bark up the throat, and the rot at the bottom: rotting
bark and mushrooms with sap seeping through, glowing faintly. The walls are the trunk's own bark.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_shriekhollow as SH
from tools.bake_durotar_caves import M

WT = "worldtree/ground/"


def spec():
    SH.build_shriekhollow_baked()
    rx_, ry_, rrx, rry = SH.ROOST
    ex, ey, erx, ery = SH.EYRIE
    dx, dy, drx, dry = SH.DARK
    nests = [(line[-1][0], line[-1][1], 6, 5) for _s, line in SH.NESTS]
    return dict(
        build="build_shriekhollow_baked", seed=4751, slug="shriekhollow",
        materials={"floor": M(WT + "wt_carved_bark"), "shade_f": M(WT + "wt_shade_bark"),
                   "nest_f": M(WT + "wt_nest_litter"), "rot_f": M(WT + "wt_rot_bark"),
                   "mush_f": M(WT + "wt_rot_mushrooms"), "seep_f": M(WT + "wt_sap_seep"),
                   "wall": M(WT + "wt_trunk_wall"), "moss_w": M(WT + "wt_trunk_moss_wall"),
                   "rot_w": M(WT + "wt_rot_mushrooms")},
        floor_keys=["floor", "shade_f", "nest_f", "rot_f", "mush_f", "seep_f"],
        wall_keys=["wall", "moss_w", "rot_w"],
        floors={"shade_f": [(rx_, ry_, rrx + 1, rry + 1)],
                "nest_f": nests + [(ex, ey, erx, ery), (28, 16, 5, 4), (53, 24, 5, 4)],
                "rot_f": [(34, 82, 8, 9), (dx, dy, drx + 2, dry + 2)],
                "mush_f": [(dx - 4, dy, 5, 4), (30, 80, 4, 4)],
                "seep_f": [(dx + 2, dy + 1, 4, 3)]},
        walls={"moss_w": [(40, 6, 14, 8)], "rot_w": [(36, 86, 16, 12)]},
        pools=[],
        glow_floors=["seep_f"],
        cfg=dict(ao=0.48, depth=0.88, lip=20, lip_col=(0.70, 0.66, 0.58), deep_dark=0.52,
                 foam_col=(200, 196, 180),
                 glows=[("d_seep_f", (200, 150, 50), 2.6, 0.5)]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"shriekhollow": s}
    BD.C = types.SimpleNamespace(BAKED=SH.BAKED, build_shriekhollow_baked=SH.build_shriekhollow_baked)
    BD.bake_spec("shriekhollow", pv)
