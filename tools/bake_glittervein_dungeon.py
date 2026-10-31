#!/usr/bin/env python3
"""
Bake The Mother Vein and The Cistern - the two halves of the Glittervein's dungeon.

    PYTHONPATH=. python3 tools/bake_glittervein_dungeon.py [mother_vein|cistern] [--preview OUT.png]

Both are CaveLayout zones, so both go through bake_durotar_caves' SPEC pipeline rather than the
open-zone Painter.

TWO MAPS THAT SHOULD NOT LOOK ALIKE, and they share a region, a tile set and an archetype, so the
separation has to be deliberate:

  THE MOTHER VEIN still has PEOPLE in it. The dig head is goblin work - orange hardpan and wadi
  gravel, the same ground as the surface, carried down a shaft. Walk ten tiles out of it and that
  stops, and everything after is seam floor and shard gravel. The zone's whole shape is "the only
  square thing here is the bit a person cut", and the paint has to say that before the geometry
  gets a chance to.
  THE CISTERN has none. No goblin ground anywhere on it, wetter throughout, and the walls go from
  vein to crystal as the player climbs toward the heart. By the top there is nothing left down
  there that was ever anybody, and the floor should have stopped looking like anywhere a person
  would work long before that.

THE CRYSTAL IS THE LIGHT SOURCE. Neither map has a sky, a lamp or a fire in it - the only thing
lit is the seam, which is why the vugs glow and the galleries between them do not. That is also
the zone's loot and the reason the player is here, so the brightest rooms are the ones worth
walking into.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_mother_vein as MV
from tools import handbuilt_cistern as CI
from tools.bake_durotar_caves import M, dim

#: bake_spec() resolves its build function off BD.C, which is bound to the Durotar caves module.
#: Each map here lives in its own module, so C is swapped per bake - the same thing
#: tools/bake_tanaris_places.py and tools/bake_return_voyage.py do.
MODULES = {"mother_vein": MV, "cistern": CI}

UD = "underdark/materials/"
SF = "shimmering_flats/materials/"

SPECS = {}

SPECS["mother_vein"] = lambda: dict(
    build="build_mother_vein_baked", seed=781, slug="mother_vein",
    materials={
        # the seam itself: what the player walks on everywhere a goblin did not cut it
        "floor":   M(UD + "ud_seam_floor", UD + "ud_shard_gravel"),
        # THE DIG HEAD, and it is the same ground as the surface, carried down a shaft
        "dry":     M(dim(SF + "tan_hardpan_orange", 0.70), dim(SF + "tan_wadi_gravel", 0.72)),
        # the drowned gallery, below the water table
        "wet":     M(UD + "ud_wet_rock", dim(SF + "cen_limestone_wet", 0.78)),
        # the vugs - crystal-lined, and the only lit rooms on the map
        "crystal": M(dim(UD + "ud_crystal_floor_c", 0.82), dim(UD + "ud_crystal_floor_v", 0.84)),
        "water_s": M(dim(UD + "ud_pool_shallow", 0.86)),
        "water_d": M(dim(UD + "ud_pool_deep", 0.78)),
        "wall":    M(UD + "ud_vein_wall", dim(UD + "ud_rock_wall", 0.80)),
    },
    floor_keys=["floor", "dry", "wet", "crystal"],
    wall_keys=["wall"],
    floors={
        "dry":     [(50, 90, 21, 17), (28, 95, 23, 7), (70, 95, 23, 7)],
        "wet":     [(34, 76, 53, 15)],
        "crystal": [(44, 51, 21, 15), (59, 29, 19, 15), (33, 5, 27, 19)],
    },
    walls={},
    pools=[],
    glow_floors=["crystal"],
    # UNDER A DESERT, WITH NO SKY. High ao and deep shading, and a cold lip because the only light
    # in here comes out of the stone.
    cfg=dict(ao=0.46, depth=0.84, lip=26, lip_col=(0.70, 0.88, 1.06), deep_dark=0.40,
             foam_col=(165, 205, 220),
             # RADIUS 3.0 AT 0.85 LIT THE ROCK, not the room - the halo spread far enough past
             # each vug to put soft blue discs on solid stone several galleries away, which reads
             # as a lighting bug rather than as a glowing seam. A vug should light itself and a
             # few tiles of the gallery outside its mouth.
             glows=[("d_crystal", (84, 140, 210), 1.9, 0.44)]),
)

SPECS["cistern"] = lambda: dict(
    build="build_cistern_baked", seed=782, slug="cistern",
    materials={
        # NO GOBLIN GROUND ON THIS MAP. Nothing down here was ever anybody's workings.
        "floor":   M(UD + "ud_wet_rock", UD + "ud_seam_floor"),
        # the choir, where the lattice grows in exact repeating geometry
        "lattice": M(UD + "ud_lattice_floor", UD + "ud_rune_floor"),
        "crystal": M(dim(UD + "ud_crystal_floor_v", 0.84), dim(UD + "ud_geode_floor", 0.86)),
        "water_s": M(dim(UD + "ud_pool_shallow", 0.92)),
        "water_d": M(dim(UD + "ud_pool_deep", 0.84)),
        "wall":    M(UD + "ud_crystal_wall_v", UD + "ud_vein_wall"),
    },
    floor_keys=["floor", "lattice", "crystal"],
    wall_keys=["wall"],
    floors={
        "lattice": [(56, 89, 21, 15)],                      # the choir
        "crystal": [(33, 65, 23, 15), (54, 41, 21, 15)],    # the siphon works, the standing water
    },
    walls={},
    pools=[],
    glow_floors=["crystal", "lattice"],
    # DEEPER AND WETTER. Brighter lip than the Mother Vein, because by here the seam is the only
    # thing there is and it is everywhere - this is the room the whole region's water is in.
    cfg=dict(ao=0.48, depth=0.88, lip=28, lip_col=(0.74, 0.92, 1.12), deep_dark=0.42,
             foam_col=(175, 215, 230),
             glows=[("d_crystal", (96, 150, 220), 2.0, 0.48),
                    ("d_lattice", (120, 120, 225), 1.8, 0.38)]),
)


def main():
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
