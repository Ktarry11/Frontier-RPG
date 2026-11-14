#!/usr/bin/env python3
"""Give the Shaman the four real totem element slots, and fix two bugs.

    PYTHONPATH=. python3 tools/fix_shaman_totems.py [--dry-run]

KYLE'S REPORT, 5 Nov 2026: "totems are weird for shaman". They were, in
three separate ways, and only one of them is a design gap.

BUG 1 - TWO DAMAGE TOTEMS ARE CLASSED AS FRIENDLY SPELLS. Searing Totem
and Earthbind Totem carry no target_type at all. abilities.py:199 decides
friend from foe with

    target_type not in ("enemy", "enemy_aoe")

so a missing target_type reads as FRIENDLY. Searing Totem is a spell_dot -
a damage-over-time - that the engine believes is a friendly spell, and
Earthbind is a debuff in the same position. This is the worst of the three
because nothing reports it: the ability loads, the tooltip reads
correctly, and the data is well-formed.

BUG 2 - MANA TIDE TOTEM ONLY HELPS THE SHAMAN. Ours is target_type "self".
The real 3.3.5a spell, quoted from Spell.dbc via
data/reference/wotlk/shaman.json, is explicit:

    "Summons a Mana Tide Totem ... that restores 6% of total mana every
     3 seconds to GROUP MEMBERS within 30 yards."

A Restoration shaman's signature raid cooldown that refills only its own
mana is simply the wrong spell. Stoneclaw Totem stays "self" on purpose -
the real one taunts and, with Earth's Grasp, shields the shaman - so it is
the one "self" totem that is correct.

THE DESIGN GAP - THERE ARE NO ELEMENT SLOTS. Real WoW gives the shaman
four totem slots, Earth / Fire / Water / Air, and one totem per slot;
dropping a new one replaces whatever occupied that slot. Ours models none
of this, so all thirteen totems can be up at once. That is why the three
resistance totems looked like a balance problem (90 magic resistance each,
270 across three schools, against a game whose rule is no magic resistance
gear before level 45) - but the stacking is not the bug. In the real game
all three resistances CAN be up at once; it costs you the Fire, Water and
Air slots, so you give up Searing/Magma, Mana Spring/Mana Tide and
Windfury/Grounding to get them. That trade is one of the better decisions
in the class, and once slots exist the "problem" turns back into the
choice it was meant to be.

THE REAL ELEMENT ASSIGNMENT, which is deliberately cross-wired in WoW and
is not a transcription error here: Frost Resistance is a FIRE totem, Fire
Resistance is a WATER totem, Nature Resistance is an AIR totem. Each
resistance sits in the element that opposes the school it resists.

    Earth  Strength of Earth, Stoneclaw, Stoneskin, Earthbind
    Fire   Searing, Magma, Frost Resistance
    Water  Mana Spring, Mana Tide, Fire Resistance
    Air    Windfury, Grounding, Nature Resistance

HOW FAR THE ENGINE CAN ENFORCE THIS, stated exactly, because it is not all
the way. exclusive_group is enforced PER TARGET: status_effects.py:717
scans the effect list of the entity being applied to and drops any
existing member of the same group. An ability's exclusive_group therefore
only lands on whoever that ability targets, and abilities have no
caster-side effect key - the loader reads no self_buff/caster_effect
field, and the only on_target control in the engine lives inside a proc's
apply_effect.

So exclusivity holds between totems that land on the same side:

    Water  FULLY ENFORCED  all three are party buffs
    Air    FULLY ENFORCED  all three land on the caster or the party
    Earth  the three ally-facing ones exclude each other; Earthbind is
           enemy-facing and is not excluded by them
    Fire   Searing and Magma exclude each other on the enemy; Frost
           Resistance is a party buff and is not excluded by either

That leaves exactly two leaks - Earthbind alongside an Earth buff, and
Frost Resistance alongside a fire damage totem - and eleven of thirteen
totems correctly slotted. The leaks are NOT papered over with a 100%-proc
marker on the caster, which was tried and rejected: a party buff puts a
copy on every ally, so a caster-side marker sharing the group would strip
the SHAMAN's copy of the resistance buff and leave the party's intact.
That is a worse and much more confusing bug than the leak it closes.

Closing them properly needs a status effect to know its caster, which is
the same engine change already queued for the DoT threat gap and for
giving Pet a fire_proc_trigger (claude/engine_findings_2026_11_06.md) -
threading a (caster, engine) pair through StatusEffect. Three problems,
one fix; this makes it four.

tools/qa_shaman_totem_slots.py pins the assignment so it cannot drift.
"""

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATH = ROOT / "data/abilities/shaman.json"

#: The real 3.3.5a element assignment. See the module docstring for why
#: the resistance totems look misfiled and are not.
SLOTS = {
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

#: Bug fixes, each with the reason recorded onto the ability's _source.
TARGET_FIXES = {
    "shaman_searing_totem": (
        "enemy",
        "target_type was ABSENT, and abilities.py:199 reads a missing "
        "target_type as friendly (anything not in enemy/enemy_aoe). A "
        "spell_dot the engine believed was a friendly spell. Set to "
        "'enemy' - the real Searing Totem attacks one target at a time."),
    "shaman_earthbind_totem": (
        "enemy_aoe",
        "target_type was ABSENT, same friendly-by-default bug as Searing "
        "Totem. Set to 'enemy_aoe' - the real Earthbind Totem pulses an "
        "area snare rather than hitting one target."),
    "shaman_mana_tide_totem": (
        "party",
        "was target_type 'self', which made a Restoration shaman's "
        "signature mana cooldown refill only its own bar. The real 3.3.5a "
        "spell restores mana 'to group members within 30 yards' - quoted "
        "from Spell.dbc via data/reference/wotlk/shaman.json."),
}

SLOT_NOTE = (
    "Element slot '{slot}' added 6 Nov 2026 as exclusive_group "
    "'shaman_totem_{slot}', giving the real one-totem-per-element rule. "
    "Enforcement is per-target (status_effects.py:717), so it holds "
    "against same-element totems that land on the same side - see "
    "tools/fix_shaman_totems.py for the two documented leaks.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(PATH.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    changed = []

    for a in data["abilities"]:
        aid = a["ability_id"]
        if aid not in SLOTS:
            continue
        slot = SLOTS[aid]
        notes = []

        if a.get("exclusive_group") != f"shaman_totem_{slot}":
            a["exclusive_group"] = f"shaman_totem_{slot}"
            notes.append(SLOT_NOTE.format(slot=slot))
            changed.append((aid, "slot", slot))

        if aid in TARGET_FIXES:
            want, why = TARGET_FIXES[aid]
            if a.get("target_type") != want:
                was = a.get("target_type")
                a["target_type"] = want
                notes.append(why)
                changed.append((aid, "target_type", f"{was} -> {want}"))

        if notes:
            a["_source"] = (a.get("_source", "").rstrip() + " "
                            + " ".join(notes)).strip()

    if not changed:
        print("  nothing to change")
        return 0

    print(f"  {len(changed)} changes")
    for aid, kind, what in changed:
        print(f"    {aid:34s} {kind:12s} {what}")

    if args.dry_run:
        print("\n  --dry-run, nothing written")
        return 0

    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\n  wrote {PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
