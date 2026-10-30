"""Slice a magenta prop sheet into individual RGBA props, in a stated order.

    python3 tools/asset_pipeline/slice_prop_sheet.py <sheet.png> <out_dir> <name1,name2,...> [--by x|rows]

    --by rows   (default) group blobs into rows by vertical position, then read each row left to
                right. Correct for any grid sheet - 6x5, 5x4, the irregular 6/5/5/4 the recruit
                sprite sheet came back as.
    --by x      one single row: order purely left to right.

WHY THE ORDER IS A FLAG AND NOT A GUESS. The two Bloodsail ships came on one sheet side by side,
and the row-grouping path read them as two rows and swapped them - the galleon's masts put its
centre of mass higher than the raider's, so it sorted first and the file named bloodsail_raider
held the four-masted galleon. Nothing errored. The only reason it was caught is that the galleon
came out SMALLER than the raider, which is backwards, and that was worth looking at.

A miscount or a mis-order silently shifts every prop after it, so this refuses to write unless the
number of figures found matches the number of names given.

Keying and de-fringing are the same as the recruit sheets: magenta-ness is min(r,b) - g, art is
anything under 80, then erode a pixel off the edge and pull the magenta spill out of the next ring
in so nothing ships with a pink halo.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

MIN_BLOB = 2000  # px of real art; below this it is a speck, not a prop


def extract(sheet, by="rows", min_blob=MIN_BLOB):
    rgb = np.asarray(Image.open(sheet).convert("RGB")).astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    solid = (np.minimum(r, b) - g) < 80
    H, _W = solid.shape

    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=4))
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s >= min_blob]
    if not keep:
        raise SystemExit("no props found - is the background actually magenta?")
    cents = ndimage.center_of_mass(solid, lab, keep)

    if by == "x":
        seq = [k for k, _c in sorted(zip(keep, cents), key=lambda t: t[1][1])]
        print(f"  {len(seq)} props, ordered left to right")
    else:
        ordered = sorted(zip(keep, cents), key=lambda t: t[1][0])
        rows, cur = [], [ordered[0]]
        for item in ordered[1:]:
            if item[1][0] - cur[-1][1][0] > H * 0.08:
                rows.append(cur)
                cur = [item]
            else:
                cur.append(item)
        rows.append(cur)
        seq = [k for row in rows for k, _c in sorted(row, key=lambda t: t[1][1])]
        print(f"  {len(seq)} props in {len(rows)} rows: {[len(r) for r in rows]}")

    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    rgb8 = rgb.astype(np.uint8)
    out = []
    for k in seq:
        mask = (lab == k) & inner
        ys, xs = np.where(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([rgb8, np.where(mask, 255, 0).astype(np.uint8)])[y0:y1, x0:x1].copy()
        r_, g_, b_ = (rgba[..., i].astype(int) for i in range(3))
        spill = ring[y0:y1, x0:x1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        out.append(Image.fromarray(rgba, "RGBA"))
    return out


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    sheet, out_dir, names = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    by = sys.argv[sys.argv.index("--by") + 1] if "--by" in sys.argv else "rows"
    crops = extract(sheet, by)
    if len(crops) != len(names):
        raise SystemExit(f"found {len(crops)} props but was given {len(names)} names - refusing to "
                         f"write, because a miscount shifts everything after it")
    os.makedirs(out_dir, exist_ok=True)
    for name, im in zip(names, crops):
        im.save(os.path.join(out_dir, f"{name.strip()}.png"))
        print(f"  {name.strip():28} {im.size}")


if __name__ == "__main__":
    main()
