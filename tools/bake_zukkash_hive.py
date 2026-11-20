"""
Bake The Zukk'ash Hive (tools/handbuilt_zukkash_hive.py).

    PYTHONPATH=. python3 tools/bake_zukkash_hive.py [--preview DIR]

Kyle's Zukk'ash Hive sheet (docs/feralas_art_prompts.md sheet 8, 19 Nov 2026, sliced to assets/tiles/feralas/
writhing_deep): root earth for the gallery near the forest floor, egg-strewn floors in the brood cells, amber resin in
the Deep Mother's chamber, and the dug tunnel drying out to the Dry Deep's black sand at the far end. (Stonetalon's and
the Broodspiral's materials stood in before it.)
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_zukkash_hive as WD
from tools.bake_durotar_caves import M

WDT = "feralas/writhing_deep/"


def _room(rname, pad=0):
    x, y, w, h = WD.ROOM_NAMES[rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec():
    WD.build_zukkash_hive_baked()
    cells = [(c[0], c[1], 7, 6) for (_s, _l, c) in WD.BROOD]
    cx, cy, rx, ry = WD.CHAMBER
    return dict(
        build="build_zukkash_hive_baked", seed=4901, slug="zukkash_hive",
        materials={"floor": M(WDT + "wd_earth"), "root_f": M(WDT + "wd_root_earth"), "hive_f": M(WDT + "wd_chitin_floor"),
                   "resin_f": M(WDT + "wd_resin"), "larval_f": M(WDT + "wd_egg_floor"), "sand_f": M(WDT + "wd_dark_sand"),
                   "wall": M(WDT + "wd_root_wall"), "chitin_w": M(WDT + "wd_honeycomb_wall"),
                   "queen_w": M(WDT + "wd_resin_wall")},
        floor_keys=["floor", "root_f", "hive_f", "resin_f", "larval_f", "sand_f"],
        wall_keys=["wall", "chitin_w", "queen_w"],
        floors={"root_f": [(52, 14, 10, 14)], "larval_f": cells, "resin_f": [(cx, cy, rx + 2, ry + 2)],
                "hive_f": [(54, 50, 8, 12)], "sand_f": [(60, 104, 14, 20)]},
        walls={"chitin_w": [(54, 40, 30, 20)], "queen_w": [(cx, cy, rx + 6, ry + 6)]},
        pools=[],
        cfg=dict(ao=0.46, depth=0.88, lip=20, lip_col=(0.85, 0.70, 0.40), deep_dark=0.45,
                 foam_col=(210, 200, 170), glows=[]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"zukkash_hive": s}
    BD.C = types.SimpleNamespace(BAKED=WD.BAKED, build_zukkash_hive_baked=WD.build_zukkash_hive_baked)
    BD.bake_spec("zukkash_hive", pv)
