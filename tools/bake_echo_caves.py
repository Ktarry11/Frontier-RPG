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
        "sand": [(60, 92, 12, 5)],
        "cave": [(12, 58, 11, 9), (22, 13, 13, 9)],
        "pearl": [(100, 14, 11, 9)],
        "kelp": [(108, 60, 11, 10)],
        "deck": [(60, 48, 9, 9)],
    },
    walls={"wall": [(12, 58, 13, 11), (22, 13, 13, 10), (60, 92, 14, 7)],
           "coral": [(108, 60, 14, 12), (100, 14, 14, 12)],
           "vent": [(60, 100, 14, 6)]},
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
        "sigil": [(74, 20, 15, 9), (28, 14, 16, 8), (50, 75, 9, 5), (22, 36, 9, 6)],
        "bones": [(100, 70, 13, 9), (110, 32, 11, 8), (16, 72, 6, 3)],
        "straw": [(76, 48, 12, 8)],
        "ash": [(72, 20, 6, 3), (28, 12, 6, 3)],
    },
    walls={"zwall": [(28, 14, 20, 12), (74, 20, 18, 12), (22, 36, 12, 10)],
           "bonew": [(100, 70, 15, 12), (110, 32, 13, 11)],
           "basalt": [(50, 75, 11, 8)]},
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
