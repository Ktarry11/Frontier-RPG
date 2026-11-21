"""
Bake The Golem Vault (tools/handbuilt_golem_vault.py).

    PYTHONPATH=. python3 tools/bake_golem_vault.py [--preview DIR]

The Kharad's old stone: engraved slabs with gold lines down the stair and the gallery, crystal granite in the wrights'
hall, gold-veined marble under the sleepers, and blue-and-gold broken inlay in the hall at the Deep Stair, where the
storm below shows through. The walls are the Kharad's block walls, bronze-banded round the deep hall and the wrights'
hall. The Storm-Well below is tools/bake_storm_well.py. (The sheet's temple floor and relief wall carry a platform edge in the tile, which bands a cave.)
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_golem_vault as GV
from tools.bake_durotar_caves import M

SK = "sky/ground/"


def spec():
    GV.build_golem_vault_baked()
    dx, dy, drx, dry = GV.DEEP_HALL
    sx, sy, srx, sry = GV.SLEEPERS
    hx, hy, hrx, hry = GV.WRIGHTS
    return dict(
        build="build_golem_vault_baked", seed=5051, slug="golem_vault",
        materials={"floor": M(SK + "ae_engraved_stone"), "ring_f": M(SK + "sk_broken_inlay"),
                   "granite_f": M(SK + "kh_quartz_granite"), "marble_f": M(SK + "kh_gold_marble"),
                   "wall": M(SK + "sk_ancient_wall"), "dark_w": M(SK + "kh_bronze_wall")},
        floor_keys=["floor", "ring_f", "granite_f", "marble_f"],
        wall_keys=["wall", "dark_w"],
        floors={"ring_f": [(dx, dy, drx + 1, dry + 1), (42, 92, 5, 6)],
                "granite_f": [(hx, hy, hrx + 1, hry + 1)],
                "marble_f": [(sx, sy, srx + 1, sry + 1)]},
        walls={"dark_w": [(dx, dy, drx + 6, dry + 5), (hx, hy, hrx + 5, hry + 5)]},
        pools=[],
        glow_floors=[],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.70, 0.72, 0.80), deep_dark=0.50,
                 foam_col=(200, 205, 230), glows=[]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"golem_vault": s}
    BD.C = types.SimpleNamespace(BAKED=GV.BAKED, build_golem_vault_baked=GV.build_golem_vault_baked)
    BD.bake_spec("golem_vault", pv)
