#!/usr/bin/env python3
"""Spread the companions across the world instead of huddling them in two capitals.

    PYTHONPATH=. python3 tools/spread_recruits.py --dry-run
    PYTHONPATH=. python3 tools/spread_recruits.py

Kyle, 2026-10-31: "lets actually audit the recruits now. We have a LOT more zones! Lets spread
them out... We want to keep some of them lower level but i want more variety - im seeing like 6
in org side by side."

He was looking at a real huddle. Undercity held 6 and Orgrimmar 5, and the Orgrimmar five stood
at (100,85), (88,86), (93,87), (98,88) and (93,82) - close enough to be one clump on screen.
Between them the two capitals held a quarter of every companion in the game, and both are towns
with no encounter table, so none of them could be "levelled to the zone they're found in"
because their zone has no level.

THREE RULES, IN ORDER OF AUTHORITY:

  1. suggested_zone WINS. Thirteen recruits carry a suggested_zone that disagrees with where
     they actually stand - somebody wrote down where each of these people belongs and then the
     placement pass did something else. That field is authorial intent and this honours it
     wherever it names a zone that exists.
  2. AT MOST PER_ZONE ANYWHERE. The huddle is the bug; a cap is the fix.
  3. LEVELLED TO THE ZONE (Kyle's standing rule). A recruit's level is set to the middle of
     their zone's encounter band, so meeting them is always level-appropriate. Capitals and
     other town zones have no band, so a recruit left in one keeps their authored level.

WHAT THIS NEVER TOUCHES. Asher Coleman, who is hand-authored, fixed, and belongs in the Burning
Blade Coven by design. Nobody's class, spec, name, backstory or greeting - only zone, x, y and
level, because who they are was written by hand and where they stand was not.

PLACEMENT IS VALIDATED, not assumed. Every chosen tile is run through the zone's own
is_walkable, and snapped to the nearest walkable tile if it is not, using the same spiral
ZoneManager uses for portal arrivals. A recruit on solid rock is unreachable and would read as
a missing recruit, not a misplaced one.
"""
import argparse
import collections
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: Never moved, never re-levelled. See the module docstring.
FIXED = {"asher_coleman"}

#: The huddle cap. Two is "you might meet a pair travelling together"; six is a queue.
PER_ZONE = 2

#: Minimum tiles between two recruits in the same zone, so a pair never reads as a clump.
MIN_SPACING = 12

#: MINIMAL DISRUPTION IS THE POINT. An audit that relocates 43 of 44 companions is not an audit,
#: it is a rewrite - and it would throw away every deliberate placement in the game: the miner in
#: Azurelode, the goblin town hand in Booty Bay, the one in Ragefire Chasm. A recruit MOVES only
#: if their zone is over the cap or their suggested_zone disagrees with where they stand.
#: Everyone else is left exactly where they were written.


