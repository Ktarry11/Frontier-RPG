#!/usr/bin/env python3
"""Labelled contact sheets of talent icons, for reviewing them by eye.

    python3 tools/talent_icon_sheet.py dupes          # only the reused icons
    python3 tools/talent_icon_sheet.py class mage     # one class, all specs
    python3 tools/talent_icon_sheet.py all            # every class, one sheet each

Whether a talent's icon MATCHES what the talent does cannot be checked
automatically - it needs eyes on it next to the talent's name. This renders
that: icon, talent name, and spec, big enough to judge.

Duplicates are the one part that IS machine-detectable and worth looking at
first: two different talents sharing a byte-identical image means at least one
of them is wrong, since no two talents should illustrate the same idea.
"""
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons" / "talents"
OUT = ROOT / "tools" / "icon_sheets"
FONT = "/home/claude/frontier-rpg/assets/fonts/Lora-Regular.ttf"
BOLD = "/home/claude/frontier-rpg/assets/fonts/Lora-Bold.ttf"

CELL = 64          # icon draw size
PAD = 14
COL_W = 300        # icon + label
ROW_H = CELL + 22
COLS = 4


def load_talents():
    """-> {talent_id: (class, spec, name, description)}"""
    out = {}
    for f in sorted((ROOT / "data" / "talents").glob("*.json")):
        stem = f.stem
        cls = stem.split("_")[0]
        spec = stem[len(cls) + 1:] or stem
        d = json.loads(f.read_text(encoding="utf-8"))
        for n in d.get("nodes", []):
            out[n["talent_id"]] = (cls, spec, n.get("name", "?"), n.get("description", ""))
    return out


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def draw_sheet(entries, title, path):
    """entries = [(talent_id, label_top, label_bottom)]"""
    rows = (len(entries) + COLS - 1) // COLS
    W = COLS * COL_W + PAD
    H = rows * ROW_H + 70
    img = Image.new("RGBA", (W, H), (20, 19, 25, 255))
    d = ImageDraw.Draw(img)
    try:
        f_title = ImageFont.truetype(BOLD, 24)
        f_name = ImageFont.truetype(BOLD, 14)
        f_sub = ImageFont.truetype(FONT, 11)
    except Exception:
        f_title = f_name = f_sub = ImageFont.load_default()

    d.text((PAD, 18), title, font=f_title, fill=(236, 214, 158))

    for i, (tid, top, bottom) in enumerate(entries):
        c, r = i % COLS, i // COLS
        x = PAD + c * COL_W
        y = 60 + r * ROW_H
        p = ICONS / f"{tid}.png"
        if p.exists():
            try:
                ic = Image.open(p).convert("RGBA").resize((CELL, CELL), Image.LANCZOS)
                img.alpha_composite(ic, (x, y))
            except Exception:
                d.rectangle([x, y, x + CELL, y + CELL], outline=(200, 80, 80))
        else:
            d.rectangle([x, y, x + CELL, y + CELL], outline=(200, 80, 80))
            d.text((x + 8, y + CELL // 2 - 6), "MISSING", font=f_sub, fill=(220, 120, 120))
        d.rectangle([x, y, x + CELL - 1, y + CELL - 1], outline=(92, 76, 40))
        tx = x + CELL + 10
        d.text((tx, y + 6), top[:30], font=f_name, fill=(226, 222, 214))
        d.text((tx, y + 26), bottom[:36], font=f_sub, fill=(140, 134, 124))
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dupes"
    talents = load_talents()

    if mode == "dupes":
        by_hash = defaultdict(list)
        for tid in talents:
            p = ICONS / f"{tid}.png"
            if p.exists():
                by_hash[md5(p)].append(tid)
        groups = [v for v in by_hash.values() if len(v) > 1]
        groups.sort(key=len, reverse=True)
        entries = []
        for gi, g in enumerate(groups):
            for tid in sorted(g):
                cls, spec, name, _ = talents[tid]
                entries.append((tid, name, f"{cls}/{spec}  · group {gi+1}"))
        print(f"{len(groups)} shared icons across {len(entries)} talents")
        for g in groups[:12]:
            names = [f"{talents[t][2]} ({talents[t][0]})" for t in sorted(g)]
            print(f"   x{len(g)}: " + "  |  ".join(names))
        p = draw_sheet(entries, f"REUSED TALENT ICONS - {len(groups)} images shared by {len(entries)} talents",
                       OUT / "talent_dupes.png")
        print(f"\n{p}")
        return

    if mode == "class":
        cls = sys.argv[2]
        sel = {t: v for t, v in talents.items() if v[0] == cls}
        entries = [(t, v[2], v[1]) for t, v in sorted(sel.items(), key=lambda kv: (kv[1][1], kv[1][2]))]
        p = draw_sheet(entries, f"{cls.upper()} TALENTS ({len(entries)})", OUT / f"talents_{cls}.png")
        print(p)
        return

    if mode == "all":
        classes = sorted({v[0] for v in talents.values()})
        for cls in classes:
            sel = {t: v for t, v in talents.items() if v[0] == cls}
            entries = [(t, v[2], v[1]) for t, v in sorted(sel.items(), key=lambda kv: (kv[1][1], kv[1][2]))]
            p = draw_sheet(entries, f"{cls.upper()} TALENTS ({len(entries)})", OUT / f"talents_{cls}.png")
            print(p)
        return

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
