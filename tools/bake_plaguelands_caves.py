"""
Bake the Plaguelands' four caves (tools/handbuilt_plaguelands_caves.py).

    PYTHONPATH=. python3 tools/bake_plaguelands_caves.py [writhing_deep weeping_cave marris_crypt bone_mines]
                                                          [--preview DIR]

Existing art only (Kyle: "when we do the caves we can use existing art most likely"): the seamless Tirisfal
materials the Scourge Cave was painted with. Each cave reads differently underfoot:

  THE WRITHING DEEP   scourge earth, webbed floor in the brood chamber and the Bride's pocket, bone dirt out at the rim
  THE WEEPING CAVE    wet cave floor, mud and standing water where the rungs run down and in the pool at the end
  THE MARRIS CRYPT    crypt flagstones, marble in the chapel, grave gravel in the niches; ossuary walls round the hall
  THE BONE MINES      broken rock, bone dirt in the workings, scourge earth in the pit, a ritual floor in the workshop
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_plaguelands_caves as PC
from tools.bake_durotar_caves import M, dim

TF = "tirisfal/materials/tf_"


def _room(cave, rname, pad=0):
    x, y, w, h = PC.ROOM_NAMES[cave][rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec_writhing():
    c = PC.WRITHING
    PC.build(c)
    return dict(
        build="build_writhing_baked", seed=401, slug="writhing_deep",
        materials={"floor": M(TF + "scourge_earth"), "web_f": M(TF + "cobweb_floor"), "bone_f": M(TF + "bone_dirt"),
                   "wall": M(dim(TF + "cave_wall", 0.8)), "rock_w": M(TF + "rock_wall")},
        floor_keys=["floor", "web_f", "bone_f"],
        wall_keys=["wall", "rock_w"],
        floors={"web_f": [_room(c, "The Brood Chamber", 2), _room(c, "The Bride's Pocket", 1)],
                "bone_f": [(14, 40, 6, 10), (82, 40, 6, 10), (48, 8, 10, 4), (30, 70, 8, 5), (66, 70, 8, 5)]},
        walls={"rock_w": [(48, 40, 22, 20)]},
        pools=[],
        cfg=dict(ao=0.52, depth=0.90, lip=22, lip_col=(0.86, 0.94, 0.84), deep_dark=0.45,
                 foam_col=(200, 210, 200), glows=[]),
    )


def spec_weeping():
    c = PC.WEEPING
    PC.build(c)
    return dict(
        build="build_weeping_baked", seed=409, slug="weeping_cave",
        materials={"floor": M(TF + "cave_floor"), "mud_f": M(TF + "mud_puddles"), "moss_f": M(TF + "marsh_moss"),
                   "wall": M(TF + "rock_wall"), "wet_w": M(dim(TF + "cave_wall", 0.7))},
        floor_keys=["floor", "mud_f", "moss_f"],
        wall_keys=["wall", "wet_w"],
        floors={"mud_f": [(25, 32, 4, 12), (43, 32, 4, 12), (63, 32, 4, 12), (83, 32, 4, 12),
                          _room(c, "The Weeping Pool")],
                "moss_f": [(30, 48, 14, 4), (70, 48, 14, 4), _room(c, "The Hermit's Cell")]},
        walls={"wet_w": [_room(c, "The Weeping Pool", 6), (52, 32, 46, 8)]},
        pools=[],
        cfg=dict(ao=0.50, depth=0.88, lip=24, lip_col=(0.82, 0.90, 0.96), deep_dark=0.42,
                 foam_col=(190, 210, 220), glows=[]),
    )


def spec_marris():
    c = PC.MARRIS
    PC.build(c)
    return dict(
        build="build_marris_baked", seed=419, slug="marris_crypt",
        materials={"floor": M(TF + "crypt_floor"), "marble_f": M(TF + "mausoleum_marble"),
                   "gravel_f": M(TF + "grave_gravel"),
                   "wall": M(TF + "crypt_wall"), "oss_w": M(TF + "ossuary_wall")},
        floor_keys=["floor", "marble_f", "gravel_f"],
        wall_keys=["wall", "oss_w"],
        floors={"marble_f": [_room(c, "The Choir Chapel"), (45, 39, 6, 6)],
                "gravel_f": [(14, 40, 6, 26), (76, 40, 6, 26), (32, 40, 3, 22), (58, 40, 3, 22)]},
        walls={"oss_w": [_room(c, "The Sexton's Hall", 5), _room(c, "The Choir Chapel", 4)]},
        pools=[],
        cfg=dict(ao=0.46, depth=0.86, lip=18, lip_col=(0.90, 0.88, 0.82), deep_dark=0.38,
                 foam_col=(210, 205, 195), glows=[]),
    )


def spec_bone():
    c = PC.BONE
    PC.build(c)
    return dict(
        build="build_bone_baked", seed=421, slug="bone_mines",
        materials={"floor": M(TF + "rocky_ground"), "bone_f": M(TF + "bone_dirt"),
                   "scourge_f": M(TF + "scourge_earth"), "ritual_f": M(TF + "ritual_floor"),
                   "wall": M(TF + "rock_wall"), "oss_w": M(TF + "ossuary_wall")},
        floor_keys=["floor", "bone_f", "scourge_f", "ritual_f"],
        wall_keys=["wall", "oss_w"],
        floors={"bone_f": [(50, 48, 30, 4), (40, 30, 26, 4), (30, 12, 14, 4)],
                "scourge_f": [_room(c, "The Marrow Pit")],
                "ritual_f": [_room(c, "The Ossifier's Workshop")]},
        walls={"oss_w": [_room(c, "The Marrow Pit", 5), _room(c, "The Ossifier's Workshop", 3)]},
        pools=[],
        cfg=dict(ao=0.50, depth=0.88, lip=20, lip_col=(0.88, 0.84, 0.76), deep_dark=0.42,
                 foam_col=(205, 200, 190), glows=[]),
    )


SPECS = {"writhing_deep": (PC.WRITHING, spec_writhing), "weeping_cave": (PC.WEEPING, spec_weeping),
         "marris_crypt": (PC.MARRIS, spec_marris), "bone_mines": (PC.BONE, spec_bone)}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        cave, fn = SPECS[k]
        spec = fn()
        BD.SPECS = {k: spec}
        BD.C = types.SimpleNamespace(BAKED=PC.BAKED[cave], **{spec["build"]: getattr(PC, spec["build"])})
        BD.bake_spec(k, pv)
