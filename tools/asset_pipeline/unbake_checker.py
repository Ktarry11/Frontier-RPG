"""Turn a prop with a BAKED-IN fake-transparency checkerboard (opaque white/light-grey squares) into a real RGBA cut-out.

    python3 tools/asset_pipeline/unbake_checker.py file.png ...

Light neutral pixels (all channels >= 215, spread <= 9) are background if their connected region touches the border or is a
hole of >= 120 px between branches; a final 1px rim of near-white halo is removed, then the image is tight-cropped."""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def clean(path, pad=2):
    a = np.array(Image.open(path).convert("RGBA")).astype(np.int32)
    rgb = a[..., :3]
    light = (rgb.min(axis=2) >= 215) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 9)
    lab, n = ndi.label(light)
    h, w = light.shape
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndi.sum(light, lab, index=np.arange(1, n + 1))
    keep_bg = np.zeros(n + 1, bool)
    strict = (rgb.min(axis=2) >= 230) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 7)
    lab2, n2 = ndi.label(strict)
    sizes2 = ndi.sum(strict, lab2, index=np.arange(1, n2 + 1))
    for i in range(1, n + 1):
        if i in border or sizes[i - 1] >= 120:
            keep_bg[i] = True
    bg = keep_bg[lab]
    for i in range(1, n2 + 1):               # small near-white specks left between blades / branches
        if sizes2[i - 1] >= 10:
            bg |= lab2 == i
    # halo: pixels touching background that are still very light
    edge = ndi.binary_dilation(bg, iterations=2) & ~bg
    halo = edge & (rgb.min(axis=2) >= 190) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 14)
    bg = bg | halo
    a[..., 3] = np.where(bg, 0, 255)
    # drop stray fragments: tiny pieces, and thin strips hugging the image edge (generator border artefacts)
    flab, fn = ndi.label(a[..., 3] > 0)
    for i, sl in enumerate(ndi.find_objects(flab), start=1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        touches = sl[0].start == 0 or sl[1].start == 0 or sl[0].stop == h or sl[1].stop == w
        area = int((flab[sl] == i).sum())
        if area < 150 or (touches and (hh <= 20 or ww <= 20)):
            a[..., 3] = np.where(flab == i, 0, a[..., 3])
    ys, xs = np.where(a[..., 3] > 0)
    y0, y1, x0, x1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, h), max(xs.min() - pad, 0), min(xs.max() + pad + 1, w)
    out = Image.fromarray(a.astype(np.uint8), "RGBA").crop((x0, y0, x1, y1))
    out.save(path)
    return out.size


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(p, clean(p))
