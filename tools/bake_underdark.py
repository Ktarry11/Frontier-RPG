"""
Bake the Crystalline Underdark cluster.

    PYTHONPATH=. python3 tools/bake_underdark.py [frostward_descent ...] [--preview DIR]

Currently holds the Frostward Descent; the Underdark itself, the Hollow Geode and the Deep Bloom land here too.

LIGHT IS THE WHOLE POINT, AND THE BAKER FIGHTS IT BY DEFAULT. Every other cave in the game is dark, so the shared
cave baker leans hard on ambient occlusion and depth-darkening - Hillsbrad's three interiors run ao 0.48-0.52 and
depth 0.86. Run that over the Underdark's tiles and the crystal, which is painted GLOWING FROM INSIDE, comes out
as grey rock near every wall. So this spec runs ao 0.36 and depth 0.70: enough to keep the warren's chambers
reading as chambers, not enough to put out the lights.

The ice end still wants a little more darkness than the crystal end, which one global cfg cannot express. It is
handled in the materials instead - the ice band paints ud_ice_floor and ud_frost_rock, which are themselves
lit art, and the shading difference between the bands comes from the textures rather than the post-process.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_frostward_descent as FD
from tools import handbuilt_hollow_geode as HG
from tools.bake_durotar_caves import M

UD = "underdark/materials/"


def spec_frostward_descent():
    """Three bands across one map: glacier ice, the wet black seam, then arcane crystal.

    The bands are painted as very wide, shallow ellipses rather than hard rectangles, so the boundary between
    them wanders instead of ruling a line across the map. That wander is the entire reason the transition works
    - a player crossing a straight edge notices the edge, and the point of this map is that they do not.
    """
    return dict(
        build="build_frostward_descent_baked", seed=811, slug="frostward_descent",
        materials={
            # base: the seam. Everything else is painted over it.
            "rock":      M(UD + "ud_wet_rock", UD + "ud_cavern_dark"),
            "ice":       M(UD + "ud_ice_floor", UD + "ud_ice_cracked"),
            "frost":     M(UD + "ud_frost_rock", UD + "ud_snow_pack"),
            "crystal":   M(UD + "ud_crystal_floor_v", UD + "ud_crystal_floor_c"),
            "lattice":   M(UD + "ud_lattice_floor"),
            "seamfloor": M(UD + "ud_seam_floor"),
            "rock_w":    M(UD + "ud_rock_wall"),
            "ice_w":     M(UD + "ud_ice_wall", UD + "ud_frost_wall"),
            "vein_w":    M(UD + "ud_vein_wall"),
            "crystal_w": M(UD + "ud_crystal_wall_v", UD + "ud_crystal_wall_c"),
        },
        floor_keys=["rock", "ice", "frost", "crystal", "lattice", "seamfloor"],
        wall_keys=["rock_w", "ice_w", "vein_w", "crystal_w"],
        floors={
            "ice":       [(60, 128, 56, 16), (36, 114, 24, 12)],
            "frost":     [(60, 110, 58, 14), (86, 112, 20, 10)],
            "seamfloor": [(60, 86, 58, 14)],
            "crystal":   [(60, 32, 58, 24), (56, 44, 22, 12)],
            "lattice":   [(56, 44, 14, 8), (58, 17, 12, 7)],
        },
        walls={
            "ice_w":     [(60, 124, 60, 22), (36, 112, 26, 14)],
            "vein_w":    [(60, 80, 60, 24)],
            "crystal_w": [(60, 30, 60, 26)],
        },
        pools=[],
        # See the module docstring: this cave is LIT, so the ambient occlusion that makes every other cave in
        # the game read as underground would here just switch the crystal off.
        cfg=dict(ao=0.36, depth=0.70, lip=16, lip_col=(0.72, 0.78, 0.95), deep_dark=0.40,
                 foam_col=(190, 215, 235), glows=[]),
    )


def spec_hollow_geode():
    """All crystal, and the walls are the point. A geode's shell is lined with inward-pointing druse, so the
    WALL materials carry more of this map's identity than the floor does - which is the opposite of every
    other interior, where the floor is what the player reads and the wall is background."""
    return dict(
        build="build_hollow_geode_baked", seed=1187, slug="hollow_geode",
        materials={
            "floor":    M(UD + "ud_geode_floor", UD + "ud_geode_rubble"),
            "core":     M(UD + "ud_geode_core"),
            "crystal":  M(UD + "ud_crystal_floor_v", UD + "ud_crystal_floor_c"),
            "lattice":  M(UD + "ud_lattice_floor"),
            "wall":     M(UD + "ud_geode_wall"),
            "crys_w":   M(UD + "ud_crystal_wall_v", UD + "ud_crystal_wall_c"),
        },
        floor_keys=["floor", "core", "crystal", "lattice"],
        wall_keys=["wall", "crys_w"],
        floors={
            "core":    [(55, 54, 14, 12)],
            "crystal": [(55, 30, 15, 9), (80, 54, 9, 13), (55, 76, 15, 9), (30, 54, 9, 13)],
            "lattice": [(55, 54, 7, 6)],
        },
        walls={"crys_w": [(55, 54, 46, 46)]},
        pools=[],
        # Brighter even than the Descent's lower chambers: a geode is lined with the stuff, and the light
        # here has nowhere to go but back at you.
        cfg=dict(ao=0.30, depth=0.62, lip=14, lip_col=(0.80, 0.82, 1.0), deep_dark=0.35,
                 foam_col=(200, 220, 240), glows=[]),
    )


MODULES = {"frostward_descent": FD, "hollow_geode": HG}
SPECS = {"frostward_descent": spec_frostward_descent, "hollow_geode": spec_hollow_geode}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
