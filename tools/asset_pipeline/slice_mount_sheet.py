#!/usr/bin/env python3
"""Slice a mount sprite sheet into assets/mounts/<id>_<facing>.png.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_mount_sheet.py SHEET.png \
        mire_hopper crag_lizard carrion_horse rune_saber plaguebone_charger veinlit_strider
    ...add --dry-run to see what it would write without writing it.

The sheet is 6 columns x 4 rows: columns are mounts, rows are facings in the order the prompt in
claude/mount_art_prompts.md asks for - down, left, right, up.

IT FINDS THE SPRITES RATHER THAN TRUSTING THE GRID, which is the whole reason this file exists
instead of a generic 6x4 slicer. On the first real sheet, 17 of the 24 nominal cells had artwork
touching or crossing their grid boundary - a lizard's tail and a horse's muzzle do not respect a
line the generator never drew. Cutting on the arithmetic would have clipped most of the sheet.
Connected components of the non-magenta pixels give the real bounding boxes, and on that sheet
there were exactly 24 of them, cleanly six to a row.

MAGENTA IS KEYED WITH A HALO PASS. A hard threshold leaves a one-or-two-pixel magenta rind around
every sprite, which reads as a pink outline against the game's dark tiles. Pixels that are
partially magenta have that contribution removed and their alpha reduced, so the edge stays soft
without staying pink.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "assets" / "mounts"

#: Row order. Matches the prompt, and the four names the first six mounts already use on disk.
FACINGS = ["down", "left", "right", "up"]

COLS, ROWS = 6, 4
PAD = 3                 # transparent breathing room around each crop
MIN_BLOB = 3000         # px; below this is keying noise, not an animal


def _masks(rgb):
    """(is_background, magenta_strength 0..1) for the magenta key."""
    r, g, b = rgb[..., 0].astype(float), rgb[..., 1].astype(float), rgb[..., 2].astype(float)
    # Magenta is high red AND high blue with low green. Strength is how far green has been
    # pushed down relative to the red/blue level, which is what a soft anti-aliased edge looks
    # like when it is half background.
    level = np.minimum(r, b)
    strength = np.clip((level - g) / 255.0, 0, 1)
    hard = (r > 200) & (b > 200) & (g < 90)
    return hard, strength


def _key(rgb, hard, strength):
    """RGBA with magenta removed, including the halo."""
    h, w, _ = rgb.shape
    out = np.zeros((h, w, 4), np.uint8)
    alpha = np.where(hard, 0.0, 1.0 - 0.85 * strength)     # partial magenta -> partial alpha
    col = rgb.astype(float).copy()
    # Pull the magenta contribution back out of the surviving pixels: lift green toward the
    # red/blue level in proportion to how contaminated the pixel was.
    lift = strength * (np.minimum(col[..., 0], col[..., 2]) - col[..., 1])
    col[..., 1] = np.clip(col[..., 1] + lift * 0.85, 0, 255)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1 + COLS:
        raise SystemExit(f"usage: slice_mount_sheet.py SHEET.png <{COLS} mount ids, left to right>")
    sheet, ids = Path(args[0]), args[1:]
    if not sheet.exists():
        raise SystemExit(f"no sheet at {sheet}")

    rgb = np.array(Image.open(sheet).convert("RGB"))
    hard, strength = _masks(rgb)
    content = ~hard

    # close small gaps (a thin tail, a gap between legs) so one animal is one blob
    lab, n = ndimage.label(ndimage.binary_closing(content, structure=np.ones((9, 9))))
    sizes = ndimage.sum(content, lab, range(1, n + 1))
    blobs = [i + 1 for i in range(n) if sizes[i] >= MIN_BLOB]
    if len(blobs) != COLS * ROWS:
        raise SystemExit(
            f"found {len(blobs)} sprites, expected {COLS * ROWS}. Either two animals are touching "
            f"(raise the closing structure) or one is split (lower MIN_BLOB, currently "
            f"{MIN_BLOB}). Sizes: {sorted(sizes, reverse=True)[:30]}")

    boxes = []
    for i in blobs:
        ys, xs = np.where(lab == i)
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), i))
    boxes.sort(key=lambda bx: (bx[1] + bx[3]) / 2)              # into rows by vertical centre
    keyed = _key(rgb, hard, strength)
    H, W, _ = rgb.shape
    wrote = []
    for ri in range(ROWS):
        row = sorted(boxes[ri * COLS:(ri + 1) * COLS], key=lambda bx: (bx[0] + bx[2]) / 2)
        for ci, (x0, y0, x1, y1, blob) in enumerate(row):
            x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
            x1, y1 = min(W - 1, x1 + PAD), min(H - 1, y1 + PAD)
            # MASK TO THIS SPRITE, not just to its rectangle. Two sprites can have overlapping
            # bounding boxes without touching - a lizard's tail reaches into the box around the
            # horse beside it - and cropping the rectangle alone carried that tail tip into
            # carrion_horse_left as a fragment floating in mid-air. Dilated by one so the
            # anti-aliased rim of the real sprite survives the cut.
            mine = ndimage.binary_dilation(lab[y0:y1 + 1, x0:x1 + 1] == blob,
                                           structure=np.ones((3, 3)))
            cut = keyed[y0:y1 + 1, x0:x1 + 1].copy()
            cut[..., 3] = np.where(mine, cut[..., 3], 0)
            img = Image.fromarray(cut, "RGBA")
            dst = OUT / f"{ids[ci]}_{FACINGS[ri]}.png"
            wrote.append((dst, img.size))
            if not dry:
                OUT.mkdir(parents=True, exist_ok=True)
                img.save(dst)

    for dst, size in wrote:
        print(f"  {'would write' if dry else 'wrote'} {dst.relative_to(ROOT)}  {size[0]}x{size[1]}")
    print(f"\n{len(wrote)} sprites{' (dry run)' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
