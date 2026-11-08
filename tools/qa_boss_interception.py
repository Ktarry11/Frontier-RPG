#!/usr/bin/env python3
"""A BOSS can use the five interception hooks, not just a player.

    PYTHONPATH=. python3 tools/qa_boss_interception.py [--list]

=============================================================================
WHY THIS EXISTS SEPARATELY FROM qa_damage_interception.py
=============================================================================

Character and Monster have entirely separate take_damage implementations.
A defensive mechanic added to one is invisible to the other, and that is not
a hypothetical: of 358 bosses, each with its own unique kit, 0 could stun, 0
carried a shield and 1 applied anything dispellable, while the player side
grew a dozen mechanics. The variety was in the ability NAMES.

These five were written on Character first, which was the wrong home. They
now live on StatusEffectMixin, which both classes inherit, rather than being
copied into monster.py - two copies of one rule is exactly what produced the
stacks-vs-pool drift recorded in value_conventions_and_dead_data.

So the player-side suite passing says nothing about the boss side. This
checks the boss side specifically, on a real Monster, through real
take_damage calls.

TWO NAMING DIFFERENCES the mixin papers over, and either would break this
silently:

  - MAXIMUM HEALTH is Character.health but Monster.max_health. A hook that
    reads .health on a Monster gets 0 (Monster has no such attribute), so
    every percentage-based floor and threshold would compute to zero and
    quietly never fire. _max_hp() is why that does not happen, and the
    percentage cases below are what prove it.
  - _pending_proc_messages exists on Character always and is built lazily on
    Monster, so a hook appending to it directly raises AttributeError on a
    boss. _note_proc() handles both.

PROBED WITH MAGIC DAMAGE. Dodge, parry and block are physical-only here, so
a physical probe makes every one of these checks flaky - a dodged lethal
blow leaves the victim at full health, which looks exactly like a death
floor that failed to fire. Six consecutive runs of the player-side suite
failed differently for that reason before it was switched over.
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    from entities.character import Character
    from entities.monster import Monster
    from combat.status_effects import StatusEffect, EffectType, StatusEffectMixin

    findings, rows = [], []

    def boss(name="Boss"):
        m = Monster(name, "beast_basic", level=60)
        m.is_boss = True
        m.current_health = m.max_health
        return m

    def arm(holder, eid, name, **fields):
        e = StatusEffect(eid, name, EffectType.BUFF, 5, stat_mods={},
                         source_name="Boss")
        for k, v in fields.items():
            setattr(e, k, v)
        holder.apply_status_effect(e)
        return e

    # ---- 0. the hooks are actually ON the shared mixin --------------------
    for m in ("_share_damage_out", "_prevent_death", "_reflect_damage",
              "_check_low_health_trigger", "_convert_damage_to_shield",
              "_max_hp", "_note_proc"):
        if not hasattr(StatusEffectMixin, m):
            findings.append(f"{m} is not on StatusEffectMixin - it has drifted "
                            f"back onto one class and the other cannot use it")

    # _max_hp must work for BOTH, which is the whole point
    b = boss()
    c = Character("Hero", "Warrior", 60)
    rows.append(("_max_hp", "Monster", b._max_hp(), b.max_health))
    rows.append(("_max_hp", "Character", c._max_hp(), c.health))
    if b._max_hp() != b.max_health:
        findings.append(f"_max_hp on a Monster gave {b._max_hp()}, want "
                        f"max_health {b.max_health}")
    if c._max_hp() != c.health:
        findings.append(f"_max_hp on a Character gave {c._max_hp()}, want "
                        f"health {c.health}")

    # ---- 1. damage sharing: a boss soaking for its adds -------------------
    b, add = boss(), Monster("Add", "beast_basic", level=60)
    add.current_health = add.max_health
    arm(add, "sh", "Shielded by the Boss",
        damage_share_to=b, damage_share_pct=50)
    bb, ab = b.current_health, add.current_health
    add.take_damage(400, "arcane", attacker_level=60)
    soaked, lost = bb - b.current_health, ab - add.current_health
    rows.append(("damage share", "boss soaks 50% for its add",
                 f"add {lost}, boss {soaked}", "equal halves"))
    if soaked <= 0:
        findings.append("a boss soaked NOTHING for its add - damage sharing "
                        "is not reaching Monster.take_damage")
    elif abs(soaked - lost) > max(2, (soaked + lost) * 0.06):
        findings.append(f"a 50% share split {lost}/{soaked} - the halves "
                        f"should match")

    # ---- 2. death prevention, by absolute hp AND by percent ---------------
    b = boss()
    arm(b, "dp", "Not Yet", death_prevent_hp=1, death_prevent_uses=1)
    b.take_damage(10 ** 6, "arcane", attacker_level=60)
    held = b.current_health
    b.take_damage(10 ** 6, "arcane", attacker_level=60)
    rows.append(("death floor", "hp=1", f"held {held}, then {b.current_health}",
                 "1 then 0"))
    if held != 1:
        findings.append(f"a boss death floor of 1 hp held at {held}")
    if b.current_health > 0:
        findings.append("a boss survived a SECOND lethal blow - one use means "
                        "one")

    # PERCENT is the case that catches the .health/.max_health mistake: on a
    # Monster, reading .health gives 0, so the floor computes to 0 and never
    # fires while looking like a correct no-op.
    b = boss()
    arm(b, "dp2", "Held", death_prevent_pct=20, death_prevent_uses=1)
    want = int(b.max_health * 0.20)
    b.take_damage(10 ** 6, "arcane", attacker_level=60)
    rows.append(("death floor", "pct=20", b.current_health, want))
    if b.current_health != want:
        findings.append(f"a boss floor of 20% held at {b.current_health}, want "
                        f"{want} - a percentage floor on a Monster must use "
                        f"max_health, not health")

    # ---- 3. reflect -------------------------------------------------------
    b = boss()
    hero = Character("Hero", "Warrior", 60)
    hero.current_health = hero.health
    arm(b, "rf", "Spines", reflect_pct=30)
    hb = hero.current_health
    took = b.take_damage(400, "arcane", attacker_level=60, attacker=hero)
    back = hb - hero.current_health
    rows.append(("reflect", "30% to the attacker", f"took {took}, back {back}",
                 f"want {int(took * 0.3)}"))
    if abs(back - int(took * 0.3)) > 2:
        findings.append(f"a boss reflected {back} off a {took} hit, want "
                        f"{int(took * 0.3)}")

    # ---- 4. low-health trigger (percent of max_health again) --------------
    b = boss()
    arm(b, "lh", "Second Wind", on_low_health_pct=30,
        on_low_health_shield_pct=25, on_low_health_uses=1)
    b.current_health = int(b.max_health * 0.9)
    b.take_damage(int(b.max_health * 0.75), "arcane", attacker_level=60)
    shield = sum(getattr(e, "absorb", 0) or 0 for e in b._effects())
    want = int(b.max_health * 0.25)
    rows.append(("low health", "shield 25% below 30%", shield, want))
    if abs(shield - want) > 2:
        findings.append(f"a boss low-health shield gave {shield}, want {want}")

    # ---- 5. incoming damage converted to a shield -------------------------
    b = boss()
    arm(b, "cv", "Mana Carapace", damage_to_shield_pct=40,
        damage_to_shield_school="magic")
    took = b.take_damage(300, "arcane", attacker_level=60)
    shield = sum(getattr(e, "absorb", 0) or 0 for e in b._effects())
    rows.append(("dmg to shield", "40% of magic", shield,
                 f"want {int(took * 0.4)}"))
    if abs(shield - int(took * 0.4)) > 2:
        findings.append(f"a boss converted {shield} of a {took} magic hit, "
                        f"want {int(took * 0.4)}")
    b2 = boss()
    arm(b2, "cv2", "Mana Carapace", damage_to_shield_pct=40,
        damage_to_shield_school="magic")
    b2.take_damage(300, "physical", attacker_level=60)
    phys = sum(getattr(e, "absorb", 0) or 0 for e in b2._effects())
    rows.append(("dmg to shield", "physical ignored", phys, 0))
    if phys:
        findings.append(f"a magic-only conversion fired on a PHYSICAL hit "
                        f"({phys})")

    # ---- 6. the whole bestiary must be untouched --------------------------
    plain = boss("Plain")
    before = plain.current_health
    dealt = plain.take_damage(400, "arcane", attacker_level=60)
    rows.append(("no effects", "ordinary boss", before - plain.current_health,
                 dealt))
    if before - plain.current_health != dealt:
        findings.append("a boss with NO interception effects did not take its "
                        "full damage - the hooks must be inert by default")

    print(f"  {len(rows)} measurement(s) on a real Monster, through real "
          f"take_damage\n")
    if args.list:
        print(f"  {'hook':16}{'case':34}{'got':>14}{'want':>14}")
        for a, b_, c_, d in rows:
            print(f"  {a:16}{str(b_)[:32]:34}{str(c_):>14}{str(d):>14}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings:
            print(f"    {f}")
        print("\nFAIL")
        return 1

    print("  all five interception hooks work on a boss, percentages read "
          "max_health\n  correctly, and a boss carrying none of them is "
          "unaffected")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
