#!/usr/bin/env python3
"""Cut an epic-gear icon sheet into gear_epic_<key>_<n>.png files.

    PYTHONPATH=. python3 tools/slice_icon_sheets.py SHEET [--apply]
                                                   [--rows R --cols C]
                                                   [--layout weapons|armour]
                                                   [--out DIR]

Companion to tools/slice_background_sheets.py and deliberately the same
shape: a sheet goes in, a NAMED manifest says what each cell is, and the
names are what the game's prefix tables glob for. The alternative - slicing
blind and renaming by hand afterwards - is how you end up with a gauntlet
icon called gear_epic_feet_plate_2.

LAYOUT, NOT PER-SHEET MANIFEST. Unlike the background sheets, these are
regular: the prompts in docs/epic_icon_prompts.md lay out sheet 1 as sixteen
weapon families of three and sheet 2 as twelve armour slots of four, both in
reading order. So the manifest here is the ORDER, and the grid shape is
derived from it. Pass --rows/--cols only if a sheet comes back laid out
differently from the prompt.

TRANSPARENCY. Icons sit on a plain dark background in the generated sheet.
This does NOT key it out: guessing a background colour and making it alpha
eats the dark parts of the art itself, and the game draws icons on an opaque
slot anyway. The cell is cropped and saved as-is.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEAR = ROOT / "assets" / "icons" / "gear"

#: Sheet 1: sixteen weapon families, three variants each, reading order.
WEAPON_ORDER = [
    "sword_1h", "sword_2h", "axe_1h", "axe_2h", "mace_1h", "mace_2h",
    "dagger", "staff", "polearm", "shield", "bow", "gun", "wand",
    "fist_weapon", "tome", "libram",
]
WEAPON_PER = 3

#: Sheet 2: twelve armour slots, four variants each (plate/mail/leather/cloth
#: where the ordinary table splits by type; four designs where it does not).
#: The suffixed keys match gear_icons._epic_key, which builds "<slot>_<type>"
#: only for the slots ARMOR_ICON_PREFIXES actually splits.
#: The only slots ARMOR_ICON_PREFIXES actually keys by armour type. Checked
#: against the table rather than guessed - "legs" looks like it should split
#: and does not, and naming four legplate icons gear_epic_legs_plate_1 would
#: have made four files _epic_key never asks for.
ARMOUR_SPLIT = ["head", "chest", "feet"]
ARMOUR_ORDER = [
    "head", "shoulder", "chest", "hands", "waist", "legs", "feet",
    "wrist", "back", "neck", "ring", "trinket",
]
ARMOUR_PER = 4
MATERIALS = ["plate", "mail", "leather", "cloth"]


def cell_names(layout):
    """Every cell's stem, in reading order."""
    names = []
    if layout == "weapons":
        for key in WEAPON_ORDER:
            for i in range(1, WEAPON_PER + 1):
                names.append(f"gear_epic_{key}_{i}")
    else:
        for slot in ARMOUR_ORDER:
            for i in range(ARMOUR_PER):
                if slot in ARMOUR_SPLIT:
                    names.append(f"gear_epic_{slot}_{MATERIALS[i]}_1")
                else:
                    names.append(f"gear_epic_{slot}_{i + 1}")
    return names


def _grid(count, rows, cols):
    if rows and cols:
        return rows, cols
    # 48 -> 6x8. Prefer wider than tall, which is how the prompts are written.
    for c in range(int(count ** 0.5) + 1, count + 1):
        if count % c == 0:
            return count // c, c
    return 1, count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--layout", choices=("weapons", "armour"), default=None,
                    help="defaults to weapons for a 48-cell sheet named *weapon*")
    ap.add_argument("--rows", type=int, default=None)
    ap.add_argument("--cols", type=int, default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=None, help="write here instead of the gear pack")
    args = ap.parse_args()

    layout = args.layout
    if layout is None:
        layout = "armour" if "arm" in args.sheet.name.lower() else "weapons"
    names = cell_names(layout)
    rows, cols = _grid(len(names), args.rows, args.cols)

    from PIL import Image
    sheet = Image.open(args.sheet).convert("RGB")
    # FLOAT BOUNDARIES, not an integer cell size. 1024 / 6 rows = 170.67, so
    # an int cell of 170 drops two thirds of a pixel per row and by the
    # bottom row the crop window sits ~4px high - which pulled the tip of the
    # polearm above into the top-left of the shield icon. Each edge is
    # computed from the full sheet dimension instead, so error never
    # accumulates.
    cw, ch = sheet.width / cols, sheet.height / rows
    dest = Path(args.out) if args.out else GEAR
    # 1/48th of a cell was not enough and neither was 1/20th: the generator
    # does not respect the cell edge exactly, so a long weapon in one cell -
    # the polearm's tassel, a bow tip - overhangs into its neighbour. 1/14th
    # clears the overhang. The prompt asks the art to fill ~85% of a cell, so
    # this still cannot bite into the icon itself.
    trim = max(3, int(min(cw, ch) // 14))

    written = []
    for idx, stem in enumerate(names):
        r, c = divmod(idx, cols)
        if r >= rows:
            break
        cell = sheet.crop((round(c * cw) + trim, round(r * ch) + trim,
                           round((c + 1) * cw) - trim, round((r + 1) * ch) - trim))
        if args.apply:
            dest.mkdir(parents=True, exist_ok=True)
            cell.save(dest / f"{stem}.png")
        written.append(stem)

    print(f"  {layout}: {len(written)} icons from a {rows}x{cols} grid "
          f"({cw:.1f}x{ch:.1f} cells, {trim}px trim)\n")
    for i in range(0, len(written), cols):
        print("   " + "  ".join(n.replace("gear_epic_", "") for n in written[i:i + cols]))
    print("\n  written to " + str(dest) if args.apply
          else "\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
