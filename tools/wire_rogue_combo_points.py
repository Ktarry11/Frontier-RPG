#!/usr/bin/env python3
"""Give the Rogue's abilities their combo-point builder/finisher roles.

    PYTHONPATH=. python3 tools/wire_rogue_combo_points.py [--dry-run]

WHY. The Rogue had no combo points at all - CLASS_RESOURCE_MAP listed it as
(ENERGY, None) - and 13 of the 83 real WotLK Rogue talents are written in
terms of them: Relentless Strikes, Seal Fate, Setup, Initiative,
Premeditation, Honor Among Thieves, Cut to the Chase, Lethality,
Ruthlessness, Riposte and more. Kyle's call on 5 Nov 2026 was to add them
rather than build a tree full of substitutes, because a Rogue without combo
points is not a Rogue.

The engine already had ResourceType.COMBO, because Templar spends it as a
PRIMARY resource. The Rogue is the first class to carry it as a SECOND
pool, and that is what needed Ability.secondary_cost: a finisher pays
Energy AND combo points, and a single cost field cannot express both.
Spending combo alone would have made Energy irrelevant to the only buttons
that matter.

THE SCALE IS TEMPLAR'S, not invented here. Every resource pool in this
engine is 0-100, so a generator grants 20 - one "combo point" - and a
finisher costs 20/40, which reads as the familiar 1-5 points at 20 each.
Templar's builders already grant exactly 20 and its finishers cost
20/40/60/80, so this follows a pattern the project is already running
rather than adding a second convention.

FINISHER COSTS ARE SET FROM MEASURED FIGHT LENGTH, not from real WoW.
Fights run 2-3 turns on trash and 5-6 on a boss (tools/qa_dot_durations.py
carries the measurements). Real WoW rogues finish at 5 points, which here
would be five generator turns - longer than most trash fights, so the
finisher would simply never fire. So:

    20 (one generator)   Slice and Dice, Expose Armor, Kidney Shot, Envenom
    40 (two generators)  Eviscerate, Rupture

That gives a generator-then-finisher pair inside a 2-turn trash fight, and
room to reach the 40-cost pair on anything longer. The two 40s are the
heavy hits, so the choice on a short fight is a real one.

WHAT IS DELIBERATELY NOT MODELLED. Real finishers scale their damage with
the number of combo points spent; this engine has no mechanism to read a
resource amount at cast time and scale off it (claude/engine_findings_
2026_11_06.md: nothing reads a live resource amount). So costs are flat and
the damage is fixed, exactly as Templar's are. A finisher is gated on
having built, not sharpened by how much. Recorded here rather than left as
a surprise.

Combo is NOT reset between turns - restore_resources_between_turns only
refills Energy and Mana - so it accumulates across a fight the way combo
points should.
"""

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATH = ROOT / "data/abilities/rogue.json"

#: One combo point, on the engine's universal 0-100 pool.
POINT = 20

#: Abilities that AWARD a combo point, exactly the real WotLK set.
GENERATORS = {
    "rogue_sinister_strike": "the baseline builder",
    "rogue_backstab": "builder, Subtlety's core",
    "rogue_mutilate": "builder, Assassination's core",
    "rogue_hemorrhage": "builder, awards 1 point in 3.3.5a",
    "rogue_garrote": "opener, awards 1 point",
    "rogue_ambush": "opener, awards 1 point",
    "rogue_cheap_shot": "opener, awards 1 point",
    "rogue_gouge": "awards 1 point in 3.3.5a",
    "rogue_shiv": "awards 1 point",
}

#: Abilities that SPEND combo points, with the cost in pool units.
#: See the module docstring for why these numbers and not 1-5 points.
FINISHERS = {
    "rogue_slice_and_dice": (POINT, "cheap self-buff finisher, usable at 1 point"),
    "rogue_expose_armor": (POINT, "debuff finisher, usable at 1 point"),
    "rogue_kidney_shot": (POINT, "stun finisher, usable at 1 point"),
    "rogue_envenom": (POINT, "poison finisher, usable at 1 point"),
    "rogue_eviscerate": (POINT * 2, "the heavy direct finisher"),
    "rogue_rupture": (POINT * 2, "the heavy bleed finisher"),
}

GEN_NOTE = (
    "Combo-point GENERATOR, wired 5 Nov 2026 when the Rogue gained combo "
    "points (Kyle's call). Grants {amt} of the 0-100 combo pool - one combo "
    "point on the same scale Templar already uses. {why}.")

FIN_NOTE = (
    "Combo-point FINISHER, wired 5 Nov 2026: secondary_cost {amt} means it "
    "spends {pts} combo point(s) ON TOP OF its Energy cost, via the new "
    "Ability.secondary_cost. {why}. Cost set from measured fight length "
    "(2-3 turns trash, 5-6 boss), not from real WoW's 5-point finishers, "
    "which would never fire here. Damage does NOT scale with points spent - "
    "no engine mechanism reads a live resource amount.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(PATH.read_text(), object_pairs_hook=OrderedDict)
    changed = []

    for a in data["abilities"]:
        aid = a["ability_id"]
        if aid in GENERATORS:
            if not a.get("generates"):
                a["generates"] = {"resource": "combo", "amount": POINT}
                a["_source"] = (a.get("_source", "").rstrip() + " "
                                + GEN_NOTE.format(amt=POINT,
                                                  why=GENERATORS[aid])).strip()
                changed.append((aid, "generator", f"+{POINT} combo"))
        elif aid in FINISHERS:
            cost, why = FINISHERS[aid]
            if not a.get("secondary_cost"):
                a["secondary_cost"] = cost
                a["_source"] = (a.get("_source", "").rstrip() + " "
                                + FIN_NOTE.format(amt=cost,
                                                  pts=cost // POINT,
                                                  why=why)).strip()
                changed.append((aid, "finisher", f"-{cost} combo"))

    unknown = ((set(GENERATORS) | set(FINISHERS))
               - {a["ability_id"] for a in data["abilities"]})
    if unknown:
        print(f"  ERROR: these ability_ids do not exist: {sorted(unknown)}")
        return 1

    if not changed:
        print("  nothing to change")
        return 0

    print(f"  {len(changed)} abilities wired "
          f"({sum(1 for c in changed if c[1] == 'generator')} generators, "
          f"{sum(1 for c in changed if c[1] == 'finisher')} finishers)")
    for aid, kind, what in sorted(changed, key=lambda r: (r[1], r[0])):
        print(f"    {aid:28s} {kind:10s} {what}")

    if args.dry_run:
        print("\n  --dry-run, nothing written")
        return 0

    PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(f"\n  wrote {PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
