"""
Thirteen more recruit signature abilities - the EARLY recruits, the ones a new player meets first.

Kyle, 12 Nov: "Imagine people playing the game, they experience lower stuff before end game."
Every companion below is level 5 to 14.

Ten had no mechanic behind their text and have one now:
  Esteban Ruiz      The Formalities Removed       heals the lowest ally for 60% of the damage
  Esteban Ruiz      Absolute Precision            always critically strikes
  Marisol Quintero  One More Instrument on a Tray heals the lowest ally for 70% of the damage
  Marisol Quintero  She Reaches Them Faster       30% more on an ally under half health
  Marcus Okafor     The Biggest One There Is      costs him 25% of his maximum health
  Ryan Murphy       Pays On Time                  pays 15% of his health, gets that much mana
  Silas Vance       Sharper Rules Than Antwerp    only under 30% health, and then triple
  Diego Salazar     Take a Thing Apart            target's armour -30% for 4 turns
  Marco Rossi       He Fixes Other Things         heals every ally 5% of their maximum
  Berat Yilmaz      A Frightened Patient Moves    the healed ally acts at once

Three were already doing what they say (or promised a protection against nothing):
  Marisol *The Habit of Narrating*, Sophia *A Grammar of This World*, Freja *A Working Pair of Hands*.
"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recruit_manager import get_recruit_manager
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat import rows
    from combat.status_effects import StatusEffect, EffectType
    rm = get_recruit_manager()
    built = {}
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is not None:
            built[c.name] = c
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    by_name = {a["name"]: a for k in kits.values() if isinstance(k, dict) for a in (k.get("abilities") or [])}

    def kit(who, title):
        c = built.get(who)
        entry = by_name.get(title)
        if not check(c is not None and entry is not None, f"rig: no {who} / {title}"):
            return None, None
        ab = c.ability_book.get_ability(entry["ability_id"])
        if not check(ab is not None, f"rig: {who} does not have {title}"):
            return c, None
        ab.is_learned = True
        ab.turns_remaining = 0
        c.current_health = c.health
        for attr in ("current_mana", "current_energy", "current_rage", "current_focus"):
            if hasattr(c, attr):
                setattr(c, attr, 10 ** 5)
        check(not str(entry.get("engine", "")).startswith("needs"), f"{title} is still marked {entry.get('engine')!r}")
        return c, ab

    def mob(row="front", armor=None):
        m = Monster("Mottled Boar", "beast_basic", level=60)
        m.row = row
        m.health = m.current_health = 10 ** 6
        if armor is not None:
            m.armor = armor
        return m

    def average(fn, n=60):
        random.seed(11)
        return sum(fn() for _ in range(n)) / n

    def hit(c, ab, m):
        before = m.current_health
        ab.turns_remaining = 0
        ab.use(c, m, party=[c], free=True)
        return before - m.current_health


    # --- Esteban: the lowest ally is healed for 60% of the damage ---------------------------
    a1, a2 = built.get("Ama Boateng"), built.get("Pavlo Hryn")
    for who, title, share in (("Esteban Ruiz", "The Formalities Removed", 0.6),
                              ("Marisol Quintero", "One More Instrument on a Tray", 0.7)):
        c, ab = kit(who, title)
        if ab and a1 and a2:
            m = mob()
            a1.current_health = int(a1.health * 0.9)
            a2.current_health = max(1, int(a2.health * 0.2))
            h2, before = a2.current_health, m.current_health
            ok, msg = ab.use(c, m, party=[c, a1, a2], free=True)
            dealt, got = before - m.current_health, a2.current_health - h2
            check(ok and dealt > 0, f"{title} did no damage ({msg})")
            check(abs(got - min(a2.health - h2, dealt * share)) <= max(2, dealt * 0.05),
                  f"{title} dealt {dealt:.0f} and healed the lowest ally for {got:.0f}; {share:.0%} is {dealt * share:.0f}")
            a1.current_health, a2.current_health = a1.health, a2.health

    # --- Esteban: always a critical strike -------------------------------------------------
    c, ab = kit("Esteban Ruiz", "Absolute Precision")
    if ab:
        m = mob()
        crits = 0
        random.seed(3)
        for _ in range(30):
            ab.turns_remaining = 0
            ab.use(c, m, party=[c], free=True)
            crits += bool(getattr(ab, "_last_crit", False))
        check(crits == 30, f"Absolute Precision crit {crits} times in 30")

    # --- Marisol: 30% more on an ally under half ------------------------------------------
    c, ab = kit("Marisol Quintero", "She Reaches Them Faster")
    friend = built.get("Tomas Havel")
    if ab and friend:
        friend.health = max(friend.health, 10 ** 5)

        def healed(at):
            friend.current_health = int(friend.health * at)
            before = friend.current_health
            ab.turns_remaining = 0
            ab.use(c, friend, party=[c, friend], free=True)
            return friend.current_health - before
        low, high = average(lambda: healed(0.3)), average(lambda: healed(0.7))
        check(1.2 < low / max(1, high) < 1.4, f"She Reaches Them Faster healed {low:.0f} under half and "
                                              f"{high:.0f} above - expected 30% more")
        friend._recalculate_derived_stats()

    # --- Marcus: a quarter of his health, and everybody is hit ----------------------------
    c, ab = kit("Marcus Okafor", "The Biggest One There Is")
    if ab:
        front, back = mob(), mob(row="back")
        eng = CombatEngine(c, front, party=Party(c), enemies=[front, back])
        eng.current_actor = c
        c.current_health = c.health
        ok, msg = eng.execute_ability(c, ab.ability_id, front)
        check(ok, f"The Biggest One There Is would not cast ({msg})")
        paid = c.health - c.current_health
        check(abs(paid - c.health * 0.25) <= 2, f"The Biggest One There Is cost {paid:.0f} health; 25% is {c.health * 0.25:.0f}")
        check(front.current_health < front.health and back.current_health < back.health,
              "The Biggest One There Is did not hit every enemy")
        c.current_health = c.health

    # --- Ryan: health for mana, one for one ------------------------------------------------
    c, ab = kit("Ryan Murphy", "Pays On Time")
    if ab:
        c.current_health, c.current_mana = c.health, 0
        ok, msg = ab.use(c, c, party=[c], free=True)
        paid, got = c.health - c.current_health, c.current_mana
        check(ok and abs(paid - int(c.health * 0.15)) <= 1, f"Pays On Time cost {paid} health; 15% is {int(c.health * 0.15)}")
        check(got == min(c.mana, paid), f"Pays On Time paid {paid} health and returned {got} mana")
        c.current_health = c.health

    # --- Silas: nothing above 30%, triple below --------------------------------------------
    c, ab = kit("Silas Vance", "Sharper Rules Than Antwerp")
    if ab:
        m = mob()
        ok, msg = ab.use(c, m, party=[c], free=True)
        check(not ok and m.current_health == m.health, "Sharper Rules Than Antwerp could be used on a healthy enemy")

        def at():
            m.current_health = int(m.health * 0.2)
            return hit(c, ab, m)
        with_rule = average(at)
        ab.cast_bonus_pct = 0
        plain = average(at)
        ab.cast_bonus_pct = 200
        check(2.6 < with_rule / max(1, plain) < 3.4, f"Sharper Rules did {with_rule:.0f} against {plain:.0f} without "
                                                     f"the rule - expected triple")

    # --- Diego: armour down 30% -------------------------------------------------------------
    c, ab = kit("Diego Salazar", "Take a Thing Apart")
    if ab:
        m = mob(armor=4000)
        m.base_armor = 4000
        ok, msg = ab.use(c, m, party=[c], free=True)
        check(ok, f"Take a Thing Apart would not cast ({msg})")
        check(abs(m.armor - 2800) <= 1, f"Take a Thing Apart left the target on {m.armor} armour; 30% off 4000 is 2800")
        for _ in range(5):
            m.tick_status_effects()
        check(m.armor == 4000, "the armour did not come back after 4 turns")

    # --- Marco: everybody gets 5% -----------------------------------------------------------
    c, ab = kit("Marco Rossi", "He Fixes Other Things")
    if ab and a1 and a2:
        a1.current_health = int(a1.health * 0.5)
        a2.current_health = 0
        before = a1.current_health
        ab.use(c, [c, a1, a2], party=[c, a1, a2], free=True)
        got = a1.current_health - before
        check(abs(got - a1.health * 0.05) <= max(2, a1.health * 0.01), f"He Fixes Other Things healed {got:.0f}; "
                                                                      f"5% of {a1.health} is {a1.health * 0.05:.0f}")
        check(a2.current_health == 0, "He Fixes Other Things raised the dead")
        a1.current_health, a2.current_health = a1.health, a2.health

    # --- Berat: the patient moves -----------------------------------------------------------
    c, ab = kit("Berat Yilmaz", "A Frightened Patient Moves")
    if ab and a1:
        from config import TURN_THRESHOLD
        a1.turn_meter = 0.0
        a1.current_health = int(a1.health * 0.5)
        ab.use(c, a1, party=[c, a1], free=True)
        check(a1.turn_meter >= TURN_THRESHOLD, "A Frightened Patient Moves did not give the ally their turn")
        check(a1.current_health > int(a1.health * 0.5), "A Frightened Patient Moves did not heal")
        a1.current_health = a1.health

    # --- three that were live already --------------------------------------------------------
    c, ab = kit("Marisol Quintero", "The Habit of Narrating")
    if ab and a1:
        ab.use(c, [c, a1], party=[c, a1], free=True)
        taken = a1.get_status_stat_mod("damage_taken_pct")
        check(taken in (-20, -0.2), f"The Habit of Narrating put damage_taken_pct {taken} on an ally, not -20%")
        check(a1.get_status_stat_mod("damage_dealt_pct") == -5, "The Habit of Narrating did not cost the party 5% damage")
        a1.clear_combat_effects()
        c.clear_combat_effects()
    c, ab = kit("Sophia Dias", "A Grammar of This World")
    if ab:
        ab.use(c, c, party=[c], free=True)
        check(c.get_status_stat_mod("spell_penetration") >= 30, "A Grammar of This World gave no spell penetration")
        c.clear_combat_effects()
    c, ab = kit("Freja Lindqvist", "A Working Pair of Hands")
    if ab and a1:
        a1.current_health = int(a1.health * 0.5)
        ab.use(c, [c, a1], party=[c, a1], free=True)
        check(a1.current_health > int(a1.health * 0.5), "A Working Pair of Hands did not heal the party")
        check("interrupt" not in by_name["A Working Pair of Hands"]["description"].lower(),
              "A Working Pair of Hands still promises it cannot be interrupted - nothing interrupts a cast")
        a1.current_health = a1.health

    if fails:
        print(f"{len(fails)} problem(s):")
        for f in fails:
            print("  -", f)
        return 1
    print("kit abilities batch 4 OK - thirteen early-recruit abilities do what they say.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
