#!/usr/bin/env python3
"""Put every herb in zones a character of the right level can actually reach.

    PYTHONPATH=. python3 tools/rebalance_herb_nodes.py [--apply]

Idempotent. Prints the plan by default; --apply writes node_pools.json.

=============================================================================
WHY THIS EXISTS
=============================================================================

tools/reanchor_gathering_ladders.py moved every WoW-named herb to its real
Classic skill. Fadeleaf went from 20 to 160, Khadgar's Whisker from 160 to 185,
and six new herbs (Wild Steelbloom through Black Lotus) were created with no
zone placement at all. A herb's skill decides which trainer tier you need, and
the trainer tier decides your minimum level, so moving the skill moves where
the herb belongs. Nineteen placements were left stranded - Fadeleaf in seven
zones banded 4-21 when it now needs level 25.

=============================================================================
THE TWO RULES, AND WHICH ONE IS ALLOWED TO BEND
=============================================================================

HARD - the trainer gate. data/professions/professions.json: skill 75/150/225/300
is trainable at level 1/10/25/40. A herb at skill 160 needs Journeyman's
successor, Expert, which is level 25, so it may ONLY sit in a zone whose band
reaches 25. This is the game's own rule and it never bends: a node you cannot
pick is worse than no node.

SOFT - the natural band. In WoW a herb's skill tracks the level of the zone it
grows in at roughly skill = level x 5, which is why Peacebloom (1) is in
starter zones and Sungrass (230) is in the mid-forties. So each herb PREFERS
zones whose band contains skill/5, and takes the closest legal band when its
preference does not exist. Black Lotus wants level 60; the game's highest zone
is 52; it goes to 52 rather than nowhere.

Weights are preserved. A herb already placed legally is left exactly where it
is - this tool moves what is broken and places what is new, and does not
reshuffle a zone that is already correct.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOLS = ROOT / "data" / "gathering" / "node_pools.json"

SKILL_PER_LEVEL = 5.0          # WoW's own rule of thumb, see docstring

#: How many zones a herb should appear in, by how common it is meant to be.
#: Black Lotus in one zone at weight 1 is the point of Black Lotus.
SPREAD_BY_RARITY = [(0, 4), (150, 3), (230, 2), (290, 1)]

#: Default weight for a newly placed herb, by skill. Commons are plentiful,
#: the terminal herb is not.
WEIGHT_BY_SKILL = [(0, 3), (150, 2), (230, 2), (290, 1)]


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def by_threshold(table, skill):
    out = table[0][1]
    for lo, v in table:
        if skill >= lo:
            out = v
    return out


def slug(n):
    s = str(n).lower().replace(" ", "_").replace("'", "")
    return s[4:] if s.startswith("the_") else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mats = load("data/gathering/materials.json")["materials"]
    bands = load("data/zones/zone_levels.json")["zones"]
    tiers = [(t["cap"], t["required_level"]) for t in
             load("data/professions/professions.json")["tiers"]]
    doc = load("data/gathering/node_pools.json")
    pools = doc["zones"]

    def gate(skill):
        for cap, lvl in tiers:
            if skill <= cap:
                return lvl
        return None

    # zone key as node_pools spells it -> (lo, hi)
    zband = {}
    for name, band in bands.items():
        for key in (slug(name), str(name).lower().replace(" ", "_").replace("'", "")):
            zband.setdefault(key, tuple(band))
    pooled = {z: zband[z] for z in pools if z in zband}

    herbs = {mid: m for mid, m in mats.items() if m["material_type"] == "herb"}
    removals, additions = [], []

    for mid, m in sorted(herbs.items(), key=lambda kv: kv[1]["skill_range"][0]):
        skill = m["skill_range"][0]
        need = gate(skill)
        if need is None:
            continue                               # past every tier: not placeable
        legal = {z: b for z, b in pooled.items() if b[1] >= need}
        here = {z for z, p in pools.items() if mid in (p.get("table") or {})}

        # strip the illegal ones
        for z in sorted(here - set(legal)):
            removals.append((z, mid, m["name"], pools[z]["table"][mid],
                             f"zone tops at {pooled[z][1]}, needs {need}"))

        kept = here & set(legal)
        want = by_threshold(SPREAD_BY_RARITY, skill)
        if len(kept) >= want:
            continue

        # fill up to `want` with the legal zones nearest the natural band
        natural = skill / SKILL_PER_LEVEL
        def distance(z):
            lo, hi = legal[z]
            return 0 if lo <= natural <= hi else min(abs(natural - lo), abs(natural - hi))
        for z in sorted(set(legal) - kept, key=lambda z: (distance(z), z))[:want - len(kept)]:
            additions.append((z, mid, m["name"], by_threshold(WEIGHT_BY_SKILL, skill),
                              f"natural lv {natural:.0f}, zone {legal[z][0]}-{legal[z][1]}"))

    print(f"  {len(herbs)} herbs over {len(pooled)} pooled zones")
    print(f"  gate: skill -> tier -> minimum level, from professions.json\n")

    if removals:
        print(f"  REMOVE {len(removals)} unreachable placement(s)")
        for z, mid, name, w, why in removals:
            print(f"    {z[:26]:28}{name[:22]:24}w={w}   {why}")
    if additions:
        print(f"\n  ADD {len(additions)} placement(s)")
        for z, mid, name, w, why in additions:
            print(f"    {z[:26]:28}{name[:22]:24}w={w}   {why}")
    if not removals and not additions:
        print("  every herb is already placed where it can be picked")

    # NO HERB MAY END UP IN ZERO ZONES. A removal pass that strands a material
    # is worse than the misplacement it fixed, and the arithmetic is easy to get
    # wrong: a herb pulled from seven zones gets no replacement if it already
    # sits in enough legal ones, which looks identical in the plan above to a
    # herb pulled from everywhere and given nothing. Check, do not squint.
    final = {}
    for mid in herbs:
        zs = {z for z, p in pools.items() if mid in (p.get("table") or {})}
        zs -= {z for z, m, *_ in removals if m == mid}
        zs |= {z for z, m, *_ in additions if m == mid}
        final[mid] = zs
    stranded = sorted(mid for mid, zs in final.items() if not zs)
    if stranded:
        print(f"\n  REFUSING TO WRITE - {len(stranded)} herb(s) would be in no zone at all:")
        for mid in stranded:
            m = herbs[mid]
            print(f"    {m['name']} (skill {m['skill_range'][0]}, needs level "
                  f"{gate(m['skill_range'][0])})")
        print("  Either a zone high enough does not exist, or SPREAD_BY_RARITY is too small.")
        return 1
    print(f"\n  every one of the {len(herbs)} herbs ends up in at least one reachable zone "
          f"(fewest: {min(len(z) for z in final.values())})")

    if args.apply:
        for z, mid, *_ in removals:
            pools[z]["table"].pop(mid, None)
        for z, mid, name, w, _ in additions:
            pools[z].setdefault("table", {})[mid] = w
        POOLS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"\n  wrote {POOLS.relative_to(ROOT)}")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
