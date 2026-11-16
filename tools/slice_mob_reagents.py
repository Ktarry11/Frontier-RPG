#!/usr/bin/env python3
"""Slice Kyle's creature-material icon sheet (docs/mob_material_icon_prompts.md) into
assets/gathering_nodes/mob_reagents/<material id>.png, 96x96, and delete the placeholders. Idempotent.

    PYTHONPATH=. python3 tools/slice_mob_reagents.py [tools/building_sheets/mob_reagents_sheet.png]

8 columns x 6 rows, in the order the materials are listed in data/creatures/mob_materials.json (the same order
as the prompt). The key is #FF00FF. Several of these icons are honestly purple (the hex bead, the lattice
shard, the worgen fang's glow), so the magenta spill is only taken off the soft edge where the key bled in,
never off the inside of an icon.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/gathering_nodes/mob_reagents"
COLS, ROWS, SIZE = 8, 6, 96
#: glows and swirls the model painted half-transparent over the key: the key shows through as pink across the
#: whole glow, not just the edge. None of these is meant to be purple, so they're de-spilled all over.
FULL_DESPILL = {"mob_whirling_grit", "mob_grave_dust", "mob_barrow_dust", "mob_luminous_spore", "mob_veinlight_mote"}


def key(cell, full=False):
    a = np.asarray(cell.convert("RGB"), np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mag = np.minimum(r, b) - g                         # how magenta: 255 on the key, low on any real colour
    alpha = np.clip((210.0 - mag) / 90.0, 0.0, 1.0)    # solid below 120, clear above 210
    solid = alpha > 0.5
    # keep only the largest connected object and anything near it (sparks, motes), not specks
    lab, n = ndi.label(ndi.binary_dilation(solid, iterations=6))
    if n > 1:
        sizes = ndi.sum(solid, lab, range(1, n + 1))
        keep = lab == (1 + int(np.argmax(sizes)))
        alpha = alpha * keep
    # despill only the fringe: pixels within 3px of the key
    edge = (alpha > 0) if full else (ndi.binary_dilation(alpha < 0.95, iterations=3) & (alpha > 0))
    spill = np.clip(mag, 0, None) * edge
    a[..., 0] -= spill
    a[..., 2] -= spill
    rgba = np.dstack([np.clip(a, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools/building_sheets/mob_reagents_sheet.png"
    sheet = Image.open(src).convert("RGB")
    W, H = sheet.size
    ids = list(json.loads((ROOT / "data/creatures/mob_materials.json").read_text(encoding="utf-8"))["materials"])
    assert len(ids) == COLS * ROWS, len(ids)
    OUT.mkdir(parents=True, exist_ok=True)
    cw, ch = W / COLS, H / ROWS
    for i, mid in enumerate(ids):
        c, r = i % COLS, i // COLS
        cell = sheet.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))
        im = key(cell, full=mid in FULL_DESPILL)
        bbox = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        if not bbox:
            raise SystemExit(f"{mid}: empty cell {c},{r}")
        im = im.crop(bbox)
        side = int(max(im.size) * 1.08) + 2
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
        sq.resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{mid}.png")
        (OUT / f".placeholder_{mid}").unlink(missing_ok=True)
    print(f"{len(ids)} icons -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
