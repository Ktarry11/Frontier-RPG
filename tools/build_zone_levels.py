#!/usr/bin/env python3
"""Writes data/zones/zone_levels.json: zone name -> [level_min, level_max]. Idempotent.

    PYTHONPATH=. python3 tools/build_zone_levels.py

For the overworld banner - "~ Valley of Trials - Level 1-6 ~". Kyle asked for the zone's band to
be on screen, which the game knows four different ways and had never written down once.

DERIVED, NOT HAND-WRITTEN, and that is the whole point of this file existing. A hand-kept table of
a hundred zones' level ranges is a table that is wrong within two content passes and wrong
silently, because nothing in the game reads it except a label. Every number here comes from the
creatures that actually spawn in the zone, so it cannot drift from what the player meets.

THREE SOURCES, IN ORDER:

  1. AN OPEN ZONE takes the band of its own creatures - the open_zone table plus every subzone -
     EXCLUDING is_boss entries. Rares and pinned bosses sit above their zone on purpose (a 47 rare
     in a 44-47 zone, a 53 boss at the end of a 48-52 dungeon), so counting them would quietly
     inflate every band in the game by two or three levels.
  2. A CAVE OR DUNGEON takes the band of its own table, which lives under its parent zone's
     "caves" key. Same boss exclusion, for the same reason.
  3. A TOWN has no creatures at all, so it INHERITS from the zone that leads into it. Steamwheedle
     Port is 41-44 because Northern Tanaris is, which is also the honest answer to "what level is
     this town" - a town is as dangerous as the ground around it, which is to say not at all, and
     what the player wants to know is whether they are in the right part of the world.

An audit at the end requires every zone the game actually builds to come out with a band, so a new
zone that forgets its encounter table shows up here rather than as a blank label.
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

OUT = ROOT / "data/zones/zone_levels.json"
ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"


#: Fraction of the weighted spawn mass to trim off each end before reading the band.
#: WHY TRIM AT ALL. Eastern Hillsbrad's table holds a Worg Prowler (11-14) and a Giant Spider
#: (11-17) alongside twelve creatures at 22-26, because those two are generic animals shared with
#: the early zones. The raw min/max is 11-27, which is TRUE - they do spawn - and useless on a
#: label, because the zone is a 22-26 zone with two strays in it. Weighting by encounter weight
#: and cutting the thin tails leaves the band a player would actually report.
#:
#: It is weighted, not a plain percentile over creature names, so a creature that appears at
#: weight 2 out of 40 cannot move the band the way one at weight 6 can.
#:
#: TRIMMED AT THE BOTTOM ONLY. Trimming both ends by the same fraction cut Valley of Trials to 1-5
#: and Durotar to 6-12, and both of those top ends are real - Durotar genuinely runs to 18 because
#: it is the whole starter continent. The strays are always at the FLOOR, because the generic
#: low-level animals (worgs, spiders, murlocs) are the ones shared across zones; nothing shares a
#: creature DOWNWARD into a zone it is too strong for. So the ceiling is taken as it is.
TRIM_LO, TRIM_HI = 0.06, 0.0


def _band(entries, creatures):
    """(lo, hi) over non-boss creatures, trimmed by weighted spawn mass, or None.

    `entries` is {creature name: encounter weight}.
    """
    mass = {}
    for n, w in entries.items():
        c = creatures.get(n)
        if not c or c.get("is_boss") or w <= 0:
            continue
        a, b = c.get("level_range", [None, None])[:2]
        if a is None:
            continue
        span = max(1, b - a + 1)
        for lv in range(a, b + 1):
            mass[lv] = mass.get(lv, 0.0) + w / span
    if not mass:
        return None
    total = sum(mass.values())
    levels = sorted(mass)

    run, lo = 0.0, levels[0]
    for lv in levels:
        run += mass[lv]
        if run > total * TRIM_LO:
            lo = lv
            break
    run, hi = 0.0, levels[-1]
    for lv in reversed(levels):
        run += mass[lv]
        if run > total * TRIM_HI:
            hi = lv
            break
    return (lo, hi) if lo <= hi else (levels[0], levels[-1])


def main():
    creatures = json.loads(CRE.read_text(encoding="utf-8"))["creatures"]
    zones = json.loads(ENC.read_text(encoding="utf-8"))["zones"]

    bands = {}
    for zname, z in zones.items():
        entries = dict(z.get("open_zone", {}).get("creatures", {}))
        for sz in z.get("subzones", {}).values():
            for n, w in sz.get("creatures", {}).items():
                entries[n] = max(entries.get(n, 0), w)
        b = _band(entries, creatures)
        if b:
            bands[zname] = b
        # caves and dungeons carry their own table under the parent
        for cname, cv in z.get("caves", {}).items():
            cb = _band(dict(cv.get("creatures", {})), creatures)
            if cb:
                bands[cname] = cb

    # ---- towns and anything else with no creatures of its own: inherit from what leads in
    from world.portal_manager import PortalManager
    links = PortalManager()._links
    inbound = defaultdict(set)
    for src, doors in links.items():
        for (_tile, dest) in doors.items():
            inbound[dest[0]].add(src)

    from world.zone_generator import create_all_zones
    built = create_all_zones()

    # SAME REGION ONLY, and that filter is doing real work. Taking the union of everything that
    # portals into a town gave Booty Bay 12-50 and the Grom'gol zeppelin tower 6-34, because boats
    # and zeppelins link places a continent apart and a town is not the range of everywhere you
    # can sail to from it. Filtering the inbound neighbours to the ones that share the town's
    # region leaves the ground it is actually standing in: Steamwheedle Port takes Northern
    # Tanaris and not the Shimmering Flats two zones up the road.
    region = {n: getattr(z, "region", None) for n, z in built.items()}
    for zname in built:
        if zname in bands:
            continue
        near = [s for s in inbound.get(zname, ()) if s in bands]
        same = [s for s in near if region.get(s) and region[s] == region.get(zname)]
        cands = [bands[s] for s in (same or near)]
        if cands:
            bands[zname] = (min(c[0] for c in cands), max(c[1] for c in cands))

    missing = sorted(z for z in built if z not in bands)
    print(f"{len(bands)} zones banded, {len(built)} built")

    # A BAND WIDER THAN THIS IS ALMOST ALWAYS A BUG, not a big zone - either a stray creature in
    # an encounter table or a town that inherited from somewhere it is not. Reported, not fatal:
    # Durotar genuinely runs 6-18 because it is the whole starter continent.
    wide = sorted((z, b) for z, b in bands.items() if b[1] - b[0] > 14)
    if wide:
        print(f"\n  {len(wide)} band(s) wider than 14 levels - check these are real:")
        for z, b in wide:
            print(f"    {z:30} {b[0]}-{b[1]}")
    if missing:
        print("\nFAILED - these zones have no level band and would show a blank label:")
        for z in missing:
            print(f"  - {z}")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out = {"_notes": ("Zone name -> [level_min, level_max], for the overworld banner. DERIVED by "
                      "tools/build_zone_levels.py from the creatures that actually spawn - never "
                      "hand-edit this, edit the encounter tables and re-run."),
           "zones": {z: list(b) for z, b in sorted(bands.items())}}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"-> {OUT.relative_to(ROOT)}")
    for z in ("Valley of Trials", "Durotar", "Northern Tanaris", "Steamwheedle Port",
              "The Lashings", "The Abyssal Sands", "Glittervein", "The Mother Vein",
              "The Cistern"):
        if z in bands:
            print(f"    {z:26} {bands[z][0]}-{bands[z][1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
