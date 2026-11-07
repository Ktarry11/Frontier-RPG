#!/usr/bin/env python3
"""Cut the generated 8x6 icon sheets into named 64x64 PNGs.

    PYTHONPATH=. python3 tools/slice_icon_sheets.py SHEET1 SHEET2 SHEET3 [--apply]

Kyle generated three sheets from docs/icon_prompts.md. Each is 48 icons in
an 8 x 6 grid, in the exact order that file lists them, so every cell has a
known ability_id or passive owner and nothing needs matching by eye.

GEOMETRY. The sheets come back 1536 x 1024, so a cell is 192 x 170.7 - wider
than tall, because the generator fits 8 x 6 into a 3:2 canvas rather than
making the cells square. Each cell is centre-cropped to its short side
before the downscale, which trims the left and right edges rather than
squashing a round shield into an oval.

NAMING. Abilities are written as <ability_id>.png, which is the convention
IconRenderer.ABILITY_ICON_DIR already resolves by. Passives are written as
passive_<recruit_id>.png and passive_racial_<race>.png - a passive is one
icon per character, not one per stat, which is why there are 35 and not 71.

SHEET 3 HAS SPARES. 13 of its 48 cells are generic objects with no owner
(whetstone, rope, pocket watch...). They are written to a spares/ folder
rather than discarded - they are the reusable vocabulary for abilities that
do not earn bespoke art.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/icons/abilities"
SPARES = ROOT / "assets/icons/spares"

COLS, ROWS = 8, 6
SIZE = 64


def kit_order():
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    recruits = {r["recruit_id"]: r for r in
                json.loads((ROOT / "data/npcs/recruits.json").read_text())["recruits"]}
    by_role = {}
    for rid, v in kits.items():
        if rid.startswith("_"):
            continue
        by_role.setdefault(recruits[rid].get("gear_theme"), []).append((rid, v))
    return kits, by_role


def build_manifest():
    """Ordered [(name, label)] for each of the three sheets."""
    kits, by_role = kit_order()
    racials = json.loads((ROOT / "data/races/racials.json").read_text())

    def abilities(role):
        return [(a["ability_id"], f"{v['name']} - {a['name']}")
                for rid, v in by_role[role] for a in v["abilities"]]

    # Sheet 1 - MARTIAL: tank 27 + melee 21
    sheet1 = abilities("tank") + abilities("melee_dps")

    # Sheet 2 - ARCANE/LIGHT/HUNT: ranged 24 + healer 18 + the first 6 racials
    racial_abilities = [(a["ability_id"], f"{v['label']} - {a['name']}")
                        for rid, v in racials.items() if not rid.startswith("_")
                        for a in v["abilities"]]
    sheet2 = abilities("ranged_dps") + abilities("healer") + racial_abilities[:6]

    # Sheet 3 - CRESTS: 30 kit passives, 5 racial passives, 13 spares
    sheet3 = [(f"passive_{rid}", f"{v['name']} - {v['passives'].get('_name','?')}")
              for rid, v in kits.items() if not rid.startswith("_")]
    sheet3 += [(f"passive_racial_{rid}", f"{v['label']} - {v['passives'].get('_name','?')}")
               for rid, v in racials.items() if not rid.startswith("_")]
    sheet3 += [(f"spare_{i:02d}", "unassigned vocabulary")
               for i in range(1, COLS * ROWS - len(sheet3) + 1)]
    return [sheet1, sheet2, sheet3]


def slice_sheet(path, names, apply_):
    from PIL import Image
    sheet = Image.open(path).convert("RGBA")
    w, h = sheet.size
    cw, ch = w / COLS, h / ROWS
    side = min(cw, ch)
    written = []
    for index, name in enumerate(names):
        if index >= COLS * ROWS:
            break
        r, c = divmod(index, COLS)
        cx, cy = (c + 0.5) * cw, (r + 0.5) * ch
        box = (round(cx - side / 2), round(cy - side / 2),
               round(cx + side / 2), round(cy + side / 2))
        icon = sheet.crop(box).resize((SIZE, SIZE), Image.LANCZOS)
        target = (SPARES if name[0].startswith("spare_") else OUT) / f"{name[0]}.png"
        if apply_:
            target.parent.mkdir(parents=True, exist_ok=True)
            icon.save(target)
        written.append((name[0], name[1], target))
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheets", nargs=3, type=Path,
                    help="the three sheets, in docs/icon_prompts.md order: "
                         "martial, arcane, crests")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    manifest = build_manifest()
    total = 0
    for sheet_no, (path, names) in enumerate(zip(args.sheets, manifest), 1):
        written = slice_sheet(path, names, args.apply)
        total += len(written)
        print(f"\nsheet {sheet_no}: {path.name} -> {len(written)} icons")
        for key, label, target in written[:4]:
            print(f"   {key:46}{label}")
        print(f"   ... and {len(written) - 4} more")

    print(f"\n{total} icons"
          + (f" written" if args.apply else " (report only; pass --apply to write)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
