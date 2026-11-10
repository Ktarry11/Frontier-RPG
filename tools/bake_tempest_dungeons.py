"""
Bake Tempest Isle's two interiors: Khaz Varun and (later) the Emberdeep.

    PYTHONPATH=. python3 tools/bake_tempest_dungeons.py [key ...] [--preview DIR]

NO NEW TEXTURES. Everything paints from assets/tiles/durotar_caves/materials, the shared interior
library the whole game draws on - 60-odd pre-dimmed floors, walls, waters and decks. Two new
interiors shipping with two new texture sets would be two more things to keep in step, and the
library already has the right surface for each of these.

What differs is the PAIRING, and the pairing is chosen to say what the place is:

  The Emberdeep  ash floor on the crust islands, basalt wall, and REAL LAVA - lava=True turns on
               the baker's d_lava distance field, so the light in this dungeon comes off the lake
               rather than from nowhere. The islands are small and the lake is enormous, which is
               exactly the lighting the glow was written for.
  Khaz Varun   temple flagstones and dressed stone wall, because this is a CITY and the whole
               archetype depends on it reading as built rather than carved. Ragefire ash floor in
               the forge, the smelter and the pits - the three rooms that were still working when
               it went dark - and gravel in the borer workings, because a mine floor is spoil.
               The ONE carved room, the Ash Pits, gets basalt grit so the fissure reads as rock
               the dwarves broke into rather than a room they cut.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M

from tools import handbuilt_khaz_varun as KV
from tools import handbuilt_emberdeep as ED

CS = "caves/seamless/"      # the Ragefire set: real lava floor, lava wall and basalt wall
_L = "durotar_caves/materials/"
# The Blackfathom temple floor is deep blue-green, which is right for a drowned night elf temple
# and wrong for a Dark Iron hold - the first bake came out teal. These two are that floor and the
# dressed-stone wall desaturated to charcoal and pushed warm: soot and ember, not amethyst.
FLAG_F = "tempest/materials/kv_flagstone"     # dressed flagstones: the halls and the road
ASH_F = _L + "rf_ash_floor_a_dim90"           # the forge, the smelter, the pits
BASALT_F = _L + "tan_basalt_grit_dim66"       # the one carved room
GRAVEL_F = _L + "vot_gravel_dim62"            # the borer workings - a mine floor is spoil
STONE_W = "tempest/materials/kv_wall"         # dressed stone wall


def _rect(rooms, key, pad=2):
    x0, y0, x1, y1, _c, _n = rooms[key]
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0 + pad, (y1 - y0) / 2.0 + pad)


def spec_khaz_varun():
    R = KV.ROOMS
    return dict(
        build="build_khaz_varun_baked", seed=521, slug="khaz_varun",
        materials={"floor": M(FLAG_F), "ash_f": M(ASH_F), "basalt_f": M(BASALT_F),
                   "gravel_f": M(GRAVEL_F), "wall": M(STONE_W)},
        floor_keys=["floor", "ash_f", "basalt_f", "gravel_f"], wall_keys=["wall"],
        floors={
            # the rooms that were still working when the city went dark
            "ash_f": [_rect(R, "forge"), _rect(R, "smelter"), _rect(R, "gallery")],
            # the one carved space: a fissure they broke into, not a room they cut
            "basalt_f": [(78, 58, 22, 13), (64, 52, 9, 7), (94, 52, 9, 7)],
            "gravel_f": [_rect(R, "borer"), _rect(R, "cells")],
        },
        walls={}, pools=[],
        # Warm lip and a low ambient: a hold lit by furnace glow rather than daylight.
        cfg=dict(ao=0.44, depth=0.82, lip=18, lip_col=(0.80, 0.62, 0.42), deep_dark=0.40,
                 foam_col=(200, 195, 185), glows=[]),
    )


def spec_emberdeep():
    # Every lobe of every island, plus the stepping stones: basalt crust on top of the ash
    # floor, so the ground the player fights on reads as cooled rock rather than cinder.
    isl = [(cx, cy, rx + 2, ry + 2)
           for lobes in ED.ISLANDS.values() for (cx, cy, rx, ry) in lobes]
    isl += [(cx, cy, rx + 1, ry + 1) for (cx, cy, rx, ry) in ED.STEPPING]
    return dict(
        build="build_emberdeep_baked", seed=557, slug="emberdeep",
        materials={"floor": M(ASH_F), "basalt_f": M(BASALT_F),
                   "lava": M(CS + "rf_lava_floor_a"),
                   "wall": M(CS + "rf_basalt_wall_a"), "magma": M(CS + "rf_lava_wall_a")},
        floor_keys=["floor", "basalt_f"], wall_keys=["wall", "magma"],
        # The islands are cooled crust - basalt - standing on an ash floor.
        floors={"basalt_f": isl},
        # Magma seams in the caldera wall behind the last island, so the far end glows hottest.
        # Magma seams in the caldera wall behind the arena, so the south end - the end you
        # finish at - glows hottest.
        walls={"magma": [(85, 168, 46, 16)]},
        pools=[], lava=True,
        # A HOT grade and a strong lava glow: the lake is the only light in here.
        cfg=dict(ao=0.50, depth=0.90, lip=30, lip_col=(1.0, 0.52, 0.30), deep_dark=0.50,
                 foam_col=(150, 120, 100), glows=[("d_lava", (180, 68, 14), 3.0, 1.0)]),
    )


SPECS = {"khaz_varun": (spec_khaz_varun, KV, KV.BAKED),
         "emberdeep": (spec_emberdeep, ED, ED.BAKED)}


class _Shim:
    """What bake_spec needs off a module: the build function it names, and a BAKED path."""

    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        make, module, baked = SPECS[k]
        spec = make()
        BD.SPECS = {k: spec}
        BD.C = _Shim(module, spec["build"], baked)
        BD.bake_spec(k, preview=(f"{pv}/{k}.png" if pv else None))
