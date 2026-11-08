#!/usr/bin/env python3
"""Give every crafting profession a reagent ladder that climbs with its recipes.

    PYTHONPATH=. python3 tools/tier_crafting_reagents.py [--apply] [profession ...]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
WHY
=============================================================================

Kyle, 7 Nov 2026: "Don't forget we need vials. We should use wow style where
there are different vials. Currently we just have 1 type." Then: "We also need
this for Blacksmithing."

Alchemy had three vials - Empty, Leaded, Crystal - sitting in materials.json
with art installed, and all 79 recipes reached for the Empty one. Blacksmithing
was worse: three fluxes and a whetstone, all with art, and not one recipe used
a reagent at all. Every plan was bars and nothing else. That is most of why
tools/qa_materials.py reported trade_goods at 2 of 23 materials consumed.

ONE TOOL, NOT ONE PER PROFESSION. The rule is identical everywhere - a recipe
takes the reagent whose tier matches its own skill - and this codebase's
recurring defect is the same rule implemented twice and drifting apart (two
take_damage paths, two block formulas, two output schemas in the recipe files).
Adding tailoring or leatherworking here is a table entry, not a new script.

=============================================================================
WHICH RECIPES GET ONE
=============================================================================

Only recipes that produce a FINISHED good - armor, a weapon, a consumable. The
intermediate steps do not: smelting an ore into a bar needs no flux, and
weaving cloth into a bolt needs no thread, for the same reason WoW does not ask
for them. Gating on output kind rather than on profession keeps that honest
even when a profession does both, as blacksmithing does with its upgrade kits.

A recipe that already carries a reagent from its own ladder is RETIERED, not
doubled - the old one is removed first. That is what makes this safe to re-run
after the skill ladders move again.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Where each profession's recipes live. Two shapes: a file with a top-level
#: "recipes", or data/crafting/recipes.json keyed by profession.
SOURCES = {
    "blacksmithing": ("data/blacksmithing/recipes.json", None),
    "leatherworking": ("data/leatherworking/recipes.json", None),
    "alchemy": ("data/crafting/recipes.json", "alchemy"),
    "tailoring": ("data/crafting/recipes.json", "tailoring"),
    "woodworking": ("data/crafting/recipes.json", "woodworking"),
    "engineering": ("data/crafting/recipes.json", "engineering"),
}

#: Output kinds that count as a finished good and so take a reagent.
FINISHED = {"armor", "weapon", "consumable"}

#: profession -> slot name -> ladder. A ladder is (skill_below, material_id)
#: pairs, last entry None meaning "and everything above". `kinds` limits a slot
#: to certain output kinds; None means every finished good.
#:
#: The thresholds are WoW's own shape - a new reagent roughly every hundred
#: skill, which is one per trainer tier.
LADDERS = {
    "alchemy": {
        "vial": dict(qty=1, kinds=None, tiers=[
            (100, "vial_empty"), (200, "vial_leaded"), (None, "vial_crystal")]),
    },
    "blacksmithing": {
        "flux": dict(qty=1, kinds=None, tiers=[
            (100, "flux_weak"), (200, "flux_medium"), (None, "flux_strong")]),
        # A blade needs an edge put on it; a breastplate does not.
        "stone": dict(qty=1, kinds={"weapon"}, tiers=[(None, "whetstone")]),
    },
    "leatherworking": {
        "cure": dict(qty=1, kinds=None, tiers=[
            (150, "tanning_reagent"), (None, "curing_salt")]),
    },
    "tailoring": {
        "thread": dict(qty=1, kinds=None, tiers=[
            (100, "thread_coarse"), (200, "thread_fine"), (None, "thread_silken")]),
    },
    "woodworking": {
        "bond": dict(qty=1, kinds=None, tiers=[
            (150, "glue"), (None, "resin")]),
    },
}


def pick(tiers, skill):
    for below, mid in tiers:
        if below is None or skill < below:
            return mid
    return tiers[-1][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("professions", nargs="*", default=None)
    args = ap.parse_args()

    mats = json.loads((ROOT / "data/gathering/materials.json").read_text())["materials"]
    want = set(args.professions) or set(LADDERS)

    # every reagent named in a ladder must exist, or we would author a recipe
    # that can never be completed
    named = {m for slots in LADDERS.values() for s in slots.values()
             for _, m in s["tiers"]}
    missing = sorted(named - set(mats))
    if missing:
        print(f"  REFUSING - reagent(s) not in materials.json: {', '.join(missing)}")
        return 1

    docs, changes = {}, []
    for prof in sorted(want & set(LADDERS)):
        rel, key = SOURCES[prof]
        if rel not in docs:
            docs[rel] = json.loads((ROOT / rel).read_text())
        doc = docs[rel]
        recipes = (doc["professions"][key]["recipes"] if key else doc["recipes"])
        slots = LADDERS[prof]
        owned = {m for s in slots.values() for _, m in s["tiers"]}

        for rid, r in recipes.items():
            if not isinstance(r, dict):
                continue
            out = r.get("output")
            kind = out.get("kind") if isinstance(out, dict) else None
            inputs = r.get("inputs")
            if kind not in FINISHED or not isinstance(inputs, dict):
                continue
            skill = r.get("skill_required", 0)
            for sname, s in slots.items():
                if s["kinds"] is not None and kind not in s["kinds"]:
                    continue
                target = pick(s["tiers"], skill)
                present = [m for m in inputs if m in {t[1] for t in s["tiers"]}]
                if present == [target] and inputs[target] == s["qty"]:
                    continue
                changes.append((prof, rid, r.get("name", rid), skill, sname,
                                present[0] if present else None, target))
                if args.apply:
                    for m in present:
                        inputs.pop(m, None)
                    inputs[target] = s["qty"]

    by_prof = {}
    for c in changes:
        by_prof.setdefault(c[0], []).append(c)

    print(f"  {len(changes)} recipe reagent(s) to set, over {len(by_prof)} profession(s)")
    print(f"  only finished goods ({', '.join(sorted(FINISHED))}) take a reagent\n")
    for prof in sorted(by_prof):
        rows = by_prof[prof]
        added = sum(1 for r in rows if r[5] is None)
        print(f"  {prof}  ({len(rows)} recipes: {added} gained a reagent, "
              f"{len(rows) - added} retiered)")
        counts = {}
        for _, _, _, skill, sname, old, new in rows:
            counts[(sname, new)] = counts.get((sname, new), 0) + 1
        for (sname, new), n in sorted(counts.items()):
            lo = min(r[3] for r in rows if r[4] == sname and r[6] == new)
            hi = max(r[3] for r in rows if r[4] == sname and r[6] == new)
            print(f"      {sname:7}{mats[new]['name']:20}{n:>4} recipes   skill {lo}-{hi}")

    if args.apply:
        for rel, doc in docs.items():
            (ROOT / rel).write_text(json.dumps(doc, indent=2) + "\n")
        print(f"\n  wrote {', '.join(sorted(docs))}")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
