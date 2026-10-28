#!/usr/bin/env python3
"""Give the last three orphaned materials a real use. Idempotent.

    PYTHONPATH=. python3 tools/build_material_sinks.py

Kyle, 2026-10-28: "we need to ensure each tier of resources gets actual crafted items from them."

After the re-tier closed every cloth and leather dead end, three materials were still mined or
harvested by players and consumed by nothing at all:

    bar_weakstone      smelted from level-1 ore, zero consumers
    bar_silver         smelted from silver ore, zero consumers
    part_tide_seal     made from Drowning Floor tideglass, zero consumers - my own orphan, added
                       with the cooking pass and never wired to anything

THESE ARE RETROFITS, NOT NEW RECIPES, which is the whole point. A new recipe for an unused material
just moves the problem one step along the chain: now the recipe's OUTPUT is the thing nobody wants.
Adding the material to content that already exists and that players already make makes it
load-bearing immediately.

Each choice follows from what the material actually is:

  * Weakstone's own description is "a brittle refined bar, barely holds together". That rules out
    armour and tools, and it is exactly right for SHOT - cheap metal fired out of a gun by the
    handful and never seen again. It is the one sink where brittle is a feature.
  * Silver is a conductor, so it goes into the three engineering recipes that move a charge.
  * The Tideglass Seal keeps water out of things that mind, and the Brine Flask is a flask of
    seawater. It should always have needed one.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: {recipe_id: {material: quantity}} added to the recipe's existing inputs.
SINKS = {
    # brittle, cheap, fired by the handful
    "eng_iron_shot": {"bar_weakstone": 2},
    "eng_brine_shot": {"bar_weakstone": 2},
    # conductors
    "eng_static_charge": {"bar_silver": 1},
    "eng_jumper_cables": {"bar_silver": 1},
    "eng_charged_shot": {"bar_silver": 1},
    # keeps the sea out of the flask
    "eng_brine_flask": {"part_tide_seal": 1},
}


def main():
    p = ROOT / "data/crafting/recipes.json"
    doc = json.loads(p.read_text())
    eng = doc["professions"]["engineering"]["recipes"]

    # The ids above are guesses at a naming convention, and a guess that silently matches nothing
    # is the worst outcome here - it would print success and change nothing. Resolve by recipe NAME
    # as well, and refuse to continue if any target is unresolved.
    by_name = {r.get("name"): rid for rid, r in eng.items() if isinstance(r, dict)}
    wanted = {
        "eng_iron_shot": "Iron Shot",
        "eng_brine_shot": "Brine Shot",
        "eng_static_charge": "Static Charge",
        "eng_jumper_cables": "Jumper Cables",
        "eng_charged_shot": "Charged Shot",
        "eng_brine_flask": "Brine Flask",
    }
    resolved, missing = {}, []
    for key, adds in SINKS.items():
        rid = key if key in eng else by_name.get(wanted[key])
        if rid is None:
            missing.append(wanted[key])
        else:
            resolved[rid] = adds
    if missing:
        print(f"FAILED: no recipe found for {missing}")
        return 1

    touched = 0
    for rid, adds in resolved.items():
        inputs = eng[rid].setdefault("inputs", {})
        changed = False
        for mid, qty in adds.items():
            if mid not in inputs:
                inputs[mid] = qty
                changed = True
        if changed:
            touched += 1
            print(f"  {eng[rid]['name']:<22}+ {', '.join(f'{q}x {m}' for m, q in adds.items())}")

    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{touched} recipes changed ({len(resolved) - touched} already had their input)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
