"""
Hue-shift tinting for boss portrait icons. Shifts only the Hue channel of
an HSV decomposition (Saturation/Value/Alpha untouched), so linework,
shading and highlights are all fully preserved - only the color family
changes. This is what lets 8 real creature sprites (Kyle's
spritesheets.zip upload, 2026-09-06) cover 12 distinct boss "template"
archetypes without every shared-sprite template looking identical: e.g.
demon_caster and elemental_bruiser both start from a mage spritesheet,
but land as visually distinct hot-red vs green-tinted portraits.

A flat color multiply (tint = original * color) was considered and
rejected - it muddies dark shading and can wash out linework on sprites
this small (64x64), where every remaining pixel of contrast matters for
readability. HSV hue rotation keeps the source art's actual shading
intact and just spins its color wheel position.
"""
import numpy as np
from PIL import Image


def hue_shift(img, degrees):
    """Return a copy of img (RGBA) with its Hue channel rotated by
    `degrees` (0-360, wraps). Saturation, Value and Alpha are untouched."""
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    hsv = Image.merge("RGB", (r, g, b)).convert("HSV")
    h, s, v = hsv.split()

    h_arr = np.array(h, dtype=np.int16)
    shift = int(round(degrees / 360 * 256)) % 256
    h_arr = (h_arr + shift) % 256
    h_new = Image.fromarray(h_arr.astype("uint8"), "L")

    rgb_new = Image.merge("HSV", (h_new, s, v)).convert("RGB")
    r2, g2, b2 = rgb_new.split()
    return Image.merge("RGBA", (r2, g2, b2, a))
