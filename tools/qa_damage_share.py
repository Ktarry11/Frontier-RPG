#!/usr/bin/env python3
"""A guardian really soaks the share of a hit their ability promises.

    PYTHONPATH=. python3 tools/qa_damage_share.py [--list]

=============================================================================
WHAT THIS GUARDS
=============================================================================

Seven personal-kit abilities are written as one character taking damage
aimed at someone else:

    Pasang,  "absorbs 30% of all damage dealt to the party"
    Nicolas, "takes 35% of all damage dealt to the party in their place"
    Elias,   "takes 30% ... and heals for a tenth of what he absorbs"
    Marco,   "damage dealt to the chosen ally is redirected to Marco,
              reduced by 33%"
    Saoirse, "takes every blow aimed at the chosen ally, reduced by 40%"
    Dan,     "the NEXT attack aimed at any ally is redirected to Dan"  x2

take_damage runs on the VICTIM, and a victim has no way to reach whoever is
protecting them - the party lives on CombatEngine, which is not reachable
from inside a damage calculation. So the buff is applied to each recipient
separately and every copy carries a reference back to the caster. That is
the part a data inspection cannot see, and it is what this measures.

THREE THINGS THAT WOULD BE WRONG AND LOOK FINE:

1. THE DISCOUNT APPLIED TO THE WRONG SIDE. "Redirected to Marco, reduced by
   33%" means the ally loses the WHOLE blow and Marco pays two thirds. A
   reading where the ally keeps a third turns a full redirect into a partial
   one, and the ally's health still goes down less than before, so it looks
   like it works.

2. DOUBLE MITIGATION. The share has already been through the victim's
   armour, resistances, level difference, block and every
   damage_taken_pct on them. Routing it through the guardian's take_damage
   would mitigate it a second time, so a tank soaking 30% would feel far
   less than 30% - and it would recurse, because a shared hit re-enters
   take_damage.

3. A DEAD GUARDIAN EATING HITS. Writing the test naively hides this: a
   guardian soaking 100% of repeated hits DIES partway through, after which
   the share correctly stops. An earlier version of this check measured a
   running total across many hits and reported Saoirse at 17% instead of
   60% - the guardian had died on hit three. Each claim here is measured on
   ONE landed hit, retrying past dodge and parry rolls, which is also why
   it does not use a fixed number of swings.
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

#: A dodge or parry means a swing carries no information, so each claim is
#: retried until one lands rather than averaged over a fixed count.
MAX_SWINGS = 30
HIT = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    from entities.character import Character
    from combat.status_effects import StatusEffect, EffectType
    from world.recruit_manager import get_recruit_manager

    findings, rows = [], []

    # ---- 1. the primitive, in isolation -----------------------------------
    def duo():
        t = Character("Tank", "Warrior", 60)
        a = Character("Ally", "Priest", 60)
        t.current_health, a.current_health = t.health, a.health
        return t, a

    def attach(ally, tank, **kw):
        e = StatusEffect("sh", "Share", EffectType.BUFF, 4, stat_mods={},
                         source_name="T")
        e.damage_share_to = tank
        for k, v in kw.items():
            setattr(e, f"damage_share_{k}", v)
        ally.apply_status_effect(e)
        return e

    def one_landed_hit(setup):
        """(guardian_paid, ally_lost) for a single hit that actually landed."""
        for _ in range(MAX_SWINGS):
            tank, ally = duo()
            setup(ally, tank)
            tb, ab = tank.current_health, ally.current_health
            ally.take_damage(HIT, "physical", attacker_level=60)
            paid, lost = tb - tank.current_health, ab - ally.current_health
            if paid or lost:
                return paid, lost
        return None, None

    # a dead guardian must share nothing - the hit stays where it landed
    def dead_guardian(ally, tank):
        attach(ally, tank, pct=50)
        tank.current_health = 0
    paid, lost = one_landed_hit(dead_guardian)
    rows.append(("dead guardian", "pct=50", paid, lost, "guardian 0, ally all"))
    if paid:
        findings.append(f"a DEAD guardian still paid {paid} - a downed "
                        f"protector must not soak anything")
    if not lost:
        findings.append("with a dead guardian the hit vanished instead of "
                        "staying with the victim")

    # a guardian cannot soak for themselves
    for _ in range(MAX_SWINGS):
        tank, _a = duo()
        e = StatusEffect("self", "Self", EffectType.BUFF, 4, stat_mods={},
                         source_name="T")
        e.damage_share_to = tank
        e.damage_share_pct = 100
        tank.apply_status_effect(e)
        before = tank.current_health
        tank.take_damage(HIT, "physical", attacker_level=60)
        if before != tank.current_health:
            break
    else:
        findings.append("a self-targeted share never produced a landed hit")
    rows.append(("self-share", "pct=100", "n/a", before - tank.current_health,
                 "takes it normally"))
    if tank.current_health == before and before > 0:
        findings.append("a guardian soaked a hit for THEMSELVES - that is an "
                        "immunity, not a redirect")

    # mutual guardians must not loop forever
    try:
        a, b = duo()
        attach(a, b, pct=50)
        attach(b, a, pct=50)
        a.take_damage(HIT, "physical", attacker_level=60)
        rows.append(("mutual pair", "both pct=50", "-", "-", "no recursion"))
    except RecursionError:
        findings.append("two guardians protecting each other recursed - the "
                        "_sharing_damage guard is not holding")

    # ---- 2. every authored spec, on the real recruit -----------------------
    doc = json.loads(KITS.read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict)
                      else rm.recruits)}
    authored = 0
    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            spec = a.get("damage_share")
            if not spec:
                continue
            authored += 1
            who = f"{kit.get('name')} / {a.get('name')}"
            pct = spec.get("pct", 0)
            red = spec.get("reduction_pct", 0)
            if not 0 < pct <= 100:
                findings.append(f"{who}: damage_share pct {pct} is outside 1-100")
            if not 0 <= red < 100:
                findings.append(f"{who}: reduction_pct {red} is outside 0-99")
            r = recs.get(kid)
            if r is None:
                findings.append(f"{who}: no recruit {kid!r}")
                continue

            def setup(ally, guardian, _r=r, _aid=a["ability_id"]):
                g = _r.build_character()
                g.level = 60
                try:
                    g.recalculate_stats()
                except Exception:
                    pass
                ab = next((x for x in g.ability_book.get_all_abilities()
                           if x.ability_id == _aid), None)
                if ab is None:
                    return None
                for res in ("mana", "rage", "energy", "focus"):
                    for at in (f"max_{res}", f"current_{res}", res):
                        if isinstance(getattr(g, at, None), (int, float)):
                            setattr(g, at, 99999)
                try:
                    g.set_resource(ab._effective_resource_type(g), 99999)
                except Exception:
                    pass
                g.current_health = g.health
                ab.turns_remaining = 0
                ab.use(g, ally if ab.target_type == "ally" else [g, ally],
                       party=[g, ally], in_combat=True)
                # hand the real guardian back to the measuring loop
                setup.guardian = g
                return g

            # EXACT ARITHMETIC, deterministically. Inferring the original
            # hit from paid+lost only works while the victim still loses
            # something: at pct=100 the ally loses 0, so paid+lost IS the
            # already-reduced share and an expected value derived from it
            # halves a halved number. An earlier version of this check did
            # exactly that and "failed" Dan, Marco and Saoirse while the
            # engine was right.
            #
            # So the share maths is measured by calling _share_damage_out
            # with a known amount - no armour, no block, no dodge roll - and
            # what the real ability is checked for is that it puts the
            # authored spec onto the recipient at all.
            tank, ally = duo()
            g = setup(ally, tank)
            if g is None:
                findings.append(f"{who}: ability not granted to them")
                continue
            applied = next((e for e in ally._effects()
                            if getattr(e, "damage_share_to", None) is not None),
                           None)
            if applied is None:
                findings.append(f"{who}: cast put no damage_share effect on "
                                f"the ally - the spec never reached the engine")
                continue
            if applied.damage_share_to is not g:
                findings.append(f"{who}: the share points at "
                                f"{getattr(applied.damage_share_to, 'name', None)!r}, "
                                f"not at the caster")
            for field, key in (("damage_share_pct", "pct"),
                               ("damage_share_reduction_pct", "reduction_pct"),
                               ("damage_share_heal_pct", "heal_pct"),
                               ("damage_share_uses", "uses")):
                want = spec.get(key, 0 if key != "uses" else None)
                have = getattr(applied, field, None)
                if have != want:
                    findings.append(f"{who}: {field} arrived {have!r}, "
                                    f"authored {want!r}")

            # Sized to the GUARDIAN, not a round number. A guardian can
            # only pay what they have - the subtraction floors at 0 - so a
            # 1000-damage probe against Dan's ~490 health clamped at his
            # health and the check "failed" a correct full redirect. That
            # floor is right (a redirect can kill the protector; it cannot
            # take him below zero), so the probe stays well inside it.
            AMOUNT = max(50, int(g.current_health * 0.25))
            gb = g.current_health
            left = ally._share_damage_out(AMOUNT, "physical", None)
            paid = gb - g.current_health
            want_left = AMOUNT * (100 - pct) / 100.0
            want_paid = AMOUNT * pct / 100.0 * (100 - red) / 100.0
            want_paid *= (100 - spec.get("heal_pct", 0)) / 100.0
            rows.append((kit.get("name"), a.get("name"), paid, left,
                         f"want guardian {want_paid:.0f}, victim keeps "
                         f"{want_left:.0f}"))
            if abs(left - want_left) > 2:
                findings.append(f"{who}: victim kept {left}, want "
                                f"{want_left:.0f} (pct={pct})")
            if abs(paid - want_paid) > 2:
                findings.append(f"{who}: guardian paid {paid}, want "
                                f"{want_paid:.0f} (pct={pct}, reduction={red}, "
                                f"heal={spec.get('heal_pct', 0)})")

    print(f"  {authored} ability/abilities author a damage_share spec")
    print(f"  {len(rows)} measurement(s), each on ONE landed hit\n")

    if args.list:
        print(f"  {'who':17}{'what':28}{'guardian':>10}{'ally':>8}  expected")
        for a, b, c, d, e in rows:
            print(f"  {str(a)[:15]:17}{str(b)[:26]:28}{str(c):>10}{str(d):>8}  {e}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings:
            print(f"    {f}")
        print("\nFAIL")
        return 1

    print("  every guardian soaks the share their ability promises, the "
          "discount lands on\n  the guardian rather than the victim, and a "
          "downed guardian soaks nothing")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
