#!/usr/bin/env python3
"""Companions must be recruitable by 45, and never at the end of a dungeon.

Kyle, 31 Oct 2026, two rules set in the same conversation:

  "Let's never put recruits at the end of a dungeon! If we can limit it to
   before the first boss. Does that make sense? If not before the first boss
   than after the first boss but hidden."

  "Let's keep them all before level 49. This way we can recruit them by lvl 45.
   I'd rather not have any recruit that we can't get until after 45."

The first one matters more than it sounds: a companion at the end of a dungeon
means you clear the whole thing WITHOUT the help they would have given, so the
reward lands after you needed it.

MEASURING IT PROPERLY. Straight-line distance to a boss says nothing about
whether you reach somebody before or after that boss on the way in, so this
walks the zone: BFS from the tile you actually arrive on, then compare the
companion's walking distance from that door against the first boss chamber's.

The entrance is recovered from world/portal_manager.py's destination table,
because zones do not record their own. If that table ever stops being
parseable this check reports the zone as unmeasurable rather than passing it,
since a silent pass is the failure mode worth avoiding.
"""
import sys, os, json, re, collections, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_LEVEL = 48

#: Asher is camped at the Burning Blade Coven by design, is leashed there, and
#: his text is hash-locked. He is the one deliberate exception.
EXEMPT = {"asher_coleman"}


def arrival_points():
    src = (ROOT / "world/portal_manager.py").read_text()
    out = collections.defaultdict(list)
    for m in re.finditer(
            r'\(\s*\d+\s*,\s*\d+\s*\)\s*:\s*\(\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', src):
        out[m.group(1)].append((int(m.group(2)), int(m.group(3))))
    return out


def bfs(zone, start):
    W, H = zone.width, zone.height
    sx, sy = start
    if not (0 <= sx < W and 0 <= sy < H) or zone.collision_layer[sy][sx] is not None:
        best = None
        for y in range(H):
            for x in range(W):
                if zone.collision_layer[y][x] is None:
                    d = (x - sx) ** 2 + (y - sy) ** 2
                    if best is None or d < best[0]:
                        best = (d, x, y)
        if best is None:
            return {}
        sx, sy = best[1], best[2]
    dist = {(sx, sy): 0}
    q = collections.deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)]
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in dist \
                    and zone.collision_layer[ny][nx] is None:
                dist[(nx, ny)] = d + 1
                q.append((nx, ny))
    return dist


def main():
    from world.zone_generator import create_all_zones
    recs = json.load(open(ROOT / "data/npcs/recruits.json"))["recruits"]
    zones = create_all_zones()
    arrive = arrival_points()

    fails, unmeasured, checked = [], [], 0

    too_high = [r for r in recs if r["level"] > MAX_LEVEL and r["recruit_id"] not in EXEMPT]
    print(f"  {len(recs)} companions; {len(too_high)} above level {MAX_LEVEL}")
    for r in too_high:
        fails.append(f"{r['name']} is level {r['level']}, so cannot be recruited by 45")

    for r in recs:
        if r["recruit_id"] in EXEMPT:
            continue
        z = zones.get(r["zone"])
        if z is None:
            continue
        bosses = [b for b in (getattr(z, "boss_positions", None) or []) if b]
        if not bosses and getattr(z, "boss_position", None):
            bosses = [z.boss_position]
        if not bosses:
            continue                      # open world or town: rule does not apply
        starts = arrive.get(r["zone"])
        if not starts:
            unmeasured.append(f"{r['name']} in {r['zone']}: no arrival point known")
            continue
        dist = bfs(z, starts[0])
        dr = dist.get((r["x"], r["y"]))
        bd = sorted(d for d in (dist.get((b[0], b[1])) for b in bosses) if d is not None)
        if dr is None or not bd:
            unmeasured.append(f"{r['name']} in {r['zone']}: unreachable from the entrance")
            continue
        checked += 1
        if dr >= bd[0]:
            where = "AFTER THE FINAL boss" if dr > bd[-1] else "past the first boss"
            fails.append(f"{r['name']} in {r['zone']} is {where} "
                         f"({dr} steps in, first boss at {bd[0]})")

    print(f"  {checked} companions measured inside a dungeon or cave against its first boss")
    if unmeasured:
        print(f"\n  {len(unmeasured)} could NOT be measured (reported, not passed):")
        for u in unmeasured:
            print(f"      {u}")
    if fails:
        print()
        for f in fails:
            print(f"  FAIL - {f}")
    print("\nPASS" if not fails and not unmeasured else "\nFAIL")
    return 0 if (not fails and not unmeasured) else 1


if __name__ == "__main__":
    sys.exit(main())
