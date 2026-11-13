#!/usr/bin/env python3
"""The final pass: every recruit ability read against its own text, and the last gaps closed.

    python3 tools/qa_kit_abilities_batch11.py

Fourteen more used in a real fight, and one standing rule: no ability in the kits may carry
a note saying a mechanic is still needed.
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

    doc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}
    owner = {a["name"]: (kid, a["ability_id"]) for kid, kit in doc.items() if not kid.startswith("_")
             for a in kit["abilities"]}

    # ---- the standing rule ----
    stale = [f"{kit['name']} / {a['name']}: {a.get('engine', '')[:60]!r}"
             for kid, kit in doc.items() if not kid.startswith("_") for a in kit["abilities"]
             if not str(a.get("engine", "")).startswith(("live", "existing"))]
    check(not stale, f"{len(stale)} abilities still noted as unfinished: {stale[:4]}")

    def fill(ch, ab=None):
        for res in ("rage", "energy", "mana", "focus", "power"):
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

    def setup(name, friends=1, foes=("beast_basic",)):
        kid, aid = owner[name]
        ch = recs[kid].build_character()
        ab = next(x for x in ch.ability_book.get_all_abilities() if x.ability_id == aid)
        others = [recs[k].build_character() for k in list(recs) if k != kid and k in doc][:friends]
        party = Party(ch)
        for o in others:
            party.members.append(o)
        mobs = [Monster(f"Boar {i + 1}", kind, ch.level) for i, kind in enumerate(foes)]
        for m in mobs:
            m.max_health = m.current_health = 10 ** 7
            m.dodge = m.parry = 0.0
        eng = CombatEngine(ch, mobs[0], party=party, enemies=mobs)
        for c in [ch] + others:
            c.current_health = c.health
            c.dodge = c.parry = 0.0
        return ch, ab, others, mobs, eng

    def at(c, frac):
        c.current_health = max(1, int(c.health * frac))
        return c.current_health

    def cast(ch, ab, target, eng, seed=7, expect=True):
        fill(ch, ab)
        random.seed(seed)
        ok, msg = ab.use(ch, target, party=eng.living_allies(), engine=eng)
        if ok != expect:
            bad.append(f"{ab.name}: cast returned {ok} ({msg!r})")
        return msg

    def basic(c):
        return c.ability_book.abilities[c.get_basic_attack_id()]

    # Emre: a kill gives him his turn back
    ch, ab, others, mobs, eng = setup("One Door Closes", foes=("beast_basic", "beast_basic"))
    cast(ch, ab, ch, eng)
    from config import TURN_THRESHOLD
    ch.turn_meter = 0.0
    for seed in range(8):
        mobs[0].max_health = mobs[0].current_health = 1
        cast(ch, basic(ch), mobs[0], eng, seed=seed)
        if not mobs[0].is_alive():
            break
    check(not mobs[0].is_alive() and ch.turn_meter >= TURN_THRESHOLD, f"One Door Closes: killed={not mobs[0].is_alive()}, turn meter {ch.turn_meter}")

    # Vuk: his own +25% against the taunted target
    ch, ab, others, mobs, eng = setup("Too Irritated to Leave It Alone", foes=("beast_basic", "beast_basic"))
    base = basic(ch)._damage_multiplier(ch, "physical", mobs[0])
    cast(ch, ab, mobs[0], eng)
    check(basic(ch)._damage_multiplier(ch, "physical", mobs[0]) - base >= 0.24
          and abs(basic(ch)._damage_multiplier(ch, "physical", mobs[1]) - base) < 0.01, "Too Irritated: Vuk's +25% is not on the taunted target alone")

    # the two party restores reach each ally
    for name, cap in (("Water Where There Is None", None), ("The Water Allowance", 0.5)):
        ch, ab, others, mobs, eng = setup(name, friends=3)
        pools = []
        for i, c in enumerate(others):
            pool = getattr(c, "resource_type", "mana")
            top = c.get_resource_max(pool) or 0
            c.set_resource(pool, int(top * (0.1 if i < 2 else 0.9)))
            pools.append((c, pool, c.get_resource(pool), top))
        cast(ch, ab, eng.living_allies(), eng)
        low = [c.get_resource(pool) > was for c, pool, was, top in pools[:2] if top]
        check(low and all(low), f"{name}: allies low on resource got nothing")
        c, pool, was, top = pools[2]
        if cap and top:
            check(c.get_resource(pool) == was, f"{name}: an ally above half got some too")

    # dispels with a rider
    def poison(holder, source, name="t_venom"):
        holder.apply_status_effect(StatusEffect(name, "Venom", EffectType.DOT, 4, potency=10, damage_school="nature",
                                                dispel_type="poison", source_name=source.name))
    ch, ab, others, mobs, eng = setup("He Knows Doses, He Knows Poisons")
    friend = others[0]; low = at(friend, 0.3); poison(friend, mobs[0])
    cast(ch, ab, eng.living_allies(), eng)
    check(not any(e.effect_id == "t_venom" for e in friend.active_effects) and friend.current_health - low == 40,
          f"He Knows Doses: healed {friend.current_health - low}, wanted the 40 the poison had left")

    ch, ab, others, mobs, eng = setup("She Works the Rot")
    friend = others[0]; poison(friend, mobs[0]); hp = mobs[0].current_health
    cast(ch, ab, eng.living_allies(), eng)
    check(mobs[0].current_health < hp, "She Works the Rot: nothing went back to the enemy that applied it")

    ch, ab, others, mobs, eng = setup("Too Neat, and Neat Where Nobody Looks")
    for i in range(2):
        mobs[0].apply_status_effect(StatusEffect(f"t_boon{i}", f"Boon {i}", EffectType.BUFF, 9, stat_mods={"attack_power": 5},
                                                 dispel_type="magic", real_time_seconds=None))
    hp = mobs[0].current_health
    cast(ch, ab, mobs[0], eng)
    two = hp - mobs[0].current_health
    mobs[0].apply_status_effect(StatusEffect("t_boon9", "Boon 9", EffectType.BUFF, 9, stat_mods={"attack_power": 5},
                                             dispel_type="magic", real_time_seconds=None))
    hp = mobs[0].current_health
    cast(ch, ab, mobs[0], eng)
    one = hp - mobs[0].current_health
    check(one > 0 and 1.8 <= two / max(1, one) <= 2.2, f"Too Neat: two buffs taken dealt {two}, one dealt {one}")

    ch, ab, others, mobs, eng = setup("They Tie Off Badly")
    mobs[0].apply_status_effect(StatusEffect("t_boon", "Boon", EffectType.BUFF, 9, stat_mods={"attack_power": 5},
                                             dispel_type="magic", real_time_seconds=None))
    armor = mobs[0].armor
    cast(ch, ab, mobs[0], eng)
    check(armor > 0 and abs(mobs[0].armor - armor * 0.75) <= 2, f"They Tie Off Badly: armour {armor} -> {mobs[0].armor}, wanted -25%")

    # Tarek: the shield is rebuilt each turn
    ch, ab, others, mobs, eng = setup("He Calls It Building")
    cast(ch, ab, eng.living_allies(), eng)
    friend = others[0]
    shield = next((e for e in friend.active_effects if e.effect_id == ab.ability_id), None)
    full = shield.absorb if shield else 0
    if shield:
        shield.absorb = 1
        friend.tick_status_effects()
    check(shield is not None and full > 1 and shield.absorb == full, f"He Calls It Building: shield {full} -> {shield and shield.absorb} after a turn")

    # Fiona: lands on whichever enemy is closest to dying
    ch, ab, others, mobs, eng = setup("The One Entry That Doesn't Fit", foes=("beast_basic", "beast_basic"))
    mobs[1].current_health = mobs[1].max_health // 10
    hp0, hp1 = mobs[0].current_health, mobs[1].current_health
    for seed in range(6):
        cast(ch, ab, mobs[0], eng, seed=seed)
    check(mobs[0].current_health == hp0 and mobs[1].current_health < hp1, "The One Entry: did not go to the enemy closest to dying")

    # Eino: nothing from anybody else's buffs
    ch, ab, others, mobs, eng = setup("Six Months of Dark")
    cast(ch, ab, ch, eng)
    msg = ch.apply_status_effect(StatusEffect("t_gift", "Gift", EffectType.BUFF, 3, stat_mods={"armor": 50},
                                              source_name=others[0].name, real_time_seconds=None))
    check(not any(e.effect_id == "t_gift" for e in ch.active_effects), f"Six Months of Dark: took an ally's buff ({msg!r})")
    check(any(e.effect_id == ab.ability_id for e in ch.active_effects), "Six Months of Dark: refused his own buff")

    # Vuk: ONE heal for the party
    ch, ab, others, mobs, eng = setup("A Second Bowl", friends=2)
    cast(ch, ab, eng.living_allies(), eng)
    gains = []
    for c in others:
        low = at(c, 0.1)
        c._check_low_health_trigger()
        gains.append(c.current_health - low)
    check(gains[0] > 0 and gains[1] == 0, f"A Second Bowl: gains {gains}, wanted the first to fall low healed and nobody else")

    # Pasang: only once somebody has fallen
    ch, ab, others, mobs, eng = setup("He Has the Names", friends=2)
    cast(ch, ab, ch, eng, expect=False)
    others[1].current_health = 0
    cast(ch, ab, ch, eng)

    # Ivan: the whole party is up at once
    ch, ab, others, mobs, eng = setup("Directing Traffic", friends=2)
    for c in [ch] + others:
        c.turn_meter = 0.0
    cast(ch, ab, eng.living_allies(), eng)
    check(all(c.turn_meter >= TURN_THRESHOLD for c in others), f"Directing Traffic: party turn meters {[c.turn_meter for c in others]}")

    # Kesten: the target's next move is shown
    ch, ab, others, mobs, eng = setup("If You Know the Hand")
    cast(ch, ab, mobs[0], eng)
    check(mobs[0] in eng.revealed_intents(), "If You Know the Hand: the target's next move is not shown")

    print("14 abilities in a real fight; no ability noted as unfinished")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