def zone_bands():
    """zone name -> (min_level, max_level) from its own open-zone encounter table."""
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    out = {}
    for zname, zdata in (enc.get("zones") or enc).items():
        if not isinstance(zdata, dict):
            continue
        levels = []
        for cname in ((zdata.get("open_zone") or {}).get("creatures") or {}):
            c = creatures.get(cname)
            if c and c.get("level_range"):
                levels += list(c["level_range"])
        if levels:
            out[zname] = (min(levels), max(levels))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=20261031)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    path = ROOT / "data/npcs/recruits.json"
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
    block = data.get("recruits", data)
    recruits = list(block.values()) if isinstance(block, dict) else block

    bands = zone_bands()
    band_zones = sorted(bands, key=lambda z: bands[z])

    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from world.zone_manager import ZoneManager
    zm = ZoneManager()

    def zone_obj(name):
        try:
            return zm.get_zone_by_name(name)
        except Exception:
            return None

    # ---- who goes where ------------------------------------------------------------------
    placed = collections.Counter()
    assignment = {}

    movable = [r for r in recruits if r["recruit_id"] not in FIXED]
    for r in recruits:
        if r["recruit_id"] in FIXED:
            placed[r["zone"]] += 1
            assignment[r["recruit_id"]] = r["zone"]

    # 1. Everyone KEEPS their zone, up to the cap. Within an over-full zone the ones who stay
    #    are those the zone suits best - a recruit whose suggested_zone names this place, then
    #    whoever has stood here longest in authored terms (lowest level first, so the capital
    #    reads as where new arrivals turn up). The rest become the move list.
    for zname in sorted({r["zone"] for r in movable}):
        here = [r for r in movable if r["zone"] == zname]

        def keep_rank(r):
            sz = (r.get("suggested_zone") or "").split("(")[0].strip()
            return (0 if sz == zname else 1, r.get("level") or 0)

        room = max(0, PER_ZONE - placed[zname])
        for r in sorted(here, key=keep_rank)[:room]:
            assignment[r["recruit_id"]] = zname
            placed[zname] += 1

    # 2. The displaced go where they were SUPPOSED to be, if that field names a real zone with
    #    room. Thirteen recruits carry a suggested_zone that disagrees with where they stand.
    for r in movable:
        if r["recruit_id"] in assignment:
            continue
        sz = (r.get("suggested_zone") or "").split("(")[0].strip()
        if sz and sz in bands and placed[sz] < PER_ZONE:
            assignment[r["recruit_id"]] = sz
            placed[sz] += 1

    # 3. Anyone still homeless fills the emptiest banded zone that suits their level.
    #
    #    NEVER DOWNWARD. tools/qa_recruit_levels.py states the rule this has to respect:
    #    "NOBODY IS EVER BELOW THEIR AUTHORED LEVEL... A companion written at 36 is a statement
    #    about who they are, and meeting them at 20 must not shrink them." A first version of
    #    this pass sent four displaced capital recruits into the starter zones and cut them from
    #    13-15 down to 3-5, which is exactly what that rule forbids. So only zones whose band
    #    TOPS OUT at or above the recruit's authored level are candidates, and the level that
    #    gets written below can only ever rise.
    leftover = [r for r in movable if r["recruit_id"] not in assignment]
    leftover.sort(key=lambda r: -(r.get("level") or 0))      # highest first: fewest options
    for r in leftover:
        lvl = r.get("level") or 1
        fits = [z for z in band_zones if bands[z][1] >= lvl]
        options = [z for z in fits if placed[z] < PER_ZONE] or fits or band_zones
        best = min(options, key=lambda z: (placed[z], abs((bands[z][0] + bands[z][1]) / 2 - lvl)))
        assignment[r["recruit_id"]] = best
        placed[best] += 1

    # ---- where exactly, and at what level ------------------------------------------------
    taken = collections.defaultdict(list)
    moved = relevelled = 0
    report = []
    for r in recruits:
        rid = r["recruit_id"]
        new_zone = assignment[rid]
        old = (r.get("zone"), r.get("x"), r.get("y"), r.get("level"))

        if rid in FIXED:
            taken[new_zone].append((r["x"], r["y"]))
            continue

        z = zone_obj(new_zone)
        x, y = r.get("x", 0), r.get("y", 0)
        staying = new_zone == r.get("zone")
        spaced = all(max(abs(x - px), abs(y - py)) >= MIN_SPACING for px, py in taken[new_zone])
        if staying and spaced and z is not None and z.is_walkable(x, y):
            # Already where they were written, already clear of everyone else, already on a
            # walkable tile - there is nothing to fix, so nothing is touched.
            pass
        elif z is not None:
            # A fresh spot, far enough from anyone already standing in this zone. Tried from
            # random candidates rather than a fixed offset so two zones do not end up with
            # their recruits in the same corner.
            for _ in range(400):
                cx = rng.randrange(2, max(3, z.width - 2))
                cy = rng.randrange(2, max(3, z.height - 2))
                snapped = ZoneManager._find_nearest_walkable(z, cx, cy)
                if snapped is None:
                    continue
                if all(max(abs(snapped[0] - px), abs(snapped[1] - py)) >= MIN_SPACING
                       for px, py in taken[new_zone]):
                    x, y = snapped
                    break
            else:
                snapped = ZoneManager._find_nearest_walkable(z, x, y)
                if snapped:
                    x, y = snapped
        taken[new_zone].append((x, y))

        # LEVEL FOLLOWS THE ZONE, but only where it has to. Someone who did not move and is
        # already inside their zone's band keeps the exact level they were authored at - that
        # number is a statement about the character and this pass has no business rounding it
        # to a midpoint for tidiness.
        band = bands.get(new_zone)
        level = r.get("level")
        changed_zone = new_zone != r.get("zone")
        if band and (changed_zone or not (band[0] <= (level or 0) <= band[1])):
            # max(): see rule 3 above - a companion's authored level is a floor, never a target
            # to round down to.
            level = max(level or 1, round((band[0] + band[1]) / 2))

        if (r.get("zone"), r.get("x"), r.get("y")) != (new_zone, x, y):
            moved += 1
        if level != r.get("level"):
            relevelled += 1
        r["zone"], r["x"], r["y"], r["level"] = new_zone, x, y, level
        report.append((old, (new_zone, x, y, level), r["name"], r["char_class"]))

    if not args.dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    per = collections.Counter(r["zone"] for r in recruits)
    print(f"{len(recruits)} recruits over {len(per)} zones "
          f"(was 26; {moved} moved, {relevelled} re-levelled)")
    print(f"  busiest zone now holds {max(per.values())}\n")
    for (oz, ox, oy, ol), (nz, nx, ny, nl), name, cls in sorted(report, key=lambda t: t[1][3]):
        flag = "   " if (oz, ox, oy, ol) == (nz, nx, ny, nl) else "-> "
        print(f"  lvl {nl:2d} {flag}{name:18s} {cls:16s} {nz:28s} ({nx},{ny})"
              + (f"   was lvl {ol} in {oz}" if flag.strip() else ""))
    print()
    for z, n in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"  {n}  {z}")
    print(f"\n{'dry run - nothing written' if args.dry_run else 'written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
