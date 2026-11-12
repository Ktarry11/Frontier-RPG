"""
A chest's loot is the ZONE's level, whoever opens it.

Kyle, 10 Nov: "chest items should be based on zone not on party level! i opened a chest in STV
and got a lvl 58 item."

For every zone with a level band, a level 60 opening its chests must never get an item above
the top of the band, and a level 1 must get the same range - the opener does not move it.
Rolled through the real ChestManager and LootGenerator, 150 chests a zone.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from world.chest_manager import get_chest_manager
    from world.zone_levels import _load
    cm = get_chest_manager()
    gen = cm._get_loot_generator()
    bands = _load()
    if len(bands) < 20:
        print(f"FAIL only {len(bands)} zone bands loaded - the rig is not seeing the zones")
        return 1
    bad = []
    checked = 0
    for zone, (lo, hi) in sorted(bands.items()):
        if cm._dungeon_level_for_zone(zone) is not None:
            continue                      # a dungeon uses its boss's level, tested elsewhere
        checked += 1
        for opener in (60, 1):
            top = 0
            for _ in range(150):
                level = cm.chest_level(zone, opener)
                if not (lo <= level <= hi):
                    bad.append(f"{zone} ({lo}-{hi}): chest level {level} for a level {opener} opener")
                    break
                item = gen.generate_loot_for_creature(creature_level=level, player_level=60,
                                                      drop_chance=1.0)
                if item is not None:
                    top = max(top, item.item_level)
            if top > hi:
                bad.append(f"{zone} ({lo}-{hi}): a level {opener} opener got item level {top}")
    print(f"{checked} open zones, 150 chests each, opened at level 60 and level 1")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:20]:
            print("  ", b)
        return 1
    print("chest levels OK - the zone sets the level, not the opener.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
