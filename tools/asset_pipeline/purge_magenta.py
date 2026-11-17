"""Remove leaked #FF00FF background (and its pink edge blend) that flood-fill keying missed inside gaps/holes of a prop.

    python3 tools/asset_pipeline/purge_magenta.py file_or_dir ...

Any pixel within colour-distance 105 of (255,0,255) becomes transparent; pixels just outside that (105-150) that are pinkish AND touch
a transparent pixel are pulled toward their grey value.  Genuine violet/purple art sits well beyond 105 from pure magenta."""
import glob
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def purge(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(np.int32)
    d = np.sqrt((a[..., 0] - 255) ** 2 + a[..., 1] ** 2 + (a[..., 2] - 255) ** 2)
    kill = (d < 105) & (a[..., 3] > 0)
    a[..., 3] = np.where(kill, 0, a[..., 3])
    edge = ndi.binary_dilation(a[..., 3] == 0, iterations=1) & (a[..., 3] > 0)
    pink = edge & (d < 150) & (np.minimum(a[..., 0], a[..., 2]) - a[..., 1] > 30)
    g = a[..., 1]
    for c in (0, 2):
        a[..., c] = np.where(pink, np.minimum(a[..., c], g + 25), a[..., c])
    Image.fromarray(a.astype(np.uint8), "RGBA").save(path)
    return int(kill.sum())


def rim_fix(path, band_px=3):
    """The darker purple rim purge() can't see: a painted edge that blended with the key reads (120, 40, 120),
    far from pure magenta, so the distance test leaves it. Any pixel within band_px of transparency whose hue
    is magenta (270-335 degrees) and is saturated takes the colour of the nearest clean pixel inside the
    sprite. Alpha is kept. NOT for sprites whose real colour is violet (an arcane wisp, a mana wyrm)."""
    import matplotlib.colors as mc
    a = np.array(Image.open(path).convert("RGBA"))
    op = a[..., 3] > 0
    dist = ndi.distance_transform_edt(op)
    hsv = mc.rgb_to_hsv(a[..., :3] / 255.0)
    h, sat = hsv[..., 0] * 360, hsv[..., 1]
    bad = op & (dist <= band_px) & (h >= 270) & (h <= 335) & (sat > 0.15)
    good = op & ~bad
    if not bad.any() or not good.any():
        return 0
    _, (iy, ix) = ndi.distance_transform_edt(~good, return_indices=True)
    for c in range(3):
        a[..., c] = np.where(bad, a[..., c][iy, ix], a[..., c])
    Image.fromarray(a, "RGBA").save(path)
    return int(bad.sum())


if __name__ == "__main__":
    files = []
    for p in sys.argv[1:]:
        files += sorted(glob.glob(os.path.join(p, "*.png"))) if os.path.isdir(p) else [p]
    for f in files:
        n = purge(f)
        if n > 30:
            print(f"{os.path.basename(f)}: {n} px")
