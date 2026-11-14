#!/usr/bin/env python3
"""Tint the neutral elemental vendor-trash icons into per-element variants (vt_core -> vt_core_fire, ...).

Run after tools/slice_icon_sheet.py:   python3 tools/build_trash_element_icons.py
Which variants exist comes from data/items/vendor_trash.json (an entry with "element": true and optionally an
"elements" list).  The item code looks for assets/icons/vendor_trash/<icon>_<element>.png and falls back to no icon.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "assets" / "icons" / "vendor_trash"

# element -> (hue 0-360, saturation, brightness multiplier)
TINTS = {
    "fire": (22, 0.85, 1.05),
    "water": (208, 0.75, 1.00),
    "earth": (32, 0.38, 0.90),
    "air": (185, 0.28, 1.10),
    "ice": (195, 0.50, 1.12),
    "nature": (115, 0.65, 1.00),
    "shadow": (270, 0.50, 0.72),
    "arcane": (255, 0.70, 1.05),
}
# These bases already glow orange on their own: the fire variant is just the original art.
KEEP_ORIGINAL_FOR_FIRE = {"vt_slag", "vt_ash"}


def tint(img, hue, sat, vmul):
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    hsv = np.asarray(rgba.convert("RGB").convert("HSV")).astype(np.float64)
    v = hsv[..., 2] / 255.0
    s = sat * (1.0 - 0.55 * v ** 4)          # keep the bright glow paler than the body
    hsv[..., 0] = hue / 360.0 * 255.0
    hsv[..., 1] = np.clip(s, 0, 1) * 255.0
    hsv[..., 2] = np.clip(v * vmul, 0, 1) * 255.0
    out = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB").convert("RGBA")
    out.putalpha(alpha)
    return out


def main():
    cfg = json.loads((ROOT / "data" / "items" / "vendor_trash.json").read_text(encoding="utf-8"))
    made = 0
    for fam in cfg["families"].values():
        for entry in fam:
            if not entry.get("element"):
                continue
            base = ICON_DIR / f"{entry['icon']}.png"
            if not base.exists():
                print("missing base", base)
                continue
            img = Image.open(base)
            for el in entry.get("elements", list(cfg["elements"])):
                if el == "fire" and entry["icon"] in KEEP_ORIGINAL_FOR_FIRE:
                    out = img.copy()
                else:
                    out = tint(img, *TINTS[el])
                out.save(ICON_DIR / f"{entry['icon']}_{el}.png")
                made += 1
    print("wrote", made, "element variants")


if __name__ == "__main__":
    main()
