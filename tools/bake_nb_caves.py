"""
Bake the two Northern Barrens caves: Boulder Lode Mine (quarried rock + a blue-violet crystal vein chamber) and
Serena's Hollow (weathered cliff gorge + a woven-nest roost).

    PYTHONPATH=. python3 tools/bake_nb_caves.py [boulder_lode_mine|serenas_hollow ...] [--preview DIR]

The 8 source textures (assets/tiles/boulder_lode_mine/*.png, assets/tiles/serenas_hollow/*.png) are tall (~300x612)
and NOT seamless, so the first run makes 256px seamless copies in each folder's materials/ dir and the Durotar cave
baker paints from those.
"""
import sys

import numpy as np
from PIL import Image

from tools import bake_durotar_caves as BD
from tools import handbuilt_boulder_lode as BL
from tools import handbuilt_serenas_hollow as SH
from tools.bake_durotar_caves import M, TEX, dim

SIZE = 256


def make_seamless(folder, name, offset=0.5):
    src = TEX / folder
    mat = src / "materials"
    out = mat / f"{name}.png"
    if out.exists():
        return f"{folder}/materials/{name}"
    mat.mkdir(parents=True, exist_ok=True)
    im = Image.open(src / f"{name}.png").convert("RGB")
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
    return f"{folder}/materials/{name}"


def spec_lode():
    f = make_seamless("boulder_lode_mine", "floor")
    fc = make_seamless("boulder_lode_mine", "floor_crystal")
    w = make_seamless("boulder_lode_mine", "wall")
    wc = make_seamless("boulder_lode_mine", "wall_crystal")
    R = BL.ROOMS
    vx, vy = R["vein"][:2]
    return dict(
        build="build_boulder_lode_baked", seed=307, slug="boulder_lode_mine",
        materials={"floor": M(f), "crystal_f": M(fc), "wall": M(w), "crystal_w": M(wc)},
        floor_keys=["floor", "crystal_f"],
        wall_keys=["wall", "crystal_w"],
        floors={"crystal_f": [(vx, vy, 23, 13)]},
        walls={"crystal_w": [(vx, vy, 30, 17)]},
        pools=[],
        cfg=dict(ao=0.48, depth=0.84, lip=20, lip_col=(0.80, 0.62, 0.42), deep_dark=0.4,
                 foam_col=(200, 200, 210), glows=[]),
    )


def spec_hollow():
    f = make_seamless("serenas_hollow", "floor")
    fn = make_seamless("serenas_hollow", "floor_nest")
    w = make_seamless("serenas_hollow", "wall")
    wn = make_seamless("serenas_hollow", "wall_nest")
    R = SH.ROOMS
    rx, ry = R["roost"][:2]
    sx, sy = R["ledge"][:2]
    ax, ay = R["nest_a"][:2]
    return dict(
        build="build_serenas_hollow_baked", seed=311, slug="serenas_hollow",
        materials={"floor": M(f), "nest_f": M(fn), "wall": M(w), "nest_w": M(wn)},
        floor_keys=["floor", "nest_f"],
        wall_keys=["wall", "nest_w"],
        floors={"nest_f": [(rx, ry, 22, 11), (sx, sy, 10, 8), (ax, ay, 9, 7), (R["nest_w"][0], R["nest_w"][1], 8, 7)]},
        walls={"nest_w": [(rx, ry, 27, 15)]},
        pools=[],
        cfg=dict(ao=0.46, depth=0.85, lip=20, lip_col=(0.82, 0.70, 0.55), deep_dark=0.4,
                 foam_col=(220, 210, 190), glows=[]),
    )


MODULES = {"boulder_lode_mine": BL, "serenas_hollow": SH}
SPECS = {"boulder_lode_mine": spec_lode, "serenas_hollow": spec_hollow}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
