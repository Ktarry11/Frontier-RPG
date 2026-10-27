#!/usr/bin/env python3
"""Slice the 6x5 magenta-background BUILDING sheet into 30 transparent PNGs in assets/buildings/.

    python3 tools/slice_building_sheet.py tools/building_sheets/eastern_kingdoms_buildings.png
    python3 tools/slice_building_sheet.py <sheet.png> --preview /tmp/ek_buildings.png

Same magenta key as the icon sheets (tools/slice_icon_sheet.key_magenta: soft alpha ramp plus a despill pass so
dark eaves and timber edges don't come back with a pink fringe). Prompts and the cell order live in
claude/eastern_kingdoms_building_prompts.md - NAMES below is that table, and the two must stay in step.

Two things differ from slice_icon_sheet, both because these are buildings and not inventory icons:

  * no square padding and no fixed output size. An icon is a 96x96 square by contract; a building is a sprite
    placed by its bottom-centre with a declared height in tiles, so it keeps its own aspect.
  * RELATIVE SCALE IS PRESERVED. Every sprite is cropped to its own bounding box but NOT normalised, so a
    cottage stays smaller than a barn exactly as drawn. Normalising per-cell is right for a sheet of unrelated
    objects (a feather and a strongbox) and wrong here, where a cottage drawn at a cottage's size is the
    information. Same reasoning as the potion sheet's PRESERVE_SCALE.

The generated sheets are never on a perfect pixel grid - rows drift - so sprites are found as connected blobs
and assigned to whichever cell holds their centre, rather than cut on arithmetic cell boundaries.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slice_icon_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 6, 5

#: Cell order, left to right then top to bottom - the same order as the numbered list in the prompt doc.
NAMES = [
    # row 1 - the mill cluster
    "ek_watermill", "ek_mill_sluice", "ek_granary",
    "ek_millstone_shelter", "ek_apothecarium", "ek_plague_vat_platform",
    # row 2 - occupation and village
    "ek_forsaken_field_tent", "ek_forsaken_watchtower", "ek_cottage_small",
    "ek_cottage_medium", "ek_townhouse", "ek_village_inn",
    # row 3 - village services
    "ek_village_chapel", "ek_smithy_forge", "ek_stable_block",
    "ek_barn", "ek_trading_post", "ek_fishery_shed",
    # row 4 - working buildings
    "ek_boathouse", "ek_sawmill_shed", "ek_tannery",
    "ek_apiary_shelter", "ek_border_watchtower", "ek_gatehouse",
    # row 5 - military and ruin
    "ek_barracks_hall", "ek_command_tent", "ek_ruined_gatehouse",
    "ek_burnt_cottage", "ek_syndicate_house", "ek_wayshrine",
]
assert len(NAMES) == COLS * ROWS, len(NAMES)

#: A blob this big ANCHORS a cell - it is the building body. Buildings are far larger than icons, so the icon
#: slicer's 60px floor would let keying dirt anchor a cell on its own.
MIN_BLOB = 1500
#: ...but a detached chimney, banner, lantern, weathervane or wheel paddle is far SMALLER than that and must
#: still be merged into its building, so anything above plain keying noise is kept as long as its cell already
#: has an anchor. Found by testing: a 20x22 chimney left 10px clear of its roof is 440px and was being
#: silently dropped, which cost the sprite its whole top.
MIN_PART = 60


def slice_sheet(sheet_path, out_dir=None, preview=None):
    from scipy import ndimage
    out_dir = Path(out_dir) if out_dir else ROOT / "assets" / "buildings"
    out_dir.mkdir(parents=True, exist_ok=True)

    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS

    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False          # a sheet edge that is not quite magenta is not a building
    solid[:, :4] = solid[:, -4:] = False
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=4))

    cells, parts = {}, {}
    for lab in range(1, n + 1):
        m = (labels == lab) & solid
        area = m.sum()
        if area < MIN_PART:
            continue
        ys, xs = np.where(m)
        key = (int(ys.mean() // ch), int(xs.mean() // cw))
        (cells if area >= MIN_BLOB else parts).setdefault(key, []).append(m)

    problems, written = [], []
    for idx, name in enumerate(NAMES):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{name}: no building found in cell r{r} c{c}")
            continue
        # A building is one object, but chimneys, banners and wheel paddles can key as their own blobs, so
        # everything whose centre lands in the cell is merged rather than taking only the largest.
        mask = np.logical_or.reduce(blobs + parts.get((r, c), []))
        ys, xs = np.where(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        cut = rgba[y0:y1, x0:x1].copy()
        cut[..., 3] *= mask[y0:y1, x0:x1]         # drop a neighbour bleeding into this bounding box
        img = Image.fromarray(cut.astype(np.uint8), "RGBA")
        img.save(out_dir / f"{name}.png")
        written.append((name, img.size))
        n_extra = len(blobs) - 1 + len(parts.get((r, c), []))
        if n_extra:
            problems.append(f"{name}: {n_extra} detached part(s) merged in (chimney/banner?) - eyeball it")

    for (name, size) in written:
        print(f"  {name:28} {size[0]:4}x{size[1]:<4}")
    print(f"\n{len(written)}/{len(NAMES)} sliced -> {out_dir}")
    if written:
        tall = max(written, key=lambda w: w[1][1])
        short = min(written, key=lambda w: w[1][1])
        print(f"relative scale kept: tallest {tall[0]} {tall[1][1]}px, shortest {short[0]} {short[1][1]}px")
    for p in problems:
        print(f"  !! {p}")

    if preview:
        _preview(written, out_dir, preview)
    return written, problems


def _preview(written, out_dir, path):
    """One contact sheet of everything that was cut, on a mid grey so alpha fringing shows up."""
    cols = 6
    cells = [Image.open(out_dir / f"{n}.png") for (n, _) in written]
    cw = max(c.width for c in cells) + 16
    rh = max(c.height for c in cells) + 16
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * rh), (110, 110, 115, 255))
    for i, c in enumerate(cells):
        r, k = divmod(i, cols)
        sheet.alpha_composite(c, (k * cw + (cw - c.width) // 2, r * rh + (rh - c.height) - 8))
    sheet.convert("RGB").save(path)
    print(f"preview -> {path}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    slice_sheet(args[0], preview=pv)
