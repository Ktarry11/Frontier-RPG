#!/usr/bin/env python3
"""Ranged weapons authored into a melee slot. Reports, or rewrites.

    PYTHONPATH=. python3 tools/fix_ranged_slots.py --check
    PYTHONPATH=. python3 tools/fix_ranged_slots.py

A bow, gun, crossbow, wand, totem, libram, idol or thrown weapon belongs in
the `ranged` slot. Twenty authored items said `main_hand`, so equipping a bow
took the character's melee weapon off. entities/equipment._resolve_slot now
routes by the weapon type's `hand` field regardless of what the item says, so
the game is correct either way - but data that disagrees with the engine is a
trap for the next person who reads it, and for any tool that groups loot by
slot without going through Equipment.

WHICH TYPES ARE RANGED IS READ, NOT LISTED. The first version of this tool
carried its own list of ranged weapon types, which is how a tool ends up
disagreeing with the data it is checking the moment somebody adds a type.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ranged_types():
    """Weapon types whose `hand` is "ranged", straight from the weapon data."""
    wt = json.loads((ROOT / "data/items/weapon_types.json").read_text())["weapon_types"]
    return {k for k, v in wt.items() if v.get("hand") == "ranged"}


def walk(node, ranged, found):
    """Every dict in the tree that is a ranged weapon filed under another slot."""
    if isinstance(node, dict):
        if node.get("weapon_type") in ranged and node.get("slot") not in (None, "ranged"):
            found.append(node)
        for v in node.values():
            walk(v, ranged, found)
    elif isinstance(node, list):
        for v in node:
            walk(v, ranged, found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report and exit non-zero; change nothing")
    args = ap.parse_args()

    ranged = ranged_types()
    total = 0
    touched = []
    for path in sorted((ROOT / "data").rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        found = []
        walk(data, ranged, found)
        if not found:
            continue
        total += len(found)
        rel = path.relative_to(ROOT)
        for item in found:
            print(f"  {rel}: {item.get('name')} "
                  f"({item.get('weapon_type')} in {item.get('slot')})")
        if not args.check:
            for item in found:
                item["slot"] = "ranged"
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
            touched.append(rel)

    if not total:
        print("clean: every ranged weapon is in the ranged slot")
        return 0
    if args.check:
        print(f"\n{total} ranged weapons are in a melee slot")
        return 1
    print(f"\nmoved {total} items to the ranged slot across {len(touched)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
