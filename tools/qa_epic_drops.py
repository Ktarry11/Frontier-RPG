#!/usr/bin/env python3
"""Epics exist, are rare, are varied, and never show up before level 30.

    PYTHONPATH=. python3 tools/qa_epic_drops.py

Kyle, 2026-10-28: "occasional drops as epic after lvl 30 in Dungeons and also for world drop after
lvl 30."

This rolls the real dice rather than reading the config, for the same reason tools/qa_tier_floor.py
does: the config said epic was gated at level 30 and enabled, and there was still not one epic drop
in the game, because hand-authored boss pools never reach the rarity roller at all.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.epic_drops import BOSS_CHANCE, MIN_LEVEL, WORLD_CHANCE, roll_epic  # noqa: E402

#: Acceptable per-kill bounds. A world epic should be the drop somebody mentions; a boss epic
#: should be a real reason to go in without being the expected outcome.
WORLD_BOUNDS = (0.0005, 0.01)
BOSS_BOUNDS = (0.02, 0.15)


class _Dummy:
    def __init__(self, level, boss=False):
        self.level, self.is_boss, self.name = level, boss, "test subject"


def main():
    random.seed(0)
    fails = []
    data = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    world, dungeon = data.get("world", []), data.get("dungeon", [])

    if not world or not dungeon:
        print("FAIL - data/loot/epic_drops.json is missing a pool")
        return 1

    # ---- nothing below the gate, either path
    for level in range(1, MIN_LEVEL):
        for boss in (False, True):
            for _ in range(4000):
                if roll_epic(_Dummy(level, boss), level) is not None:
                    fails.append(f"an epic dropped at level {level} (boss={boss})")
                    break

    # ---- and they do drop above it, at a sane rate
    for label, boss, bounds in (("world", False, WORLD_BOUNDS), ("boss", True, BOSS_BOUNDS)):
        n = 200000 if not boss else 20000
        hits = sum(1 for _ in range(n) if roll_epic(_Dummy(38, boss), 38) is not None)
        rate = hits / n
        if not bounds[0] <= rate <= bounds[1]:
            fails.append(f"{label} epic rate is {rate:.4%}, outside the intended "
                         f"{bounds[0]:.2%}-{bounds[1]:.2%}")
        print(f"  {label:<6} {rate:.4%} per kill  (1 in {int(1 / rate) if rate else 0})")

    # ---- every entry has to rebuild into a real Item, and be epic
    from entities.item import Item
    for bucket, rows in (("world", world), ("dungeon", dungeon)):
        for d in rows:
            try:
                it = Item.from_dict(dict(d))
            except Exception as exc:                       # noqa: BLE001
                fails.append(f"{bucket}/{d.get('name')} will not rebuild: {exc}")
                continue
            if it.rarity != "epic":
                fails.append(f"{bucket}/{it.name} is {it.rarity}, not epic")
            if not getattr(it, "flavor_text", ""):
                fails.append(f"{bucket}/{it.name} has no flavour text")

    # ---- Kyle's standing rule on loot spread
    rows = world + dungeon
    armour = Counter(d.get("armor_type") for d in rows if d.get("armor_type"))
    weapons = Counter(d.get("weapon_type") for d in rows if d.get("weapon_type"))
    for cls in ("cloth", "leather", "mail", "plate"):
        if armour[cls] < 2:
            fails.append(f"only {armour[cls]} {cls} epics - the spread is lopsided")
    if weapons and max(weapons.values()) > 3:
        hog = max(weapons, key=weapons.get)
        fails.append(f"{weapons[hog]} of the epic weapons are {hog}")

    # ---- the procedural roller must not outshine the named ones
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    proc = sum(1 for _ in range(40000) if gen.roll_rarity(38) == "epic") / 40000 * 0.35
    print(f"  procedural epics, same level: {proc:.4%} per kill")
    if proc > WORLD_CHANCE * 4:
        fails.append(f"procedural epics ({proc:.4%}) swamp the named world drops "
                     f"({WORLD_CHANCE:.4%}) - lower rarity.json's epic drop_weight")

    print(f"\n== {len(world)} world epics, {len(dungeon)} dungeon epics; "
          f"armour {dict(armour)}")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS - epics are gated at 30, rare, varied, and rebuild correctly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
