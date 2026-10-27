#!/usr/bin/env python3
"""Verify EVERY portal in the game, through the real lookup the game uses.

    PYTHONPATH=. python3 tools/verify_portals.py [--zone "Name"]

WHY THIS IS GLOBAL AND NOT PER-ZONE. Both Hillsbrad halves shipped with every single portal dead, in both
directions, and nothing caught it: the zones built, baked, rendered and validated. The cause was that
`zone.name` was "Eastern Hillsbrad Foothills" while the registry key was "Eastern Hillsbrad", and
PortalManager.get_destination keys on zone.name - so the lookup missed on every tile and try_use_portal
quietly returned False. Two zones out of sixty-one were wrong and it took a player walking into a door
to find out.

So this does not inspect the tables. It asks the live PortalManager the same question the game asks, from
the live zones, and then checks the player can actually stand where they land:

  1  zone.name == the key it is registered under in create_all_zones   (the Hillsbrad killer)
  2  every declared portal tile resolves through get_destination
  3  every destination zone exists
  4  the ACTUAL landing tile, computed the way zone_manager.transition_to_zone computes it

     THIS TOOK THREE GOES AND THE LESSON IS THE POINT. The first version checked PortalManager's raw
     spawn and called 23 cave exits broken. The second added a one-tile southward nudge and still called
     21 broken. Both were wrong, and in both cases the shipped game was fine. The real rule, at
     world/zone_manager.py:374, is: offset 2 north, then +3 south when LEAVING A CAVE for the overworld,
     and then a safety net that snaps to the nearest walkable tile if the static coordinate has gone
     stale. A verifier that models the engine approximately is worse than none, because it buries real
     failures under noise it invented - so this replicates all three steps.

     The net means a stale coordinate does not strand anybody, so relying on it is reported as DRIFT
     rather than failure: the portal works, but its registry entry no longer matches the map and will
     keep decaying. Only a landing the net cannot rescue is a failure.
  5  every portal tile is itself walkable and reachable, so the player can get to the door
  6  one-way portals are reported, since the registry is one-way by design and a missing return trip is
     usually a mistake rather than a decision
"""
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from world.portal_manager import PortalManager          # noqa: E402
from world.zone_generator import create_all_zones       # noqa: E402

#: Portals with no return trip that are deliberate. Anything else one-way gets reported.
ONE_WAY_OK = set()


def nearest_walkable(zone, x, y, rad=12):
    """Mirror of zone_manager._find_nearest_walkable: the engine's safety net for stale coordinates."""
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if 0 <= x + dx < zone.width and 0 <= y + dy < zone.height \
                    and zone.is_walkable(x + dx, y + dy):
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, x + dx, y + dy)
    return None if best is None else (best[1], best[2])


def reachable_from_any(zone, targets):
    """Flood from the zone's start (or any walkable tile) and report which targets were found."""
    start = getattr(zone, "player_start", None) or getattr(zone, "start", None)
    if not (start and zone.is_walkable(*start)):
        start = next(((x, y) for y in range(zone.height) for x in range(zone.width)
                      if zone.is_walkable(x, y)), None)
    if start is None:
        return set()
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < zone.width and 0 <= n[1] < zone.height \
                    and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return {t for t in targets if tuple(t) in seen}


def main():
    only = None
    if "--zone" in sys.argv:
        only = sys.argv[sys.argv.index("--zone") + 1]

    zones = create_all_zones()
    pm = PortalManager()
    fails = []
    drift = []

    # ---- 1: the Hillsbrad killer. zone.name must equal the registry key.
    print("== zone.name vs registry key  (a mismatch kills every portal in that zone, silently)")
    bad_names = [(k, z.name) for k, z in zones.items() if getattr(z, "name", k) != k]
    print(f"  {len(zones)} zones, {len(bad_names)} mismatched")
    for k, n in bad_names:
        print(f"  FAIL registry {k!r} but zone.name {n!r}")
        fails.append(f"zone.name {n!r} != key {k!r} - every portal in it is dead")

    # ---- 2-5: walk every declared portal through the real lookup
    print("\n== portals")
    links = {}
    total = dead = 0
    for key in sorted(zones):
        if only and key != only:
            continue
        positions = pm.get_portal_positions(key)
        if not positions:
            continue
        zone = zones[key]
        found = reachable_from_any(zone, positions)
        rows = []
        for (px, py) in sorted(positions):
            total += 1
            dest = pm.get_destination(key, px, py)
            if dest is None:
                rows.append(f"    ({px:>3},{py:>3})  FAIL - declared but does not resolve")
                fails.append(f"{key} ({px},{py}) does not resolve")
                dead += 1
                continue
            dz, sx, sy = dest
            tz = zones.get(dz)
            notes = []
            if tz is None:
                notes.append("DEST ZONE MISSING")
                fails.append(f"{key} ({px},{py}) -> unknown zone {dz!r}")
            else:
                # world/zone_manager.py:374, exactly.
                if getattr(zone, "is_cave", False) and not getattr(tz, "is_cave", False):
                    sy += 3            # clear of the cave-mouth landmark AND of the trigger tile
                if not tz.is_walkable(sx, sy):
                    rescued = nearest_walkable(tz, sx, sy)
                    if rescued is None:
                        notes.append(f"STRANDED at ({sx},{sy}) - no walkable tile in range")
                        fails.append(f"{key} ({px},{py}) -> {dz} strands the player at ({sx},{sy})")
                    else:
                        drift.append(f"{key} ({px},{py}) -> {dz} ({sx},{sy}) snapped to {rescued}")
                        notes.append(f"DRIFT - snapped to {rescued}")
                        sx, sy = rescued
            if not zone.is_walkable(px, py):
                notes.append("PORTAL TILE NOT WALKABLE")
                fails.append(f"{key} ({px},{py}) portal tile is not walkable")
            elif (px, py) not in found:
                notes.append("PORTAL UNREACHABLE")
                fails.append(f"{key} ({px},{py}) cannot be walked to")
            links[(key, dz)] = True
            rows.append(f"    ({px:>3},{py:>3}) -> {dz:28s} land ({sx:>3},{sy:>3})  "
                        + ("ok" if not notes else "FAIL " + "; ".join(notes)))
        print(f"  {key}  ({len(positions)})")
        for r in rows:
            print(r)

    # ---- 6: one-way links
    print("\n== return trips")
    oneway = [(a, b) for (a, b) in links if (b, a) not in links and (a, b) not in ONE_WAY_OK]
    print(f"  {len(links)} links, {len(oneway)} with no return trip")
    for a, b in sorted(oneway):
        print(f"  one-way: {a} -> {b}  (no portal back)")
        fails.append(f"one-way link {a} -> {b}")

    print(f"\n== drift  (works, but the registry entry no longer matches the map)")
    print(f"  {len(drift)} portals relying on the engine's nearest-walkable net")
    for d in drift:
        print("   ", d)

    print(f"\n{total} portals checked, {dead} unresolved, {len(drift)} drifting")
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    for f in fails:
        print("  -", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
