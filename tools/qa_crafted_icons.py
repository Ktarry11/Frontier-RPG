#!/usr/bin/env python3
"""Crafted gear icons: one fixed icon per piece, matched to its collection's colour; epics get their own art.

    PYTHONPATH=. python3 tools/qa_crafted_icons.py

Kyle, 15 Nov 2026: "Ensure crafting makes ONE icon per craft. Not random", then "You can shift some icons
to use for crafting. Blues I don't much care about. For epics we will use proper art."

  1. Every crafted piece names an icon, and the file exists.
  2. No collection uses the same icon twice on greens and blues.
  3. Coloured collections land near their colour: most strongly coloured pieces are a close match.
  4. The picks are repeatable: building twice gives the same icons.
  5. Epics: reports how many have their own art yet (gear_epic_crafted_<name>.png); the rest show a stand-in.
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import gear_icons as GI  # noqa: E402
from crafted_icon_palette import Picker, target, measure, distance  # noqa: E402
from build_crafted_gear import epic_icon_id  # noqa: E402

FILES = ["data/crafting/recipes.json", "data/blacksmithing/recipes.json", "data/leatherworking/recipes.json",
         "data/jewelcrafting/recipes.json"]
CLOSE = 0.6
CLOSE_SHARE = 0.75


def walk(x):
    if isinstance(x, dict):
        o = x.get("output")
        if isinstance(o, dict) and isinstance(o.get("item"), dict) and o["item"].get("slot"):
            yield o["item"]
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)


def main():
    bad = []
    items = []
    for f in FILES:
        items += list(walk(json.loads((ROOT / f).read_text(encoding="utf-8"))))
    have = set(GI._all_gear_files())

    missing = [i["name"] for i in items if i.get("icon_id") not in have]
    if missing:
        bad.append(f"{len(missing)} crafted pieces name no icon file, e.g. {missing[:5]}")
    print(f"1. {len(items) - len(missing)}/{len(items)} pieces have an icon file")

    plain = [i for i in items if i.get("rarity") not in ("epic", "legendary")]
    sets = collections.defaultdict(list)
    for i in plain:
        sets[i["name"].split()[0].lower()].append(i["icon_id"])
    repeats = {k: v for k, v in sets.items() if len(v) != len(set(v))}
    if repeats:
        bad.append(f"{len(repeats)} collections repeat an icon: {list(repeats)[:6]}")
    print(f"2. {len(sets) - len(repeats)}/{len(sets)} collections never repeat an icon")

    strong = [i for i in plain if target(i["name"], i.get("armor_type"))[1] >= 0.45]
    close = [i for i in strong if distance(target(i["name"], i.get("armor_type")), measure(i["icon_id"])) <= CLOSE]
    share = len(close) / max(1, len(strong))
    print(f"3. {len(close)}/{len(strong)} strongly coloured pieces are a close match ({share:.0%})")
    if share < CLOSE_SHARE:
        bad.append(f"only {share:.0%} of coloured pieces match their colour (want {CLOSE_SHARE:.0%})")

    def picks():
        p = Picker()
        return [p.pick(i["name"], i["slot"], i.get("armor_type"), i.get("weapon_type")) for i in plain]
    a, b = picks(), picks()
    if a != b:
        bad.append("two builds picked different icons")
    print("4. two builds pick the same icons" if a == b else "4. builds differ")

    epics = [i for i in items if i.get("rarity") in ("epic", "legendary")]
    own = [i for i in epics if i.get("icon_id") == epic_icon_id(i["name"])]
    print(f"5. epics with their own art: {len(own)}/{len(epics)} (the rest show the epic pool's stand-in)")

    if bad:
        print("\nFAILED:")
        for x in bad:
            print("  -", x)
        return 1
    print("\ncrafted icons OK - one fixed icon each, each collection in its own colour, no repeats inside a set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
