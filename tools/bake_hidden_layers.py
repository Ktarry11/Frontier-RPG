#!/usr/bin/env python3
"""Paint the hidden levels under the dungeons (tools/handbuilt_hidden_layers.py).

    PYTHONPATH=. python3 tools/bake_hidden_layers.py [slug ...] [--preview DIR]

Same pipeline as tools/bake_small_caves.py. Kyle, 14 Nov 2026: "hidden Dungeons can look similar to
their base Dungeons", so each is painted in its parent's own materials, a shade darker and deeper.

WATER IN THE LIGHTLESS REACH is read off the built map's water tiles (the baker's tile_water, the
same switch Blackfathom Deeps uses), because a gallery of islands is not an ellipse.
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
WC = "wailing_caverns/materials/"
SP = "silverpine/materials/sp_"
STV = "stranglethorn/materials/"
UD = "underdark/materials/"

SPECS = {}

SPECS["cinderwell"] = lambda: dict(
    build="build_cinderwell", seed=901, slug="cinderwell", lava=True,
    materials={
        "floor":  M(dim(CS + "rf_basalt_floor_a", 0.85)),
        "ash":    M(dim(CS + "rf_ash_floor_a", 0.80)),
        "cult":   M(dim(CS + "rf_cult_floor_a", 0.85)),
        "molten": M(CS + "rf_molten_floor_a"),
        "lava":   M(CS + "rf_lava_floor_a"),
        "wall":   M(dim(CS + "rf_basalt_wall_a", 0.8), None, 2.0),
        "obsid":  M(CS + "rf_obsidian_wall_a", None, 2.0),
        "magma":  M(CS + "rf_lava_wall_a", None, 2.0),
    },
    floor_keys=["floor", "ash", "cult", "molten"],
    wall_keys=["wall", "obsid", "magma"],
    floors={"ash": [(55, 82, 10, 6), (24, 70, 10, 7)],
            "cult": [(16, 41, 9, 9), (94, 44, 10, 10), (84, 73, 11, 8)],
            "molten": [(55, 46, 18, 18)]},
    walls={"obsid": [(16, 41, 12, 12), (84, 73, 14, 11)], "magma": [(55, 46, 22, 22)]},
    pools=[],
    cfg=dict(ao=0.55, depth=0.92, lip=28, lip_col=(1.0, 0.45, 0.25), deep_dark=0.55,
             foam_col=(140, 170, 190), glows=[("d_lava", (190, 70, 14), 3.2, 1.0)]),
)

SPECS["dreaming_root"] = lambda: dict(
    build="build_dreaming_root", seed=902, slug="dreaming_root",
    materials={
        "floor":  M(dim(WC + "wc_cavern_floor", 0.70)),
        "edge":   M(dim(WC + "wc_river_edge_floor", 0.70)),
        "moss":   M(dim(CS + "wc_floor_a", 0.65)),
        "root":   M(dim(SP + "root_earth", 0.70)),
        "water_s": M(dim(WC + "wc_river_water", 0.75)),
        "water_d": M(dim(WC + "wc_river_water", 0.6)),
        "wall":   M(dim(WC + "wc_cavern_wall", 0.65)),
        "shrine": M(dim(WC + "wc_serpent_shrine_wall", 0.6)),
    },
    floor_keys=["floor", "edge", "moss", "root"],
    wall_keys=["wall", "shrine"],
    floors={"edge": [(60, 50, 14, 14)], "root": [(22, 74, 10, 7), (30, 20, 11, 8), (60, 11, 9, 7)],
            "moss": [(98, 74, 10, 7), (104, 50, 10, 9), (88, 20, 11, 8)]},
    walls={"shrine": [(60, 11, 12, 10), (60, 50, 16, 16)]},
    pools=[[(60, 52, 7.5, 5.0, 0.6), (104, 50, 4.0, 3.0, 1.9)]],
    cfg=dict(ao=0.52, depth=0.9, lip=20, lip_col=(0.75, 0.6, 1.0), deep_dark=0.55,
             foam_col=(180, 170, 220), glows=[]),
)

SPECS["ossuary_below"] = lambda: dict(
    build="build_ossuary", seed=903, slug="ossuary_below",
    materials={
        "floor":  M(dim(SP + "crypt_floor", 0.75)),
        "keep":   M(dim(SP + "keep_floor", 0.70)),
        "bone":   M(dim(CS + "rubble_strewn_floor_a", 0.70)),
        "ritual": M(dim(SP + "ritual_floor", 0.75)),
        "wall":   M(dim(SP + "keep_wall", 0.6), None, 2.0),
        "mossy":  M(dim(SP + "keep_wall_mossy", 0.6), None, 2.0),
        "rock":   M(dim(SP + "rock_wall", 0.6), None, 2.0),
    },
    floor_keys=["floor", "keep", "bone", "ritual"],
    wall_keys=["rock", "wall", "mossy"],
    floors={"bone": [(76, 50, 12, 9), (98, 74, 10, 8)], "ritual": [(60, 15, 13, 10)],
            "keep": [(20, 46, 10, 9), (14, 84, 8, 6)]},
    walls={"wall": [(60, 15, 18, 14), (20, 46, 13, 12)], "mossy": [(55, 80, 40, 10)]},
    pools=[],
    cfg=dict(ao=0.55, depth=0.9, lip=18, lip_col=(0.7, 0.8, 1.0), deep_dark=0.5,
             foam_col=(160, 170, 180), glows=[]),
)

SPECS["lightless_reach"] = lambda: dict(
    build="build_lightless_reach", seed=904, slug="lightless_reach", tile_water=True,
    materials={
        "floor":  M(dim(CS + "bfd_cave_floor_a", 0.70)),
        "temple": M(dim(CS + "bfd_temple_floor_a", 0.70)),
        "sand":   M(dim(CS + "gro_sand_a", 0.50)),
        "water_s": M(dim(CS + "gro_tidepool_a", 0.55)),
        "water_d": M(dim(CS + "gro_deep_floor_a", 0.40)),
        "wall":   M(dim(CS + "bfd_cave_wall_a", 0.6), None, 2.0),
        "twall":  M(dim(CS + "bfd_temple_wall_a", 0.6), None, 2.0),
    },
    floor_keys=["floor", "temple", "sand"],
    wall_keys=["wall", "twall"],
    floors={"temple": [(60, 22, 12, 8), (58, 52, 8, 6), (96, 32, 8, 7)], "sand": [(60, 90, 8, 6)]},
    walls={"twall": [(60, 18, 20, 12)]},
    pools=[],
    cfg=dict(ao=0.5, depth=0.9, lip=16, lip_col=(0.5, 0.75, 1.0), deep_dark=0.6,
             foam_col=(120, 150, 170), glows=[]),
)

SPECS["blood_pits"] = lambda: dict(
    build="build_blood_pits", seed=905, slug="blood_pits",
    materials={
        "sand":   M(dim(STV + "stv_arena_sand", 0.70)),
        "stone":  M(dim(STV + "stv_plaza", 0.70)),
        "bone":   M(dim(STV + "stv_beach", 0.60)),
        "ruin":   M(dim(STV + "stv_ruin", 0.70)),
        "wall":   M(dim(STV + "stv_cliff_b", 0.6), None, 2.0),
        "basalt": M(dim(CS + "rf_basalt_wall_a", 0.7), None, 2.0),
    },
    floor_keys=["sand", "stone", "bone", "ruin"],
    wall_keys=["wall", "basalt"],
    floors={"stone": [(50, 88, 9, 5)], "bone": [(50, 11, 12, 7), (24, 47, 10, 8), (76, 47, 10, 8)],
            "ruin": [(90, 47, 7, 7)]},
    walls={"basalt": [(50, 47, 18, 18)]},
    pools=[],
    cfg=dict(ao=0.52, depth=0.88, lip=22, lip_col=(1.0, 0.55, 0.45), deep_dark=0.5,
             foam_col=(160, 160, 160), glows=[]),
)

SPECS["unwritten_stacks"] = lambda: dict(
    build="build_unwritten_stacks", seed=906, slug="unwritten_stacks",
    materials={
        "floor":  M(dim(UD + "ud_dalaran_floor", 0.75)),
        "crack":  M(dim(UD + "ud_dalaran_cracked", 0.75)),
        "bloom":  M(dim(UD + "ud_bloom_floor", 0.75)),
        "rune":   M(dim(UD + "ud_rune_floor", 0.75)),
        "wall":   M(dim(UD + "ud_shelf_wall", 0.75), None, 2.0),
        "bwall":  M(dim(UD + "ud_bloom_wall", 0.7), None, 2.0),
        "dwall":  M(dim(UD + "ud_dalaran_wall", 0.7), None, 2.0),
    },
    floor_keys=["floor", "crack", "bloom", "rune"],
    wall_keys=["wall", "bwall", "dwall"],
    floors={"rune": [(56, 12, 12, 7), (98, 44, 7, 8)], "bloom": [(14, 14, 7, 6), (56, 86, 8, 4)],
            "crack": [(30, 60, 14, 10), (80, 40, 12, 10)]},
    walls={"bwall": [(14, 14, 10, 9), (98, 44, 10, 11)], "dwall": [(56, 12, 16, 10)]},
    pools=[],
    glow_floors=("rune",),
    cfg=dict(ao=0.5, depth=0.88, lip=18, lip_col=(0.8, 0.7, 1.0), deep_dark=0.5,
             foam_col=(170, 170, 200), glows=[("d_rune", (60, 40, 110), 2.6, 0.7)]),
)


SPECS["world_root_hollow"] = lambda: dict(
    build="build_world_root", seed=907, slug="world_root_hollow",
    materials={
        "floor":  M(dim(SP + "root_earth", 0.70)),
        "moss":   M(dim(CS + "mossy_cave_floor_a", 0.75)),
        "amber":  M(dim(UD + "ud_bloom_floor", 0.85)),
        "fern":   M(dim(SP + "fern_floor", 0.65)),
        "water_s": M(dim(WC + "wc_river_water", 0.8)),
        "water_d": M(dim(WC + "wc_river_water", 0.6)),
        "wall":   M(dim(WC + "wc_cavern_wall", 0.6), None, 2.0),
        "bark":   M(dim(SP + "moss_rock", 0.6), None, 2.0),
    },
    floor_keys=["floor", "moss", "amber", "fern"],
    wall_keys=["wall", "bark"],
    floors={"amber": [(56, 50, 13, 13), (56, 12, 14, 8)], "moss": [(30, 76, 10, 8), (82, 76, 10, 8), (14, 52, 8, 10)],
            "fern": [(34, 30, 11, 8), (80, 30, 11, 8)]},
    walls={"bark": [(56, 50, 18, 18), (56, 12, 18, 12)]},
    pools=[[(56, 50, 4.5, 3.5, 0.9)]],
    glow_floors=("amber",),
    cfg=dict(ao=0.5, depth=0.88, lip=20, lip_col=(1.0, 0.8, 0.4), deep_dark=0.5,
             foam_col=(200, 200, 160), glows=[("d_amber", (150, 95, 20), 3.0, 0.9)]),
)


class _C:
    BAKED = "assets/tiles/hidden/{}/baked"

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


def _attach_builds():
    from tools import handbuilt_hidden_layers as H
    for name in ("build_cinderwell", "build_dreaming_root", "build_ossuary", "build_lightless_reach",
                 "build_blood_pits", "build_unwritten_stacks", "build_world_root"):
        setattr(_C, name, staticmethod(getattr(H, name)))


def main():
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    _attach_builds()
    BD.C = _C
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.bake_spec(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
