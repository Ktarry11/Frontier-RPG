#!/usr/bin/env python3
"""Slice a creature sprite sheet into assets/creatures/<sprite_id>.png.

    PYTHONPATH=. python3 tools/asset_pipeline/slice_creature_sheet.py SHEET.png <sheet name> [--stage]

`sheet name` is a key of creature_sprites.SHEETS, whose list gives the ids in reading order.

--stage writes to assets/npcs_staging/<sheet>/NN.png with position numbers instead of ids, and
makes a numbered contact sheet. THAT IS THE DEFAULT WAY TO START on a sheet whose detected count
does not match the id list: the generator does not always produce the number of cells asked for,
and if one cell is missing then every id after it is wrong - a gnoll drawing as a dwarf, silently,
forever. Stage, look, write the mapping, then run for real.

Sprite detection, magenta keying and the mask-to-component rule are the same as
slice_mount_sheet.py; see that file for why each of them is needed.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import creature_sprites as CS  # noqa: E402

OUT = ROOT / "assets" / "creatures"
STAGE = ROOT / "assets" / "npcs_staging"
PAD = 3
MIN_BLOB = 2500
#: two sprites counted as one when their bounding boxes overlap by more than this much of the
#: smaller one - a raised claw reaching over a neighbour.
ROW_TOL = 0.45


def masks(rgb):
    r, g, b = rgb[..., 0].astype(float), rgb[..., 1].astype(float), rgb[..., 2].astype(float)
    level = np.minimum(r, b)
    strength = np.clip((level - g) / 255.0, 0, 1)
    hard = (r > 190) & (b > 190) & (g < 110)
    return hard, strength


def key(rgb, hard, strength):
    h, w, _ = rgb.shape
    out = np.zeros((h, w, 4), np.uint8)
    alpha = np.where(hard, 0.0, 1.0 - 0.85 * strength)
    col = rgb.astype(float).copy()
    lift = strength * (np.minimum(col[..., 0], col[..., 2]) - col[..., 1])
    col[..., 1] = np.clip(col[..., 1] + lift * 0.85, 0, 255)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(alpha * 255, 0, 255).astype(np.uint8)
    return out


def find(rgb):
    """-> [(x0, y0, x1, y1, blob_label)] in reading order."""
    hard, _ = masks(rgb)
    lab, n = ndimage.label(ndimage.binary_closing(~hard, structure=np.ones((9, 9))))
    sizes = ndimage.sum(~hard, lab, range(1, n + 1))
    boxes = []
    for i in range(n):
        if sizes[i] < MIN_BLOB:
            continue
        ys, xs = np.where(lab == i + 1)
        boxes.append([int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), i + 1])
    # group into rows by vertical overlap rather than by a fixed grid: the sheets are not
    # perfectly ruled and a row of short creatures sits higher than a row of tall ones.
    boxes.sort(key=lambda b: (b[1] + b[3]) / 2)
    rows, cur = [], []
    for b in boxes:
        if not cur:
            cur = [b]
            continue
        mid = (b[1] + b[3]) / 2
        top = min(x[1] for x in cur)
        bot = max(x[3] for x in cur)
        if top <= mid <= bot or (mid - bot) < (b[3] - b[1]) * ROW_TOL:
            cur.append(b)
        else:
            rows.append(cur)
            cur = [b]
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        out += sorted(r, key=lambda b: (b[0] + b[2]) / 2)
    return out, lab


def crop(keyed, lab, box, W, H):
    x0, y0, x1, y1, blob = box
    x0, y0 = max(0, x0 - PAD), max(0, y0 - PAD)
    x1, y1 = min(W - 1, x1 + PAD), min(H - 1, y1 + PAD)
    mine = ndimage.binary_dilation(lab[y0:y1 + 1, x0:x1 + 1] == blob, structure=np.ones((3, 3)))
    cut = keyed[y0:y1 + 1, x0:x1 + 1].copy()
    cut[..., 3] = np.where(mine, cut[..., 3], 0)
    return Image.fromarray(cut, "RGBA")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    stage = "--stage" in sys.argv
    if len(args) != 2:
        raise SystemExit("usage: slice_creature_sheet.py SHEET.png <sheet name> [--stage]")
    path, sheet = Path(args[0]), args[1]
    ids = CS.SHEETS.get(sheet)
    if ids is None:
        raise SystemExit(f"no sheet {sheet!r}; known: {sorted(CS.SHEETS)}")

    rgb = np.array(Image.open(path).convert("RGB"))
    H, W, _ = rgb.shape
    hard, strength = masks(rgb)
    keyed = key(rgb, hard, strength)
    boxes, lab = find(rgb)
    print(f"{path.name}: {len(boxes)} sprites found, id list has {len(ids)}")

    if stage:
        d = STAGE / sheet
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.png"):
            old.unlink()
        cell = 150
        cols = 6
        rowsn = -(-len(boxes) // cols)
        sheet_img = Image.new("RGBA", (cols * (cell + 10) + 10, rowsn * (cell + 26) + 10),
                              (24, 24, 30, 255))
        for i, b in enumerate(boxes):
            img = crop(keyed, lab, b, W, H)
            img.save(d / f"{i:02d}.png")
            t = img.copy()
            t.thumbnail((cell, cell))
            cx = 10 + (i % cols) * (cell + 10)
            cy = 10 + (i // cols) * (cell + 26)
            sheet_img.alpha_composite(t, (cx + (cell - t.width) // 2, cy + (cell - t.height) // 2))
        sheet_img.save(d / "_contact.png")
        print(f"  staged {len(boxes)} to {d.relative_to(ROOT)}/NN.png with _contact.png")
        return 0

    if len(boxes) != len(ids):
        raise SystemExit(
            f"REFUSING TO WRITE: {len(boxes)} sprites but {len(ids)} ids. Mapping them in order "
            f"would shift every id after the first missing cell and the wrong creature would draw "
            f"forever. Re-run with --stage, look at the contact sheet, and fix the id list.")
    OUT.mkdir(parents=True, exist_ok=True)
    for i, b in enumerate(boxes):
        crop(keyed, lab, b, W, H).save(OUT / f"{ids[i]}.png")
    print(f"  wrote {len(ids)} sprites to {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
