#!/usr/bin/env python3
"""Install sliced background panels into assets/backgrounds/<pack>/[<variant>/].

    PYTHONPATH=. python3 tools/asset_pipeline/install_background_panels.py STAGEDIR [--dry-run]

STAGEDIR holds s1/..s5/ as written by slice_background_sheet.py, one NN.png per panel.

THE MAPPING BELOW IS THE WHOLE POINT OF THIS FILE. It was written by looking at each numbered
contact sheet and naming what the painting actually is, which is the step the creature sheets
proved cannot be skipped: there, a list with the right COUNT was in the wrong ORDER and would
have given 180 creatures the wrong sprite in silence. A panel's number means nothing except
"where it sat on the sheet", so the destination is recorded per panel, by hand, once.

Seven packs are new. Six of them exist because the game had places with nowhere to fight:
nineteen flooded/shipboard locations, the crystal Underdark, the Deep Bloom's fungal halls, two
zeppelin decks over open sky, two silithid hives and a salt pan - all of which were rendering as
a sunny green forest.
"""
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEST = ROOT / "assets" / "backgrounds"

#: (sheet, panel) -> "pack" or "pack/Variant". What each painting IS, read off the contact
#: sheets. Comments are the painting, so a wrong entry is findable by eye later.
MAPPING = {
    # ---- sheet 1 -------------------------------------------------------------
    ("s1", "00"): "desert",             # sun-bleached dunes, ribcage, cracked pan
    ("s1", "01"): "fire_dungeon",       # obsidian hall, lava seams underfoot
    ("s1", "02"): "mossy_forest",       # mystical forest, glowing motes
    # sky is what you see from a zeppelin deck: cloud and land far below. The void and the
    # constellation stair were in here and a zeppelin tower rolled DEEP SPACE, so they moved
    # to crystal, which is the arcane pack.
    ("s1", "03"): "sky",                # floating islands, waterfalls into cloud
    ("s1", "04"): "crystal",            # crystal cave, cyan and magenta spars
    ("s1", "05"): "fungal",             # surreal mushroom grove
    ("s1", "06"): "crystal",            # arcane sanctum, rune circle
    ("s1", "07"): "fire_dungeon",       # volcanic caldera
    ("s1", "08"): "ice_dungeon",        # frozen tundra under aurora
    ("s1", "09"): "blighted",           # corrupted shadow bog
    ("s1", "10"): "jungle",             # overgrown temple colonnade
    ("s1", "11"): "dark_dungeon",       # steampunk foundry - pipes and firelight

    # ---- sheet 2 -------------------------------------------------------------
    ("s2", "00"): "salt_flat",          # cracked violet salt pan, standing obelisks
    ("s2", "01"): "desert",             # lone savanna tree at sunset - the Barrens read
    ("s2", "02"): "hive",               # honeycomb chamber, insect brood
    ("s2", "03"): "mountain",           # alpine meadow under snow peaks
    ("s2", "04"): "nautical/Flooded",   # sunlit coral ruins underwater
    ("s2", "05"): "nautical/Deck",      # galleon in a lightning storm
    ("s2", "06"): "blighted",           # blighted bog, bones, dead trees
    ("s2", "07"): "dark_dungeon",       # crypt interior, blue braziers
    ("s2", "08"): "jungle",             # tropical beach and green peaks
    ("s2", "09"): "crystal",                # constellation stair through the void
    ("s2", "10"): "jungle",             # dense jungle, carnivorous plants
    ("s2", "11"): "sky",                # castle on a cloud bank at sunset

    # ---- sheet 3 -------------------------------------------------------------
    ("s3", "00"): "nautical/Hold",      # gun deck, cannons, lantern light
    ("s3", "01"): "keep",               # timber-framed village street
    ("s3", "02"): "mountain",           # red rock canyon with a timber gate
    ("s3", "03"): "mossy_forest",       # farm meadow, cottage and barn
    ("s3", "04"): "blighted",           # moonlit ruins in a purple wood
    ("s3", "05"): "keep",               # white and gold palace interior
    ("s3", "06"): "mountain",           # canyon river at dusk
    ("s3", "07"): "mossy_forest",       # autumn forest road
    ("s3", "08"): "nautical/Deck",      # wreck on rocks in a grey sea
    ("s3", "09"): "keep",               # castle courtyard, gatehouse
    ("s3", "10"): "jungle",             # jungle understorey
    ("s3", "11"): "fire_dungeon",       # lava cave
    # 12-15 are second takes of 04/09/10/11 and are in DROPPED below.

    # ---- sheet 4 -------------------------------------------------------------
    ("s4", "00"): "nautical/Flooded",   # bioluminescent jellyfish, deep water
    ("s4", "01"): "nautical/Flooded",   # drowned temple, coral, statues
    ("s4", "02"): "crystal",            # crystal cave with a running stream
    ("s4", "03"): "crystal",            # violet crystal and ley lines
    ("s4", "04"): "fungal",             # giant mushroom cavern
    ("s4", "05"): "nautical/Flooded",   # wreck beached inside a sea cave
    ("s4", "06"): "nautical/Deck",      # sea arch, heavy surf
    ("s4", "07"): "crystal",                # nebula and tumbling rock
    ("s4", "08"): "ice_dungeon",        # ice cave
    ("s4", "09"): "fire_dungeon",       # lava flow between black rock
    ("s4", "10"): "crystal",            # arcane sanctum, blue
    ("s4", "11"): "dark_dungeon",       # grey stalactite cave
    ("s4", "12"): "nautical/Flooded",   # green mossy cave, standing water
    ("s4", "13"): "fire_dungeon",       # lava flow, second take
    ("s4", "14"): "crystal",            # arcane sanctum, second take
    ("s4", "15"): "dark_dungeon",       # grey stalactite cave, second take

    # ---- sheet 5 -------------------------------------------------------------
    ("s5", "00"): "jungle",             # jungle interior
    ("s5", "01"): "nautical/Deck",      # ship anchored off a sand beach
    ("s5", "02"): "jungle",             # overgrown stepped temple
    ("s5", "03"): "dark_dungeon",       # troll crypt, glowing carvings
    ("s5", "04"): "jungle",             # waterfall shrine
    ("s5", "05"): "nautical/Deck",      # coastal fort at sunset

    # ---- sheet 6 -------------------------------------------------------------
    ("s6", "00"): "mossy_forest",       # autumn lakeshore, broken arches
    ("s6", "01"): "blighted",           # plague swamp, green and violet ooze
    ("s6", "03"): "jungle",             # deep jungle, ruins among the roots
    ("s6", "04"): "fire_dungeon",       # fel hall, green fire over lava
    ("s6", "05"): "blighted",           # corrupted wood, red tendrils
    ("s6", "07"): "crystal",            # arcane cavern, blue pool and ley lines
}

