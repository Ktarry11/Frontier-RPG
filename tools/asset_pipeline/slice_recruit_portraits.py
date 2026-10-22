"""Slice the 6x4 recruit portrait sheet (flat magenta background) into assets/ui/portraits/<recruit_id>.png.

    python3 tools/asset_pipeline/slice_recruit_portraits.py sheet.png [--out assets/ui/portraits]

Same order as the sprite sheet (claude/recruit_art_prompts.md).  Busts are keyed out of the magenta, de-fringed, and pasted
bottom-centre onto one shared canvas so every head keeps the same scale.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from slice_recruit_sheet import IDS, extract  # noqa: E402


def main(sheet, out):
    crops = extract(sheet)
    cwid, chei = max(c.width for c in crops), max(c.height for c in crops)
    os.makedirs(out, exist_ok=True)
    for cid, im in zip(IDS, crops):
        canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
        canvas.paste(im, ((cwid - im.width) // 2, chei - im.height), im)
        canvas.save(os.path.join(out, f"{cid}.png"))
    print("canvas", cwid, chei)


if __name__ == "__main__":
    out = "assets/ui/portraits"
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    main(sys.argv[1], out)
