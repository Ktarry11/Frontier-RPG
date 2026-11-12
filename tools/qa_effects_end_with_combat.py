"""
Nothing that belonged to a fight follows the party out of it.

Kyle, 10 Nov, standing in the overworld with "Swallow the Swimmer (1t)" and "Thrash the Hall
(4t)" on him: "i could likely collect them like bad STDs."

A combat-scope effect counts TURNS, and turns only pass in combat, so anything left on the
party when a fight ended stayed forever. The end-of-fight clear only removed DoTs and HoTs.

A real CombatEngine fight, ended three ways (victory, flee, wipe). Before it ends the hero
carries one of everything; after it:

  GONE   an enemy's turn-counted debuff, an enemy's real-time debuff, a DoT, a HoT, a
         turn-counted combat buff - and the debuff's stat penalty with it
  KEPT   a real-time raid buff (and its stats), a talent proc carrier, an equipped trinket's
         proc carrier, a permanent passive
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROBLEMS = []


def setup():
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat.status_effects import StatusEffect, EffectType, TALENT_PROC_PREFIX

    hero = Character(name="Tester", char_class="Warrior", level=55)
    foe = Monster("Training Target", "humanoid_warrior", level=55)
    party = Party(hero)
    engine = CombatEngine(hero, foe, party=party, enemies=[foe])

    # A trinket with a proc, worn - the real item carrier.
    from entities import boss_loot
    for boss, pool in boss_loot._load_boss_loot_tables().items():
        for d in pool:
            if d.get("name") == "Running-Dry Charm":
                trinket = boss_loot._item_from_def(d)
    hero.inventory.append(trinket)
    assert hero.equip_item(trinket), "rig: could not equip the trinket"

    base_ap = hero.attack_power
    E = StatusEffect
    fx = {
        "enemy turn debuff": E("t_hex", "Thrash the Hall", EffectType.DEBUFF, duration=4,
                               stat_mods={"attack_power": -40}, source_name=foe.name,
                               real_time_seconds=None),
        "enemy clock debuff": E("t_curse", "Old Curse", EffectType.DEBUFF, duration=4,
                                stat_mods={"attack_power": -10}, source_name=foe.name),
        "dot": E("t_dot", "Rend", EffectType.DOT, duration=5, potency=5, source_name=foe.name),
        "hot": E("t_hot", "Renew", EffectType.HOT, duration=5, potency=5, source_name="Ally"),
        "combat buff": E("t_shout", "Enrage", EffectType.BUFF, duration=6,
                         stat_mods={"attack_power": 15}, source_name=hero.name,
                         real_time_seconds=None),
        "raid buff": E("t_might", "Blessing of Might", EffectType.BUFF, duration=999,
                       stat_mods={"attack_power": 25}, source_name="Ally"),
        "talent proc": E(TALENT_PROC_PREFIX + "t_test", "Talent", EffectType.BUFF, duration=999999,
                         stat_mods={}, real_time_seconds=None, proc={"trigger": "on_crit"}),
        "permanent passive": E("t_passive", "Moon Gazing", EffectType.BUFF, duration=999999,
                               stat_mods={}, real_time_seconds=None),
    }
    for e in fx.values():
        hero.active_effects.append(e)
    hero._recalculate_derived_stats()
    return hero, foe, engine, fx, base_ap


def check(way, finish):
    from combat.status_effects import ITEM_PROC_PREFIX
    hero, foe, engine, fx, base_ap = setup()
    during = hero.attack_power
    if during != base_ap - 40 - 10 + 15 + 25:
        PROBLEMS.append(f"{way}: rig - attack power in the fight is {during}, expected "
                        f"{base_ap - 40 - 10 + 15 + 25}; the effects are not all applying")
    finish(engine, hero, foe)
    if engine.is_active:
        PROBLEMS.append(f"{way}: rig - the fight did not end")
        return
    ids = {e.effect_id for e in hero.active_effects}
    gone = ["enemy turn debuff", "enemy clock debuff", "dot", "hot", "combat buff"]
    kept = ["raid buff", "talent proc", "permanent passive"]
    bad = [f"{k} survived" for k in gone if fx[k].effect_id in ids]
    bad += [f"{k} was removed" for k in kept if fx[k].effect_id not in ids]
    if not any(str(i).startswith(ITEM_PROC_PREFIX) for i in ids):
        bad.append("the worn trinket's proc carrier was removed")
    want_ap = base_ap + 25
    if hero.attack_power != want_ap:
        bad.append(f"attack power is {hero.attack_power}, expected {want_ap} "
                   f"(base {base_ap} + the raid buff only)")
    if bad:
        for b in bad:
            PROBLEMS.append(f"{way}: {b}")
            print(f"  FAIL {way}: {b}")
    else:
        print(f"  ok   {way}: 5 fight effects gone, 4 lasting ones kept, "
              f"attack power {during} -> {hero.attack_power}")


def win(engine, hero, foe):
    foe.current_health = 0
    engine._check_combat_end()


def flee(engine, hero, foe):
    for _ in range(50):
        if not engine.is_active:
            return
        for name in ("execute_flee",):
            fn = getattr(engine, name, None)
            if fn:
                fn(hero)
                break
        else:
            PROBLEMS.append("flee: rig - no flee method found on the engine")
            return


def wipe(engine, hero, foe):
    hero.current_health = 0
    engine._check_combat_end()


def main():
    check("victory", win)
    check("flee", flee)
    check("wipe", wipe)
    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        for p in PROBLEMS:
            print("  ", p)
        return 1
    print("\nend of combat OK - nothing from the fight follows the party out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