#: Near-duplicate takes of a panel already mapped above. Kyle: "remove redundancy to not take up
#: extra space."
#:
#: Chosen BY EYE, from the pairs rendered side by side, not by a similarity score. A 16x16
#: perceptual hash was tried first and could not do it: the two lava caves below scored 0.87
#: apart while genuinely different jungle paintings scored 0.41, so any global threshold either
#: kept duplicates or deleted distinct art. Two pairs the hash flagged (s2/10 vs s3/10, s1/10 vs
#: s5/00) turned out on inspection to be different paintings and are both kept.
DROPPED = {
    ("s3", "12"): "second take of s3/04, moonlit purple ruins",
    ("s3", "13"): "second take of s3/09, castle courtyard",
    ("s3", "14"): "second take of s3/10, jungle understorey",
    ("s3", "15"): "second take of s3/11, lava cave",
    ("s6", "02"): "second take of s6/01, plague swamp",
    ("s6", "06"): "second take of s6/05, corrupted wood",
}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) != 1:
        raise SystemExit("usage: install_background_panels.py STAGEDIR [--dry-run]")
    stage = Path(args[0])

    missing = [k for k in MAPPING if not (stage / k[0] / f"{k[1]}.png").exists()]
    if missing:
        raise SystemExit(f"REFUSING: {len(missing)} mapped panel(s) are not in {stage}: "
                         f"{missing[:6]}")
    # The other direction matters just as much: a panel nobody mapped is a painting that was
    # sliced, paid for and then silently thrown away.
    on_disk = {(d.name, p.stem) for d in stage.iterdir() if d.is_dir()
               for p in d.glob("[0-9][0-9].png")}
    unmapped = sorted(on_disk - set(MAPPING) - set(DROPPED))
    if unmapped:
        raise SystemExit(f"REFUSING: {len(unmapped)} sliced panel(s) are neither mapped nor "
                         f"explicitly dropped: {unmapped}")
    overlap = sorted(set(MAPPING) & set(DROPPED))
    if overlap:
        raise SystemExit(f"REFUSING: {overlap} are both mapped and dropped")

    tally = Counter()
    for (sheet, panel), dest in sorted(MAPPING.items()):
        out = DEST / dest
        tally[dest] += 1
        target = out / f"{sheet}_{panel}.png"
        if not dry:
            out.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stage / sheet / f"{panel}.png", target)
    for dest, n in sorted(tally.items()):
        print(f"  {'would write' if dry else 'wrote'} {n:2d} -> assets/backgrounds/{dest}/")
    print(f"\n{sum(tally.values())} panels across {len(tally)} destinations"
          f"{' (dry run)' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
