#!/usr/bin/env python3
"""Find walkable, reachable, out-of-the-way tiles to tuck a vendor into.

    PYTHONPATH=. python3 tools/find_hidden_vendor_spots.py "Southern Thousand Needles" [n]

Kyle, 2026-10-28: "We can also spice up the new zones and have hidden vendors."

WALKABLE IS NOT THE SAME AS REACHABLE, which is the bug this exists to prevent. Ivan was placed at
Ragefire (100,100) on a tile that passed is_walkable and sat inside a sealed pocket of rock, so he
existed and could never be spoken to. A single is_walkable call cannot tell the difference. This
flood-fills the whole map first, keeps only the LARGEST connected region - the one the player is
actually standing in - and scores candidates inside it.

WHAT MAKES A SPOT HIDDEN RATHER THAN JUST EMPTY. A hidden vendor should feel tucked away and still be
findable by someone who explores, so a candidate wants three things at once: a clear 3x3 pocket to
stand in and talk, a high count of blocked tiles in the ring just beyond it (walls, rock, trees -
something that hides them), and distance from every NPC already in the zone. Scoring all three
together is what separates "behind the rocks at the end of a gully" from "a random patch of open
desert", which is what distance-from-centre alone would have given.
"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def largest_region(tm):
    """The set of walkable tiles in the biggest connected area - where the player can actually be."""
    seen, best = set(), set()
    for sy in range(tm.height):
        for sx in range(tm.width):
            if (sx, sy) in seen or not tm.is_walkable(sx, sy):
                continue
            region, q = set(), deque([(sx, sy)])
            seen.add((sx, sy))
            while q:
                x, y = q.popleft()
                region.add((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in seen or not (0 <= nx < tm.width and 0 <= ny < tm.height):
                        continue
                    if tm.is_walkable(nx, ny):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            if len(region) > len(best):
                best = region
    return best


def score(tm, region, x, y, npcs):
    """None if unusable, else (hiddenness, distance to nearest NPC) - bigger is better."""
    # a clear 3x3 to stand and talk in
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (x + dx, y + dy) not in region:
                return None
    # how enclosed the ring just beyond that is
    blocked = 0
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if max(abs(dx), abs(dy)) != 3:
                continue
            nx, ny = x + dx, y + dy
            if not (0 <= nx < tm.width and 0 <= ny < tm.height) or not tm.is_walkable(nx, ny):
                blocked += 1
    if not npcs:
        return blocked, 999
    near = min(abs(x - nx) + abs(y - ny) for nx, ny in npcs)
    return blocked, near


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    zone_name = sys.argv[1]
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    from world.zone_manager import ZoneManager
    zm = ZoneManager()
    if zone_name not in zm.zones:
        print(f"no zone {zone_name!r}. try one of:")
        for k in sorted(zm.zones):
            print(f"   {k}")
        return 1
    tm = zm.zones[zone_name]["tilemap"]

    import json
    npcs = []
    for rel, key in (("data/npcs/vendors.json", "vendors"),
                     ("data/npcs/ambient_npcs.json", "npcs")):
        p = ROOT / rel
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for n in d.get(key, []) if isinstance(d.get(key), list) else []:
            if str(n.get("zone", "")).lower().replace(" ", "_").replace("'", "") == \
                    zone_name.lower().replace(" ", "_").replace("'", ""):
                npcs.append((n.get("x", 0), n.get("y", 0)))

    region = largest_region(tm)
    walkable = sum(1 for y in range(tm.height) for x in range(tm.width) if tm.is_walkable(x, y))
    print(f"{zone_name}: {tm.width}x{tm.height}, {walkable} walkable, "
          f"{len(region)} of them reachable in one piece, {len(npcs)} NPCs already placed\n")

    cands = []
    for (x, y) in region:
        s = score(tm, region, x, y, npcs)
        if s and s[0] >= 8 and s[1] >= 12:
            cands.append((s[0], s[1], x, y))
    cands.sort(reverse=True)

    # Spread the results out, or the top ten are all the same gully.
    picked = []
    for blocked, near, x, y in cands:
        if all(abs(x - px) + abs(y - py) > 25 for _b, _n, px, py in picked):
            picked.append((blocked, near, x, y))
        if len(picked) >= want:
            break
    for blocked, near, x, y in picked:
        sub = tm.get_subzone_at(x, y) if hasattr(tm, "get_subzone_at") else None
        where = getattr(sub, "name", sub) if sub else "open ground"
        print(f"  ({x:>3},{y:>3})  enclosed by {blocked:>2} blocked tiles, "
              f"{near:>3} from the nearest NPC   [{where}]")
    if not picked:
        print("  nothing met the bar - loosen the thresholds or the zone is too open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
