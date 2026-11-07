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
import sys, os, re, collections
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

    _subzones(zones)
    _empty_packs(by_pack)
    return 0


def _subzones(zones):
    """Which subzones differ from the ground they stand on.

    Until 7 Nov this was unanswerable, because the loader never consulted
    SUBZONE_BIOME at all - it resolved a background from the zone name and
    that was the end of it, so Slug Fens fought on the same backdrop as the
    open scrub above it. Now that get_background_for_zone takes a subzone,
    the thing worth printing is the DIFFERENCE: a subzone that resolves to
    its parent's pack is not necessarily wrong, but a fen, pool, grove or
    cave that does is the bug class Kyle hit.
    """
    from world.combat_backgrounds import resolve_place
    from world.tile_textures import SUBZONE_BIOME

    # Names that promise terrain the open zone does not have. A subzone
    # matching one of these and STILL sharing its parent's pack is the
    # shortlist to review - it is not a failure, it is where to look.
    #
    # MATCHED ON WORD BOUNDARIES, not substrings. The first version used
    # `w in name.lower()` and reported 101 subzones, most of which were its
    # own fault: "Fenris Proper" matched 'fen', "Burning Blade Coven" and
    # "The Druids' Alcove" both matched 'cove', "Moonwhisper Grove" is a
    # grove in a forest and always was. A shortlist that is mostly noise is
    # a shortlist nobody reads.
    WATER = ("fen", "pool", "oasis", "spring", "lake", "marsh", "bog", "shore",
             "coast", "strand", "falls", "river", "delta", "cove", "reef")
    STONE = ("cave", "cavern", "hollow", "mine", "quarry", "ridge", "cliff",
             "crag", "peak", "barrow", "crypt", "ruin", "dig")
    GREEN = ("grove", "glade", "thicket", "wood", "orchard", "garden", "copse")

    total = differs = flagged = 0
    rows = []
    for zname, z in sorted(zones.items()):
        for sz in getattr(z, "subzones", []) or []:
            name = sz["name"] if isinstance(sz, dict) else getattr(sz, "name", None)
            if not name:
                continue
            total += 1
            is_cave = bool(getattr(z, "is_cave", False) or getattr(z, "boss_positions", None))
            own = SUBZONE_BIOME.get(name)
            pp, _, _ = resolve_place(zname, None, is_cave)
            sp, _, _ = resolve_place(zname, name, is_cave)
            if sp != pp:
                differs += 1
                rows.append((name, zname, pp, sp, "own biome"))
                continue
            # A subzone that IS its zone (a one-room cave registering
            # itself) shares the parent's pack because it is the parent.
            if name == zname:
                continue
            words = set(re.findall(r"[a-z]+", name.lower()))
            hit = next((w for group in (WATER, STONE, GREEN) for w in group
                        if w in words or w + "s" in words), None)
            if hit and not own:
                flagged += 1
                rows.append((name, zname, pp, sp, f"shares parent; name says '{hit}'"))

    print(f"  -- subzones --------------------------------------------------")
    print(f"  {total} subzones; {len(SUBZONE_BIOME)} have a biome of their own")
    print(f"  {differs} now resolve a DIFFERENT backdrop than their parent zone")
    print(f"  {flagged} are named for terrain their parent pack does not show\n")
    for name, zname, pp, sp, why in rows:
        arrow = f"{pp} -> {sp}" if pp != sp else pp
        print(f"       {name:34s} {zname:22s} {arrow:26s} {why}")
    print()


def _empty_packs(by_pack):
    """A pack routed to by nothing, or holding no images, is a black screen."""
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "assets", "backgrounds")
    bad = []
    for folder in sorted(set(BIOME_TO_BACKGROUND.values()) | set(by_pack)):
        path = os.path.join(root, folder)
        n = sum(1 for _, _, fs in os.walk(path)
                for f in fs if f.lower().endswith((".png", ".jpg", ".jpeg")))
        if n == 0:
            bad.append(folder)
        elif n <= 2:
            print(f"  thin pack: {folder} has {n} image(s)")
    for folder in bad:
        print(f"  EMPTY PACK: assets/backgrounds/{folder} has no images")
    print()


if __name__ == "__main__":
    sys.exit(main())
