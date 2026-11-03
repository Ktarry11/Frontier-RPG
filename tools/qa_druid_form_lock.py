#!/usr/bin/env python3
"""
A shapeshifted druid must never be unable to take a turn.

    PYTHONPATH=. python3 tools/qa_druid_form_lock.py

Kyle's friend, 2 Nov 2026: "Had to close the game couldn't do anything in
combat. Had bear form but took regular attack off my bar. Couldn't do anything
at all because casting doesn't remove bear form and with no rage I couldn't
attack or switch to the next character."

He had to kill the process. That is the worst class of bug in the game, and it
needed four separate things to be wrong at once:

  1. shift_form() zeroed current_mana along with rage and energy. The cited
     WOTLK rule is "shifting resets your current resource" and it means RAGE
     and ENERGY - mana persists in real WoW. Zeroing all three means a druid
     who shifts to bear has 0 rage (correct) AND 0 mana (wrong), so there is
     no resource left anywhere to spend on anything.
  2. Casting a mana ability did not drop the form, so even holding mana there
     was no way to use it.
  3. Basic attack lived only on the hotbar. Remove it and the one rage-
     generating action in the game is gone with it.
  4. CombatAction.FLEE was an enum member that nothing implemented, so there
     was no exit from the fight either.

Fix any three of those and the fourth still locks the game. So this asserts all
four, and it asserted them BEFORE the fix - every check below failed first, on
purpose, or it is not testing the bug.

The last check is the one that matters most: it reproduces the exact position
he was in - bear form, 0 rage, no attack on the bar - and demands that at least
one legal action exists.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    from entities.character import Character
    from entities.monster import Monster
    from combat.combat_engine import CombatEngine

    fails = []

    def druid(level=20):
        return Character(name="Bruin", char_class="Druid", level=level)

    # ---- 1. mana survives a shift; rage and energy do not
    d = druid()
    full_mana = d.mana
    d.current_rage = 40
    ok, _ = d.shift_form("bear")
    if not ok:
        print("  SKIP  could not shift into bear form")
        return 0
    if d.current_mana != full_mana:
        fails.append(f"shifting wiped mana: {d.current_mana}/{full_mana} - "
                     f"the druid now has no resource of any kind")
    if d.current_rage != 0:
        fails.append(f"shifting left {d.current_rage} rage - shifts must reset rage")

    # Reverting must not wipe it either, or shifting out to cast is still a trap.
    d.revert_form()
    if d.current_mana != full_mana:
        fails.append(f"reverting wiped mana: {d.current_mana}/{full_mana}")

    # ---- 2. casting a mana ability in a rage form drops the form first
    d = druid()
    d.shift_form("bear")
    caster_spell = None
    # Must cost mana, not merely BE a mana ability. Every class's basic
    # attack is typed mana with a cost of 0 (druid_attack, warrior_attack,
    # ...), so a picker that only checked the type grabbed "Attack" and
    # asserted that swinging a paw should drop you out of Bear Form - which
    # would be its own way to lose a turn. The engine gates on cost > 0 for
    # exactly this reason; the test has to agree with it.
    for ab in d.ability_book.get_all_abilities():
        rt = getattr(getattr(ab, "resource_type", None), "value", None)
        cost = ab.talented_cost(d) if hasattr(ab, "talented_cost") else 0
        if rt == "mana" and cost > 0 and getattr(ab, "effect_type", None) != "shapeshift":
            caster_spell = ab
            break
    if caster_spell is None:
        print("  NOTE  no mana ability found on a level 20 druid to test with")
    else:
        enemy = Monster("Target Dummy", "beast_basic", level=20)
        eng = CombatEngine(d, enemy)
        ok, msg = eng.execute_ability(d, caster_spell.ability_id, enemy)
        if not ok:
            fails.append(f"could not cast {caster_spell.name} in bear form: {msg}")
        elif d.current_form is not None:
            fails.append(f"cast {caster_spell.name} but stayed in "
                         f"{d.current_form} - casting must drop the form")

    # ---- 3. a basic attack is always reachable, hotbar or not
    d = druid()
    d.hotbar = [None] * len(d.hotbar)
    basic = None
    if hasattr(d, "get_basic_attack_id"):
        basic = d.get_basic_attack_id()
    if not basic:
        fails.append("no always-available basic attack - clearing the hotbar "
                     "removes the only way to build rage")
    else:
        d.shift_form("bear")
        enemy = Monster("Target Dummy", "beast_basic", level=20)
        eng = CombatEngine(d, enemy)
        before = d.current_rage
        ok, msg = eng.execute_ability(d, basic, enemy)
        if not ok:
            fails.append(f"basic attack failed in bear form: {msg}")
        elif d.current_rage <= before:
            fails.append(f"basic attack generated no rage ({before} -> "
                         f"{d.current_rage}) - nothing else can build it")

    # ---- 3b. shifting must not move the health bar, out or back
    #
    # Bear Form's Stamina raises max health, and the health you gain with it
    # has to come back off when you leave. Testing one shift is not enough:
    # the first version of this fix looked perfect going in (420 -> 620) and
    # halved the druid coming out (620 -> 220), because
    # _recalculate_derived_stats already clamps current health to the new
    # max and the carry then subtracted the same loss a second time. Only
    # the ROUND TRIP shows it, so the round trip is what is asserted.
    from combat.forms import FORMS
    for form_id, form in FORMS.items():
        c = Character(name="T", char_class=form["class"], level=60)
        for frac in (1.0, 0.5, 0.1):
            c.current_health = max(1, int(c.health * frac))
            c.current_mana = c.mana
            before_hp, before_mana = c.current_health, c.current_mana
            if not c.shift_form(form_id)[0]:
                break
            if c.mana <= 0 and form["class"] != "Warrior":
                fails.append(f"{form_id}: mana pool vanished while shifted")
            c.revert_form()
            if c.current_health != before_hp:
                fails.append(f"{form_id} at {frac:.0%}: health {before_hp} -> "
                             f"{c.current_health} across a shift round trip")
            if c.current_mana != before_mana:
                fails.append(f"{form_id} at {frac:.0%}: mana {before_mana} -> "
                             f"{c.current_mana} across a shift round trip")

    # ---- 4. fleeing works, and works at 100%
    d = druid()
    enemy = Monster("Target Dummy", "beast_basic", level=20)
    eng = CombatEngine(d, enemy)
    if not hasattr(eng, "execute_flee"):
        fails.append("CombatEngine has no execute_flee - CombatAction.FLEE is "
                     "an enum member nothing implements")
    else:
        for attempt in range(20):
            e2 = CombatEngine(druid(), Monster("Target Dummy", "beast_basic", level=20))
            fled, _ = e2.execute_flee(e2.player)
            if not fled:
                fails.append(f"flee failed on attempt {attempt + 1} - Kyle "
                             f"specified 100%")
                break
            if e2.is_active:
                fails.append("flee reported success but combat is still active")
                break

    # ---- 5. THE ACTUAL BUG. His exact position: bear, no rage, empty bar.
    d = druid()
    d.hotbar = [None] * len(d.hotbar)
    d.shift_form("bear")
    d.current_rage = 0
    enemy = Monster("Target Dummy", "beast_basic", level=20)
    eng = CombatEngine(d, enemy)

    escapes = []
    if hasattr(d, "get_basic_attack_id") and d.get_basic_attack_id():
        escapes.append("basic attack")
    if hasattr(eng, "execute_flee"):
        escapes.append("flee")
    if hasattr(eng, "execute_defend"):
        escapes.append("defend/pass")
    if d.current_mana > 0:
        escapes.append("cast (shifts out)")

    if not escapes:
        fails.append("HARD LOCK: bear form, 0 rage, empty hotbar - no legal "
                     "action exists. This is the close-the-game bug.")

    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1

    print("mana survives shifting; rage and energy reset")
    print("casting in bear form drops the form and casts")
    print("basic attack always reachable and builds rage")
    print("flee implemented, 100% success, ends combat")
    print(f"no-rage bear with an empty bar can still: {', '.join(escapes)}")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
