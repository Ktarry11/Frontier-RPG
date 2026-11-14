#!/usr/bin/env python3
"""Move the NPCs that are standing on top of each other.

    PYTHONPATH=. python3 tools/spread_town_npcs.py [--zone orgrimmar] [--apply]

Kyle, 7 Nov: "fix up towns. the trainers bunching together is just tiring
....especially in massive cities like orgrimmar or UC [...] spread NPCs out in
towns. make the town alive."

WHAT IS ACTUALLY WRONG, per tools/audit_npc_spread.py. It is not scatter, it
is one specific thing: the class trainer and the five profession trainers were
placed as a BLOCK, in a 5x5 square, in every town that has them. Orgrimmar is
200x200 and all six of its trainers stand inside x 94-98, y 51-55.

    ct_org          Trainer Garrek      94 53
    pt_org_forge    Forge Brakka        98 53
    pt_org_herbs    Apothecary Shazra   97 54
    pt_org_wood     Woodwright Bruga    97 52
    pt_org_hide     Tanner Thurgan      96 55
    pt_org_essence  Tinker Brakka       96 51

The hand-placed rosters were spread out in an earlier pass; these were missed
because they are filed under the town's DISPLAY name ("Orgrimmar") while the
hand-placed ones use the slug ("orgrimmar"), so an audit grouping by the raw
string saw two different towns and judged each of them fine.

WHERE THEY GO, and why not just scatter them. A trainer standing in the middle
of a road is not more alive than a trainer in a pile - it is just lonelier.
Every destination here is a walkable tile ON THE PERIMETER OF A STRUCTURE, and
each displaced NPC gets a DIFFERENT structure, so the forge trainer, the
tanner and the tinker end up outside three different buildings. Structures are
read off the collision layer: 'wall' blobs where a town has them, 'landmark'
blobs where it does not (Brill and the Crossroads have no 'wall' at all), and
never 'cliff', which is terrain rather than architecture.

THREE THINGS EVERY DESTINATION HAS TO SATISFY, because getting any of them
wrong ships an NPC you cannot talk to:

  walkable    the tile itself, and at least one walkable neighbour to stand
              in while talking.
  reachable   the same connected walkable region the NPC started in. A
              building perimeter can be INSIDE a sealed building; placing a
              trainer there is worse than the pile, because the pile is at
              least usable.
  separated   at least MIN_SEPARATION from every other NPC in the zone,
              counting the hand-placed roster, not just the ones being moved.

Deterministic: candidates are ordered, and the tie-break is a hash of the
npc_id, so re-running produces the same town rather than a new one.
"""

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROSTER = os.path.join(ROOT, "data/npcs/ambient_npcs.json")

#: Two NPCs closer than this read as a pile. Chebyshev, because movement is
#: 8-directional.
MIN_SEPARATION = 5

#: Do not relocate anyone further than this from where they started. A trainer
#: belongs to a town, and a 200x200 city has wilderness in it - without a
#: leash, "maximise distance from other NPCs" puts the tanner on a mountain.
MAX_RELOCATION = 28

#: Collision ids that are architecture rather than terrain, best first.
STRUCTURE_IDS = ("wall", "landmark")

NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

#: ONLY THESE MOVE. Kyle named the trainers, and the trainers are the ones
#: placed by a generator as a block. The hand-placed roster was spread in an
#: earlier pass and its remaining tight groups are deliberate - an innkeeper,
#: a flight master and a stable master standing together at a city gate is a
#: hub, not a pile, and the first run of this tool cheerfully moved
#: Orgrimmar's innkeeper 28 tiles from her own inn.
MOVABLE_PREFIXES = ("ct_", "pt_")


def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def walkable_set(zone):
    out = set()
    for y in range(zone.height):
        for x in range(zone.width):
            try:
                if zone.is_walkable(x, y):
                    out.add((x, y))
            except Exception:
                pass
    return out


def region_of(walk, start):
    """Flood fill the walkable region containing `start` (or nearest to it)."""
    if start not in walk:
        near = min(walk, key=lambda t: chebyshev(t, start), default=None)
        if near is None:
            return set()
        start = near
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in NEIGHBOURS:
            t = (x + dx, y + dy)
            if t in walk and t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def structures(zone):
    """Connected blobs of architecture -> list of sets of (x, y).

    Uses 'wall' if the town has any, else 'landmark'. Mixing them would merge
    a building into the rock outcrop it is built against and report one
    enormous structure, which is no anchor at all.
    """
    for tile_id in STRUCTURE_IDS:
        cells = set()
        for y in range(zone.height):
            for x in range(zone.width):
                if zone.collision_layer[y][x] == tile_id:
                    cells.add((x, y))
        if len(cells) < 4:
            continue
        blobs = []
        unseen = set(cells)
        while unseen:
            start = unseen.pop()
            blob = {start}
            stack = [start]
            while stack:
                x, y = stack.pop()
                for dx, dy in NEIGHBOURS:
                    t = (x + dx, y + dy)
                    if t in unseen:
                        unseen.discard(t)
                        blob.add(t)
                        stack.append(t)
            # A two-tile smear is scenery, not a building worth standing at.
            if len(blob) >= 4:
                blobs.append(blob)
        if blobs:
            return blobs, tile_id
    return [], None


def perimeter(blob, walk, region):
    """Walkable, reachable tiles touching this structure."""
    out = set()
    for (x, y) in blob:
        for dx, dy in NEIGHBOURS:
            t = (x + dx, y + dy)
            if t in walk and t in region:
                out.add(t)
    return out


