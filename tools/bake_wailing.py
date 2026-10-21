"""
Bake Wailing Caverns painting (river-silt cavern floors, green river water, serpent-shrine stone around the Fang's
chambers; cavern rock / mossy rock walls).

    PYTHONPATH=. python3 tools/bake_wailing.py [--preview DIR]

The five wc_* textures in assets/tiles/wailing_caverns/ are tall (~240x613) and NOT seamless, so the first run makes
256px seamless copies in assets/tiles/wailing_caverns/materials/ and the Durotar cave baker paints from those.
"""
import sys

import numpy as np
from PIL import Image

from tools import bake_durotar_caves as BD
from tools import handbuilt_wailing as WC
from tools.bake_durotar_caves import M, TEX, dim, CS

SRC = TEX / "wailing_caverns"
MAT = SRC / "materials"
SIZE = 256


def make_seamless(name, offset=0.5):
    out = MAT / f"{name}.png"
    if out.exists():
        return f"wailing_caverns/materials/{name}"
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
    return f"wailing_caverns/materials/{name}"


def make_water(name="wc_river_water"):
    """Brighter, bluer river water (the source texture is a dark swamp green; deep pool centres went black)."""
    out = MAT / f"{name}_lit.png"
    if not out.exists():
        a = np.asarray(Image.open(MAT / f"{name}.png").convert("RGB"), np.float32)
        a = a * 1.6 + np.array([-6, 4, 16], np.float32)
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
    return f"wailing_caverns/materials/{name}_lit"


def spec():
    floor = make_seamless("wc_cavern_floor")
    edge = make_seamless("wc_river_edge_floor")
    wall = make_seamless("wc_cavern_wall")
    shrine = make_seamless("wc_serpent_shrine_wall")
    make_seamless("wc_river_water")
    water = make_water()
    R = WC.ROOMS
    return dict(
        build="build_wailing_baked", seed=211, slug="wailing_caverns",
        materials={
            "floor": M(floor, CS + "wc_floor_a"),
            "silt": M(edge, floor),
            "moss": M(CS + "wc_floor_a"),
            "shrine_f": M(dim(shrine, 0.9)),
            "water_s": M(water),
            "water_d": M(dim(water, 0.85)),
            "wall": M(wall),
            "mosswall": M(CS + "wc_wall_a"),
            "shrine": M(shrine),
        },
        floor_keys=["floor", "silt", "moss", "shrine_f"],
        wall_keys=["wall", "mosswall", "shrine"],
        floors={
            "silt": [(R["main"][0], R["main"][1] + 2, 38, 14), (R["kresh"][0], R["kresh"][1], 22, 15),
                     (R["pythas"][0], R["pythas"][1], 12, 9), (R["den"][0], R["den"][1], 12, 9)],
            "moss": [(R["skum"][0], R["skum"][1], 18, 12), (R["nook_w"][0], R["nook_w"][1], 10, 8),
                     (R["nook_se"][0], R["nook_se"][1], 10, 8), (R["nook_sw"][0], R["nook_sw"][1], 10, 8)],
            "shrine_f": [(R["fang"][0], R["fang"][1], 22, 14), (R["dream"][0], R["dream"][1], 17, 12)],
        },
        walls={
            "mosswall": [(R["skum"][0], R["skum"][1], 24, 17), (R["kresh"][0], R["kresh"][1], 26, 18),
                         (R["den"][0], R["den"][1], 22, 16)],
            "shrine": [(R["fang"][0], R["fang"][1], 30, 20), (R["dream"][0], R["dream"][1], 26, 18),
                       (R["main"][0], R["main"][1] - 26, 12, 8)],
        },
        pools=[WC.WC_POOLS],
        cfg=dict(ao=0.46, depth=0.85, lip=22, lip_col=(0.55, 0.78, 0.58), deep_dark=0.4,
                 foam_col=(190, 225, 190), glows=[]),
    )


BD.C = WC
BD.SPECS = {"wailing_caverns": spec()}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.bake_spec("wailing_caverns", pv)
