"""
Bake Azshara's two caves (tools/handbuilt_azshara_caves.py).

    PYTHONPATH=. python3 tools/bake_azshara_caves.py [haldarr_den hetaeras_grotto] [--preview DIR]

Painted from Kyle's Azshara ground sheet where it has the right ground, and the grotto set where it doesn't:

  HALDARR DEN       cursed violet soil up the taproot, fel-rot soil out in the pockets where the Highborne are bound,
                    scorched earth round Haldarr's fires in the hollow; grey lichen rock for the walls
  HETAERA'S GROTTO  shell silt and kelp along the spiral, the sea standing in every chamber (tide pools over deep
                    water), the drowned Highborne mosaic in the hall at the core; coral and wet sea-cave walls
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_azshara_caves as AC
from tools.bake_durotar_caves import M, dim

AZ = "azshara/ground/az_"
CS = "caves/seamless/"


def _room(cave, rname, pad=0):
    x, y, w, h = AC.ROOM_NAMES[cave][rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec_den():
    c = AC.DEN
    AC.build(c)
    pockets = [(tip[0], tip[1], 6, 5) for (_s, _l, forks) in AC.SIDE_ROOTS for tip in forks]
    return dict(
        build="build_den_baked", seed=541, slug="haldarr_den",
        materials={"floor": M(AZ + "cursed_soil"), "fel_f": M(AZ + "felrot_soil"), "scorch_f": M(AZ + "scorched"),
                   "wall": M(dim(AZ + "lichen_stone", 0.55)), "root_w": M(dim(AZ + "rock_hill", 0.5))},
        floor_keys=["floor", "fel_f", "scorch_f"],
        wall_keys=["wall", "root_w"],
        floors={"fel_f": pockets, "scorch_f": [_room(c, "Haldarr's Hollow", 1)]},
        walls={"root_w": [(48, 60, 16, 40)]},
        pools=[],
        cfg=dict(ao=0.50, depth=0.90, lip=20, lip_col=(0.80, 0.70, 0.90), deep_dark=0.45,
                 foam_col=(200, 210, 200), glows=[]),
    )


def spec_grotto():
    c = AC.GROTTO
    AC.build(c)
    return dict(
        build="build_grotto_baked", seed=547, slug="hetaeras_grotto",
        materials={"floor": M(AZ + "shell_silt"), "kelp_f": M(CS + "gro_kelp_floor_a"),
                   "hall_f": M(AZ + "drowned_mosaic"), "marble_f": M(AZ + "wet_marble"),
                   "water_s": M(CS + "gro_tidepool_a"), "water_d": M(CS + "gro_deep_floor_a"),
                   "wall": M(CS + "gro_cave_wall_a"), "coral_w": M(CS + "gro_coral_wall_a")},
        floor_keys=["floor", "kelp_f", "hall_f", "marble_f"],
        wall_keys=["wall", "coral_w"],
        floors={"hall_f": [_room(c, "The Drowned Hall", -2)],
                "marble_f": [_room(c, "The Drowned Hall", 2)],
                "kelp_f": [_room(c, "The Sea Mouth"), _room(c, "Hetaera's Pool")]},
        walls={"coral_w": [_room(c, "The Drowned Hall", 6), _room(c, "Hetaera's Pool", 4)]},
        pools=[AC.POOLS[c]],
        cfg=dict(ao=0.42, depth=0.84, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
                 foam_col=(205, 238, 245), glows=[]),
    )


SPECS = {"haldarr_den": (AC.DEN, spec_den), "hetaeras_grotto": (AC.GROTTO, spec_grotto)}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        cave, fn = SPECS[k]
        spec = fn()
        BD.SPECS = {k: spec}
        BD.C = types.SimpleNamespace(BAKED=AC.BAKED[cave], **{spec["build"]: getattr(AC, spec["build"])})
        BD.bake_spec(k, pv)
