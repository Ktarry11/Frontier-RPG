#!/usr/bin/env python3
"""What backdrop does every zone actually fight on?

Kyle, 2026-10-31: "also we need to ensure backgrounds are proper. grom's rest is
a fel dungeon and it just has standard RFC background."

He is right, and the cause is structural rather than a one-off: a zone with no
ZONE_BACKGROUND override falls through to its BIOME, and a biome is a palette
for a FAMILY of places. Grom's Rest is built on cave_demonic, which routes to
fire_dungeon - the same pack Ragefire Chasm uses, because for a Burning Blade
cave that is correct. For a fel-corrupted forest dungeon it is not.

There is no silent failure to detect here, because get_background_folder always
returns something. That is exactly the problem: a wrong backdrop looks like a
working one. So this tool does not pass or fail - it PRINTS the resolved backdrop
for every zone, grouped by pack, so a wrong one can be seen rather than stumbled
into during play.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.combat_backgrounds import (get_background_for_place, ZONE_BACKGROUND,
                                      BIOME_TO_BACKGROUND)


def main():
    from world.zone_generator import create_all_zones
    zones = create_all_zones()

    # Ask the SAME function the game asks, with the same is_cave flag the
    # loader passes. A first version of this tool read a `.biome` attribute off
    # the zone, which does not exist, so every zone defaulted to "grassland" and
    # the report cheerfully claimed 61 zones fight in a green forest. Measuring
    # through the real entry point is the only way this is worth anything.
    from world.tile_textures import get_biome_for_zone

    by_pack = collections.defaultdict(list)
    for name, z in zones.items():
        is_cave = bool(getattr(z, "is_cave", False) or getattr(z, "boss_positions", None))
        biome = get_biome_for_zone(name, is_cave=is_cave)
        folder, variant = get_background_for_place(name, biome)
        src = "override" if name in ZONE_BACKGROUND else f"biome:{biome}"
        by_pack[folder].append((name, src))

    print(f"  {len(zones)} zones across {len(by_pack)} background packs")
    print(f"  {len(ZONE_BACKGROUND)} have an explicit override; the rest follow their biome\n")

    for pack in sorted(by_pack):
        rows = sorted(by_pack[pack])
        print(f"  == {pack}  ({len(rows)})")
        for name, src in rows:
            mark = "" if src == "override" else "   <- from biome, never reviewed"
            print(f"       {name:42s} {src}{mark}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
