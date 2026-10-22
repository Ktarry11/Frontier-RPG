"""Quick structural picture of a hand-built cave (walls / floor / water / props / markers / trash packs).

    PYTHONPATH=. python3 tools/dungeon_preview.py moonwell|barrows|groms [out.png]
"""
import importlib
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

KEYS = {"moonwell": ("tools.handbuilt_moonwell_hollow", "build_moonwell_baked"),
        "barrows": ("tools.handbuilt_howling_barrows", "build_barrows_baked"),
        "groms": ("tools.handbuilt_groms_rest", "build_groms_baked")}


def render(zone, L, path, scale=8, trash=None):
    img = np.zeros((zone.height, zone.width, 3), np.uint8)
    for y in range(zone.height):
        for x in range(zone.width):
            c = (24, 24, 30)
            if zone.is_walkable(x, y):
                c = (150, 135, 100)
                b = zone.base_layer[y][x]
                if b == "shallow_water":
                    c = (90, 160, 210)
                elif b == "deep_water":
                    c = (40, 80, 150)
            elif zone.collision_layer[y][x] == "landmark":
                c = (200, 70, 60)
            img[y, x] = c
    im = Image.fromarray(img).resize((zone.width * scale, zone.height * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for (x, y, n, lvl) in (trash if trash is not None else getattr(zone, "trash_spawns", []) or []):
        d.ellipse([x * scale + 1, y * scale + 1, (x + 1) * scale - 1, (y + 1) * scale - 1], fill=(255, 140, 0))
    for (x, y, n) in getattr(zone, "boss_positions", []) or []:
        d.ellipse([x * scale - 3, y * scale - 3, (x + 1) * scale + 3, (y + 1) * scale + 3], fill=(255, 255, 0))
    mods = {"chest": (60, 220, 90), "portal": (255, 0, 255)}
    for y in range(zone.height):
        for x in range(zone.width):
            k = zone.interaction_layer[y][x] if hasattr(zone, "interaction_layer") else None
            if k in mods:
                d.rectangle([x * scale, y * scale, (x + 1) * scale, (y + 1) * scale], fill=mods[k])
    im.save(path)


if __name__ == "__main__":
    mod, fn = KEYS[sys.argv[1]]
    zone, L = getattr(importlib.import_module(mod), fn)()
    out = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/claude-0/-home-claude/30d87233-f87c-5af4-8dcf-f392a0bc59b8/scratchpad/{sys.argv[1]}_plan.png"
    render(zone, L, out)
    print(out, "props", L.placed, "skipped", len(L.skipped))
    for s in L.skipped:
        print("  skip", s)
