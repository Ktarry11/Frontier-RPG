#!/usr/bin/env python3
"""Slice Kyle's T0 armour-set sheets into one icon per set piece, plus a recoloured copy per
other version of the set.

    python3 tools/slice_t0_set_icons.py

Sheets are tools/icon_sheets/t0_sets_sheet<N>.png, laid out as claude/t0_set_icon_prompts.md asks:
one ROW per set, eight icons left to right in tools/build_t0_sets.SLOTS order (head, shoulder,
chest, wrist, hands, waist, legs, feet). SHEETS below says which sets each sheet holds; a sheet
that has not arrived yet is skipped and its sets keep the plain slot picture.

Files: assets/icons/gear/<set_id>_<slot>.png for a set's first version, and
<set_id>_<slot>__<version>.png for each other version (the same icon with its hue turned), which
is what world/gear_sets.icon_for() looks up.

WHY NOT slice_icon_sheet's KEYING. That one fades anything near magenta, which is right for a
sprite with soft edges and wrong here: these are framed squares, and several sets are violet or
purple, which sits close enough to #FF00FF to come out half transparent. So the background is
only the magenta that is CONNECTED TO THE SHEET'S EDGE; everything inside an icon's frame is kept
whole, whatever colour it is.
"""
import colorsys
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SHEET_DIR = ROOT / "tools" / "icon_sheets"
OUT = ROOT / "assets" / "icons" / "gear"
SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet"]
SIZE = 64

#: sheet number -> the classes on it, top row first (claude/t0_set_icon_prompts.md)
SHEETS = {
    1: ["Warrior", "Paladin", "Knight of Xoroth", "Guardian"],
    2: ["Cultist", "Starcaller", "Sun Cleric", "Primalist"],
    3: ["Shaman", "Hunter", "Witch Hunter", "Tinker"],
    4: ["Venomancer", "Reaper", "Rogue", "Druid"],
    5: ["Barbarian", "Witch Doctor", "Felsworn", "Templar"],
    6: ["Bloodmage", "Ranger", "Priest", "Mage"],
    7: ["Warlock", "Necromancer", "Pyromancer", "Runemaster"],
    8: ["Chronomancer", "Stormbringer"],
}
#: degrees of hue turn for a set's 2nd, 3rd, 4th ... version
HUE_TURNS = [38, -38, 76, -76, 150]


def set_id(char_class):
    return "t0_" + char_class.lower().replace(" ", "_")


def find_icons(rgb):
    """-> list of (mask, bbox) for each framed icon, in reading order as rows of eight."""
    mag = np.array([255.0, 0.0, 255.0])
    near = np.sqrt(((rgb - mag) ** 2).sum(axis=2)) < 110.0
    lab, _ = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    outside = np.isin(lab, list(edge))
    icons, n = ndimage.label(~outside)
    found = []
    for i, sl in enumerate(ndimage.find_objects(icons), start=1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h * w < 60 * 60:
            continue
        found.append(((icons[sl] == i), sl))
    found.sort(key=lambda f: f[1][0].start)
    rows = [found[i:i + 8] for i in range(0, len(found), 8)]
    return [sorted(r, key=lambda f: f[1][1].start) for r in rows]


def cut(rgb, mask, sl):
    mask = ndimage.binary_erosion(ndimage.binary_fill_holes(mask), iterations=2)
    crop = rgb[sl]
    h, w = mask.shape
    side = max(h, w)
    canvas = np.zeros((side, side, 4), np.uint8)
    oy, ox = (side - h) // 2, (side - w) // 2
    canvas[oy:oy + h, ox:ox + w, :3] = crop
    canvas[oy:oy + h, ox:ox + w, 3] = mask * 255
    return Image.fromarray(canvas, "RGBA").resize((SIZE, SIZE), Image.LANCZOS)


def turn_hue(img, degrees):
    a = np.asarray(img).astype(np.float64) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hsv = np.vectorize(colorsys.rgb_to_hsv)(r, g, b)
    h = (hsv[0] + degrees / 360.0) % 1.0
    rgb = np.vectorize(colorsys.hsv_to_rgb)(h, hsv[1], hsv[2])
    out = np.dstack([rgb[0], rgb[1], rgb[2], a[..., 3]])
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


def main():
    sets = json.loads((ROOT / "data/items/gear_sets.json").read_text(encoding="utf-8"))["sets"]
    OUT.mkdir(parents=True, exist_ok=True)
    base = extra = 0
    problems, waiting = [], []
    for n, classes in SHEETS.items():
        path = SHEET_DIR / f"t0_sets_sheet{n}.png"
        if not path.exists():
            waiting.append((n, classes))
            continue
        rgb = np.asarray(Image.open(path).convert("RGB"))
        rows = find_icons(rgb.astype(np.float64))
        if len(rows) != len(classes) or any(len(r) != 8 for r in rows):
            problems.append(f"sheet {n}: found rows of {[len(r) for r in rows]}, wanted {len(classes)} rows of 8")
            continue
        for char_class, row in zip(classes, rows):
            sid = set_id(char_class)
            versions = list(sets[sid]["variants"])
            for slot, (mask, sl) in zip(SLOTS, row):
                icon = cut(rgb, mask, sl)
                icon.save(OUT / f"{sid}_{slot}.png")
                base += 1
                for k, version in enumerate(versions[1:]):
                    turn_hue(icon, HUE_TURNS[k % len(HUE_TURNS)]).save(OUT / f"{sid}_{slot}__{version}.png")
                    extra += 1
    print(f"{base} set-piece icons and {extra} recoloured versions written to {OUT.relative_to(ROOT)}")
    for n, classes in waiting:
        print(f"  waiting on sheet {n}: {', '.join(classes)}")
    for p in problems:
        print("  PROBLEM", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
