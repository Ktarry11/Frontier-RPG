#!/usr/bin/env python3
"""Six more recruit abilities do what they say, and a monster's attack says who made it.

    python3 tools/qa_kit_abilities_batch7.py

13 Nov 2026. Each was a buff or debuff with no numbers and no mechanic: it cast, an icon
appeared, nothing changed. Every check below is the ability used in a real exchange.

Also the bug found on the way: MonsterAbility.use never passed attacker= to take_damage, so
reflect, enemy miss chance and dodge retaliation all worked in tests and never in a fight.
"""
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

bad = []


def check(ok, text):
    if not ok:
        bad.append(text)


def main():
    from combat.combat_engine import CombatEngine
    from combat.status_effects import StatusEffect, EffectType
    from entities.monster import Monster
    from entities.party import Party
    from world.recruit_manager import get_recruit_manager

    doc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}

    def setup(ability_name, foes=2):
        for kid, kit in doc.items():
            if kid.startswith("_"):
                continue
            for a in kit["abilities"]:
                if a["name"] == ability_name:
                    ch = recs[kid].build_character()
                    for res in ("rage", "energy", "mana", "focus", "power"):
                        for attr in (f"max_{res}", f"current_{res}"):
                            if isinstance(getattr(ch, attr, None), (int, float)):
                                setattr(ch, attr, 9999)
                    ab = next(x for x in ch.ability_book.get_all_abilities() if x.ability_id == a["ability_id"])
                    try:
                        rtype = ab._effective_resource_type(ch)
                        ch.set_resource(rtype, max(ch.get_resource_max(rtype) or 0, 9999))
                    except Exception:
                        pass
                    mobs = [Monster(f"Kolkar Bruiser {i + 1}", "humanoid_warrior", ch.level) for i in range(foes)]
                    for m in mobs:
                        m.max_health = m.current_health = 10 ** 7
                    eng = CombatEngine(ch, mobs[0], party=Party(ch), enemies=mobs)
                    ch.health = ch.current_health = 10 ** 6
                    return ch, ab, mobs, eng
        raise KeyError(ability_name)

    def basic(ch):
        return ch.ability_book.abilities[ch.get_basic_attack_id()]

    def spell_mult(ch, ab, foe):
        return ab._damage_multiplier(ch, "physical", foe)

    # ---- a monster's attack names its attacker ----
    ch, ab, mobs, eng = setup("Without Deciding To")
    seen = []
    orig = type(ch).take_damage
    def spy(self, amount, damage_type="physical", attacker_level=None, attacker=None):
        seen.append(attacker)
        return orig(self, amount, damage_type, attacker_level, attacker)
    type(ch).take_damage = spy
    try:
        for _ in range(4):
            act = mobs[0].choose_action(ch)
            act.use(mobs[0], ch, engine=eng)
    finally:
        type(ch).take_damage = orig
    check(seen and all(s is mobs[0] for s in seen), f"a monster's attack does not say who attacked ({seen})")

    # ---- Jun-seo: a missed attack is answered ----
    ok, _ = ab.use(ch, ch, party=[ch], engine=eng)
    check(ok and any(getattr(e, "counter_on_miss", False) for e in ch.active_effects), "Without Deciding To: no counter effect")
    ch.dodge = 100.0
    hp = mobs[0].current_health
    slash = next(a for a in mobs[0].abilities if a.kind == "damage")
    slash.turns_remaining = 0
    _, msg = slash.use(mobs[0], ch, engine=eng)
    # Answered, not necessarily landed: the counter is a real attack and can itself miss.
    check("Without Deciding To:" in msg, f"Without Deciding To: a dodged attack was not answered ({msg!r})")
    ch.dodge = 0.0; ch.parry = 0.0
    hp = mobs[0].current_health
    slash.turns_remaining = 0
    slash.use(mobs[0], ch, engine=eng)
    _, msg = "", ""
    slash.turns_remaining = 0
    _, msg = slash.use(mobs[0], ch, engine=eng)
    check("Without Deciding To:" not in msg, "Without Deciding To: an attack that LANDED was answered too")

    # ---- Bashir: his damage to the marked row, nobody else's ----
    ch, ab, mobs, eng = setup("He Snaps the Chalk Line")
    hit = basic(ch)
    before = spell_mult(ch, hit, mobs[0])
    ab.use(ch, mobs, party=[ch], engine=eng)
    marked = [m for m in mobs if any(getattr(e, "marked_pct", 0) for e in m.active_effects)]
    check(marked, "Chalk Line: nothing was marked")
    if marked:
        check(abs(spell_mult(ch, hit, marked[0]) - before * 1.30) < 1e-6 or spell_mult(ch, hit, marked[0]) - before >= 0.29,
              f"Chalk Line: {before} -> {spell_mult(ch, hit, marked[0])}, wanted +30%")
        other = recs["alonso_pyromancer"].build_character()
        ob = basic(other)
        check(ob._damage_multiplier(other, "physical", marked[0]) == ob._damage_multiplier(other, "physical", None),
              "Chalk Line: somebody else gets the bonus too")

    # ---- Tarek: more damage to whoever has hurt the party ----
    ch, ab, mobs, eng = setup("A Visible Enemy")
    hit = basic(ch)
    ab.use(ch, ch, party=[ch], engine=eng)
    clean = spell_mult(ch, hit, mobs[0])
    ch.apply_status_effect(StatusEffect("t_rend", "Rend", EffectType.DOT, 3, potency=1, source_name=mobs[0].name))
    check(spell_mult(ch, hit, mobs[0]) - clean >= 0.34, f"A Visible Enemy: no bonus against the enemy that hurt him ({clean} -> {spell_mult(ch, hit, mobs[0])})")
    innocent = Monster("Quiet Boar", "beast_basic", ch.level)
    check(spell_mult(ch, hit, innocent) <= clean + 1e-9, "A Visible Enemy: bonus against an enemy that did nothing")

    # ---- Pavlo: guard holds while he stands, drops when he attacks ----
    ch, ab, mobs, eng = setup("Stand Still While Something Comes")
    ab.use(ch, ch, party=[ch], engine=eng)
    eff = next((e for e in ch.active_effects if getattr(e, "breaks_on_attack", False)), None)
    check(eff is not None and eff.stat_mods.get("physical_damage_taken_pct") == -35, f"Stand Still: guard not applied as written ({eff and eff.stat_mods})")
    ch.tick_status_effects()
    check(any(getattr(e, "breaks_on_attack", False) for e in ch.active_effects), "Stand Still: guard fell without an attack")
    hp = mobs[0].current_health
    random.seed(3)
    slash = next(a for a in mobs[0].abilities if a.kind == "damage")
    ch.dodge = ch.parry = 0.0
    slash.use(mobs[0], ch, engine=eng)
    check(mobs[0].current_health < hp, "Stand Still: nothing was returned to the attacker")
    basic(ch).use(ch, mobs[0], engine=eng)
    ch.tick_status_effects()
    check(not any(getattr(e, "breaks_on_attack", False) for e in ch.active_effects), "Stand Still: guard survived an attack")

    # ---- Khalid: waiting builds the next shot, attacking spends it ----
    ch, ab, mobs, eng = setup("The Waiting")
    hit = basic(ch)
    base = spell_mult(ch, hit, mobs[0])
    ab.use(ch, ch, party=[ch], engine=eng)
    ch.tick_status_effects()
    one = spell_mult(ch, hit, mobs[0])
    ch.tick_status_effects()
    two = spell_mult(ch, hit, mobs[0])
    check(one - base >= 0.29 and two - one >= 0.29, f"The Waiting: {base} -> {one} -> {two}, wanted +30% a turn")
    hit.use(ch, mobs[0], engine=eng)
    ch.tick_status_effects()
    check(abs(spell_mult(ch, hit, mobs[0]) - base) < 1e-6 or not any(getattr(e, "idle_charge_pct", 0) for e in ch.active_effects),
          "The Waiting: the charge was not spent by attacking")

    # ---- Karim: the row burns and turns on him ----
    ch, ab, mobs, eng = setup("He Has Stopped Apologising For It")
    ok, msg = ab.use(ch, mobs, party=[ch], engine=eng)
    burning = [m for m in mobs if any(e.effect_type == EffectType.DOT for e in m.active_effects)]
    check(ok and burning, f"Stopped Apologising: nothing is burning ({msg!r})")
    check(any(ev for ev in (getattr(ab, "_last_threat_events", None) or [])), "Stopped Apologising: no threat was made")
    if burning:
        hp = burning[0].current_health
        burning[0].tick_status_effects()
        check(burning[0].current_health < hp, "Stopped Apologising: the burn does no damage")

    print("7 checks: attacker named, counter on a miss, mark, grudge, guard, waiting, burning taunt")
    if bad:
        print("FAIL:")
        for b in bad:
            print("  " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
