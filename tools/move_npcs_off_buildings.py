"""Move every NPC that is drawn under a building, tree or banner to clear ground beside it.

    python3 tools/move_npcs_off_buildings.py [--apply]

Backlog C [34]. tools/audit_npcs_on_props.py finds them (a prop's picture is bigger than its
footprint, so an NPC just behind the footprint is drawn on the roof). This picks the nearest
tile - in front of the building first - that is walkable, has nothing drawn over it, is not a
door or another NPC, and has a walkable neighbour, then rewrites the NPC's position where it is
stored (ambient_npcs.json, vendors.json or recruits.json). Anything it cannot find a source or
a tile for is printed, not guessed.
"""
import collections
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    apply = "--apply" in sys.argv
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from PIL import Image
    from core.game_state import GameStateManager
    from entities.character import Character
    from world.zone_keys import zone_key
    sm = GameStateManager(screen)
    sm.player = Character(name="H", char_class="Warrior", level=60)
    zm = sm._live_zone_manager()
    cache = {}

    def cover(l, x, y):
        ax, ay, w, h = l["anchor_x"], l["anchor_y"], l["width_tiles"], l["height_tiles"]
        if not (ax <= x < ax + w and ay <= y < ay + h):
            return 0.0
        key = (l["sprite_key"], w, h)
        if key not in cache:
            try:
                cache[key] = Image.open(l["sprite_key"]).convert("RGBA").resize((w * 16, h * 16)).getchannel("A")
            except Exception:
                cache[key] = None
        a = cache[key]
        if a is None:
            return 0.0
        px = list(a.crop(((x - ax) * 16, (y - ay) * 16, (x - ax) * 16 + 16, (y - ay) * 16 + 16)).getdata())
        return sum(1 for v in px if v > 128) / len(px)

    files = {"ambient": ("data/npcs/ambient_npcs.json", "npcs"), "vendor": ("data/npcs/vendors.json", "vendors"),
             "recruit": ("data/npcs/recruits.json", "recruits")}
    data = {k: json.load(open(p)) for k, (p, _) in files.items()}
    where = collections.defaultdict(list)
    for kind, (_p, key) in files.items():
        for row in data[kind][key]:
            if isinstance(row, dict) and row.get("x") is not None and row.get("zone"):
                where[(zone_key(row["zone"]), row["x"], row["y"])].append((kind, row))

    moved = stuck = 0
    for name, e in zm.zones.items():
        t = e["tilemap"] if isinstance(e, dict) else e
        lms = list(getattr(t, "landmarks", []) or [])
        npcs = {(x, y) for y in range(t.height) for x in range(t.width) if t.interaction_layer[y][x] == "npc"}
        covered = lambda x, y: max([cover(l, x, y) for l in lms] or [0.0])
        for (x, y) in sorted(npcs):
            if covered(x, y) <= 0.5:
                continue
            rows = where.get((zone_key(name), x, y))
            if not rows:
                print(f"  ?? {name} ({x},{y}): no stored NPC at this tile (placed in code)")
                stuck += 1
                continue
            best = None
            for d in range(1, 9):
                ring = [(x + dx, y + dy) for dx in range(-d, d + 1) for dy in range(-d, d + 1) if max(abs(dx), abs(dy)) == d]
                ring.sort(key=lambda p: (-(p[1] - y), abs(p[0] - x)))          # in front (south) first
                for (nx, ny) in ring:
                    if not (1 <= nx < t.width - 1 and 1 <= ny < t.height - 1):
                        continue
                    if not t.is_walkable(nx, ny) or t.interaction_layer[ny][nx]:
                        continue
                    if covered(nx, ny) > 0.15:
                        continue
                    if any(abs(nx - ox) <= 1 and abs(ny - oy) <= 1 for (ox, oy) in npcs if (ox, oy) != (x, y)):
                        continue
                    if not any(t.is_walkable(nx + a, ny + b) for a, b in ((0, 1), (1, 0), (-1, 0), (0, -1))):
                        continue
                    best = (nx, ny)
                    break
                if best:
                    break
            if not best:
                print(f"  ?? {name} ({x},{y}): no clear tile within 8")
                stuck += 1
                continue
            for kind, row in rows:
                print(f"  {name}: {row.get('name')} ({x},{y}) -> {best}")
                row["x"], row["y"] = best
            npcs.discard((x, y))
            npcs.add(best)
            moved += 1
    if apply:
        for kind, (p, _k) in files.items():
            Path(p).write_text(json.dumps(data[kind], indent=2, ensure_ascii=False) + "\n")
    print(f"{moved} moved{'' if apply else ' (dry run)'}, {stuck} not moved")


if __name__ == "__main__":
    main()
