#!/usr/bin/env python3
"""Which authored creatures can a player actually meet?

    PYTHONPATH=. python3 tools/qa_creature_reachability.py [--list]

A creature in creatures.json costs real work - stats, a level band, an ability kit, a sprite
rule - and none of that is visible to anyone unless something places it. A creature nobody
placed is indistinguishable from a creature somebody placed badly, because both are simply
never seen.

EVERY WAY A CREATURE REACHES THE WORLD, and this list is the whole point of the file. I twice
reported wrong numbers for this by checking some of them and assuming the rest:

  1. encounters.json open_zone                  zones[zone]["open_zone"]["creatures"]
  2. encounters.json subzones                   zones[zone]["subzones"][sub]["creatures"]
  3. encounters.json caves                      zones[REGION]["caves"][cave]["creatures"]
                                                - keyed by the cave's PARENT, not its own name
  4. data/dungeons/trash_packs.json             authored dungeon packs
  5. zone.trash_packs set in a handbuilt module pack adds pinned in code, e.g. the Gurbashi
                                                arena's Jin'sha, who is deliberately NOT in any
                                                table and reachable only this way
  6. zone.boss_positions set in a module        pinned bosses

NOT a source, and this matters: data/creatures/spawn_points.json is read by NOTHING at runtime
(only two one-off sync tools and a comment). A creature that appears only there is unreachable,
so counting it as placed hides exactly the bug this tool is for.

Sources 5 and 6 only exist once the zones are BUILT, so this builds them rather than reading
files, which is also the only honest way to see what ships.
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))


def placed():
    """-> {creature name: {how it is placed}}"""
    where = defaultdict(set)
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    for zn, z in enc.items():
        for n in (z.get("open_zone") or {}).get("creatures") or {}:
            where[n].add(f"{zn} (open)")
        for sn, s in (z.get("subzones") or {}).items():
            for n in (s.get("creatures") or {}):
                where[n].add(f"{zn}/{sn}")
        for cn, c in (z.get("caves") or {}).items():
            for n in (c.get("creatures") or {}):
                where[n].add(cn)

    tp = ROOT / "data/dungeons/trash_packs.json"
    if tp.exists():
        for n in re.findall(r'"([^"]+)"', tp.read_text(encoding="utf-8")):
            where[n].add("trash_packs.json")

    from world.zone_generator import create_all_zones
    zones = create_all_zones()
    if isinstance(zones, dict):
        zones = list(zones.values())
    for z in zones:
        for entry in (getattr(z, "boss_positions", None) or []):
            if len(entry) >= 3 and isinstance(entry[2], str):
                where[entry[2]].add(f"{z.name} (pinned boss)")
        for pack in (getattr(z, "trash_packs", None) or []):
            for member in pack:
                if len(member) >= 3 and isinstance(member[2], str):
                    where[member[2]].add(f"{z.name} (pack)")
    return where, len(zones)


def main():
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    where, nzones = placed()
    reach = {n for n in cre if n in where}
    orphan = sorted(set(cre) - reach)

    # Anything only in the legacy file is NOT reachable - calling it placed is the mistake.
    legacy = set(re.findall(r'"creature":\s*"([^"]+)"',
                            (ROOT / "data/creatures/spawn_points.json").read_text(encoding="utf-8")))
    stranded = sorted(set(orphan) & legacy)

    print(f"{len(cre)} creatures authored across {nzones} built maps")
    print(f"  {len(reach)} reachable, {len(orphan)} unreachable "
          f"({len(orphan) / len(cre):.0%})")
    if stranded:
        print(f"  {len(stranded)} of those appear ONLY in spawn_points.json, which nothing reads "
              f"at runtime: {stranded}")

    if orphan:
        bands = defaultdict(list)
        for n in orphan:
            lo = (cre[n].get("level_range") or [0])[0]
            bands[(lo // 10) * 10].append(n)
        print("\n  unreachable by level band:")
        for lo in sorted(bands):
            names = bands[lo]
            nb = sum(1 for n in names if cre[n].get("is_boss"))
            print(f"    {lo:2d}-{lo + 9:<3d} {len(names):3d}  ({nb} boss)")
        if "--list" in sys.argv:
            print("\n  every unreachable creature:")
            for n in orphan:
                c = cre[n]
                print(f"    {n:34s} lvl {str(c.get('level_range')):10s} "
                      f"{c.get('template','?'):18s}{' BOSS' if c.get('is_boss') else ''}")

    # Reported, not failed. A creature written ahead of the zone that will use it is normal
    # authoring; the number mattering is what it drifts to, and which ones are bosses.
    print("\nreachability reported, not asserted - placing a creature is content design. "
          "Run with --list for the full roster.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
