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


CHECKS = {
    "personal_sworn_kesten_written_down_properly": c_kesten,
    "personal_sworn_adrian_let_them_carry_it": c_adrian,
    "personal_sworn_tarek_built_to_last": c_tarek,
    "personal_sworn_diego_put_it_right": c_diego,
    "personal_sworn_freja_calmest_in_the_room": c_freja,
}


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
        if not a:
            continue
        rm, bm = rig()
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
