"""Slice the twelve townsfolk sheets (docs/townsfolk_npc_art_prompts.md, 22 Nov 2026): 24 front-only figures each, the
same 6x4 layout as the blood elf and Aetherian sheets, so the same figure finding (slice_recruit_sheet6).

    python3 tools/asset_pipeline/slice_townsfolk_sheets.py <sheet.png> <race> <gender> <prefix>

Writes assets/npcs/<race>[/<gender dir>]/<prefix>1..24/down.png. Humans keep their male/ and female/ folders; every other
race's looks sit straight under its folder. They're NPC looks: world/race_registry.py appends them after every look a
save can hold and keeps the character creator's offer as it was.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet2 import figures            # noqa: E402
from slice_recruit_sheet6 import grid_figures       # noqa: E402


def slice_one(sheet, race, gender, prefix):
    crops = figures(sheet)
    if len(crops) != 24:
        crops = grid_figures(sheet, cols=6, rows=4)
    if len(crops) != 24:
        raise SystemExit(f"{sheet}: found {len(crops)} figures but need 24")
    cwid = max(c.width for c in crops) + 8
    chei = max(c.height for c in crops) + 4
    base = os.path.join("assets/npcs", race, gender) if race == "human" else os.path.join("assets/npcs", race)
    for k, im in enumerate(crops, 1):
        canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
        canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
        d = os.path.join(base, f"{prefix}{k}")
        os.makedirs(d, exist_ok=True)
        canvas.save(os.path.join(d, "down.png"))
    print(f"  {base}/{prefix}1..24 {canvas.size}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    slice_one(*sys.argv[1:])
