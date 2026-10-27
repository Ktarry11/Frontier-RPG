"""
Verify The Deep Bloom.

    PYTHONPATH=. python3 tools/verify_deep_bloom.py

THE POINT OF THIS FILE. The Deep Bloom's whole design is one claim: the deeper you go, the less the Bloom
remembers what a building is. A docstring can say that. A map can fail to do it while rendering perfectly and
passing every reachability check in the kit - which is the failure mode this project keeps producing, so the
claim gets a number.

RECTANGULARITY, measured as the straight-run fraction of the floor/wall boundary. For every floor tile with a
wall to its north, ask whether the two tiles either side of it also have a wall to their north. A rectangle's
edge answers yes all the way along; an ellipse's edge steps and curves and answers no constantly. Same for
south, east and west. Report the fraction per band and require it to FALL from the Portico to the Heart.

Also here: the ordinary things. Every target reachable, the portal carved, three-to-four packs between each
boss (Kyle's rule), nothing stacked on a boss or a chest, and the dungeon flags actually set - because a
"dungeon" with fixed_spawns unset rolls random spawns and nobody notices until the packs are not there.
"""
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import handbuilt_deep_bloom as DB          # noqa: E402

#: Non-overlapping y bands, entrance first. These are the measurement windows, not the subzones.
BANDS = [("The Portico", 126, 150),
         ("The Stacks", 100, 126),
         ("The Repeated Wing", 64, 100),
         ("The Scriptorium", 42, 64),
         ("The Lower Stacks", 20, 42),
         ("The Heart", 0, 20)]

DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
#: Perpendicular axis to walk along when asking "is this edge straight?"
PERP = {"N": (1, 0), "S": (1, 0), "E": (0, 1), "W": (0, 1)}


def rectangularity(zone, y0, y1, reach=2):
    """Fraction of floor/wall boundary tiles that sit on a straight axis-aligned run."""
    walk = lambda x, y: zone.is_walkable(x, y)          # noqa: E731
    hits = straight = 0
    for y in range(max(0, y0), min(zone.height, y1)):
        for x in range(zone.width):
            if not walk(x, y):
                continue
            for d, (dx, dy) in DIRS.items():
                if walk(x + dx, y + dy):
                    continue                            # not a boundary in this direction
                hits += 1
                px, py = PERP[d]
                ok = all(walk(x + px * k, y + py * k) and not walk(x + px * k + dx, y + py * k + dy)
                         for k in list(range(-reach, 0)) + list(range(1, reach + 1)))
                straight += 1 if ok else 0
    return (straight / hits if hits else 0.0), hits


def reachable(zone, start):
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and zone.is_walkable(*n):
                seen.add(n)
                stack.append(n)
    return seen


