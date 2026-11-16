"""
Bake Stonetalon's caves (docs/stonetalon_brief.md).

    PYTHONPATH=. python3 tools/bake_stonetalon_caves.py [windshear_mine ...] [--preview DIR]

Windshear Mine: the Venture Co.'s quarried rock (Boulder Lode Mine's materials, the same company's digging) for the
drift and the ring, and at the Breakthrough the chimney's floor: grey ash blown down from the Blowdown on talus.
Kyle's Stonetalon tile sheet (basalt, ash, pumice) replaces the ash and talus when it lands.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_windshear_mine as WM
from tools import handbuilt_ashvent as AV
from tools import handbuilt_eldest_sequoia as ES
from tools.bake_durotar_caves import M
from tools.bake_nb_caves import make_seamless


def spec_windshear():
    f = make_seamless("boulder_lode_mine", "floor")
    w = make_seamless("boulder_lode_mine", "wall")
    vx, vy = WM.ROOMS["breach"][:2]
    return dict(
        build="build_windshear_mine_baked", seed=331, slug="windshear_mine",
        materials={"floor": M(f), "ash_f": M("aspen/materials/asp_ash_patch"), "wall": M(w),
                   "talus_w": M("aspen/materials/asp_talus")},
        floor_keys=["floor", "ash_f"],
        wall_keys=["wall", "talus_w"],
        floors={"ash_f": [(vx, vy, 20, 11)]},
        walls={"talus_w": [(vx, vy, 26, 14)]},
        pools=[],
        cfg=dict(ao=0.48, depth=0.84, lip=20, lip_col=(0.80, 0.66, 0.50), deep_dark=0.4,
                 foam_col=(200, 200, 210), glows=[]),
    )


def spec_ashvent():
    """The Ashvent: black basalt tube walls and floor (Kyle's Stonetalon tiles), the Skylight's floor grey with ash
    that fell through the roof, and at the Crust, steaming ground and glossy obsidian walls."""
    R = AV.ROOMS
    sx, sy = R["skylight"][:2]
    cx, cy = R["crust"][:2]
    mx, my = R["mother"][:2]
    return dict(
        build="build_ashvent_baked", seed=337, slug="ashvent",
        materials={"floor": M("stonetalon/materials/st_basalt"), "ash_f": M("stonetalon/materials/st_ash_plain"),
                   "steam_f": M("stonetalon/materials/st_steaming_ground"),
                   "wall": M("stonetalon/materials/st_basalt_cliff"),
                   "obsidian_w": M("stonetalon/materials/st_obsidian")},
        floor_keys=["floor", "ash_f", "steam_f"],
        wall_keys=["wall", "obsidian_w"],
        floors={"ash_f": [(sx, sy, 11, 9), (mx, my, 9, 7)], "steam_f": [(cx, cy, 19, 11)]},
        walls={"obsidian_w": [(cx, cy, 24, 14)]},
        pools=[],
        # the Crust still glows: the heat at the bottom of the tube, and the only warm light in it
        glow_floors=["steam_f"],
        cfg=dict(ao=0.50, depth=0.86, lip=18, lip_col=(0.90, 0.48, 0.24), deep_dark=0.45,
                 foam_col=(220, 140, 90), glows=[("d_steam_f", (170, 70, 20), 2.4, 0.7)]),
    )


def spec_trunk():
    """The Eldest Sequoia, inside the trunk: red-gold heartwood underfoot with its growth rings, growth-ring walls,
    bark-beetle galleries bored through the west, and the Sap Well's amber, glowing where the light catches it."""
    C = ES.T_CAVERNS
    gal = [(C[k][0], C[k][1], C[k][2] + 4, C[k][3] + 4) for k in ("gal_a", "gal_b", "gal_c", "queen")]
    sx, sy = C["sapwell"][:2]
    return dict(
        build="build_trunk_baked", seed=341, slug="trunk",
        materials={"floor": M("stonetalon/materials/st_heartwood_floor"),
                   "beetle_f": M("stonetalon/materials/st_beetle_galleries"),
                   "sap_f": M("stonetalon/materials/st_sap_pool"),
                   "wall": M("stonetalon/materials/st_ring_wall"),
                   "bark_w": M("stonetalon/materials/st_inner_bark_wall")},
        floor_keys=["floor", "beetle_f", "sap_f"],
        wall_keys=["wall", "bark_w"],
        floors={"beetle_f": gal, "sap_f": [(sx, sy, 10, 7)]},
        walls={"bark_w": gal + [(50, 112, 16, 10)]},
        pools=[],
        glow_floors=["sap_f"],
        cfg=dict(ao=0.42, depth=0.86, lip=16, lip_col=(0.92, 0.66, 0.40), deep_dark=0.35,
                 foam_col=(230, 170, 90), glows=[("d_sap_f", (190, 120, 30), 2.2, 0.55)]),
    )


# THE CROWN is not a cave: no walls, open air off every branch (Kyle, 15 Nov 2026). It has its own baker,
# tools/bake_eldest_crown.py; "crown" here just hands over to it.


MODULES = {"windshear_mine": WM, "ashvent": AV, "trunk": ES}
SPECS = {"windshear_mine": spec_windshear, "ashvent": spec_ashvent, "trunk": spec_trunk}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    if "crown" in sys.argv[1:] or not [a for a in sys.argv[1:] if a in SPECS]:
        from tools.bake_eldest_crown import bake as bake_crown
        bake_crown()
        keys = [a for a in sys.argv[1:] if a in SPECS] or ([] if "crown" in sys.argv[1:] else list(SPECS))
    BD.SPECS = {k: SPECS[k]() for k in keys}
    import types
    for k in keys:
        mod = MODULES[k]
        if mod is ES:
            # the dungeon module keeps both maps' baked folders in one dict; the cave baker wants a string
            mod = types.SimpleNamespace(BAKED=ES.BAKED[k], build_trunk_baked=ES.build_trunk_baked)
        BD.C = mod
        BD.bake_spec(k, pv)
