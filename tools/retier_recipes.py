#!/usr/bin/env python3
"""Point every crafted item at the material tier its own power says it should use. Idempotent.

    PYTHONPATH=. python3 tools/retier_recipes.py [--apply]

Kyle, 2026-10-28: "we need to ensure each tier of resources gets actual crafted items from them."

THE AUDIT THAT FOUND THIS. 341 of 655 recipes ask for more skill than their best material is worth -
every profession, worst gap 130 points. The symptom in one line: Plagueweave Robe needs Tailoring 208
and is made of Silk, which drops off level-18 humanoids. A tailor at the top of the profession was
still farming the same cloth they farmed at skill 60, and every tier above Silk fell on the floor. It
accumulated honestly: each zone's content pass reached for whatever material was familiar at the time,
and the skill axis climbed while the material axis stood still.

WHY ITEM LEVEL IS THE ANCHOR AND NOT SKILL RANK. The first version of this ranked recipes by skill and
dealt the ladder out by percentile. It produced a beautifully even spread and it was nonsense: a
themed robe of item level 21 came out wanting cloth off level-38 mobs, so you would farm late
material to make early gear. Item level is what the piece is actually worth, so the rung is chosen by
it - the highest tier whose SOURCE drops at or below the gear's own level, and whose skill band the
crafter can have reached. Both conditions, so nothing ever asks for a material above its own level or
above its own skill.

WHAT IS DELIBERATELY LEFT ALONE:

  * Anything whose name carries its material. "Silk Robe" made of Thistledown is not a re-tier, it is
    a lie, and upgrade kits name their tier in the output id as well. Those are the base sets: they
    define each rung and keep their own cloth.
  * Anything that is not gear. Bolts, kits and parts are intermediate steps, not items.
  * Blacksmithing, woodworking, engineering and alchemy. Their mis-tiering is real - a smith at skill
    200 is still smelting bronze - but it cannot be fixed here. Cloth and leather have 40 authored
    tiers each; ore has 7 and wood has 7, so those ladders simply END, and Kyle has ruled out adding
    gathering tiers ("i dont want to start adding new tiers of gathering stuff"). Re-pointing a
    skill-200 plate recipe would mean pointing it at steel, which is where it already points. That
    gap needs a decision about the ore and wood ladders, not a script.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Each ladder, in rung order, limited to tiers whose source is reachable at or below the level cap.
LADDERS = {
    "bolt": ["bolt_linen", "bolt_wool", "bolt_cotton", "bolt_hempen", "bolt_silk",
             "bolt_mageweave", "bolt_spidersilk", "bolt_dusk_velvet", "bolt_gossamer",
             "bolt_thistledown"],
    "leather": ["leather_scrap", "leather_light", "leather_medium", "leather_heavy",
                "leather_thick", "leather_rugged", "leather_cragscale", "leather_stormscale",
                "leather_stonebound"],
}

#: (recipe file, path to the recipe dict inside it, which ladder its primary input comes from)
TARGETS = [
    ("data/crafting/recipes.json", ("professions", "tailoring", "recipes"), "bolt"),
    ("data/leatherworking/recipes.json", ("recipes",), "leather"),
]

GEAR = {"armor", "weapon"}


def dig(d, path):
    for k in path:
        d = d[k]
    return d


def drop_level(mid, first):
    """The mob level at which this material's SOURCE first appears. A bolt inherits its cloth's."""
    src = mid.replace("bolt_", "cloth_") if mid.startswith("bolt_") else mid
    return first.get(src, 999)


def main():
    apply = "--apply" in sys.argv
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text())["materials"]

    import importlib.util
    spec = importlib.util.spec_from_file_location("qm", ROOT / "tools/qa_materials.py")
    qm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qm)
    first = qm.obtainable()

    # Every tier word that appears in any cloth, bolt or leather id, so a recipe NAMED for its
    # material is recognised even when that material is off the in-reach ladder (Runecloth, Felcloth).
    words = set()
    for mid, data in mats.items():
        if data.get("material_type") in ("bolt", "cloth", "leather"):
            words |= set(re.findall(r"[a-z]+", mid.split("_", 1)[1]))

    moves, kept = [], 0
    for rel, path, fam in TARGETS:
        p = ROOT / rel
        doc = json.loads(p.read_text())
        recipes = dig(doc, path)
        ladder = sorted(LADDERS[fam], key=lambda m: drop_level(m, first))

        for rid, r in recipes.items():
            if not isinstance(r, dict):
                continue
            out = r.get("output") or {}
            inputs = r.get("inputs") or {}
            family_inputs = [m for m in inputs if mats.get(m, {}).get("material_type") == fam]
            # TWO MATERIALS FROM THE SAME LADDER IS AN AUTHORED BLEND, NOT A MISTAKE. Woven Hempen
            # Leggings is hempen and wool on purpose; Thick Leather Gloves is Thick and Cragscale on
            # purpose. Re-pointing one half of a blend collapses it into the other half. This also
            # caught a real oscillation: the first version took whichever family input came first in
            # dict order as "the" primary, so Grovewalker Mantle moved its medium leather on one run
            # and then its light leather on the next, and the tool never settled.
            if len(family_inputs) != 1 or out.get("kind") not in GEAR:
                kept += 1
                continue
            primary = family_inputs[0]
            if any(w in r.get("name", "").lower() for w in words):
                kept += 1          # its name IS its tier; the base sets define the rungs
                continue

            ilvl = out.get("item_level") or 1
            skill = r.get("skill_required", 0)
            pick = ladder[0]
            for rung in ladder:
                if drop_level(rung, first) <= ilvl and mats[rung]["skill_range"][0] <= skill:
                    pick = rung
            if pick == primary:
                kept += 1
                continue

            moves.append((rel, path, rid, r.get("name", rid), ilvl, skill, primary, pick))
            if apply:
                qty = inputs.pop(primary)
                inputs[pick] = inputs.get(pick, 0) + qty
                # material_tier is what the item card and upgrade-kit matching read off the output.
                if out.get("material_tier"):
                    out["material_tier"] = pick.split("_", 1)[1]

        if apply:
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print(f"{len(moves)} recipes re-tiered, {kept} left as authored\n")
    for rel, _path, _rid, name, ilvl, skill, old, new in sorted(moves, key=lambda m: (m[0], m[4])):
        print(f"  ilvl {ilvl:>3}  skill {skill:>3}   {name:<34}{old:<22} -> {new}")
    if not apply:
        print("\n(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
