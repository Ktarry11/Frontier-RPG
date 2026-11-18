"""
Bake the Rotroot Deeps' floor and walls (tools/handbuilt_rotroot_deeps.py).

    PYTHONPATH=. python3 tools/bake_rotroot_deeps.py [--preview DIR]

Painted from Kyle's Azshara ground sheet, worse the deeper it goes:
  THE BURIAL HALLS      the Timbermaw's mossy flagstones (they built this part)
  THE SPOREGARDEN       fel-rot soil and fungus
  THE WARDEN'S GAUNTLET the satyrs' cursed violet soil
  THE ROOT CATHEDRAL    fel-rot soil on the root knots and bridges
  THE GLOOMHOLLOW       scorched black earth where the rot started
and dark loam on the passages between; grey lichen rock for the walls, darker as you go down.
THE OOZE is real collision (lava tiles under the hood) painted as the Felwood's fel pool water, with a sick
green glow off it so the lakes light the rooms they fill.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_rotroot_deeps as RD

AZ = "azshara/ground/az_"


def _room(name, pad=2):
    spec = RD.ROOMS[name]
    if spec[0] == "rect":
        _k, x0, y0, x1, y1, _c = spec
        return [((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad)]
    return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in spec[1]]


def spec_rotroot():
    return dict(
        build="build_rotroot_baked", seed=571, slug="rotroot_deeps",
        materials={"floor": M(dim(AZ + "loam", 0.7)), "flag_f": M(AZ + "mossy_flag"),
                   "rot_f": M(AZ + "felrot_soil"), "shroom_f": M(AZ + "moss_shroom"),
                   "curse_f": M(AZ + "cursed_soil"), "scorch_f": M(AZ + "scorched"),
                   "wall": M(dim(AZ + "lichen_stone", 0.55)), "deep_w": M(dim(AZ + "rock_hill", 0.5)),
                   "lava": M("ashenvale/materials/av_fel_pool_water")},
        floor_keys=["floor", "flag_f", "rot_f", "shroom_f", "curse_f", "scorch_f"],
        wall_keys=["wall", "deep_w"],
        floors={"flag_f": _room("The Burial Halls", 6),
                "shroom_f": _room("The Sporegarden", 0) + [(66, 108, 4, 30)],
                "rot_f": _room("The Root Cathedral"),
                "curse_f": _room("The Warden's Gauntlet", 6),
                "scorch_f": _room("The Gloomhollow")},
        walls={"deep_w": [(110, 140, 80, 30)]},
        pools=[], lava=True,
        cfg=dict(ao=0.50, depth=0.90, lip=18, lip_col=(0.70, 0.85, 0.55), deep_dark=0.46,
                 foam_col=(200, 210, 190), glows=[("d_lava", (70, 150, 30), 2.4, 0.7)]),
    )


class _Shim:
    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    spec = spec_rotroot()
    BD.SPECS = {"rotroot_deeps": spec}
    BD.C = _Shim(RD, spec["build"], RD.BAKED)
    BD.bake_spec("rotroot_deeps", preview=(f"{pv}/rotroot_deeps.png" if pv else None))
