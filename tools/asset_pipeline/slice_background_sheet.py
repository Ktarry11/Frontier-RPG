#!/usr/bin/env python3
"""Cut a contact sheet of combat backgrounds into its individual panels.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_background_sheet.py SHEET.jpg OUTDIR

These sheets arrive as a grid of finished paintings on a flat dark backing, sometimes with a
caption band under each one, sometimes not, and the grids are not all the same shape (4x3, 4x4,
3x2). So the panels are FOUND, not computed from rows x cols:

  - the backing colour is read off the sheet's own border rather than assumed,
  - a row or column counts as a gutter when nearly all of it is that backing colour,
  - panels are the content runs between gutters.

Captions are cropped off afterwards by trimming any band at the bottom of a panel that is
backing-coloured apart from text, so a label never ends up baked into a background the player
sees behind a fight.

WHEN A CAPTION IS NOT ON THE BACKING, pass --trim-bottom=N and cut it by hand. On one of these
sheets the labels sat on their own grey band, and on another over the painting itself. I tried
to separate caption from art by pixel statistics - near-backing fraction, row saturation,
greyscale fraction - and every rule that caught the captions also caught a grey stalactite cave
that had to be kept, because "mostly grey at the bottom" is a true description of both. There is
no general rule here, only a general-looking one that silently eats art, so the escape hatch is
an explicit number you chose after looking at the result.

ALWAYS LOOK AT _contact.png BEFORE USING THE OUTPUT. This writes NN.png by position and nothing
else; naming them is a separate, human step. The creature sheets are the reason for that rule -
there, a list that merely had the right COUNT was in the wrong ORDER, and slicing "in order"
would have silently handed 180 creatures the wrong sprite.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

MIN_PANEL = 120          # px; anything thinner than this is a caption band or a rule, not art
BG_TOL = 26              # how far from the backing colour still counts as backing
GUTTER_FRAC = 0.985      # fraction of a line that must be backing for it to be a gutter


def backing_colour(a):
    """The sheet's own backing, read from its outermost ring of pixels."""
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    return np.median(edge, axis=0)


def runs(is_gutter, min_len):
    """-> [(start, end_exclusive)] of the content stretches between gutters."""
    out, start = [], None
    for i, g in enumerate(is_gutter):
        if not g and start is None:
            start = i
        elif g and start is not None:
            if i - start >= min_len:
                out.append((start, i))
            start = None
    if start is not None and len(is_gutter) - start >= min_len:
        out.append((start, len(is_gutter)))
    return out


def trim_caption(cell, bg):
    """Drop a caption band from the bottom of one panel.

    A caption band is mostly backing with a little text in it, so it reads as a near-backing
    strip. The painting above it does not. Only the BOTTOM is trimmed: these sheets caption
    under the image, and trimming all four sides would eat the dark sky off a night scene.
    """
    near = (np.abs(cell.astype(int) - bg).max(axis=2) <= BG_TOL)
    rowfrac = near.mean(axis=1)
    bottom = cell.shape[0]
    while bottom > MIN_PANEL and rowfrac[bottom - 1] > 0.80:
        bottom -= 1
    return cell[:bottom]


