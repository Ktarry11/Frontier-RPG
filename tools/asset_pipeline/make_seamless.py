"""
Seamless tile edge-blending tool.

Origin: built ad-hoc mid-session to fix visible seams in 2 of 15 cropped
Barrens grass tiles (thorny_brush, grass_with_flowers - both had a faint
but real horizontal seam confirmed via 3x3 self-tile render tests).
Generalized here into a real reusable tool per Kyle: "This game will
eventually have 1000s of zones... let's set up the system fully" - every
future tileset drop should run through this before being wired into
tile_textures.py, not get a bespoke one-off script per zone.

WHAT THIS DOES NOT FIX: this only smooths the boundary between a tile
and ITSELF (for when the same tile repeats). It does not fix banding
caused by a bad variant-picker (see get_texture_entry's 2D hash fix,
same session) and does not add real texture variety - it just makes a
single tile's edges wrap cleanly.

Usage:
    python make_seamless.py <input_dir> <output_dir> [--blend-px 20]

Every .png in input_dir gets edge-blended and written to output_dir
with the same filename. Non-square images are center-cropped to square
first (a real bug caught this session: a 3x5 grid crop from a
1254x1254 sheet used the WRONG divisor for one axis, producing
251x418 "tiles" that visibly stretched when rendered - square is
enforced here so that mistake can't ship silently again).
"""
import sys
import os
import argparse
import numpy as np
from PIL import Image


def make_square(im):
    """Center-crop to square using the smaller dimension. Returns the
    crop unchanged if already square."""
    w, h = im.size
    if w == h:
        return im
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return im.crop((left, top, left + side, top + side))


def make_seamless(im, blend_px=20):
    """Make a tile wrap cleanly using an OVERLAP cross-fade.

    The first `b` columns/rows are cross-faded with the `b` columns/rows
    that sit just past the tile's last full column (i.e. the image is
    treated as if its far edge overlaps its near edge by b px). The result
    is (w-b)x(h-b) and is truly periodic - pixel (w-b-1) is the real
    neighbour of pixel 0 in the source - so it is then resized back to the
    input size so callers still get the size they passed in.

    BUG FIXED (this version): the previous implementation blended the left
    strip with weights `left*(1-alpha_rev) + right*alpha`, which equals
    `2*alpha` in total - the first column went BLACK and the last of the
    strip went double-bright, drawing a dark double line at every wrap.
    It went unnoticed on the Barrens grass (the line is 1-2px on a 900px
    texture) but was glaring on 32px-per-tile cave floors."""
    arr = np.array(im.convert("RGB")).astype(np.float64)
    h, w = arr.shape[:2]
    b = min(blend_px, w // 4, h // 4)
    if b < 2:
        return im  # too small to blend meaningfully, return as-is

    # Horizontal overlap: columns [0,b) fade from the far strip (x+w-b)
    # into the near strip (x); everything else is untouched.
    t = np.linspace(0, 1, b, endpoint=False).reshape(1, b, 1)
    hb = arr[:, :w - b].copy()
    hb[:, :b] = arr[:, w - b:] * (1 - t) + arr[:, :b] * t

    # Vertical overlap on the horizontally-fixed result, so both axes wrap.
    t = np.linspace(0, 1, b, endpoint=False).reshape(b, 1, 1)
    out = hb[:h - b, :].copy()
    out[:b, :] = hb[h - b:, :] * (1 - t) + hb[:b, :] * t

    res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return res.resize((w, h), Image.LANCZOS)


def self_tile_preview(im, grid=3):
    """Build an NxN self-tiled preview for visual seam verification.
    Always eyeball this before shipping a tile - the blend math can
    still leave a faint seam on high-contrast source art (2 of the 15
    Barrens tiles needed the blend specifically because they weren't
    seamless even though most of the batch was fine)."""
    w, h = im.size
    preview = Image.new(im.mode, (w * grid, h * grid))
    for r in range(grid):
        for c in range(grid):
            preview.paste(im, (c * w, r * h))
    return preview


def process_directory(input_dir, output_dir, blend_px=20, save_previews=True):
    os.makedirs(output_dir, exist_ok=True)
    preview_dir = os.path.join(output_dir, "_previews")
    if save_previews:
        os.makedirs(preview_dir, exist_ok=True)

    results = []
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".png"):
            continue
        path = os.path.join(input_dir, fname)
        im = Image.open(path)
        orig_size = im.size

        squared = make_square(im)
        seamless = make_seamless(squared, blend_px=blend_px)

        out_path = os.path.join(output_dir, fname)
        seamless.save(out_path)

        if save_previews:
            preview = self_tile_preview(seamless, grid=3)
            preview.save(os.path.join(preview_dir, fname))

        results.append({
            "file": fname,
            "orig_size": orig_size,
            "final_size": seamless.size,
            "was_cropped_to_square": orig_size != squared.size,
        })

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--blend-px", type=int, default=20)
    parser.add_argument("--no-previews", action="store_true")
    args = parser.parse_args()

    results = process_directory(
        args.input_dir, args.output_dir,
        blend_px=args.blend_px,
        save_previews=not args.no_previews,
    )

    print(f"Processed {len(results)} tiles -> {args.output_dir}")
    for r in results:
        flag = " [CENTER-CROPPED TO SQUARE]" if r["was_cropped_to_square"] else ""
        print(f"  {r['file']}: {r['orig_size']} -> {r['final_size']}{flag}")
    if not args.no_previews:
        print(f"3x3 self-tile previews written to {os.path.join(args.output_dir, '_previews')}")
        print("ALWAYS eyeball these before wiring into tile_textures.py - "
              "the blend can still leave a faint seam on high-contrast art.")
