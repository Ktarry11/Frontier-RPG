"""Slice a generated 8x6 tile sheet whose rows are NOT straight (each column's row lines sit at different heights).

    python3 tools/asset_pipeline/slice_sheet_percell.py sheet.png out_dir name1 ... name48

For every column the strongest row-to-row colour jump near each expected boundary is found inside that column only, so a cell is cut
between ITS OWN neighbours; each cell is then inset a few px, centre-cropped to a square and resized to 256.  Run make_seamless.py next.
"""
import os
import sys

import numpy as np
from PIL import Image

COLS, ROWS, INSET = 8, 6, 14


def main(sheet, out_dir, names):
    assert len(names) == COLS * ROWS
    im = Image.open(sheet).convert("RGB")
    a = np.asarray(im, np.float32)
    H, W = a.shape[:2]
    cw = W / COLS
    os.makedirs(out_dir, exist_ok=True)
    xs = [int(round(c * cw)) for c in range(COLS + 1)]
    for c in range(COLS):
        x0, x1 = xs[c], xs[c + 1]
        d = np.abs(a[1:, x0 + 6:x1 - 6] - a[:-1, x0 + 6:x1 - 6]).mean(axis=(1, 2))
        bounds = [0]
        for r in range(1, ROWS):
            e = int(r * H / ROWS)
            lo, hi = max(e - 45, bounds[-1] + 60), min(e + 45, H - 60)
            bounds.append(lo + int(np.argmax(d[lo:hi])) + 1)
        bounds.append(H)
        for r in range(ROWS):
            y0, y1 = bounds[r] + INSET, bounds[r + 1] - INSET
            cx0, cx1 = x0 + INSET, x1 - INSET
            side = min(cx1 - cx0, y1 - y0)
            ox, oy = cx0 + (cx1 - cx0 - side) // 2, y0 + (y1 - y0 - side) // 2
            im.crop((ox, oy, ox + side, oy + side)).resize((256, 256), Image.LANCZOS).save(f"{out_dir}/{names[r * COLS + c]}.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
