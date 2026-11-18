#!/usr/bin/env python3
"""Slice the Collection's icon sheet (Sheet D, docs/collection_art_prompts.md) into assets/icons/collection/.

    python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png

A 6x6 sheet on a magenta key, delivered 18 Nov 2026. Cut on the magenta gutters (the columns and rows with the least
art near each sixth), not by blob-finding, so a glow that floats free of its icon (the spirit wolf charm's blue mist)
stays with it. Each icon is keyed, de-fringed and centred on a 96x96 square, the size of the quest-item icons.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

OUT = os.path.join("assets", "icons", "collection")
SIZE = 96
IDS = [
    "col_reins_kodo", "col_reins_runabout", "col_reins_turtle", "col_reins_elk", "col_reins_hawkstrider",
    "col_reins_nightmare",
    "col_reins_rose", "col_reins_dawn", "col_reins_spring", "col_reins_jade", "col_reins_tide", "col_reins_twilight",
    "col_charm_murloc", "col_charm_wolf", "col_charm_serpent", "col_charm_bird", "col_charm_spirit",
    "col_charm_drowned",
    "col_title_common", "col_title_rare", "col_feather_kalimdor", "col_feather_eastern", "col_tome_hearth",
    "col_hearthstone_2",
    "col_satchel_bank", "col_peddler_bell", "col_courier_horn", "col_book_master", "col_book_professions",
    "col_satchel_reagents",
    "col_heirloom_head", "col_heirloom_shoulder", "col_heirloom_chest", "col_heirloom_back",
    "col_heirloom_two_hand", "col_heirloom_shield",
]


def cuts(profile, n, size):
    out = [0]
    for k in range(1, n):
        lo, hi = int(size * k / n - size / 14), int(size * k / n + size / 14)
        out.append(lo + int(np.argmin(profile[lo:hi])))
    return out + [size]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    rgb = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    solid = (np.minimum(r, b) - g) < 80
    H, W = solid.shape
    xs, ys = cuts(solid.sum(axis=0), 6, W), cuts(solid.sum(axis=1), 6, H)
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    rgb8 = rgb.astype(np.uint8)
    os.makedirs(OUT, exist_ok=True)
    k = 0
    for j in range(6):
        for i in range(6):
            cell = np.zeros_like(inner)
            cell[ys[j]:ys[j + 1], xs[i]:xs[i + 1]] = True
            mask = inner & cell
            yy, xx = np.where(mask)
            if len(yy) == 0:
                raise SystemExit(f"cell {k + 1} ({IDS[k]}) is empty - refusing to write")
            y0, y1, x0, x1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
            rgba = np.dstack([rgb8, np.where(mask, 255, 0).astype(np.uint8)])[y0:y1, x0:x1].copy()
            r_, g_, b_ = (rgba[..., c].astype(int) for c in range(3))
            spill = ring[y0:y1, x0:x1] & (np.minimum(r_, b_) > g_ + 25)
            lim = g_ + 25
            rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
            rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
            im = Image.fromarray(rgba, "RGBA")
            side = max(im.width, im.height)
            sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
            sq.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, f"{IDS[k]}.png"))
            k += 1
    print(f"  {k} icons written to {OUT} (cuts x {xs[1:-1]}, y {ys[1:-1]})")


if __name__ == "__main__":
    main()
