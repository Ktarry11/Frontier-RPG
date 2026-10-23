"""
Bake the Silverpine dungeon paintings (Widow's Lair, Ambermill Tower, Shadowfang Keep) from the seamless Silverpine materials
(assets/tiles/silverpine/materials/sp_*.png), through the Durotar cave baker.

    PYTHONPATH=. python3 tools/bake_silverpine_dungeons.py [widows_lair|ambermill_tower|shadowfang_keep ...] [--preview DIR]
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

SP = "silverpine/materials/sp_"


class _C:
    BAKED = "assets/tiles/{}/baked"
    _builds = {}

    def __getattr__(self, name):
        if name in self._builds:
            return self._builds[name]
        raise AttributeError(name)

    @staticmethod
    def pool_fields(pools, gx, gy):
        from tools.handbuilt_vot_caves import pool_fields
        return pool_fields(pools, gx, gy)


C = _C()
SPECS = {}


def spec_widows():
    from tools import handbuilt_widows_lair as WL
    R = WL.ROOMS
    C._builds["build_widows_baked"] = WL.build_widows_baked
    return dict(
        build="build_widows_baked", seed=517, slug="widows_lair",
        materials={
            "floor":  M(SP + "cave_floor", SP + "root_earth"),
            "web":    M(SP + "web_ground"),
            "nest":   M(SP + "peat", SP + "root_earth"),
            "wall":   M(dim(SP + "cave_wall", 0.85)),
            "webwall": M(SP + "web_wall"),
            "rock":   M(SP + "rock_wall"),
            "water_s": M(SP + "pool_shallow_flat"),
            "water_d": M(SP + "pool_deep_flat"),
        },
        floor_keys=["floor", "web", "nest"],
        wall_keys=["wall", "webwall", "rock"],
        floors={
            "web": [(R["hub"][0], R["hub"][1], 20, 16), (R["mouth"][0], R["mouth"][1], 14, 7),
                    (R["spire"][0], R["spire"][1], 25, 14), (R["skitter"][0], R["skitter"][1], 17, 13)],
            "nest": [(R["silka"][0], R["silka"][1], 16, 12), (R["nurs_w"][0], R["nurs_w"][1], 11, 8),
                     (R["nurs_e"][0], R["nurs_e"][1], 11, 8)],
        },
        walls={
            "webwall": [(R["hub"][0], R["hub"][1], 22, 18), (R["spire"][0], R["spire"][1], 27, 16),
                        (R["skitter"][0], R["skitter"][1], 19, 15)],
            "rock": [(R["silka"][0], R["silka"][1], 19, 15), (R["larder"][0], R["larder"][1], 11, 9),
                     (R["pit"][0], R["pit"][1], 11, 9)],
        },
        pools=[],
        cfg=dict(ao=0.48, depth=0.80, lip=18, lip_col=(0.8, 0.85, 0.95), deep_dark=0.2,
                 foam_col=(220, 230, 240), glows=[]),
    )


def spec_tower():
    from tools import handbuilt_ambermill_tower as AT
    R = AT.ROOMS
    C._builds["build_tower_baked"] = AT.build_tower_baked
    box = lambda k, pad=2: ((R[k][0] + R[k][2]) / 2, (R[k][1] + R[k][3]) / 2, (R[k][2] - R[k][0]) / 2 + pad, (R[k][3] - R[k][1]) / 2 + pad)
    return dict(
        build="build_tower_baked", seed=523, slug="ambermill_tower",
        materials={
            "floor":  M(SP + "slate_clean"),
            "arcane": M(SP + "arcane_floor"),
            "keep":   M(SP + "keep_floor", SP + "flagstone"),
            "ritual": M(SP + "ritual_floor"),
            "kwall":  M(SP + "keep_wall"),
            "twall":  M(SP + "tower_wall"),
            "rock":   M(SP + "keep_wall_mossy"),
            "water_s": M(SP + "pool_shallow_flat"),
            "water_d": M(SP + "pool_deep_flat"),
        },
        floor_keys=["floor", "arcane", "keep", "ritual"],
        wall_keys=["kwall", "twall", "rock"],
        floors={
            "arcane": [box("observ"), box("orrery")],
            "keep":   [box("lab"), box("store"), box("vestibule")],
            "ritual": [(75, 18, 11, 7)],
        },
        walls={
            "twall": [box("observ", 3), box("orrery", 3), box("reading", 3), box("gallery", 3)],
            "rock":  [box("vestibule", 3), box("map_room", 3), box("scripto", 3), box("lab", 3), box("store", 3)],
        },
        pools=[],
        cfg=dict(ao=0.46, depth=0.74, lip=20, lip_col=(0.80, 0.88, 1.0), deep_dark=0.2,
                 foam_col=(220, 235, 255), glows=[]),
    )


def spec_keep():
    from tools import handbuilt_shadowfang_keep as SK
    R = SK.ROOMS
    C._builds["build_keep_baked"] = SK.build_keep_baked
    box = lambda k, pad=2: ((R[k][0] + R[k][2]) / 2, (R[k][1] + R[k][3]) / 2, (R[k][2] - R[k][0]) / 2 + pad, (R[k][3] - R[k][1]) / 2 + pad)
    return dict(
        build="build_keep_baked", seed=541, slug="shadowfang_keep",
        materials={
            "floor":  M(SP + "slate_clean"),
            "keepf":  M(SP + "keep_floor"),
            "flag":   M(SP + "flagstone", SP + "old_cobble"),
            "crypt":  M(SP + "crypt_floor"),
            "den":    M(SP + "root_earth"),
            "arcane": M(SP + "arcane_floor"),
            "ritual": M(SP + "ritual_floor"),
            "slate":  M(SP + "slate_clean"),
            "wall":   M(SP + "keep_wall"),
            "mossy":  M(SP + "keep_wall_mossy"),
            "cwall":  M(SP + "sepulcher_wall"),
            "rock":   M(SP + "rock_wall"),
            "water_s": M(SP + "pool_shallow_flat"),
            "water_d": M(SP + "pool_deep_flat"),
        },
        floor_keys=["floor", "keepf", "flag", "crypt", "den", "arcane", "ritual", "slate"],
        wall_keys=["wall", "mossy", "cwall", "rock"],
        floors={
            "flag":   [box("bailey"), box("gate")],
            "keepf":  [box("hall")],
            "crypt":  [(33, 53, 25, 20)],
            "den":    [box("kennel"), box("yard")],
            "arcane": [(100, 16, 18, 14)],
            "ritual": [(100, 18, 11, 8)],
            "slate":  [box("armory"), (178, 78, 14, 16), box("landing", 4)],
        },
        walls={
            "mossy": [box("bailey", 3), box("gate", 3), box("hall", 2)],
            "cwall": [(33, 53, 26, 21)],
            "rock":  [box("kennel", 3), box("yard", 3)],
        },
        pools=[],
        cfg=dict(ao=0.46, depth=0.76, lip=18, lip_col=(0.80, 0.82, 0.95), deep_dark=0.2,
                 foam_col=(220, 230, 240), glows=[]),
    )


REGISTRY = {"widows_lair": spec_widows, "ambermill_tower": spec_tower, "shadowfang_keep": spec_keep}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    keys = args or list(REGISTRY)
    BD.C = C
    for k in keys:
        SPECS[k] = REGISTRY[k]()
    BD.SPECS = SPECS
    for k in keys:
        BD.bake_spec(k, pv)


if __name__ == "__main__":
    main()
