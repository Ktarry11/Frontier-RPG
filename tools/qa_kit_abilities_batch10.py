#!/usr/bin/env python3
"""The last of the recruit abilities that hit or healed but lacked their special half.

    python3 tools/qa_kit_abilities_batch10.py

Delayed strikes, heals that grow or pay late, heals with a price or a rule, rewinds. Each is
cast in a real fight with the dice pinned and compared with the same cast when its condition
does not hold.
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
    owner = {a["name"]: (kid, a["ability_id"]) for kid, kit in doc.items() if not kid.startswith("_")
             for a in kit["abilities"]}

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
        """The caster, `friends` other recruits in the party, monsters, a live engine."""
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
        """Put c at this share of their real maximum health; return the number."""
        c.current_health = max(1, int(c.health * frac))
        return c.current_health

    def cast(ch, ab, target, eng, seed=7):
        fill(ch, ab)
        random.seed(seed)
        party = eng.living_allies()
        ok, msg = ab.use(ch, target, party=party, engine=eng)
        if not ok:
            bad.append(f"{ab.name}: would not cast ({msg!r})")
        return msg

    def heal_gain(ch, ab, who, eng, start, seed=7, target=None):
        start = at(who, start)
        cast(ch, ab, who if target is None else target, eng, seed)
        return who.current_health - start

    def ratio(a, b):
        return a / b if b else 0.0

    # ---------------- delayed ----------------
    for name, turns in (("The Lift Takes Its Time", 2), ("Hanging Weight Overhead", 2)):
        ch, ab, others, mobs, eng = setup(name, foes=("beast_basic", "beast_basic"))
        aim = mobs if ab.target_type != "enemy" else mobs[0]
        hp = [m.current_health for m in mobs]
        msg = cast(ch, ab, aim, eng)
        check(all(m.current_health == h for m, h in zip(mobs, hp)), f"{name}: landed at once ({msg!r})")
        landed_after = None
        for t in range(1, 5):
            eng._end_turn(ch)
            if any(m.current_health < h for m, h in zip(mobs, hp)):
                landed_after = t
                break
        check(landed_after == turns + 1, f"{name}: landed after {landed_after} turn-ends, wanted {turns + 1} (the casting turn and {turns} more)")
        if ab.target_type != "enemy":
            # aimed at both: one of them may still be missed, which is the dice, not the ability
            line = " ".join(eng.combat_log[-2:])
            check(all(m.name in line for m in mobs), f"{name}: was not aimed at the whole row ({line!r})")

    ch, ab, others, mobs, eng = setup("An Order Going Out at Dawn", friends=2)
    low = [at(c, 0.1) for c in others]
    at(ch, 0.1)
    cast(ch, ab, eng.living_allies(), eng)
    check([c.current_health for c in others] == low, "Order at Dawn: healed at once")
    eng._end_turn(ch); mid = [c.current_health for c in others]
    eng._end_turn(ch); late = [c.current_health for c in others]
    check(mid == low and all(v > l for v, l in zip(late, low)), f"Order at Dawn: start {low}, after one turn {mid}, after two {late}")

    ch, ab, others, mobs, eng = setup("Finish the Sum")
    cast(ch, ab, mobs[0], eng)
    spell = next(x for x in ch.ability_book.get_all_abilities()
                 if getattr(x, "effect_type", "") == "spell_damage" and not x.ability_id.startswith("personal_"))
    eng._end_turn(ch)
    hp = mobs[0].current_health
    for i in range(2):
        cast(ch, spell, mobs[0], eng, seed=20 + i)
        eng._end_turn(ch)
    dealt = hp - mobs[0].current_health
    hp = mobs[0].current_health
    eng._end_turn(ch)
    due = hp - mobs[0].current_health
    check(dealt > 0 and 0.4 * dealt <= due <= 1.6 * dealt, f"Finish the Sum: he dealt {dealt} in between, the sum paid {due}")

    # ---------------- heals that grow ----------------
    ch, ab, others, mobs, eng = setup("Slow and Correct")
    friend = others[0]; at(friend, 0.02)
    cast(ch, ab, friend, eng)
    ticks = []
    for _ in range(5):
        before = friend.current_health; friend.tick_status_effects(); ticks.append(friend.current_health - before)
    check(ticks[0] > 0 and all(1.3 <= ratio(b, a) <= 1.5 for a, b in zip(ticks, ticks[1:])), f"Slow and Correct: ticks {ticks}, wanted +40% each")

    for name, last in (("Exactly Right", 3.0), ("Several Seasons for the Sentence to Finish", 5.0)):
        ch, ab, others, mobs, eng = setup(name)
        friend = others[0]; at(friend, 0.02)
        cast(ch, ab, friend, eng)
        ticks = []
        for _ in range(4):
            before = friend.current_health; friend.tick_status_effects(); ticks.append(friend.current_health - before)
        check(ticks[0] > 0 and abs(ratio(ticks[3], ticks[0]) - last) <= 0.2 and ticks[1] == ticks[0], f"{name}: ticks {ticks}, wanted the last x{last:g}")

    ch, ab, others, mobs, eng = setup("Just Sitting There")
    friend = others[0]; at(friend, 0.02)
    cast(ch, ab, friend, eng)
    ch._attacked_last_turn = False
    b = friend.current_health; friend.tick_status_effects(); idle = friend.current_health - b
    ch._attacked_last_turn = True
    b = friend.current_health; friend.tick_status_effects(); busy = friend.current_health - b
    check(1.4 <= ratio(idle, busy) <= 1.6, f"Just Sitting There: idle tick {idle}, busy tick {busy}, wanted x1.5")

    ch, ab, others, mobs, eng = setup("Sit Down, Tell Me What Is Wrong")
    friend = others[0]; at(friend, 0.02)
    for i in range(2):
        friend.apply_status_effect(StatusEffect(f"t_hex{i}", f"Hex {i}", EffectType.DEBUFF, 9, stat_mods={"armor": -5},
                                                real_time_seconds=None))
    cast(ch, ab, friend, eng)
    left = []
    for _ in range(2):
        friend.tick_status_effects()
        left.append(sum(1 for e in friend.active_effects if e.effect_id.startswith("t_hex")))
    check(left == [1, 0], f"Sit Down: harmful effects left after each tick {left}, wanted [1, 0]")

    ch, ab, others, mobs, eng = setup("Learning Them From Scratch")
    friend = others[0]
    early = heal_gain(ch, ab, friend, eng, 0.02)
    ch._fight_turns = 10
    late = heal_gain(ch, ab, friend, eng, 0.02)
    ch._fight_turns = 40
    capped = heal_gain(ch, ab, friend, eng, 0.02)
    check(1.9 <= ratio(late, early) <= 2.1 and capped == late, f"Learning Them: turn 0 {early}, turn 10 {late}, turn 40 {capped}")

    ch, ab, others, mobs, eng = setup("When Called and All At Once", friends=3)
    watch = others[0]
    for o in others:
        at(o, 0.9)
    calm = heal_gain(ch, ab, watch, eng, 0.6, target=eng.living_allies())
    at(others[1], 0.02); at(others[2], 0.02)
    urgent = heal_gain(ch, ab, watch, eng, 0.6, target=eng.living_allies())
    check(1.4 <= ratio(urgent, calm) <= 1.6, f"When Called: nobody low {calm}, two below half {urgent}, wanted x1.5")

    ch, ab, others, mobs, eng = setup("One Hundred and Forty", friends=3)
    watch = others[0]
    whole = heal_gain(ch, ab, watch, eng, 0.02, target=eng.living_allies())
    others[2].current_health = 0
    short = heal_gain(ch, ab, watch, eng, 0.02, target=eng.living_allies())
    check(1.3 <= ratio(short, whole) <= 1.5, f"One Hundred and Forty: all standing {whole}, one down {short}, wanted x1.4")

    ch, ab, others, mobs, eng = setup("Relentlessly Encouraging")
    friend = others[0]
    friend._turns_below_half = 0
    fresh = heal_gain(ch, ab, friend, eng, 0.02)
    friend._turns_below_half = 2
    worn = heal_gain(ch, ab, friend, eng, 0.02)
    friend._turns_below_half = 30
    cap = heal_gain(ch, ab, friend, eng, 0.02)
    check(1.5 <= ratio(worn, fresh) <= 1.7 and 2.8 <= ratio(cap, fresh) <= 3.2, f"Relentlessly: {fresh}, two turns low {worn}, long low {cap}")
    friend._turns_below_half = 0; at(friend, 0.1); friend.tick_status_effects(); friend.tick_status_effects()
    check(friend._turns_below_half == 2, f"Relentlessly: turns below half not counted ({friend._turns_below_half})")

    # ---------------- heals with a price or a rule ----------------
    ch, ab, others, mobs, eng = setup("First On Scene. Always.")
    friend = others[0]; at(friend, 0.5)
    fill(ch, ab); ok, _ = ab.use(ch, friend, party=eng.living_allies(), engine=eng)
    check(not ok, "First On Scene: usable on an ally at half health")
    got = heal_gain(ch, ab, friend, eng, 0.1)
    check(got >= friend.health * 0.49, f"First On Scene: healed {got} of {friend.health}, wanted at least half")

    ch, ab, others, mobs, eng = setup("Told to Leave Somebody Behind", friends=2)
    held = at(others[0], 0.9); at(others[1], 0.2)
    cast(ch, ab, others[0], eng)
    check(others[1].current_health >= others[1].health * 0.89 and others[0].current_health == held, f"Told to Leave: lowest ended at {others[1].current_health} of {others[1].health}, the clicked ally moved {others[0].current_health - held}")
    at(others[1], 0.6)
    fill(ch, ab); ok, _ = ab.use(ch, others[0], party=eng.living_allies(), engine=eng)
    check(not ok, "Told to Leave: usable when nobody is below 30%")

    ch, ab, others, mobs, eng = setup("To Check On People Behind Him", friends=2)
    held = at(others[0], 0.9); low = at(others[1], 0.3)
    cast(ch, ab, others[0], eng)
    check(others[1].current_health > low and others[0].current_health == held, "To Check On People: did not go to the lowest ally")

    ch, ab, others, mobs, eng = setup("A Van With Four Spaces", friends=4)
    team = [ch] + others
    start = [at(c, 0.1 + i * 0.1) for i, c in enumerate(team)]
    cast(ch, ab, team, eng)
    got = [c.current_health - s0 for c, s0 in zip(team, start)]
    check(all(g > 0 for g in got[:4]) and got[4] == 0, f"A Van With Four Spaces: gains {got}, wanted four healed and the least hurt left out")

    ch, ab, others, mobs, eng = setup("The Arithmetic, In Public", friends=2)
    start = [at(c, 0.02) for c in others]
    ch.current_health = ch.health
    spent = int(ch.health * 0.25)
    cast(ch, ab, eng.living_allies(), eng)
    gains = [c.current_health - s0 for c, s0 in zip(others, start)]
    check(ch.current_health == ch.health - spent and all(abs(g - spent) <= 2 or c.current_health == c.health for g, c in zip(gains, others)),
          f"The Arithmetic, In Public: Ziad spent {ch.health - ch.current_health} (wanted {spent}), others gained {gains} (wanted {spent} each)")

    ch, ab, others, mobs, eng = setup("Something Offered")
    friend = others[0]; ch.current_health = ch.health
    got = heal_gain(ch, ab, friend, eng, 0.02)
    paid = ch.health - ch.current_health
    check(got > 0 and abs(ratio(paid, got) - 0.2) <= 0.03, f"Something Offered: healed {got}, Rui paid {paid}, wanted a fifth")

    ch, ab, others, mobs, eng = setup("Extremely Effective and Visibly Uncomfortable")
    cast(ch, ab, eng.living_allies(), eng)
    ch.current_health = 1; ch.heal(100)
    check(ch.current_health == 51, f"Extremely Effective: Rui healed {ch.current_health - 1} of 100 afterwards, wanted 50")
    others[0].current_health = 1; others[0].heal(100)
    check(others[0].current_health == 101, "Extremely Effective: an ally's healing was halved too")

    ch, ab, others, mobs, eng = setup("How Much of the Truth a Frightened Person Can Take", friends=2)
    others[0].current_health = others[0].health - 2; a0 = at(others[1], 0.02); b0 = at(ch, 0.02)
    cast(ch, ab, others[0], eng)
    check(others[1].current_health > a0 and ch.current_health > b0, f"How Much of the Truth: the spare was not shared ({others[1].current_health - a0}, {ch.current_health - b0})")

    ch, ab, others, mobs, eng = setup("He Rebuilt the Room")
    friend = others[0]
    friend.apply_status_effect(StatusEffect("t_ward", "Test Ward", EffectType.BUFF, 1, stat_mods={"armor": 50},
                                            real_time_seconds=None))
    for _ in range(3):
        if any(e.effect_id == "t_ward" for e in friend.active_effects):
            friend.tick_status_effects()
    low = at(friend, 0.02)
    cast(ch, ab, eng.living_allies(), eng)
    check(friend.current_health - low >= friend.health * 0.35, f"He Rebuilt the Room: ally gained {friend.current_health - low} of {friend.health}, wanted 35% of maximum and more")
    check(any(e.effect_id == "t_ward" for e in friend.active_effects), "He Rebuilt the Room: the lapsed buff did not come back")

    ch, ab, others, mobs, eng = setup("The Thing He Is Actually Good At")
    friend = next((c for c in [ch] + others if getattr(c, "mana", 0)), None)
    start = [at(c, 0.02) for c in [ch] + others]
    if friend is not None:
        friend.mana = 1000; friend.current_mana = 0
    ab.turns_remaining = 0
    random.seed(7); ok, msg = ab.use(ch, eng.living_allies(), party=eng.living_allies(), engine=eng, free=True)
    check(ok and all(c.current_health - s0 >= c.health * 0.4 for c, s0 in zip([ch] + others, start)), f"The Thing He Is Good At: party at {[c.current_health for c in [ch] + others]} ({msg!r})")
    if friend is not None:
        check(friend.current_mana == 200, f"The Thing He Is Good At: mana went to {friend.current_mana} of 1000, wanted 200")

    # ---------------- rewinds ----------------
    for name, turns in (("Never Letting Your Voice Carry", 2), ("It Runs Backwards On Its Chain", 3)):
        ch, ab, others, mobs, eng = setup(name)
        friend = others[0]
        marks = []
        for frac in (0.9, 0.7, 0.5, 0.3):
            marks.append(at(friend, frac))
            friend.tick_status_effects()
        at(friend, 0.05)
        cast(ch, ab, friend, eng)
        want = {2: marks[2], 3: marks[1]}[turns]
        check(friend.current_health == want, f"{name}: back to {friend.current_health}, wanted {want}")

    # ---------------- the rest ----------------
    ch, ab, others, mobs, eng = setup("The Ability to Answer Back")
    hot = next((x for x in ch.ability_book.get_all_abilities() if x.ability_id.startswith("personal_") and x.effect_type == "hot"), None)
    friend = others[0]; at(friend, 0.02)
    if hot is None:
        check(False, "Answer Back: Anjali has no heal-over-time to turn")
    else:
        cast(ch, hot, friend, eng)
        hp = mobs[0].current_health
        msg = cast(ch, ab, mobs[0], eng)
        check(mobs[0].current_health < hp and not any(e.effect_type == EffectType.HOT for e in friend.active_effects),
              f"Answer Back: {msg!r}")

    ch, ab, others, mobs, eng = setup("Discovering She Could Start One", foes=("beast_basic", "beast_basic"))
    mobs[0].max_health = mobs[0].current_health = 1
    cast(ch, ab, mobs, eng)
    once = 10 ** 7 - mobs[1].current_health
    ch2, ab2, o2, mobs2, eng2 = setup("Discovering She Could Start One", foes=("beast_basic", "beast_basic"))
    cast(ch2, ab2, mobs2, eng2)
    plain = 10 ** 7 - mobs2[1].current_health
    check(not mobs[0].is_alive() and once > plain * 1.2, f"Discovering She Could Start One: survivor took {once} after a kill, {plain} without one")

    ch, ab, others, mobs, eng = setup("The Cold Comes Off Her", foes=("beast_basic", "beast_basic"))
    cast(ch, ab, mobs, eng)
    check(all(m.get_status_stat_mod("haste") == -30 for m in mobs), f"The Cold Comes Off Her: haste on the row {[m.get_status_stat_mod('haste') for m in mobs]}")

    ch, ab, others, mobs, eng = setup("Doing the Loud Part")
    cast(ch, ab, mobs[0], eng)
    check(getattr(ch, "is_stunned", False), "Doing the Loud Part: Osvaldo can still act next turn")

    # Kyle, 13 Nov: all of them true trump cards with cooldowns. The two "cheaper each cast in
    # a row" abilities made no sense on a 10-turn cooldown and now build on what he has done.
    ch, ab, others, mobs, eng = setup("Six Nights a Week")
    def dealt(c, a_, m, seed=5):
        fill(c, a_); random.seed(seed); hp = m.current_health
        a_.use(c, m, party=[c], engine=eng)
        return hp - m.current_health
    ch._fight_uses = {}
    first = dealt(ch, ab, mobs[0])
    ch._fight_uses = {"some_other_spell": 3}
    later = dealt(ch, ab, mobs[0])
    ch._fight_uses = {"some_other_spell": 30}
    capped = dealt(ch, ab, mobs[0])
    check(1.38 <= ratio(later, first) <= 1.52 and 1.68 <= ratio(capped, first) <= 1.82,
          f"Six Nights a Week: fresh {first}, after three spells {later}, after thirty {capped}")

    ch, ab, others, mobs, eng = setup("The Same Two Motions")
    ch._attack_streak = (None, 0)
    first = dealt(ch, ab, mobs[0])
    ch._attack_streak = (mobs[0], 2)
    later = dealt(ch, ab, mobs[0])
    ch._attack_streak = (mobs[0], 40)
    capped = dealt(ch, ab, mobs[0])
    check(1.24 <= ratio(later, first) <= 1.36 and 1.68 <= ratio(capped, first) <= 1.82,
          f"The Same Two Motions: fresh {first}, two attacks in {later}, forty in {capped}")

    ch, ab, others, mobs, eng = setup("No Interest At All In How Long It Takes")
    cast(ch, ab, mobs[0], eng)
    dot = next((e for e in mobs[0].active_effects if e.effect_type == EffectType.DOT), None)
    check(dot is not None and dot.dispel_type is None, "No Interest At All: the damage-over-time can be dispelled")

    ch, ab, others, mobs, eng = setup("She Will Not Take a Message She Has Not Read", foes=("humanoid_warrior",))
    mobs[0].dodge, mobs[0].parry = 60.0, 39.0
    plain = ch.ability_book.abilities[ch.get_basic_attack_id()]
    def lands():
        n = 0
        for seed in range(12):
            fill(ch, plain); random.seed(seed); hp = mobs[0].current_health
            plain.use(ch, mobs[0], party=[ch], engine=eng)
            n += mobs[0].current_health < hp
        return n
    before = lands()
    cast(ch, ab, mobs[0], eng)
    after = lands()
    check(before <= 4 and after == 12, f"She Will Not Take a Message: {before}/12 landed before, {after}/12 after")

    ch, ab, others, mobs, eng = setup("Never Been Refused Twice")
    cast(ch, ab, ch, eng)
    spell = next((x for x in ch.ability_book.get_all_abilities()
                  if getattr(x, "effect_type", "") == "spell_damage" and not x.ability_id.startswith("personal_")), None)
    if spell is None:
        check(False, "Never Been Refused Twice: Orlando has no damaging spell to test with")
    else:
        ch.apply_status_effect(StatusEffect("t_blind", "Blind", EffectType.DEBUFF, 9, stat_mods={"hit_rating": -100},
                                            real_time_seconds=None))
        hp = mobs[0].current_health
        m1 = cast(ch, spell, mobs[0], eng)
        first = hp - mobs[0].current_health
        m2 = cast(ch, spell, mobs[0], eng)
        second = hp - first - mobs[0].current_health
        check(first == 0 and second > 0, f"Never Been Refused Twice: first {first} ({m1!r}), second {second} ({m2!r})")

    print("38 abilities checked in real casts")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
