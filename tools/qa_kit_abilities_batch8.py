#!/usr/bin/env python3
"""Six more recruit abilities that cast and did nothing, each used in a real exchange.

    python3 tools/qa_kit_abilities_batch8.py

Pavlo (enemies that repeat themselves hit softer), Imelda (the duel), Khalid (the trap),
Owen (lapsed buffs come back), Marta (devices hit harder), Gianluca (the right resistance).
"""
import json
import os
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

    def setup(ability_name, kinds=("humanoid_warrior", "humanoid_warrior")):
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
                    mobs = [Monster(f"Kolkar {i + 1}", kind, ch.level) for i, kind in enumerate(kinds)]
                    for m in mobs:
                        m.max_health = m.current_health = 10 ** 7
                    eng = CombatEngine(ch, mobs[0], party=Party(ch), enemies=mobs)
                    ch.health = ch.current_health = 10 ** 6
                    ch.dodge = ch.parry = 0.0
                    return ch, ab, mobs, eng
        raise KeyError(ability_name)

    # ---- Pavlo: an enemy that repeats itself hits softer ----
    ch, ab, mobs, eng = setup("The Same Four Wars Every Spring")
    ok, msg = ab.use(ch, mobs, party=[ch], engine=eng)
    foe = mobs[0]
    # world/difficulty.py scales every open-world monster's output; these abilities act on top
    from world import difficulty
    D = difficulty.factor(foe, "damage")
    check(ok and abs(foe.damage_output_multiplier / D - 1.0) < 1e-9, f"Same Four Wars: softer before anything was repeated ({foe.damage_output_multiplier}, {msg!r})")
    slash = foe.abilities[0]
    outs = []
    for _ in range(4):
        slash.turns_remaining = 0
        slash.use(foe, ch, engine=eng)
        outs.append(round(foe.damage_output_multiplier / D, 2))
    check(outs == [1.0, 0.75, 0.5, 0.5], f"Same Four Wars: output went {outs}, wanted 1.0, 0.75, 0.5, 0.5")

    # ---- Imelda: the duel ----
    ch, ab, mobs, eng = setup("Rules, A Count, Somebody Keeping Time")
    basic = ch.ability_book.abilities[ch.get_basic_attack_id()]
    mine = basic._damage_multiplier(ch, "physical", mobs[0])
    ok, _ = ab.use(ch, mobs[0], party=[ch], engine=eng)
    check(ok and abs(mobs[0].damage_output_multiplier / D - 1.3) < 1e-9, f"Duel: the target deals x{mobs[0].damage_output_multiplier / D}, wanted 1.3")
    check(basic._damage_multiplier(ch, "physical", mobs[0]) - mine >= 0.29, "Duel: Imelda deals no more to it")
    check(basic._damage_multiplier(ch, "physical", mobs[1]) - mine < 0.01, "Duel: Imelda deals more to the other enemy too")
    check(any(ev for ev in (getattr(ab, "_last_threat_events", None) or [])), "Duel: nothing holds the target on her")

    # ---- Khalid: the trap ----
    ch, ab, mobs, eng = setup("Exactly Where He Said He Would Be")
    ok, _ = ab.use(ch, mobs, party=[ch], engine=eng)
    trapped = [m for m in mobs if any(getattr(e, "trap_damage", 0) for e in m.active_effects)]
    check(ok and len(trapped) == 2, f"Trap: laid on {len(trapped)} enemies, wanted the row of 2")
    hp_me, hp_foe = ch.current_health, mobs[0].current_health
    eng.current_actor = mobs[0]
    eng.execute_monster_action()
    check(mobs[0].current_health < hp_foe, "Trap: the first to act took no damage")
    check(ch.current_health == hp_me, "Trap: the trapped enemy still got its attack off")
    check(not any(getattr(e, "trap_damage", 0) for m in mobs for e in m.active_effects), "Trap: still armed after it went off")
    eng.current_actor = mobs[1]
    eng.execute_monster_action()
    check(ch.current_health < hp_me or any("Kolkar 2" in l for l in eng.combat_log[-3:]), "Trap: the second enemy did not act normally")

    # ---- Owen: lapsed buffs come back ----
    ch, ab, mobs, eng = setup("A Record of the Route")
    ch.apply_status_effect(StatusEffect("t_ward", "Test Ward", EffectType.BUFF, 1, stat_mods={"armor": 50},
                                        real_time_seconds=None))
    for _ in range(3):
        if any(e.effect_id == "t_ward" for e in ch.active_effects):
            ch.tick_status_effects()
    check(not any(e.effect_id == "t_ward" for e in ch.active_effects), "Record: harness - the ward did not lapse")
    ok, msg = ab.use(ch, ch, party=[ch], engine=eng)
    back = next((e for e in ch.active_effects if e.effect_id == "t_ward"), None)
    check(ok and back is not None and back.duration >= 1, f"Record: the lapsed ward did not come back ({msg!r})")
    for _ in range(6):
        ch.tick_status_effects()
    ab.turns_remaining = 0
    ok, msg = ab.use(ch, ch, party=[ch], engine=eng)
    check(not any(e.effect_id == "t_ward" for e in ch.active_effects), "Record: brought back a buff that lapsed long ago")

    # ---- Marta: devices hit harder ----
    ch, ab, mobs, eng = setup("Fixes It Properly")
    summon = next((x for x in ch.ability_book.get_all_abilities()
                   if getattr(x, "effect_type", "") == "summon_pet"), None)
    if summon is None:
        check(False, "Fixes It Properly: Marta has nothing to summon in this build")
    else:
        summon.use(ch, ch, party=[ch], engine=eng)
        eng.sync_pets()
        pet = getattr(ch, "active_pet", None)
        check(pet is not None, "Fixes It Properly: harness - no device came out")
        if pet is not None:
            ok, msg = ab.use(ch, pet, party=[ch], engine=eng)
            held = [e for e in (getattr(pet, "active_effects", None) or []) if e.effect_id == ab.ability_id]
            check(ok and held and held[0].stat_mods.get("damage_dealt_pct") == 20, f"Fixes It Properly: not on the device ({msg!r})")
            check(not any(e.effect_id == ab.ability_id for e in ch.active_effects), "Fixes It Properly: landed on Marta")
            pa = next((x for x in pet.ability_book.get_all_abilities()), None) if hasattr(pet, "ability_book") else None
            if pa is not None and held:
                with_buff = pa._damage_multiplier(pet, "physical", mobs[0])
                pet._discard_effect(held[0])
                check(with_buff > pa._damage_multiplier(pet, "physical", mobs[0]), "Fixes It Properly: the device hits no harder")

    # ---- Gianluca: the right resistance ----
    ch, ab, mobs, eng = setup("He Already Knew", kinds=("humanoid_caster", "humanoid_caster"))
    school = ab._anticipated_school(eng)
    ok, _ = ab.use(ch, ch, party=[ch], engine=eng)
    held = next((e for e in ch.active_effects if e.effect_id == ab.ability_id), None)
    check(school and held is not None and held.stat_mods.get(f"{school}_resistance") == 25,
          f"He Already Knew: casters use {school}, buff gave {held and held.stat_mods}")
    ch, ab, mobs, eng = setup("He Already Knew", kinds=("beast_basic",))
    if ab._anticipated_school(eng) is None:
        ab.use(ch, ch, party=[ch], engine=eng)
        held = next((e for e in ch.active_effects if e.effect_id == ab.ability_id), None)
        check(held is not None and held.stat_mods.get("physical_damage_taken_pct") == -10,
              f"He Already Knew: no magic about, buff gave {held and held.stat_mods}")

    print("6 abilities: reuse stacks, duel, trap, lapsed buffs, devices, anticipated resistance")
    if bad:
        print("FAIL:")
        for b in bad:
            print("  " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
