#!/usr/bin/env python3
"""Every cave the bakers smoothed is smoothed the same way in the game, and no secret was touched.

    PYTHONPATH=. python3 tools/qa_cave_smoothing.py

Backlog O [86] (Kyle: "no 1-tile jags on walkable edges, minimum corridor width"). The rule and why it
lives in two places is in world/cave_smoothing.py. What this checks:
  1. every cave in data/world/smoothed_caves.json exists in the game;
  2. every tile its baker opened is floor in the game, so nobody walks into painted floor and hits rock;
  3. no opened tile is within two tiles of a secret, so every hidden way in still looks solid.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from world.cave_smoothing import listed, secret_guard
    from world.zone_generator import create_all_zones
    zones = create_all_zones()
    caves = listed()
    bad = []
    opened = 0
    for name, tiles in caves.items():
        z = zones.get(name)
        if z is None:
            bad.append(f"{name}: no such map")
            continue
        opened += len(tiles)
        shut = [t for t in tiles if z.collision_layer[t[1]][t[0]] is not None]
        if shut:
            bad.append(f"{name}: {len(shut)} painted-open tiles are rock in the game, e.g. {shut[:3]}")
        near = [t for t in tiles if tuple(t) in secret_guard(name)]
        if near:
            bad.append(f"{name}: {len(near)} opened tiles next to a secret, e.g. {near[:3]}")
    print(f"{len(caves)} caves smoothed, {opened} snag tiles opened")
    if bad:
        for b in bad:
            print("  -", b)
        return 1
    print("\ncave smoothing OK - painting and floor agree, and every secret still looks like rock.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
