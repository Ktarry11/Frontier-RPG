"""
Bake Jaedenar's floor and walls.

    PYTHONPATH=. python3 tools/bake_jaedenar.py [--preview DIR]

NO NEW TEXTURES, the rule tools/bake_tempest_dungeons.py set: the shared interior library has what
this needs. The PAIRING says what each half is:

  The Shadow Hold    keep flagstones and dressed keep wall, lifted a little so the halls read:
                     the masonry the Council took over. Ritual floor in the Black Library, the Shadow Chapel and the Sanctum, the three
                     rooms they use for their work.
  The Summoning Pit  cult floor and black basalt wall: rock they cut into, scorched by what came
                     through it, with ash in the pit itself and on the throne's floor.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_jaedenar as JD

_L = "durotar_caves/materials/"
_SP = "silverpine/materials/"


def _rect(key, pad=2):
    x0, y0, x1, y1, _c, _n = JD.ROOMS[key]
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0 + pad, (y1 - y0) / 2.0 + pad)


def _cav(key, pad=3):
    cx, cy, rx, ry, _r, _p, _n = JD.CAVERNS[key]
    return (cx, cy, rx + pad, ry + pad)


def spec_jaedenar():
    return dict(
        build="build_jaedenar_baked", seed=553, slug="jaedenar", wall_tile="rock",
        materials={"floor": M(dim(_SP + "sp_keep_floor", 1.15)), "ritual_f": M(dim(_SP + "sp_ritual_floor", 1.0)),
                   "cult_f": M(_L + "rf_cult_floor_a_dim85"), "ash_f": M(_L + "rf_ash_floor_a_dim80"),
                   "wall": M(dim(_SP + "sp_keep_wall", 0.9)), "basalt_w": M(_L + "rf_basalt_wall_a_dim80")},
        floor_keys=["floor", "ritual_f", "cult_f", "ash_f"], wall_keys=["wall", "basalt_w"],
        floors={"ritual_f": [_rect("library"), _rect("chapel"), _rect("sanctum")],
                # the whole carved north half, rims and tunnels included
                "cult_f": [(80, 38, 110, 42)],
                "ash_f": [_cav("pit", 1), _cav("throne", 1)]},
        walls={"basalt_w": [(80, 38, 110, 42)]},            # the whole north half is carved rock
        pools=[],
        # Fel-lit: a green cast on the lips, the dark kept deep.
        cfg=dict(ao=0.40, depth=0.88, lip=16, lip_col=(0.52, 0.78, 0.36), deep_dark=0.40,
                 foam_col=(150, 200, 120), glows=[]),
    )


class _Shim:
    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    spec = spec_jaedenar()
    BD.SPECS = {"jaedenar": spec}
    BD.C = _Shim(JD, spec["build"], JD.BAKED)
    BD.bake_spec("jaedenar", preview=(f"{pv}/jaedenar.png" if pv else None))
