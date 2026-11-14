#!/usr/bin/env python3
"""Slice Kyle's two 5x5 gemstone sheets into the 50 gem icons.

    python3 tools/slice_gem_sheets.py

Sheet 1 (tools/icon_sheets/gems_sheet1.png) is the 25 lower-skill stones, sheet 2 the 25
high-skill ones. Cell order is the order in claude/gem_icon_prompts.md, which is generated
from tools/build_gems.py - gems sorted by their ore's mining skill, then by id - and is
rebuilt here the same way, so the two cannot drift.

Uses slice_icon_sheet's keying and blob-finding (the sheets came back 1254x1254, not the
960x960 asked for; icons are found as blobs, so the size does not matter).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import slice_icon_sheet as S  # noqa: E402
from build_gems import GEMS   # noqa: E402

OUT = ROOT / "assets" / "gathering_nodes" / "gems"


def cell_order():
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))
    mats = mats.get("materials", mats)
    order = sorted(GEMS, key=lambda g: (mats[g[2]]["skill_range"][0], g[0]))
    return [g[0][4:] for g in order]            # icon ids: the gem id without "gem_"


def main():
    names = cell_order()
    S.COLS, S.ROWS, S.OUT_SIZE = 5, 5, 64
    total = 0
    for n, chunk in ((1, names[:25]), (2, names[25:])):
        S.NAMES[f"gems{n}"] = ("gems", chunk)
        sheet = ROOT / "tools" / "icon_sheets" / f"gems_sheet{n}.png"
        total += S.slice_sheet(f"gems{n}", sheet, out_dir=OUT) or 0
    print(f"{len(list(OUT.glob('*.png')))} gem icons in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
