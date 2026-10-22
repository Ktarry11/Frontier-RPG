"""Cut the 24 chests out of the generated 6x4 chest sheet (gradient background, NOT flat magenta) with GrabCut.

    python3 tools/asset_pipeline/slice_chest_sheet.py assets/tiles/chests/sheet/chest_sheet_24.png [--out assets/tiles/chests]

Per cell: border pixels are definite background, the central blob is probable foreground; GrabCut refines it, then the mask is
cleaned (largest piece + nearby pieces, holes filled, 1px feather) and each chest is saved tight-cropped as ch_<name>.png on a
shared bottom-centre canvas so all chests keep their relative size.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

COLS, ROWS = 6, 4
NAMES = ["plain_box", "rope_crate", "iron_banded", "burlap_crate", "travel_trunk", "sea_chest",
         "orc_hide", "savannah", "moonwood", "undead_rusted", "goblin_lockbox", "troll_tiki",
         "dark_oak", "steel_strongbox", "ornate_gold", "stone_coffer", "sunken_coral", "chained_cursed",
         "fel_forged", "frost_rimed", "crystal_reliquary", "royal_gold", "ossuary", "void_obsidian"]


def cut(cell, tight=False):
    h, w = cell.shape[:2]
    mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    m = 10 if tight else 6
    mask[:m], mask[-m:], mask[:, :m], mask[:, -m:] = cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD, cv2.GC_BGD
    mask[h // 5 if tight else h // 9: -(h // 5 if tight else h // 9), w // 6 if tight else w // 10: -(w // 6 if tight else w // 10)] = cv2.GC_PR_FGD
    mask[(h // 3 if tight else h // 4): -(h // 3 if tight else h // 4), (w // 3 if tight else w // 4): -(w // 3 if tight else w // 4)] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(cv2.cvtColor(cell, cv2.COLOR_RGB2BGR), mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
    fg = (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)
    fg = ndimage.binary_opening(fg, iterations=1) if tight else ndimage.binary_closing(fg, structure=np.ones((3, 3)), iterations=4)
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        big = int(np.argmax(sizes)) + 1
        keep = np.isin(lab, [k for k in range(1, n + 1) if k == big or sizes[k - 1] > 0.04 * sizes[big - 1]])
        fg = keep
    fg = ndimage.binary_fill_holes(fg)
    return fg


def main(sheet, out):
    im = np.asarray(Image.open(sheet).convert("RGB"))
    H, W = im.shape[:2]
    cw, ch = W // COLS, H // ROWS
    crops = []
    for i in range(COLS * ROWS):
        r, c = divmod(i, COLS)
        cell = im[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
        # full = generous cut (keeps thin edges), tight = conservative cut; keep the generous one only near the tight one
        # so corner background patches the generous pass swallowed are dropped.
        fg = cut(cell) & ndimage.binary_dilation(cut(cell, tight=True), iterations=7)
        soft = ndimage.gaussian_filter(ndimage.binary_erosion(fg, iterations=1).astype(np.float32), 0.8)
        rgba = np.dstack([cell, (np.clip(soft, 0, 1) * 255).astype(np.uint8)])
        ys, xs = np.where(fg)
        crops.append(Image.fromarray(rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1], "RGBA"))
        print(NAMES[i], crops[-1].size)
    cwid, chei = max(x.width for x in crops) + 4, max(x.height for x in crops) + 4
    os.makedirs(out, exist_ok=True)
    for name, cr in zip(NAMES, crops):
        canvas = Image.new("RGBA", (cwid, chei), (0, 0, 0, 0))
        canvas.paste(cr, ((cwid - cr.width) // 2, chei - cr.height - 2), cr)
        canvas.save(os.path.join(out, f"ch_{name}.png"))
    print("canvas", cwid, chei)


if __name__ == "__main__":
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "assets/tiles/chests"
    main(sys.argv[1], out)
