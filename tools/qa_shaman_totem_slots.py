#!/usr/bin/env python3
"""The Shaman's four totem element slots must stay intact.

    PYTHONPATH=. python3 tools/qa_shaman_totem_slots.py [--report]

WHAT THIS PROTECTS. Real WoW gives the shaman four totem slots - Earth,
Fire, Water, Air - and one totem per slot, a new one replacing whatever
held that slot. Frontier models it with exclusive_group, one tag per
element, and Kyle's whole complaint on 5 Nov 2026 ("totems are weird for
shaman") was that none of it existed: all thirteen totems could be up at
once.

The assignment is pinned here rather than inferred, because it cannot be
inferred - it is deliberately cross-wired in the real game and looks like
a transcription error every time somebody reads it:

    Frost Resistance Totem  is a FIRE totem
    Fire Resistance Totem   is a WATER totem
    Nature Resistance Totem is an AIR totem

Each resistance sits in the element that OPPOSES the school it resists. A
future reader "fixing" Fire Resistance into the Fire slot would quietly
undo a real mechanic, so this test exists to argue back.

It also guards the two target_type bugs found alongside, because both were
invisible. Searing Totem and Earthbind Totem carried NO target_type, and
abilities.py:199 decides friend from foe with `target_type not in
("enemy", "enemy_aoe")` - so a missing value reads as FRIENDLY, and
Searing Totem was a damage-over-time the engine believed was a friendly
spell. Nothing reported it: the ability loaded, the tooltip read
correctly, the JSON was well-formed.

HOW MUCH OF THE SLOT RULE IS ACTUALLY ENFORCED, stated honestly, because
it is not all of it. exclusive_group is enforced PER TARGET
(status_effects.py:717 scans the receiving entity's own effect list), and
an ability has no caster-side effect key, so the tag only lands on
whoever the ability targets. Exclusivity therefore holds between totems
that land on the same side:

    Water  FULLY ENFORCED  three party buffs
    Air    FULLY ENFORCED  caster/party
    Fire   Searing and Magma exclude each other on the enemy; Frost
           Resistance is a party buff and is excluded by neither
    Earth  the three ally-facing ones exclude each other; Earthbind is
           enemy-facing and is excluded by none of them

Two leaks, eleven of thirteen totems correctly slotted. They are NOT
closed with a 100%-proc caster-side marker: a party buff puts a copy on
every ally, so a marker sharing the group would strip the SHAMAN's copy of
the resistance buff and leave the party's intact - a worse bug than the
leak. Closing them needs a status effect to know its caster, the same
engine change already queued for the DoT threat gap and for giving Pet a
fire_proc_trigger.

ONE ENGINE FIX CAME OUT OF THIS. The dot branch of the buff/debuff/dot
split never passed exclusive_group through to the StatusEffect it built
(abilities.py:2833), while the buff and debuff branches both did. So no
dot could occupy a slot, and the two Fire damage totems stacked. Found by
live-casting them back to back - not by any audit, all of which passed.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATH = ROOT / "data/abilities/shaman.json"

#: The real 3.3.5a element assignment. Cross-wired on purpose - see the
#: module docstring before "correcting" any of the resistance totems.
EXPECTED = {
    "shaman_strength_of_earth_totem": "earth",
    "shaman_stoneclaw_totem": "earth",
    "shaman_stoneskin_totem": "earth",
    "shaman_earthbind_totem": "earth",
    "shaman_searing_totem": "fire",
    "shaman_magma_totem": "fire",
    "shaman_frost_resistance_totem": "fire",
    "shaman_mana_spring_totem": "water",
    "shaman_mana_tide_totem": "water",
    "shaman_fire_resistance_totem": "water",
    "shaman_windfury_totem": "air",
    "shaman_grounding_totem": "air",
    "shaman_nature_resistance_totem": "air",
}

#: A damage or debuff totem MUST declare an enemy target_type, or
#: abilities.py:199 files it as a friendly spell.
MUST_BE_HOSTILE = {
    "shaman_searing_totem": "enemy",
    "shaman_magma_totem": "enemy_aoe",
    "shaman_earthbind_totem": "enemy_aoe",
}

#: The one totem that is correctly "self": the real Stoneclaw taunts and,
#: with Earth's Grasp, shields the shaman.
ALLOWED_SELF = {"shaman_stoneclaw_totem", "shaman_grounding_totem"}


def main():
    report = "--report" in sys.argv
    abilities = {a["ability_id"]: a
                 for a in json.loads(PATH.read_text())["abilities"]}
    totems = {k: v for k, v in abilities.items() if "totem" in k}

    missing, wrong_slot, wrong_target, untagged = [], [], [], []

    for aid, want in EXPECTED.items():
        a = totems.get(aid)
        if a is None:
            missing.append(aid)
            continue
        got = a.get("exclusive_group")
        if got != f"shaman_totem_{want}":
            wrong_slot.append((aid, want, got))

    for aid in totems:
        if aid not in EXPECTED:
            untagged.append(aid)

    for aid, want in MUST_BE_HOSTILE.items():
        a = totems.get(aid)
        if a is not None and a.get("target_type") != want:
            wrong_target.append((aid, want, a.get("target_type")))

    for aid, a in totems.items():
        if (a.get("target_type") == "self" and aid not in ALLOWED_SELF):
            wrong_target.append((aid, "party/ally (not self)", "self"))

    print(f"  {len(totems)} totem abilities, {len(EXPECTED)} slotted")

    if report:
        byslot = defaultdict(list)
        for aid, slot in EXPECTED.items():
            byslot[slot].append(aid)
        for slot in ("earth", "fire", "water", "air"):
            print(f"\n  {slot.upper()} slot")
            for aid in sorted(byslot[slot]):
                a = totems.get(aid, {})
                tt = a.get("target_type")
                side = ("enemy" if tt in ("enemy", "enemy_aoe")
                        else "ally ")
                print(f"    {aid:34s} {str(tt):10s} {side}")
            sides = {("enemy" if totems.get(x, {}).get("target_type")
                      in ("enemy", "enemy_aoe") else "ally")
                     for x in byslot[slot]}
            print(f"    -> {'FULLY ENFORCED' if len(sides) == 1 else 'PARTIAL - members land on different sides, see docstring'}")

    problems = (len(missing) + len(wrong_slot) + len(wrong_target)
                + len(untagged))
    if not problems:
        print("\n  4 ELEMENT SLOTS INTACT, 0 TOTEMS MISFILED\n\nPASS")
        return 0

    if missing:
        print(f"\n  {len(missing)} SLOTTED TOTEMS NO LONGER EXIST")
        for aid in missing:
            print(f"    {aid}")

    if untagged:
        print(f"\n  {len(untagged)} TOTEMS WITH NO ELEMENT SLOT")
        print("  A new totem needs an element, or it can be up alongside "
              "every other.\n")
        for aid in untagged:
            print(f"    {aid}")

    if wrong_slot:
        print(f"\n  {len(wrong_slot)} TOTEMS IN THE WRONG SLOT")
        print("  Read this file's docstring before 'fixing' a resistance "
              "totem - they are\n  cross-wired in the real game on "
              "purpose.\n")
        for aid, want, got in wrong_slot:
            print(f"    {aid:34s} want shaman_totem_{want:6s} got {got}")

    if wrong_target:
        print(f"\n  {len(wrong_target)} TOTEMS WITH THE WRONG TARGET SIDE")
        print("  A missing or friendly target_type on a damage/debuff "
              "totem makes the engine\n  file it as a friendly spell "
              "(abilities.py:199).\n")
        for aid, want, got in wrong_target:
            print(f"    {aid:34s} want {want:24s} got {got}")

    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
