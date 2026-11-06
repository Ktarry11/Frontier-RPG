#!/usr/bin/env python3
"""Re-level the loot-gap items to the pools they were dropped into.

    PYTHONPATH=. python3 tools/fix_gap_item_levels.py [--apply]

WHAT WENT WRONG. tools/build_loot_gap_items.py authored 64 items for the
five starved weapon types (Kyle: "fix loot balance. Throw in an item
throughout caves or Dungeons or quest rewards" - thrown 4 -> 21, tome 7 ->
32, fist_weapon 17 -> 32, libram 0 -> 5, idol 0 -> 2). It picked a FILE by
level band and then a boss inside it by index, but it set each item's
item_level from its own authored table and never from the boss the item
actually landed on. So 29 of them sit in a pool whose every other drop is
a different item level - an Aspen Snow-Dart at 30 among four items at 33,
a Codex Interminable at 43 among items at 40.

That is what the per-zone content checks were reporting as "item_level =
creature level + 3" violations, and they were right: a boss's drops should
look like they came off the same boss.

THE RULE IS THE POOL'S OWN, NOT A GLOBAL ONE, and that matters here. A
survey of every boss pool in the game finds 94 hand-authored items at
creature level + 2 and the Aspen and Underdark pools at + 3, so there is no
single offset to impose - and imposing one would re-level 94 items nobody
asked about. Each gap item is instead levelled to whatever its OWN
pool-mates use, which is both the smaller change and the more obviously
correct one.

Stats scale with the move, by the item-level ratio, so an item pushed from
30 to 33 does not stay priced for 30. Checked afterwards with
tools/audit_item_budgets.py.

A one-off repair for items already written, AND the same rule is now in
build_loot_gap_items.py so a future run places them correctly.
"""

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pool_level(items):
    """The item level this pool's own authored drops agree on, or None.

    Modal rather than mean: a pool is a hand-authored set that shares one
    level, so the mode IS the answer wherever there is one, and a pool with
    no agreement among its authored items is left alone rather than guessed
    at.
    """
    authored = [i.get("item_level") for i in items
                if "label" not in i and isinstance(i.get("item_level"), int)]
    if not authored:
        return None
    counts = Counter(authored)
    level, n = counts.most_common(1)[0]
    return level if n >= 2 or len(counts) == 1 else None


def rescale(item, old, new):
    """Move an item's numbers from item level `old` to `new`."""
    if not old or old == new:
        return
    r = new / old
    for group in ("primary_stats", "secondary_stats"):
        for k, v in list((item.get(group) or {}).items()):
            if isinstance(v, int):
                item[group][k] = max(1, round(v * r))
            elif isinstance(v, float):
                item[group][k] = round(v * r, 2)
    for k in ("weapon_damage_min", "weapon_damage_max", "armor_value",
              "block_value", "sell_price"):
        if isinstance(item.get(k), int) and item[k] > 0:
            item[k] = max(1, round(item[k] * r))
    if item.get("weapon_damage_max", 0) and \
            item["weapon_damage_max"] <= item.get("weapon_damage_min", 0):
        item["weapon_damage_max"] = item["weapon_damage_min"] + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    moved, skipped = [], []
    for path in sorted((ROOT / "data/loot").glob("*boss_loot*.json")):
        data = json.loads(path.read_text())
        pools = data.get("bosses") or {k: v for k, v in data.items()
                                       if isinstance(v, list)}
        touched = False
        for boss, items in pools.items():
            if not isinstance(items, list):
                continue
            want = pool_level(items)
            gaps = [i for i in items if "label" in i]
            if want is None:
                skipped += [(path.name, boss, i["name"]) for i in gaps]
                continue
            for i in gaps:
                old = i.get("item_level")
                if old == want:
                    continue
                rescale(i, old, want)
                i["item_level"] = want
                i["required_level"] = max(1, want - 3)
                moved.append((path.name, boss, i["name"], old, want))
                touched = True
        if touched and args.apply:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print(f"{len(moved)} gap item(s) re-levelled to their pool")
    for f, boss, name, old, new in moved:
        print(f"  {name:38} {old:>3} -> {new:<3}  {boss} ({f})")
    if skipped:
        print(f"\n{len(skipped)} left alone - their pool's own items do not "
              f"agree on a level:")
        for f, boss, name in skipped:
            print(f"  {name:38} {boss} ({f})")
    if not args.apply:
        print("\n(report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
