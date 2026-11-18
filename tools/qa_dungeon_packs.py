#!/usr/bin/env python3
"""Every fixed-spawn dungeon's trash comes in packs, never as lone fights.

    PYTHONPATH=. python3 tools/qa_dungeon_packs.py

Kyle, 23 Oct 2026: dungeons are run by full parties, so trash comes in packs. Kyle, 14 Nov: "in dungeons enemies are
in packs of 4 to 5...not individual!" Kyle, 17 Nov, when the sizes were settled by level: "we keep them 3-4 below
30", and of this check: "Add this QA, yes."

A dungeon gets its packs one of two ways: the older ones from data/dungeons/trash_packs.json (tools/build_dungeon_pulls.py,
attached by world/dungeon_packs.apply_packs), the hand-built ones from their own builder (world/dungeon_packs.pad_packs).
Either way the game reads zone.trash_packs. A dungeon that only has a flat zone.trash_spawns list spawns every mob as
its own fight, which is the bug this check exists to stop. For every dungeon map with fixed spawns and any trash:
  * it has trash_packs, and every trash mob it has is in one;
  * no pack is smaller than its band allows: 3 below level 30 and 4 from 30 up, with one pack per dungeon allowed one
    short (a nook only has room for so many).
Hidden maps are counted, never named.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from tools.build_fast_exits import load_world
    from world.dungeon_packs import ALSO_DUNGEONS, BIG_PACKS_FROM
    from world.hidden_zones import registry
    from world.zone_classification import is_dungeon
    tiles = load_world()
    reg = registry()
    levels = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))
    levels = levels.get("zones") or levels

    def label(n):
        return "a hidden map" if n in reg else n

    checked, bad, hidden_bad = 0, [], 0
    for n, t in sorted(tiles.items()):
        if not (is_dungeon(n) or n in ALSO_DUNGEONS):
            continue
        if not getattr(t, "fixed_spawns", True):
            continue
        flat = list(getattr(t, "trash_spawns", None) or [])
        packs = list(getattr(t, "trash_packs", None) or [])
        if not flat and not packs:
            continue
        checked += 1
        band = levels.get(n)
        smallest = 4 if band and band[0] >= BIG_PACKS_FROM else 3
        problems = []
        if not packs:
            problems.append(f"{len(flat)} trash mobs and no packs: every one is a lone fight")
        else:
            in_packs = {(m[0], m[1]) for p in packs for m in p}
            loose = [m for m in flat if (m[0], m[1]) not in in_packs]
            if loose:
                problems.append(f"{len(loose)} trash mobs outside any pack")
            short = sorted(len(p) for p in packs if len(p) < smallest)
            if len(short) > 1 or (short and short[0] < smallest - 1):
                problems.append(f"packs under {smallest}: sizes {short}")
        if problems:
            if n in reg:
                hidden_bad += 1
            bad.append(f"{label(n)}: " + "; ".join(problems))

    print(f"{checked} fixed-spawn dungeon maps with trash checked")
    if bad:
        print("FAILED:")
        for b in bad:
            print("  " + b)
        if hidden_bad:
            print(f"  ({hidden_bad} of these are hidden maps, not named)")
        return 1
    print("OK: every one fights in packs of its band's size")
    return 0


if __name__ == "__main__":
    sys.exit(main())
