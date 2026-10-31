"""
Measure the three claims The Lashings' archetype makes.

    PYTHONPATH=. python3 tools/verify_lashings.py

CLAIM 1 - EVERY ROOM IS A HULL, which means every room is LONG. A hull has a bow, a stern and a
centreline; you fight down it, not across it. A room that comes out square is just a room, and a
map of rooms joined by corridors is every other dungeon in the game.

CLAIM 2 - IT IS A TREE, which is the exact inverse of the Glittervein dungeon. There, every
gallery is doubled and the seam always rejoins, and the test is that severing any one of them
changes nothing. Here there is no second way round ANYWHERE, so the test is the mirror image:
remove any one plank and something must be stranded. Eight planks, eight strandings.

    The map is rebuilt without each plank rather than having its tiles blocked by a reconstruction
    of where the plank probably ran. That reconstruction was the bug in the Mother Vein's first
    verifier - a second implementation of the carve that landed on slightly different tiles and
    let every control pass through the slivers it missed.

CLAIM 3 - NOBODY SKIPS A BOSS. Kyle, on the Anchorage: "No fuckers are skipping bosses in this
game!" There it took tidal cuts carved into a beach to produce a chokepoint. Here it is simply
what a gangplank is - but "simply" is not a measurement, so this sails the boss's trigger radius
shut and requires everything beyond it to go unreachable.
"""
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_lashings as LA  # noqa: E402
from tools import ship_builder as sb  # noqa: E402

#: A hull has to be at least this many times longer than it is wide.
MIN_ASPECT = 2.0


def _reach(zone, start, blocked=frozenset()):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < LA.W and 0 <= n[1] < LA.H and n not in seen and n not in blocked
                    and zone.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def _hull_tiles(key, zone):
    (_k, _nm, x0, x1, ycen, beam, _bow) = LA.HULL_BY_KEY[key]
    return {(x, y) for x in range(x0, x1 + 1)
            for y in range(ycen - beam, ycen + beam + 1) if zone.is_walkable(x, y)}


def main():
    bad = []
    zone, L = LA.build_lashings()
    LA.dress(zone, L)
    LA.finish(zone, L)
    start = (LA.PORTAL[0], LA.PORTAL[1] - 2)
    base = _reach(zone, start)
    print(f"The Lashings ({LA.W}x{LA.H}): walkable "
          f"{sum(1 for y in range(LA.H) for x in range(LA.W) if zone.is_walkable(x, y))}, "
          f"reachable {len(base)}")

    # ---------- CLAIM 1: every room is a hull ----------
    print("\n  hull aspect (length : beam)")
    for (key, nm, x0, x1, ycen, beam, _bow) in LA.HULLS:
        loa = (x1 - x0) + 1
        width = 2 * beam + 1
        ratio = loa / width
        flag = "" if ratio >= MIN_ASPECT else "   <-- too square to be a ship"
        print(f"    {nm:20} {loa:3} x {width:2}  = {ratio:.2f}{flag}")
        if ratio < MIN_ASPECT:
            bad.append(f"{nm} is {ratio:.2f}:1, which is a room rather than a hull")

    # ---------- CLAIM 2: it is a tree ----------
    if len(LA.PLANKS) != len(LA.HULLS) - 1:
        bad.append(f"{len(LA.PLANKS)} planks for {len(LA.HULLS)} hulls - a tree has exactly "
                   f"{len(LA.HULLS) - 1}, so this map either has a cycle or is in pieces")

    stranded_ok = 0
    print("\n  removing each plank")
    for i, (kind, a, b) in enumerate(LA.PLANKS):
        z2, _l2 = LA.build_lashings(omit={i})
        seen2 = _reach(z2, start)
        lost = [nm for (key, nm, *_r) in LA.HULLS
                if _hull_tiles(key, z2) and not (_hull_tiles(key, z2) & seen2)]
        if lost:
            stranded_ok += 1
            print(f"    {a}->{b:4} strands {', '.join(lost)}")
        else:
            print(f"    {a}->{b:4} strands NOTHING")
            bad.append(f"removing the {a}->{b} plank strands nothing, so there is a second way "
                       f"round it and this map is not a tree")

    # ---------- CLAIM 3: nobody skips a boss ----------
    print("\n  sealing each boss's trigger radius")
    R = sb.TRIGGER_BAND // 2
    order = [nm for (_x, _y, nm) in zone.boss_positions]
    for idx, nm in enumerate(order):
        bx, by = LA.BOSSES[nm]
        seal = {(bx + dx, by + dy) for dx in range(-R, R + 1) for dy in range(-R, R + 1)}
        seen3 = _reach(zone, start, frozenset(seal))
        beyond = [n for n in order[idx + 1:] if LA.BOSSES[n] in seen3]
        if beyond:
            print(f"    {nm:26} CAN be walked past to reach {beyond}")
            bad.append(f"{nm} can be skipped - {beyond} stay reachable with her trigger band "
                       f"sealed")
        else:
            print(f"    {nm:26} holds the plank")

    if bad:
        print("\nFAILED:")
        for line in bad:
            print("  - " + line)
        raise SystemExit(1)
    print("\nThe Lashings is a lashed fleet: long hulls, one plank each, and no way round a boss.")


if __name__ == "__main__":
    main()
