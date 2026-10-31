#!/usr/bin/env python3
"""Every place a fight can start has a background that was CHOSEN, not defaulted into.

    PYTHONPATH=. python3 tools/qa_combat_backgrounds.py

Kyle: "are we ensuring that each fight gets backgrounds? We have background art."

The loader is best-effort by design, and that is right - a missing file should cost a backdrop,
not the fight. But best-effort hides two stacked silent defaults:

    get_biome_for_zone(zone)    -> ZONE_BIOME.get(zone, DEFAULT_BIOME)
    get_background_folder(biome)-> BIOME_TO_BACKGROUND.get(biome, "mossy_forest")

so a zone nobody added to ZONE_BIOME does not fail, it quietly fights in a green forest. In a
desert. Forever. Nothing logs it and the screen looks finished, which is the expensive kind of
wrong: you only find it by walking into Tanaris and noticing the trees.

FOUR CLAIMS:

  1. EVERY OVERWORLD ZONE HAS AN EXPLICIT BIOME. Not a default that happens to look fine.
  2. EVERY CAVE AND DUNGEON HAS AN EXPLICIT BIOME. Caves are checked against CAVE_BIOME first,
     so a dungeon missing from that table falls through to the OVERWORLD table and inherits the
     outdoor biome of a zone it shares a name prefix with, or the global default.
  3. EVERY BIOME THAT IS ACTUALLY REACHED MAPS TO A REAL FOLDER WITH IMAGES IN IT. A folder in
     the table that nobody drew art for is a flat fill with extra steps.
  4. THE LOADER REALLY RETURNS A SURFACE for each of them. Claims 1-3 are table-reading; this
     one runs the thing the game runs, because the tables agreeing is not the same as the file
     loading.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

from world.tile_textures import ZONE_BIOME, CAVE_BIOME, DEFAULT_BIOME, get_biome_for_zone  # noqa: E402
from world.combat_backgrounds import BIOME_TO_BACKGROUND, get_background_folder  # noqa: E402
from ui.combat_background_loader import get_background_for_zone, _resolve_folder_path, _list_images  # noqa: E402


def places():
    """-> ([overworld zone names], [cave/dungeon names]) as the game actually ships them."""
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    zones = sorted(enc)
    caves = sorted({cv.get("name") or cn
                    for z in enc.values() for cn, cv in (z.get("caves") or {}).items()})
    return zones, caves


def main():
    bad = []
    zones, caves = places()

    # ---- 1 & 2. explicit biome, not a default
    for name in zones:
        if name not in ZONE_BIOME:
            bad.append(f"zone {name!r} is not in ZONE_BIOME - it silently gets DEFAULT_BIOME "
                       f"({DEFAULT_BIOME!r}) and whatever backdrop that maps to")
    for name in caves:
        if name not in CAVE_BIOME:
            bad.append(f"cave/dungeon {name!r} is not in CAVE_BIOME - it falls through to the "
                       f"OVERWORLD table and fights under an outdoor sky")

    # ---- 3. the biomes actually reached have art
    reached = defaultdict(list)
    for name in zones:
        reached[get_biome_for_zone(name, is_cave=False)].append(name)
    for name in caves:
        reached[get_biome_for_zone(name, is_cave=True)].append(name)

    for biome, users in sorted(reached.items()):
        if biome not in BIOME_TO_BACKGROUND:
            bad.append(f"biome {biome!r} ({len(users)} place(s), e.g. {users[0]!r}) is not in "
                       f"BIOME_TO_BACKGROUND - it defaults to mossy_forest")
            continue
        folder = get_background_folder(biome)
        if not _list_images(_resolve_folder_path(folder)):
            bad.append(f"biome {biome!r} -> folder {folder!r}, which holds no images; "
                       f"{len(users)} place(s) would fall back to the flat fill")

    # ---- 4. the loader really returns a Surface
    #
    # Table-reading above says the mapping is right. This says the file opens. They are not the
    # same claim: a folder can be listed, present, and full of something pygame cannot decode.
    blank = []
    for name, is_cave in [(z, False) for z in zones] + [(c, True) for c in caves]:
        try:
            surf = get_background_for_zone(name, is_cave=is_cave, size=(320, 180), reroll=True)
        except Exception as exc:
            bad.append(f"{name!r} raised loading its background: {exc!r}")
            continue
        if surf is None:
            blank.append(name)
    if blank:
        bad.append(f"{len(blank)} place(s) load NO background and fight on the flat fill: "
                   f"{blank[:10]}{' ...' if len(blank) > 10 else ''}")

    # ---- report
    folders = sorted({get_background_folder(b) for b in reached if b in BIOME_TO_BACKGROUND})
    print(f"{len(zones)} overworld zones + {len(caves)} caves/dungeons = "
          f"{len(zones) + len(caves)} places a fight can start")
    print(f"  {len(reached)} biomes in use -> {len(folders)} background packs: {folders}")
    spread = Counter()
    for biome, users in reached.items():
        spread[get_background_folder(biome) if biome in BIOME_TO_BACKGROUND else "DEFAULTED"] += len(users)
    print(f"  places per pack: {dict(spread.most_common())}")
    unused = sorted(set(BIOME_TO_BACKGROUND.values()) - set(folders))
    if unused:
        print(f"  packs no place currently uses: {unused}")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\ncombat backgrounds OK - every zone and dungeon has an explicitly chosen biome, "
          "every biome in use maps to a pack that has art, and every one of them really loads.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
