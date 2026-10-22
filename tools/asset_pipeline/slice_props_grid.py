"""Grid-based prop slicer for sheets where slice_sheet.py's object grouping miscounts (fused/fragmented props).

    python3 tools/asset_pipeline/slice_props_grid.py sheet.png out_dir COLSxROWS name1 name2 ...

Keys the magenta background exactly like slice_sheet.py, then assigns every foreground component to the grid cell
holding most of its pixels (props sit inside their own cell by prompt design), drops specks, tight-crops and
writes <name>.png.  Reports cells with 0 or >1 large components and props whose bbox leaves their cell.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from slice_sheet import key_magenta, despill  # noqa: E402


def slice_grid(sheet, out_dir, grid, names, min_px=400):
    cols, rows = (int(v) for v in grid.lower().split("x"))
    assert len(names) == cols * rows, f"need {cols*rows} names"
    arr = np.array(Image.open(sheet).convert("RGBA"))
    H, W = arr.shape[:2]
    bg = key_magenta(arr)
    fg = ndi.binary_opening(~bg, iterations=1)
    arr = despill(arr, fg)
    arr[:, :, 3] = np.where(fg, 255, 0)
    lab, n = ndi.label(fg)
    cw, ch = W / cols, H / rows
    owner = {}
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        m = lab[sl] == i
        cnt = int(m.sum())
        if cnt < min_px:
            continue
        ys, xs = np.nonzero(m)
        cx, cy = xs.mean() + sl[1].start, ys.mean() + sl[0].start
        cell = int(cy // ch) * cols + int(cx // cw)
        owner.setdefault(cell, []).append(i)
    os.makedirs(out_dir, exist_ok=True)
    problems = []
    for cell, name in enumerate(names):
        ids = owner.get(cell, [])
        if not ids:
            problems.append((name, "EMPTY"))
            continue
        sel = np.isin(lab, ids)
        ys, xs = np.nonzero(sel)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        sub = arr[y0:y1 + 1, x0:x1 + 1].copy()
        sub[:, :, 3] = np.where(sel[y0:y1 + 1, x0:x1 + 1], 255, 0)
        Image.fromarray(sub).save(os.path.join(out_dir, name + ".png"))
        r, c = divmod(cell, cols)
        if x0 < c * cw - 4 or x1 > (c + 1) * cw + 4 or y0 < r * ch - 4 or y1 > (r + 1) * ch + 4:
            problems.append((name, "leaves its cell"))
        if len(ids) > 1:
            problems.append((name, f"{len(ids)} pieces merged"))
        if x0 <= 1 or y0 <= 1 or x1 >= W - 2 or y1 >= H - 2:
            problems.append((name, "touches sheet border"))
    print("problems:", problems or "none")


if __name__ == "__main__":
    slice_grid(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