def _contact(panels, outdir):
    """Numbered contact sheet. Numbers are drawn ON the thumbnails because a grid of unlabelled
    thumbnails is exactly as easy to miscount as the original sheet was."""
    if not panels:
        return
    from PIL import ImageDraw
    cell_w, cell_h, cols_n = 200, 130, 4
    rows_n = -(-len(panels) // cols_n)
    sheet = Image.new("RGB", (cols_n * (cell_w + 8) + 8, rows_n * (cell_h + 22) + 8), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(panels):
        t = p.copy()
        t.thumbnail((cell_w, cell_h))
        cx = 8 + (i % cols_n) * (cell_w + 8)
        cy = 8 + (i // cols_n) * (cell_h + 22)
        sheet.paste(t, (cx + (cell_w - t.width) // 2, cy))
        d.text((cx + 4, cy + cell_h + 4), f"{i:02d}", fill=(255, 230, 120))
    sheet.save(outdir / "_contact.png")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        raise SystemExit("usage: slice_background_sheet.py SHEET.jpg OUTDIR")
    src, outdir = Path(args[0]), Path(args[1])
    outdir.mkdir(parents=True, exist_ok=True)

    a = np.array(Image.open(src).convert("RGB"))
    bg = backing_colour(a)
    near = (np.abs(a.astype(int) - bg).max(axis=2) <= BG_TOL)

    rects_file = next((x for x in sys.argv[1:] if x.startswith("--rects=")), None)
    if rects_file:
        # SOME SHEETS ARE MOSAICS, NOT GRIDS. One of these had a double-height ice cave beside a
        # double-height arena, a column split into two half-height cells, and two rows of four
        # below - no rows x cols describes it, and slicing it 4x3 produced twelve cells each
        # holding fragments of two different paintings. Rather than write a general mosaic
        # segmenter for one sheet, the rectangles are measured off the sheet's own separator
        # lines and listed in a file, which is reproducible and wrong in ways a contact sheet
        # shows immediately.
        boxes = []
        for line in Path(rects_file.split("=", 1)[1]).read_text().splitlines():
            line = line.split("#")[0].strip()
            if line:
                boxes.append(tuple(int(v) for v in line.replace(",", " ").split()))
        n = 0
        panels = []
        for (x0, y0, x1, y1) in boxes:
            img = Image.fromarray(a[y0:y1, x0:x1])
            img.save(outdir / f"{n:02d}.png")
            panels.append(img)
            n += 1
        _contact(panels, outdir)
        print(f"{src.name}: {n} panels from {len(boxes)} explicit rectangles in {outdir}")
        return 0

    grid = next((x for x in sys.argv[1:] if x.startswith("--grid=")), None)
    if grid:
        # SOME SHEETS HAVE NO GUTTERS - the paintings butt edge to edge with no backing between
        # them, so there is genuinely nothing to detect and the arithmetic IS the right answer.
        # It is opt-in and never a fallback: silently dropping to a grid when detection came up
        # short is how you get an off-by-one that shifts every panel after it, and the contact
        # sheet below is still the thing that decides whether it worked.
        gc, gr = (int(v) for v in grid.split("=", 1)[1].lower().split("x"))
        H, W, _ = a.shape
        rows = [(round(i * H / gr), round((i + 1) * H / gr)) for i in range(gr)]
        cols = [(round(i * W / gc), round((i + 1) * W / gc)) for i in range(gc)]
    else:
        rows = runs(near.mean(axis=1) >= GUTTER_FRAC, MIN_PANEL)
        cols = runs(near.mean(axis=0) >= GUTTER_FRAC, MIN_PANEL)
    if not rows or not cols or (len(rows) * len(cols)) < 2:
        raise SystemExit(
            f"{src.name}: found {len(rows)} row band(s) x {len(cols)} column band(s). If this "
            f"sheet's panels touch with no backing between them there is nothing to detect - "
            f"count the grid yourself and pass --grid=COLSxROWS.")

    hand_trim = next((x for x in sys.argv[1:] if x.startswith("--trim-bottom=")), None)
    hand_trim = int(hand_trim.split("=", 1)[1]) if hand_trim else 0

    n = 0
    panels = []
    for (y0, y1) in rows:
        for (x0, x1) in cols:
            cell = trim_caption(a[y0:y1, x0:x1], bg)
            if hand_trim:
                cell = cell[:max(MIN_PANEL, cell.shape[0] - hand_trim)]
            if cell.shape[0] < MIN_PANEL or cell.shape[1] < MIN_PANEL:
                continue
            img = Image.fromarray(cell)
            img.save(outdir / f"{n:02d}.png")
            panels.append(img)
            n += 1

    _contact(panels, outdir)

    print(f"{src.name}: {len(rows)} row band(s) x {len(cols)} column band(s) -> {n} panels "
          f"in {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