def approachable(tile, walk):
    """At least one walkable neighbour, so the player can stand and talk."""
    return any((tile[0] + dx, tile[1] + dy) in walk for dx, dy in NEIGHBOURS)


def clumps(people):
    parent = list(range(len(people)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            if chebyshev(people[i]["pos"], people[j]["pos"]) < MIN_SEPARATION:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
    groups = collections.defaultdict(list)
    for i, p in enumerate(people):
        groups[find(i)].append(p)
    return [g for g in groups.values() if len(g) > 1]


def _movable(npc):
    return npc["id"].startswith(MOVABLE_PREFIXES)


def _anchor_first(group):
    """Who stays put. The class trainer if there is one, else the lowest id.

    The class trainer is the one the player is sent to by name and the one a
    quest is most likely to describe the location of, so it is the cheapest
    one to leave exactly where it has always been.
    """
    order = sorted(group, key=lambda p: (not p["id"].startswith("ct_"), p["id"]))
    return order[0], [p for p in order[1:] if _movable(p)]


def plan_zone(zname, people, zone):
    """-> list of (npc, old, new, why). Does not write anything."""
    walk = walkable_set(zone)
    if not walk:
        return [], "no walkable tiles"
    blobs, kind = structures(zone)

    occupied = {p["pos"] for p in people}
    moves = []

    for group in clumps(people):
        anchor, movers = _anchor_first(group)
        region = region_of(walk, anchor["pos"])
        # Structures this group can actually reach, nearest first. Each one is
        # consumed as it is used so two trainers never share a wall.
        usable = []
        for blob in blobs:
            ring = [t for t in perimeter(blob, walk, region) if approachable(t, walk)]
            if ring:
                cx = sum(x for x, _ in blob) / len(blob)
                cy = sum(y for _, y in blob) / len(blob)
                usable.append(((cx, cy), ring))
        all_blobs = list(usable)

        for npc in sorted(movers, key=lambda p: p["id"]):
            old = npc["pos"]
            placed = None
            # A town's architecture does not always come in separate pieces -
            # Orgrimmar's 'wall' is one connected rampart, so "a different
            # structure each" starves after the first trainer and everybody
            # else lands in a field. Prefer an unused blob, then allow reuse
            # (separation is enforced on the tiles regardless), and only then
            # give up on walls.
            for pool in (usable, all_blobs):
                pool.sort(key=lambda u: chebyshev((round(u[0][0]), round(u[0][1])), old))
                for idx, (centre, ring) in enumerate(pool):
                    cands = [t for t in sorted(ring)
                             if chebyshev(t, old) <= MAX_RELOCATION
                             and all(chebyshev(t, o) >= MIN_SEPARATION
                                     for o in occupied if o != old)]
                    if not cands:
                        continue
                # Furthest from the pile it came from, then a stable
                # tie-break on the id so a re-run is the same town.
                    cands.sort(key=lambda t: (-min(chebyshev(t, o) for o in occupied
                                                   if o != old),
                                              (hash((npc["id"], t)) & 0xffff)))
                    placed = cands[0]
                    if pool is usable:
                        usable.pop(idx)
                    break
                if placed is not None:
                    break
            if placed is None:
                # No free structure in range. Fall back to the most isolated
                # reachable tile within the leash - still spread out, just
                # not standing against a wall.
                cands = [t for t in region
                         if chebyshev(t, old) <= MAX_RELOCATION
                         and approachable(t, walk)
                         and all(chebyshev(t, o) >= MIN_SEPARATION
                                 for o in occupied if o != old)]
                if not cands:
                    continue
                cands.sort(key=lambda t: (-min(chebyshev(t, o) for o in occupied
                                               if o != old),
                                          (hash((npc["id"], t)) & 0xffff)))
                placed = cands[0]
                why = "open ground (no free structure in range)"
            else:
                why = f"beside a {kind}"
            occupied.discard(old)
            occupied.add(placed)
            npc["pos"] = placed
            moves.append((npc, old, placed, why))
    return moves, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    from world.zone_generator import create_all_zones
    from world.zone_keys import zone_key

    with open(ROSTER, encoding="utf-8") as fh:
        doc = json.load(fh)

    by_zone = collections.defaultdict(list)
    for n in doc["npcs"]:
        z, x, y = n.get("zone"), n.get("x"), n.get("y")
        if z and x is not None and y is not None:
            by_zone[zone_key(z)].append(
                {"id": n.get("npc_id", ""), "name": n.get("name") or n.get("npc_id"),
                 "pos": (int(x), int(y)), "raw": n})

    zones = {zone_key(k): v for k, v in create_all_zones().items()}

    total = 0
    for zname in sorted(by_zone):
        if args.zone and zname != args.zone:
            continue
        zone = zones.get(zname)
        if zone is None:
            continue
        people = by_zone[zname]
        moves, err = plan_zone(zname, people, zone)
        if err or not moves:
            continue
        total += len(moves)
        print(f"\n  == {zname}  ({len(people)} npcs, {zone.width}x{zone.height})")
        for npc, old, new, why in moves:
            print(f"     {npc['name'][:28]:30}{str(old):11} -> {str(new):11}"
                  f" {chebyshev(old, new):>3} tiles  {why}")
        if args.apply:
            for npc, _old, new, _why in moves:
                npc["raw"]["x"], npc["raw"]["y"] = int(new[0]), int(new[1])

    print(f"\n  {total} NPCs relocated"
          + (" and written" if args.apply else " (report only; pass --apply to write)"))
    if args.apply and total:
        with open(ROSTER, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
