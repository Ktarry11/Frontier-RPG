"""
Bake the two Echo Isles cave paintings.

    python3 tools/bake_echo_caves.py [temple_grotto|hollow ...] [--preview DIR]

Reuses the Durotar cave baker (tools/bake_durotar_caves.bake_spec) with Echo's own
layouts (tools/handbuilt_echo_caves) and material specs.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_echo_caves as EC
from tools.bake_durotar_caves import M, dim, CS, VC

EM = "echo_caves/materials/"

SPECS = {}

# Sunken Temple Grotto: a DROWNED TEMPLE (ornate temple floors, coral and kelp), not a cave
SPECS["temple_grotto"] = dict(
    build="build_temple_grotto", seed=101, slug="temple_grotto",
    materials={
        "temple":  M(CS + "gro_temple_floor_a"),
        "sand":    M(dim(CS + "gro_sand_a", 0.62)),
        "cave":    M(dim(CS + "gro_cave_floor_a", 0.80)),
        "pearl":   M(dim(CS + "gro_pearl_floor_a", 0.60)),
        "kelp":    M(CS + "gro_kelp_floor_a"),
        "deck":    M(dim(CS + "gro_deck_a", 0.9)),
        "water_s": M(CS + "gro_tidepool_a"),
        "water_d": M(CS + "gro_deep_floor_a"),
        "twall":   M(CS + "gro_temple_wall_a"),
        "wall":    M(CS + "gro_cave_wall_a"),
        "coral":   M(CS + "gro_coral_wall_a"),
        "vent":    M(CS + "gro_vent_wall_a"),
    },
    floor_keys=["temple", "sand", "cave", "pearl", "kelp", "deck"],
    wall_keys=["twall", "wall", "coral", "vent"],
    floors={
        "sand": [(50, 80, 12, 5), (42, 79, 5, 4), (58, 79, 5, 4)],
        "cave": [(16, 68, 12, 8), (10, 63, 5, 4), (18, 74, 6, 4), (16, 42, 11, 8), (9, 38, 4, 4)],
        "pearl": [(84, 42, 10, 7), (91, 38, 4, 4)],
        "kelp": [(84, 69, 11, 7), (90, 63, 4, 4)],
        "deck": [(50, 8, 14, 5)],
    },
    walls={"wall": [(16, 68, 14, 10), (10, 63, 6, 6), (16, 42, 12, 10), (50, 80, 14, 7)],
           "coral": [(84, 69, 14, 10), (84, 42, 14, 10)],
           "vent": [(50, 6, 12, 5), (16, 42, 6, 5)]},
    pools=[EC.STG_POOLS],
    cfg=dict(ao=0.42, depth=0.84, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
             foam_col=(200, 240, 245), glows=[]),
)

# Zalazane's Hollow: packed dark earth, voodoo sigils, bone, hide
SPECS["hollow"] = dict(
    build="build_hollow", seed=113, slug="hollow",
    materials={
        "dirt":    M(dim(VC + "den_floor_damp", 0.75), dim(VC + "den_floor_a", 0.7)),
        "sigil":   M(EM + "zal_floor"),
        "bones":   M(dim(VC + "vot_bonesand", 0.62)),
        "straw":   M(dim(CS + "keep_kennel_a", 0.85)),
        "ash":     M(dim(CS + "rf_ash_floor_a", 0.9)),
        "rock":    M(VC + "vot_rock_dark"),
        "zwall":   M(EM + "zal_wall"),
        "bonew":   M(VC + "den_wall_bones"),
        "basalt":  M(CS + "rf_basalt_wall_a"),
    },
    floor_keys=["dirt", "sigil", "bones", "straw", "ash"],
    wall_keys=["rock", "zwall", "bonew", "basalt"],
    floors={
        "sigil": [(52, 28, 14, 6), (52, 9, 15, 6), (18, 66, 8, 5), (18, 42, 8, 5), (52, 66, 8, 4)],
        "bones": [(84, 66, 10, 6), (82, 42, 9, 5), (52, 84, 8, 3)],
        "straw": [(52, 46, 13, 6), (44, 44, 4, 3), (60, 44, 4, 3)],
        "ash": [(52, 28, 6, 3), (52, 9, 6, 3)],
    },
    walls={"zwall": [(52, 9, 20, 9), (52, 28, 16, 8), (18, 42, 11, 8), (52, 14, 6, 5)],
           "bonew": [(84, 66, 13, 9), (82, 42, 12, 8)],
           "basalt": [(18, 66, 12, 9)]},
    pools=[],
    cfg=dict(ao=0.50, depth=0.90, lip=22, lip_col=(1.0, 0.7, 0.9), deep_dark=0.45,
             foam_col=(200, 220, 220), glows=[]),
)

BD.C = EC
BD.SPECS = SPECS

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    for k in (args or list(SPECS)):
        BD.bake_spec(k, pv)
