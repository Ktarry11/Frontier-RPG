#!/usr/bin/env python3
"""Does every reputation shelf, taken together, have something for every one of the 30 classes' specs?

    PYTHONPATH=. python3 tools/audit_rep_coverage.py [--detail]

Kyle, 17 Nov 2026: "Ensuring variation in all rep vendors? Includes ALL 30 classes and specs?" And on 15 Nov: "DONT
tunnel people ... Don't pigeon hole!!!". Every faction's shelf has a direction; between them they must cover the game.

What's counted: every rep item (data/items/faction_rewards.json, any faction, revered blues and exalted epics) and every
exalted rep recipe's crafted item. What serves a spec is tools/audit_class_gear_coverage.serves() for armour and
accessories (its armour type and its lead stat), and for weapons: the class can use the weapon type and it carries the
lead stat, or it's a stat stick (wand, totem, libram, idol, tome, shield) the class can hold.

Fails when a spec has nothing at all, or no epic (an exalted piece or an exalted recipe's) anywhere.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from audit_class_gear_coverage import SPEC_GEAR, SPEC_CLASS, WEAPON_MAP, STAT_STICKS, serves  # noqa: E402
from world.spec_gear_needs import wanted_stats  # noqa: E402


def rep_items():
    """[(source, item, is_epic)] for every rep item and rep recipe output."""
    out = []
    fr = json.loads((ROOT / "data/items/faction_rewards.json").read_text(encoding="utf-8"))["items"]
    for iid, it in fr.items():
        if it.get("faction"):
            out.append((f"{it['faction']}:{iid}", it, it.get("rarity") == "epic"))
    from world.recipe_manager import _load_all_recipes
    for rid, (trade, r) in _load_all_recipes().items():
        if r.get("faction") and (r.get("output") or {}).get("item"):
            it = r["output"]["item"]
            out.append((f"{r['faction']}:{rid} ({trade})", it, it.get("rarity") == "epic"))
    return out


def weapon_serves(item, spec):
    wt = item.get("weapon_type")
    cls = SPEC_CLASS[spec]
    allowed = set(WEAPON_MAP.get(cls, []))
    if wt not in allowed:
        return False
    if wt in STAT_STICKS:
        return True
    lead = wanted_stats(SPEC_GEAR[spec][1])[0]
    return lead in (item.get("primary_stats") or {})


def coverage():
    items = rep_items()
    got = defaultdict(list)
    for spec, (armour, template, _role, _why) in SPEC_GEAR.items():
        for src, it, epic in items:
            ok = weapon_serves(it, spec) if it.get("weapon_type") else serves(it, armour, template)
            if ok:
                got[spec].append((src, epic))
    return items, got


def main():
    items, got = coverage()
    bad = []
    by_class = defaultdict(list)
    for spec in SPEC_GEAR:
        n = len(got[spec])
        e = sum(1 for _s, ep in got[spec] if ep)
        by_class[SPEC_CLASS[spec]].append((spec, n, e))
        if n == 0:
            bad.append(f"{spec} ({SPEC_GEAR[spec][0]}/{SPEC_GEAR[spec][1]}): nothing on any rep shelf")
        elif e == 0:
            bad.append(f"{spec} ({SPEC_GEAR[spec][0]}/{SPEC_GEAR[spec][1]}): {n} blues, no epic anywhere")
    if "--detail" in sys.argv:
        for cls in sorted(by_class):
            print(cls)
            for spec, n, e in by_class[cls]:
                print(f"   {spec:34s} {n:3d} items, {e:2d} epic  ({SPEC_GEAR[spec][0]}/{SPEC_GEAR[spec][1]})")
    for b in bad:
        print("  FAIL", b)
    print(f"{len(items)} rep items and recipes, {len(SPEC_GEAR)} specs across {len(by_class)} classes: "
          f"{len(bad)} short")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
