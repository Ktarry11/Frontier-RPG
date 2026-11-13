"""
Composite a zone's baked ground with its props, so you can look at what the player will actually see.

    PYTHONPATH=. python3 tools/zone_dressed_preview.py aspen --out /tmp/aspen_dressed.png [--scale 4]

WHY THIS EXISTS. A baker preview shows the GROUND only, because that is all the baker makes. But half of
what a forest zone looks like is the trees standing on it, and judging a forest from its soil is how you
end up with a zone that measures beautifully and plays like a car park. Until now the only way to see a
dressed zone was to launch the game and walk it, which does not work for the overview question - "does
this read as a mountain" - because the player's camera never sees more than a few dozen tiles.

So: load the baked chunks, paint them into one image, then paste every landmark sprite at its anchor in
draw order (north to south, so a tree in front overlaps the one behind it the way the game draws them).

Generic on purpose. Any zone module that exposes W, H, BAKED_DIR and a build that produces z.landmarks
can be previewed by adding one line to ZONES.
"""
import importlib
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

TILE_PX = 32

ZONES = {
    "aspen": "tools.handbuilt_aspen_wilderness",
    "weeping_ice": "tools.handbuilt_weeping_ice",
    "southern_needles": "tools.handbuilt_southern_needles",
    "shimmering_flats": "tools.handbuilt_shimmering_flats",
    "freewind": "tools.handbuilt_freewind_post",
    "drowning_floor": "tools.handbuilt_drowning_floor",
    "rocky_pass": "tools.handbuilt_rocky_pass",
    "crossing": "tools.handbuilt_return_voyage",
    "raider_deck": "tools.handbuilt_bloodsail_raider",
    "raider_hold": "tools.handbuilt_bloodsail_raider",
    "anchorage": "tools.handbuilt_bloodsail_galleon",
    "galleon_deck": "tools.handbuilt_bloodsail_galleon",
    "galleon_hold": "tools.handbuilt_bloodsail_galleon",
    "cabin": "tools.handbuilt_bloodsail_galleon",
    "black_strand": "tools.handbuilt_black_strand",
    "onyxhollow": "tools.handbuilt_onyxhollow",
    "dry_deep": "tools.handbuilt_dry_deep",
}

#: A cave module's entry point is build_<slug>_baked() rather than build_layout(), and it returns
#: (zone, layout) instead of a layout object. Both shapes are handled in build().
BUILDERS = {
    "weeping_ice": "build_weeping_ice_baked",
    "black_strand": "build_black_strand_baked",
    "onyxhollow": "build_onyxhollow_baked",
    "dry_deep": "build_dry_deep_baked",
    "freewind": "build_freewind_baked",
    "drowning_floor": "build_drowning_floor_baked",
    "rocky_pass": "build_rocky_pass_baked",
    "crossing": "build_crossing_baked",
    "raider_deck": "build_raider_deck_baked",
    "raider_hold": "build_raider_hold_baked",
    "anchorage": "build_anchorage_baked",
    "galleon_deck": "build_galleon_deck_baked",
    "galleon_hold": "build_galleon_hold_baked",
    "cabin": "build_cabin_baked",
}


def build(key):
    M = importlib.import_module(ZONES[key])
    fn = BUILDERS.get(key)
    if fn:
        zone, L = getattr(M, fn)()
        L.z = zone
        return M, L
    return M, M.build_layout()


def compose(key, out, scale=4, props=True):
    M, L = build(key)
    # The size comes from the zone: a module may hold several zones of different sizes
    # (handbuilt_bloodsail_galleon has four), so M.W would be wrong or absent.
    W, H = L.z.width, L.z.height
    canvas = Image.new("RGBA", (W * TILE_PX, H * TILE_PX), (18, 18, 20, 255))

    # open zones call it BAKED_DIR, cave modules call it BAKED
    baked = getattr(M, "BAKED_DIR", None) or getattr(M, "BAKED", "")
    if "{}" in baked:
        baked = baked.format(key)
    baked = ROOT / baked
    n = 0
    # Bakers write JPEG chunks (ground_<cx>_<cy>.jpg); accept PNG too in case a baker changes.
    files = sorted(list(baked.glob("*.jpg")) + list(baked.glob("*.png")))
    for f in files:
        # chunk files are named <...>_<cx>_<cy>.png in tile coordinates
        stem = f.stem.split("_")
        try:
            cx, cy = int(stem[-2]), int(stem[-1])
        except (ValueError, IndexError):
            continue
        canvas.alpha_composite(Image.open(f).convert("RGBA"), (cx * TILE_PX, cy * TILE_PX))
        n += 1
    print(f"ground: {n} chunks")

    if props:
        marks = list(getattr(L.z, "landmarks", []) or [])
        # Draw order is north to south. A sprite's anchor is its BASE, so sorting on anchor_y makes the
        # tree lower down the screen overlap the one behind it - the same order the game's renderer uses.
        marks.sort(key=lambda m: m.get("anchor_y", 0))
        cache = {}
        drawn = 0
        for m in marks:
            k = m["sprite_key"]
            if k not in cache:
                p = ROOT / k
                cache[k] = Image.open(p).convert("RGBA") if p.exists() else None
            im = cache[k]
            if im is None:
                continue
            # THE ANCHOR IS THE SPRITE'S TOP-LEFT, NOT ITS BOTTOM-CENTRE.
            #
            # Tilemap.add_landmark documents anchor_x/anchor_y as "top-left", and the game blits at
            # world_to_screen(anchor_x, anchor_y) with no offset (ui/tilemap_renderer.py). This tool
            # used to paste at (ax - width/2, ay - height), so every prop in every preview came out half
            # a sprite-width to the LEFT and a full sprite-height ABOVE its real position - which over
            # Freewind's drop looked exactly like the buildings were floating off the mesas. They were
            # not. The preview was lying, and two props got moved to chase a bug that was in here.
            ax = int(m.get("anchor_x", 0) * TILE_PX)
            ay = int(m.get("anchor_y", 0) * TILE_PX)
            wpx = int(m.get("width_tiles", 1) * TILE_PX)
            hpx = int(m.get("height_tiles", 1) * TILE_PX)
            if wpx < 1 or hpx < 1:
                continue
            s = im.resize((wpx, hpx), Image.LANCZOS)
            canvas.alpha_composite(s, (ax, ay))
            drawn += 1
        print(f"props: {drawn} of {len(marks)} landmarks")

    img = canvas.convert("RGB")
    if scale and scale != TILE_PX:
        img = img.resize((W * scale, H * scale), Image.LANCZOS)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    key = next((a for a in args if a in ZONES), "aspen")
    out = args[args.index("--out") + 1] if "--out" in args else f"/tmp/{key}_dressed.png"
    scale = int(args[args.index("--scale") + 1]) if "--scale" in args else 4
    compose(key, out, scale, props="--no-props" not in args)
