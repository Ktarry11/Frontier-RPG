"""
Bake The Broodspiral painting (amber hive, resin, larval floors; chitin/resin/queen walls).

    python3 tools/bake_broodspiral.py [--preview DIR]

The amber hive textures in assets/tiles/broodspiral/*.png are ~400px and NOT seamless, so the first run makes
256px seamless copies in assets/tiles/broodspiral/materials/ (cosine-blended half-shift) and the Durotar cave
baker (tools/bake_durotar_caves.bake_spec) paints from those.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from tools import bake_durotar_caves as BD
from tools import handbuilt_broodspiral as BS
from tools.bake_durotar_caves import M, TEX

SRC = TEX / "broodspiral"
MAT = SRC / "materials"
SIZE = 256


def make_seamless(name, tint=1.0):
    out = MAT / f"{name}.png"
    if out.exists():
        return f"broodspiral/materials/{name}"
    MAT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC / f"{name}.png").convert("RGB")
    w, h = im.size
    s = min(w, h) - 24                                           # drop the painted border
    x0, y0 = (w - s) // 2, (h - s) // 2
    a = np.asarray(im.crop((x0, y0, x0 + s, y0 + s)).resize((SIZE, SIZE), Image.LANCZOS), np.float32)
    b = np.roll(a, (SIZE // 2, SIZE // 2), axis=(0, 1))          # seams now run through the middle
    t = (np.arange(SIZE, dtype=np.float32) + 0.5) / SIZE
    wx = 0.5 - 0.5 * np.cos(2 * np.pi * t)                       # 0 at the tile edge, 1 at the centre
    wgt = np.sqrt(np.outer(wx, wx))[..., None]                   # original kept in the middle, shifted copy at edges
    # centre of `a` is clean, edges of `a` are where the seam of `b` is not -> blend a (centre) into b (edges)
    res = a * wgt + b * (1 - wgt)
    res *= tint
    Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).save(out)
    return f"broodspiral/materials/{name}"


def mats():
    return {n: make_seamless(n) for n in
            ("hive_floor", "resin_floor", "larval_floor", "chitin_wall", "resin_wall", "queens_chamber_wall")}


def spec():
    m = mats()
    wx, wy = BS.sp(BS.TH_WARDEN)
    kx, ky = BS.sp(BS.TH_KEEPER)
    gx, gy = BS.sp(BS.TH_GUARD)
    nk = {}
    for key, n in BS.NOOKS.items():
        x, y = BS.radial(n["theta"], n["side"] * n["dist"])
        nk[key] = (round(x), round(y))
    return dict(
        build="build_broodspiral_baked", seed=151, slug="broodspiral",
        materials={
            "hive":   M(m["hive_floor"]),
            "resin":  M(m["resin_floor"]),
            "larval": M(m["larval_floor"]),
            "chitin": M(m["chitin_wall"]),
            "rwall":  M(m["resin_wall"]),
            "qwall":  M(m["queens_chamber_wall"]),
        },
        floor_keys=["hive", "resin", "larval"],
        wall_keys=["chitin", "rwall", "qwall"],
        floors={
            "resin": [(round(kx), round(ky), 19, 15), (nk["amberwing"][0], nk["amberwing"][1], 12, 8),
                      (BS.CX, BS.CY, 12, 11)],
            "larval": [(round(gx), round(gy), 17, 13), (nk["eggs"][0], nk["eggs"][1], 11, 8),
                       (nk["gnash"][0], nk["gnash"][1], 12, 9), (BS.CX + 4, BS.CY + 24, 14, 8)],
        },
        walls={
            "rwall": [(round(kx), round(ky), 22, 18), (nk["amberwing"][0], nk["amberwing"][1], 14, 10),
                      (nk["skrix"][0], nk["skrix"][1], 13, 10)],
            "qwall": [(BS.CX, BS.CY, 30, 28)],
        },
        pools=[],
        cfg=dict(ao=0.46, depth=0.82, lip=22, lip_col=(1.0, 0.78, 0.35), deep_dark=0.4,
                 foam_col=(230, 200, 140), glows=[]),
    )


BD.C = BS
BD.SPECS = {"broodspiral": spec()}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.bake_spec("broodspiral", pv)
