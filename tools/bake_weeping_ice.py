"""
Bake The Weeping Ice.

    PYTHONPATH=. python3 tools/bake_weeping_ice.py [--preview DIR]

Reuses the Underdark's ice family (ud_ice_floor, ud_ice_cracked, ud_frost_rock, ud_snow_pack, ud_ice_wall,
ud_frost_wall) rather than generating a new sheet. The Frostward Descent already paints its glacier band
from exactly these, they are the only ice tiles in the game, and this cave is ice. Nothing here needed new
art.

THE MAP IS PAINTED AS A THAW GRADIENT, and that gradient is the cave's whole story.

The player enters at the MOULIN, at the bottom of the image (y~126) - the shaft where meltwater pours in
from the snowfield. That is the warm end: daylight reaches it, it is wet, and the ice there has mostly
gone, so the floor is wet rock with the glacier's stone bed showing through. Every step further in (toward
LOW y) is colder and less melted, until THE SINK at the top of the image, which is still properly frozen
and is the only part of this cave that looks like the glacier it used to be.

So the bands run bottom-to-top: wet rock -> frost rock -> cracked ice -> solid ice. A player walking in
can SEE that they are walking into the last cold part of a dying thing, which is also why the yetis are
cornered down there and why the bears stay nearer the door.

Bands are wide shallow ellipses, not rectangles, so the boundaries wander instead of ruling lines across
the map - same reason the Frostward Descent does it, and the same reason it works: a player who crosses a
straight edge notices the edge.

AO is 0.44 / depth 0.80 - darker than the Underdark's 0.36/0.70, because unlike the Crystalline Underdark
this cave is NOT lit from within. Ice is not a light source. It wants to read as a cave.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_weeping_ice as WI
from tools.bake_durotar_caves import M

UD = "underdark/materials/"


def spec_weeping_ice():
    return dict(
        build="build_weeping_ice_baked", seed=617, slug="weeping_ice",
        materials={
            # base: frost rock. Everything else is painted over it.
            "frost":   M(UD + "ud_frost_rock", UD + "ud_snow_pack"),
            "wet":     M(UD + "ud_wet_rock", UD + "ud_cavern_dark"),
            "cracked": M(UD + "ud_ice_cracked", UD + "ud_frost_rock"),
            "ice":     M(UD + "ud_ice_floor", UD + "ud_ice_cracked"),
            "rock_w":  M(UD + "ud_rock_wall"),
            "frost_w": M(UD + "ud_frost_wall"),
            "ice_w":   M(UD + "ud_ice_wall", UD + "ud_frost_wall"),
        },
        floor_keys=["frost", "wet", "cracked", "ice"],
        wall_keys=["rock_w", "frost_w", "ice_w"],
        floors={
            # (cx, cy, rx, ry) - the thaw gradient, warm end (high y) to frozen end (low y)
            "wet":     [(48, 124, 40, 16), (48, 104, 34, 12)],
            "cracked": [(48, 70, 44, 20), (28, 44, 20, 12), (68, 44, 20, 12)],
            "ice":     [(48, 16, 32, 16), (48, 28, 26, 10)],
        },
        walls={
            "frost_w": [(48, 86, 48, 30)],
            "ice_w":   [(48, 22, 40, 22)],
        },
        # THE CISTERN is standing meltwater that never drains fast enough - the one pool in the cave, and
        # the reason the lower braid is tighter than the upper one.
        pools=[WI.WI_POOLS],
        cfg=dict(ao=0.44, depth=0.80, lip=14, lip_col=(0.78, 0.86, 0.96), deep_dark=0.46,
                 foam_col=(200, 222, 238), glows=[]),
    )


MODULES = {"weeping_ice": WI}
SPECS = {"weeping_ice": spec_weeping_ice}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
