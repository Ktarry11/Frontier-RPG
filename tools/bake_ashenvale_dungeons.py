"""
Bake the Ashenvale dungeon paintings (Moonwell Hollow, Howling Barrows, Grom's Rest) from the real Ashenvale
materials in assets/tiles/ashenvale/materials (av_*.png, 256px seamless), through the Durotar cave baker.

    PYTHONPATH=. python3 tools/bake_ashenvale_dungeons.py [moonwell_hollow|howling_barrows|groms_rest ...] [--preview DIR]
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

AV = "ashenvale/materials/av_"


def _a(name):
    return AV + name


def spec_moonwell():
    from tools import handbuilt_moonwell_hollow as MH
    R = MH.ROOMS
    return dict(
        build="build_moonwell_baked", seed=311, slug="moonwell_hollow",
        materials={
            "floor": M(_a("root_earth"), _a("forest_floor")),
            "fern": M(_a("fern_floor")),
            "cobble": M(_a("mossy_cobble")),
            "rim": M(_a("moon_rim")),
            "water_s": M(_a("moon_water")),
            "water_d": M(_a("moon_water")),
            "wall": M(_a("rock_wall")),
            "roots": M(_a("corrupt_root_wall")),
            "cliff": M(_a("cliff_b")),
        },
        floor_keys=["floor", "fern", "cobble", "rim"],
        wall_keys=["wall", "roots", "cliff"],
        floors={
            "fern": [(R["grotto"][0], R["grotto"][1] + 1, 24, 11), (R["lantern"][0], R["lantern"][1], 8, 6),
                     (R["alcove"][0], R["alcove"][1], 8, 6)],
            "cobble": [(R["sanctum"][0], R["sanctum"][1] - 2, 30, 13)],
            "rim": [(R["sanctum"][0], R["sanctum"][1] + 3, 13, 8)],
        },
        walls={
            "roots": [(R["sanctum"][0], R["sanctum"][1] - 6, 30, 12), (R["alcove"][0], R["alcove"][1], 10, 8)],
            "cliff": [(R["grotto"][0], R["grotto"][1] + 8, 24, 8)],
        },
        pools=[MH.MH_POOLS],
        cfg=dict(ao=0.44, depth=0.80, lip=22, lip_col=(0.55, 0.78, 0.95), deep_dark=0.18,
                 foam_col=(200, 225, 255), glows=[]),
    )


class _C:
    BAKED = "assets/tiles/{}/baked"

    @staticmethod
    def build_moonwell_baked():
        from tools import handbuilt_moonwell_hollow as MH
        return MH.build_moonwell_baked()

    @staticmethod
    def build_barrows_baked():
        from tools import handbuilt_howling_barrows as HB
        return HB.build_barrows_baked()

    @staticmethod
    def build_groms_baked():
        from tools import handbuilt_groms_rest as GR
        return GR.build_groms_baked()

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


BD.C = _C
SPEC_FNS = {"moonwell_hollow": spec_moonwell}
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv in args:
        args.remove(pv)
    for k in (args or list(SPEC_FNS)):
        BD.SPECS[k] = SPEC_FNS[k]()
        BD.bake_spec(k, pv)
