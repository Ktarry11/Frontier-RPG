#!/usr/bin/env python3
"""Goggle art for engineering's goggles, one icon each.

    PYTHONPATH=. python3 tools/make_goggle_icons.py

Kyle, 16 Nov 2026: "Head piece (goggles made with leather and gems throughout the entire 1-60)", and "every unique
item in the game can only have ONE icon". The game has four pictures of goggles (a monocle, two pairs of goggles, a
goggled helm) and engineering now makes 28 goggles, so each armour type takes one picture and every level tints it
round the colour wheel: the set reads as one family, and no two pieces share a file.

Same inputs, same outputs. tools/build_crafting_expansion_nov16.py writes the ids onto the goggles.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEAR = ROOT / "assets/icons/gear"
BASES = {"cloth": "gear_inv_helmet_44", "leather": "gear_inv_helmet_47", "mail": "gear_wow_head_newgoggles",
         "plate": "gear_inv_helmet_49"}
LEVELS = (6, 15, 24, 33, 42, 51, 58)


def icon_id(atype, level):
    return f"gear_wow_head_goggles_{atype}_{level}"


def tint(img, shift):
    """Rotate the hue by `shift` (0-255), keeping alpha, light and saturation."""
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    h, s, v = rgba.convert("RGB").convert("HSV").split()
    h = h.point(lambda x: (x + shift) % 256)
    out = Image.merge("HSV", (h, s, v)).convert("RGB").convert("RGBA")
    out.putalpha(alpha)
    return out


def main():
    made = 0
    for atype, base in BASES.items():
        src = Image.open(GEAR / f"{base}.png")
        for j, lv in enumerate(LEVELS):
            dst = GEAR / f"{icon_id(atype, lv)}.png"
            tint(src, 0 if j == 0 else round(j * 256 / len(LEVELS))).save(dst)
            made += 1
    print(f"{made} goggle icons")


if __name__ == "__main__":
    main()
