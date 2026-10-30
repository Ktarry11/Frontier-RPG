#!/usr/bin/env python3
"""Prove the Gurbashi Arena's octagon is a GAUNTLET and not a racetrack.

    PYTHONPATH=. python3 tools/verify_gurbashi_arena.py

tools/handbuilt_gurbashi_arena.py already flood-fills on build (CaveLayout.finish raises on an
unreachable marker or an isolated pocket).  What that does NOT catch is the one property the whole
layout exists for: that the four ring bosses can only be reached in one order, because the upper-right
pair of octagon faces was never cut.  A ring that accidentally closes still builds, still verifies,
still looks right on screen - and lets a party walk clockwise straight to the three o'clock boss.

So this checks four things:

  1  every boss, the exit portal and every chest is walkable and reachable from the arrival tile
  2  reachable == walkable - one connected space, no pockets
  3  wall station N and bosses N+1..5 go dark.  Done for all four ring stations, which is the
     statement "you cannot get past a fight you have not won"
  4  the upper-right face really is rock: block the ring just anticlockwise of the stair and three
     o'clock becomes unreachable, so there is no clockwise route to it at all
"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_gurbashi_arena as GA  # noqa: E402


def reach(zone, start, blocked=frozenset()):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if (0 <= n[0] < zone.width and 0 <= n[1] < zone.height
                    and n not in seen and n not in blocked and zone.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    return seen


def main():
    zone, L = GA.build_arena()
    errs = []
    print(f"{zone.name}: {zone.width}x{zone.height}  props placed {L.placed}, skipped {len(L.skipped)}")
    for s in L.skipped:
        print(f"  SKIPPED PROP {s}")

    walkable = {(x, y) for y in range(zone.height) for x in range(zone.width)
                if zone.is_walkable(x, y)}
    seen = reach(zone, GA.ARRIVAL)
    print(f"  walkable {len(walkable)}   reachable from {GA.ARRIVAL} {len(seen)}")

    # --- 1  markers
    targets = [(GA.PORTAL, "exit portal")] + \
              [((x, y), n) for (x, y, n, _d) in GA.BOSSES] + \
              [(GA.ADD[:2], GA.ADD[2])] + \
              [(c, f"chest {c}") for c in GA.CHESTS]
    for (t, label) in targets:
        if t not in walkable:
            errs.append(f"[1] {label} {t} is NOT WALKABLE")
        elif t not in seen:
            errs.append(f"[1] {label} {t} is walkable but UNREACHABLE")
    print(f"  [1] {len(targets)} markers walkable and reachable: "
          f"{'OK' if not errs else 'FAIL'}")

    # --- 2  no pockets
    pockets = walkable - seen
    if pockets:
        errs.append(f"[2] {len(pockets)} walkable tiles unreachable, e.g. {sorted(pockets)[:6]}")
    print(f"  [2] reachable == walkable: {'OK' if not pockets else f'FAIL ({len(pockets)} orphans)'}")

    # --- 3  the gauntlet: station N walled drops N+1..5
    order = [(x, y, n) for (x, y, n, _d) in GA.BOSSES]
    for i in range(4):
        block = GA.boss_block_tiles(zone, i)
        s = reach(zone, GA.ARRIVAL, block)
        still = [n for (x, y, n) in order[i + 1:] if (x, y) in s]
        gone = [n for (x, y, n) in order[i + 1:] if (x, y) not in s]
        tag = "OK" if not still else "FAIL"
        print(f"  [3] wall station {i + 1} ({order[i][2].split(' ')[0]}, {len(block)} tiles) "
              f"-> {len(gone)}/{len(order) - i - 1} later bosses unreachable: {tag}")
        if still:
            errs.append(f"[3] station {i + 1} walled but still reachable: {still} "
                        f"- the ring is looping somewhere")

    # --- 4  the upper-right face is rock: no clockwise route out of the stair
    stair = GA.RING_VERTS[0]
    stair = (round(stair[0]), round(stair[1]))
    acw = GA.boss_block_tiles(zone, 0)          # cut the ring at ten o'clock
    s = reach(zone, stair, acw)
    #: the boss's tile AND the vertex sand he is the doorway to, because the face would be just as
    #: broken if the walk round the top let you out onto three o'clock's floor behind him.
    three = [GA.BOSSES[3][:2], (82, 56)]
    bad = [t for t in three if t in s]
    if bad:
        errs.append(f"[4] {bad} reachable from the stair {stair} with ten o'clock walled - "
                    f"the 270->315->0 faces are NOT solid")
    print(f"  [4] no clockwise route from the stair {stair} to three o'clock {three}: "
          f"{'OK' if not bad else 'FAIL'}  (reached {len(s)} tiles)")
    # ... and the hall behind it goes with it
    if GA.CENTRE in s:
        errs.append(f"[4] the hall {GA.CENTRE} is reachable without walking the ring")

    if errs:
        print("\nFAILED:")
        for e in errs:
            print(f"  {e}")
        raise SystemExit(1)
    print("\nall four properties hold.")


if __name__ == "__main__":
    main()
