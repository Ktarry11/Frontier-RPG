#!/usr/bin/env python3
"""A chest gives the same thing every time you reload the save in front of it.

    PYTHONPATH=. python3 tools/qa_chest_no_scum.py

Kyle's friend, 15 Nov 2026: "If you save it right before opening a special areas chest you can get
something different every time you load the save." Every roll used the global random at the moment
of opening. world/chest_manager.py now seeds each roll on the save's seed, the chest, and how many
times it's been opened.

  1. A regular chest, a boss chest and a hidden cache each open to the same item on every reload.
  2. A chest that respawns rolls something new (it isn't the same chest forever).
  3. A save from before seeds is stable too.
  4. Two different saves don't open every chest to the same thing.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TM:
    def __init__(self, name):
        self.name = name

    def set_tile(self, *a):
        pass


def desc(it):
    if it is None:
        return None
    return (it.name, it.rarity, it.item_level,
            json.dumps({**it.primary_stats, **it.secondary_stats}, sort_keys=True))


def main():
    from world.chest_manager import ChestManager
    from world.secrets import get_secrets
    bad = []
    cache = next(iter(get_secrets()._caches))

    def open_at(c, where, boss):
        zone, x, y = where
        return c.open_secret_cache(TM(zone), x, y, 55) if boss is None else \
            c.open_chest(TM(zone), x, y, 55, is_boss_chest=boss)

    for label, where, boss in (("a boss chest", ("Durotar", 51, 61), True),
                               ("a hidden cache", cache, None),
                               ("a regular chest", ("Ashenvale East", 80, 90), False)):
        save = json.loads(json.dumps(ChestManager().to_dict()))
        seen = set()
        for _ in range(5):
            c = ChestManager()
            c.load_dict(save)
            seen.add(desc(open_at(c, where, boss)))
        if len(seen) != 1:
            bad.append(f"{label} opened to {len(seen)} different things over five reloads")
        else:
            print(f"  {label}: the same on five reloads")

    c = ChestManager()
    a = desc(c.open_chest(TM("Durotar"), 52, 62, 55, True))
    c._looted.clear()
    b = desc(c.open_chest(TM("Durotar"), 52, 62, 55, True))
    if a == b:
        bad.append("a respawned chest gave exactly the same item again")

    old = {"looted": [["Durotar", 1, 1]], "wait": []}
    seen = set()
    for _ in range(3):
        c = ChestManager()
        c.load_dict(old)
        seen.add(desc(c.open_chest(TM("Durotar"), 53, 63, 55, True)))
    if len(seen) != 1:
        bad.append("a save from before seeds still re-rolls on reload")

    diffs = 0
    for i in range(6):
        c1, c2 = ChestManager(), ChestManager()
        c1.load_dict(json.loads(json.dumps(ChestManager().to_dict())))
        c2.load_dict(json.loads(json.dumps(ChestManager().to_dict())))
        diffs += desc(c1.open_chest(TM("Durotar"), 60 + i, 70, 55, True)) != \
            desc(c2.open_chest(TM("Durotar"), 60 + i, 70, 55, True))
    if diffs == 0:
        bad.append("two different saves open every chest to the same thing")

    if bad:
        print("\nFAILED:")
        for x in bad:
            print("  -", x)
        return 1
    print("chests OK - no save-scumming: a reload opens to the same thing, a respawn rolls again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
