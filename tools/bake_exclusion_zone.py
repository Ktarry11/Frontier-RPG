"""
Bake the Exclusion Zone's three floors (tools/handbuilt_exclusion_zone.py).

    PYTHONPATH=. python3 tools/bake_exclusion_zone.py [shadow] [hall] [foot] [--preview DIR]

Painted from Kyle's Exclusion Zone tile sheet (docs/deadwind_art_prompts.md sheet 6, assets/tiles/fallout_zone). The
deeper you go, the less of Deadwind is left in it and the more of the copy.

THE WHEEL'S SHADOW: gouged rock round the rim with seep-veined walls, each chamber its own ground.
  the Crater Floor    rubble, the pass's own rock
  the Brood           flesh, flesh walls
  the Stacks          Karazhan's flagstones (the archive came out of the tower), black-glass walls, violet light
  the Hanging Cars    corroded iron, grated walls
  the Open Spoke and the Axle   the seep's veins, and the seep itself round the shaft
THE REACTOR HALL: grey ash stone and plain rock, a building's colours.
  the Axle's Foot     the seep's veins, where it pours down the shaft
  the Turbine Hall    shattered concrete, the turbines and the walls in iron
  the Bubbler Pools   seep-stained rock, seep walls, the pools themselves a deep sick green
  the Ninety Seconds  scorched rock, stopped walls, the pale blue of stopped time
  the Lid             crystal and glow, glass walls
THE FOOT: corroded ground and sunken walls down the Steam Corridor, ash in the Sandfall, and the melt everywhere
  else: slag, lit from inside, with wound tissue on the Heart's island.
The seep and the melt are real collision (lava under the hood).
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_exclusion_zone as EZ

FZ = "fallout_zone/fz_"


def _r(floor, name, pad=2):
    return EZ.room_ellipses(floor, name, pad)


def spec_shadow():
    S = EZ.SHADOW
    return dict(
        build="build_shadow_baked", seed=601, slug="exclusion_zone",
        materials={"floor": M(FZ + "gouged_rock"), "crater_f": M(FZ + "rubble"), "flesh_f": M(FZ + "flesh"),
                   "stacks_f": M(FZ + "tower_flags"), "cars_f": M(FZ + "corroded"), "axle_f": M(FZ + "glow_veins"),
                   "wall": M(dim(FZ + "seep_wall", 0.7)), "flesh_w": M(dim(FZ + "flesh_wall", 0.7)),
                   "glass_w": M(dim(FZ + "glass_wall", 0.7)), "grate_w": M(dim(FZ + "iron_grate", 0.75)),
                   "lava": M(FZ + "toxic_shallow")},
        floor_keys=["floor", "crater_f", "flesh_f", "stacks_f", "cars_f", "axle_f"],
        wall_keys=["wall", "flesh_w", "glass_w", "grate_w"],
        floors={"crater_f": _r(S, "The Crater Floor", 3), "flesh_f": _r(S, "The Brood", 2),
                "stacks_f": _r(S, "The Stacks", 1), "cars_f": _r(S, "The Hanging Cars", 1),
                "axle_f": _r(S, "The Axle", 1) + _r(S, "The Open Spoke", 0)},
        walls={"flesh_w": _r(S, "The Brood", 10), "glass_w": _r(S, "The Stacks", 8),
               "grate_w": _r(S, "The Hanging Cars", 8)},
        floor_weight={"axle_f": 1.3},
        pools=[], lava=True, glow_floors=["stacks_f", "axle_f"],
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.80, 0.95, 0.45), deep_dark=0.46,
                 foam_col=(200, 230, 120), glows=[("d_lava", (150, 190, 40), 2.6, 0.7),
                                                   ("d_axle_f", (140, 200, 60), 1.8, 0.35),
                                                   ("d_stacks_f", (120, 80, 180), 1.6, 0.30)]),
    )


def spec_hall():
    H = EZ.HALL
    return dict(
        build="build_hall_baked", seed=602, slug="reactor_hall",
        materials={"floor": M(FZ + "ash_stone"), "axle_f": M(FZ + "glow_veins"), "turbine_f": M(FZ + "shattered"),
                   "pools_f": M(FZ + "seep_rock"), "roof_f": M(FZ + "scorched_rock"), "lid_f": M(FZ + "crystal_floor"),
                   "wall": M(dim(FZ + "rock_wall", 0.7)), "grate_w": M(dim(FZ + "iron_grate", 0.75)),
                   "seep_w": M(dim(FZ + "seep_wall", 0.7)), "stopped_w": M(dim(FZ + "stopped_wall", 0.75)),
                   "glass_w": M(dim(FZ + "glass_wall", 0.7)),
                   "lava": M(FZ + "toxic_deep")},
        floor_keys=["floor", "axle_f", "turbine_f", "pools_f", "roof_f", "lid_f"],
        wall_keys=["wall", "grate_w", "seep_w", "stopped_w", "glass_w"],
        floors={"axle_f": _r(H, "The Axle's Foot", 0), "turbine_f": _r(H, "The Turbine Hall", 1),
                "pools_f": _r(H, "The Bubbler Pools", 1), "roof_f": _r(H, "The Ninety Seconds", 1),
                "lid_f": _r(H, "The Lid", 0)},
        walls={"grate_w": _r(H, "The Turbine Hall", 4), "seep_w": _r(H, "The Bubbler Pools", 6),
               "stopped_w": _r(H, "The Ninety Seconds", 6), "glass_w": _r(H, "The Lid", 8)},
        floor_weight={"lid_f": 1.3, "roof_f": 1.2},
        pools=[], lava=True, glow_floors=["axle_f", "roof_f", "lid_f"],
        # LIGHT. The pools' sick green; the roof gallery the cold pale blue stopped time is everywhere in the pass;
        # the core lit green from below, the brightest room on the floor
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.80, 0.95, 0.45), deep_dark=0.50,
                 foam_col=(190, 225, 110), glows=[("d_lava", (130, 190, 40), 2.4, 0.7),
                                                   ("d_axle_f", (140, 200, 60), 1.6, 0.30),
                                                   ("d_roof_f", (120, 150, 210), 1.4, 0.22),
                                                   ("d_lid_f", (150, 220, 70), 2.2, 0.50)]),
    )


def spec_foot():
    F = EZ.FOOT
    return dict(
        build="build_foot_baked", seed=603, slug="the_foot",
        materials={"floor": M(FZ + "corroded"), "sand_f": M(FZ + "deep_ash"), "heart_f": M(FZ + "wound_tissue"),
                   "wall": M(dim(FZ + "sunk_wall", 0.7)), "slag_w": M(dim(FZ + "slag_wall", 0.7)),
                   "lava": M(dim(FZ + "slag", 0.72), dim(FZ + "ooze_pool", 0.66), 2.0)},
        floor_keys=["floor", "sand_f", "heart_f"],
        wall_keys=["wall", "slag_w"],
        floors={"sand_f": _r(F, "The Sandfall", 2), "heart_f": [(75, 84, 8, 6)]},
        walls={"slag_w": _r(F, "The Elephant's Foot", 6)},
        floor_weight={"heart_f": 1.4},
        pools=[], lava=True, glow_floors=["heart_f"],
        # LIGHT. The melt, lit from inside and brightest of anything in the pass; the Heart's island a deep red
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.95, 0.95, 0.40), deep_dark=0.44,
                 foam_col=(230, 230, 110), glows=[("d_lava", (170, 200, 50), 2.2, 0.45),
                                                   ("d_heart_f", (190, 60, 40), 2.2, 0.45)]),
    )


class _Shim:
    def __init__(self, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(EZ, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    only = [a for a in sys.argv[1:] if a in ("shadow", "hall", "foot")]
    for key, fn, floor in (("shadow", spec_shadow, EZ.SHADOW), ("hall", spec_hall, EZ.HALL),
                           ("foot", spec_foot, EZ.FOOT)):
        if only and key not in only:
            continue
        spec = fn()
        BD.SPECS = {spec["slug"]: spec}
        BD.C = _Shim(spec["build"], EZ.BAKED[floor])
        BD.bake_spec(spec["slug"], preview=(f"{pv}/{spec['slug']}.png" if pv else None))
