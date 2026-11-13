#!/usr/bin/env python3
"""Which props stand on the same ground, before the game clears them? Report only.

    PYTHONPATH=. python3 tools/audit_prop_overlap.py [--zone "Name"]

The rule and the measuring live in world/prop_clearance.py, which removes the lesser prop of each
pair on every finished map. This lists what it will remove, by zone, read from the maps as the
generators leave them - so it is the list of placements worth fixing at the source one day.
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
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((1, 1))
        from world.zone_generator import create_all_zones
        from world import prop_clearance as PC
        zones = create_all_zones()
    only = sys.argv[sys.argv.index("--zone") + 1] if "--zone" in sys.argv else None
    total = 0
    for name, z in sorted(zones.items()):
        if only and name != only:
            continue
        found = PC.shared_ground(z)
        if not found:
            continue
        total += len(found)
        print(f"{name}: {len(found)}")
        for (f, a, b) in sorted(found, key=lambda r: -r[0]):
            print(f"    {f:4.0%}  {PC._name(a)[:-4]} ({a['anchor_x']},{a['anchor_y']})"
                  f"  and  {PC._name(b)[:-4]} ({b['anchor_x']},{b['anchor_y']})")
    print(f"\n{total} pair(s) share ground as generated; the game removes one prop of each.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
