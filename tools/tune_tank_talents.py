#!/usr/bin/env python3
"""Give four tanks the mechanic their own description already promises. Idempotent.

    PYTHONPATH=. python3 tools/tune_tank_talents.py [--apply]

Kyle, 2026-10-28: "Yeah lets fix these up. moon guard is a magic tank, in coa its ranged too. but
its needs buff here."

Measured first, with tools/sim_role_balance.py, after three separate corrections to the measurement
itself - specs are built for the role being audited, shifted into their form, and now actually use
their rotation, because Moon Guard's mitigation triggers on_damage_cast and Dreadnought's
Void-Enhanced Shield on_cast, and a tank that only defends never fires either.

WHAT THE NUMBERS SAID, level 60, eight tank specs:

    paladin_protection    best effective HP and reduction, ZERO threat generation
    cultist_dreadnought   "sword-and-board ... blocking" in its own description, ZERO block chance
    sun_cleric_seraphim   "one-hand-and-shield block chassis", ZERO block chance
    starcaller_moon_guard last on effective HP by 1400, 3 turns alive against 6-12, zero threat,
                          and - for the spec Kyle calls the magic tank - zero magic mitigation

EVERY EDIT GOES ON A NODE THAT ALREADY MEANS IT. Improved Righteous Fury is Classic's threat talent
and already carries damage_taken_pct; Void-Enhanced Shield already has block_value_pct and only
lacked the block chance to apply it to; Bulwark of the Sun is the Seraphim's shield node. Adding a
key to an existing, named, thematically-correct node keeps the tree readable - a new "+threat" node
bolted on would say the designer forgot, where this says the talent does what it sounds like.

MOON GUARD IS THE EXCEPTION AND GETS THREE CHANGES, because one mechanic was not its problem. It was
last on survival by a wide margin AND had nothing it was best at. Its magic mitigation is set above
Sun Cleric Seraphim's 28%, deliberately: Seraphim keeps magic as a real secondary strength, and the
spec whose whole identity is tanking magic should be the one that tanks it best.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: (tree, node name, {effect key: value per point}, why)
EDITS = [
    ("paladin_protection", "Improved Righteous Fury", {"threat_generation_pct": 0.08},
     "Righteous Fury IS the Classic threat talent. 3 points puts it at 24%, level with the "
     "Protection Warrior, which is right for the other main tank."),

    ("cultist_dreadnought", "Void-Enhanced Shield", {"block": 3.0},
     "It already scales block VALUE by 3% a point and had no block CHANCE to apply it to - the "
     "talent was scaling something that never happened. 5 points gives 15 block."),
    ("cultist_dreadnought", "Entropic Retaliation", {"threat_generation_pct": 0.04},
     "A retaliation talent that already procs on damage taken is the natural home for threat. "
     "5 points gives 20%, under the Warrior's 24 - Dreadnought's pull is its shadow damage."),

    ("sun_cleric_seraphim", "Bulwark of the Sun", {"block": 3.0},
     "Same gap as Dreadnought: block value scaled by 4% a point, no block chance anywhere in the "
     "tree, on a spec described as a one-hand-and-shield block chassis."),

    ("starcaller_moon_guard", "Crystal Shield", {"spell_damage_taken_pct": -0.07},
     "THE magic tank had no magic mitigation at all. 5 points gives -35%, deliberately above Sun "
     "Cleric Seraphim's 28% so the spec built around tanking magic is the best at it."),
    ("starcaller_moon_guard", "Endless Sky", {"stamina_pct": 4.0},
     "Was 2% a point, and Moon Guard sat 1400 effective HP below the next tank and survived 3 "
     "turns against 6 to 12. Doubling its one health talent is the smallest lever that closes it."),
    ("starcaller_moon_guard", "Guarded by the Moon", {"threat_generation_pct": 0.2},
     "Its third zero. A one-point capstone-ish node that already applies a mitigation buff when it "
     "casts is the right place for a tank's threat."),
]


def main():
    apply = "--apply" in sys.argv
    argparse.ArgumentParser().parse_known_args()

    changed, already, missing = 0, 0, []
    for tree_id, node_name, effects, why in EDITS:
        path = ROOT / f"data/talents/{tree_id}.json"
        doc = json.loads(path.read_text())
        node = next((n for n in doc["nodes"] if n.get("name") == node_name), None)
        if node is None:
            missing.append(f"{tree_id}: no node named {node_name!r}")
            continue
        eff = node.setdefault("effects", {})
        todo = {k: v for k, v in effects.items() if eff.get(k) != v}
        if not todo:
            already += 1
            continue
        pts = node.get("max_points", 1)
        print(f"  {tree_id}/{node_name} ({pts}pt)")
        for k, v in todo.items():
            before = eff.get(k, "absent")
            print(f"      {k}: {before} -> {v}   = {v * pts:+.2f} at full")
        print(f"      {why}")
        if apply:
            eff.update(todo)
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        changed += 1

    if missing:
        print(f"\nFAILED - {len(missing)} node names did not match:")
        for m in missing:
            print(f"  - {m}")
        return 1
    print(f"\n{changed} nodes changed, {already} already correct")
    if not apply:
        print("(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
