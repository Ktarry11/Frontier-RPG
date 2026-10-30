"""Render an UNBAKED zone straight from its tiles, plus its props.

    PYTHONPATH=. python3 tools/zone_tile_preview.py <module>:<builder> --out shot.png [--scale 6]

e.g. PYTHONPATH=. python3 tools/zone_tile_preview.py \
         tools.handbuilt_return_voyage:build_the_crossing --out /tmp/crossing.png

WHY A SECOND PREVIEW TOOL. tools/zone_dressed_preview.py composites BAKED ground chunks, which is
the right thing for a zone that has been through a baker. The ship zones have not: they render from
tile colours in-game, the same way Ragefire Chasm does, so there are no chunks to composite and
that tool draws a black rectangle with some barrels on it.

This paints each tile its registry colour, darkens blocking tiles so the collision layer is
visible, and then pastes the landmarks in north-to-south draw order at their TOP-LEFT anchors -
which is where Tilemap.add_landmark actually puts them, and where the other preview tool learned
the hard way to paste them after half a session of chasing props that looked like they were
floating.

Blocking tiles are drawn, not left blank, because on these maps the blocking tile is the sea and
the sea is most of the picture.
"""
import argparse
import importlib
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from world.tiles import get_tile_color  # noqa: E402


def build(spec):
    """'<module>:<fn>' -> zone. The builder may return a zone, (zone, L) or
    (zone, L, extras); all three shapes show up across the handbuilt modules."""
    mod_name, fn_name = spec.split(":")
    M = importlib.import_module(mod_name)
    res = getattr(M, fn_name)()
    zone, L = (res, None) if not isinstance(res, tuple) else (res[0], res[1] if len(res) > 1 else None)
    # Dress it if the module separates dressing from building, so the preview shows what the
    # player sees rather than an undressed hull.
    if L is not None and hasattr(M, "dress") and not getattr(zone, "landmarks", None):
        M.dress(zone, L)
    return zone


def render(zone, scale=6, grid=0):
    W, H = zone.width, zone.height
    img = Image.new("RGB", (W, H), (10, 10, 12))
    px = img.load()
    for y in range(H):
        for x in range(W):
            base = zone.base_layer[y][x]
            col = get_tile_color(base) if base else (10, 10, 12)
            if not zone.is_walkable(x, y):
                # Blocking: same hue, darker. Keeps the sea reading as sea while making the
                # difference between "deck" and "water painted to look like deck" obvious.
                col = tuple(int(c * 0.72) for c in col)
            px[x, y] = col
    # interaction markers on top, at tile resolution
    for y in range(H):
        for x in range(W):
            mark = zone.interaction_layer[y][x]
            if mark == "portal":
                px[x, y] = (255, 230, 90)
            elif mark == "boss_marker":
                px[x, y] = (255, 70, 70)
            elif mark == "chest":
                px[x, y] = (255, 160, 40)

    img = img.resize((W * scale, H * scale), Image.NEAREST)
    canvas = img.convert("RGBA")

    marks = sorted(list(getattr(zone, "landmarks", []) or []),
                   key=lambda m: m.get("anchor_y", 0))
    cache = {}
    drawn = 0
    for m in marks:
        key = m["sprite_key"]
        if key not in cache:
            p = ROOT / key
            cache[key] = Image.open(p).convert("RGBA") if p.exists() else None
        im = cache[key]
        if im is None:
            continue
        ax = int(m.get("anchor_x", 0) * scale)
        ay = int(m.get("anchor_y", 0) * scale)
        wpx = max(1, int(m.get("width_tiles", 1) * scale))
        hpx = max(1, int(m.get("height_tiles", 1) * scale))
        canvas.alpha_composite(im.resize((wpx, hpx), Image.LANCZOS), (ax, ay))
        drawn += 1
    print(f"  {zone.name}: {W}x{H}, {drawn} of {len(marks)} props drawn")
    return canvas.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="module.path:builder_fn")
    ap.add_argument("--out", default="/tmp/zone.png")
    ap.add_argument("--scale", type=int, default=6, help="pixels per tile")
    args = ap.parse_args()

    zone = build(args.spec)
    img = render(zone, args.scale)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
