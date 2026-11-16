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
    seen_names = set()
    for i in plain:
        if i["name"] in seen_names:      # the same piece written in two recipes is one piece, one icon
            continue
        seen_names.add(i["name"])
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

    # 4. the picks are written down (tools/assign_crafted_icons.py), so a rebuild gives the same icons
    assigned = json.loads((ROOT / "data/items/crafted_icons.json").read_text(encoding="utf-8"))["icons"]
    from build_crafted_gear import icon_for
    drift = [i["name"] for i in items if assigned.get(i["name"]) != i.get("icon_id")
             or icon_for(i["name"], i["slot"], i.get("armor_type"), i.get("weapon_type"), i.get("rarity"))
             != i.get("icon_id")]
    if drift:
        bad.append(f"{len(drift)} pieces would get a different icon on a rebuild, e.g. {drift[:4]}")
    print(f"4. a rebuild keeps every icon ({len(items) - len(drift)}/{len(items)})")

    # 5. Kyle, 16 Nov: "every unique item in the game can only have ONE icon". A crafted epic's icon is its
    # own: no other crafted piece, and no other item anywhere, draws it.
    from assign_crafted_icons import icons_used_elsewhere
    elsewhere = icons_used_elsewhere()
    by_icon = collections.defaultdict(set)
    for i in items:
        by_icon[i.get("icon_id")].add(i["name"])
    epics = {i["name"]: i for i in items if i.get("rarity") in ("epic", "legendary")}
    shared = [n for n, i in epics.items() if len(by_icon[i["icon_id"]]) > 1 or elsewhere.get(i["icon_id"])]
    if shared:
        bad.append(f"{len(shared)} crafted epics share their icon, e.g. {shared[:4]}")
    print(f"5. crafted epics with an icon of their own: {len(epics) - len(shared)}/{len(epics)}")
    ep = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    epic_owned = {d.get("icon_id") for k in ("world", "dungeon") for d in ep.get(k, [])}
    on_epic = sorted({i["name"] for i in items if i.get("icon_id") in epic_owned})
    if on_epic:
        bad.append(f"{len(on_epic)} crafted pieces draw a named epic's icon, e.g. {on_epic[:4]}")
    plain_names = {i["name"] for i in plain}
    many = sum(1 for icon, names in by_icon.items() if len(names & plain_names) > 1)
    print(f"   (greens and blues: {many} icons still on more than one piece, where a slot's art runs short)")

    if bad:
        print("\nFAILED:")
        for x in bad:
            print("  -", x)
        return 1
    print("\ncrafted icons OK - one fixed icon each, each collection in its own colour, no repeats inside a set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
