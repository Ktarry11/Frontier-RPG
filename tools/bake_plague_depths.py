"""
Bake the Plague Depths painting from the seamless Tirisfal/Undercity materials (assets/tiles/tirisfal/materials/tf_*.png),
through the Durotar cave baker.  Each chamber gets its own floor + wall so the rooms read apart: wet sewer-brick cistern,
crypt-stone Court, marble Throne of Rot, flagstone Archive, plague-soaked Vault, ritual Heart.

    PYTHONPATH=. python3 tools/bake_plague_depths.py [--preview DIR]
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_plague_depths as PD
from tools.bake_durotar_caves import M, dim

TF = "tirisfal/materials/tf_"


class _C:
    BAKED = "assets/tiles/{}/baked"

    @staticmethod
    def build_plague_baked():
        return PD.build_plague_baked()

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


R = PD.ROOMS
SPEC = dict(
    build="build_plague_baked", seed=277, slug="plague_depths",
    materials={
        "floor":   M(TF + "sewer_floor", dim(TF + "cave_floor", 0.9)),
        "crypt":   M(TF + "crypt_floor"),
        "marble":  M(dim(TF + "mausoleum_marble", 0.85)),
        "flag":    M(TF + "flagstone", TF + "old_cobble"),
        "plague":  M(TF + "plague_ground"),
        "slime":   M(TF + "plague_slime", TF + "plague_ground"),
        "ritual":  M(TF + "ritual_floor"),
        "water_s": M("tirisfal/materials/uc_sewer_water"),
        "water_d": M("tirisfal/materials/uc_sewer_water"),
        "wall":    M(dim(TF + "cave_wall", 0.8)),
        "cwall":   M(TF + "crypt_wall"),
        "ossw":    M(TF + "ossuary_wall"),
        "rock":    M(TF + "rock_wall"),
    },
    floor_keys=["floor", "crypt", "marble", "flag", "plague", "slime", "ritual"],
    wall_keys=["wall", "cwall", "ossw", "rock"],
    floors={
        "crypt":  [(R["loom"][0], R["loom"][1], 25, 18), (R["ante"][0], R["ante"][1], 27, 13),
                   (R["nook_w"][0], R["nook_w"][1], 9, 7), (R["nook_nw"][0], R["nook_nw"][1], 9, 7)],
        "marble": [(R["throne"][0], R["throne"][1], 27, 18)],
        "flag":   [(R["archive"][0], R["archive"][1], 26, 18), (R["nook_ne"][0], R["nook_ne"][1], 9, 7),
                   (R["mid"][0], R["mid"][1], 19, 11)],
        "plague": [(R["vault"][0], R["vault"][1], 27, 18), (R["nook_e"][0], R["nook_e"][1], 9, 7),
                   (R["nook_se"][0], R["nook_se"][1], 9, 7)],
        "slime":  [(R["heart"][0], R["heart"][1], 35, 17)],
        "ritual": [(R["heart"][0], R["heart"][1] + 2, 17, 10)],
    },
    walls={
        "cwall": [(R["loom"][0], R["loom"][1], 26, 19), (R["throne"][0], R["throne"][1], 28, 19),
                  (R["nook_w"][0], R["nook_w"][1], 10, 8)],
        "ossw":  [(R["heart"][0], R["heart"][1], 36, 18), (R["ante"][0], R["ante"][1], 27, 14)],
        "rock":  [(R["archive"][0], R["archive"][1], 26, 19), (R["vault"][0], R["vault"][1], 28, 19),
                  (R["nook_sw"][0], R["nook_sw"][1], 10, 8), (R["nook_se"][0], R["nook_se"][1], 10, 8)],
    },
    pools=[PD.PD_POOLS],
    cfg=dict(ao=0.48, depth=0.80, lip=20, lip_col=(0.55, 0.95, 0.35), deep_dark=0.2,
             foam_col=(190, 235, 150), glows=[]),
)

BD.C = _C
BD.SPECS = {"plague_depths": SPEC}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.bake_spec("plague_depths", pv)
