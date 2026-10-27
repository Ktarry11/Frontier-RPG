#!/usr/bin/env python3
"""
Recolour the generic blood elf buildings into Kael's Bastion's arcane variants.

    python3 tools/hue_shift_buildings.py                      # writes bud_* beside the be_* originals
    python3 tools/hue_shift_buildings.py --preview OUT.png    # side-by-side before/after contact sheet

Kael's Bastion is a blood elf holdfast lit by arcane crystal instead of sunlight, so its buildings are the SAME
architecture under different light. Rather than generate a second 30-building sheet, the `be_*` sprites are
recoloured here and written as `bud_*`; the originals stay untouched for Silvermoon, the Ghostlands and Eversong.

WHY A FLAT HUE ROTATION IS WRONG. The source palette has two distinct families doing two different jobs - crimson
roofing (hue ~0) and gold trim (hue ~45) - and one global rotation cannot serve both. Rotating crimson to violet
(+265 degrees) drags the gold to magenta-pink, which is both ugly and the one colour the magenta key cannot
tolerate anywhere near the art. So the hue map is PIECEWISE: the reds swing a long way to violet, the golds swing
a short way to pale blue-silver and lose most of their saturation, and the near-neutral cream stone is left
almost alone so the masonry still reads as masonry.

Luminance is never touched. Every highlight, shadow and edge the painter put in survives exactly, which is the
whole reason this works at all.
"""
import argparse
import colorsys
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BLD = ROOT / "assets" / "buildings"

sys.path.insert(0, str(ROOT / "tools"))
from slice_building_sheet import SETS  # noqa: E402

#: (hue band in degrees, target hue, saturation multiplier). Bands are matched in order; the first hit wins.
#: Hue is 0-360 with red at 0, gold ~45, cyan ~180, violet ~270.
BANDS = [
    # crimson roofing and banners -> deep arcane violet, kept saturated so the roofs still carry the building
    ((335, 360), 268, 1.00),
    ((0, 25), 268, 1.00),
    # gold trim, finials and filigree -> pale blue-silver. Desaturated hard: gold's job is "precious metal
    # catching light", and under crystal light that reads as silver, not as blue paint.
    ((25, 70), 205, 0.34),
    # cream-gold stone is nearly neutral already - a light touch keeps it stone instead of tinting it candy
    ((70, 110), 215, 0.55),
    # the arcane glass that was already blue/violet stays where it is
    ((180, 300), None, 1.15),
]
DEFAULT_HUE, DEFAULT_SAT = 250, 0.8


def _remap(h_deg, s):
    for (lo, hi), target, smul in BANDS:
        if lo <= h_deg < hi:
            return (h_deg if target is None else target), min(1.0, s * smul)
    return DEFAULT_HUE, min(1.0, s * DEFAULT_SAT)


_VEC = None


def _lut():
    """256x256 lookup over (hue, sat) so 30 sprites recolour in well under a second."""
    global _VEC
    if _VEC is None:
        out = np.zeros((256, 256, 2), np.float32)
        for hi in range(256):
            for si in range(256):
                h, s = _remap(hi * 360.0 / 256.0, si / 255.0)
                out[hi, si] = (h / 360.0, s)
        _VEC = out
    return _VEC


def shift(img):
    a = np.asarray(img.convert("RGBA")).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3]
    mx, mn = rgb.max(2), rgb.min(2)
    v = mx
    d = mx - mn
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    # hue, the usual six-sector form
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(v)
    nz = d > 1e-6
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm = nz & (mx == b) & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = ((b - r)[gm] / d[gm]) + 2
    h[bm] = ((r - g)[bm] / d[bm]) + 4
    h = h / 6.0

    lut = _lut()
    hi = np.clip((h * 255).astype(np.int32), 0, 255)
    si = np.clip((s * 255).astype(np.int32), 0, 255)
    h2 = lut[hi, si, 0]
    s2 = lut[hi, si, 1]

    # back to rgb, V untouched so every highlight and shadow survives
    i = np.floor(h2 * 6.0)
    f = h2 * 6.0 - i
    p, q, t = v * (1 - s2), v * (1 - s2 * f), v * (1 - s2 * (1 - f))
    i = i.astype(np.int32) % 6
    ii = i[..., None]            # conditions must broadcast across the 3 colour channels, not just the plane
    out = np.select(
        [ii == 0, ii == 1, ii == 2, ii == 3, ii == 4, ii == 5],
        [np.stack([v, t, p], -1), np.stack([q, v, p], -1), np.stack([p, v, t], -1),
         np.stack([p, q, v], -1), np.stack([t, p, v], -1), np.stack([v, p, q], -1)])
    out = np.concatenate([out, alpha[..., None]], -1)
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8), "RGBA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    args = ap.parse_args()

    names = SETS["blood_elf"][3]
    done = []
    for n in names:
        src = BLD / f"{n}.png"
        if not src.exists():
            print(f"  !! missing {n}.png")
            continue
        im = Image.open(src)
        out = shift(im)
        out.save(BLD / f"bud_{n[3:]}.png")
        done.append((n, im, out))
    print(f"{len(done)}/{len(names)} recoloured -> {BLD}/bud_*.png")

    if args.preview and done:
        cols = 6
        cw = max(max(i.width, o.width) for _, i, o in done) + 12
        rh = max(max(i.height, o.height) for _, i, o in done) + 12
        rows = (len(done) + cols - 1) // cols
        sheet = Image.new("RGBA", (cols * cw, rows * 2 * rh), (108, 108, 114, 255))
        for k, (n, i, o) in enumerate(done):
            r, c = divmod(k, cols)
            for j, img in enumerate((i, o)):
                y = (r * 2 + j) * rh
                sheet.alpha_composite(img.convert("RGBA"),
                                      (c * cw + (cw - img.width) // 2, y + (rh - img.height) - 6))
        sheet.convert("RGB").save(args.preview)
        print(f"before/after preview -> {args.preview}")


if __name__ == "__main__":
    main()
