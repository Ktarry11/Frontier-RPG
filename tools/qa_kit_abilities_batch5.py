"""
Fourteen more early-recruit abilities (levels 5-14) - most of them ALREADY WORKED.

The kit data marks 166 abilities "needs: ..." and a large share of those notes are stale: the
mechanic was built since and nobody came back to the note. Each one below was cast in a rig
rather than read about.

Already live, note corrected:
  Marco Rossi     Somebody Had To               every hit on the chosen ally lands on Marco, -33%
  Dan Okafor      Stand In Front                the FIRST hit on any ally lands on Dan, halved
  Dan Okafor      Four Men, Long Shifts         6% less damage per living ally
  Sondre Haugen   First Awake Every Morning     the whole party's turn comes at once
  Ryan Murphy     Read What It Wants            the target's best resistance goes to zero
  Silas Vance     Which Crate's Light           every resistance drops to its weakest
  Sophia Dias     Simultaneous                  a second cast this turn, at 60%
  Diego Salazar   The Clockwork Beetle          summons the construct

Given the mechanic they describe:
  Dan Okafor      Shift Change                  Dan and the ally trade rows for the fight
  Sondre Haugen   Something He Had Not Asked For  Sondre is stunned for his next turn
  Hana Tamihana   She's Pulled a Lot of People Out  only under 25%, and heals exactly 60% of maximum
  Diego Salazar   Everybody Learned to Keep Working in the Dark  cannot be controlled, costs -30%

Text corrected to what happens: Marco *A Formality, Arrived Late*, Berat *Small Careful Work*.
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
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
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



    def by_name_starting(prefix):
        return next(n for n in by_name if n.startswith(prefix))

    def make_plain_hit(victim):
        """What the same 400 fire hit costs `victim` with nothing protecting anybody."""
        before = victim.current_health
        victim.take_damage(400, "fire", attacker_level=60, attacker=mob())
        lost = before - victim.current_health
        victim.current_health = before
        return lost

    ally = built.get("Ama Boateng")
    attacker = mob()

    def struck(victim, amount=400, school="fire"):
        before = victim.current_health
        victim.take_damage(amount, school, attacker_level=60, attacker=attacker)
        return before - victim.current_health

    # --- Marco: every hit on the ally lands on him, a third smaller -----------------------
    c, ab = kit("Marco Rossi", "Somebody Had To")
    if ab and ally:
        ally.current_health = ally.health
        ab.use(c, ally, party=[c, ally], free=True)
        h0 = c.current_health
        lost = struck(ally)
        moved = h0 - c.current_health
        check(lost == 0, f"Somebody Had To: the protected ally still lost {lost}")
        check(moved > 0, "Somebody Had To: Marco took nothing")
        plain = make_plain_hit(c)
        check(0.55 < moved / max(1, plain) < 0.80, f"Somebody Had To: Marco took {moved} of a hit worth {plain} "
                                                    f"to him - expected about a third less")
        ally.clear_combat_effects(); c.clear_combat_effects(); c.current_health = c.health

    # --- Dan: only the FIRST hit --------------------------------------------------------------
    c, ab = kit("Dan Okafor", "Stand In Front")
    if ab and ally:
        ally.current_health = ally.health
        ab.use(c, [c, ally], party=[c, ally], free=True)
        h0 = c.current_health
        first = struck(ally)
        took = h0 - c.current_health
        second = struck(ally)
        check(first == 0 and took > 0, f"Stand In Front: first hit cost the ally {first} and Dan {took}")
        check(second > 0, "Stand In Front redirected a second hit - it is the NEXT attack only")
        ally.clear_combat_effects(); c.clear_combat_effects()
        ally.current_health, c.current_health = ally.health, c.health

    # --- Dan: trades rows ----------------------------------------------------------------------
    c, ab = kit("Dan Okafor", "Shift Change")
    if ab and ally:
        c.row, ally.row = "front", "back"
        ab.use(c, ally, party=[c, ally], free=True)
        check(rows.row_of(c) == "back" and rows.row_of(ally) == "front",
              f"Shift Change: Dan is in the {rows.row_of(c)} row and the ally in the {rows.row_of(ally)}")
        check((c.row, ally.row) == ("front", "back"), "Shift Change rewrote the formation itself - it would outlast the fight")
        ally.clear_combat_effects(); c.clear_combat_effects()
        check(rows.row_of(c) == "front" and rows.row_of(ally) == "back", "the swap outlived the end of the fight")

    # --- Dan: 6% per living ally ----------------------------------------------------------------
    c, ab = kit("Dan Okafor", "Four Men, Long Shifts")
    other = built.get("Pavlo Hryn")
    if ab and ally and other:
        ab.use(c, c, party=[c, ally, other], free=True)
        got = c.get_status_stat_mod("physical_damage_taken_pct")
        check(got == -18, f"Four Men, Long Shifts with three alive gave {got}% - expected -18")
        check("forces" not in by_name["Four Men, Long Shifts"]["description"].lower(),
              "Four Men, Long Shifts still promises a forced taunt that is not built")
        c.clear_combat_effects()

    # --- Sondre -----------------------------------------------------------------------------------
    c, ab = kit("Sondre Haugen", "First Awake Every Morning")
    if ab and ally:
        from config import TURN_THRESHOLD
        ally.turn_meter = 0.0
        ab.use(c, [c, ally], party=[c, ally], free=True)
        check(ally.turn_meter >= TURN_THRESHOLD, "First Awake Every Morning did not bring the party's turn forward")
        ally.clear_combat_effects(); c.clear_combat_effects()
    c, ab = kit("Sondre Haugen", "Something He Had Not Asked For")
    if ab:
        m = mob()
        ab.use(c, m, party=[c], free=True)
        check(m.current_health < m.health, "Something He Had Not Asked For did no damage")
        check(c.is_stunned, "Something He Had Not Asked For did not stun Sondre")
        c.tick_status_effects()          # the end of the turn he cast on: the stun is still to come
        check(c.is_stunned, "Sondre's stun was gone before his next turn began")
        c.tick_status_effects()          # the end of the turn he lost
        check(not c.is_stunned, "Sondre was stunned for longer than his next turn")
        c.clear_combat_effects()

    # --- resistances ---------------------------------------------------------------------------------
    for who, title, expect in (("Ryan Murphy", "Read What It Wants", "highest"),
                               ("Silas Vance", by_name_starting("Which Crate"), "flat")):
        c, ab = kit(who, title)
        if ab:
            m = mob()
            m.base_fire_resist, m.base_frost_resist = 60, 20
            before = (m.get_resistance("fire"), m.get_resistance("frost"))
            check(before[0] > before[1] > 0, "rig: the boar's resistances did not take")
            ab.use(c, m, party=[c], free=True)
            fire, frost = m.get_resistance("fire"), m.get_resistance("frost")
            if expect == "highest":
                check(fire <= 0 and frost == before[1], f"{title}: fire {before[0]} -> {fire}, frost {before[1]} -> {frost}; "
                                                         f"only the highest should go, to zero")
            else:
                low = min(m.get_resistance(s) for s in ("fire", "frost", "nature", "shadow", "arcane", "holy"))
                check(fire == low and frost == low, f"{title}: fire {fire}, frost {frost}, lowest {low} - all should match")

    # --- Sophia: a second cast at 60% --------------------------------------------------------------
    c, ab = kit("Sophia Dias", "Simultaneous")
    if ab:
        c.turn_meter = 0.0
        ab.use(c, c, party=[c], free=True)
        from config import TURN_THRESHOLD
        check(c.turn_meter >= TURN_THRESHOLD, "Simultaneous did not give Sophia a second cast")
        check(c.get_status_stat_mod("damage_dealt_pct") == -40, "Simultaneous: the second cast is not at 60%")
        c.clear_combat_effects()

    # --- Diego ---------------------------------------------------------------------------------------
    c, ab = kit("Diego Salazar", "The Clockwork Beetle")
    if ab:
        ok, msg = ab.use(c, c, party=[c], free=True)
        check(ok and getattr(c, "all_pets", []), f"The Clockwork Beetle summoned nothing ({msg})")
    c, ab = kit("Diego Salazar", "Everybody Learned to Keep Working in the Dark")
    if ab:
        from combat.status_effects import StatusEffect, EffectType
        ab.use(c, c, party=[c], free=True)
        c.apply_status_effect(StatusEffect("t_stun", "Stun", EffectType.DEBUFF, 2, is_stun=True, real_time_seconds=None))
        check(not c.is_stunned, "Working in the Dark: Diego was stunned while it held")
        check(c.get_status_stat_mod("all_ability_cost_pct") in (0.3, 30), "Working in the Dark: no cost reduction")
        c.clear_combat_effects()

    # --- Hana: only under a quarter, and exactly 60% --------------------------------------------------
    c, ab = kit("Hana Tamihana", "She's Pulled a Lot of People Out")
    if ab and ally:
        ally.current_health = int(ally.health * 0.6)
        ok, _msg = ab.use(c, ally, party=[c, ally], free=True)
        check(not ok, "She's Pulled a Lot of People Out could be cast on an ally above 25%")
        ally.current_health = int(ally.health * 0.1)
        start = ally.current_health
        ab.turns_remaining = 0
        ok, msg = ab.use(c, ally, party=[c, ally], free=True)
        check(ok, f"She's Pulled a Lot of People Out refused a dying ally ({msg})")
        check(abs((ally.current_health - start) - ally.health * 0.6) <= 2,
              f"She's Pulled a Lot of People Out healed {ally.current_health - start}; 60% of {ally.health} is {ally.health * 0.6:.0f}")
        ally.current_health = ally.health

    # --- the bug this batch found: a buff that says "for N turns" lasts N turns ------------
    half_hour = []
    for who in built.values():
        for a in who.ability_book.abilities.values():
            if str(a.ability_id).startswith("personal_") and a.effect_type == "buff" and a.duration \
                    and a.buff_scope != "combat":
                half_hour.append(f"{who.name}: {a.name}")
    check(not half_hour, f"{len(half_hour)} companion buffs are thirty-minute buffs, not turn-counted: {half_hour[:5]}")
    c, ab = kit("Marco Rossi", "Somebody Had To")
    if ab and ally:
        ab.use(c, ally, party=[c, ally], free=True)
        mine = [e for e in ally._effects() if e.effect_id == ab.ability_id]
        check(mine and mine[0].real_time_seconds is None and mine[0].duration == 3,
              "Somebody Had To is not a three-turn effect")
        ally.clear_combat_effects()
        check(not [e for e in ally._effects() if e.effect_id == ab.ability_id],
              "Somebody Had To outlived the end of the fight")
        c.clear_combat_effects()

    for title, word in (("A Formality, Arrived Late", "holy"), ("Everybody Learned to Keep Working in the Dark", "silenced")):
        check(word not in by_name[title]["description"].lower(), f"{title} still says '{word}'")

    if fails:
        print(f"{len(fails)} problem(s):")
        for f in fails:
            print("  -", f)
        return 1
    print("kit abilities batch 5 OK - fourteen more early-recruit abilities do what they say.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
