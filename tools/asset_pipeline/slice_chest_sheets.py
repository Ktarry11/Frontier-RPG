"""Slice the chest sheets CH1, CH2 and CH3 (docs/chest_art_prompts.md, 22 Nov 2026) into
assets/tiles/chests/ch_<name>.png.

    python3 tools/asset_pipeline/slice_chest_sheets.py CH1 assets/tiles/chests/sheet/sheet_CH1.png

Twelve chests in three rows of four on flat magenta (Kyle: "Our current ones suck ass"; the old sheet came on a gradient
and had to be cut out with GrabCut, which is where the ragged halos came from). Each chest is found by its own outline,
the same way the leader sheets are, keyed with the project's one magenta curve, de-fringed, and saved tight with a few
pixels of air. world/chest_looks.chest_sprite scales every chest to the same width, so tight crops are what keep them
the same size on the ground.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from tools.asset_pipeline.slice_leader_sheet import key, MIN_BLOB

SHEETS = {
    "CH1": ["plain_box", "rope_crate", "iron_banded", "travel_trunk",
            "orc_hide", "savannah", "troll_tiki", "goblin_lockbox",
            "moonwood", "sea_chest", "sandstone_coffer", "wildwood"],
    "CH2": ["undead_rusted", "chained_cursed", "vine_bound", "highland",
            "dark_iron", "elven_gilded", "highborne_ruin", "bark_hollow",
            "aetherian_coffer", "geode", "storm_driftwood", "grave_ward"],
    "CH3": ["dark_oak", "steel_strongbox", "stone_coffer", "sunken_coral",
            "frost_rimed", "fel_forged", "crystal_reliquary", "ornate_gold",
            "royal_gold", "ossuary", "void_obsidian", "molten"],
}
ROWS, COLS, PAD = 3, 4, 4


def main(which, sheet, out="assets/tiles/chests"):
    names = SHEETS[which]
    rgb = np.asarray(Image.open(sheet).convert("RGB"))
    solid = key(rgb) > 128
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=6))
    blobs = []
    for i in range(1, n + 1):
        m = (lab == i) & solid
        if m.sum() < MIN_BLOB:
            continue
        ys, xs = np.nonzero(m)
        blobs.append({"k": i, "x0": xs.min(), "cy": (ys.min() + ys.max()) / 2})
    if len(blobs) != len(names):
        raise SystemExit(f"found {len(blobs)} chests, expected {len(names)}")
    blobs.sort(key=lambda b: b["cy"])
    cuts = sorted(sorted(range(len(blobs) - 1), key=lambda i: blobs[i + 1]["cy"] - blobs[i]["cy"],
                         reverse=True)[:ROWS - 1])
    rows, start = [], 0
    for c in cuts + [len(blobs) - 1]:
        rows.append(sorted(blobs[start:c + 1], key=lambda b: b["x0"]))
        start = c + 1
    if [len(r) for r in rows] != [COLS] * ROWS:
        raise SystemExit(f"rows came out {[len(r) for r in rows]}")
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    for b, name in zip([b for r in rows for b in r], names):
        mask = ndimage.binary_fill_holes((lab == b["k"]) & inner)
        ys, xs = np.nonzero(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])[y0:y1, x0:x1].copy()
        r_, g_, b_ = (rgba[..., i].astype(int) for i in range(3))
        spill = ring[y0:y1, x0:x1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        im = Image.fromarray(rgba, "RGBA")
        canvas = Image.new("RGBA", (im.width + 2 * PAD, im.height + 2 * PAD), (0, 0, 0, 0))
        canvas.paste(im, (PAD, PAD), im)
        canvas.save(os.path.join(out, f"ch_{name}.png"))
        print(f"  ch_{name:<18}{canvas.size}")
    print(f"{which}: {len(names)} chests")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