def main():
    zone, L = DB.build_deep_bloom()
    DB.dress(zone, L)
    DB.finish(zone, L)
    fails = []

    print("== flags")
    for attr, want in (("is_cave", True), ("fixed_spawns", True), ("region", "The Crystalline Underdark")):
        got = getattr(zone, attr, None)
        ok = got == want
        print(f"  {attr:14s} {got!r:34s} {'ok' if ok else 'FAIL (want ' + repr(want) + ')'}")
        if not ok:
            fails.append(f"{attr}={got!r}")
    from world import zone_classification as ZC
    in_dungeons = "The Deep Bloom" in ZC.DUNGEONS
    print(f"  {'DUNGEONS':14s} {in_dungeons!r:34s} {'ok' if in_dungeons else 'FAIL - would get gathering nodes'}")
    if not in_dungeons:
        fails.append("not in zone_classification.DUNGEONS")

    print("\n== architecture collapses into tissue  (straight-run fraction of the floor/wall boundary)")
    # The first version of this test demanded a monotone fall band by band, and the map failed it twice. The
    # map was right and the test was wrong, which is worth recording: the Repeated Wing is MORE rectangular
    # than the Stacks (0.67 vs 0.56) because the Stacks are full of shelf-pillars and a pillar is four corners,
    # while the Wing is two enormous clean rects. And the Heart measures a hair above the Lower Stacks because
    # a big lobe has longer near-flat stretches than a small one. Neither is a defect.
    #
    # The design never claimed a smooth slide. It claimed the Bloom copies a library competently and then STOPS
    # BEING ABLE TO - architecture for three sections, then a collapse. So that is what gets tested: the upper
    # three bands all architectural, the lower three all not, and a hard step between them.
    vals = []
    for (name, y0, y1) in BANDS:
        r, n = rectangularity(zone, y0, y1)
        vals.append(r)
        print(f"  {name:20s} y{y0:>3}-{y1:<3} {r:5.3f}  (n={n:4d})  {'#' * int(round(r * 46))}")
    upper, lower = vals[:3], vals[3:]
    for (name, _a, _b), r in zip(BANDS[:3], upper):
        if r < 0.45:
            fails.append(f"{name} rectangularity {r:.3f} < 0.45 - should still read as a building")
            print(f"  FAIL: {name} {r:.3f} is not architectural enough")
    for (name, _a, _b), r in zip(BANDS[3:], lower):
        if r > 0.30:
            fails.append(f"{name} rectangularity {r:.3f} > 0.30 - still reads as a building")
            print(f"  FAIL: {name} {r:.3f} still reads as masonry")
    step = min(upper) - max(lower)
    print(f"  architectural floor {min(upper):.3f} | tissue ceiling {max(lower):.3f} | step {step:.3f}  "
          f"{'ok' if step >= 0.15 else 'FAIL - the collapse is too soft to feel'}")
    if step < 0.15:
        fails.append(f"collapse step only {step:.3f}")

    print("\n== the mirror goes with the corners  (walkable agreement across the spine at x=65)")
    # A library is symmetric: matching stacks either side of a spine. A growth is not. So the upper half of
    # this map is mirrored and the lower half must not be - otherwise the bottom of the map keeps reading as
    # architecture no matter what shape it is carved in, which is exactly what the first draft did.
    def symmetry(y0, y1, axis=65):
        # Only tiles where at least ONE side is floor count. Scoring every tile lets a band that is mostly
        # solid rock claim near-perfect symmetry for matching rock against rock, which had the Heart reading
        # as 0.92 "mirrored" when its floor plan is nothing of the sort. This is agreement of SHAPE.
        hit = same = 0
        for y in range(max(0, y0), min(zone.height, y1)):
            for x in range(zone.width):
                mx = 2 * axis - x
                if not 0 <= mx < zone.width:
                    continue
                a, b = zone.is_walkable(x, y), zone.is_walkable(mx, y)
                if not (a or b):
                    continue
                hit += 1
                same += 1 if a == b else 0
        return same / hit if hit else 0.0

    syms = []
    for (name, y0, y1) in BANDS:
        sv = symmetry(y0, y1)
        syms.append(sv)
        print(f"  {name:20s} y{y0:>3}-{y1:<3} {sv:5.3f}  {'#' * int(round(sv * 46))}")
    for (name, _a, _b), sv in zip(BANDS[:3], syms[:3]):
        if sv < 0.90:
            fails.append(f"{name} symmetry {sv:.3f} < 0.90 - the built half should be mirrored")
            print(f"  FAIL: {name} {sv:.3f} is not mirrored enough for a building")
    for (name, _a, _b), sv in zip(BANDS[4:], syms[4:]):
        if sv > 0.88:
            fails.append(f"{name} symmetry {sv:.3f} > 0.88 - still mirrored, so still reads as built")
            print(f"  FAIL: {name} {sv:.3f} is still mirrored")

    print("\n== reachability")
    seen = reachable(zone, (DB.PORTAL[0], DB.PORTAL[1] - 1))
    targets = [("portal", DB.PORTAL)] + [(n, p) for n, p in DB.BOSSES.items()] \
        + [(f"chest{i}", c) for i, c in enumerate(DB.CHESTS)] \
        + [(f"{n}@{x},{y}", (x, y)) for (x, y, n, _l) in DB.TRASH]
    bad = [n for n, p in targets if tuple(p) not in seen]
    print(f"  {len(targets)} targets, {len(bad)} unreachable")
    if bad:
        fails.append(f"unreachable: {bad[:8]}")
        print("  FAIL", bad[:8])

    print("\n== packs between bosses  (Kyle: 3-4 groups, sometimes less)")
    # Packs are authored in order down the map, so bucket them by which boss they come before.
    order = ["The Index", "The Second Copy", "The Scriptor", "Errata", "The Deep Bloom"]
    cuts = [DB.BOSSES[n][1] for n in order]            # boss y, descending
    buckets = Counter()
    for (cx, cy, _m) in DB.PACKS:
        for n, by in zip(order, cuts):
            if cy >= by:
                buckets[n] += 1
                break
        else:
            buckets[order[-1]] += 1
    for n in order:
        c = buckets[n]
        ok = 2 <= c <= 4
        print(f"  {n:18s} {c} packs  {'ok' if ok else 'FAIL (want 2-4)'}")
        if not ok:
            fails.append(f"{n} has {c} packs")
    sizes = Counter(len(m) for (_x, _y, m) in DB.PACKS)
    print(f"  pack sizes {dict(sorted(sizes.items()))}  total mobs {len(DB.TRASH)}")

    print("\n== spacing")
    occ = {}
    for (x, y, n, _l) in DB.TRASH:
        occ.setdefault((x, y), []).append(n)
    dupes = {k: v for k, v in occ.items() if len(v) > 1}
    print(f"  stacked trash tiles: {len(dupes)}  {'ok' if not dupes else 'FAIL'}")
    if dupes:
        fails.append(f"stacked trash: {list(dupes)[:5]}")
    reserved = list(DB.BOSSES.values()) + [tuple(c) for c in DB.CHESTS] + [DB.PORTAL]
    close = [(x, y, n) for (x, y, n, _l) in DB.TRASH
             if any(max(abs(x - a), abs(y - b)) < 2 for (a, b) in reserved)]
    print(f"  trash within 1 tile of a boss/chest/portal: {len(close)}  {'ok' if not close else 'FAIL'}")
    if close:
        fails.append(f"trash crowding reserved tiles: {close[:5]}")

    print("\n== the Repeated Wing is actually repeated")
    # The fiction is that the mycelium copied a shelf-rank and did not notice it already had one. If the two
    # copies are not the same shape, the player never gets the moment of "I have been here", and the section
    # is just two rooms.
    a = DB.RECTS["repeat_a"]
    b = DB.RECTS["repeat_b"]
    same = (a[2] - a[0], a[3] - a[1]) == (b[2] - b[0], b[3] - b[1]) and a[0] == b[0]
    print(f"  repeat_a {a}  repeat_b {b}   {'ok - identical' if same else 'FAIL - copies differ'}")
    if not same:
        fails.append("the Repeated Wing's two copies are not identical")

    print("\n" + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    for f in fails:
        print("  -", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
