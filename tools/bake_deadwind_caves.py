"""
Bake Deadwind's two caves (tools/handbuilt_deadwind_caves.py).

    PYTHONPATH=. python3 tools/bake_deadwind_caves.py [widows_nest drowned_seep] [--preview DIR]

Painted from Kyle's Deadwind ground sheet (docs/deadwind_art_prompts.md sheet 1), which has cave ground of its own:

  THE WIDOWS' NEST   silk over the Sheet, glowing egg floor in the alcoves and the brood, bare cave floor up the
                     Throat; black rock walls, with the seep glowing through them nearer the brood
  THE DROWNED SEEP   ooze mud along the banks, cave floor between, the seep itself as toxic water over black water in
                     the deep stretches, and flesh growing over the sump's shelf; seep-veined cave walls
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_deadwind_caves as DC
from tools.bake_durotar_caves import M, dim

DW = "deadwind/ground/dw_"


def _room(cave, rname, pad=0):
    x, y, w, h = DC.ROOM_NAMES[cave][rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec_nest():
    c = DC.NEST
    DC.build(c)
    alcoves = [(x, y, 4, 3) for (x, y) in DC.EGG_ALCOVES]
    retreats = [(p[0], p[1], 5, 4) for (_s, _l, p) in DC.RETREATS]
    return dict(
        build="build_nest_baked", seed=581, slug="widows_nest",
        materials={"floor": M(DW + "cave_floor"), "web_f": M(DW + "web_floor"), "egg_f": M(DW + "egg_floor"),
                   "bone_f": M(DW + "bone_crust"),
                   "wall": M(dim(DW + "black_rock", 0.55)), "seep_w": M(dim(DW + "cave_wall", 0.8))},
        floor_keys=["floor", "web_f", "egg_f", "bone_f"],
        wall_keys=["wall", "seep_w"],
        floors={"web_f": [_room(c, "The Sheet", 2)], "egg_f": alcoves + [_room(c, "The Brood", -2)],
                "bone_f": retreats},
        walls={"seep_w": [_room(c, "The Brood", 8)]},
        pools=[], glow_floors=["egg_f"],
        # the eggs are the only light in the nest
        cfg=dict(ao=0.52, depth=0.90, lip=18, lip_col=(0.80, 0.85, 0.60), deep_dark=0.46,
                 foam_col=(200, 210, 190), glows=[("d_egg_f", (140, 190, 60), 2.2, 0.55)]),
    )


def spec_seep():
    c = DC.SEEP
    DC.build(c)
    banks = [(x, y, 7, 7) for (x, y) in DC.MEANDER]
    return dict(
        build="build_seep_baked", seed=587, slug="drowned_seep",
        materials={"floor": M(DW + "cave_floor"), "mud_f": M(DW + "ooze_mud"), "flesh_f": M(DW + "flesh_growth"),
                   "seep_f": M(DW + "cave_seep"),
                   "water_s": M(DW + "toxic_water"), "water_d": M(dim(DW + "black_pond", 0.8)),
                   "wall": M(dim(DW + "cave_wall", 0.7)), "rock_w": M(dim(DW + "black_rock", 0.5))},
        floor_keys=["floor", "mud_f", "flesh_f", "seep_f"],
        wall_keys=["wall", "rock_w"],
        floors={"mud_f": banks, "flesh_f": [_room(c, "The Sump", -4)], "seep_f": [_room(c, "The Oxbows", -20)]},
        walls={"rock_w": [(50, 50, 30, 30)]},
        pools=[DC.POOLS[c]], glow_floors=["mud_f", "flesh_f"],
        # the seep lights its own banks green, and the sump glows a sick red where the flesh has grown over it
        cfg=dict(ao=0.48, depth=0.88, lip=18, lip_col=(0.70, 0.90, 0.45), deep_dark=0.50,
                 foam_col=(190, 230, 120), glows=[("d_mud_f", (110, 170, 40), 2.0, 0.45),
                                                   ("d_flesh_f", (160, 60, 50), 2.4, 0.40)]),
    )


SPECS = {"widows_nest": (DC.NEST, spec_nest), "drowned_seep": (DC.SEEP, spec_seep)}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        cave, fn = SPECS[k]
        spec = fn()
        BD.SPECS = {k: spec}
        BD.C = types.SimpleNamespace(BAKED=DC.BAKED[cave], **{spec["build"]: getattr(DC, spec["build"])})
        BD.bake_spec(k, pv)
