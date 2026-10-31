#!/usr/bin/env python3
"""Move every authored item onto a new slot budget, keeping where it already sits on the curve.

    PYTHONPATH=. python3 tools/rescale_item_stats.py --dry-run
    PYTHONPATH=. python3 tools/rescale_item_stats.py

Kyle, 2026-10-31, on the fitted curve: "I think we should bump this up roughly. It's too much
of a difference." The gap between the best and worst slot was 6.2x (two-handers 1.232 against a
ring 0.198); the new numbers put it at 3.1x.

WHY THIS IS A MULTIPLY AND NOT A REWRITE. The budget curve is

    value = ( SUM (amount * mod) ** 1.5 ) ** (2/3)

so multiplying every amount on an item by f multiplies each term by f**1.5, the sum by f**1.5,
and the result by exactly f. Budget is LINEAR in a uniform stat multiply. An item at 118% of
its old budget is still at 118% of the new one, so this changes how much gear is worth without
touching the relative quality of any two items, and the 375 items that were off-curve stay
exactly as off-curve as they were - this is a rescale, not a cleanup, and conflating the two
would hide which items were authored wrong.

WHAT IS DELIBERATELY NOT SCALED. weapon_damage_min/max, attack_speed and armor_value are not
stats off the budget - damage is the weapon's own line and armour value is derived from item
level - so touching them here would change two things at once and make the balance sim
unreadable.

Integer stats stay integers. Rounding a 1 up to a 2 is a 100% jump on that stat, so small
values are the one place this is lumpy; the alternative is fractional Strength.
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from entities.item_budget import RARITY_MULT, SLOT_K, slot_key  # noqa: E402

#: The curve as it was FITTED from the game's own items, before Kyle's bump. Each item is
#: multiplied by target/old for its slot, which is why this has to be written down rather than
#: read from item_budget.py - that file now holds the target.
OLD_SLOT_K = {
    "2H": 1.232,
    "chest": 0.476, "legs": 0.473,
    "shoulder": 0.372, "head": 0.370,
    "main_hand_weapon": 0.324, "off_hand_weapon": 0.290,
    "wrist": 0.254, "feet": 0.251, "shield": 0.240, "waist": 0.237, "hands": 0.233,
    "neck": 0.198, "ring": 0.198, "trinket": 0.193, "back": 0.192,
    "ranged_weapon": 0.172,
}

#: Fields that are NOT budget stats and must not move. See the module docstring.
UNTOUCHED = ("weapon_damage_min", "weapon_damage_max", "attack_speed", "armor_value")

DIRS = ["data/loot", "data/items", "data/quests", "data/crafting", "data/leatherworking",
        "data/blacksmithing"]


def factor(item):
    k = slot_key(item)
    old, new = OLD_SLOT_K.get(k), SLOT_K.get(k)
    if not old or not new or abs(new - old) < 1e-9:
        return None
    return new / old


def rescale(item, f):
    """Multiply every budget stat. Integers stay integers; a stat never rounds to nothing."""
    changed = False
    for group in ("primary_stats", "secondary_stats"):
        block = item.get(group)
        if not isinstance(block, dict):
            continue
        for stat, amount in list(block.items()):
            if not isinstance(amount, (int, float)) or amount <= 0:
                continue
            if isinstance(amount, int):
                block[stat] = max(1, round(amount * f))
            else:
                block[stat] = round(amount * f, 2)
            changed = changed or block[stat] != amount
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    touched = Counter()
    files = 0
    for d in DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for f in sorted(root.rglob("*.json")):
            try:
                text = f.read_text(encoding="utf-8")
                data = json.loads(text, object_pairs_hook=OrderedDict)
            except Exception:
                continue
            hits = 0
            stack = [data]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    if (o.get("item_level") and o.get("rarity") in RARITY_MULT
                            and (o.get("primary_stats") or o.get("secondary_stats"))):
                        fac = factor(o)
                        if fac and rescale(o, fac):
                            hits += 1
                            touched[slot_key(o)] += 1
                    stack.extend(o.values())
                elif isinstance(o, list):
                    stack.extend(o)
            if hits and not args.dry_run:
                f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            if hits:
                files += 1

    for k, n in sorted(touched.items(), key=lambda kv: -kv[1]):
        print(f"  {k:18s} {n:5d} items  x{SLOT_K[k] / OLD_SLOT_K[k]:.3f}")
    print(f"\n{sum(touched.values())} items across {files} files"
          f"{' (dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
