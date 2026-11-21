#!/usr/bin/env python3
"""Links (world/links.py): short-range ways across a gap on the same map.

    PYTHONPATH=. python3 tools/qa_links.py

Kyle, 21 Nov 2026: "Can we do little short range portals that link islands instead of bridges? Like a new system".
Checks, on every live map that has links:
  1. every pad is a "link" interaction tile you can stand on, and its landing beside the partner is walkable
  2. links come in pairs: each pad's partner leads back to it, and a pad's landing is beside its partner, not itself
  3. every kind is a known kind with words for the player
  4. through the real ZoneManager: standing on a pad and crossing puts the player at the landing, on the same map
  5. a map that uses links is whole: every walkable tile is reachable from its start once the links count, and the
     same map with its links taken away is NOT (otherwise the link is a shortcut, which is fine, but say so)
  6. the Firmament leans on them (Kyle: "more heavily found later") and one or two come before it
"""
import contextlib
import io
import os
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

FAILS = []
NOTES = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)


def flood(z, start, use_links=True):
    from world.links import edges
    jumps = edges(z) if use_links else {}
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        steps = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if (x, y) in jumps:
            steps.append(jumps[(x, y)])
        for n in steps:
            if 0 <= n[0] < z.width and 0 <= n[1] < z.height and n not in seen and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def main():
    from world.links import KINDS, message
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        zones = create_all_zones()
    starts = {"The Fading Firmament": ("tools.handbuilt_worldtree_fading_firmament", "START"),
              "The Anchorfields": ("tools.handbuilt_worldtree_anchorfields", "START"),
              "Aurelion": ("tools.handbuilt_worldtree_aurelion", "START")}
    with_links = {n: z for n, z in zones.items() if getattr(z, "links", None)}
    check("The Fading Firmament" in with_links, "the Firmament has no links")
    before = [n for n in with_links if n != "The Fading Firmament"]
    check(1 <= len(before) <= 3, f"links before the Firmament: {before} (Kyle: one or two)")
    check(len(with_links.get("The Fading Firmament").links) >= 2 * max(
        len(with_links[n].links) for n in before) if before else True,
        "the Firmament doesn't lean on links more than the maps before it")
    pads = 0
    for name, z in with_links.items():
        for pad, v in z.links.items():
            pads += 1
            x, y = pad
            check(z.get_interaction(x, y) == "link", f"{name}: the pad at {pad} isn't a link tile")
            check(z.is_walkable(x, y), f"{name}: the pad at {pad} can't be stood on")
            lx, ly = v["to"]
            check(z.is_walkable(lx, ly), f"{name}: the landing {v['to']} beside {v['pad']} isn't walkable")
            other = z.links.get(tuple(v["pad"]))
            check(other is not None and tuple(other["pad"]) == pad, f"{name}: {pad}'s partner doesn't lead back")
            check(abs(lx - v["pad"][0]) + abs(ly - v["pad"][1]) <= 3, f"{name}: {pad} lands far from its partner")
            check(v["kind"] in KINDS and message(v["kind"]), f"{name}: {pad} is an unknown kind {v['kind']}")
        # 4. through the zone manager
        import pygame
        pygame.init()
        from world.zone_manager import ZoneManager
        zm = ZoneManager.__new__(ZoneManager)
        zm.current_zone = z
        pad, v = next(iter(z.links.items()))
        zm.player_x, zm.player_y = pad
        zm._find_nearest_walkable = lambda zone, x, y: None
        dest = zm.link_destination()
        kind = zm.try_use_link()
        check(dest is not None and kind == v["kind"] and (zm.player_x, zm.player_y) == tuple(v["to"])
              and zm.current_zone is z, f"{name}: crossing {pad} didn't land at {v['to']}")
        # 5. whole with links; say whether it would be whole without them
        if name in starts:
            import importlib
            mod, attr = starts[name]
            st = tuple(getattr(importlib.import_module(mod), attr))
            walk = {(x, y) for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y)}
            got = flood(z, st)
            check(walk <= got, f"{name}: {len(walk - got)} walkable tiles unreachable even with links")
            without = flood(z, st, use_links=False)
            NOTES.append(f"{name}: {len(z.links) // 2} link(s); without them {len(walk - without)} tiles would be "
                         f"cut off")
    print(f"{len(with_links)} maps with links, {pads} pads")
    for n in NOTES:
        print("  " + n)
    if FAILS:
        print(f"FAIL ({len(FAILS)})")
        for f in FAILS:
            print("  - " + f)
        return 1
    print("links OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
