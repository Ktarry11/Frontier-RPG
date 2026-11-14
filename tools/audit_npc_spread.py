#!/usr/bin/env python3
"""How crowded is every town, and where exactly?

    PYTHONPATH=. python3 tools/audit_npc_spread.py [--zone Orgrimmar]

Kyle, 7 Nov: "fix up towns. the trainers bunching together is just tiring
....especially in massive cities like orgrimmar or UC. We need to [...] spread
NPCs out in towns. make the town alive."

Bunching is not one bug, it is three, and they want different fixes, so this
measures them separately rather than printing one "crowdedness" number:

  CLUMP      NPCs standing within a couple of tiles of each other. The thing
             Kyle is looking at. A trainer, a vendor and a quest giver in a
             3x3 block means the player walks to one spot and does everything,
             and the other 95% of the city is scenery.

  FOOTPRINT  how much of the walkable town the NPCs actually occupy. A city
             can have no two NPCs adjacent and still feel dead if all of them
             are along one road. Measured as the area of their bounding box
             against the walkable area of the map.

  EMPTY      the largest walkable region with no NPC in it at all. This is the
             part of the city the player has no reason to ever enter.

It reports, it does not move anybody. Every position is read from
data/npcs/ambient_npcs.json, which is where they live.
"""

import argparse
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Two NPCs this close or closer count as clumped. Chebyshev distance, because
#: movement is 8-directional - a diagonal neighbour is as close as an
#: orthogonal one and should not read as further away.
CLUMP_DISTANCE = 2

#: A zone with fewer than this many NPCs is a camp, not a town; spread is not
#: a meaningful question about four people standing at a crossroads.
TOWN_MIN_NPCS = 6


def _chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _load():
    path = os.path.join(ROOT, "data/npcs/ambient_npcs.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["npcs"]


def _walkable(zone):
    """Set of walkable (x, y) on a generated zone, or None if unavailable."""
    # Tilemap has no `.tiles`; it has base_layer/collision_layer and
    # is_walkable(x, y). Reading the attribute that does not exist is how
    # the first run printed "?" for every footprint in the report.
    if not hasattr(zone, "is_walkable"):
        return None
    out = set()
    for y in range(getattr(zone, "height", 0)):
        for x in range(getattr(zone, "width", 0)):
            try:
                if zone.is_walkable(x, y):
                    out.add((x, y))
            except Exception:
                return None
    return out


def _clumps(points):
    """Connected groups under CLUMP_DISTANCE. Union-find, no library."""
    parent = list(range(len(points)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if _chebyshev(points[i][1], points[j][1]) <= CLUMP_DISTANCE:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b

    groups = collections.defaultdict(list)
    for i, p in enumerate(points):
        groups[find(i)].append(p)
    return [g for g in groups.values() if len(g) > 1]


def _largest_empty(walkable, occupied, radius=6):
    """Walkable tile furthest from any NPC, and how far that is.

    A proxy for "the biggest part of town nobody has a reason to visit" that
    does not need a real region decomposition: if the furthest-from-anyone
    walkable tile is 20 tiles from the nearest NPC, there is a 20-tile-deep
    hole in the city.
    """
    if not walkable or not occupied:
        return None, 0
    best, best_d = None, -1
    for tile in walkable:
        d = min(_chebyshev(tile, o) for o in occupied)
        if d > best_d:
            best, best_d = tile, d
    return best, best_d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone", help="only this zone")
    ap.add_argument("--all", action="store_true",
                    help="include small camps, not just towns")
    args = ap.parse_args()

    # NORMALISE THE ZONE KEY. The roster spells the same map two ways -
    # "Orgrimmar" for the generated trainer block and "orgrimmar" for the
    # hand-placed content - and world/zone_keys.py folds them together, so
    # the game sees one zone with 44 NPCs where a naive read sees two zones
    # with 6 and 38. Grouping by the raw string reports a city as roomy
    # because half its population is filed under the other spelling.
    from world.zone_keys import zone_key
    npcs = _load()
    by_zone = collections.defaultdict(list)
    for n in npcs:
        z = n.get("zone")
        if z and n.get("x") is not None and n.get("y") is not None:
            by_zone[zone_key(z)].append((n.get("name") or n.get("npc_id"),
                                         (int(n["x"]), int(n["y"])),
                                         n.get("npc_id", "")))

    from world.zone_generator import create_all_zones
    zones = {zone_key(k): v for k, v in create_all_zones().items()}

    rows = []
    for zname, people in sorted(by_zone.items()):
        if not args.zone and not args.all and len(people) < TOWN_MIN_NPCS:
            continue
        if args.zone and zname != args.zone:
            continue

        pts = [(p[0], p[1]) for p in people]
        clumps = _clumps(pts)
        clumped = sum(len(c) for c in clumps)

        xs = [p[1][0] for p in pts]
        ys = [p[1][1] for p in pts]
        box = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)

        zone = zones.get(zname)
        walk = _walkable(zone) if zone is not None else None
        occupied = {p[1] for p in pts}
        hole, hole_d = _largest_empty(walk, occupied)
        coverage = (len(walk) and box / len(walk)) if walk else None

        rows.append(dict(zone=zname, n=len(people), clumps=clumps,
                         clumped=clumped, box=box,
                         walk=len(walk) if walk else None,
                         coverage=coverage, hole=hole, hole_d=hole_d))

    rows.sort(key=lambda r: -(r["clumped"] / max(1, r["n"])))

    print(f"  {len(rows)} towns, {sum(r['n'] for r in rows)} placed NPCs")
    print(f"  clumped = standing within {CLUMP_DISTANCE} tiles of another NPC\n")
    print(f"  {'zone':24}{'npcs':>5}{'clumped':>9}{'groups':>8}"
          f"{'footprint':>11}{'deepest hole':>14}")
    for r in rows:
        cov = f"{r['coverage']*100:.0f}%" if r["coverage"] is not None else "?"
        pct = r["clumped"] / max(1, r["n"]) * 100
        print(f"  {r['zone'][:23]:24}{r['n']:>5}{r['clumped']:>6} "
              f"({pct:>3.0f}%){len(r['clumps']):>8}{cov:>11}"
              f"{r['hole_d']:>11} tiles")

    print("\n  -- worst groups ------------------------------------------")
    flat = []
    for r in rows:
        for c in r["clumps"]:
            flat.append((len(c), r["zone"], c))
    flat.sort(key=lambda t: -t[0])
    for size, zname, group in flat[:14]:
        xs = [p[1][0] for p in group]
        ys = [p[1][1] for p in group]
        where = f"({min(xs)}-{max(xs)}, {min(ys)}-{max(ys)})"
        who = ", ".join(p[0] for p in group[:4])
        more = f" +{size-4}" if size > 4 else ""
        print(f"  {zname[:20]:22}{size:>3} at {where:16} {who}{more}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
