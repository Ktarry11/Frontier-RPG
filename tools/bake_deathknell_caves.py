"""
Bake the two Deathknell cave paintings.

    python3 tools/bake_deathknell_caves.py [nwh|crypt ...] [--preview DIR]

Reuses the Durotar cave baker (tools/bake_durotar_caves.bake_spec) with Deathknell's own layouts
(tools/handbuilt_deathknell_caves) and the seamless Tirisfal materials (assets/tiles/tirisfal/materials).
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_deathknell_caves as DC
from tools.bake_durotar_caves import M, dim

TF = "tirisfal/materials/tf_"

SPECS = {}

# Night Web's Hollow: damp burrow earth, silk everywhere, roots in the nurseries, bone in the pit
_web_pts = [DC.web_pt(f) for f in (0.30, 0.45, 0.60, 0.72, 0.85, 0.95)]
SPECS["nwh"] = dict(
    build="build_nwh", seed=131, slug="nwh",
    materials={
        "floor":  M(TF + "cave_floor"),
        "web":    M(TF + "cobweb_floor"),
        "roots":  M(TF + "root_floor"),
        "bones":  M(TF + "bone_dirt"),
        "wall":   M(TF + "cave_wall"),
        "rock":   M(TF + "rock_wall"),
    },
    floor_keys=["floor", "web", "roots", "bones"],
    wall_keys=["wall", "rock"],
    floors={
        "web": [(45, 34, 11, 9), (79, 58, 9, 7), (78, 12, 9, 7)] + [(round(x), round(y), 5, 4) for x, y in _web_pts],
        "roots": [(12, 12, 9, 7), (45, 66, 8, 4)],
        "bones": [(11, 58, 8, 6)],
    },
    walls={"rock": [(12, 12, 14, 11), (78, 12, 14, 11), (11, 58, 13, 10), (79, 58, 13, 10)]},
    pools=[],
    cfg=dict(ao=0.48, depth=0.88, lip=20, lip_col=(0.85, 0.95, 0.9), deep_dark=0.4,
             foam_col=(200, 220, 220), glows=[]),
)

# Scarlet Crypt: dressed crypt stone, a bone ossuary west, marble reliquary east, scarlet tile in the sanctum
SPECS["crypt"] = dict(
    build="build_crypt", seed=147, slug="crypt",
    materials={
        "crypt":  M(TF + "crypt_floor"),
        "marble": M(TF + "mausoleum_marble"),
        "scarlet": M(TF + "scarlet_floor"),
        "bones":  M(TF + "bone_dirt"),
        "earth":  M(TF + "graveyard_earth"),
        "cwall":  M(dim(TF + "crypt_wall", 0.55)),
        "ossw":   M(TF + "ossuary_wall"),
        "swall":  M(TF + "scarlet_wall"),
        "mwall":  M(dim(TF + "stone_wall", 0.6)),
    },
    floor_keys=["crypt", "marble", "scarlet", "bones", "earth"],
    wall_keys=["cwall", "ossw", "swall", "mwall"],
    floors={
        "marble": [(47, 32, 10, 9), (71, 54, 13, 13), (47, 18, 4, 6)],
        "scarlet": [(47, 9, 8, 4), (81, 32, 7, 6), (71, 54, 4, 4)],
        "bones": [(23, 54, 13, 13)],
        "earth": [(15, 32, 7, 7)],
    },
    walls={"ossw": [(23, 54, 16, 16), (15, 32, 11, 11)],
           "swall": [(47, 5, 14, 5)],
           "mwall": [(47, 73, 15, 8)]},
    pools=[],
    cfg=dict(ao=0.50, depth=0.90, lip=34, lip_col=(1.0, 0.88, 0.75), deep_dark=0.4,
             foam_col=(200, 220, 220), glows=[]),
)

BD.C = DC
BD.SPECS = SPECS

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    for k in (args or list(SPECS)):
        BD.bake_spec(k, pv)
