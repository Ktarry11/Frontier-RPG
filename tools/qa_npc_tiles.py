#!/usr/bin/env python3
"""No NPC stands sealed inside rock.

    PYTHONPATH=. python3 tools/qa_npc_tiles.py

Found 13 Nov: the live Ragefire Chasm map had an NPC tile at (100,100) inside solid rock that no
data file accounted for. Nobody could see or reach it. By 14 Nov it was gone (the cave smoothing
and secret-door passes rebuilt that map), but nothing would have caught it coming back, on that map
or any other.

ONE CLAIM: every "npc" tile on every finished map can be walked up to - at least one of the four
tiles beside it is open ground. An NPC whose four sides are rock is a person nobody can talk to.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    bad, total = [], 0
    for name, entry in sorted(zm.zones.items()):
        z = entry["tilemap"]
        for y in range(z.height):
            for x in range(z.width):
                if z.interaction_layer[y][x] != "npc":
                    continue
                total += 1
                if not any(0 <= x + dx < z.width and 0 <= y + dy < z.height
                           and z.collision_layer[y + dy][x + dx] is None and z.is_walkable(x + dx, y + dy)
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    bad.append(f"{name} ({x},{y}): an NPC tile with rock on all four sides")
    print(f"{total} NPC tiles across {len(zm.zones)} maps")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:30]:
            print("  -", b)
        return 1
    print("\nNPC tiles OK - everyone can be walked up to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
