#!/usr/bin/env python3
"""Slice Kyle's heroic sheet HB1 (docs/heroic_art_prompts.md, 21 Nov 2026) into the game's icon folders.

    python3 tools/slice_heroic_icons.py tools/building_sheets/heroic_hb1_icons.png

Six by six square icons on magenta. Each cell's square is found as the bounding box of its non-magenta pixels (the
generator never lands on an exact grid), trimmed two pixels inside its frame so no magenta fringe survives, and saved
opaque at the size its folder uses: gear icons 60 px, UI icons 64 px, the Frontier Mark 32 px as a material (with a
64 px copy for the vendor's price line).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEAR = "assets/icons/gear/"
UI = "assets/icons/ui/"

#: in sheet order: (output path, size)
NAMES = [
    ("assets/gathering_nodes/reagents/frontier_mark.png", 32), (UI + "heroic_emblem.png", 64),
    (UI + "vendor_tab_cloth.png", 64), (UI + "vendor_tab_leather.png", 64), (UI + "vendor_tab_mail.png", 64),
    (UI + "vendor_tab_plate.png", 64),
    (UI + "vendor_tab_jewelry.png", 64), (UI + "vendor_tab_main_hand.png", 64), (UI + "vendor_tab_off_hand.png", 64),
    (UI + "vendor_tab_ranged.png", 64),
] + [(f"{GEAR}hb_{k}.png", 60) for k in (
    "exarch", "echo_of_the_queen", "rivendare", "victor_hale", "gandling", "wounds_heart", "dathrohan", "warheart",
    "xavras", "caldera", "ahnthera", "morrun", "zargothrax", "resonance", "grebble_vask", "tarpot", "whitemane",
    "the_index", "vektar", "herod", "doan", "falconcrest", "zulketh", "razorflank", "thalnos", "lord_nightmare")]
assert len(NAMES) == 36, len(NAMES)
#: the mark's larger copy, for the price line and the tab row
MARK_UI = (UI + "frontier_mark.png", 64)


def main(sheet):
    im = Image.open(sheet).convert("RGB")
    a = np.asarray(im).astype(int)
    mag = (a[..., 0] > 200) & (a[..., 1] < 90) & (a[..., 2] > 200)
    H, W = mag.shape
    cw, ch = W / 6, H / 6
    for i, (out, size) in enumerate(NAMES):
        r, c = divmod(i, 6)
        x0, y0, x1, y1 = int(c * cw), int(r * ch), int((c + 1) * cw), int((r + 1) * ch)
        # the square is the cell's biggest connected patch of not-magenta (stray specks round it don't count), and
        # the crop steps three pixels inside its frame so no magenta fringe is left
        from scipy import ndimage
        lab, n = ndimage.label(~mag[y0:y1, x0:x1])
        biggest = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))))
        ys, xs = np.where(lab == biggest)
        crop = im.crop((x0 + xs.min() + 3, y0 + ys.min() + 3, x0 + xs.max() - 2, y0 + ys.max() - 2))
        side = min(crop.size)
        crop = crop.crop(((crop.width - side) // 2, (crop.height - side) // 2,
                          (crop.width - side) // 2 + side, (crop.height - side) // 2 + side))
        path = ROOT / out
        path.parent.mkdir(parents=True, exist_ok=True)
        crop.resize((size, size), Image.LANCZOS).save(path)
        if i == 0:
            crop.resize((MARK_UI[1], MARK_UI[1]), Image.LANCZOS).save(ROOT / MARK_UI[0])
        print(f"  {out}  {crop.size[0]}px -> {size}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "tools/building_sheets/heroic_hb1_icons.png"))
