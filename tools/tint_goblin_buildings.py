"""Lightly tinted copies of the goblin town set, one colourway per port.

Kyle, 15 Nov 2026: "feel free to lightly tint goblin buildings for different towns if needed."

The goblin sheet came out in one palette, so four ports built from it would look like one port four times.
Each port gets a gentle wash toward its own light: Booty Bay keeps the originals (jungle and sea already
colour it), Ratchet goes dusty and warm like the Barrens, Steamwheedle Port bleaches toward Tanaris sand, and
Saltwheel cools toward salt flat and sea spray. The wash keeps each pixel's brightness, so the drawing reads
the same and only the colour of the light changes. Alpha is untouched.

    PYTHONPATH=. python3 tools/tint_goblin_buildings.py          # (re)write assets/buildings/tinted/<town>/
"""
import glob
import os

import numpy as np
from PIL import Image

SRC = "assets/buildings"
OUT = "assets/buildings/tinted"

#: town -> (tint colour, strength). Strength is how far each pixel moves toward the tinted grey.
TINTS = {
    "ratchet": ((214, 150, 96), 0.30),
    "steamwheedle_port": ((230, 204, 150), 0.30),
    "saltwheel": ((140, 184, 206), 0.30),
}


def tint(im, colour, strength):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3:]
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2])[..., None]
    c = np.array(colour, np.float32)
    washed = lum * (c / (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]))
    out = rgb * (1 - strength) + washed * strength
    return Image.fromarray(np.concatenate([np.clip(out, 0, 255), alpha], -1).astype(np.uint8), "RGBA")


def path_for(town, sprite):
    """The name a builder passes to bld() for a tinted goblin building: 'tinted/<town>/<sprite>'."""
    return f"tinted/{town}/{sprite}" if town in TINTS else sprite


def main():
    srcs = sorted(glob.glob(f"{SRC}/gob_*.png"))
    for town, (colour, strength) in TINTS.items():
        d = f"{OUT}/{town}"
        os.makedirs(d, exist_ok=True)
        for f in srcs:
            tint(Image.open(f), colour, strength).save(f"{d}/{os.path.basename(f)}", optimize=True)
        print(town, len(srcs))


if __name__ == "__main__":
    main()
