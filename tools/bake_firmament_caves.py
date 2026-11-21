"""
Bake the Fading Firmament's three caves: the Hearthdeep and the Wellspring (the Threefold Forge's roots, two floors) and
the Hollow Engine (inside the greatest dead engine).

    PYTHONPATH=. python3 tools/bake_firmament_caves.py [hearthdeep|wellspring|hollow_engine ...] [--preview DIR]

THE HEARTHDEEP: grey crystal ash down the stair and over the Ash Hall, the giants' quartz granite in their flue, the
cutters' forge floor in the works, the Veyr's talon stone in the singers' gallery, and the Confluence's floor of hot
metal still glowing faintly under the deep anvil. Kharad block walls, carved Veyr walls round the gallery.
THE WELLSPRING: the giants' temple floor, mosaic in the seedbeds, rune platform along the wind-ways, and crystal veins
round the Motherstone lit from inside; the Motherstone's pool in sky-water. Relief walls, carved walls on the channel.
THE HOLLOW ENGINE: engine plates, gear grating in the galleries, bronze in the works, the coolant standing dark, and
the core's floor burned black and cracked, the void's violet showing through. Gear and pipe walls.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_hearthdeep as HD, handbuilt_wellspring as WS, handbuilt_hollow_engine as HE
from tools.bake_durotar_caves import M

SK = "sky/ground/"


def _e(r, pad=1):
    return (r[0], r[1], r[2] + pad, r[3] + pad)


def hearthdeep():
    HD.build_hearthdeep_baked()
    return dict(
        build="build_hearthdeep_baked", seed=5911, slug="hearthdeep", tile_water=True,
        materials={"floor": M(SK + "ff_crystal_ash"), "granite_f": M(SK + "kh_quartz_granite"),
                   "forge_f": M(SK + "ae_forge_floor"), "talon_f": M(SK + "vy_talon_stone"),
                   "heat_f": M(SK + "ae_hot_metal"),
                   "water_s": M(SK + "sk_sky_pool"), "water_d": M(SK + "sk_sky_deep"),
                   "wall": M(SK + "kh_citadel_wall"), "veyr_w": M(SK + "vy_carved_wall")},
        floor_keys=["floor", "granite_f", "forge_f", "talon_f", "heat_f"],
        wall_keys=["wall", "veyr_w"],
        floors={"granite_f": [_e(HD.FLUE)], "forge_f": [_e(HD.WORKS)], "talon_f": [_e(HD.GALLERY)],
                "heat_f": [(HD.CONFLUENCE[0], HD.CONFLUENCE[1] - 2, 12, 6)]},
        walls={"veyr_w": [(HD.GALLERY[0], HD.GALLERY[1], HD.GALLERY[2] + 8, HD.GALLERY[3] + 8)]},
        pools=[],
        glow_floors=["heat_f"],
        cfg=dict(ao=0.48, depth=0.86, lip=20, lip_col=(0.70, 0.66, 0.62), deep_dark=0.5,
                 foam_col=(220, 200, 170),
                 glows=[("d_heat_f", (255, 150, 90), 3.0, 0.45)]),
    )


def wellspring():
    WS.build_wellspring_baked()
    return dict(
        build="build_wellspring_baked", seed=5913, slug="wellspring", tile_water=True,
        materials={"floor": M(SK + "kh_temple_floor"), "bed_f": M(SK + "kh_mineral_mosaic"),
                   "rune_f": M(SK + "vy_rune_platform"), "vein_f": M(SK + "sk_crystal_veins"),
                   "water_s": M(SK + "sk_sky_pool"), "water_d": M(SK + "sk_sky_deep"),
                   "wall": M(SK + "kh_relief_wall"), "veyr_w": M(SK + "vy_carved_wall")},
        floor_keys=["floor", "bed_f", "rune_f", "vein_f"],
        wall_keys=["wall", "veyr_w"],
        floors={"bed_f": [_e(WS.BEDS_W), _e(WS.BEDS_E)], "rune_f": [(44, 86, 20, 5), (44, 10, 5, 10)],
                "vein_f": [_e(WS.MOTHER, 0)]},
        walls={"veyr_w": [(44, 86, 26, 10)]},
        pools=[],
        glow_floors=["vein_f"],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.66, 0.74, 0.86), deep_dark=0.45,
                 foam_col=(200, 230, 255),
                 glows=[("d_vein_f", (140, 200, 255), 2.0, 0.3)]),
    )


def hollow_engine():
    HE.build_hollow_engine_baked()
    return dict(
        build="build_hollow_engine_baked", seed=5917, slug="hollow_engine", tile_water=True,
        materials={"floor": M(SK + "ae_engine_plates"), "grate_f": M(SK + "ae_gear_grating"),
                   "bronze_f": M(SK + "ae_bronze_floor"), "black_f": M(SK + "ff_void_cracks"),
                   "water_s": M(SK + "ae_coolant"), "water_d": M(SK + "ff_void"),
                   "wall": M(SK + "ae_gear_wall"), "pipe_w": M(SK + "ae_pipe_wall")},
        floor_keys=["floor", "grate_f", "bronze_f", "black_f"],
        wall_keys=["wall", "pipe_w"],
        floors={"grate_f": [_e(HE.GEARS_W), _e(HE.GEARS_E)], "bronze_f": [_e(HE.WORKS)],
                "black_f": [_e(HE.CORE)]},
        walls={"pipe_w": [(HE.COOLANT[0], HE.COOLANT[1], 20, 16), (HE.WORKS[0], HE.WORKS[1], 20, 16)]},
        pools=[],
        glow_floors=["black_f"],
        cfg=dict(ao=0.5, depth=0.88, lip=20, lip_col=(0.62, 0.66, 0.70), deep_dark=0.6,
                 foam_col=(170, 200, 210),
                 glows=[("d_black_f", (190, 120, 255), 3.0, 0.55)]),
    )


CAVES = {"hearthdeep": (hearthdeep, HD, "build_hearthdeep_baked"),
         "wellspring": (wellspring, WS, "build_wellspring_baked"),
         "hollow_engine": (hollow_engine, HE, "build_hollow_engine_baked")}


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    which = [a for a in sys.argv[1:] if a in CAVES] or list(CAVES)
    for slug in which:
        fn, mod, build = CAVES[slug]
        s = fn()
        BD.SPECS = {slug: s}
        BD.C = types.SimpleNamespace(BAKED=mod.BAKED, **{build: getattr(mod, build)})
        BD.bake_spec(slug, pv)
