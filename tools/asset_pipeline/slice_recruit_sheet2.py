"""Slice recruit art sheet 2 (20 characters) by READING ORDER rather than a fixed grid.

    python3 tools/asset_pipeline/slice_recruit_sheet2.py sprites <sheet.png>
    python3 tools/asset_pipeline/slice_recruit_sheet2.py portraits <sheet.png>

WHY NOT slice_recruit_sheet.py. That one assigns each figure to a cell of a hardcoded 6x4 grid by
majority pixel, which works when the generator fills every cell evenly. Sheet 2's sprite image does
not: its four rows hold 6, 5, 5 and 4 figures, spread to fill the width. Forcing a 5x4 or 6x4 grid
over that puts two people in one cell and leaves others empty, and the failure is silent - you get
twenty files, some of them wrong, and only notice when a recruit is wearing somebody else's face.

So this finds the figures first and infers the layout from them: label the non-magenta blobs, group
them into rows by vertical position, then read each row left to right. That is the order a person
writes a prompt list in and the order an image generator fills a sheet, and it does not care how
many are in a row.

The portrait sheet IS a clean 5x4, but it goes through the same path - one code path that reads
what is there beats two that disagree.

Order is the ID list below, which is the order in claude/recruit_art_prompts_sheet2.md. Verified
against the delivered art: row 1 is Kesten, Tarek, Fiona, Pavlo, Jun-seo, Minh.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

#: Reading order, matching claude/recruit_art_prompts_sheet2.md.
IDS2 = [
    "kesten_the_catalogued", "tarek_templar", "fiona_witchhunter", "pavlo_knight", "junseo_reaper",
    "minh_chronomancer", "alonso_pyromancer", "delroy_witchdoctor", "imelda_primalist",
    "tomas_warrior", "eino_barbarian", "ziad_felsworn", "pieter_guardian", "esteban_bloodmage",
    "kiet_rogue", "stelios_necromancer", "ratih_ranger", "kourosh_mage", "driss_shaman",
    "marisol_priest",
]

MIN_BLOB = 2000  # px; below this it is a stray speck, not a character


def figures(sheet):
    """Every character on the sheet as an RGBA crop, in reading order."""
    rgb = np.asarray(Image.open(sheet).convert("RGB")).astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # Magenta-ness: high where the background is, low on real art. Same idea as sheet 1's key().
    mag = np.minimum(r, b) - g
    solid = mag < 80
    H, W = solid.shape

    # Dilate before labelling so a staff tip or a loose scarf stays joined to its owner.
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=4))
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s >= MIN_BLOB]
    if not keep:
        raise SystemExit("no figures found - is the background actually magenta?")
    cents = ndimage.center_of_mass(solid, lab, keep)

    # Group into rows by vertical centre, then read each row left to right.
    order = sorted(zip(keep, cents), key=lambda t: t[1][0])
    rows, cur = [], [order[0]]
    for item in order[1:]:
        if item[1][0] - cur[-1][1][0] > H * 0.08:
            rows.append(cur)
            cur = [item]
        else:
            cur.append(item)
    rows.append(cur)
    seq = [k for row in rows for k, _c in sorted(row, key=lambda t: t[1][1])]
    print(f"  {len(seq)} figures in {len(rows)} rows: {[len(r) for r in rows]}")

    # De-fringe exactly as sheet 1 does: erode a pixel off the keyed edge, then pull the magenta
    # spill out of the next ring in rather than leaving a pink halo.
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    rgb8 = rgb.astype(np.uint8)
    crops = []
    for k in seq:
        mask = (lab == k) & inner
        ys, xs = np.where(mask)
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([rgb8, np.where(mask, 255, 0).astype(np.uint8)])[by0:by1, bx0:bx1].copy()
        r_, g_, b_ = (rgba[..., i].astype(int) for i in range(3))
        spill = ring[by0:by1, bx0:bx1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        crops.append(Image.fromarray(rgba, "RGBA"))
    return crops


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kind, sheet = sys.argv[1], sys.argv[2]
    crops = figures(sheet)
    if len(crops) != len(IDS2):
        raise SystemExit(f"found {len(crops)} figures but expected {len(IDS2)} - refusing to "
                         f"write, because a miscount means everyone after it gets the wrong art")

    if kind == "sprites":
        # One shared canvas so every figure keeps the same scale and stands on the same baseline,
        # which is what makes a row of them look like one cast rather than a collage.
        cwid = max(c.width for c in crops) + 8
        chei = max(c.height for c in crops) + 4
        out = "assets/npcs/recruits"
        for cid, im in zip(IDS2, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height - 2), im)
            d = os.path.join(out, cid)
            os.makedirs(d, exist_ok=True)
            canvas.save(os.path.join(d, "down.png"))
            print(f"  {cid:28} {canvas.size}")
        print("sprite canvas", cwid, chei)
    elif kind == "portraits":
        cwid = max(c.width for c in crops)
        chei = max(c.height for c in crops)
        out = "assets/ui/portraits"
        os.makedirs(out, exist_ok=True)
        for cid, im in zip(IDS2, crops):
            canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
            canvas.paste(im, ((cwid - im.width) // 2, chei - im.height), im)
            canvas.save(os.path.join(out, f"{cid}.png"))
            print(f"  {cid:28} {canvas.size}")
        print("portrait canvas", cwid, chei)
    else:
        raise SystemExit("first argument must be 'sprites' or 'portraits'")


if __name__ == "__main__":
    main()
