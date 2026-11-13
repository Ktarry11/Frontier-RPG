#!/usr/bin/env python3
"""Can the player actually get to everything in a zone?

    python3 tools/audit_zone_reachable.py "Glittervein" ["Southern Thousand Needles" ...]

Loads the LIVE zone (the one the game builds, with NPCs, chests, nodes, portals and props on it),
floods out from every arrival, and lists each thing the player is meant to touch that has no
reachable tile beside it. Written 13 Nov 2026 for the Needles / Tanaris region rework, where the
ground, the props and one whole descent were changed under content that was placed by coordinate.
"""
import os
import sys
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def audit(zm, name):
    z = zm.zones[name]["tilemap"]
    W, H = z.width, z.height
    starts = [p for p in (getattr(z, "arrivals", None) or [])] or []
    for y in range(H):
        for x in range(W):
            if z.interaction_layer[y][x] == "portal":
                starts.append((x, y))
    seen, q = set(), deque()
    for (x, y) in starts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if 0 <= n[0] < W and 0 <= n[1] < H and z.is_walkable(*n) and n not in seen:
                    seen.add(n)
                    q.append(n)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    kinds, lost = Counter(), []
    for y in range(H):
        for x in range(W):
            kind = z.interaction_layer[y][x]
            if not kind:
                continue
            kinds[kind] += 1
            near = any((x + dx, y + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if not near:
                lost.append((kind, x, y))
    walk = sum(z.is_walkable(x, y) for y in range(H) for x in range(W))
    return dict(reachable=len(seen), walkable=walk, kinds=dict(kinds), lost=lost)


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((64, 64))
    from core.game_state import GameStateManager
    from entities.character import Character
    sm = GameStateManager(screen)
    sm.player = Character(name="Audit", char_class="Warrior", level=60)
    zm = sm._live_zone_manager()
    bad = 0
    for name in sys.argv[1:]:
        if name not in zm.zones:
            print(f"{name}: no such zone")
            bad += 1
            continue
        r = audit(zm, name)
        print(f"{name}: {r['reachable']} of {r['walkable']} walkable tiles reachable; {r['kinds']}")
        for (kind, x, y) in r["lost"]:
            print(f"    CANNOT BE REACHED: {kind} at ({x},{y})")
        bad += len(r["lost"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
