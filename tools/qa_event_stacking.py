#!/usr/bin/env python3
"""A stack earned from an event is earned once per event, and caps.

    PYTHONPATH=. python3 tools/qa_event_stacking.py [--list]

=============================================================================
WHAT THIS GUARDS
=============================================================================

StatusEffect has supported max_stacks and per-stack stat_mods all along.
What was missing is anything that ADDS a stack when something happens, so
three kit abilities had no way to be expressed:

    Imelda, "each attack that lands gives her 8% more healing done,
             stacking to 40%"
    Nizar,  "each repeat of the same spell deals 15% more, to 75%"
    Driss,  "the target takes 15% more damage each time it REPEATS an
             ability, stacking to 45%"

Driss's sits on the ENEMY, so the enemy repeating is what feeds it - one
trigger serving both directions, which is why this suite drives a Monster as
well as a Character.

=============================================================================
THE THREE WAYS THIS GOES WRONG, ALL OF WHICH LOOK FINE
=============================================================================

1. THE FIRST STACK IS FREE. The ordinary convention is that an effect exists
   at 1 stack, but for one whose stacks are EARNED the first stack is the
   thing the player works for. Imelda showed 16% after her first attack
   because the buff landed at 1 stack and the attack added another - every
   one of these abilities sat permanently one stack ahead of its own
   tooltip. An earned effect starts at ZERO.

2. A PROC BREAKS THE CHAIN. A proc fires its own ability through
   Ability.use, so a random proc landing between two casts of the same spell
   makes them look like two different abilities and the repeat stack is
   never earned. This produced a DIFFERENT stack count on every single run,
   which is the part that matters: a test that ran once would have passed.
   The fix is the `free` flag - a proc cast is free, a deliberate one is not
   - after a re-entrancy guard was tried and did NOT work, because the proc
   fires from inside _apply_effect and still recorded itself first.

   So this suite runs the repeat sequence SEVERAL TIMES and requires every
   run to agree. One run proves nothing here.

3. THE CAP IS READ AS A PERCENTAGE. stat_mods are per stack, so Nizar's
   "stacking to 75%" is 15 per stack with max_stacks 5 - not max_stacks 75,
   which would be +1125% damage.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

#: A proc is random, so one pass proves nothing. Every pass must agree.
RUNS = 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    from entities.monster import Monster
    from world.recruit_manager import get_recruit_manager

    findings, rows = [], []
    doc = json.loads(KITS.read_text(encoding="utf-8"))
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict)
                      else rm.recruits)}

    def topup(c):
        for res in ("mana", "rage", "energy", "focus"):
            for at in (f"max_{res}", f"current_{res}", res):
                if isinstance(getattr(c, at, None), (int, float)):
                    setattr(c, at, 99999)

    authored = 0
    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            trigger = a.get("stack_on")
            if not trigger:
                continue
            authored += 1
            who = f"{kit.get('name')} / {a.get('name')}"
            cap = a.get("max_stacks") or 1
            mods = a.get("stat_mods") or {}

            # the cap is a stack count, not a percentage
            if cap > 20:
                findings.append(f"{who}: max_stacks {cap} is a STACK COUNT, "
                                f"not a percentage - stat_mods are per stack")
            per = max((abs(v) for v in mods.values()
                       if isinstance(v, (int, float))), default=0)
            if per and per * cap > 200:
                findings.append(f"{who}: {per} per stack x {cap} stacks is "
                                f"{per * cap}% at full stacks")

            r = recs.get(kid)
            if r is None:
                findings.append(f"{who}: no recruit {kid!r}")
                continue
            key = next((k for k in mods), None)
            if key is None:
                findings.append(f"{who}: stack_on with no stat_mods to stack")
                continue

            sequences = []
            for _ in range(RUNS):
                g = r.build_character()
                g.level = 60
                try:
                    g.recalculate_stats()
                except Exception:
                    pass
                ab = next((x for x in g.ability_book.get_all_abilities()
                           if x.ability_id == a["ability_id"]), None)
                if ab is None:
                    findings.append(f"{who}: not granted")
                    break
                topup(g)
                ab.turns_remaining = 0
                hostile = ab.target_type in ("enemy", "enemy_aoe", "all_enemies")
                foe = Monster("T", "beast_basic", level=60)
                ab.use(g, foe if hostile else g, party=[g], in_combat=True)
                holder = foe if hostile else g
                eff = next((e for e in holder._effects()
                            if e.effect_id == a["ability_id"]), None)
                if eff is None:
                    findings.append(f"{who}: the cast applied no effect")
                    break

                # AN EARNED COUNT STARTS AT ZERO
                if eff.stacks != 0:
                    findings.append(f"{who}: lands at {eff.stacks} stacks - an "
                                    f"earned stack must start at 0, or the "
                                    f"first one is free")
                if eff.max_stacks != cap:
                    findings.append(f"{who}: effect max_stacks {eff.max_stacks}, "
                                    f"authored {cap}")

                seq = []
                if hostile:
                    # the enemy repeating one ability is what feeds it
                    for _i in range(cap + 2):
                        holder.note_ability_used("Cleave", True)
                        seq.append(eff.stacks)
                else:
                    dmg = next((x for x in g.ability_book.get_all_abilities()
                                if x.effect_type in ("damage", "spell_damage")),
                               None)
                    if dmg is None:
                        findings.append(f"{who}: no damaging ability to drive it")
                        break
                    for _i in range(cap + 2):
                        dmg.turns_remaining = 0
                        topup(g)
                        dmg.use(g, Monster("T", "beast_basic", level=60),
                                party=[g], in_combat=True)
                        seq.append(eff.stacks)
                sequences.append(tuple(seq))

            if not sequences:
                continue

            # EVERY RUN MUST AGREE - this is the proc bug
            if len(set(sequences)) != 1:
                findings.append(
                    f"{who}: the stack sequence differs between runs "
                    f"{sorted(set(sequences))[:3]} - something random "
                    f"(a proc) is breaking the chain")
            seq = sequences[0]
            rows.append((kit.get("name"), a.get("name"), trigger,
                         f"{seq}", f"cap {cap}"))

            if max(seq) != cap:
                findings.append(f"{who}: reached {max(seq)} stacks of {cap} "
                                f"over {len(seq)} events")
            if any(b - x > 1 for x, b in zip(seq, seq[1:])):
                findings.append(f"{who}: gained more than one stack from a "
                                f"single event: {seq}")

    print(f"  {authored} ability/abilities author an event stack trigger")
    print(f"  each driven {RUNS} times, every run required to agree\n")

    if args.list:
        print(f"  {'recruit':17}{'ability':30}{'on':9}{'stacks per event':28}cap")
        for a, b, c, d, e in rows:
            print(f"  {str(a)[:15]:17}{str(b)[:28]:30}{c:9}{d:28}{e}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings:
            print(f"    {f}")
        print("\nFAIL")
        return 1

    print("  earned stacks start at zero, gain one per event, cap where the "
          "tooltip says,\n  and do the same thing on every run")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
