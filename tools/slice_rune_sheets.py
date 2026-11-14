#!/usr/bin/env python3
"""Cut Kyle's three rune sheets into icons, and tint each rank. Idempotent.

    PYTHONPATH=. python3 tools/slice_rune_sheets.py
    PYTHONPATH=. python3 tools/build_runecrafting.py     # points every rune at its own icon

Kyle's art, 14 Nov 2026 (prompts: claude/rune_icon_prompts.md), kept in
assets/gathering_nodes/runes/_sheets/:

  regular.png    36 regular runes, small rounded river-stones
  capstones.png  31 Capstones and 5 spares, tall standing stones with a bronze rim
  sheet3.png     the last 3 regular runes, 3 ink bottles, and 30 spare stones

Each sheet is a 6 x 6 grid on a transparent background; the cells are found from the alpha
channel, not assumed. The glyphs were drawn pure white so they could be recoloured (Kyle: "We can
recolor as needed"), and this does that:

  rune_<family>.png   the untinted white original, kept as the family's icon
  <rune id>.png       each rank's own icon. Regular runes take their role's colour (tank blue,
                      damage red, healing green, any violet); Capstones take their element's colour
                      (fire, frost, nature, shadow, holy, arcane) or gold. Lesser is a pale wash
                      of it, the plain rank is fuller, Greater is the full colour.

Only the glyph is tinted: bright, unsaturated pixels. The grey stone and the bronze rim keep their
colour. Spares go to runes/spare/ for runes added later.

There were three ink bottles where the prompt asked for five, so Soul and Dream share the second
bottle and Vision and Illusion the third, each tinted its own dust colour.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SHEETS = ROOT / "assets/gathering_nodes/runes/_sheets"
OUT = ROOT / "assets/gathering_nodes/runes"
SIZE = 128

ROLE_TINT = {"tank": (90, 160, 255), "damage": (255, 85, 70), "healing": (80, 235, 120), "any": (190, 120, 255)}
ELEMENT_TINT = {"fire": (255, 120, 40), "frost": (120, 210, 255), "nature": (120, 235, 90),
                "shadow": (175, 90, 255), "holy": (255, 220, 90), "arcane": (255, 110, 230)}
CAPSTONE_TINT = (255, 200, 70)
#: how much of the colour each rank takes
RANK_STRENGTH = {1: 0.45, 2: 0.75, 3: 1.0}
INK_TINT = {"strange": (240, 200, 230), "soul": (150, 230, 255), "vision": (170, 190, 255),
            "dream": (150, 255, 170), "illusion": (255, 150, 230)}


def bands(proj):
    on = proj > proj.max() * 0.05
    out, start = [], None
    for i, v in enumerate(on):
        if v and start is None:
            start = i
        if not v and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(on)))
    return [b for b in out if b[1] - b[0] > 20]


def cells(path):
    """The sheet's 36 icons as RGBA images, left to right, top to bottom."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im)[:, :, 3]
    rows, cols = bands((a > 200).sum(1)), bands((a > 200).sum(0))
    assert len(rows) == 6 and len(cols) == 6, f"{path.name}: found {len(rows)} rows, {len(cols)} columns"
    out = []
    for r0, r1 in rows:
        for c0, c1 in cols:
            pad = 6
            box = (max(0, c0 - pad), max(0, r0 - pad), min(im.width, c1 + pad), min(im.height, r1 + pad))
            out.append(square(im.crop(box)))
    return out


def square(img):
    """Drop the faint haze around the stone, centre it on a square and scale to SIZE."""
    arr = np.array(img)
    arr[:, :, 3] = np.where(arr[:, :, 3] < 40, 0, arr[:, :, 3])
    img = Image.fromarray(arr)
    bbox = img.getbbox() or (0, 0, img.width, img.height)
    img = img.crop(bbox)
    side = max(img.width, img.height)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    return canvas.resize((SIZE, SIZE), Image.LANCZOS)


def tint(img, colour, strength):
    """Colour the white glyph (bright, unsaturated pixels) and leave the stone alone."""
    arr = np.array(img).astype(np.float32)
    rgb = arr[:, :, :3]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    v = mx / 255.0
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    # the glyph is near white; the lit tops of the stones are pale grey, so the ramp starts high
    mask = np.clip((v - 0.80) / 0.12, 0, 1) * np.clip((0.22 - sat) / 0.12, 0, 1) * strength
    lum = rgb.mean(axis=2, keepdims=True) / 255.0
    target = np.array(colour, dtype=np.float32)[None, None, :] * np.clip(lum * 1.05, 0, 1)
    arr[:, :, :3] = rgb * (1 - mask[:, :, None]) + target * mask[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def capstone_tint(family):
    for el, col in ELEMENT_TINT.items():
        if family.startswith(el + "_"):
            return col
    return CAPSTONE_TINT


def main():
    from world import runes as R
    runes = R.data()["runes"]
    regular = [f for f in dict.fromkeys(r["family"] for r in runes.values() if not r["capstone"])]
    capstone = [f for f in dict.fromkeys(r["family"] for r in runes.values() if r["capstone"])]
    assert len(regular) == 39 and len(capstone) <= 36, (len(regular), len(capstone))

    reg_cells = cells(SHEETS / "regular.png")
    cap_cells = cells(SHEETS / "capstones.png")
    s3 = cells(SHEETS / "sheet3.png")
    art = dict(zip(regular[:36], reg_cells))
    art.update(zip(regular[36:], s3[:3]))
    art.update(zip(capstone, cap_cells))

    (OUT / "spare").mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(cap_cells[len(capstone):]):
        img.save(OUT / "spare" / f"capstone_spare_{i + 1}.png")
    for i, img in enumerate(s3[6:]):
        img.save(OUT / "spare" / f"rune_spare_{i + 1}.png")

    for family, img in art.items():
        img.save(OUT / f"rune_{family}.png")
    made = 0
    for rid, rn in runes.items():
        colour = capstone_tint(rn["family"]) if rn["capstone"] else ROLE_TINT[rn.get("role", "any")]
        tint(art[rn["family"]], colour, RANK_STRENGTH[rn["rank"]]).save(OUT / f"{rid}.png")
        made += 1

    bottles = s3[3:6]
    for ink, bottle in (("strange", 0), ("soul", 1), ("vision", 2), ("dream", 1), ("illusion", 2)):
        tint(bottles[bottle], INK_TINT[ink], 0.8).save(OUT / f"rune_ink_{ink}.png")
    print(f"{len(art)} families, {made} rank icons, 5 inks, "
          f"{len(cap_cells) - len(capstone)} + {len(s3) - 6} spares")
    return 0


if __name__ == "__main__":
    sys.exit(main())
