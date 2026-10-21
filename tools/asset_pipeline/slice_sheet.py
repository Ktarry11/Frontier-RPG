"""Slice ChatGPT sheets into game assets.

  tiles:  python3 slice_sheet.py tiles  sheet.png out_dir COLSxROWS name1 name2 ...
          Cuts an evenly divided grid of flush tiles (256px each from a
          1536x1024 6x4 sheet) and writes <name>.png. Run make_seamless.py on
          the output afterwards.
  props:  python3 slice_sheet.py props  sheet.png out_dir name1 name2 ...
          Keys the flat #FF00FF background out (flood-filled from the outside
          so magenta-ish coral/crystal INSIDE a prop survives), despills the
          pink edge fringe, groups pixels into objects, orders them row-major
          and writes one tight-cropped RGBA png per name. Prints any object
          that touches the sheet border (= cropped by the generator).
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def slice_tiles(sheet, out_dir, grid, names):
    cols, rows = (int(v) for v in grid.lower().split("x"))
    im = Image.open(sheet).convert("RGB")
    cw, ch = im.width // cols, im.height // rows
    assert len(names) == cols * rows, f"need {cols*rows} names, got {len(names)}"
    os.makedirs(out_dir, exist_ok=True)
    for i, n in enumerate(names):
        c, r = i % cols, i // cols
        im.crop((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)).save(os.path.join(out_dir, n + ".png"))


def key_magenta(arr, dist=120):
    rgb = arr[:, :, :3].astype(float)
    d = np.sqrt(((rgb - [255, 0, 255]) ** 2).sum(axis=2))
    cand = d < dist
    lab, n = ndi.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    # background = candidate regions that reach the sheet border OR are huge
    sizes = ndi.sum(cand, lab, range(1, n + 1))
    bg = np.isin(lab, [i for i in border] + [i + 1 for i, s in enumerate(sizes) if s > 4000])
    # enclosed pockets (inside an anchor ring, a sail, a wheel...): only drop the
    # near-PURE magenta ones so pink/violet coral and crystals survive.
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    # shaded magenta (the generator darkens "background" seen through holes):
    # bright-ish R and B, almost no green, R ~ B. Pink/violet coral has more G.
    pure = (d < 70) | ((R > 105) & (B > 105) & (G < 0.30 * np.minimum(R, B)) & (np.abs(R - B) < 55))
    plab, pn = ndi.label(pure)
    psz = ndi.sum(pure, plab, range(1, pn + 1))
    bg |= np.isin(plab, [i + 1 for i, s in enumerate(psz) if s > 40])
    # tiny gaps (rib spaces, net holes, chain links): strict hue, any size
    strict = (np.minimum(R, B) > 120) & (G < 0.22 * np.minimum(R, B)) & (np.abs(R - B) < 45)
    bg |= strict
    # grow into the antialiased rim that still leans magenta
    loose = (np.minimum(R, B) > 90) & (G < 0.42 * np.minimum(R, B)) & (np.abs(R - B) < 70)
    for _ in range(3):
        bg |= ndi.binary_dilation(bg) & loose
    return bg


def despill(arr, alpha_mask):
    rgb = arr[:, :, :3].astype(float)
    edge = alpha_mask & ~ndi.binary_erosion(alpha_mask, iterations=3)
    g = rgb[:, :, 1]
    spill = np.minimum(rgb[:, :, 0], rgb[:, :, 2]) - g
    k = np.clip(spill, 0, None)
    out = rgb.copy()
    m = edge & (k > 0)
    out[:, :, 0][m] -= 0.85 * k[m]
    out[:, :, 2][m] -= 0.85 * k[m]
    arr[:, :, :3] = np.clip(out, 0, 255).astype(np.uint8)
    return arr


def slice_props(sheet, out_dir, names, grid="6x4", dil=7):
    cols, rows = (int(v) for v in grid.lower().split("x"))
    arr = np.array(Image.open(sheet).convert("RGBA"))
    bg = key_magenta(arr)
    # peel the 1px antialiased rim of bg-blended pixels
    fg = ~bg
    fg = ndi.binary_opening(fg, iterations=1)
    alpha = fg.copy()
    arr = despill(arr, alpha)
    arr[:, :, 3] = np.where(alpha, 255, 0)
    H, W = alpha.shape
    assert len(names) == cols * rows, f"need {cols*rows} names"
    os.makedirs(out_dir, exist_ok=True)
    # group fragments into objects, merge tiny specks into the nearest big object
    grp, n = ndi.label(ndi.binary_dilation(alpha, iterations=dil))
    info = []
    for i in range(1, n + 1):
        ys, xs = np.where((grp == i) & alpha)
        if len(xs):
            info.append([i, xs.min(), xs.max(), ys.min(), ys.max(), len(xs)])
    big = [o for o in info if o[5] >= 2500]
    print(f"objects >=2500px: {len(big)} (expected {len(names)}); small specks dropped: {len(info) - len(big)}")
    if len(big) != len(names):
        raise AssertionError("object count mismatch - try --dil N")
    big.sort(key=lambda o: (round(((o[3] + o[4]) / 2) / (H / rows) - 0.5), (o[1] + o[2]) / 2))
    flagged = []
    for o, name in zip(big, names):
        i, x0, x1, y0, y1, _ = o
        sel = (grp == i) & alpha
        sub = arr[y0:y1 + 1, x0:x1 + 1].copy()
        sub[:, :, 3] = np.where(sel[y0:y1 + 1, x0:x1 + 1], 255, 0)
        Image.fromarray(sub).save(os.path.join(out_dir, name + ".png"))
        if x0 <= 1 or y0 <= 1 or x1 >= W - 2 or y1 >= H - 2:
            flagged.append(name)
    print("touching sheet border (cropped by the generator):", flagged or "none")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "tiles":
        slice_tiles(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
    else:
        slice_props(sys.argv[2], sys.argv[3], sys.argv[4:])
