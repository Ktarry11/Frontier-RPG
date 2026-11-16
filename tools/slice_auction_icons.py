#!/usr/bin/env python3
"""Slice Kyle's auction and mail icon sheet (docs/auction_house_art_prompts.md, part 3) into
assets/ui/auction/icons/<id>.png, 96x96. Idempotent.

    PYTHONPATH=. python3 tools/slice_auction_icons.py [tools/building_sheets/auction_mail_icons_sheet.png]

6 columns x 4 rows in the prompt's order. The key is #FF00FF. The model didn't keep to its cells (the mailboxes
reach up across the row line), so icons are found as whole objects on the sheet and then assigned to the
nearest grid slot, rather than cut on the grid lines. The Forsaken mailbox is honestly purple, so only the soft
fringe is de-spilled there; the glass of the hourglasses and the lens show the key straight through, so those
are de-spilled all over.
"""
import sys
from pathlib import Path

from PIL import Image

from tools.slice_mob_reagents import key

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/ui/auction/icons"
COLS, ROWS, SIZE = 6, 4, 96
IDS = [
    "coin_gold", "coin_silver", "coin_copper", "coin_pile", "gavel", "bid_paddle",
    "hourglass_full", "hourglass_half", "hourglass_low", "hourglass_empty", "star", "magnifier",
    "letter_sealed", "letter_open", "parcel", "letter_coins", "letter_returned", "letter_auction",
    "mailbox_orc", "mailbox_forsaken", "mailbox_tauren", "mailbox_goblin", "mail_flag_down", "mail_flag_up",
]


FULL = {"hourglass_full", "hourglass_half", "hourglass_low", "hourglass_empty", "magnifier", "mail_flag_up"}


def objects(sheet):
    """Bounding boxes of the icons on the whole sheet, keyed by grid slot (col, row)."""
    import numpy as np
    from scipy import ndimage as ndi
    a = np.asarray(sheet, np.float32)
    mag = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]
    solid = mag < 150
    lab, n = ndi.label(ndi.binary_dilation(solid, iterations=10))
    W, H = sheet.size
    out = {}
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        area = int((solid[sl] & (lab[sl] == i)).sum())
        if area < 1500:
            continue
        cy, cx = (sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2
        slot = (int(cx / (W / COLS)), int(cy / (H / ROWS)))
        box = (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        if slot in out:                       # two pieces of one icon: merge them
            b = out[slot]
            box = (min(b[0], box[0]), min(b[1], box[1]), max(b[2], box[2]), max(b[3], box[3]))
        out[slot] = box
    return out


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools/building_sheets/auction_mail_icons_sheet.png"
    sheet = Image.open(src).convert("RGB")
    W, H = sheet.size
    OUT.mkdir(parents=True, exist_ok=True)
    boxes = objects(sheet)
    for i, iid in enumerate(IDS):
        c, r = i % COLS, i // COLS
        if (c, r) not in boxes:
            raise SystemExit(f"{iid}: nothing found in slot {c},{r}")
        x0, y0, x1, y1 = boxes[(c, r)]
        pad = 6
        cell = sheet.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)))
        im = key(cell, full=iid in FULL)
        bbox = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        if not bbox:
            raise SystemExit(f"{iid}: empty cell {c},{r}")
        im = im.crop(bbox)
        side = int(max(im.size) * 1.06) + 2
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
        sq.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{iid}.png")
    print(f"{len(IDS)} icons -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
