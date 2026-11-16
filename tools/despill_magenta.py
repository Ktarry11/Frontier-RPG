#!/usr/bin/env python3
"""Pull leftover magenta spill out of keyed sprites. Idempotent.

    PYTHONPATH=. python3 tools/despill_magenta.py <file.png> [...]

A sheet generated on #FF00FF leaves the key colour in two places the slicer's soft alpha can't reach: the fringe
of busy edges (needle foliage comes back purple-flecked) and anything semi-transparent the model painted over the
key (smoke comes back pink). Magenta spill lifts red AND blue above green together, so the amount both sit above
green is the spill, and it comes off both. A real red (paint, blood, a banner) has low blue and a real orange
(lava) has low blue too, so neither is touched.
"""
import sys

import numpy as np
from PIL import Image


def despill(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im, np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spill = np.clip(np.minimum(r, b) - g, 0, None)
    a[..., 0] = r - spill
    a[..., 2] = b - spill
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(path)
    return float((spill > 8).mean())


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f"{f}: {despill(f) * 100:.1f}% of pixels de-spilled")
