#!/usr/bin/env python3
"""The two Collection forms that need a tint, made from creature art the game already has. Idempotent.

    python3 tools/build_collection_art.py

Every other form wears a creature's own sprite (tools/build_collection.py). The Spirit Wolf is a timber wolf gone
ghost-blue and see-through, and the Shade of the Drowned Court a drowned noble gone sea-blue. The mount colourways are
hue-shifted when they're drawn, not stored (world/collection_art.py).
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
FORMS = ROOT / "assets" / "collection" / "forms"


def tint(im, rgb, keep, bright, alpha):
    """Lay the picture's own light and shade over one colour (a ghost needs a real tint, not a hue turn)."""
    from PIL import ImageEnhance
    im = im.convert("RGBA")
    r, g, b, a = im.split()
    lum = ImageEnhance.Brightness(Image.merge("RGB", (r, g, b)).convert("L").convert("RGB")).enhance(bright)
    lum = lum.convert("L")
    out = Image.merge("RGB", tuple(lum.point(lambda v, c=c: min(255, int(v * c / 160))) for c in rgb))
    out = Image.blend(out, Image.merge("RGB", (r, g, b)), keep)
    out.putalpha(a.point(lambda v: int(v * alpha)))
    return out


def main():
    FORMS.mkdir(parents=True, exist_ok=True)
    for name, src, rgb, keep, bright, alpha in (
            ("spirit_wolf", "az_timber_wolf", (150, 210, 255), 0.1, 1.3, 0.72),
            ("shade_of_the_drowned_court", "az_ghost_noble", (40, 100, 200), 0.25, 1.05, 0.8)):
        im = tint(Image.open(ROOT / "assets" / "creatures" / f"{src}.png"), rgb, keep, bright, alpha)
        im.save(FORMS / f"{name}.png")
        print(f"  {name}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
