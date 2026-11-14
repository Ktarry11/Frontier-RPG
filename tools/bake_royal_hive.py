"""
Bake the Royal Hive's floor and walls.

    PYTHONPATH=. python3 tools/bake_royal_hive.py [--preview DIR]

NO NEW TEXTURES, the same rule as tools/bake_tempest_dungeons.py: the shared interior library
already has a hive. Hive floor in the tunnels and the drone galleries, poured resin in the two
chambers the hive keeps for itself (the resin halls and the queen's chamber), and chitin walls
throughout, so the place reads as built by insects rather than cut by miners.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M

from tools import handbuilt_royal_hive as RH

_L = "durotar_caves/materials/"


def _box(lobes, pad=2):
    return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in lobes]


def spec_royal_hive():
    C = RH.CHAMBERS
    return dict(
        build="build_royal_hive_baked", seed=601, slug="royal_hive", wall_tile="wall",
        materials={"floor": M(_L + "sf_hive_floor_dim80"), "resin_f": M(_L + "resin_floor_dim85"),
                   "wall": M(_L + "chitin_wall_dim55")},
        floor_keys=["floor", "resin_f"], wall_keys=["wall"],
        floors={"resin_f": _box(C["The Resin Halls"]) + _box(C["The Royal Chamber"])
                + _box(C["The Brood Chambers"])},
        walls={}, pools=[],
        # Dim and amber: the only light is what the resin gives off.
        cfg=dict(ao=0.48, depth=0.86, lip=16, lip_col=(0.78, 0.62, 0.30), deep_dark=0.46,
                 foam_col=(190, 170, 120), glows=[]),
    )


class _Shim:
    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    spec = spec_royal_hive()
    BD.SPECS = {"royal_hive": spec}
    BD.C = _Shim(RH, spec["build"], RH.BAKED)
    BD.bake_spec("royal_hive", preview=(f"{pv}/royal_hive.png" if pv else None))
