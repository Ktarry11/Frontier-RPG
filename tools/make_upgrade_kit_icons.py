#!/usr/bin/env python3
"""Recolour an existing upgrade-kit icon into the tier icons that have no art.

    PYTHONPATH=. python3 tools/make_upgrade_kit_icons.py [--dry-run]

Kyle: "You can recolor icons as needed."

Seven material tiers ship armour and weapon recipes but have no upgrade kit, so none of that
gear can ever be upgraded - 47 of validate_content's failures are exactly this. The kits need
icons and nobody has drawn them.

THIS IS A DIFFERENT JOB FROM reskin_vendor_trash_icons.py AND USES A DIFFERENT RULE. That one
makes the SAME object look more valuable, so it leans on saturation and an outer rim glow,
which is what reads as quality in an inventory grid. These are not quality tiers - a Stormscale
kit is not a better Cragscale kit, it is a different material - so the signal has to be the
MATERIAL, and that means hue. The rim glow is deliberately absent: put it on all seven and they
read as seven legendaries rather than seven leathers.

Each tier therefore gets a strong tint toward its own colour, a mild saturation lift so the
tint does not read as a grey wash, and nothing else. Luminance is preserved, so the base art's
shading, stitching and highlights survive and the kit still reads as the same kind of object.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "gathering_nodes" / "upgrade_kits"

#: tier -> (base icon to recolour, tint rgb, tint strength, saturation)
#: Bases are chosen by MATERIAL: a leather tier recolours a leather kit, a cloth tier recolours
#: a cloth kit, so the object in the icon stays the right kind of thing.
TIERS = {
    # ---- leatherworking -------------------------------------------------------------------
    # Tints are pushed FURTHER APART than the materials really are, because these are 32px
    # icons sitting in a grid: at that size a faithful "slightly warmer brown" is the same
    # icon twice. The first pass had gossamer, stonebound and thistledown all reading as one
    # pale box.
    "cragscale":   ("upgrade_kit_thick",  (150, 118,  78), 0.62, 1.10),  # dry stone-brown scale
    "stormscale":  ("upgrade_kit_thick",  ( 70, 112, 205), 0.72, 1.25),  # storm blue
    "stonebound":  ("upgrade_kit_rugged", ( 96, 100, 106), 0.72, 0.55),  # dark flat grey
    # ---- tailoring ------------------------------------------------------------------------
    "spidersilk":  ("upgrade_kit_silk",   (150, 112, 200), 0.66, 1.20),  # violet
    "dusk_velvet": ("upgrade_kit_silk",   ( 74,  48, 112), 0.78, 1.15),  # deep dusk purple
    "gossamer":    ("upgrade_kit_silk",   (150, 224, 232), 0.68, 1.05),  # cold pale cyan
    "thistledown": ("upgrade_kit_wool",   (140, 200, 124), 0.66, 1.10),  # seed-green
    # ---- older gaps, not from this pass --------------------------------------------------
    # These two were already in MATERIAL_KITS with no icon file at all, so the kit rendered as
    # a blank in the bag. Found by checking every kit had art rather than only the new ones.
    "iron":        ("upgrade_kit_rough_iron", (150, 152, 158), 0.55, 0.85),  # clean iron grey
    "resonant":    ("upgrade_kit_steel",      ( 96, 198, 206), 0.70, 1.20),  # engineering crystal
}


def recolour(src: Path, tint, k, sat) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    a = np.array(im)
    rgb, alpha = a[..., :3].astype(np.float32), a[..., 3]
    m = alpha > 0
    px = rgb[m]
    if len(px):
        lum = px @ np.array([0.299, 0.587, 0.114], np.float32)
        px = lum[:, None] + (px - lum[:, None]) * sat          # saturation about luminance
        # Tint toward the tier colour while KEEPING each pixel's own brightness, so the leather's
        # shading and stitching survive instead of flattening into a coloured blob.
        tinted = np.array(tint, np.float32)[None, :] * (lum[:, None] / 255.0 + 0.35)
        px = px * (1.0 - k) + tinted * k
        rgb[m] = np.clip(px, 0, 255)
    out = np.dstack([rgb.astype(np.uint8), alpha])
    return Image.fromarray(out, "RGBA")


def main():
    dry = "--dry-run" in sys.argv
    missing = [t for t, (b, *_rest) in TIERS.items() if not (OUT / f"{b}.png").exists()]
    if missing:
        raise SystemExit(f"base icon missing for: {missing}")
    for tier, (base, tint, k, sat) in TIERS.items():
        dst = OUT / f"upgrade_kit_{tier}.png"
        img = recolour(OUT / f"{base}.png", tint, k, sat)
        if not dry:
            img.save(dst)
        print(f"  {'would write' if dry else 'wrote'} {dst.name:34s} from {base}.png  {img.size}")
    print(f"\n{len(TIERS)} kit icons{' (dry run)' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
