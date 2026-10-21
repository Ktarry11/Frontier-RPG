"""Recolour the pink chroma-key glow on the rim of nature props to savannah ochre.

    python3 tools/asset_pipeline/defringe_props.py assets/tiles/barrens/props br_golden_grass_tuft br_kodo_skeleton ...

Only touches pixels within 7px of transparency that are pink/red-ish; interior art is untouched.
Do NOT run on sprites with legitimate red (banners, tents).
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import matplotlib.colors as mc


def defringe(path, band_px=7):
    a = np.asarray(Image.open(path).convert("RGBA")).copy()
    op = a[..., 3] > 0
    dist = ndi.distance_transform_edt(op)
    band = op & (dist <= band_px)
    hsv = mc.rgb_to_hsv(a[..., :3] / 255.0)
    h, s, v = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    pink = band & ((h >= 325) | (h <= 22)) & (s > 0.18) & (v > 0.55)
    w = np.clip(1 - (dist - 1) / band_px, 0.35, 1.0)
    nh = np.where(pink, 38 * w + h * (1 - w), h)
    nh = np.where(pink & (h >= 325), 38 * w + (h - 360) * (1 - w), nh) % 360
    ns = np.where(pink, s * (1 - 0.45 * w), s)
    nv = np.where(pink, v * (1 - 0.12 * w), v)
    new = mc.hsv_to_rgb(np.stack([nh / 360, ns, nv], -1))
    a[..., :3] = np.where(pink[..., None], (new * 255).astype(np.uint8), a[..., :3])
    Image.fromarray(a, "RGBA").save(path)
    return int(pink.sum())


if __name__ == "__main__":
    d = sys.argv[1]
    for n in sys.argv[2:]:
        print(n, defringe(f"{d}/{n}.png"))
