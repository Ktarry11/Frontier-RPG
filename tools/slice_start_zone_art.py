#!/usr/bin/env python3
"""Slice sheet SZ1 (docs/start_zone_art_prompts.md): a 2x2 of 4:3 paintings into the start zone cards.

    python3 tools/slice_start_zone_art.py tools/building_sheets/start_zones_sz1.png

Cuts the sheet into quarters (a small inset trims any seam), and saves each at 800x600 to the path its start names in
world/start_zones.py, in the sheet's order: the Valley of Trials, Deathknell, Dawnhaven, the White Expanse.
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from world.start_zones import get_start_cards  # noqa: E402

ORDER = ["valley_of_trials", "deathknell", "dawnhaven", "white_expanse"]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    sheet = Image.open(sys.argv[1]).convert("RGB")
    W, H = sheet.size
    art = {s.start_id: s.art for s in get_start_cards()}
    inset = max(2, W // 400)
    for k, sid in enumerate(ORDER):
        col, row = k % 2, k // 2
        box = (col * W // 2 + inset, row * H // 2 + inset, (col + 1) * W // 2 - inset, (row + 1) * H // 2 - inset)
        out = ROOT / art[sid]
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.crop(box).resize((800, 600), Image.LANCZOS).save(out, optimize=True)
        print(f"  {sid:18s} -> {art[sid]}")


if __name__ == "__main__":
    main()
