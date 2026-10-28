#!/usr/bin/env python3
"""Nothing the world hands you is a dead end.

    PYTHONPATH=. python3 tools/qa_materials.py [--all]

Kyle, 2026-10-28: "We need to ensure each harvestable is being used... the higher level or different
materials cant end up being useless."

THE RAW NUMBER LIES, WHICH IS WHY THIS TOOL IS NOT A ONE-LINE GREP. 151 of 260 materials are never a
recipe input, and that sounds like a catastrophe. It is not:

  * upgrade kits are OUTPUTS - you make them and apply them to gear, they were never meant to be an
    input to anything;
  * most dead tiers drop at levels 45-99, and the game's real ceiling is 40 (the Crystalline Underdark
    is 32-40, and no vendor anywhere is geared above 38). Material ladders were authored out to the
    endgame years before the zones.

So the honest question is narrower: of the things a player can ACTUALLY OBTAIN at a level they can
actually reach, how many have nowhere to go? That is what this reports. --all shows the full picture
including the forward tiers, for when the level cap moves.

When it last failed, the answer was four, all cloth, and the cause was one missing link rather than a
missing profession: tailoring has 113 recipes but the chain is cloth -> BOLT -> armour, and the
cloth-to-bolt ladder stopped at seven tiers while cloth kept dropping.
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: The level the game actually reaches. Raise it when a zone does.
LEVEL_CAP = 42


def recipe_graph():
    """(materials consumed by some recipe, materials produced by some recipe)."""
    used, produced = set(), set()

    def scan(recipes):
        if not isinstance(recipes, dict):
            return
        for _rid, r in recipes.items():
            if not isinstance(r, dict):
                continue
            used.update((r.get("inputs") or {}).keys())
            out = r.get("output")
            if isinstance(out, dict) and out.get("material_id"):
                produced.add(out["material_id"])

    for f in sorted(ROOT.glob("data/*/recipes.json")):
        d = json.loads(f.read_text())
        if "professions" in d:
            for _p, b in d["professions"].items():
                if isinstance(b, dict):
                    scan(b.get("recipes", {}))
        else:
            scan(d.get("recipes", d))
    sm = json.loads((ROOT / "data/gathering/smelting_recipes.json").read_text())
    scan(sm.get("recipes", sm))
    return used, produced


def obtainable():
    """{material_id: lowest level it can first be obtained}."""
    first = defaultdict(lambda: 999)
    pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text())["zones"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]

    def zone_floor(zone_key):
        for zn, zd in enc.items():
            if zn.lower().replace(" ", "_").replace("'", "") != zone_key:
                continue
            lv = []
            for t in [zd.get("open_zone", {})] + list(zd.get("subzones", {}).values()) \
                    + list(zd.get("caves", {}).values()):
                for n in t.get("creatures", {}):
                    r = creatures.get(n, {}).get("level_range")
                    if r:
                        lv += list(r)
            if lv:
                return min(lv)
        return 1

    for zkey, v in pools.items():
        floor = zone_floor(zkey)
        for mid in v.get("table", {}):
            first[mid] = min(first[mid], floor)
    # Drop tables carry their own bands in the source.
    for mod in ("entities/skinning_drops.py", "entities/cloth_drops.py", "entities/meat_drops.py"):
        src = (ROOT / mod).read_text()
        for lo, _hi, tbl in re.findall(r"\((\d+),\s*(\d+),\s*(\{[^}]*\})\)", src):
            for mid in re.findall(r'"([a-z_]+)"', tbl):
                first[mid] = min(first[mid], int(lo))
    # A BAND IS NOT A PROMISE. Both drop modules filter high tiers out of every roll below level 60
    # (entities/material_tiers), so reading the bands alone reports tiers as obtainable that the
    # world will not hand anybody until then. Ask the module, do not re-derive it.
    from entities.material_tiers import HIGH_TIER, HIGH_TIER_FLOOR
    for mid in HIGH_TIER:
        first[mid] = max(first.get(mid, HIGH_TIER_FLOOR), HIGH_TIER_FLOOR)
    return first


def main():
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text())
    mats = mats.get("materials", mats)
    used, produced = recipe_graph()
    first = obtainable()
    show_all = "--all" in sys.argv

    inband = {m: lv for m, lv in first.items() if lv <= LEVEL_CAP}
    dead = sorted((lv, m) for m, lv in inband.items() if m not in used and m not in produced)
    forward = sorted((lv, m) for m, lv in first.items()
                     if lv > LEVEL_CAP and m not in used and m not in produced)

    print(f"== {len(mats)} materials, {len(used)} consumed by a recipe, "
          f"{len(first)} obtainable in the world\n")
    print(f"IN REACH (first obtainable at or below level {LEVEL_CAP}): {len(inband)}")
    print(f"  of those, with no recipe that consumes them: {len(dead)}")
    for lv, m in dead:
        print(f"     from level {lv:>2}   {m:<28}{mats.get(m, {}).get('material_type', '?')}")

    print(f"\nFORWARD TIERS (first obtainable above {LEVEL_CAP}): {len(forward)} unused")
    if show_all:
        for lv, m in forward:
            print(f"     from level {lv:>2}   {m}")
    else:
        print("  (not a failure - these are ladders authored past the level cap. --all to list)")

    print("\n== every profession has somewhere to spend its own output")
    by_prof = defaultdict(lambda: [0, 0])
    for m, data in mats.items():
        p = data.get("profession")
        if not p:
            continue
        by_prof[p][0] += 1
        if m in used:
            by_prof[p][1] += 1
    for p in sorted(by_prof):
        n, u = by_prof[p]
        print(f"  {p:<18}{u:>3}/{n:<4} of its materials are consumed somewhere")

    print()
    if dead:
        print(f"FAIL ({len(dead)})")
        for lv, m in dead:
            print(f"  - {m} drops from level {lv} and no recipe anywhere consumes it")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
