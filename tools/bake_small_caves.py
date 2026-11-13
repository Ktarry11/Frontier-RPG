#!/usr/bin/env python3
"""Paint the two underground maps that never had a painting: Ragefire Chasm and The Undercrust.

    PYTHONPATH=. python3 tools/bake_small_caves.py [ragefire_chasm] [undercrust] [--preview DIR]

Both were found on 13 Nov 2026 while going through the region: every other cave and dungeon in the
game draws one continuous painted floor, and these two drew in loose tiles. Ragefire Chasm even had
its own set of seamless materials (caves/seamless/rf_*) that nothing used.

Same pipeline as tools/bake_durotar_caves.py. LESS IS MORE: one floor per kind of place, placed by
room, not blended.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import bake_durotar_caves as BD                # noqa: E402
from tools.bake_durotar_caves import M, dim              # noqa: E402

CS = "caves/seamless/"
SF = "shimmering_flats/materials/"
BR = "broodspiral/materials/"

SPECS = {}

# RAGEFIRE CHASM. Volcanic rock, and each tenant has changed the floor under them: troggs have
# trodden theirs to dirt, the cult has laid stone, the ore spur is ore, and the lake is lava.
SPECS["ragefire_chasm"] = lambda: dict(
    build="build_rfc_baked", seed=611, slug="ragefire_chasm", lava=True,
    materials={
        "floor":  M(CS + "rf_basalt_floor_a"),
        "ash":    M(CS + "rf_ash_floor_a"),
        "trogg":  M(CS + "rf_trogg_floor_a"),
        "ore":    M(CS + "rf_ore_floor_a"),
        "cult":   M(CS + "rf_cult_floor_a"),
        "lava":   M(CS + "rf_lava_floor_a"),
        "wall":   M(CS + "rf_basalt_wall_a", None, 2.0),
        "obsid":  M(CS + "rf_obsidian_wall_a", None, 2.0),
        "magma":  M(CS + "rf_lava_wall_a", None, 2.0),
    },
    floor_keys=["floor", "ash", "trogg", "ore", "cult"],
    wall_keys=["wall", "obsid", "magma"],
    floors={
        "ash":   [(120, 205, 20, 12)],                                   # the Cleft Gate
        "trogg": [(95, 166, 22, 15), (60, 105, 20, 15)],                 # the Warrens, Oggleflint's Den
        "ore":   [(54, 168, 12, 8)],                                     # the Ore Spur
        "cult":  [(124, 128, 20, 12), (65, 14, 21, 12), (120, 13, 20, 11)],   # antechamber, Jergosh, Bazzalan
    },
    walls={
        "obsid": [(124, 128, 24, 16), (65, 14, 25, 15), (120, 13, 24, 14)],
        "magma": [(90, 60, 30, 26)],                                     # round Taragaman's lake
    },
    pools=[],
    cfg=dict(ao=0.50, depth=0.88, lip=28, lip_col=(1.0, 0.5, 0.3), deep_dark=0.5,
             foam_col=(140, 170, 190), glows=[("d_lava", (170, 62, 12), 2.8, 0.9)]),
)

# THE UNDERCRUST. A hive under the salt. Hive floor everywhere, pale salt where the crust fell in
# and daylight comes down, and resin - which is the only light - in the Queen's chamber.
SPECS["undercrust"] = lambda: dict(
    build="build_undercrust_baked", seed=612, slug="undercrust",
    materials={
        "floor":  M(dim(SF + "sf_hive_floor", 0.85), None, 1.5),
        "salt":   M(dim(SF + "sf_salt_gravel", 0.80), None, 1.5),
        "resin":  M(dim(BR + "resin_floor", 0.85), None, 1.5),
        "wall":   M(dim(BR + "chitin_wall", 0.55), None, 2.0),
    },
    floor_keys=["floor", "salt", "resin"],
    wall_keys=["wall"],
    floors={
        "salt":  [(18, 62, 10, 8), (104, 54, 7, 6)],        # under the Crustfall and the Deep Shaft
        "resin": [(62, 60, 8, 6), (34, 84, 5, 4)],          # the Queen's chamber, the nursery
    },
    walls={},
    pools=[],
    glow_floors=("resin",),
    cfg=dict(ao=0.46, depth=0.82, lip=20, lip_col=(1.0, 0.85, 0.6), deep_dark=0.4,
             foam_col=(170, 210, 215), glows=[("d_resin", (150, 84, 14), 3.0, 0.8)]),
)


class _C:
    BAKED = "assets/tiles/{}/baked"

    @staticmethod
    def build_rfc_baked():
        """The runtime zone, with its three wall styles renamed to the baker's 'rock'."""
        from tools import handbuilt_dungeons as HD
        zone = HD.build_ragefire_chasm()
        for row in zone.collision_layer:
            for x, c in enumerate(row):
                if c in ("wall", "cliff"):
                    row[x] = "rock"
        return zone, None

    @staticmethod
    def build_undercrust_baked():
        from tools import handbuilt_undercrust as U
        return U.build_undercrust_baked()

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


def main():
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.C = _C
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.bake_spec(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
