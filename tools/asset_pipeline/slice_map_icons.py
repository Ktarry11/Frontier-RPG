"""Slice sheet MI1 (docs/map_icon_art_prompts.md, 22 Nov 2026) into assets/icons/map/<name>.png.

    python3 tools/asset_pipeline/slice_map_icons.py assets/icons/map/_src/sheet_MI1.png

Twenty-four round medallions on a 6 x 4 grid on magenta. Each cell's medallion is found by its own outline (the largest
blob in the cell), keyed off the magenta with the project's one key curve, trimmed to a square round its centre and
saved at 128 px, which is far more than the map ever draws (16 to 24 px) and keeps the downscale clean.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from tools.asset_pipeline.slice_leader_sheet import key

NAMES = ["shop", "rep", "flight", "inn", "hearth", "ride",
         "class", "prof", "forge", "sawmill", "mail", "auction",
         "ore", "herb", "wood", "fish", "portal", "boat",
         "chest", "poi", "player", "bank", "dungeon", "leader"]
COLS, ROWS, SIZE = 6, 4, 128


def main(sheet, out="assets/icons/map"):
    rgb = np.asarray(Image.open(sheet).convert("RGB"))
    H, W = rgb.shape[:2]
    cw, ch = W / COLS, H / ROWS
    alpha = key(rgb)
    for i, name in enumerate(NAMES):
        r, c = divmod(i, COLS)
        x0, y0, x1, y1 = int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch)
        a = alpha[y0:y1, x0:x1]
        lab, n = ndimage.label(a > 128)
        if not n:
            raise SystemExit(f"{name}: nothing in its cell")
        big = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
        m = ndimage.binary_fill_holes(lab == big)
        ys, xs = np.nonzero(m)
        cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
        half = max(xs.max() - xs.min(), ys.max() - ys.min()) / 2 + 2
        bx0, by0 = int(round(cx - half)), int(round(cy - half))
        side = int(round(2 * half))
        tile = np.zeros((side, side, 4), np.uint8)
        sx0, sy0 = max(0, bx0), max(0, by0)
        sx1, sy1 = min(a.shape[1], bx0 + side), min(a.shape[0], by0 + side)
        tile[sy0 - by0:sy1 - by0, sx0 - bx0:sx1 - bx0, :3] = rgb[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
        tile[sy0 - by0:sy1 - by0, sx0 - bx0:sx1 - bx0, 3] = np.where(m[sy0:sy1, sx0:sx1], a[sy0:sy1, sx0:sx1], 0)
        Image.fromarray(tile, "RGBA").resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(out, f"{name}.png"))
        print(f"  {name:<9} {side}px")
    print(f"MI1: {len(NAMES)} icons")


if __name__ == "__main__":
    main(sys.argv[1])
