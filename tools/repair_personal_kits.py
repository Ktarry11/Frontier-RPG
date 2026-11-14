#!/usr/bin/env python3
"""Classify the inert personal-kit abilities. ANALYSIS ONLY - it writes nothing.

WHY --apply IS GONE. This started as an automated repair: read each inert
ability's description, pick a stat_mods key, write it. Reviewing the 28 it
proposed against their own text, a third were wrong, and wrong in ways that
would have been very hard to find later:

  Sondre, "Control, Not Power" - "Sondre's spells DEAL 20% less damage and
  cannot miss" became magic_damage_taken_pct -20, which makes him TAKE 20%
  less. A deliberate drawback silently turned into a defensive buff.

  Ivan, "He Never Hit One" - "enemies he cleaves TAKE 15% more damage" became
  +15% attack power on Ivan. Right number, wrong character, wrong direction.

  Imelda, "Ten Fights a Year" - "8% more healing DONE" became
  healing_taken_pct, which is healing RECEIVED.

  Giorgi, "Completely Unhurried" - "takes 35% less damage AND deals 40% more"
  captured one clause of two.

The descriptions distinguish takes/deals/enemies-deal, carry conditions
("from whichever school last hit him"), stack ("stacking to 40%"), and scope
to the party rather than the caster. A regex over prose cannot tell those
apart, and an ability that LOOKS repaired while delivering the opposite of
its text is worse than one that obviously does nothing.

So this reports and groups; a human writes the mods.


    PYTHONPATH=. python3 tools/repair_personal_kits.py [--all]

Writes nothing. tools/apply_kit_mods.py holds the hand-written table that
actually lands, and tools/qa_kit_mods.py checks the result in real combat.

=============================================================================
WHAT IS WRONG
=============================================================================

Of the 201 personal-kit abilities, 106 are a buff or debuff with EMPTY
stat_mods. They are castable, they consume a turn and a resource, and they do
nothing whatsoever. Their descriptions promise a real effect - "takes 50% less
damage from it", "deals 1% more damage for every 2% of health missing" - and
the engine has nowhere to read that from.

The kits were authored as design first, data second: each ability carries an
"engine:" note saying what the combat engine would need. Many of those notes
describe mechanics the engine genuinely lacks. But many others describe
something the engine ALREADY does, and were left empty anyway.

This pass fills in the ones that are expressible today, taking the magnitude
from the ability's own description so the tooltip and the effect agree.

=============================================================================
UNITS - read this before changing the table
=============================================================================

From claude/value_conventions_and_dead_data_2026_10_29.md, which is the
authority. These are an ABILITY's stat_mods, which is NOT the same channel as
a talent's effects, and several keys mean different things in the two:

    physical_damage_taken_pct, magic_damage_taken_pct, <school>_damage_taken_pct
        PERCENT POINTS here, FRACTION as a talent effect. -50 = 50% less.
    damage_taken_pct            FRACTION, added undivided. -0.5 = 50% less.
    healing_taken_pct           PERCENT POINTS. Negative is the anti-heal.
    threat_generation_pct       PERCENT POINTS here, FRACTION as a talent.
    max_health_pct              FRACTION.
    every other _pct            PERCENT POINTS.

Getting this backwards is the single trap that doc records as causing
"thirteen bugs in one session, including two permanent damage immunities".
A defensive delivering 0.1% instead of 10% fails silently, which is the
direction that survives hand-checking.

WHERE THE MODS GO. A buff's stat_mods fold into the same bonus pool as gear
and talents (entities/character.py, the status-effect loop), so any key the
recalc reads works - not only the eighteen that route through
get_status_stat_mod. That is a much wider palette than the authored kits used.

=============================================================================
WHAT THIS DOES NOT TOUCH
=============================================================================

Abilities whose description needs a mechanic the engine does not have -
redirect a queued attack, swap rows mid-combat, scale a stat by living party
members, reveal enemy intent - are LEFT ALONE and listed at the end. Inventing
a stat_mod that half-expresses them would make the ability look fixed while
still not doing what it says, which is worse than obviously doing nothing.

effect_value 0 is NOT repaired here: combat/abilities.py already treats a zero
scalar with non-empty stat_mods as 100, so once a mod exists the scalar is
handled. Verified before writing this rather than assumed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

SCHOOL_KEYS = {
    "fire": "fire_resistance", "frost": "frost_resistance",
    "nature": "nature_resistance", "shadow": "shadow_resistance",
    "arcane": "arcane_resistance", "holy": "holy_resistance",
}


def pct(text, *patterns):
    """First percentage in the description matching any pattern."""
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            for g in m.groups():
                if g and g.replace(".", "").isdigit():
                    return float(g)
    return None


def propose(desc, effect_type):
    """-> (stat_mods, why) for a description the engine can express, else None.

    Order matters: the most specific reading wins, because "takes 50% less
    damage" and "takes 50% less FIRE damage" want different keys.
    """
    d = desc or ""
    low = d.lower()

    # SCALING DESCRIPTIONS ARE NOT FLAT MODS. "6% less damage for each ally
    # still alive" is not a 6% reduction, it is 6 to 24 depending on the
    # party; "1% more damage for every 2% of health missing" is not +1%.
    # The first version of this tool matched the per-unit number and wrote it
    # as a flat value, which makes an ability LOOK repaired while delivering a
    # quarter of what it promises - exactly the failure this file's docstring
    # says is worse than obviously doing nothing. These need a real scaling
    # hook in the engine, so they are left alone and reported.
    if re.search(r"\bfor each\b|\bfor every\b|\bper (?:ally|turn|stack|enemy|point)\b"
                 r"|\beach (?:ally|turn|stack|enemy)\b|\bup to \d+%", low):
        return None

    # --- damage taken, by school where the text names one
    v = pct(low, r"takes? (\d+)% less damage", r"(\d+)% less damage",
            r"reduced by (\d+)%", r"(\d+)% of (?:the )?damage .* (?:reduced|prevented)")
    if v:
        for school, _key in SCHOOL_KEYS.items():
            if school in low:
                return ({f"{school}_damage_taken_pct": -v},
                        f"takes {v:.0f}% less {school} damage")
        if "magic" in low or "spell" in low:
            return ({"magic_damage_taken_pct": -v}, f"takes {v:.0f}% less magic damage")
        if "melee" in low or "physical" in low:
            return ({"physical_damage_taken_pct": -v}, f"takes {v:.0f}% less physical damage")
        return ({"physical_damage_taken_pct": -v, "magic_damage_taken_pct": -v},
                f"takes {v:.0f}% less damage of either kind")

    # --- outgoing damage
    v = pct(low, r"deals? (\d+)% more damage", r"(\d+)% more damage",
            r"damage .* increased by (\d+)%")
    if v:
        if "spell" in low or "magic" in low:
            return ({"spell_power_pct": v}, f"+{v:.0f}% spell power")
        return ({"attack_power_pct": v}, f"+{v:.0f}% attack power")

    # --- healing received / done
    v = pct(low, r"(\d+)% more healing", r"healing .* increased by (\d+)%",
            r"receives? (\d+)% more")
    if v:
        return ({"healing_taken_pct": v}, f"+{v:.0f}% healing received")

    # --- resistances
    v = pct(low, r"(\d+) (?:points? of )?(?:fire|frost|nature|shadow|arcane|holy) resistance",
            r"resistance by (\d+)")
    if v:
        for school, key in SCHOOL_KEYS.items():
            if school in low:
                return ({key: v}, f"+{v:.0f} {school} resistance")
        return ({"magic_resistance": v}, f"+{v:.0f} magic resistance")

    # --- threat
    v = pct(low, r"(\d+)% (?:more|additional|extra) threat", r"threat by (\d+)%")
    if v:
        sign = -1 if ("less" in low or "reduc" in low) else 1
        return ({"threat_generation_pct": sign * v},
                f"{'+' if sign > 0 else '-'}{v:.0f}% threat")

    # --- crit
    v = pct(low, r"(\d+)% (?:more )?crit", r"critical .* by (\d+)%")
    if v:
        return ({"crit_chance_physical": v, "crit_chance_spell": v},
                f"+{v:.0f}% crit")

    # --- armor
    v = pct(low, r"(\d+)% (?:more )?armou?r", r"armou?r by (\d+)%")
    if v:
        return ({"armor_pct": v}, f"+{v:.0f}% armor")

    # --- haste / speed of action
    v = pct(low, r"(\d+)% (?:more )?haste", r"haste by (\d+)%")
    if v:
        return ({"haste": v}, f"+{v:.0f}% haste")

    # --- cost reduction
    v = pct(low, r"cost(?:s)? (\d+)% less", r"(\d+)% less (?:mana|energy|rage)")
    if v:
        return ({"all_ability_cost_pct": v / 100.0}, f"abilities cost {v:.0f}% less")

    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also list what is left alone")
    args = ap.parse_args()

    doc = json.loads(KITS.read_text(encoding="utf-8"))
    fixed, left = [], []

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            if a.get("effect_type") not in ("buff", "debuff"):
                continue
            if a.get("stat_mods"):
                continue
            got = propose(a.get("description", ""), a.get("effect_type"))
            if got is None:
                left.append((kit.get("name"), a.get("name"),
                             str(a.get("engine", ""))[:58], a.get("description", "")))
                continue
            mods, why = got
            fixed.append((kit.get("name"), a.get("name"), mods, why))

    print(f"  {len(fixed) + len(left)} inert buff/debuff abilities")
    print(f"  {len(fixed)} match a keyword pattern - ALREADY REVIEWED AND "
          f"REJECTED BY HAND")
    print(f"  {len(left)} do not even pattern-match\n")
    print("  The first group is not a to-do list. Each one was read against its\n"
          "  own text and turned down: Marco's and Saoirse's need a damage\n"
          "  redirect, Ivan's and Pieter's and Gianluca's percentages apply to\n"
          "  MONSTER output which has no multiplier, Imelda's and Driss's stack,\n"
          "  Callum's picks a school at runtime, and Sondre's would invert a\n"
          "  deliberate drawback into a buff. See the docstring.\n")

    if fixed:
        print(f"  {'recruit':16}{'ability':30}{'stat_mods':44}why")
        for who, name, mods, why in fixed:
            print(f"  {str(who)[:14]:16}{str(name)[:28]:30}{json.dumps(mods)[:42]:44}{why}")

    if left:
        print(f"\n  LEFT ALONE - {len(left)} abilities whose text needs new engine work:")
        if args.all:
            for who, name, eng, desc in left:
                print(f"    {str(who)[:14]:16}{str(name)[:26]:28}{eng}")
        else:
            print(f"    pass --all to list them")

    print("\n  analysis only - tools/apply_kit_mods.py is what writes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
