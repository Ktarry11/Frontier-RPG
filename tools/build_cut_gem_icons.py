#!/usr/bin/env python3
"""Cut gems get their own icons, recoloured and polished from the stone they're cut from. Idempotent.

    PYTHONPATH=. python3 tools/build_cut_gem_icons.py

Kyle, 14 Nov 2026: "make the cuts look different colours at least or change them". Every cut drew its
raw stone's icon, so a stone's three or four cuts sat in the bag as identical pictures.

Each CUT NAME has one look, the same on every stone, so a player learns it: Bold is always deep and
dark, Brilliant always bright, Delicate always pale, and so on. The look is a small hue turn (small
enough that a red-socket gem still reads red), a saturation and brightness change, more contrast (it's
been polished) and a glint in the corner. The raw stone keeps its rough, unpolished drawing.

Writes assets/gathering_nodes/gems/cut_<cut>_<stone>.png for every cut gem in data/jewelcrafting/
gems.json and points the cut's icon_id at it (tools/build_jewelcrafting.py keeps that pointer).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GEMS = ROOT / "assets/gathering_nodes/gems"

#: cut -> (hue turn in degrees, saturation x, brightness x)
LOOK = {
    "Bold": (-8, 1.30, 0.80), "Brilliant": (10, 1.05, 1.25), "Delicate": (14, 0.62, 1.18),
    "Runed": (-22, 1.15, 0.88), "Teardrop": (18, 0.85, 1.10), "Bright": (-14, 1.25, 1.15),
    "Solid": (-18, 1.20, 0.82), "Sparkling": (16, 0.80, 1.22), "Stormy": (24, 1.10, 0.95),
    "Lustrous": (8, 0.70, 1.20), "Smooth": (-10, 0.75, 1.05), "Rigid": (-20, 1.25, 0.85),
    "Gleaming": (12, 1.10, 1.20), "Quick": (22, 1.30, 1.05), "Thick": (-24, 1.20, 0.78),
    "Sovereign": (-12, 1.35, 0.90), "Shifting": (20, 1.15, 0.92), "Glowing": (14, 1.20, 1.15),
    "Royal": (-16, 1.10, 0.88), "Balanced": (6, 0.85, 1.00), "Purified": (10, 0.60, 1.25),
    "Regal": (-14, 1.15, 0.86), "Enduring": (-20, 1.05, 0.84), "Dazzling": (18, 1.25, 1.18),
    "Inscribed": (-12, 1.10, 0.92), "Potent": (16, 1.30, 1.00), "Etched": (-18, 0.90, 0.90),
    "Glinting": (12, 1.00, 1.22), "Veiled": (-22, 0.80, 0.80), "Wicked": (-24, 1.30, 0.82),
    "Fluorescent": (22, 1.35, 1.20), "Luminous": (8, 1.05, 1.28), "Prismatic": (30, 1.10, 1.12),
    # the spell-hit cuts (15 Nov 2026)
    "Great": (-6, 1.15, 1.30), "Vivid": (16, 1.40, 1.10), "Serene": (-8, 0.70, 1.25),
    "Piercing": (26, 1.20, 0.90),
}
DEFAULT = (12, 1.1, 1.05)


def _hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return h % 1.0, s, mx


def _rgb(h, s, v):
    hh = (h % 1.0) * 6.0
    i = np.floor(hh).astype(int) % 6
    f = hh - np.floor(hh)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (a, b, c) in enumerate(((v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q))):
        m = i == k
        out[..., 0][m], out[..., 1][m], out[..., 2][m] = a[m], b[m], c[m]
    return out


def cut_icon(src, cut):
    a = np.asarray(Image.open(src).convert("RGBA")).astype(np.float64) / 255.0
    rgb, al = a[..., :3], a[..., 3]
    turn, sm, vm = LOOK.get(cut, DEFAULT)
    h, s, v = _hsv(rgb)
    h = h + turn / 360.0
    s = np.clip(s * sm, 0, 1)
    v = np.clip(v * vm, 0, 1)
    v = np.clip(0.5 + (v - 0.5) * 1.18, 0, 1)          # polished: a little more contrast
    out = _rgb(h, s, v)
    # the glint: a small four-point star near the top right of the stone
    ys, xs = np.nonzero(al > 0.5)
    if len(xs):
        H, W = al.shape
        gx = int(xs.min() + 0.72 * (xs.max() - xs.min()))
        gy = int(ys.min() + 0.25 * (ys.max() - ys.min()))
        r = max(2, (xs.max() - xs.min()) // 7)
        for d in range(-r, r + 1):
            k = 1.0 - abs(d) / (r + 1)
            for (x, y) in ((gx + d, gy), (gx, gy + d)):
                if 0 <= x < W and 0 <= y < H and al[y, x] > 0.2:
                    out[y, x] = out[y, x] * (1 - k) + k
    res = np.concatenate([out, al[..., None]], -1)
    return Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8), "RGBA")


def main():
    gems = json.loads((ROOT / "data/jewelcrafting/gems.json").read_text(encoding="utf-8"))["cut_gems"]
    mp = ROOT / "data/gathering/materials.json"
    mats = json.loads(mp.read_text(encoding="utf-8"))
    made = missing = 0
    for cid, g in gems.items():
        stone = g["raw"][4:]
        src = GEMS / f"{stone}.png"
        m = mats["materials"].get(cid)
        if not src.exists() or m is None:
            missing += 1
            continue
        icon = cid[4:]           # cut_<cut>_<stone> -> <cut>_<stone>, beside the stones
        cut_icon(src, g["cut"]).save(GEMS / f"cut_{icon}.png")
        m["icon_id"] = f"cut_{icon}"
        made += 1
    mp.write_text(json.dumps(mats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{made} cut gem icons written, {missing} without a stone drawing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
