#!/usr/bin/env python3
"""Is there hand-authored gear for every class, at every level band?

    PYTHONPATH=. python3 tools/audit_class_gear_coverage.py [--class Warrior] [--band 31-40]

Kyle, 29 Oct 2026: "i want gear to be unique, diverse, and have something for every class/spec but
i also love balance. i want any class to be viable"

Budget (tools/audit_item_budgets.py) answers "is this item the right SIZE". This answers the other
half: is anything here FOR YOU. An item can be perfectly on curve and still leave a class with
nothing to wear, and that failure is invisible to a budget check - a zone can be 100% on-curve and
hand a Venomancer not one usable piece.

WHAT COUNTS AS GEAR FOR A CLASS. Two data files already decide it:
  data/items/armor_types.json     class_armor_map        Warrior -> plate, Priest -> cloth
  data/items/stat_templates.json  class_stat_template_map Warrior -> str_physical

A class's stat template names the stats it actually wants - str_physical is 70% strength and 30%
stamina. So an armour piece serves a class when its armour type matches AND it carries that class's
lead stat. A weapon serves a class when its type is in that class's class_weapon_map list and it
carries the lead stat, or it is a pure stat-stick type (wand, totem, libram, idol, tome) that class
can hold.

Frontier has THIRTY classes over twelve (armour, template) niches, which is why this needs checking
rather than eyeballing: eleven classes are int_caster and three are str_physical, so a table full of
strength plate serves three classes and a table full of intellect cloth serves eight. "One item per
armour type" is NOT even coverage.

A niche is reported as thin when a level band holds fewer than THIN items for it. Below that a
player levelling through the band sees nothing for their class in that content and the levelling
curve stops working for them, however well budgeted everything is.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
_aib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_aib)

ARMOR_MAP = json.loads((ROOT / "data/items/armor_types.json").read_text())["class_armor_map"]
TEMPLATES = json.loads((ROOT / "data/items/stat_templates.json").read_text())
TEMPLATE_MAP = TEMPLATES["class_stat_template_map"]
TEMPLATE_STATS = TEMPLATES["stat_templates"]
WEAPON_MAP = json.loads((ROOT / "data/items/weapon_types.json").read_text()).get("class_weapon_map", {})

BANDS = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60)]

#: Fewer than this many items for a niche in a band is thin. Three is one per roughly three levels
#: of a ten-level band, which is sparse but survivable; below that the band has effectively nothing.
THIN = 3

#: Off-hand and relic types that are stat sticks rather than damage weapons - a class that can hold
#: one is served by it whatever its lead stat, because it has no competing alternative.
STAT_STICKS = {"wand", "totem", "libram", "idol", "tome", "shield"}


def lead_stats(template):
    """The stats a class with this template actually wants, best first."""
    stats = TEMPLATE_STATS[template]["primary_stats"]
    return [s for s, _w in sorted(stats.items(), key=lambda kv: -kv[1])]


def serves(item, armor_type, template):
    """Does this item serve a class wearing `armor_type` with `template`?"""
    primary = item.get("primary_stats") or {}
    wants = lead_stats(template)
    lead = wants[0]
    wtype = item.get("weapon_type")
    if wtype:
        return None  # weapons handled separately, they need the class name
    if item.get("slot") in ("neck", "ring", "trinket", "back"):
        # Accessories have no armour type, so they serve on stats alone.
        return lead in primary
    if item.get("armor_type") != armor_type:
        return False
    return lead in primary


def main():
    only_class = None
    if "--class" in sys.argv:
        only_class = sys.argv[sys.argv.index("--class") + 1]
    only_band = None
    if "--band" in sys.argv:
        lo, hi = sys.argv[sys.argv.index("--band") + 1].split("-")
        only_band = (int(lo), int(hi))

    rows = [i for _s, _o, i in _aib.collect() if i.get("item_level")]

    # (band, armour, template) -> count of armour/accessory items serving it
    niche = defaultdict(int)
    # (band, class) -> count of usable weapons
    weapons = defaultdict(int)

    for item in rows:
        band = next((b for b in BANDS if b[0] <= item["item_level"] <= b[1]), None)
        if band is None:
            continue
        wtype = item.get("weapon_type")
        if wtype:
            primary = item.get("primary_stats") or {}
            for cls, allowed in WEAPON_MAP.items():
                if wtype not in allowed:
                    continue
                if wtype in STAT_STICKS or lead_stats(TEMPLATE_MAP.get(cls, "str_physical"))[0] in primary:
                    weapons[(band, cls)] += 1
            continue
        for cls in TEMPLATE_MAP:
            if cls not in ARMOR_MAP:
                continue
            if serves(item, ARMOR_MAP[cls], TEMPLATE_MAP[cls]):
                niche[(band, ARMOR_MAP[cls], TEMPLATE_MAP[cls])] += 1

    classes = sorted(c for c in TEMPLATE_MAP if c in ARMOR_MAP)
    if only_class:
        classes = [c for c in classes if c.lower() == only_class.lower()]
        if not classes:
            raise SystemExit(f"unknown class {only_class!r}")

    findings = []
    bands = [only_band] if only_band else BANDS
    hdr = "".join(f"{lo}-{hi:<7}" for lo, hi in bands)
    print(f"{'class':20}{'armour':9}{'template':17}{hdr}")
    print(f"{'':20}{'':9}{'':17}" + "".join("arm/wpn  " for _ in bands))
    for cls in classes:
        armor, template = ARMOR_MAP[cls], TEMPLATE_MAP[cls]
        cells = []
        for band in bands:
            a = niche[(band, armor, template)]
            w = weapons[(band, cls)]
            cells.append(f"{a:>3}/{w:<4}")
            if a < THIN:
                findings.append(f"{cls} ({armor}/{template}) has {a} armour piece(s) in ilvl {band[0]}-{band[1]}")
            if w < THIN:
                findings.append(f"{cls} has {w} usable weapon(s) in ilvl {band[0]}-{band[1]}")
        print(f"  {cls:18}{armor:9}{template:17}" + "".join(cells))

    # Niche totals, which is where the 30-classes-12-niches imbalance shows
    print("\nitems per (armour, template) niche, all levels, with how many classes share it:")
    share = defaultdict(list)
    for cls in TEMPLATE_MAP:
        if cls in ARMOR_MAP:
            share[(ARMOR_MAP[cls], TEMPLATE_MAP[cls])].append(cls)
    for key, clss in sorted(share.items(), key=lambda kv: -len(kv[1])):
        total = sum(niche[(b, key[0], key[1])] for b in BANDS)
        per = total / len(clss)
        print(f"   {key[0]:8} {key[1]:17} {total:5} items / {len(clss):2} class(es) = {per:6.1f} each")

    print()
    if findings:
        seen = []
        for f in findings:
            if f not in seen:
                seen.append(f)
        print(f"{len(seen)} finding(s):")
        for f in seen[:40]:
            print(f"  {f}")
        if len(seen) > 40:
            print(f"  ... and {len(seen) - 40} more")
        return 1
    print(f"every class has at least {THIN} armour pieces and {THIN} weapons in every level band")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
