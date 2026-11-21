"""
Bake The Storm-Well (tools/handbuilt_storm_well.py), the Golem Vault's second floor.

    PYTHONPATH=. python3 tools/bake_storm_well.py [--preview DIR]

Deeper and stormier than the vault above: engraved slabs in the stair and the Binding Hall, blue-and-gold broken inlay
round the Well, crystal granite in the Core Racks, the bound storm in the middle of the Well as dark storm-cloud (read
off the map's water tiles, so the dais and the bridges stay dry), and the dais where the storm runs blue through the
runes, lighting the cavern. Bronze-banded walls round the Well, the Kharad's block walls elsewhere.
"""
import sys
import types

from tools import bake_durotar_caves as BD
from tools import handbuilt_storm_well as SW
from tools.bake_durotar_caves import M

SK = "sky/ground/"


def spec():
    SW.build_storm_well_baked()
    bx, by, brx, bry = SW.BINDING
    rx, ry, rrx, rry = SW.RACKS
    dx, dy, drx, dry = SW.DAIS
    return dict(
        build="build_storm_well_baked", seed=5151, slug="storm_well", tile_water=True,
        materials={"floor": M(SK + "sk_broken_inlay"), "stone_f": M(SK + "ae_engraved_stone"),
                   "granite_f": M(SK + "kh_quartz_granite"), "bolt_f": M(SK + "ae_rune_floor"),
                   "water_s": M(SK + "sk_cloud_storm"), "water_d": M(SK + "sk_cloud_shadow"),
                   "wall": M(SK + "sk_ancient_wall"), "dark_w": M(SK + "kh_bronze_wall")},
        floor_keys=["floor", "stone_f", "granite_f", "bolt_f"],
        wall_keys=["wall", "dark_w"],
        floors={"stone_f": [(42, 8, 5, 8), (bx, by, brx, bry)],
                "granite_f": [(rx, ry, rrx + 1, rry + 1)],
                "bolt_f": [(dx, dy, drx + 2, dry + 2)]},
        walls={"dark_w": [(42, 66, 38, 33)]},
        pools=[],
        glow_floors=["bolt_f"],
        cfg=dict(ao=0.48, depth=0.88, lip=20, lip_col=(0.70, 0.72, 0.80), deep_dark=0.55,
                 foam_col=(170, 190, 255),
                 glows=[("d_bolt_f", (150, 170, 255), 3.0, 0.75)]),
    )


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    s = spec()
    BD.SPECS = {"storm_well": s}
    BD.C = types.SimpleNamespace(BAKED=SW.BAKED, build_storm_well_baked=SW.build_storm_well_baked)
    BD.bake_spec("storm_well", pv)
