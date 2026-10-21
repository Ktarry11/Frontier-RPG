"""
Bake Razorfen Kraul painting (thorn-tunnel floors, boar-pen dirt, bone-strewn ritual ground; bramble / packed earth /
beast-pit walls).

    PYTHONPATH=. python3 tools/bake_razorfen.py [--preview DIR]

The five rfk_* textures in assets/tiles/razorfen_kraul/ are tall (~240x617) and NOT seamless, so the first run makes
256px seamless copies in assets/tiles/razorfen_kraul/materials/ and the Durotar cave baker paints from those.
"""
import sys

import numpy as np
from PIL import Image

from tools import bake_durotar_caves as BD
from tools import handbuilt_razorfen as RZ
from tools.bake_durotar_caves import M, TEX, dim, VC

SRC = TEX / "razorfen_kraul"
MAT = SRC / "materials"
SIZE = 256


def make_seamless(name, offset=0.5):
    out = MAT / f"{name}.png"
    if out.exists():
        return f"razorfen_kraul/materials/{name}"
    MAT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC / f"{name}.png").convert("RGB")
    w, h = im.size
    s = min(w, h) - 6
    x0 = (w - s) // 2
    y0 = int((h - s) * offset)
    a = np.asarray(im.crop((x0, y0, x0 + s, y0 + s)).resize((SIZE, SIZE), Image.LANCZOS), np.float32)
    b = np.roll(a, (SIZE // 2, SIZE // 2), axis=(0, 1))
    t = (np.arange(SIZE, dtype=np.float32) + 0.5) / SIZE
    wx = 0.5 - 0.5 * np.cos(2 * np.pi * t)
    wgt = np.sqrt(np.outer(wx, wx))[..., None]
    res = a * wgt + b * (1 - wgt)
    Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).save(out)
    return f"razorfen_kraul/materials/{name}"


def spec():
    thorn = make_seamless("rfk_thorn_tunnel_floor")
    boar = make_seamless("rfk_boar_pen_floor")
    bram = make_seamless("rfk_bramble_wall")
    earth = make_seamless("rfk_packed_earth_wall")
    beast = make_seamless("rfk_beast_pit_wall")
    R = RZ.ROOMS
    return dict(
        build="build_razorfen_baked", seed=163, slug="razorfen_kraul",
        materials={
            "thorn": M(thorn),
            "boar": M(boar),
            "bones": M(dim(VC + "vot_bonesand", 0.62)),
            "bramble": M(bram),
            "earth": M(earth),
            "beast": M(beast),
        },
        floor_keys=["thorn", "boar", "bones"],
        wall_keys=["bramble", "earth", "beast"],
        floors={
            "boar": [(R["hub"][0], R["hub"][1], 30, 24), (R["aggem"][0], R["aggem"][1], 20, 15),
                     (R["roogug"][0], R["roogug"][1], 19, 13), (R["nook_n"][0], R["nook_n"][1], 10, 8)],
            "bones": [(R["jargba"][0], R["jargba"][1], 19, 14), (R["charlga"][0], R["charlga"][1], 25, 15),
                      (R["nook_e"][0], R["nook_e"][1], 10, 8)],
        },
        walls={
            "earth": [(R["hub"][0], R["hub"][1], 38, 32), (R["court"][0], R["court"][1], 26, 17),
                      (R["jargba"][0], R["jargba"][1], 24, 17), (R["charlga"][0], R["charlga"][1], 30, 18)],
            "beast": [(R["pit"][0], R["pit"][1], 26, 20)],
        },
        pools=[],
        cfg=dict(ao=0.48, depth=0.84, lip=20, lip_col=(0.85, 0.62, 0.38), deep_dark=0.4,
                 foam_col=(220, 190, 140), glows=[]),
    )


BD.C = RZ
BD.SPECS = {"razorfen_kraul": spec()}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.bake_spec("razorfen_kraul", pv)
