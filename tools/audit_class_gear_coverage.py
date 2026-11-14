#!/usr/bin/env python3
"""Is there gear for every SPEC, at every level band?

    PYTHONPATH=. python3 tools/audit_class_gear_coverage.py [--spec shaman_enhancement]
                                                            [--class Shaman] [--band 31-40]
                                                            [--thin 3]

Kyle, 29 Oct 2026: "i want gear to be unique, diverse, and have something for every class/spec but
i also love balance. i want any class to be viable" and then, on the first version of this file,
"we NEED to consider complex hybrid classes bro".

He was right and the first version was wrong in a way worth recording. It read
class_stat_template_map, which gives each of 30 classes ONE stat template, and then reported
coverage per class. That model cannot describe this game. An Enhancement Shaman came out as
"mail / int_caster, 455 items" when what it wants is mail agility, of which it had none - and every
one of those 455 items is perfectly on curve, so no budget audit could ever see the gap. The item
sizes were right and the item was simply not for them.

So this now reads world/spec_gear_needs.SPEC_GEAR: all 97 specs, each with the armour it wears and
the stat template it actually gears for, and a per-entry note saying whether that came from Kyle,
from a mechanical rule, or from a guess.

WHAT COUNTS AS GEAR FOR A SPEC
  armour      its type matches the spec's armour AND it carries the spec's lead stat
  accessory   no armour type, so it serves on the lead stat alone
  weapon      its type is in the CLASS's class_weapon_map AND it carries the spec's lead stat,
              or it is a stat stick (wand, totem, libram, idol, tome, shield) the class can hold

WHY THIS NEEDS CHECKING RATHER THAN EYEBALLING: the 97 specs crowd into 12 (armour, template)
niches, and they crowd unevenly - 24 specs want cloth/intellect while 2 want leather/strength. So
"one item per armour type" was never even coverage, and a boss table that looks varied can still
serve the same two dozen specs four times over.

A niche is THIN when a band holds fewer than --thin items for it (default 3). Below that, a player
levelling through that content sees nothing for their spec, however well budgeted it all is.
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

from world.spec_gear_needs import SPEC_GEAR, wanted_stats  # noqa: E402

ARMOR_MAP = json.loads((ROOT / "data/items/armor_types.json").read_text(encoding="utf-8"))["class_armor_map"]
WEAPON_MAP = json.loads((ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8")).get("class_weapon_map", {})

#: ilvl 51-60 is deliberately absent. There are 3,546 hand-authored items at ilvl 40 and below, 96
#: in 41-50, and ZERO above that - the game's content stops in the forties. Including the band made
#: every one of the 97 specs report "0 armour, 0 weapons" and buried the two findings that are real
#: under 194 that only say "this content does not exist yet". Pass --band 51-60 to look anyway.
BANDS = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]

#: Off-hands and relics that are stat sticks rather than damage weapons. A spec that can hold one is
#: served by it whatever its lead stat, because it has no competing alternative for that slot.
STAT_STICKS = {"wand", "totem", "libram", "idol", "tome", "shield"}


def spec_class(spec_id):
    """The class a spec belongs to - longest matching class prefix, so 'Knight of Xoroth' and
    'Witch Hunter' resolve before any shorter name can steal them."""
    best = None
    for cls in ARMOR_MAP:
        key = cls.lower().replace(" ", "_") + "_"
        if spec_id.startswith(key) and (best is None or len(key) > len(best[1])):
            best = (cls, key)
    return best[0] if best else None


SPEC_CLASS = {s: spec_class(s) for s in SPEC_GEAR}


def serves(item, armour, template):
    """Does this armour or accessory serve a spec wearing `armour` with `template`?"""
    if item.get("weapon_type"):
        return False
    primary = item.get("primary_stats") or {}
    lead = wanted_stats(template)[0]
    if item.get("slot") in ("neck", "ring", "trinket", "back"):
        return lead in primary
    if item.get("armor_type") != armour:
        return False
    return lead in primary


def main():
    thin = 3
    if "--thin" in sys.argv:
        thin = int(sys.argv[sys.argv.index("--thin") + 1])
    only_spec = sys.argv[sys.argv.index("--spec") + 1] if "--spec" in sys.argv else None
    only_class = sys.argv[sys.argv.index("--class") + 1] if "--class" in sys.argv else None
    bands = BANDS
    if "--band" in sys.argv:
        lo, hi = sys.argv[sys.argv.index("--band") + 1].split("-")
        bands = [(int(lo), int(hi))]

    rows = [i for _s, _o, i in _aib.collect() if i.get("item_level")]

    niche = defaultdict(int)       # (band, armour, template) -> armour/accessory count
    weapons = defaultdict(int)     # (band, spec_id) -> usable weapon count

    for item in rows:
        band = next((b for b in BANDS if b[0] <= item["item_level"] <= b[1]), None)
        if band is None:
            continue
        wtype = item.get("weapon_type")
        if wtype:
            primary = item.get("primary_stats") or {}
            for spec_id, (_armour, template, _role, _why) in SPEC_GEAR.items():
                cls = SPEC_CLASS.get(spec_id)
                if cls is None or wtype not in WEAPON_MAP.get(cls, []):
                    continue
                if wtype in STAT_STICKS or wanted_stats(template)[0] in primary:
                    weapons[(band, spec_id)] += 1
            continue
        seen_niches = set()
        for _spec_id, (armour, template, _role, _why) in SPEC_GEAR.items():
            if (armour, template) in seen_niches:
                continue
            seen_niches.add((armour, template))
            if serves(item, armour, template):
                niche[(band, armour, template)] += 1

    specs = sorted(SPEC_GEAR)
    if only_spec:
        specs = [s for s in specs if s == only_spec]
        if not specs:
            raise SystemExit(f"unknown spec {only_spec!r}")
    if only_class:
        specs = [s for s in specs if (SPEC_CLASS.get(s) or "").lower() == only_class.lower()]
        if not specs:
            raise SystemExit(f"no specs for class {only_class!r}")

    findings = []
    hdr = "".join(f"{lo}-{hi:<6}" for lo, hi in bands)
    print(f"{'spec':32}{'armour':9}{'template':16}{hdr}")
    print(f"{'':32}{'':9}{'':16}" + "".join("arm/wpn " for _ in bands))
    for spec_id in specs:
        armour, template, _role, _why = SPEC_GEAR[spec_id]
        cells = []
        for band in bands:
            a = niche[(band, armour, template)]
            w = weapons[(band, spec_id)]
            cells.append(f"{a:>3}/{w:<4}")
            if a < thin:
                findings.append(f"{spec_id} ({armour}/{template}) has {a} armour piece(s) at ilvl {band[0]}-{band[1]}")
            if w < thin:
                findings.append(f"{spec_id} has {w} usable weapon(s) at ilvl {band[0]}-{band[1]}")
        print(f"  {spec_id:30}{armour:9}{template:16}" + "".join(cells))

    print("\nitems per niche, all levels, against how many specs compete for it:")
    share = defaultdict(list)
    for spec_id, (armour, template, _r, _w) in SPEC_GEAR.items():
        share[(armour, template)].append(spec_id)
    for key, members in sorted(share.items(), key=lambda kv: -len(kv[1])):
        total = sum(niche[(b, key[0], key[1])] for b in BANDS)
        print(f"   {key[0]:8} {key[1]:16} {total:5} items / {len(members):2} spec(s) = {total / len(members):7.1f} each")

    print()
    if findings:
        uniq = list(dict.fromkeys(findings))
        print(f"{len(uniq)} finding(s):")
        for f in uniq[:40]:
            print(f"  {f}")
        if len(uniq) > 40:
            print(f"  ... and {len(uniq) - 40} more")
        return 1
    print(f"every spec has at least {thin} armour pieces and {thin} weapons in every band")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
