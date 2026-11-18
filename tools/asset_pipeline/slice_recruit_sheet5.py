"""Slice recruit art sheet 5 (16 characters: a 4x4 sprite sheet and the portraits, one 4x4 or two 4x2).

    python3 tools/asset_pipeline/slice_recruit_sheet5.py sprites <sheet.png>
    python3 tools/asset_pipeline/slice_recruit_sheet5.py portraits <sheet.png> [<second sheet.png>]

claude/recruit_art_prompts_sheet5.md asks for one 4x4 sprite sheet and one 4x4 portrait sheet. Figure finding is
slice_recruit_sheet2.figures(): label the non-magenta blobs, group into rows, read left to right, so it doesn't care
about the grid. If the portraits come back as two 4x2 images, pass both and they're read in order.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet2 import figures  # noqa: E402

IDS = [
    "taras_witchhunter", "lucia_suncleric", "wes_warrior", "mariana_priest",
    "neil_felsworn", "cristobal_knight", "valentina_starcaller", "faris_shaman",
    "iker_guardian", "wade_barbarian", "ximena_primalist", "hector_witchdoctor",
    "tobias_paladin", "camila_venomancer", "sebastian_bloodmage", "enzo_cultist",
]


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kind, sheets = sys.argv[1], sys.argv[2:]
    crops = [c for sheet in sheets for c in figures(sheet)]
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
