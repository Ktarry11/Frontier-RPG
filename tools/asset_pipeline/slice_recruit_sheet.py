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


def main(sheet, out):
    im = Image.open(sheet).convert("RGB")
    rgb = np.asarray(im)
    alpha = key(rgb)
    H, W = alpha.shape
    solid = alpha > 128
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=3))
    cw, ch = W / COLS, H / ROWS
    crops = []
    for i in range(COLS * ROWS):
        r, c = divmod(i, COLS)
        x0, x1, y0, y1 = int(c * cw), int((c + 1) * cw), int(r * ch), int((r + 1) * ch)
        sub = lab[y0:y1, x0:x1]
        ids, counts = np.unique(sub[sub > 0], return_counts=True)
        keep = [k for k, cnt in zip(ids, counts) if cnt > 400]          # drop specks, keep body + detached weapon bits
        mask = np.isin(lab, keep)
        mask[:y0], mask[y1:], mask[:, :x0], mask[:, x1:] = False, False, False, False
        ys, xs = np.where(mask & solid)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([rgb, alpha])[by0:by1, bx0:bx1].copy()
        m = ndimage.binary_dilation(mask, iterations=0)[by0:by1, bx0:bx1]
        rgba[..., 3] = np.where(ndimage.binary_dilation(mask, iterations=2)[by0:by1, bx0:bx1], rgba[..., 3], 0)
        # de-magenta the rim: any semi/edge pixel pulled towards the neighbouring solid colour
        edge = (rgba[..., 3] > 0) & (rgba[..., 3] < 255)
        r_, g_, b_ = rgba[..., 0].astype(int), rgba[..., 1].astype(int), rgba[..., 2].astype(int)
        spill = edge & (np.minimum(r_, b_) > g_ + 25)
        lim = np.maximum(g_, 0) + 25
        rgba[..., 0] = np.where(spill, np.minimum(r_, lim), r_)
        rgba[..., 2] = np.where(spill, np.minimum(b_, lim), b_)
        crops.append(Image.fromarray(rgba, "RGBA"))
        print(IDS[i], crops[-1].size)
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
