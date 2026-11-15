#!/usr/bin/env python3
"""Cut a walk-cycle sheet into per-character walk frames (claude/walk_cycle_prompts.md).

    PYTHONPATH=. python3 tools/slice_walk_sheet.py SHEET tl=forsaken/forsaken_1 tr=orc/orc_5 [bl=..] [br=..]
    PYTHONPATH=. python3 tools/slice_walk_sheet.py SHEET one=orc/orc_8        # a 3x3 sheet, one character
    PYTHONPATH=. python3 tools/slice_walk_sheet.py SHEET r1=tauren/tauren_4 r2=.. r3=..   # four-way sheet
    add --preview OUT.png to write a contact strip instead of touching assets/

A 6x6 sheet holds four 3x3 blocks (tl, tr, bl, br); a 3x3 sheet holds one (one). Inside a block:
row 1 walking down, row 2 walking up, row 3 walking right; column 1 left foot forward, column 2
standing, column 3 right foot forward. Left is the right side mirrored.

A FOUR-WAY sheet (6x6 for three characters, 6x4 landscape for two) gives each character two full rows (r1 = rows 1-2, r2 = rows 3-4,
r3 = rows 5-6): first row down 1-3 then up 1-3, second row right 1-3 then left 1-3. Its left side
is drawn, not mirrored, so whatever a character wears on one side stays there. Add --mirror-left
to throw the drawn left away and mirror the right instead, if the model botched it, or write
folder:mirror (r2=tauren/tauren_6:mirror) to do that for one character only.

Writes, into assets/npcs/<folder>/:
  walk_<down|up|right|left>_<1|2|3>.png   (left is right, mirrored)
  down.png / up.png / right.png / left.png = the standing frame (2) of each, so a folder that
  had one front pose copied four times gets real back and side views too.

Every frame of one character goes on the SAME canvas, feet on the bottom edge and the body's
centre on the canvas centre. The game scales a sprite by its height, so a shared canvas is what
keeps the character the same size in every frame and stops it jittering sideways mid-stride. The
body's centre is taken from the head and shoulders, not the whole figure: a stride or a staff
would drag a whole-figure centre about.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from slice_icon_sheet import key_magenta  # noqa: E402

BLOCKS = {"tl": (0, 0), "tr": (0, 3), "bl": (3, 0), "br": (3, 3), "one": (0, 0),
          "r1": (0, 0), "r2": (2, 0), "r3": (4, 0)}
ROWS = ("down", "up", "right")
# four-way layout: (row offset, first column) of each direction inside a character's two rows
FOUR_WAY = {"down": (0, 0), "up": (0, 3), "right": (1, 0), "left": (1, 3)}
PAD = 4


def _cells(r0, c0, four_way):
    if four_way:
        return [(d, j, r0 + dr, dc + j) for d, (dr, dc) in FOUR_WAY.items() for j in range(3)]
    return [(d, j, r0 + i, c0 + j) for i, d in enumerate(ROWS) for j in range(3)]


def _frames(rgba, grid, r0, c0, four_way=False):
    """{(dir, n): (RGBA array cropped to the figure, its body centre x)}. `grid` is (cols, rows)."""
    H, W = rgba.shape[:2]
    cw, ch = W / grid[0], H / grid[1]
    out = {}
    for d, j, r, c in _cells(r0, c0, four_way):
        y0, x0 = int(r * ch), int(c * cw)
        cell = rgba[y0:int(y0 + ch), x0:int(x0 + cw)]
        a = cell[..., 3]
        ys, xs = np.nonzero(a > 128)
        if len(ys) < 50:
            raise SystemExit(f"empty cell: block at row {r0} col {c0}, {d} frame {j + 1}")
        top, bot = ys.min(), ys.max()
        left, right = xs.min(), xs.max()
        fig = cell[top:bot + 1, left:right + 1]
        h = bot - top + 1
        band = fig[int(h * 0.05):int(h * 0.35), :, 3]
        cols = band.sum(axis=0)
        cx = float((cols * np.arange(len(cols))).sum() / max(cols.sum(), 1))
        out[(d, j + 1)] = (fig, cx)
    return out


def slice_block(rgba, grid, r0, c0, four_way=False, mirror_left=False):
    frames = _frames(rgba, grid, r0, c0, four_way)
    if mirror_left:
        frames = {k: v for k, v in frames.items() if k[0] != "left"}
    half = max(max(cx, f.shape[1] - cx) for f, cx in frames.values())
    cw = int(np.ceil(half)) * 2 + PAD * 2
    chh = max(f.shape[0] for f, _ in frames.values()) + PAD
    imgs = {}
    for (d, n), (f, cx) in frames.items():
        canvas = np.zeros((chh, cw, 4), dtype=np.float64)
        x = int(round(cw / 2 - cx))
        y = chh - f.shape[0]
        canvas[y:y + f.shape[0], x:x + f.shape[1]] = f
        imgs[(d, n)] = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGBA")
    for n in (1, 2, 3):
        if ("left", n) not in imgs:
            imgs[("left", n)] = imgs[("right", n)].transpose(Image.FLIP_LEFT_RIGHT)
    return imgs


def main(argv):
    preview = None
    if "--preview" in argv:
        k = argv.index("--preview")
        preview = argv[k + 1]
        argv = argv[:k] + argv[k + 2:]
    mirror_left = "--mirror-left" in argv
    argv = [a for a in argv if a != "--mirror-left"]
    sheet, jobs = argv[0], dict(a.split("=", 1) for a in argv[1:])
    four_way = any(k.startswith("r") for k in jobs)
    rgba = key_magenta(np.asarray(Image.open(sheet).convert("RGB")).astype(np.float64))
    # Square cells: a 6-wide sheet is 6 rows tall when square, 4 when it's 3:2 (two characters).
    cols = 3 if "one" in jobs else 6
    grid = (cols, int(round(cols * rgba.shape[0] / rgba.shape[1])))
    strips = []
    for block, folder in jobs.items():
        r0, c0 = BLOCKS[block]
        # folder:mirror throws away one character's drawn left side and mirrors its right instead
        folder, _, opt = folder.partition(":")
        imgs = slice_block(rgba, grid, r0, c0, four_way, mirror_left or opt == "mirror")
        if preview:
            strips.append(imgs)
            continue
        out = ROOT / "assets" / "npcs" / folder
        if not out.is_dir():
            raise SystemExit(f"no such sprite folder: {out}")
        for (d, n), im in imgs.items():
            im.save(out / f"walk_{d}_{n}.png")
            if n == 2:
                im.save(out / f"{d}.png")
        print(f"{folder}: 12 walk frames, {imgs[('down', 2)].size[0]}x{imgs[('down', 2)].size[1]}")
    if preview:
        order = [(d, n) for d in ("down", "up", "right", "left") for n in (1, 2, 3)]
        w = max(im.size[0] for s in strips for im in s.values())
        h = max(im.size[1] for s in strips for im in s.values())
        sheet_img = Image.new("RGBA", (w * len(order), h * len(strips)), (70, 70, 70, 255))
        for r, s in enumerate(strips):
            for c, key in enumerate(order):
                im = s[key]
                sheet_img.alpha_composite(im, (c * w + (w - im.size[0]) // 2, r * h + h - im.size[1]))
        sheet_img.save(preview)
        print("preview:", preview)


if __name__ == "__main__":
    main(sys.argv[1:])
