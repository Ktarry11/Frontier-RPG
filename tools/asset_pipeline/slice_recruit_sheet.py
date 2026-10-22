"""Slice the 6x4 recruit sprite sheet (flat magenta background) into assets/npcs/recruits/<recruit_id>/down.png.

    python3 tools/asset_pipeline/slice_recruit_sheet.py sheet.png [--out assets/npcs/recruits]

Order is row-major, the same as claude/recruit_art_prompts.md.  Every figure is keyed out of the magenta, tight-cropped, then
pasted bottom-centre onto ONE shared canvas (so bodies keep the same relative scale and the height-anchored renderer stands
everyone on the same ground line; staffs and polearms just reach higher).  Edge pixels are de-magentaed.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

COLS, ROWS = 6, 4
IDS = ["dan_warrior", "ama_priest", "silas_rogue", "rosa_hunter", "marco_paladin", "sophia_mage",
       "ryan_warlock", "carolina_shaman", "amber_druid", "marcus_stormbringer", "ivan_warrior", "asher_coleman",
       "owen_cultist", "mateo_starcaller", "pasang_primalist", "haruto_runemaster", "liam_suncleric", "marta_tinker",
       "callum_venomancer", "emre_rogue", "bakyt_hunter", "henrik_mage", "anjali_druid", "hana_shaman"]


def key(rgb):
    """Alpha 0..255 from magenta-ness; hard magenta -> 0."""
    a = rgb.astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mag = (np.minimum(r, b) - g)                      # high for magenta, small for real art
    alpha = np.clip((170 - mag) * 255 // 90, 0, 255)  # mag>=170 -> 0, mag<=80 -> 255
    return alpha.astype(np.uint8)


def extract(sheet):
    """Return 24 tight-cropped RGBA figures (row-major) from a magenta-background sheet.

    Each connected piece is assigned to the grid cell holding most of its pixels (a hat finial or staff tip may poke
    into the neighbouring cell's area), the 1px magenta rim is eroded away, and the next ring is de-magentaed."""
    rgb = np.asarray(Image.open(sheet).convert("RGB"))
    alpha = key(rgb)
    H, W = alpha.shape
    solid = alpha > 128
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    cw, ch = W / COLS, H / ROWS
    yy, xx = np.mgrid[0:H, 0:W]
    cell = np.minimum(yy // int(np.ceil(ch)), ROWS - 1) * COLS + np.minimum(xx // int(np.ceil(cw)), COLS - 1)
    owner = {}
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() < 400:
            continue
        owner[k] = int(np.bincount(cell[m & solid], minlength=COLS * ROWS).argmax())
    inner = ndimage.binary_erosion(solid, iterations=1)
    ring = inner & ~ndimage.binary_erosion(inner, iterations=2)
    crops = []
    for i in range(COLS * ROWS):
        mask = np.isin(lab, [k for k, o in owner.items() if o == i]) & inner
        ys, xs = np.where(mask)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([rgb, np.where(mask, 255, 0).astype(np.uint8)])[by0:by1, bx0:bx1].copy()
        r_, g_, b_ = (rgba[..., k].astype(int) for k in range(3))
        spill = ring[by0:by1, bx0:bx1] & (np.minimum(r_, b_) > g_ + 25)
        lim = g_ + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        crops.append(Image.fromarray(rgba, "RGBA"))
        print(IDS[i], crops[-1].size)
    return crops


def main(sheet, out):
    crops = extract(sheet)
    cwid = max(c.width for c in crops) + 8
    chei = max(c.height for c in crops) + 4
    for cid, im_ in zip(IDS, crops):
        canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
        canvas.paste(im_, ((cwid - im_.width) // 2, chei - im_.height - 2), im_)
        d = os.path.join(out, cid)
        os.makedirs(d, exist_ok=True)
        canvas.save(os.path.join(d, "down.png"))
    print("canvas", cwid, chei)


if __name__ == "__main__":
    out = "assets/npcs/recruits"
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    main(sys.argv[1], out)
