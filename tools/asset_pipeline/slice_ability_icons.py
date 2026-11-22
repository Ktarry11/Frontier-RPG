#!/usr/bin/env python3
"""Cut a sheet of full-bleed ability icons into assets/icons/abilities/<id>.png, 64x64.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_ability_icons.py SHEET.png --cols=6 --rows=6 --ids=a,b,c,...

For the trait and Sworn skill sheets (docs/trait_and_sworn_icon_prompts.md). Those icons fill their square edge to
edge, the way every ability icon in the game does (the quest-item slicer keys a magenta background out instead, which
would eat these). Each cell is cut on an even grid, the black gutter round the art is trimmed off by finding where the
picture starts, and what's left is squared and scaled to 64x64. Ids past the end of the list are skipped, so a sheet
with spare cells needs nothing special.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "icons" / "abilities"
SIZE = 64


def art_box(cell):
    """The picture's bounds inside a cell: the rows and columns that aren't gutter black."""
    a = np.asarray(cell.convert("RGB"), dtype=np.int16)
    lit = a.max(axis=2) > 28
    rows, cols = np.where(lit.mean(axis=1) > 0.35)[0], np.where(lit.mean(axis=0) > 0.35)[0]
    if len(rows) < 8 or len(cols) < 8:
        return None
    return int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = {a.split("=", 1)[0][2:]: a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--") and "=" in a}
    sheet = Image.open(args[0]).convert("RGB")
    cols, rows = int(opt.get("cols", 6)), int(opt.get("rows", 6))
    ids = [i for i in opt["ids"].split(",") if i]
    cw, ch = sheet.width / cols, sheet.height / rows
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for n, icon_id in enumerate(ids):
        if n >= cols * rows:
            break
        c, r = n % cols, n // cols
        cell = sheet.crop((int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch)))
        box = art_box(cell)
        if box:
            x0, y0, x1, y1 = box
            side = max(x1 - x0, y1 - y0)
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            cell = cell.crop((cx - side // 2, cy - side // 2, cx - side // 2 + side, cy - side // 2 + side))
        cell.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{icon_id}.png")
        made += 1
    print(f"  {made} icons written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
