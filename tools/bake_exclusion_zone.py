"""
Bake the Exclusion Zone's floor and walls (tools/handbuilt_exclusion_zone.py).

    PYTHONPATH=. python3 tools/bake_exclusion_zone.py [--preview DIR]

Painted from Kyle's Exclusion Zone tile sheet (docs/deadwind_art_prompts.md sheet 6, assets/tiles/fallout_zone), each
chamber its own ground, Deadwind rock giving way to the wound as you go round:
  THE CRATER FLOOR   rubble and gravel, the pass's own rock
  THE BROOD          flesh and root-flesh, flesh walls
  THE BUBBLER POOLS  slag and ooze-stained stone, slag walls
  THE STACKS         Karazhan's flagstones (the archive came out of the tower), black-glass walls
  THE NINETY SECONDS shattered stone, stopped walls
  THE ELEPHANT'S FOOT wound tissue, wound walls
and gouged rock round the rim and down the dead spokes, with seep-veined walls. THE SEEP is real collision (lava under
the hood) painted as the sheet's toxic water, with a sick yellow-green glow off it.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_exclusion_zone as EZ

FZ = "fallout_zone/fz_"


def _room(name, pad=2):
    spec = EZ.ROOMS[name]
    if spec[0] == "rect":
        _k, x0, y0, x1, y1, _c = spec
        return [((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad)]
    return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in spec[1]]


def spec_exclusion():
    return dict(
        build="build_exclusion_baked", seed=601, slug="exclusion_zone",
        materials={"floor": M(FZ + "gouged_rock"), "crater_f": M(FZ + "rubble"), "flesh_f": M(FZ + "flesh"),
                   "slag_f": M(FZ + "slag"), "stacks_f": M(FZ + "tower_flags"), "stopped_f": M(FZ + "shattered"),
                   "heart_f": M(FZ + "wound_tissue"),
                   "wall": M(dim(FZ + "seep_wall", 0.7)), "flesh_w": M(dim(FZ + "flesh_wall", 0.7)),
                   "slag_w": M(dim(FZ + "slag_wall", 0.7)), "glass_w": M(dim(FZ + "glass_wall", 0.7)),
                   "stopped_w": M(dim(FZ + "stopped_wall", 0.75)), "wound_w": M(dim(FZ + "wound_wall", 0.7)),
                   "lava": M(FZ + "toxic_shallow")},
        floor_keys=["floor", "crater_f", "flesh_f", "slag_f", "stacks_f", "stopped_f", "heart_f"],
        wall_keys=["wall", "flesh_w", "slag_w", "glass_w", "stopped_w", "wound_w"],
        floors={"crater_f": _room("The Crater Floor", 3), "flesh_f": _room("The Brood", 2),
                "slag_f": _room("The Bubbler Pools", 2), "stacks_f": _room("The Stacks", 1),
                "stopped_f": _room("The Ninety Seconds", 1), "heart_f": _room("The Elephant's Foot", 0)},
        walls={"flesh_w": _room("The Brood", 10), "slag_w": _room("The Bubbler Pools", 8),
               "glass_w": _room("The Stacks", 8), "stopped_w": _room("The Ninety Seconds", 6),
               "wound_w": _room("The Elephant's Foot", 10)},
        floor_weight={"stopped_f": 1.4, "heart_f": 1.3},
        pools=[], lava=True, glow_floors=["heart_f", "stopped_f", "stacks_f"],
        # LIGHT. The seep's sick green off every pool; the Foot a deep red, like something still hot; the Ninety
        # Seconds a cold pale blue, the colour stopped time is everywhere in the pass; the Stacks a dim violet,
        # Karazhan's own light
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.80, 0.95, 0.45), deep_dark=0.46,
                 foam_col=(200, 230, 120), glows=[("d_lava", (150, 190, 40), 2.6, 0.7),
                                                   ("d_heart_f", (190, 60, 40), 2.2, 0.45),
                                                   ("d_stopped_f", (120, 150, 210), 1.6, 0.35),
                                                   ("d_stacks_f", (120, 80, 180), 1.6, 0.30)]),
    )


class _Shim:
    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    spec = spec_exclusion()
    BD.SPECS = {"exclusion_zone": spec}
    BD.C = _Shim(EZ, spec["build"], EZ.BAKED)
    BD.bake_spec("exclusion_zone", preview=(f"{pv}/exclusion_zone.png" if pv else None))
