"""Slice recruit art sheet 4 (16 characters: a 4x4 sprite sheet and a 4x4 portrait sheet).

    python3 tools/asset_pipeline/slice_recruit_sheet4.py sprites <sheet.png>
    python3 tools/asset_pipeline/slice_recruit_sheet4.py portraits <sheet.png>

claude/recruit_art_prompts_sheet4.md asked for one 4x4 sprite sheet and two 4x2 portrait sheets; the portraits came
back as ONE 4x4 image (17 Nov 2026), which this reads the same way. Figure finding is slice_recruit_sheet2.figures():
label the non-magenta blobs, group into rows, read left to right, so it doesn't care about the grid.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet2 import figures  # noqa: E402

IDS = [
    "rhys_ranger", "gunnar_barbarian", "reka_necromancer", "ramiro_primalist",
    "graham_warlock", "elie_bloodmage", "bruno_templar", "joaquin_suncleric",
    "astrid_starcaller", "luka_stormbringer", "zofia_cultist", "omar_venomancer",
    "santiago_runemaster", "emiliano_pyromancer", "isla_witchhunter", "dale_reaper",
]


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kind, sheet = sys.argv[1], sys.argv[2]
    crops = figures(sheet)
    if len(crops) != len(IDS):
        raise SystemExit(f"found {len(crops)} figures but need {len(IDS)} - refusing to write, because a miscount "
                         f"silently gives everyone after it somebody else's face")
    if kind == "sprites":
        cwid = max(c.width for c in crops) + 8
        chei = max(c.height for c in crops) + 4
        for cid, im in zip(IDS, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
            d = os.path.join("assets/npcs/recruits", cid)
            os.makedirs(d, exist_ok=True)
            canvas.save(os.path.join(d, "down.png"))
            print(f"  {cid:24} {canvas.size}")
    elif kind == "portraits":
        cwid = max(c.width for c in crops)
        chei = max(c.height for c in crops)
        os.makedirs("assets/ui/portraits", exist_ok=True)
        for cid, im in zip(IDS, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height), im)
            canvas.save(os.path.join("assets/ui/portraits", f"{cid}.png"))
            print(f"  {cid:24} {canvas.size}")
    else:
        raise SystemExit("first argument must be 'sprites' or 'portraits'")


if __name__ == "__main__":
    main()
