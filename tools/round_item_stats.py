#!/usr/bin/env python3
"""Item stats are whole numbers where they are counts, one decimal where percentages.

    PYTHONPATH=. python3 tools/round_item_stats.py [--apply]

Kyle, 6 Nov, with a screenshot of Signet of the Withered Grove reading
"+7.68 Healing Power / +1.62 Mp5": "also need to fix up number rounding."

IT IS NOT THE GENERATOR. entities/loot_generator.py already rounds - whole
numbers for primary stats, one decimal for the rest - and 400 generated
items came back clean. The values are authored that way in the loot files:
1,096 of 3,644 stat values across 38 of the 39 files carry more than one
decimal, because whatever produced them wrote raw budget arithmetic
straight out.

THE RULE, which is the distinction the old code was missing:

  COUNTS ARE WHOLE. Healing power, spell power, attack power, mp5, armour,
  stamina, resistances - these are points. "+7.68 Healing Power" is not
  precision, it is arithmetic that escaped. Nobody has 0.68 of a point.

  PERCENTAGES KEEP ONE DECIMAL. Crit chance, dodge, parry, block, haste,
  hit and the other rating stats stay at 0.1, because loot_generator's own
  comment is right about why: a low-level item is SUPPOSED to roll
  "+0.3% Block Rating", and whole numbers would zero out nearly every
  early-game secondary roll.

A count that rounds to 0 is dropped rather than left as a stat line
reading "+0", which is worse than not being there.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Point values. A character has 8 Healing Power, never 7.68.
WHOLE = {
    "healing_power", "spell_power", "attack_power", "ranged_attack_power",
    "mp5", "hp5", "armor", "block_value", "stamina", "strength", "agility",
    "intellect", "spirit", "max_health", "max_mana", "spell_penetration",
    "fire_resistance", "frost_resistance", "nature_resistance",
    "shadow_resistance", "arcane_resistance", "holy_resistance",
    "magic_resistance", "all_resistance",
}
#: <school>_spell_power is a point value too, same as plain spell_power.
WHOLE |= {f"{school}_spell_power" for school in
          ("fire", "frost", "nature", "shadow", "arcane", "holy")}


def fix(value, stat):
    if not isinstance(value, (int, float)):
        return value, False
    if stat in WHOLE:
        new = int(round(value))
        # A count the author put on the item deliberately should not vanish
        # because it rounds below a half. "+1 Mp5" is the smallest honest
        # version of "+0.4 Mp5"; dropping it changes what the item is.
        if new == 0 and value > 0:
            new = 1
    else:
        new = round(float(value), 1)
        if new == int(new):
            new = int(new)
    return new, new != value


def walk(node, counts, dropped, floored):
    """Round every stat map in place; report what changed."""
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key in ("primary_stats", "secondary_stats") and isinstance(value, dict):
                for stat, raw in list(value.items()):
                    new, changed = fix(raw, stat)
                    if changed:
                        counts[stat] += 1
                    if new == 0:
                        del value[stat]
                        dropped.append((node.get("name"), stat, raw))
                    else:
                        if stat in WHOLE and raw > 0 and int(round(raw)) == 0:
                            floored.append((node.get("name"), stat, raw))
                        value[stat] = new
            else:
                walk(value, counts, dropped, floored)
    elif isinstance(node, list):
        for item in node:
            walk(item, counts, dropped, floored)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    counts, dropped, floored, touched = Counter(), [], [], 0
    for path in sorted((ROOT / "data/loot").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        before = json.dumps(doc, sort_keys=True)
        walk(doc, counts, dropped, floored)
        after = json.dumps(doc, sort_keys=True)
        if before != after:
            touched += 1
            if args.apply:
                path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{sum(counts.values())} values rounded across {touched} files\n")
    print(f"{'stat':28}{'fixed':>7}")
    for stat, n in counts.most_common(18):
        kind = "whole" if stat in WHOLE else "1dp"
        print(f"  {stat:26}{n:>7}  ({kind})")
    if floored:
        print(f"\n{len(floored)} point values rounded below a half and were "
              f"floored to 1 rather than dropped:")
        for name, stat, raw in floored[:10]:
            print(f"  {str(name)[:34]:36}{stat:22}{raw} -> 1")
    if dropped:
        print(f"\n{len(dropped)} rounded to zero and were dropped rather than "
              f"left reading '+0':")
        for name, stat, raw in dropped[:10]:
            print(f"  {str(name)[:34]:36}{stat:22}{raw}")
    if not args.apply:
        print("\n(report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
