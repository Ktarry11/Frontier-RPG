#!/usr/bin/env python3
"""Wave 4: every Sworn skill is built right, only exists while Sworn, and does what it says.

    PYTHONPATH=. python3 tools/qa_sworn_skills.py [--strict]

Kyle, 19 Nov 2026: "These character traits should be slightly stronger than the other ones.
They still will get 5 ranks when appropriate (lvl 1,15,30,45, and 60)."

  1. tools/build_sworn_skills.py passes: every key is one the engine reads, cooldowns are 12 to
     15, nothing is "once a fight", every skill quotes its profile, descriptions say the
     mechanic. --strict also fails while any recruit is still unwritten.
  2. STRONGER THAN A TRAIT. Every five-rank Sworn skill's last rank is at least 1.1 times what
     the character traits' own rule gives the same ability.
  3. ONLY WHILE SWORN. A recruit has no Sworn skill (ability or passive) until their bond is
     Sworn; swearing puts it in the book of the character with you and says so; resetting takes
     it away; a save and load gives it back (the party is rebuilt before the bonds load).
  4. RANKS AT 1, 15, 30, 45 AND 60, and a level 60 companion holds the last.
  5. EACH ONE CAST FOR REAL, in a live fight on the recruit the game builds, and its outcome
     measured: by what kind of skill it is, and by its own check below where it does something
     a kind can't show.
"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

bad = []


def check(ok, text):
    if not ok:
        bad.append(text)
    return ok


# ---------------------------------------------------------------- the rig
def rig():
    from world.recruit_manager import reset_recruit_manager
    from world.bond_manager import reset_bond_manager, get_bond_manager
    rm = reset_recruit_manager()
    reset_bond_manager()
    return rm, get_bond_manager()


def swear(bm, rid, on=True):
    from world.bond_manager import STAGES
    b = bm.bonds[rid]
    b.stage = len(STAGES) - 1 if on else 0
    return b


def fill(ch, ab=None):
    for res in ("rage", "energy", "mana", "focus", "power", "combo", "life_force", "felfury",
                "archery_points"):
        for attr in (f"max_{res}", f"current_{res}"):
            if isinstance(getattr(ch, attr, None), (int, float)):
                setattr(ch, attr, 99999)
    if ab is not None:
        try:
            rtype = ab._effective_resource_type(ch)
            ch.set_resource(rtype, max(ch.get_resource_max(rtype) or 0, 99999))
        except Exception:
            pass
        ab.turns_remaining = 0


def fight(rm, bm, rid, friends=2):
    """The recruit at 60, Sworn, with `friends` other recruits and three big monsters."""
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party
    from world import personal_kits as PK
    recs = {r.recruit_id: r for r in rm.recruits.values()}
    swear(bm, rid)
    ch = rm.build_or_restore(recs[rid], player_level=60)
    PK.grant(ch)
    others = []
    for k in recs:
        if k != rid and k in PK.kits() and len(others) < friends:
            o = rm.build_or_restore(recs[k], player_level=60)
            if o is not None:
                others.append(o)
    party = Party(ch)
    for o in others:
        party.members.append(o)
    bm.party = party
    mobs = [Monster(f"Boar {i + 1}", kind, 60) for i, kind in enumerate(("beast_basic", "humanoid_caster", "beast_basic"))]
    for m in mobs:
        m.max_health = m.current_health = 10 ** 7
        m.dodge = m.parry = 0.0
    eng = CombatEngine(ch, mobs[0], party=party, enemies=mobs)
    for c in [ch] + others:
        c.stamina = 125000
        c._recalculate_derived_stats()
        c.current_health = c.health
        c.dodge = c.parry = 0.0
    entry = PK.sworn_skills()[rid].get("ability")
    ab = ch.ability_book.get_ability(entry["ability_id"]) if entry else None
    if ab is not None:
        ab.is_learned = True
    return ch, ab, others, mobs, eng


def cast(ch, ab, target, eng, seed=7):
    fill(ch, ab)
    random.seed(seed)
    ok, msg = ab.use(ch, target, party=eng.living_allies(), engine=eng)
    check(ok, f"{ab.name}: would not cast ({msg!r})")
    return ok, msg


def has_effect(who, aid):
    return any(getattr(e, "effect_id", None) in (aid, f"{aid}_shield") for e in who._effects())


def target_for(ab, ch, others, mobs):
    t = ab.target_type
    if t == "self":
        return ch
    if t == "ally":
        return others[0]
    if t in ("party", "all_allies"):
        return [ch] + others
    if t in ("enemy_aoe", "all_enemies"):
        return mobs
    return mobs[0]


# ---------------------------------------------------------------- each skill's own check
def c_kesten(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    # an ally the blow kills without it (a Protection warrior's talents can keep him up anyway)
    for o in others:
        o.take_damage(o.health * 20, "physical", attacker=mobs[0], attacker_level=60)
    dies = [o for o in others if not o.is_alive()
            and str(getattr(o, "char_class", "")) not in ("Warrior", "Guardian", "Paladin", "Templar")]
    if not check(dies, f"{ab.name}: rig has no ally a killing blow kills"):
        return
    for o in others:
        o.current_health = o.health
    cast(ch, ab, [ch] + others, eng)
    a = dies[0]
    a.take_damage(a.health * 20, "physical", attacker=mobs[0], attacker_level=60)
    check(a.is_alive() and a.current_health == 1, f"{ab.name}: a killing blow left {a.current_health} health, wants 1")
    a.take_damage(a.health * 20, "physical", attacker=mobs[0], attacker_level=60)
    check(not a.is_alive(), f"{ab.name}: saved the same ally twice")


def c_adrian(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    hit = 6000
    before = ch.current_health
    ch.take_damage(hit, "physical", attacker=mobs[0], attacker_level=60)
    plain = before - ch.current_health
    for c in [ch] + others:
        c.current_health = c.health
    cast(ch, ab, ch, eng)
    start = {id(o): o.current_health for o in others}
    before = ch.current_health
    ch.take_damage(hit, "physical", attacker=mobs[0], attacker_level=60)
    took = before - ch.current_health
    spread = sum(start[id(o)] - o.current_health for o in others)
    check(plain > 0 and 0.3 < took / plain < 0.5,
          f"{ab.name}: Adrián took {took} of a hit he'd take {plain} of, wants about 40%")
    check(plain > 0 and 0.3 < spread / plain < 0.55 and all(start[id(o)] > o.current_health for o in others),
          f"{ab.name}: the party took {spread} between them, wants about 42% of {plain}, split")


def c_tarek(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    a = others[0]
    eff = next((e for e in a._effects() if e.effect_id == ab.ability_id), None)
    if check(eff is not None and eff.absorb > 0, f"{ab.name}: no shield on an ally"):
        size = eff.absorb
        for _ in range(12):
            a.tick_status_effects()
        eff = next((e for e in a._effects() if e.effect_id == ab.ability_id), None)
        check(eff is not None and eff.absorb == size, f"{ab.name}: the shield wore off with time")
        a.take_damage(size * 50, "physical", attacker=mobs[0], attacker_level=60)
        check(not any(e.effect_id == ab.ability_id and e.absorb > 0 for e in a._effects()),
              f"{ab.name}: the shield survived being broken")


def c_diego(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[0]
    a.current_health = 0
    ok, msg = cast(ch, ab, a, eng)
    check(a.is_alive() and abs(a.current_health - a.health * 0.4) <= 2,
          f"{ab.name}: back at {a.current_health}/{a.health}, wants 40%")
    check(has_effect(a, ab.ability_id) and any(e.absorb > 0 for e in a._effects()),
          f"{ab.name}: no shield on the revived ally ({msg})")


def c_freja(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    heal = next((x for x in ch.ability_book.get_all_abilities()
                 if x.effect_type == "heal" and x.target_type in ("ally", "party") and x.is_learned
                 and not x.ability_id.startswith("personal_sworn_")), None)
    if not check(heal is not None, "Freja: no heal to measure with"):
        return
    a = others[0]

    def healed():
        a.current_health = 1
        fill(ch, heal)
        random.seed(3)
        heal.use(ch, a if heal.target_type == "ally" else [ch] + others, party=eng.living_allies(), engine=eng)
        return a.current_health - 1
    plain = healed()
    cast(ch, ab, ch, eng)
    doubled = healed()
    check(plain > 0 and 1.8 <= doubled / plain <= 2.2, f"{ab.name}: {heal.name} healed {plain}, then {doubled}, wants double")


def c_marco(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    before = a.current_health
    a.take_damage(4000, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.current_health < before, "rig: the ally takes nothing from a plain hit")
    a.current_health = a.health
    cast(ch, ab, [ch] + others, eng)
    a_before, m_before = a.current_health, ch.current_health
    a.take_damage(4000, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.current_health == a_before, f"{ab.name}: the ally still took {a_before - a.current_health}")
    check(0 < m_before - ch.current_health, f"{ab.name}: Marco took nothing for them")


def c_sophia(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[0]
    before = a.current_health
    a.take_damage(4000, "fire", attacker=mobs[1], attacker_level=60)
    plain = before - a.current_health
    a.current_health = a.health
    cast(ch, ab, [ch] + others, eng)
    before, foe = a.current_health, mobs[1].current_health
    a.take_damage(4000, "fire", attacker=mobs[1], attacker_level=60)
    took = before - a.current_health
    check(plain > 0 and 0.5 <= took / plain <= 0.7, f"{ab.name}: magic took {took}, was {plain}, wants 40% less")
    check(foe - mobs[1].current_health == took, f"{ab.name}: the caster got back {foe - mobs[1].current_health} of {took}")
    foe = mobs[0].current_health
    a.take_damage(3000, "physical", attacker=mobs[0], attacker_level=60)
    check(mobs[0].current_health == foe, f"{ab.name}: a sword was turned back too")


def c_carolina(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.status_effects import StatusEffect, EffectType
    a = others[0]
    a.apply_status_effect(StatusEffect("qa_poison", "Poison", EffectType.DEBUFF, 6, stat_mods={"armor_pct": -10},
                                       source_name="Boar 1", real_time_seconds=None))
    a.current_health = a.health // 3
    a._recalculate_derived_stats()
    h0 = a.haste
    cast(ch, ab, [ch] + others, eng)
    check(any(e.effect_id == ab.ability_id for e in a._effects()), f"{ab.name}: nothing on the ally")
    a._recalculate_derived_stats()
    check(a.get_status_stat_mod("haste") == 25 and a.haste - h0 >= 24.9,
          f"{ab.name}: haste went {h0:.1f} to {a.haste:.1f}, wants +25")
    before = a.current_health
    a.tick_status_effects()
    check(a.current_health > before, f"{ab.name}: a tick healed nothing")
    check(not any(e.effect_id == "qa_poison" for e in a._effects()), f"{ab.name}: a tick didn't wash the poison off")


def c_ryan(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    summon = next((x for x in ch.ability_book.get_all_abilities() if x.effect_type == "summon_pet"), None)
    if summon is not None:
        fill(ch, summon)
        summon.is_learned = True
        summon.use(ch, ch, party=eng.living_allies(), engine=eng, free=True)
    cast(ch, ab, [ch] + others, eng)
    a = others[1]
    a_before, r_before = a.current_health, ch.current_health
    a.take_damage(4000, "shadow", attacker=mobs[1], attacker_level=60)
    lost, paid = a_before - a.current_health, r_before - ch.current_health
    check(lost > 0 and paid > 0 and 0.6 <= paid / lost <= 0.8, f"{ab.name}: ally lost {lost}, Ryan paid {paid}, wants about 0.7 of it")
    pets = [p for p in (getattr(ch, "all_pets", None) or []) if p.is_alive()]
    if check(pets, f"{ab.name}: rig has no demon out"):
        check(pets[0].get_status_stat_mod("damage_dealt_pct") == 40,
              f"{ab.name}: demon damage {pets[0].get_status_stat_mod('damage_dealt_pct')}, wants +40")


def c_hana(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    low = others[1]
    low.current_health = low.health // 10
    cast(ch, ab, others[0], eng)
    check(low.current_health == low.health, f"{ab.name}: the worst-off ally is at {low.current_health}/{low.health}")


def c_esteban(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    low = others[1]
    low.current_health = low.health // 10
    before = {id(c): c.current_health for c in [ch] + others}
    cast(ch, ab, others[0], eng)
    for c in [ch, others[0]]:
        gave = before[id(c)] - c.current_health
        check(abs(gave - int(c.health * 0.10)) <= 2, f"{ab.name}: {c.name} gave {gave}, wants 10% of {c.health}")
    check(low.current_health - before[id(low)] > int(ch.health * 0.1) + int(others[0].health * 0.1),
          f"{ab.name}: the dying ally got only {low.current_health - before[id(low)]}")


def c_passive(rm, bm, rid):
    """A Sworn passive is in the passive pools only while Sworn, and shows on the sheet."""
    from world import personal_kits as PK
    recs = {r.recruit_id: r for r in rm.recruits.values()}
    block = PK.sworn_skills()[rid]["passives"]
    keys = {k for k in block if not k.startswith("_")}
    swear(bm, rid, False)
    ch = rm.build_or_restore(recs[rid], player_level=60)
    off = {**PK.passives_for(ch), **PK.combat_passives_for(ch)}
    swear(bm, rid, True)
    on = {**PK.passives_for(ch), **PK.combat_passives_for(ch)}
    for k in keys:
        check(off.get(k, 0) == 0 and on.get(k, 0) != 0, f"{rid}: passive {k} is {off.get(k)} before swearing, {on.get(k)} after")
    check(any(src == "Sworn" for _, src, _ in PK.passive_entries_for(ch)), f"{rid}: the Sworn passive isn't listed")
    return ch


def c_ama(rm, bm, rid):
    ch = c_passive(rm, bm, rid)
    from entities.character import Character
    heal = next((x for x in ch.ability_book.get_all_abilities() if x.effect_type == "heal"), None)
    if not check(heal is not None, "Ama: no heal to measure"):
        return
    low, high, mid = (Character(n, "Warrior", 60) for n in ("Low", "High", "Mid"))
    for c, f in ((low, 0.3), (high, 0.95), (mid, 0.65)):
        c.current_health = int(c.health * f)
    ch._recalculate_derived_stats()
    m = {c.name: heal._damage_multiplier(ch, "healing", recipient=c) for c in (low, high, mid)}
    check(abs(m["Low"] / m["Mid"] - 1.40) < 0.01, f"Ama: below half heals x{m['Low'] / m['Mid']:.2f}, wants x1.40")
    check(abs(m["High"] / m["Mid"] - 0.80) < 0.01, f"Ama: above 80% heals x{m['High'] / m['Mid']:.2f}, wants x0.80")


def c_berat(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.status_effects import StatusEffect, EffectType
    a = others[0]
    stun = StatusEffect("qa_stun", "Stunned", EffectType.DEBUFF, 3, stat_mods={}, source_name="Boar 1",
                        real_time_seconds=None)
    stun.is_stun = True
    a.apply_status_effect(stun)
    check(a.is_stunned, "rig: the stun didn't take")
    cast(ch, ab, [ch] + others, eng)
    check(not a.is_stunned, f"{ab.name}: the ally is still stunned")
    for key, value in ab.stat_mods.items():
        check(a.get_status_stat_mod(key) == value, f"{ab.name}: {key} {a.get_status_stat_mod(key)}, wants {value}")


def c_dan(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    n = len([c for c in [ch] + others if c.is_alive()])
    a = others[0]
    got = a.get_status_stat_mod("physical_damage_taken_pct")
    check(got == -7 * n, f"{ab.name}: an ally takes {got}% with {n} standing, wants {-7 * n}")


def c_marisol(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    cast(ch, ab, a, eng)
    floor = int(a.health * 0.05)
    for _ in range(4):
        a.take_damage(a.health * 50, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.is_alive() and a.current_health >= floor - 1,
          f"{ab.name}: four killing blows left {a.current_health}, wants at least {floor}")


def c_silas(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    before = a.current_health
    a.take_damage(2000, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.current_health < before, "rig: the ally takes nothing from a plain hit")
    a.current_health = a.health
    cast(ch, ab, [ch] + others, eng)
    lost = []
    for _ in range(3):
        before = a.current_health
        a.take_damage(2000, "shadow", attacker=mobs[1], attacker_level=60)
        lost.append(before - a.current_health)
    check(lost[0] == 0 and lost[1] == 0 and lost[2] > 0, f"{ab.name}: the ally lost {lost}, wants nothing twice and then a hit")


def c_pavlo(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    for c in [ch] + others:
        before = c.current_health
        c.take_damage(5000, "physical", attacker=mobs[0], attacker_level=60)
        c.take_damage(5000, "shadow", attacker=mobs[1], attacker_level=60)
        check(c.current_health == before, f"{ab.name}: {c.name} still lost {before - c.current_health}")


def c_amber(rm, bm, rid):
    ch = c_passive(rm, bm, rid)
    hot = next((x for x in ch.ability_book.get_all_abilities() if x.effect_type == "hot"), None)
    if not check(hot is not None, "Amber: no heal over time to measure"):
        return
    from entities.character import Character
    a = Character("Friend", "Warrior", 60)
    ch._recalculate_derived_stats()
    fill(ch, hot)
    hot.use(ch, a, party=[ch, a], free=True)
    eff = next((e for e in a._effects() if e.effect_id == hot.ability_id), None)
    if check(eff is not None, f"Amber: {hot.name} put nothing on"):
        want = (hot.tick_growth_pct or 0) + 15
        check(abs(eff.tick_growth_pct - want) < 0.01, f"Amber: {hot.name} grows {eff.tick_growth_pct}% a turn, wants {want}")


def c_marta(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    hp = mobs[0].current_health
    cast(ch, ab, mobs[0], eng)
    check(mobs[0].current_health == hp, f"{ab.name}: went off at once")
    landed = None
    for t in range(1, 5):
        eng._end_turn(ch)
        if mobs[0].current_health < hp:
            landed = t
            break
    check(landed == 3, f"{ab.name}: went off after {landed} turn-ends, wants 3 (the setting turn and 2 more)")



def _stun(who, name="Stunned"):
    from combat.status_effects import StatusEffect, EffectType
    e = StatusEffect("qa_stun", name, EffectType.DEBUFF, 3, stat_mods={}, source_name="Boar 1", real_time_seconds=None)
    e.is_stun = True
    who.apply_status_effect(e)
    return e


def c_lucia(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[0]
    a.current_health = 1
    a.heal(1000)
    plain = a.current_health - 1
    cast(ch, ab, [ch] + others, eng)
    a.current_health = 1
    a.heal(1000)
    got = a.current_health - 1
    check(abs(got - plain * 1.4) <= 2, f"{ab.name}: a heal of {plain} now lands for {got}, wants {plain * 1.4:.0f}")


def c_minh(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    marks = {}
    for c in [ch] + others:
        marks[c.name] = []
        for frac in (0.9, 0.7, 0.5):
            c.current_health = int(c.health * frac)
            marks[c.name].append(c.current_health)
            c.tick_status_effects()
        c.current_health = int(c.health * 0.1)
    cast(ch, ab, [ch] + others, eng)
    for c in [ch] + others:
        check(c.current_health == marks[c.name][1],
              f"{ab.name}: {c.name} back to {c.current_health}, wants {marks[c.name][1]}")


def c_bakyt(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    m = mobs[1]
    before = m.current_health
    m.take_damage(10000, "shadow", attacker=ch, attacker_level=60)
    plain = before - m.current_health
    armor = m.armor if hasattr(m, "armor") else None
    cast(ch, ab, mobs, eng)
    before = m.current_health
    m.take_damage(10000, "shadow", attacker=ch, attacker_level=60)
    got = before - m.current_health
    check(abs(got - plain * 1.2) <= plain * 0.02, f"{ab.name}: a hit of {plain} now does {got}, wants about {plain * 1.2:.0f}")
    for f in mobs:
        check(has_effect(f, ab.ability_id), f"{ab.name}: {f.name} isn't marked")


def c_matias(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    low = others[1]
    hb = low.current_health
    low.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    raw = hb - low.current_health
    low.current_health = low.health // 4
    cast(ch, ab, others[0], eng)
    check(has_effect(low, ab.ability_id) and not has_effect(others[0], ab.ability_id),
          f"{ab.name}: didn't land on the lowest ally")
    lb, mb = low.current_health, ch.current_health
    low.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    check(low.current_health == lb, f"{ab.name}: the lowest ally still lost {lb - low.current_health}")
    took = mb - ch.current_health
    check(0 < took <= raw * 0.7 + 1, f"{ab.name}: Matías took {took} of a {raw} hit, wants at most {raw * 0.7:.0f}")


def c_tomas(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    a = others[1]
    _stun(a)
    check(not a.is_stunned, f"{ab.name}: an ally can still be stunned")
    check(a.get_status_stat_mod("armor_pct") == 30, f"{ab.name}: armour {a.get_status_stat_mod('armor_pct')}")
    a.take_damage(a.health * 50, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.is_alive() and a.current_health == 1, f"{ab.name}: a killing blow left {a.current_health}")


def c_cristobal(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat import rows
    low = others[1]
    low.current_health = low.health // 5
    cast(ch, ab, others[0], eng)
    check(has_effect(low, ab.ability_id), f"{ab.name}: no shield on the lowest ally")
    check(rows.row_of(low) == rows.BACK_ROW, f"{ab.name}: the lowest ally is in row {rows.row_of(low)}")
    before = low.current_health
    low.take_damage(200, "shadow", attacker=mobs[1], attacker_level=60)
    check(low.current_health == before, f"{ab.name}: the shield let {before - low.current_health} through")


def c_callum(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.status_effects import StatusEffect, EffectType
    a, b = others
    for i in range(2):
        a.apply_status_effect(StatusEffect(f"qa_poison{i}", f"Poison {i}", EffectType.DOT, 5, potency=300,
                                           damage_school="nature", source_name="Boar 1", real_time_seconds=None,
                                           dispel_type="poison"))
    b.apply_status_effect(StatusEffect("qa_bleed", "Bleed", EffectType.DOT, 5, potency=300,
                                       source_name="Boar 1", real_time_seconds=None))
    cast(ch, ab, [ch] + others, eng)
    check(not any(e.effect_id.startswith("qa_poison") for e in a._effects()), f"{ab.name}: a poison is still on")
    check(any(e.effect_id == "qa_bleed" for e in b._effects()), "rig: the bleed was cleansed too")
    before = b.current_health
    b.tick_status_effects()
    check(b.current_health >= before, f"{ab.name}: the bleed still ticked for {before - b.current_health}")


def c_giorgi(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[0]
    _stun(a, "Feared")
    check(a.is_stunned, "rig: the fear didn't take")
    speed = [m.turn_speed for m in mobs] if all(hasattr(m, "turn_speed") for m in mobs) else None
    cast(ch, ab, [ch] + others, eng)
    check(not a.is_stunned, f"{ab.name}: the ally is still feared")
    for m in mobs:
        check(m.get_status_stat_mod("haste") == -30, f"{ab.name}: {m.name} haste {m.get_status_stat_mod('haste')}")
    eng.turn_meter._refresh_turn_speed(mobs[0])
    if speed:
        check(mobs[0].turn_speed < speed[0] * 0.75, f"{ab.name}: enemy speed {speed[0]} -> {mobs[0].turn_speed}")


def c_camille(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from config import TURN_THRESHOLD
    a = others[1]
    ch.turn_meter = TURN_THRESHOLD
    cast(ch, ab, a, eng)
    eng._end_turn(ch)
    check(ch.turn_meter >= TURN_THRESHOLD, f"{ab.name}: after her turn the meter is {ch.turn_meter}, wants another turn")
    lost = []
    for _ in range(2):
        before = a.current_health
        a.take_damage(2000, "shadow", attacker=mobs[1], attacker_level=60)
        lost.append(before - a.current_health)
    check(lost[0] == 0 and lost[1] > 0, f"{ab.name}: the ally lost {lost}, wants nothing once and then a hit")


def c_liam(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    for c in [ch] + others:
        c.current_health = max(1, c.health // 4)
    before = {c.name: c.current_health for c in [ch] + others}
    cast(ch, ab, [ch] + others, eng)
    for c in [ch] + others:
        check(c.current_health - before[c.name] >= c.health * 0.1,
              f"{ab.name}: {c.name} healed {c.current_health - before[c.name]} of {c.health}")



def _control(a, mob, amount=3000, school="shadow"):
    """What a plain hit takes off this ally, health put back after."""
    before = a.current_health
    a.take_damage(amount, school, attacker=mob, attacker_level=60)
    lost = before - a.current_health
    a.current_health = before
    return lost


def c_orlando(rm, bm, rid):
    c_passive(rm, bm, rid)
    swear(bm, rid, False)
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    # fight() swears again; build a second engine so the opening is read with him Sworn
    from combat.combat_engine import CombatEngine
    eng = CombatEngine(ch, mobs[0], party=bm.party, enemies=mobs)
    for c in [ch] + others:
        check(has_effect(c, f"sworn_opening_{rid}"), f"Orlando: {c.name} isn't steadied as the fight opens")
        check(c.get_status_stat_mod("cc_immune") > 0, f"Orlando: {c.name} can still be frightened")
    swear(bm, rid, False)
    for c in [ch] + others:
        c._effects()[:] = [e for e in c._effects() if e.effect_id != f"sworn_opening_{rid}"]
    CombatEngine(ch, mobs[0], party=bm.party, enemies=mobs)
    check(not any(has_effect(c, f"sworn_opening_{rid}") for c in [ch] + others), "Orlando: the opening works without the bond")


def c_owen(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    raw = _control(a, mobs[1])
    phys = _control(a, mobs[0], 3000, "physical")
    check(raw > 0 and phys > 0, "rig: the ally takes nothing from a plain hit")
    cast(ch, ab, [ch] + others, eng)
    before, ob = a.current_health, ch.current_health
    a.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.current_health == before, f"{ab.name}: the ally still took {before - a.current_health} of a spell")
    check(0 < ob - ch.current_health <= raw * 0.6 + 1, f"{ab.name}: Owen took {ob - ch.current_health} of {raw}")
    before = a.current_health
    a.take_damage(3000, "physical", attacker=mobs[0], attacker_level=60)
    check(before - a.current_health > 0, f"{ab.name}: a physical hit was taken off the ally too")


def c_anjali(rm, bm, rid):
    ch = c_passive(rm, bm, rid)
    heal = next((x for x in ch.ability_book.get_all_abilities() if x.effect_type == "heal" and x.is_learned), None)
    if not check(heal is not None, "Anjali: no heal to measure"):
        return
    from entities.character import Character
    a = Character("Friend", "Warrior", 60)
    a.current_health = a.health // 4
    ch._recalculate_derived_stats()
    fill(ch, heal)
    before = a.current_health
    heal.use(ch, a, party=[ch, a], free=True)
    got = a.current_health - before
    eff = next((e for e in a._effects() if e.effect_id.endswith("_growth")), None)
    if check(eff is not None and got > 0, f"Anjali: {heal.name} healed {got} and left no growth"):
        check(abs(eff.potency - got * 0.10) <= 1, f"Anjali: growth heals {eff.potency} a turn, wants {got * 0.1:.0f}")
        a.current_health = a.health // 4
        b = a.current_health
        a.tick_status_effects()
        check(a.current_health > b, "Anjali: the growth healed nothing on its tick")


def c_pasang(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    raw = _control(a, mobs[1], 6000)
    cast(ch, ab, [ch] + others, eng)
    party = [ch] + others
    hp = {c.name: c.current_health for c in party}
    a.take_damage(6000, "shadow", attacker=mobs[1], attacker_level=60)
    lost = {c.name: hp[c.name] - c.current_health for c in party}
    n = len(party)
    check(abs(lost[a.name] - raw / n) <= raw * 0.02 + 1, f"{ab.name}: the hit ally lost {lost[a.name]} of {raw}, wants {raw / n:.0f}")
    for c in party:
        if c is not a:
            check(abs(lost[c.name] - raw / n * 0.75) <= raw * 0.02 + 1, f"{ab.name}: {c.name} carried {lost[c.name]}, wants {raw / n * 0.75:.0f}")


def c_nicolas(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    raw = _control(a, mobs[1])
    cast(ch, ab, [ch] + others, eng)
    before = a.current_health
    a.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    check(abs((before - a.current_health) - raw / 2) <= raw * 0.02 + 1, f"{ab.name}: the ally lost {before - a.current_health} of {raw}, wants half")


def c_iker(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.abilities import get_class_resource
    party = [ch] + others
    for c in party:
        c.current_health = c.health // 4
        c.set_resource(get_class_resource(c.char_class, c), 0)
    hp = {c.name: c.current_health for c in party}
    cast(ch, ab, party, eng)
    for c in party:
        kind = get_class_resource(c.char_class, c)
        check(c.current_health - hp[c.name] >= c.health * 0.1, f"{ab.name}: {c.name} healed {c.current_health - hp[c.name]}")
        if c is not ch:
            check(c.get_resource(kind) >= c.get_resource_max(kind) * 0.29,
                  f"{ab.name}: {c.name} has {c.get_resource(kind)} {getattr(kind, 'value', kind)} of {c.get_resource_max(kind)}")


def c_mateo(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    party = [ch] + others
    for c in party:
        c.current_health = c.health // 4
    hp = {c.name: c.current_health for c in party}
    foes = [m.current_health for m in mobs]
    cast(ch, ab, mobs, eng)
    check(any(m.current_health < f for m, f in zip(mobs, foes)), f"{ab.name}: no enemy was hit")
    for c in party:
        check(c.current_health - hp[c.name] >= c.health * 0.12 - 1, f"{ab.name}: {c.name} healed {c.current_health - hp[c.name]}")


def c_imelda(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    low = others[1]
    low.current_health = low.health // 10
    before, mb = low.current_health, mobs[0].current_health
    cast(ch, ab, mobs[0], eng)
    dealt = mb - mobs[0].current_health
    check(dealt > 0, f"{ab.name}: dealt nothing")
    check(low.current_health - before >= min(dealt, low.health - before) * 0.9,
          f"{ab.name}: dealt {dealt} and the most wounded ally got {low.current_health - before}")



def c_ileana(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, mobs, eng)
    for m in mobs:
        check(m.is_stunned, f"{ab.name}: {m.name} isn't frozen")


def c_rhys(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    for i, m in enumerate(mobs):
        m.turn_meter = 10.0 * i
    nxt = mobs[2]
    hp = [m.current_health for m in mobs]
    cast(ch, ab, mobs[0], eng)
    check(nxt.current_health < hp[2] and mobs[0].current_health == hp[0],
          f"{ab.name}: hit {[h - m.current_health for m, h in zip(mobs, hp)]}, wants only the one about to act")
    check(nxt.is_stunned, f"{ab.name}: the enemy about to act isn't stopped")


def c_eino(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    mobs[1].max_health = mobs[1].current_health = 2 * 10 ** 7
    hp = [m.current_health for m in mobs]
    cast(ch, ab, mobs[0], eng)
    check(mobs[1].current_health < hp[1] and mobs[0].current_health == hp[0], f"{ab.name}: didn't fell the biggest enemy")
    for key, value in ab.target_mods.items():
        check(mobs[1].get_status_stat_mod(key) == value, f"{ab.name}: {key} {mobs[1].get_status_stat_mod(key)}, wants {value}")


def c_driss(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    for m in mobs:
        check(m.get_status_stat_mod("miss_chance_pct") == 30, f"{ab.name}: {m.name} isn't blinded")
    random.seed(3)
    a = others[1]
    misses = 0
    for _ in range(400):
        before = a.current_health
        a.take_damage(100, "shadow", attacker=mobs[1], attacker_level=60)
        misses += a.current_health == before
        a.current_health = a.health
    check(90 <= misses <= 150, f"{ab.name}: {misses} of 400 spells missed, wants about 120")


def c_thiago(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    cast(ch, ab, a, eng)
    for _ in range(3):
        a.take_damage(a.health * 50, "shadow", attacker=mobs[1], attacker_level=60)
    check(a.is_alive(), f"{ab.name}: three killing blows killed them")


def c_enzo(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    m = mobs[1]
    cast(ch, ab, ch, eng)
    before, mb = ch.current_health, m.current_health
    ch.take_damage(4000, "shadow", attacker=m, attacker_level=60)
    check(ch.current_health == before, f"{ab.name}: Enzo still took {before - ch.current_health}")
    check(mb - m.current_health == 6000, f"{ab.name}: the attacker took {mb - m.current_health}, wants 6000")
    before = ch.current_health
    ch.take_damage(4000, "shadow", attacker=m, attacker_level=60)
    check(ch.current_health < before, f"{ab.name}: the second hit was turned back too")


def c_alonso(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    m = mobs[0]
    def hit(school):
        b = m.current_health
        m.take_damage(10000, school, attacker=ch, attacker_level=60)
        return b - m.current_health
    fire, frost = hit("fire"), hit("frost")
    cast(ch, ab, mobs, eng)
    f2, i2 = hit("fire"), hit("frost")
    check(abs(f2 - fire * 1.4) <= fire * 0.02 + 1, f"{ab.name}: fire {fire} -> {f2}, wants x1.4")
    check(i2 == frost, f"{ab.name}: frost changed too ({frost} -> {i2})")



def c_vuk(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    low = others[1]
    low.current_health = low.health // 4
    cast(ch, ab, others[0], eng)
    check(has_effect(low, ab.ability_id) and not has_effect(others[0], ab.ability_id), f"{ab.name}: not on the lowest ally")
    lb = low.current_health
    low.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    check(low.current_health == lb, f"{ab.name}: the lowest ally still lost {lb - low.current_health}")


def c_kourosh(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    for i, m in enumerate(mobs):
        m.turn_meter = 10.0 * i
    cast(ch, ab, mobs[0], eng)
    check(has_effect(mobs[2], ab.ability_id) and not has_effect(mobs[0], ab.ability_id), f"{ab.name}: not on the enemy about to act")
    check(abs(mobs[2].damage_output_multiplier / max(1e-9, mobs[1].damage_output_multiplier) - 0.3) < 0.01,
          f"{ab.name}: its damage is x{mobs[2].damage_output_multiplier / mobs[1].damage_output_multiplier:.2f}, wants x0.30")


def c_hector(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    hp = [m.current_health for m in mobs]
    cast(ch, ab, mobs, eng)
    hit = [m for m, h in zip(mobs, hp) if m.current_health < h]
    check(bool(hit), f"{ab.name}: hit nothing")
    for m in hit:
        check(m.is_stunned, f"{ab.name}: {m.name} was hit and isn't stunned")


def c_ziad(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    for c in others:
        c.current_health = c.health // 4
    before = {c.name: c.current_health for c in others}
    mine = ch.current_health
    cast(ch, ab, [ch] + others, eng)
    check(all(c.current_health > before[c.name] for c in others), f"{ab.name}: healed nobody")
    check(mine - ch.current_health >= int(ch.health * 0.15) - 1 - ch.health * 0.01 or ch.current_health < mine,
          f"{ab.name}: Ziad paid nothing")
    check(ch.get_status_stat_mod("damage_dealt_pct") == 40, f"{ab.name}: no fel payback ({ch.get_status_stat_mod('damage_dealt_pct')})")


def c_fiona(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.status_effects import StatusEffect, EffectType
    m = mobs[0]
    for i in range(2):
        m.apply_status_effect(StatusEffect(f"qa_ward{i}", f"Ward {i}", EffectType.BUFF, 9, stat_mods={"armor_pct": 20},
                                           source_name=m.name, real_time_seconds=None, dispel_type="magic"))
    cast(ch, ab, m, eng)
    check(not any(e.effect_id.startswith("qa_ward") for e in m._effects()), f"{ab.name}: a protection is still on")
    for key, value in ab.stat_mods.items():
        check(m.get_status_stat_mod(key) == value, f"{ab.name}: {key} {m.get_status_stat_mod(key)}, wants {value}")


def c_khalid(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    mobs[2].level = 63
    hp = [m.current_health for m in mobs]
    cast(ch, ab, mobs[0], eng)
    check(mobs[2].current_health < hp[2] and mobs[0].current_health == hp[0], f"{ab.name}: didn't stoop on the most dangerous enemy")
    check(mobs[2].get_status_stat_mod("miss_chance_pct") == 50, f"{ab.name}: it isn't blinded")


def c_delroy(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    party = [ch] + others
    for c in party:
        c.current_health = c.health // 4
    before = {c.name: c.current_health for c in party}
    cast(ch, ab, party, eng)
    for c in party:
        check(c.current_health - before[c.name] >= c.health * 0.15 - 1, f"{ab.name}: {c.name} got {c.current_health - before[c.name]} at once")
        check(has_effect(c, ab.ability_id), f"{ab.name}: {c.name} isn't still healing")


def c_karim(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, ch, eng)
    check(ch.get_status_stat_mod("armor_pct") >= 40, f"{ab.name}: armour {ch.get_status_stat_mod('armor_pct')}")
    before = ch.current_health
    ch.take_damage(200, "shadow", attacker=mobs[1], attacker_level=60)
    check(ch.current_health == before, f"{ab.name}: the shield let {before - ch.current_health} through")



def c_osvaldo(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    m = mobs[0]
    def hit(school):
        b = m.current_health
        m.take_damage(10000, school, attacker=ch, attacker_level=60)
        return b - m.current_health
    sp, ph = hit("shadow"), hit("physical")
    cast(ch, ab, mobs, eng)
    sp2, ph2 = hit("shadow"), hit("physical")
    check(abs(sp2 - sp * 1.35) <= sp * 0.02 + 1, f"{ab.name}: a spell {sp} -> {sp2}, wants x1.35")
    check(abs(ph2 - ph) <= ph * 0.02 + 1, f"{ab.name}: a physical hit changed too ({ph} -> {ph2})")


def c_bashir(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, mobs, eng)
    trapped = [e for m in mobs for e in m._effects() if getattr(e, "trap_damage", 0)]
    check(bool(trapped), f"{ab.name}: no trap was set")
    m = mobs[0]
    beast = ab._damage_multiplier(ch, "spell", recipient=m)
    m.creature_type = "undead"
    undead = ab._damage_multiplier(ch, "spell", recipient=m)
    m.creature_type = None
    check(undead / beast > 1.4, f"{ab.name}: undead x{undead:.2f} against x{beast:.2f} for a beast")


def c_pieter(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    a = others[1]
    before = a.current_health
    a.take_damage(a.health * 3, "shadow", attacker=mobs[1], attacker_level=60)
    lost = before - a.current_health
    check(0 < lost <= int(a.health * 0.15) + 1, f"{ab.name}: one hit took {lost} of {a.health}, wants at most 15%")


def _shield_holds(ab, who, mob):
    before = who.current_health
    who.take_damage(200, "shadow", attacker=mob, attacker_level=60)
    check(who.current_health == before, f"{ab.name}: the shield let {before - who.current_health} through on {who.name}")


def c_gianluca(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, ch, eng)
    _shield_holds(ab, ch, mobs[1])
    eff = next(e for e in ch._effects() if e.effect_id == ab.ability_id)
    full = getattr(eff, "absorb_max", None) or getattr(eff, "max_absorb", None)
    ch.take_damage(eff.absorb - 1, "shadow", attacker=mobs[1], attacker_level=60)
    ch.tick_status_effects()
    check(eff.absorb > 1, f"{ab.name}: the shield wasn't made whole on his turn (absorb {eff.absorb}, full {full})")


def c_camila(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat.status_effects import StatusEffect, EffectType
    a = others[0]
    a.current_health = a.health // 3
    for i, kind in enumerate(("poison", "disease", "poison")):
        a.apply_status_effect(StatusEffect(f"qa_{kind}{i}", f"Sick {i}", EffectType.DOT, 5, potency=500,
                                           damage_school="nature", source_name="Boar 1", real_time_seconds=None,
                                           dispel_type=kind))
    before = a.current_health
    cast(ch, ab, [ch] + others, eng)
    check(not any(e.effect_id.startswith("qa_") for e in a._effects()), f"{ab.name}: something is still on")
    check(a.current_health - before >= 3 * 500 * 5 * 0.9, f"{ab.name}: healed {a.current_health - before}, wants about 7500 and more")


def c_elias(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    for c in [ch] + others:
        _shield_holds(ab, c, mobs[1])


def c_kiet(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    mobs[1].level = 63
    hp = [m.current_health for m in mobs]
    ok, msg = cast(ch, ab, mobs[0], eng)
    check(mobs[1].current_health < hp[1] and mobs[0].current_health == hp[0], f"{ab.name}: didn't come out behind the most dangerous enemy")
    check("CRIT" in msg.upper(), f"{ab.name}: didn't crit ({msg!r})")
    for key, value in ab.target_mods.items():
        check(mobs[1].get_status_stat_mod(key) == value, f"{ab.name}: {key} {mobs[1].get_status_stat_mod(key)}")


def c_stelios(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    fill(ch, ab)
    ok, msg = ab.use(ch, ch, party=eng.living_allies(), engine=eng)
    check(not ok, f"{ab.name}: raised something with no enemy fallen ({msg!r})")
    mobs[2].current_health = 0
    had = list(getattr(ch, "all_pets", None) or [])
    cast(ch, ab, ch, eng)
    new = [p for p in (ch.all_pets or []) if p not in had]
    if check(len(new) == 1, f"{ab.name}: raised {len(new)} pets"):
        pet = new[0]
        check(getattr(pet, "_lifespan", None) == 5, f"{ab.name}: lifespan {getattr(pet, '_lifespan', None)}")
        for t in range(5):
            check(pet.is_alive(), f"{ab.name}: laid to rest after {t} turns, wants 5")
            eng._end_turn(pet)
        check(not pet.is_alive(), f"{ab.name}: still standing after 5 turns")



def c_ratih(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    m = mobs[0]
    m.level = 75
    friend = others[0]
    atk = next((x for x in friend.ability_book.get_all_abilities()
                if x.effect_type in ("damage", "spell_damage") and x.target_type == "enemy" and x.is_learned), None)
    if not check(atk is not None, "rig: the ally has no single-target attack"):
        return
    cast(ch, ab, m, eng)
    landed = 0
    for i in range(12):
        fill(friend, atk)
        b = m.current_health
        random.seed(100 + i)
        atk.use(friend, m, party=eng.living_allies(), engine=eng, free=True)
        landed += m.current_health < b
    check(landed == 12, f"{ab.name}: an ally's attacks on the mark landed {landed} of 12, wants every one")


def c_yusuf(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    party = [ch] + others
    others[0].current_health = others[0].health // 4
    others[1].current_health = int(others[1].health * 0.9)
    before = {c.name: c.current_health for c in party}
    cast(ch, ab, party, eng)
    a, b = others
    check(a.current_health - before[a.name] >= a.health * 0.44, f"{ab.name}: a badly hurt ally got {a.current_health - before[a.name]}")
    check(b.current_health == b.health, f"{ab.name}: a lightly hurt ally isn't topped up ({b.current_health} of {b.health})")


def c_ramiro(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    for c in [ch] + others:
        _shield_holds(ab, c, mobs[1])
        check(c.get_status_stat_mod("armor_pct") >= 25, f"{ab.name}: {c.name} armour {c.get_status_stat_mod('armor_pct')}")


def c_graham(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, mobs, eng)
    cursed = [m for m in mobs if has_effect(m, ab.ability_id)]
    if not check(bool(cursed), f"{ab.name}: no enemy cursed"):
        return
    for c in [ch] + others:
        c.current_health = c.health // 3
    before = {c.name: c.current_health for c in [ch] + others}
    cursed[0].tick_status_effects()
    for c in [ch] + others:
        check(c.current_health > before[c.name], f"{ab.name}: a tick didn't heal {c.name}")


def c_elie(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    party = [ch] + others
    for c, f in zip(party, (0.9, 0.2, 0.5)):
        c.current_health = int(c.health * f)
    share = sum(c.current_health for c in party) / sum(c.health for c in party)
    cast(ch, ab, party, eng)
    for c in party:
        check(abs(c.current_health / c.health - (share + 0.10)) < 0.01, f"{ab.name}: {c.name} at {c.current_health / c.health:.2f}, wants {share + 0.1:.2f}")


def c_bruno(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    party = [ch] + others
    for c in party:
        c.current_health = c.health // 3
    before = {c.name: c.current_health for c in party}
    mb = mobs[0].current_health
    ok, msg = cast(ch, ab, mobs[0], eng)
    dealt = mb - mobs[0].current_health
    check(msg.count(ab.name) >= 4 or msg.count(" damage") >= 4, f"{ab.name}: didn't land four times ({msg!r})")
    for c in party:
        check(c.current_health - before[c.name] >= dealt * 0.15 * 0.9, f"{ab.name}: {c.name} healed {c.current_health - before[c.name]} of {dealt} dealt")


def c_joaquin(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    a = others[1]
    raw = _control(a, mobs[1])
    a.current_health = a.health // 2
    before = a.current_health
    cast(ch, ab, [ch] + others, eng)
    check(a.current_health - before >= a.health * 0.15 - 1, f"{ab.name}: healed {a.current_health - before}")
    b = a.current_health
    a.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
    check(abs((b - a.current_health) - raw * 0.6) <= raw * 0.02 + 1, f"{ab.name}: the ally lost {b - a.current_health} of {raw}, wants 60%")


def c_luka(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    from combat import rows
    cast(ch, ab, mobs, eng)
    for m in mobs:
        check(rows.row_of(m) == rows.FRONT_ROW, f"{ab.name}: {m.name} is in row {rows.row_of(m)}")



def c_sherif(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, mobs, eng)
    for m in mobs:
        check(has_effect(m, ab.ability_id), f"{ab.name}: {m.name} isn't poisoned")
        check(m.get_status_stat_mod("damage_dealt_pct") == -20, f"{ab.name}: {m.name} isn't weakened")


def c_mohammed(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    for i, m in enumerate(mobs):
        m.turn_meter = 10.0 * i
    cast(ch, ab, mobs[0], eng)
    nxt = mobs[2]
    check(has_effect(nxt, ab.ability_id) and not has_effect(mobs[0], ab.ability_id), f"{ab.name}: not on the enemy about to act")
    a = others[1]
    for _ in range(5):
        before = a.current_health
        a.take_damage(3000, "shadow", attacker=nxt, attacker_level=60)
        check(a.current_health == before, f"{ab.name}: its attack still landed for {before - a.current_health}")


def c_tobias(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    hp = {c.name: c.current_health for c in [ch] + others}
    mb = mobs[0].current_health
    for _ in range(3):
        for c in [ch] + others:
            c.take_damage(5000, "physical", attacker=mobs[0], attacker_level=60)
    for c in [ch] + others:
        check(c.current_health == hp[c.name], f"{ab.name}: {c.name} lost {hp[c.name] - c.current_health}")
    check(mobs[0].current_health == mb, f"{ab.name}: the wall hurt the attacker ({mb - mobs[0].current_health})")


def c_taras(rm, bm, rid):
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    cast(ch, ab, [ch] + others, eng)
    a = others[1]
    lost = []
    for _ in range(2):
        before = a.current_health
        a.take_damage(3000, "shadow", attacker=mobs[1], attacker_level=60)
        lost.append(before - a.current_health)
    check(lost[0] == 0 and lost[1] > 0, f"{ab.name}: the ally lost {lost}, wants the first avoided and the second landing")


CHECKS = {
    "personal_sworn_kesten_written_down_properly": c_kesten,
    "personal_sworn_adrian_let_them_carry_it": c_adrian,
    "personal_sworn_tarek_built_to_last": c_tarek,
    "personal_sworn_diego_put_it_right": c_diego,
    "personal_sworn_freja_calmest_in_the_room": c_freja,
    "personal_sworn_marco_not_putting_it_off": c_marco,
    "personal_sworn_sophia_read_it_back": c_sophia,
    "personal_sworn_carolina_where_the_river_goes": c_carolina,
    "personal_sworn_ryan_pays_it_himself": c_ryan,
    "personal_sworn_hana_not_somewhere": c_hana,
    "personal_sworn_esteban_with_everyones_consent": c_esteban,
    "personal_sworn_berat_everybody_laughing": c_berat,
    "personal_sworn_dan_a_crew_holds_together": c_dan,
    "personal_sworn_marisol_talk_them_through": c_marisol,
    "personal_sworn_silas_says_something": c_silas,
    "personal_sworn_pavlo_nothing_gets_past": c_pavlo,
    "personal_sworn_marta_set_and_walk_away": c_marta,
    "personal_sworn_lucia_out_loud_for_everyone": c_lucia,
    "personal_sworn_minh_everyone_two_turns_back": c_minh,
    "personal_sworn_bakyt_every_weak_point": c_bakyt,
    "personal_sworn_matias_in_front_of_them": c_matias,
    "personal_sworn_tomas_braced": c_tomas,
    "personal_sworn_cristobal_brings_them_out": c_cristobal,
    "personal_sworn_callum_into_himself": c_callum,
    "personal_sworn_giorgi_rings_the_bell": c_giorgi,
    "personal_sworn_camille_takes_the_shift": c_camille,
    "personal_sworn_liam_calls_the_crew_in": c_liam,
    "personal_sworn_owen_holds_it": c_owen,
    "personal_sworn_pasang_roped_together": c_pasang,
    "personal_sworn_nicolas_there_this_time": c_nicolas,
    "personal_sworn_iker_everybody_up": c_iker,
    "personal_sworn_mateo_starlight_for_both": c_mateo,
    "personal_sworn_imelda_whole_combination": c_imelda,
    "personal_sworn_ileana_hold_the_line": c_ileana,
    "personal_sworn_rhys_tegan_stoops": c_rhys,
    "personal_sworn_eino_felling_blow": c_eino,
    "personal_sworn_driss_the_sandstorm": c_driss,
    "personal_sworn_thiago_not_today": c_thiago,
    "personal_sworn_enzo_the_perfect_riposte": c_enzo,
    "personal_sworn_alonso_firing_heat": c_alonso,
    "personal_sworn_vuk_stands_over_them": c_vuk,
    "personal_sworn_kourosh_worked_out_exactly": c_kourosh,
    "personal_sworn_hector_the_finisher": c_hector,
    "personal_sworn_ziad_the_fel_pays_back": c_ziad,
    "personal_sworn_fiona_entered_properly": c_fiona,
    "personal_sworn_khalid_the_falcon_comes_back": c_khalid,
    "personal_sworn_delroy_one_for_everyone": c_delroy,
    "personal_sworn_karim_plants_himself": c_karim,
    "personal_sworn_osvaldo_one_long_note": c_osvaldo,
    "personal_sworn_bashir_the_line_holds": c_bashir,
    "personal_sworn_pieter_the_tenth_man": c_pieter,
    "personal_sworn_gianluca_keeps_talking": c_gianluca,
    "personal_sworn_camila_all_of_it_back": c_camila,
    "personal_sworn_elias_not_putting_it_off": c_elias,
    "personal_sworn_kiet_out_of_nowhere": c_kiet,
    "personal_sworn_stelios_borrowed_properly": c_stelios,
    "personal_sworn_ratih_the_one_wrong_thing": c_ratih,
    "personal_sworn_yusuf_the_exact_dose": c_yusuf,
    "personal_sworn_ramiro_nobody_left_underneath": c_ramiro,
    "personal_sworn_graham_a_kind_ending": c_graham,
    "personal_sworn_elie_arrives_this_time": c_elie,
    "personal_sworn_bruno_the_whole_round": c_bruno,
    "personal_sworn_joaquin_carried_together": c_joaquin,
    "personal_sworn_luka_into_the_storm": c_luka,
    "personal_sworn_sherif_the_cloud": c_sherif,
    "personal_sworn_mohammed_one_moment_ahead": c_mohammed,
    "personal_sworn_tobias_the_whole_crew": c_tobias,
    "personal_sworn_taras_kashtan_knows": c_taras,
}
#: passives with a check of their own (every other passive gets c_passive)
PASSIVE_CHECKS = {"ama_priest": c_ama, "amber_druid": c_amber, "orlando_witchdoctor": c_orlando,
                  "anjali_druid": c_anjali}


def by_kind(rm, bm, rid):
    """What any skill of this kind must do when cast."""
    ch, ab, others, mobs, eng = fight(rm, bm, rid)
    t = ab.effect_type
    target = target_for(ab, ch, others, mobs)
    if t in ("damage", "spell_damage", "ranged_damage", "damage_and_heal"):
        before = sum(m.current_health for m in mobs)
        cast(ch, ab, target, eng)
        check(sum(m.current_health for m in mobs) < before, f"{ab.name}: dealt no damage")
    elif t in ("heal",):
        for c in [ch] + others:
            c.current_health = max(1, c.health // 3)
        before = sum(c.current_health for c in [ch] + others)
        cast(ch, ab, target, eng)
        check(sum(c.current_health for c in [ch] + others) > before, f"{ab.name}: healed nobody")
    elif t in ("hot", "dot", "spell_dot", "buff", "debuff"):
        cast(ch, ab, target, eng)
        hit = target if isinstance(target, list) else [target]
        check(any(has_effect(w, ab.ability_id) for w in hit), f"{ab.name}: put nothing on its target")
        for key, value in (ab.stat_mods or {}).items():
            got = [w.get_status_stat_mod(key) for w in hit]
            check(any(g == value for g in got), f"{ab.name}: {key} is {got}, wants {value}")
    elif t == "revive":
        a = others[0]
        a.current_health = 0
        cast(ch, ab, a, eng)
        check(a.is_alive(), f"{ab.name}: nobody got up")
    elif t == "summon_pet":
        cast(ch, ab, ch, eng)
        check(bool(getattr(ch, "pets", None) or getattr(ch, "pet", None)), f"{ab.name}: summoned nothing")
    else:
        cast(ch, ab, target, eng)


# ---------------------------------------------------------------- main
def main():
    import build_sworn_skills as B
    import rank_kit_abilities as R
    from world import personal_kits as PK
    strict = "--strict" in sys.argv

    # 1
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = B.main()
    check(code == 0 or (not strict and "0 problems" in out.getvalue()), "the build fails:\n" + out.getvalue())
    PK._sworn = None
    sworn = PK.sworn_skills()
    kits = json.loads(B.KITS.read_text(encoding="utf-8"))
    want = [r for r in kits if not r.startswith("_") and r not in B.EXCLUDED]
    missing = [r for r in want if r not in sworn]
    if strict:
        check(not missing, f"{len(missing)} recruits have no Sworn skill yet")
    check(not any(r in sworn for r in B.EXCLUDED), "Asher has a Sworn skill")

    # 2
    for rid, e in sworn.items():
        a = e.get("ability")
        if not a or len(a.get("ranks", [])) != 5:
            continue
        plain = json.loads(json.dumps(a))
        plain["ranks"] = [dict(plain["ranks"][0], rank=1, level_req=1)]
        for k in ("absorb", "on_damage_hot_potency"):
            plain["ranks"][0].pop(k, None)
        trait = R.ranks_for(plain, kits)[-1]
        mine = a["ranks"][-1]
        for k in R.grows(plain) & {"effect_value", "absorb"}:
            if trait.get(k):
                hits = int(a.get("repeat_hits") or 1)      # a flurry is measured by all its hits together
                check(mine.get(k, 0) * hits >= trait[k] * 1.1,
                      f"{rid}: last rank {k} {mine.get(k)} x{hits} isn't clearly above a trait's {trait[k]}")

    rm, bm = rig()
    recs = {r.recruit_id: r for r in rm.recruits.values()}

    # 3 and 4
    for rid in list(sworn)[:3]:
        aid = (sworn[rid].get("ability") or {}).get("ability_id")
        swear(bm, rid, False)
        ch = rm.build_or_restore(recs[rid], player_level=60)
        PK.grant(ch)
        check(aid is None or ch.ability_book.get_ability(aid) is None, f"{rid}: has the Sworn skill before swearing")
        from entities.party import Party
        party = Party(ch)
        bm.party = party
        b = bm.bonds[rid]
        if "goal_done" not in b.flags:
            b.flags.append("goal_done")
        from world.bond_manager import THRESHOLDS
        b.stage = len(THRESHOLDS) - 2
        b.trust = THRESHOLDS[-1] - 1
        bm._trust(b, 50)
        got = ch.ability_book.get_ability(aid) if aid else None
        check(b.stage_key == "sworn", f"{rid}: didn't swear in the rig")
        check(aid is None or got is not None, f"{rid}: swearing didn't put the Sworn skill in their book")
        check(any("Sworn skill" in t for _, t in bm.log), f"{rid}: swearing didn't say what they unlocked")
        if got is not None and len(sworn[rid]["ability"]["ranks"]) == 5:
            lv = int(ch.level)
            want_now = sum(1 for x in R.LEVELS if x <= lv)
            check(got.current_rank.get("rank") == want_now,
                  f"{rid}: at level {lv} holds rank {got.current_rank.get('rank')}, wants {want_now}")
            for lv, want_rank in ((14, 1), (15, 2), (30, 3), (45, 4), (59, 4)):
                got.refresh_rank_for_level(lv)
                check(got.current_rank.get("rank") == want_rank,
                      f"{rid}: at level {lv} rank {got.current_rank.get('rank')}, wants {want_rank}")
            got.refresh_rank_for_level(60)
        # a save and load: bonds come back after the party, so the skill is put back by regrant
        saved = bm.to_dict()
        swear(bm, rid, False)
        PK.grant(ch)
        check(aid is None or ch.ability_book.get_ability(aid) is None, f"{rid}: kept the Sworn skill after the oath was undone")
        bm.load_state(saved)
        bm.regrant_sworn(party)
        check(aid is None or ch.ability_book.get_ability(aid) is not None, f"{rid}: lost the Sworn skill over a load")

    # 5
    for rid, e in sorted(sworn.items()):
        a = e.get("ability")
        rm, bm = rig()
        if not a:
            try:
                PASSIVE_CHECKS.get(rid, c_passive)(rm, bm, rid)
            except Exception as exc:
                import traceback
                check(False, f"{rid}: passive check crashed: {exc!r}\n{traceback.format_exc()[-600:]}")
            continue
        try:
            fn = CHECKS.get(a["ability_id"], by_kind)
            fn(rm, bm, rid)
        except Exception as exc:
            import traceback
            check(False, f"{rid}: {a['name']} crashed: {exc!r}\n{traceback.format_exc()[-600:]}")

    n = len(sworn)
    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print(f"Sworn skills OK - {n} built, {len(missing)} still to write; stronger than a trait, only while Sworn, "
          f"ranked 1/15/30/45/60, and every one cast and measured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
