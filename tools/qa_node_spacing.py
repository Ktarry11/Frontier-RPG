#!/usr/bin/env python3
"""No two gathering nodes stand shoulder to shoulder, and a node draws its whole icon.

    python3 tools/qa_node_spacing.py

Kyle, 13 Nov 2026: "why are we having so many issues cropping gatherables?" and, with a second
screenshot, "there it is again bro! why!?!?!" Two nodes on neighbouring tiles: each is drawn a tile
and a half wide, so the second covers the first and leaves a sliver of it. Not a cropping fault.
And a real crop: the renderer cut 32x32 from icons that are 64x64 (every gem and every fish).
"""
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((64, 64))
    from core.game_state import GameStateManager
    from entities.character import Character
    from world.gathering_manager import GatheringNodeManager
    sm = GameStateManager(screen)
    sm.player = Character(name="Audit", char_class="Warrior", level=60)
    zm = sm._live_zone_manager()
    gm = GatheringNodeManager()
    bad, zones, nodes = [], 0, 0
    random.seed(5)
    for name, rec in zm.zones.items():
        for _ in range(2):
            gm.clear()
            gm.populate(rec["tilemap"], name)
            spots = [(n.x, n.y) for n in gm.active_nodes]
            nodes += len(spots)
            close = [(a, b) for i, a in enumerate(spots) for b in spots[i + 1:]
                     if abs(a[0] - b[0]) < 2 and abs(a[1] - b[1]) < 2]
            if close:
                bad.append(f"{name}: nodes side by side at {close[:2]}")
            # put the tiles back so the second roll starts clean
            for (x, y) in spots:
                rec["tilemap"].set_tile(x, y, None, "interaction")
        zones += 1
    src = (ROOT / "ui" / "tilemap_renderer.py").read_text(encoding="utf-8")
    if "(0, 0, 32, 32), max(node_w, node_h)" in src:
        bad.append("ui/tilemap_renderer.py crops a fixed 32x32 out of a node icon again")
    print(f"{zones} zones, {nodes} nodes rolled")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad[:12]:
            print("  " + b)
        return 1
    print("OK: no two nodes touch, and a node draws its whole icon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
