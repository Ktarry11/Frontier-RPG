"""
Bake Stonetalon's caves (docs/stonetalon_brief.md).

    PYTHONPATH=. python3 tools/bake_stonetalon_caves.py [windshear_mine ...] [--preview DIR]

Windshear Mine: the Venture Co.'s quarried rock (Boulder Lode Mine's materials, the same company's digging) for the
drift and the ring, and at the Breakthrough the chimney's floor: grey ash blown down from the Blowdown on talus.
Kyle's Stonetalon tile sheet (basalt, ash, pumice) replaces the ash and talus when it lands.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_windshear_mine as WM
from tools.bake_durotar_caves import M
from tools.bake_nb_caves import make_seamless


def spec_windshear():
    f = make_seamless("boulder_lode_mine", "floor")
    w = make_seamless("boulder_lode_mine", "wall")
    vx, vy = WM.ROOMS["breach"][:2]
    return dict(
        build="build_windshear_mine_baked", seed=331, slug="windshear_mine",
        materials={"floor": M(f), "ash_f": M("aspen/materials/asp_ash_patch"), "wall": M(w),
                   "talus_w": M("aspen/materials/asp_talus")},
        floor_keys=["floor", "ash_f"],
        wall_keys=["wall", "talus_w"],
        floors={"ash_f": [(vx, vy, 20, 11)]},
        walls={"talus_w": [(vx, vy, 26, 14)]},
        pools=[],
        cfg=dict(ao=0.48, depth=0.84, lip=20, lip_col=(0.80, 0.66, 0.50), deep_dark=0.4,
                 foam_col=(200, 200, 210), glows=[]),
    )


MODULES = {"windshear_mine": WM}
SPECS = {"windshear_mine": spec_windshear}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
