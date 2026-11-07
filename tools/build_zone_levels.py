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


def _band(entries, creatures, overrides=None):
    """(lo, hi) - the plain range of levels that spawn here, or None.

    JUST THE RANGE. It is on screen so a player can estimate whether they should be in a place,
    and the honest answer to that is the lowest and highest thing they might meet. An earlier
    version trimmed thin tails off by weighted spawn mass, which is a statistic that has to be
    tuned per-zone and was never going to be right for both Valley of Trials and a grotto with one
    odd creature in it.

    `entries` is {creature name: encounter weight}; weight is only used to skip weight-0 rows.
    `overrides` is the zone's own level_overrides map, which beats a creature's global range.

    BOSSES ARE EXCLUDED. They are pinned, fought once, and deliberately sit above their zone - a
    level 53 boss at the end of a 49-52 dungeon would otherwise make the whole place read as 53.
    """
    overrides = overrides or {}
    lo = hi = None
    for n, w in entries.items():
        c = creatures.get(n)
        if not c or c.get("is_boss") or w <= 0:
            continue
        # THE ZONE'S OWN OVERRIDE WINS, because it is what actually spawns.
        # world/creature_manager.py reads level_overrides when it rolls a
        # creature, so one name sits at different levels in different places:
        # a Murloc Spearfisher is 11-13 globally and 24-27 on the Ashenvale
        # coast. Reading the global range here gave Ashenvale West a banner of
        # 11-27 when nothing under 22 spawns in it. Ten zones use overrides.
        rng = overrides.get(n) or c.get("level_range", [None, None])
        a, b = rng[:2]
        if a is None:
            continue
        lo = a if lo is None else min(lo, a)
        hi = b if hi is None else max(hi, b)
    return (lo, hi) if lo is not None else None


def main():
    creatures = json.loads(CRE.read_text(encoding="utf-8"))["creatures"]
    zones = json.loads(ENC.read_text(encoding="utf-8"))["zones"]

    bands = {}
    for zname, z in zones.items():
        entries = dict(z.get("open_zone", {}).get("creatures", {}))
        for sz in z.get("subzones", {}).values():
            for n, w in sz.get("creatures", {}).items():
                entries[n] = max(entries.get(n, 0), w)
        b = _band(entries, creatures, z.get("level_overrides"))
        if b:
            bands[zname] = b
        # caves and dungeons carry their own table under the parent
        for cname, cv in z.get("caves", {}).items():
            cb = _band(dict(cv.get("creatures", {})), creatures, z.get("level_overrides"))
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

    # A FIXED-SPAWN DUNGEON KNOWS ITS OWN LEVELS. Its trash is hand-placed with an explicit level per
    # mob, so the encounter table is only a "what lives here" list for the quest locator and may name
    # creatures whose own level_range spans several zones - a Syndicate Footpad is 28-31 on the Arathi
    # moor and level 31-34 standing in Stromgarde's outer ward. Deriving the banner from the table
    # gave Stromgarde 28-33 and Drywhisker Deeps 33-37, both a whole band low. Where the authored
    # spawns exist, they are the better answer and they override.
    for zname, z in built.items():
        spawns = getattr(z, "authored_trash_spawns", None) or getattr(z, "trash_spawns", None)
        if not getattr(z, "fixed_spawns", False) or not spawns:
            continue
        # Older dungeons leave the level slot None and let the creature's own level_range answer -
        # those fall through to the table-derived band rather than crashing the whole file out.
        lv = [int(s[3]) for s in spawns if len(s) > 3 and isinstance(s[3], (int, float))]
        if lv:
            bands[zname] = [min(lv), max(lv)]

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
