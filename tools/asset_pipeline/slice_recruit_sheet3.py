"""Slice recruit art sheet 3 (24 characters, delivered as four images).

    python3 tools/asset_pipeline/slice_recruit_sheet3.py sprites|portraits <sheet.png> first12|last12

WHY FOUR IMAGES. The first generation was asked for all 24 at once and held for
twelve before inventing its own cast, so characters 13-24 were regenerated as a
separate pair of 6x2 sheets. That leaves:

    sprites   1-12  the TOP TWO ROWS of the original 6x4 sprite sheet
    sprites  13-24  a 6x2 sheet of its own
    portraits 1-12  the TOP TWO ROWS of the original 6x4 portrait sheet
    portraits 13-24 a 6x2 sheet of its own

So this takes an explicit half. `first12` reads the first twelve figures in
reading order and ignores whatever follows, which is what makes the usable top
half of a drifted 24-sheet recoverable without hand-cropping.

Figure finding is slice_recruit_sheet2.figures(): label the non-magenta blobs,
group into rows, read left to right. It infers the layout instead of forcing a
grid, which matters here because two of these four images are 6x2 and two are
the top half of a 6x4.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet2 import figures  # noqa: E402

FIRST12 = [
    "diego_tinker", "freja_priest", "sondre_stormbringer", "berat_tinker",
    "matias_reaper", "giorgi_primalist", "camille_ranger", "orlando_witchdoctor",
    "adrian_templar", "saoirse_starcaller", "nicolas_bloodmage", "ileana_necromancer",
]
LAST12 = [
    "thiago_paladin", "skye_pyromancer", "vuk_knight", "karim_felsworn",
    "gianluca_guardian", "elias_suncleric", "rui_cultist", "nizar_chronomancer",
    "yusuf_venomancer", "bashir_witchhunter", "osvaldo_warlock", "khalid_hunter",
]


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    kind, sheet, half = sys.argv[1], sys.argv[2], sys.argv[3]
    ids = FIRST12 if half == "first12" else LAST12

    crops = figures(sheet)
    if len(crops) < len(ids):
        raise SystemExit(
            f"found {len(crops)} figures but need {len(ids)} - refusing to write, because a "
            f"miscount silently gives everyone after it somebody else's face")
    crops = crops[:len(ids)]

    if kind == "sprites":
        cwid = max(c.width for c in crops) + 8
        chei = max(c.height for c in crops) + 4
        out = "assets/npcs/recruits"
        for cid, im in zip(ids, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
            d = os.path.join(out, cid)
            os.makedirs(d, exist_ok=True)
            canvas.save(os.path.join(d, "down.png"))
            print(f"  {cid:24} {canvas.size}")
        print("  sprite canvas", cwid, chei)
    elif kind == "portraits":
        cwid = max(c.width for c in crops)
        chei = max(c.height for c in crops)
        out = "assets/ui/portraits"
        os.makedirs(out, exist_ok=True)
        for cid, im in zip(ids, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height), im)
            canvas.save(os.path.join(out, f"{cid}.png"))
            print(f"  {cid:24} {canvas.size}")
    else:
        raise SystemExit("first argument must be 'sprites' or 'portraits'")


if __name__ == "__main__":
    main()
