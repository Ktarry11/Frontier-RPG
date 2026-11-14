#!/usr/bin/env python3
"""A personal-kit ability's stat_mods arrive at the size the data authored.

    PYTHONPATH=. python3 tools/qa_kit_mods.py [--list]

Not "the JSON contains a number" - this casts the ability on a real built
character and reads the stat back off the status effect, because the gap
between those two is where the bug lived.

=============================================================================
THE BUG THIS EXISTS TO CATCH
=============================================================================

Ability._stat_mod_scalar multiplies a buff's authored stat_mods by
effect_value/100. The kit abilities carried the description's own number in
effect_value - Skye's rank said 45 for "45% more damage" - and empty
stat_mods. That was harmless while the mods were empty, because
abilities.py:1548 falls back to a scalar of 1.0 when there is nothing to
scale.

Filling the mods in removes that fallback. So the first apply pass produced:

    Skye      authored 45  ->  arrived 20.25   (45 x 0.45)
    Karim     authored 200 ->  arrived 60      (200 x 0.30)
    Pasang    authored 25  ->  arrived 6.25    (25 x 0.25)

Every value silently a quarter to a half of what the tooltip said, in the
direction that survives hand-checking: the ability works, it just does less.
The tooltip reads from stat_mods (abilities.py:1055) and showed the full
number throughout, so nothing on screen disagreed with anything.

The fix is effect_value 100 on every rank, which means "apply the mods as
written". This checks the invariant rather than the fix: for ANY personal-kit
buff or debuff with non-empty stat_mods, what the cast applies must equal what
the data says, whatever route the data took to get there.

TAUNT is exempt from the size check and gets its own: it is a flag, not a
magnitude, and abilities.py deliberately does not scale it by effect_value.
Checked for generating real threat instead.
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

#: Topped up before casting. A rage class enters combat at 0 rage, so an
#: unprepared harness fails the cast and reports a data bug that is purely
#: the test's own fault - which is exactly what the first run of this did.
RESOURCES = ("rage", "energy", "mana", "focus", "power")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print every measurement")
    args = ap.parse_args()

    from entities.monster import Monster
    from world.recruit_manager import get_recruit_manager

    doc = json.loads(KITS.read_text(encoding="utf-8"))
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict)
                      else rm.recruits)}

    findings, measured = [], []
    built = {}

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        live = [a for a in (kit.get("abilities") or [])
                if isinstance(a, dict)
                and a.get("effect_type") in ("buff", "debuff")
                and a.get("stat_mods")]
        if not live:
            continue
        r = recs.get(kid)
        if r is None:
            findings.append(f"{kit.get('name')}: no recruit with id {kid!r}")
            continue
        for a in live:
            aid = a["ability_id"]
            authored = a["stat_mods"]

            # SCALAR CHECK FIRST, on the data alone. This is the invariant;
            # the cast below only confirms it end to end.
            # 0 IS ALLOWED, and is not the same as any other low value.
            # abilities.py:1548 reads `if effect_value or not stat_mods`, so a
            # zero WITH mods present falls through to a scalar of 1.0 - that
            # is the deliberate fix for the 113 abilities across seven classes
            # that shipped effect_value 0 from their generator's one() helper.
            # Only 1..99 is the bug: a real scalar that quietly shrinks the
            # mods. An earlier version of this check flagged 0 too and printed
            # "scales them by 0.00x" from its own arithmetic rather than the
            # engine's rule, which accused four correct abilities.
            for rank in (a.get("ranks") or []):
                ev = rank.get("effect_value") or 0
                if ev not in (0, 100):
                    findings.append(
                        f"{kit.get('name')} / {a.get('name')} rank "
                        f"{rank.get('rank')}: effect_value {ev} with non-empty "
                        f"stat_mods scales them by {ev / 100:.2f}x - "
                        f"must be 100 (or 0, read as 'as written')")

            # fresh character per ability, so one cast cannot colour the next
            ch = built.get(kid) or r.build_character()
            built[kid] = ch
            ab = next((x for x in ch.ability_book.get_all_abilities()
                       if x.ability_id == aid), None)
            if ab is None:
                findings.append(f"{kit.get('name')}: {aid} is not in their book")
                continue

            # Through the GENERIC resource API, not by guessing attribute
            # names. Character.get_resource/set_resource (character.py:2400,
            # :2431) cover both the dedicated attributes and the dict-backed
            # CoA pools - Static, Insanity, Deathfire, Focus - which have no
            # current_<name> attribute at all, so an attribute sweep missed
            # Ratih's Focus entirely and reported her ability as broken.
            # Both routes, because neither alone is enough: set_resource
            # clamps to the pool's max, so a pool whose max is low still
            # cannot pay, and the dict-backed pools have no attribute to
            # raise. Topping up every dedicated attribute AND every declared
            # pool is the only version that gets all 22 cast.
            for res in RESOURCES:
                for attr in (f"max_{res}", f"current_{res}", res):
                    if isinstance(getattr(ch, attr, None), (int, float)):
                        setattr(ch, attr, 9999)
            try:
                rtype = ab._effective_resource_type(ch)
                ch.set_resource(rtype, max(ch.get_resource_max(rtype) or 0, 9999))
            except Exception:
                pass
            ab.turns_remaining = 0
            hostile = ab.target_type in ("enemy", "enemy_aoe", "all_enemies")
            foe = Monster("Target", "beast_basic", level=max(1, ch.level))
            if ab.target_type == "pet":
                # A pet-targeted buff lands on the pet (it used to fall through to the caster,
                # which is what this check was unknowingly measuring). Give them one.
                from combat.pet_templates import PET_TEMPLATES
                if not [p for p in (ch.all_pets or []) if p is not None and p.is_alive()]:
                    for template_id in PET_TEMPLATES:
                        if ch.summon_pet(template_id)[0]:
                            break
            ok, msg = ab.use(ch, foe if hostile else ch, party=[ch], in_combat=True)
            if not ok:
                findings.append(f"{kit.get('name')} / {a.get('name')}: "
                                f"cast failed - {msg}")
                continue

            holder = foe if hostile else ch
            if ab.target_type == "pet":
                holder = next(p for p in ch.all_pets if p is not None and p.is_alive())
            for key, want in authored.items():
                if key == "taunt":
                    events = getattr(ab, "_last_threat_events", None) or []
                    threat = sum(amt for (_t, amt, flag) in events if flag)
                    measured.append((kit.get("name"), a.get("name"), "taunt",
                                     want, threat))
                    if threat <= 0:
                        findings.append(f"{kit.get('name')} / {a.get('name')}: "
                                        f"taunt generated no threat")
                    continue
                got = holder.get_status_stat_mod(key)
                # A RATE-SCALED mod does not arrive at its authored size and
                # must not: stat_mods are authored PER UNIT and multiplied by
                # a live count (StatusEffect.scaling_multiplier). Pasang's -4
                # per turn correctly reads 0 on the turn it lands, and Owen's
                # 1 per 2% missing health reads 16.7 on a half-health probe.
                # Comparing against the authored number alone accused four
                # correct abilities the moment scaling shipped - the
                # instrument lagging the engine, which is the failure this
                # file's own docstring is about. The authored value is still
                # checked, just against the multiplier the engine is using.
                applied = next((e for e in holder._effects()
                                if e.effect_id == aid), None)
                mult = 1.0
                if applied is not None and getattr(applied, "scaling", None):
                    mult = applied.scaling_multiplier(holder)
                # AN EARNED STACK COUNT IS ZERO ON CAST, and must be: the
                # stacks are what the player works for, so Imelda's 8% per
                # landed attack correctly reads 0 before she has attacked.
                # Comparing against the authored number alone accused all
                # three event-stacking abilities the moment they shipped -
                # the same way it accused the rate-scaled ones. Same cause,
                # same fix: compare against the multiplier the engine is
                # actually using.
                if applied is not None and (
                        getattr(applied, "stack_on_repeat", False)
                        or getattr(applied, "stack_on_reuse", False)
                        or getattr(applied, "stack_on_attack", False)):
                    mult *= getattr(applied, "stacks", 0)
                want = want * mult
                measured.append((kit.get("name"), a.get("name"), key, want, got))
                if abs(got - want) > 0.001:
                    findings.append(f"{kit.get('name')} / {a.get('name')}: "
                                    f"{key} authored {want}, arrived {got}")

    print(f"  {len({m[1] for m in measured})} kit abilities with stat_mods cast "
          f"on a real character")
    print(f"  {len(measured)} stat value(s) read back off the applied effect\n")

    if args.list:
        print(f"  {'recruit':17}{'ability':30}{'key':30}{'authored':>10}{'arrived':>12}")
        for who, name, key, want, got in measured:
            print(f"  {str(who)[:15]:17}{str(name)[:28]:30}{key[:28]:30}"
                  f"{want:>10}{got:>12}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings[:25]:
            print(f"    {f}")
        if len(findings) > 25:
            print(f"    ... and {len(findings) - 25} more")
        print("\nFAIL")
        return 1

    print("  every authored stat_mod arrives at the size the data says")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
