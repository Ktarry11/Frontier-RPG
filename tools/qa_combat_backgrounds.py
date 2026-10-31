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
from world.combat_backgrounds import (BIOME_TO_BACKGROUND, get_background_folder,  # noqa: E402
                                      ZONE_BACKGROUND, get_background_for_place)
from ui.combat_background_loader import get_background_for_zone, _resolve_folder_path, _list_images  # noqa: E402


def places():
    """-> ([zones that fight], [caves that fight], [places with nothing to fight]).

    Kyle: "Backgrounds are not important for places that don't have mobs." A backdrop is only
    ever seen behind a fight, so a town with no encounter table cannot show one and must not
    count against a pack's coverage - counting Orgrimmar and Ratchet as "places needing desert
    art" overstated how thin that pack really is.

    The empty ones are returned rather than dropped, because "this place has no creatures" is
    worth looking at on its own: it is right for a capital and wrong for a dungeon.
    """
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    zones, caves, empty = [], [], []
    for zn, z in enc.items():
        # z["open_zone"]["creatures"], NOT z["creatures"]. The first version read the latter,
        # which does not exist, so EVERY zone came back empty and the tool confidently reported
        # populated zones - the Frostward Descent among them - as having nothing to fight. It
        # was believed, and acted on. A key that is simply absent reads as "no creatures here"
        # and nothing anywhere says otherwise, which is why the assertion below exists.
        pools = [(z.get("open_zone") or {}).get("creatures") or {}]
        pools += [(s.get("creatures") or {}) for s in (z.get("subzones") or {}).values()]
        (zones if any(pools) else empty).append(zn)
    for z in enc.values():
        for cn, cv in (z.get("caves") or {}).items():
            name = cv.get("name") or cn
            (caves if (cv.get("creatures") or {}) else empty).append(name)
    # A schema typo here reports healthy zones as empty and empty ones as healthy, and nothing
    # downstream can tell. So: the game ships far more populated zones than empty ones, and if
    # that ever inverts it is this function that is wrong, not the content.
    if len(empty) > len(zones):
        raise SystemExit(f"REFUSING: {len(empty)} places look empty against only {len(zones)} "
                         f"populated - that is a key name that no longer matches "
                         f"encounters.json, not a game with no monsters in it.")
    return sorted(zones), sorted(set(caves)), sorted(set(empty))


def main():
    bad = []
    zones, caves, empty = places()

    # ---- 1 & 2. the backdrop was CHOSEN for this place, one way or the other
    #
    # Two ways to choose one: a biome entry (which also drives the zone's floor and wall
    # textures) or a ZONE_BACKGROUND override (which drives only the backdrop). The override
    # exists because filling in the biome tables to fix 43 backdrops would have repainted 43
    # hand-built zones. Either counts; neither means the default is showing.
    for name in zones:
        if name not in ZONE_BIOME and name not in ZONE_BACKGROUND:
            bad.append(f"zone {name!r} has neither a biome nor a background override - it "
                       f"silently gets DEFAULT_BIOME ({DEFAULT_BIOME!r}) and whatever backdrop "
                       f"that maps to")
    for name in caves:
        if name not in CAVE_BIOME and name not in ZONE_BACKGROUND:
            bad.append(f"cave/dungeon {name!r} has neither a CAVE_BIOME entry nor a background "
                       f"override - it falls through to the OVERWORLD table and fights under an "
                       f"outdoor sky")

    # ---- 3. the biomes actually reached have art
    reached = defaultdict(list)
    for name in zones:
        reached[get_biome_for_zone(name, is_cave=False)].append(name)
    for name in caves:
        reached[get_biome_for_zone(name, is_cave=True)].append(name)

    for biome, users in sorted(reached.items()):
        users = [u for u in users if u not in ZONE_BACKGROUND]
        if not users:
            continue        # every place on this biome is overridden; the biome is not in play
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
          f"{len(zones) + len(caves)} places a fight can start "
          f"({len(empty)} more have no encounter table and never show a backdrop)")
    print(f"  {len(reached)} biomes in use -> {len(folders)} background packs: {folders}")
    # Counted through the SAME resolution the game uses, overrides included. Counting it off the
    # biome alone reported 43 places in mossy_forest after the overrides had moved most of them
    # elsewhere - a summary that disagrees with the code it is summarising.
    spread = Counter()
    for name, is_cave in [(z, False) for z in zones] + [(c, True) for c in caves]:
        folder, pinned = get_background_for_place(name, get_biome_for_zone(name, is_cave))
        spread[f"{folder}/{pinned}" if pinned else folder] += 1
    print(f"  places per pack: {dict(spread.most_common())}")
    # Not a failure - every place has art and loads. But a pack with two images serving eleven
    # places means a lot of players see the same backdrop, and that is invisible from a passing
    # check that only asks "is there a file".
    thin = []
    for dest, places_n in spread.items():
        imgs = len(_list_images(_resolve_folder_path(*(dest.split("/") + [None])[:2])))
        if imgs and places_n / imgs >= 3:
            thin.append(f"{dest} ({imgs} image(s) for {places_n} places)")
    if thin:
        print(f"  thin packs, worth topping up: {', '.join(sorted(thin))}")

    # Printed, not asserted. A capital or an inn town having no encounter table is correct; a
    # built zone or a dungeon having none is a content hole wearing the same clothes, and only a
    # human can tell which is which from a list.
    if empty:
        print(f"  no encounter table (so no backdrop is ever shown): {empty}")

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
