"""
Bake the Scourge Cave painting.

    python3 tools/bake_scourge_cave.py [--preview DIR]

Reuses the Durotar cave baker (tools/bake_durotar_caves.bake_spec) with the Scourge Cave layout
(tools/handbuilt_scourge_cave) and the seamless Tirisfal materials (assets/tiles/tirisfal/materials).
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_scourge_cave as SC
from tools.bake_durotar_caves import M, dim

TF = "tirisfal/materials/tf_"

# Scourge Cave: blighted bone-earth, bone drifts in the Bone Pit and the skull, plague ground in the lab,
# ritual stone under the Abomination; ossuary walls where the bone is thick.
SPEC = dict(
    build="build_scourge", seed=163, slug="main",
    materials={
        "floor":  M(TF + "scourge_earth"),
        "bones":  M(TF + "bone_dirt"),
        "plague": M(TF + "plague_ground"),
        "ritual": M(TF + "ritual_floor"),
        "cave":   M(TF + "cave_floor"),
        "wall":   M(dim(TF + "cave_wall", 0.8)),
        "rock":   M(TF + "rock_wall"),
        "ossw":   M(TF + "ossuary_wall"),
    },
    floor_keys=["floor", "bones", "plague", "ritual", "cave"],
    wall_keys=["wall", "rock", "ossw"],
    floors={
        "bones": [(11, 41, 10, 8), (45, 13, 14, 8), (45, 64, 8, 4)],
        "plague": [(79, 29, 10, 8), (84, 26, 4, 3)],
        "ritual": [(45, 12, 7, 5), (45, 5, 4, 2)],
        "cave": [(19, 63, 5, 4), (34, 9, 3, 3), (56, 9, 3, 3)],
    },
    walls={"ossw": [(45, 10, 20, 11), (11, 41, 13, 10)],
           "rock": [(60, 26, 16, 12), (30, 50, 12, 10)]},
    pools=[],
    cfg=dict(ao=0.50, depth=0.90, lip=26, lip_col=(0.88, 0.98, 0.85), deep_dark=0.4,
             foam_col=(200, 220, 200), glows=[]),
)

BD.C = SC
BD.SPECS = {"scourge": SPEC}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.bake_spec("scourge", pv)
