#!/usr/bin/env python3
"""Every map resolves the encounter table it was written to have.

    PYTHONPATH=. python3 tools/qa_encounter_tables.py

THE BUG THIS EXISTS FOR. The Frostward Descent - the only route into the Crystalline Underdark,
written as levels 31-33 - had a complete seven-creature roster and three hand-placed bosses, and
spawned level 11-14 Worg Prowlers and level 24-26 Syndicate Bandits instead, for as long as it
has been in the game.

Nothing was missing. The table was in the wrong PLACE. A cave's table is keyed by its PARENT:

    ZoneManager.trigger_encounter    zone_name = current_zone.region   (for a cave)
    get_location_context             -> ("cave", current_zone.name)
    CreatureManager                  -> zones[region]["caves"][cave name]

and the roster sat at zones["The Frostward Descent"]["open_zone"], which nothing reads. Every
step of that failure is silent and plausible on its own: the lookup returns {}, cave_spawns
populate() returns early so the pinned bosses never appear, and trigger_encounter falls back to
the PARENT zone's open table - so the cave is not empty, it is full of the wrong zone's mobs at
the wrong level, which looks like content rather than a bug.

A cave also never consults subzones (get_location_context returns ("cave", name) before it looks
at any rectangle), so a band written as subzones inside a cave is dead on arrival. That is worth
stating because it is the obvious first fix and it does nothing.

FOUR CLAIMS:

  1. EVERY CAVE RESOLVES A NON-EMPTY TABLE BY THE PATH THE GAME USES. Not "a table exists
     somewhere in the file under this name" - the lookup the running game performs.
  2. EVERY PINNED BOSS IS IN ITS MAP'S TABLE. cave_spawns places them from the table; a boss
     pinned in a handbuilt module but absent from the table is a boss nobody can fight.
  3. EVERY CREATURE NAMED IN A TABLE EXISTS AND SPAWNS. An unknown template is a hard error at
     spawn time, i.e. mid-fight, on the player's screen.
  4. A CAVE'S LEVELS MATCH THE MAP IT IS IN. A table resolving to the parent zone's mobs passes
     claims 1-3 trivially - the fallback IS a table of real creatures - so this is the claim
     that would have caught the Frostward bug on its own.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

from world.creature_manager import CreatureManager  # noqa: E402

#: How far a cave's creatures may sit outside the band its own module declares before it is
#: likely showing the parent zone's mobs rather than its own. Generous: bands overlap by design.
LEVEL_SLACK = 6


def main():
    bad = []
    cm = CreatureManager()
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]

    from world.zone_generator import create_all_zones
    zones = create_all_zones()
    if isinstance(zones, dict):
        zones = list(zones.values())

    caves = [z for z in zones if getattr(z, "is_cave", False)]
    checked = 0
    for z in caves:
        region = getattr(z, "region", None)
        if not region:
            bad.append(f"{z.name!r} is a cave with no .region, so its table can never be found")
            continue
        table = cm.get_encounter_table(region, "cave", z.name)
        if not table:
            bad.append(f"{z.name!r} resolves NO table at zones[{region!r}]['caves'][{z.name!r}] - "
                       f"its pinned bosses will not spawn and the player will meet {region}'s "
                       f"own mobs instead")
            continue
        checked += 1

        # 2. pinned bosses are placeable
        pinned = [n for (_x, _y, n) in (getattr(z, "boss_positions", None) or [])]
        for b in pinned:
            if b not in table:
                bad.append(f"{z.name!r} pins boss {b!r} on the map but it is not in the table, "
                           f"so cave_spawns has nothing to place")

        # 3. everything named really spawns
        for n in table:
            if n not in cre:
                bad.append(f"{z.name!r} lists {n!r}, which is not in creatures.json")
                continue
            try:
                lo = cre[n]["level_range"][0]
                if cm.spawn_creature(n, lo) is None:
                    bad.append(f"{z.name!r}: {n!r} spawned as None")
            except Exception as exc:
                bad.append(f"{z.name!r}: {n!r} raises on spawn - {exc!r}")

        # 4. the levels belong to THIS map
        lv = [cre[n]["level_range"] for n in table if n in cre]
        if lv:
            lo, hi = min(x[0] for x in lv), max(x[1] for x in lv)
            band = getattr(z, "level_band", None) or getattr(z, "level_range", None)
            if band:
                blo, bhi = band[0], band[1]
                if lo < blo - LEVEL_SLACK or hi > bhi + LEVEL_SLACK:
                    bad.append(f"{z.name!r} declares levels {blo}-{bhi} but its table spawns "
                               f"{lo}-{hi} - that spread usually means it is resolving some "
                               f"other map's table")

    print(f"{len(caves)} cave/dungeon maps, {checked} with a live table")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\nencounter tables OK - every cave resolves its own non-empty table by the path the "
          "game uses, every pinned boss is placeable from it, everything named spawns, and no "
          "cave is quietly showing its parent zone's mobs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
