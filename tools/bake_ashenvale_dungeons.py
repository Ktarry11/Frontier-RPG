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


def spec_barrows():
    from tools import handbuilt_howling_barrows as HB
    R = HB.ROOMS
    return dict(
        build="build_barrows_baked", seed=412, slug="howling_barrows",
        materials={
            "floor": M(_a("barrows_floor")),
            "bone": M(_a("bone_hall_floor")),
            "wall": M(_a("barrows_wall")),
            "ossuary": M(_a("bone_hall_wall")),
            "cliff": M(_a("cliff_a")),
            "water_s": M(_a("barrows_floor")),
            "water_d": M(_a("barrows_floor")),
        },
        floor_keys=["floor", "bone"],
        wall_keys=["wall", "ossuary", "cliff"],
        floors={
            "bone": [(R["west"][0], R["west"][1], 10, 8), (R["east"][0], R["east"][1], 10, 8),
                     (R["hall"][0], R["hall"][1] - 1, 19, 10)],
        },
        walls={
            "ossuary": [(R["west"][0], R["west"][1], 13, 11), (R["east"][0], R["east"][1], 13, 11),
                        (R["gallery"][0], R["gallery"][1], 14, 9)],
            "cliff": [(R["gate"][0], R["gate"][1], 13, 8), (R["alcove_w"][0], R["alcove_w"][1], 8, 6)],
        },
        pools=[],
        cfg=dict(ao=0.50, depth=0.78, lip=18, lip_col=(0.70, 0.86, 1.0), deep_dark=0.2,
                 foam_col=(220, 235, 255), glows=[]),
    )


CS = "caves/seamless/"


def spec_bfd():
    """Blackfathom Deeps: the sunken night-elf temple.  Walls and floors are deliberately different materials (Kyle:
    they read as the same thing in the old tile version): wet cave rock walls, coral walls in the naga grottos, dark temple
    stone in the Sacellum / Twilight Gauntlet; sand, pearl, kelp and flagstone floors by area."""
    return dict(
        build="build_bfd_baked", seed=523, slug="blackfathom_deeps", tile_water=True,
        materials={
            "floor": M(CS + "gro_cave_floor_a"),
            "sand": M(dim(CS + "gro_sand_a", 0.62)),
            "temple": M(CS + "gro_temple_floor_a"),
            "pearl": M(dim(CS + "gro_pearl_floor_a", 0.60)),
            "deck": M(dim(CS + "gro_deck_a", 0.9)),
            "kelp": M(CS + "gro_kelp_floor_a"),
            "water_s": M(CS + "gro_tidepool_a"),
            "water_d": M(CS + "gro_deep_floor_a"),
            "wall": M(CS + "gro_cave_wall_a"),
            "coral": M(CS + "gro_coral_wall_a"),
            "twall": M(CS + "gro_temple_wall_a"),
            "vent": M(CS + "gro_vent_wall_a"),
        },
        floor_keys=["floor", "sand", "temple", "pearl", "deck", "kelp"],
        wall_keys=["wall", "coral", "twall", "vent"],
        floors={
            "sand": [(120, 198, 16, 10), (196, 202, 16, 10), (150, 203, 12, 3)],
            "pearl": [(50, 105, 16, 12), (45, 12, 16, 11)],
            "temple": [(120, 40, 13, 9), (120, 13, 24, 13), (165, 94, 14, 10), (120, 28, 3, 12)],
            "deck": [(191, 200, 6, 4)],
            "kelp": [(130, 65, 12, 9), (130, 152, 9, 7)],
        },
        walls={
            "coral": [(50, 105, 19, 15), (196, 200, 18, 13), (130, 65, 15, 12), (40, 12, 16, 12)],
            "twall": [(120, 26, 28, 30), (165, 93, 16, 13)],
            "vent": [(130, 152, 30, 22), (120, 190, 14, 8)],
        },
        pools=[],
        cfg=dict(ao=0.42, depth=0.86, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
                 foam_col=(200, 240, 245), glows=[]),
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
    def build_bfd_baked():
        """The runtime zone, with wall/cliff collision renamed to the baker's 'rock'."""
        from tools import handbuilt_dungeons as HD
        zone = HD.build_blackfathom_deeps()
        for row in zone.collision_layer:
            for x, c in enumerate(row):
                if c in ("wall", "cliff"):
                    row[x] = "rock"
        return zone, None

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


BD.C = _C
SPEC_FNS = {"moonwell_hollow": spec_moonwell, "howling_barrows": spec_barrows, "blackfathom_deeps": spec_bfd}
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv in args:
        args.remove(pv)
    for k in (args or list(SPEC_FNS)):
        BD.SPECS[k] = SPEC_FNS[k]()
        BD.bake_spec(k, pv)
