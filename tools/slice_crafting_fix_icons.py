#!/usr/bin/env python3
"""Slice Kyle's two crafting-icon fix sheets (docs/crafting_icon_fix_prompts.md) into assets/gathering_nodes/, 32x32.
Idempotent.

    PYTHONPATH=. python3 tools/slice_crafting_fix_icons.py

Sheet 1 (7x4) redraws the ten gathering icons whose old slices caught half a neighbour (iron ore, Duskwood, the
Ebonthorn stump and the rest) and fills the blank shafts, fibres, pages, oils, Arcanite bar and the marbled cut.
Sheet 2 (6x3) is the sixteen metal upgrade kits and the last two meat cuts. Kyle delivered both on 17 Nov 2026.

The key is #FF00FF. Icons are found as whole objects on the sheet and assigned to the nearest grid slot (the
generator drifts off its cells), the same way tools/slice_auction_icons.py does it. Slot 21 on sheet 1 is the
prompt's spare (a bow stave) and has no item, so it isn't installed.
"""
from pathlib import Path

from PIL import Image

import numpy as np
from scipy import ndimage as ndi

from tools.slice_mob_reagents import key

ROOT = Path(__file__).resolve().parent.parent
GN = "assets/gathering_nodes/"
SIZE = 32

SHEET1 = (ROOT / "tools/icon_sheets/crafting_fix_sheet1.png", 7, 4, [
    "ore/iron", "ore/cataclysmic", "wood/bramblewood", "wood/goldenleaf_tree", "wood/duskwood_stump",
    "wood/ebonthorn_stump", "wood/sylvanheart_tree",
    "wood/worldtree_heartwood_stump", "wood/genesis_bough_tree", "wood/cataclysm_root_stump", "bars/arcanite",
    "reagents/oil_blackmouth", "reagents/oil_fire", "reagents/oil_stonescale",
    "sticks/stick_green", "sticks/stick_seasoned", "sticks/stick_hardened", "sticks/stick_lacquered",
    "sticks/stick_banded", "sticks/stick_ironbound", None,
    "fibers/fiber_braided", "fibers/fiber_corded", "fibers/fiber_warded", "pages/pages_vellum", "pages/pages_leafed",
    "pages/pages_gilded", "meat/meat_marbled",
])
SHEET2 = (ROOT / "tools/icon_sheets/crafting_fix_sheet2.png", 6, 3, [
    *[f"upgrade_kits/upgrade_kit_{m}" for m in (
        "weakstone", "tin", "bronze_vein", "living_copper", "frostveined_tin", "verdant_iron",
        "felslag", "bloodiron", "deepearth", "dark_iron", "truesilver", "thorium",
        "ashen_steel", "arcanite", "elementium", "mithril")],
    "meat/meat_aged", "meat/meat_select",
])


def objects(sheet, cols, rows):
    """Bounding boxes of the icons, keyed by grid slot (col, row). A light dilation only: these icons stand
    close (the Goldenleaf's crown nearly reaches the Duskwood stump), and the auction slicer's wider one fused them."""
    a = np.asarray(sheet, np.float32)
    solid = (np.minimum(a[..., 0], a[..., 2]) - a[..., 1]) < 150
    lab, _n = ndi.label(ndi.binary_dilation(solid, iterations=3))
    W, H = sheet.size
    out = {}
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if int((solid[sl] & (lab[sl] == i)).sum()) < 300:
            continue
        cy, cx = (sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2
        slot = (int(cx / (W / cols)), int(cy / (H / rows)))
        box = (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        if slot in out:                       # two pieces of one icon: merge them
            b = out[slot]
            box = (min(b[0], box[0]), min(b[1], box[1]), max(b[2], box[2]), max(b[3], box[3]))
        out[slot] = box
    return out


def slice_sheet(path, cols, rows, ids):
    sheet = Image.open(path).convert("RGB")
    W, H = sheet.size
    boxes = objects(sheet, cols, rows)
    n = 0
    for i, iid in enumerate(ids):
        if iid is None:
            continue
        c, r = i % cols, i // cols
        if (c, r) not in boxes:
            raise SystemExit(f"{iid}: nothing found in slot {c},{r} of {path.name}")
        x0, y0, x1, y1 = boxes[(c, r)]
        pad = 6
        im = key(sheet.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))))
        bbox = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        if not bbox:
            raise SystemExit(f"{iid}: empty slot {c},{r}")
        im = im.crop(bbox)
        side = int(max(im.size) * 1.06) + 2
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
        out = ROOT / GN / f"{iid}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        sq.resize((SIZE, SIZE), Image.LANCZOS).save(out)
        n += 1
    return n


def main():
    n = sum(slice_sheet(*s) for s in (SHEET1, SHEET2))
    print(f"{n} crafting icons -> {GN}")


if __name__ == "__main__":
    main()
