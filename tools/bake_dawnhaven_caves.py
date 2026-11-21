"""
Bake Dawnhaven's four caves (tools/handbuilt_dawnhaven_caves.py).

    PYTHONPATH=. python3 tools/bake_dawnhaven_caves.py [brinecoil_grotto quiet_vault saltspine_hollow lightwell_deep]
                                                       [--preview DIR]

Painted from Kyle's Azshara ground sheet and the grotto set (docs/dawnhaven_brief.md: "Existing art now, sheets later"):

  BRINECOIL GROTTO    shell silt on the banks and kelp on the west shelf, the inlet's tide pools over deep water,
                      worn mosaic at the tide altar; wet sea-cave and coral walls
  THE QUIET VAULT     old Highborne paving down the nave and round the cloister, mossy flags in the burial niches,
                      marble in the warden's tomb; grey lichen stone walls
  SALTSPINE HOLLOW    shell silt and kelp down the terraces, the sea standing deeper in each, the naga's temple floor
                      round the throne pool; coral and sea-cave walls
  THE LIGHTWELL DEEP  the elven masons' terrace marble through the works, violet tile in the archive, arcane glass in
                      the font chamber with the root's arcane water; carved temple walls
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_dawnhaven_caves as DC
from tools.bake_durotar_caves import M, dim

AZ = "azshara/ground/az_"
CS = "caves/seamless/"


def _room(cave, rname, pad=0):
    x, y, w, h = DC.ROOM_NAMES[cave][rname]
    return (x + w // 2, y + h // 2, w // 2 + pad, h // 2 + pad)


def spec_grotto():
    c = DC.GROTTO
    DC.build(c)
    return dict(
        build="build_grotto_baked", seed=611, slug="brinecoil_grotto",
        materials={"floor": M(AZ + "shell_silt"), "kelp_f": M(AZ + "kelp_floor"), "altar_f": M(AZ + "drowned_mosaic"),
                   "water_s": M(CS + "gro_tidepool_a"), "water_d": M(CS + "gro_deep_floor_a"),
                   "wall": M(CS + "gro_cave_wall_a"), "coral_w": M(CS + "gro_coral_wall_a")},
        floor_keys=["floor", "kelp_f", "altar_f"],
        wall_keys=["wall", "coral_w"],
        floors={"kelp_f": [_room(c, "The Kelp Shelf")], "altar_f": [_room(c, "The Tide Altar", -2)]},
        walls={"coral_w": [_room(c, "The Tide Altar", 6), _room(c, "The Tide Mouth", 4)]},
        pools=[DC.POOLS[c]],
        cfg=dict(ao=0.42, depth=0.84, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
                 foam_col=(205, 238, 245), glows=[]),
    )


def spec_vault():
    c = DC.VAULT
    DC.build(c)
    return dict(
        build="build_vault_baked", seed=613, slug="quiet_vault",
        materials={"floor": M(AZ + "highborne_paving"), "niche_f": M(AZ + "mossy_flag"),
                   "tomb_f": M(AZ + "marble_terrace"), "bone_f": M(dim(AZ + "paving_leaves", 0.7)),
                   "wall": M(dim(AZ + "lichen_stone", 0.55)), "tomb_w": M(CS + "gro_temple_wall_a")},
        floor_keys=["floor", "niche_f", "tomb_f", "bone_f"],
        wall_keys=["wall", "tomb_w"],
        floors={"niche_f": [_room(c, "The West Niches"), _room(c, "The East Niches")],
                "tomb_f": [_room(c, "The Warden's Tomb", -1)], "bone_f": [_room(c, "The Ossuary")]},
        walls={"tomb_w": [_room(c, "The Warden's Tomb", 6)]},
        pools=[],
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.85, 0.80, 0.70), deep_dark=0.45,
                 foam_col=(200, 210, 200), glows=[]),
    )


def spec_hollow():
    c = DC.HOLLOW
    DC.build(c)
    return dict(
        build="build_hollow_baked", seed=617, slug="saltspine_hollow",
        materials={"floor": M(AZ + "shell_silt"), "kelp_f": M(CS + "gro_kelp_floor_a"),
                   "throne_f": M(CS + "gro_temple_floor_a"), "pearl_f": M(CS + "gro_pearl_floor_a"),
                   "water_s": M(CS + "gro_tidepool_a"), "water_d": M(CS + "gro_deep_floor_a"),
                   "wall": M(CS + "gro_cave_wall_a"), "coral_w": M(CS + "gro_coral_wall_a")},
        floor_keys=["floor", "kelp_f", "throne_f", "pearl_f"],
        wall_keys=["wall", "coral_w"],
        floors={"throne_f": [_room(c, "The Throne Pool", -1)], "kelp_f": [_room(c, "The Second Terrace")],
                "pearl_f": [_room(c, "Saltspine's Pool")]},
        walls={"coral_w": [_room(c, "The Throne Pool", 6), _room(c, "Saltspine's Pool", 4)]},
        pools=[DC.POOLS[c]],
        cfg=dict(ao=0.42, depth=0.84, lip=20, lip_col=(0.6, 0.9, 1.0), deep_dark=0.5,
                 foam_col=(205, 238, 245), glows=[]),
    )


def spec_deep():
    c = DC.DEEP
    DC.build(c)
    return dict(
        build="build_deep_baked", seed=619, slug="lightwell_deep",
        materials={"floor": M(AZ + "marble_terrace"), "archive_f": M(AZ + "violet_tile"),
                   "font_f": M(AZ + "crystal_glass"), "conduit_f": M(AZ + "highborne_paving"),
                   "water_s": M(AZ + "arcane_water"), "water_d": M(dim(AZ + "arcane_water", 0.6)),
                   "wall": M(CS + "gro_temple_wall_a"), "font_w": M(CS + "bfd_temple_wall_a")},
        floor_keys=["floor", "archive_f", "font_f", "conduit_f"],
        wall_keys=["wall", "font_w"],
        floors={"archive_f": [_room(c, "The Archive"), _room(c, "The Sealed Vault")],
                "font_f": [_room(c, "The Font", -2)], "conduit_f": [_room(c, "The Conduit Hall")]},
        walls={"font_w": [_room(c, "The Font", 6)]},
        pools=[DC.POOLS[c]],
        cfg=dict(ao=0.40, depth=0.80, lip=18, lip_col=(0.85, 0.75, 1.0), deep_dark=0.4,
                 foam_col=(220, 200, 250), glows=[]),
    )


SPECS = {"brinecoil_grotto": (DC.GROTTO, spec_grotto), "quiet_vault": (DC.VAULT, spec_vault),
         "saltspine_hollow": (DC.HOLLOW, spec_hollow), "lightwell_deep": (DC.DEEP, spec_deep)}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        cave, fn = SPECS[k]
        spec = fn()
        BD.SPECS = {k: spec}
        BD.C = types.SimpleNamespace(BAKED=DC.BAKED[cave], **{spec["build"]: getattr(DC, spec["build"])})
        BD.bake_spec(k, pv)
