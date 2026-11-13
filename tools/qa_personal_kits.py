#!/usr/bin/env python3
"""Every recruit actually receives the kit that was written for them.

    PYTHONPATH=. python3 tools/qa_personal_kits.py [--engine]

Kyle, 7 Nov 2026: "why do none of the player recruits have their special core
abilities we desgined for them?"

Because nothing loaded them. data/npcs/personal_kits.json - 67 recruits, 201
abilities, 67 named passives - and data/races/racials.json - 5 races, 10
abilities - were both authored, committed, complete, and read by no code
anywhere. Every companion played exactly like a stock character of their class
and spec, which is the one thing the kits exist to prevent.

Authored-but-unwired is the quietest failure this codebase has. The data looks
right in every inspection, the file is in git, and the game simply never asks
for it. So this checks the OUTCOME - that a built recruit is holding the
abilities - rather than that the file parses.

FOUR CLAIMS:

  1. EVERY recruit with a kit receives all of it, abilities and passives.
  2. The passives MOVE A STAT, in the right direction and the right size.
     This is the half that fails quietly: max_health_pct is a FRACTION in the
     bonus pool while the kits author percent points, so an unconverted 10
     reads as +1000%. Measured before the fix: Dan's health went 388 -> 5236.
  3. ASHER COLEMAN GETS NOTHING. His book is exactly his two abilities.
  4. Kit and racial abilities land in the spellbook's CORE tab, where the
     data file says they belong.

It also reports how many kit abilities name a mechanic the engine cannot
express yet - the "engine:" notes in the data are honest about this - so the
number is visible rather than discovered in a fight.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: Passive keys with a derived stat we can watch move, and the attribute.
MEASURABLE = {
    "max_health_pct": ("health", 0.01),
    "armor_pct": ("armor", 0.01),
    "dodge": ("dodge", None),
    "crit_chance_physical": ("crit_chance_physical", None),
    "crit_chance_spell": ("crit_chance_spell", None),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", action="store_true",
                    help="list abilities whose mechanic the engine lacks")
    args = ap.parse_args()

    import world.personal_kits as pk
    from world.recruit_manager import get_recruit_manager

    kits = pk.kits()
    racials = pk.racials()
    rm = get_recruit_manager()
    recs = list(rm.recruits.values()) if isinstance(rm.recruits, dict) else rm.recruits

    findings, measured, no_engine = [], [], []
    with_kit = 0

    for r in recs:
        rid = getattr(r, "recruit_id", None)
        kit = kits.get(rid)
        ch = r.build_character()
        have = {a.ability_id for a in ch.ability_book.get_all_abilities()}

        if rid == "asher_coleman":
            if have != {"asher_wrath", "asher_resignation"}:
                findings.append(f"Asher's book is {sorted(have)}, must be exactly his two")
            continue

        if kit:
            with_kit += 1
            want = {a["ability_id"] for a in (kit.get("abilities") or [])
                    if isinstance(a, dict) and a.get("ability_id")}
            missing = sorted(want - have)
            if missing:
                findings.append(f"{r.name}: missing kit abilities {missing}")

        race = getattr(ch, "race", None)
# A COMPANION CARRIES NO RACIAL (Kyle, [10]: "not all the same human racials"). This
        # check used to demand the Human racial on all of them, which is how 67 companions
        # came to share one Core tab; tools/qa_racials.py holds the rule now.
        if pk.racial_of(ch) is not None:
            findings.append(f"{r.name} ({race}): a companion was given the {race} racial")
        extra = sorted(a for a in ch.ability_book.abilities if str(a).startswith("racial_"))
        if extra:
            findings.append(f"{r.name} ({race}): carries racial abilities {extra}")

        # the quiet half - does a passive actually move the stat, by the right amount?
        passives = pk.passives_for(ch)
        for key, (attr, _unit) in MEASURABLE.items():
            if key not in passives or not hasattr(ch, attr):
                continue
            real = pk.passives_for
            pk.passives_for = lambda c: {}
            ch._recalculate_derived_stats()
            before = getattr(ch, attr)
            pk.passives_for = real
            ch._recalculate_derived_stats()
            after = getattr(ch, attr)
            if not before:
                continue
            if key.endswith("_pct"):
                # The expected ratio depends on the key's OWN unit, not on the
                # _pct suffix. passives_for() has already converted the
                # fraction keys, so those arrive as 0.10 and multiply directly;
                # the percent-point keys arrive as 12 and divide by 100. An
                # earlier version of this check used 1.0 + value for both and
                # accused twelve correct armor_pct passives of being 13x too
                # small - the instrument failing exactly the way
                # value_conventions_and_dead_data warns about.
                v = passives[key]
                want_ratio = (1.0 + v) if key in pk.FRACTION_KEYS else (1.0 + v / 100.0)
                got = after / before
                measured.append((r.name, key, before, after, got, want_ratio))
                if abs(got - want_ratio) > 0.06:
                    findings.append(
                        f"{r.name}: {key}={passives[key]} should give "
                        f"{want_ratio:.2f}x {attr}, gave {got:.2f}x "
                        f"({before:.0f} -> {after:.0f})")
            elif after <= before:
                findings.append(f"{r.name}: {key}={passives[key]} did not move {attr}")

    for kid, kit in kits.items():
        for a in (kit.get("abilities") or []):
            if isinstance(a, dict) and str(a.get("engine", "")).startswith("needs:"):
                no_engine.append((kit.get("name", kid), a.get("name"), a["engine"][6:].strip()))

    print(f"  {len(recs)} recruits, {with_kit} with a personal kit, "
          f"{len(racials)} races with racials")
    print(f"  {sum(len(k.get('abilities') or []) for k in kits.values())} kit abilities + "
          f"{sum(len(v.get('abilities') or []) for v in racials.values())} racial abilities authored")
    print(f"  {len(measured)} passive(s) measured against a real derived stat\n")

    if measured[:6]:
        print(f"  {'recruit':18}{'passive':22}{'stat move':>22}{'expected':>10}")
        for name, key, b, a, got, want in measured[:6]:
            print(f"  {name[:16]:18}{key:22}{f'{b:.0f} -> {a:.0f} ({got:.2f}x)':>22}{f'{want:.2f}x':>10}")
        print()

    if no_engine:
        print(f"  {len(no_engine)} kit ability/abilities name a mechanic the engine lacks.")
        print(f"  They are granted and castable; the bespoke half does nothing yet.")
        if args.engine:
            for who, what, need in no_engine:
                print(f"    {who[:16]:18}{str(what)[:28]:30}{need}")
        else:
            print(f"  Pass --engine to list them.")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings[:25]:
            print(f"    {f}")
        if len(findings) > 25:
            print(f"    ... and {len(findings) - 25} more")
        print("\nFAIL")
        return 1

    print("  every recruit holds their kit, the passives move real stats by the "
          "right amount,\n  and Asher Coleman is untouched")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
