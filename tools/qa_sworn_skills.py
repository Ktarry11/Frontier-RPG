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
    ab = ch.ability_book.get_ability(PK.sworn_skills()[rid]["ability"]["ability_id"])
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
        a.take_damage(a.health, "physical", attacker=mobs[0], attacker_level=60)
    check(a.is_alive() and a.current_health >= floor - 1,
          f"{ab.name}: four big hits left {a.current_health}, wants at least {floor}")


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
}
#: passives with a check of their own (every other passive gets c_passive)
PASSIVE_CHECKS = {"ama_priest": c_ama, "amber_druid": c_amber}


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
                check(mine.get(k, 0) >= trait[k] * 1.1,
                      f"{rid}: last rank {k} {mine.get(k)} isn't clearly above a trait's {trait[k]}")

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
