"""Extract clean square tiles from "UI card" cave sources.

WHY THIS EXISTS
---------------
assets/tiles/caves/{cave_floor_rock_*,cave_wall_*,cave_water_pool,
rubble_strewn_floor,mossy_cave_floor,cave_moss_clump}.png are crops of a
card-style sheet: ~85x132 images with a dark navy margin and a light-blue
frame baked around the real art. Rendering one of those per 32px tile
squashed the frame + margin into EVERY tile, producing a dark grid line
between every pair of tiles (Kyle: "a visible gap between tiled zone in
dungeons and some caves").

This script crops the real art out from inside the frame, takes TWO
square variants per source (top-aligned and bottom-aligned, so each card
yields two distinct tiles), and upscales them. Run make_seamless.py on the
output afterwards so each tile repeats with no visible seam, then LOOK at
the _previews/ 3x3 sheets before wiring anything in.

Usage:
    python3 tools/asset_pipeline/extract_card_tiles.py <in_dir> <out_dir> \
        name1 name2|out=file.png ... [--size 256] [--auto]

    --auto  trim dark margins/frames automatically instead of the fixed
            cave-card insets (use for Durotar crops, wc_* strips, etc).
"""
import os
import sys

from PIL import Image

# Measured from the sources (row/column luminance profiles): frame lines
# sit at x~1-3 and x~w-3, y~10-12 and y~h-12; real art starts ~2px inside.
INSET_X = 6
INSET_Y = 15


def auto_bounds(im, dark=48, pad=4):
    """Trim dark margins/frames automatically: peel rows/columns off each
    side while their mean luminance is below `dark`, then `pad` more px to
    drop the anti-aliased frame line. For sources that aren't the fixed
    cave-card layout (Durotar crops, wc_* strips)."""
    import numpy as np
    a = np.array(im.convert("L")).astype(float)
    h, w = a.shape
    x0, x1, y0, y1 = 0, w, 0, h
    while x0 < x1 - 8 and a[y0:y1, x0].mean() < dark:
        x0 += 1
    while x1 > x0 + 8 and a[y0:y1, x1 - 1].mean() < dark:
        x1 -= 1
    while y0 < y1 - 8 and a[y0, x0:x1].mean() < dark:
        y0 += 1
    while y1 > y0 + 8 and a[y1 - 1, x0:x1].mean() < dark:
        y1 -= 1
    return x0 + pad, x1 - pad, y0 + pad, y1 - pad


def extract(in_path, out_dir, name, size, auto=False):
    im = Image.open(in_path).convert("RGB")
    w, h = im.size
    if auto:
        x0, x1, y0, y1 = auto_bounds(im)
    else:
        x0, x1 = INSET_X, w - INSET_X
        y0, y1 = INSET_Y, h - INSET_Y
    side = min(x1 - x0, y1 - y0)
    # Horizontally centered; one variant aligned to the top of the art,
    # one to the bottom.
    cx0 = x0 + ((x1 - x0) - side) // 2
    variants = {
        "a": (cx0, y0, cx0 + side, y0 + side),
        "b": (cx0, y1 - side, cx0 + side, y1),
    }
    for tag, box in variants.items():
        tile = im.crop(box).resize((size, size), Image.LANCZOS)
        tile.save(os.path.join(out_dir, f"{name}_{tag}.png"))
    return side


def main():
    args = [a for a in sys.argv[1:]]
    size = 256
    if "--size" in args:
        i = args.index("--size")
        size = int(args[i + 1])
        del args[i:i + 2]
    auto = "--auto" in args
    if auto:
        args.remove("--auto")
    in_dir, out_dir, names = args[0], args[1], args[2:]
    os.makedirs(out_dir, exist_ok=True)
    for n in names:
        # name may be "outname=filename.png" when the source file's name
        # differs from the name you want the tiles saved under.
        out_name, _, fname = n.partition("=")
        fname = fname or f"{out_name}.png"
        side = extract(os.path.join(in_dir, fname), out_dir, out_name, size, auto)
        print(f"{n}: {side}px square -> {size}px x2 variants")


if __name__ == "__main__":
    main()
