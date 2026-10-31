#!/usr/bin/env python3
"""Generate higher-tier reskins of every vendor trash icon. Idempotent.

    PYTHONPATH=. python3 tools/reskin_vendor_trash_icons.py [--force]

Kyle: "just reskin trash icons to higher tier versions. If we have 30 icons....reskin them like
2 or 3 times so we go to 120. Easy."

He is right and I had the wrong number in my head: I costed a recolour as one variant per TIER
(80 icons x 9 tiers = 720 files, which is why I argued against it) when what the game needs is a
handful of ART BANDS. Three bands off 80 base icons is 240 files and no hand art at all.

  base   levels 1-29    the existing file, untouched
  _t2    levels 30-43   the same object, in better condition
  _t3    levels 44+     the same object, clearly worth money

WHAT MAKES A RESKIN READ AS "THE GOOD VERSION" IS NOT HUE. Rotating hue turns a pelt green and
reads as a different animal, not a better pelt. What reads as quality at 96px is: more saturated
and contrastier material, lifted highlights, a slight metal-tint, and above all AN OUTER RIM GLOW,
which is the single clearest "this one is valuable" signal in an inventory grid and the thing WoW
leans on for item quality. So each band is:

    saturation x S, contrast x C, a weak tint blend toward a band colour, and a rim glow of that
    colour composited UNDERNEATH the object so the silhouette stays crisp.

The glow goes under, not over, deliberately: over the top it fogs the artwork and every icon
starts to look like the same blob of light.

Bands are defined once in BANDS and the rest is mechanical, so a new base icon dropped into
assets/icons/vendor_trash/ gets its tiers on the next run.
"""
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

ICON_DIR = ROOT / "assets" / "icons" / "vendor_trash"

#: suffix -> (saturation, contrast, tint rgb, tint strength, glow rgb, glow strength, glow spread)
#: t2 is bronze/brass - the object cared for. t3 is pale gold with a cool arcane edge, which is
#: also the palette of the 44+ zones it drops in (Glittervein crystal, the Cistern).
BANDS = {
    "_t2": dict(sat=1.28, con=1.14, tint=(214, 168, 104), tint_k=0.13,
                glow=(236, 184, 96), glow_k=0.55, spread=2.0),
    # tint_k stays LOW here on purpose. At 0.20 the gold swamped the material - a demon horn came
    # out gold, a purple thing stopped being purple - and an icon that loses its own colour stops
    # being recognisable at a glance in a full bag. The rim glow carries the "valuable" signal;
    # the tint is only there to warm the highlights.
    "_t3": dict(sat=1.55, con=1.30, tint=(236, 214, 150), tint_k=0.10,
                glow=(150, 224, 255), glow_k=1.05, spread=3.6),
}

#: a file already ending in a band suffix is OUTPUT, never input - otherwise a second run reskins
#: the reskins and the art drifts a little further from the base every time it is re-run.
SUFFIXES = tuple(BANDS)


def _check_bands_match_data():
    """The engine maps level -> suffix from data/items/vendor_trash.json; we must reskin exactly
    those suffixes. If the two lists ever disagree the game asks for art that was never made."""
    import json
    want = {b["suffix"] for b in json.loads(
        (ROOT / "data/items/vendor_trash.json").read_text(encoding="utf-8")
    ).get("icon_bands", []) if b["suffix"]}
    if want and want != set(BANDS):
        raise SystemExit(f"icon_bands in vendor_trash.json wants {sorted(want)} but this tool "
                         f"makes {sorted(BANDS)}. Make them agree rather than dropping the check.")


def _adjust(rgb, a, b):
    """Saturation, contrast and tint, applied only where the icon is opaque."""
    m = a > 0
    out = rgb.astype(np.float32).copy()
    px = out[m]
    if not len(px):
        return out.astype(np.uint8)

    lum = px @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    px = lum[:, None] + (px - lum[:, None]) * b["sat"]            # saturation about luminance
    px = 128.0 + (px - 128.0) * b["con"]                          # contrast about mid grey
    px = px * (1.0 - b["tint_k"]) + np.array(b["tint"], np.float32) * b["tint_k"]
    out[m] = np.clip(px, 0, 255)
    return out.astype(np.uint8)


def _glow(a, b):
    """An alpha mask of light OUTSIDE the silhouette: blur the shape, then cut the shape back out."""
    soft = Image.fromarray(a).filter(ImageFilter.GaussianBlur(b["spread"]))
    g = np.array(soft, np.float32) * b["glow_k"]
    g = np.clip(g - a.astype(np.float32), 0, 255)   # outside only; keeps the edge crisp
    return g.astype(np.uint8)


def reskin(src: Path, suffix: str, b: dict) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    arr = np.array(im)
    rgb, a = arr[..., :3], arr[..., 3]

    body = np.dstack([_adjust(rgb, a, b), a])
    ga = _glow(a, b)
    halo = np.dstack([np.broadcast_to(np.array(b["glow"], np.uint8), rgb.shape).copy(), ga])

    out = Image.alpha_composite(Image.fromarray(halo, "RGBA"),      # glow underneath
                                Image.fromarray(body, "RGBA"))      # object on top
    return out


def main():
    force = "--force" in sys.argv
    _check_bands_match_data()
    if not ICON_DIR.is_dir():
        raise SystemExit(f"no icon directory at {ICON_DIR}")

    bases = sorted(p for p in ICON_DIR.glob("*.png") if not p.stem.endswith(SUFFIXES))
    if not bases:
        raise SystemExit(f"no base icons in {ICON_DIR} - nothing to reskin.")

    made = skipped = 0
    for src in bases:
        for suffix, b in BANDS.items():
            dst = src.with_name(f"{src.stem}{suffix}.png")
            if dst.exists() and not force:
                skipped += 1
                continue
            reskin(src, suffix, b).save(dst)
            made += 1

    total = len(list(ICON_DIR.glob("*.png")))
    print(f"{len(bases)} base icons x {len(BANDS)} bands: {made} written, {skipped} already there")
    print(f"assets/icons/vendor_trash now holds {total} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
