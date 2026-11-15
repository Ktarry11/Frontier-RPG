#!/usr/bin/env python3
"""Abilities grow with level, and power feeds them per ability.

    PYTHONPATH=. python3 tools/qa_ability_scaling.py

Kyle, 15 Nov 2026: "Player damage is rather low. There's very little skill difference between lvl 15 skills and
lvl 60." and "We need to look at scaling and also how spell power, healing power, or attack power scale to a
spell". Every main attack and heal was 2x at 56 what it was at 12, while mobs grow ~4x health and ~5x damage;
and every spell took 1.5x spell power, every heal 1.2x, every special 0.5x attack power, whatever it was.
See combat/ability_scaling.py.

  1. The rank curve: a rank learned at 20 or below is as authored; the main nukes and heals are ~4x stronger
     at their top rank than at the rank you hold at 15.
  2. Coefficients follow the ability: a big cooldown takes more power than a spammable cast; an area effect
     takes less per target; a buff's effect_value (a percentage) is never curved.
  3. Higher ranks take more of your power, Classic's way: a rank learned below 20 loses 3.75% of its coefficient
     per level short of 20, and an outlevelled rank is downrank-penalized; a coefficient named in the data (the
     Wand's 0.3) is used exactly.
  4. In a real cast: a level-60 Fireball with spell power on gains more from it than the same spell at 15.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

BAD = []


def check(label, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {label}" + (f"  ({detail})" if detail else ""))
    if not cond:
        BAD.append(label)


def main():
    from combat import ability_scaling as S
    from combat.abilities import get_class_abilities, _load_universal_ability_data, _ability_from_data

    def book(cls):
        return {a.ability_id: a for a in get_class_abilities(cls).get_all_abilities()}

    def at(ab, level):
        best = 0
        for i, r in enumerate(ab.ranks):
            if r["level_req"] <= level:
                best = i
        ab.current_rank_index = best
        return ab

    import json
    print("1. the rank curve")
    # the third pass (Kyle, 15 Nov: "Each spell rank or ability rank should FEEL like an actual step", "Steeper
    # world"): ranks follow the world curve (combat/world_curve.py) - x1 at 1, ~x2.8 at 15, ~x8.4 at 56
    check("rank 1 at level 1 is as authored", S.rank_multiplier(1) == 1.0)
    check(f"x{S.rank_multiplier(15):.2f} at 15 and x{S.rank_multiplier(56):.2f} at 56",
          2.4 <= S.rank_multiplier(15) <= 3.2 and 7.5 <= S.rank_multiplier(56) <= 9.5)
    for cls, aid in (("Mage", "mage_fireball"), ("Shaman", "shaman_lightning_bolt"), ("Priest", "priest_heal"),
                     ("Warlock", "warlock_shadow_bolt")):
        ab = book(cls).get(aid)
        if ab is None:
            check(f"{aid} exists", False)
            continue
        vals = [r["effect_value"] for r in ab.ranks]
        steps = [b / a - 1 for a, b in zip(vals, vals[1:]) if a]
        check(f"{ab.name}: every rank is a real step ({', '.join(f'+{x:.0%}' for x in steps)})",
              steps and min(steps) >= 0.20)
    for cls, aid in (("Mage", "mage_fireball"), ("Warlock", "warlock_shadow_bolt"), ("Priest", "priest_smite"),
                     ("Warrior", "warrior_heroic_strike"), ("Warlock", "warlock_searing_pain"),
                     ("Priest", "priest_heal")):
        ab = book(cls).get(aid)
        if ab is None:
            check(f"{aid} exists", False)
            continue
        lo = at(ab, 15).effect_value
        hi = at(ab, 60).effect_value
        check(f"{ab.name}: {lo} at 15 -> {hi} at 60", lo and hi / lo >= 3.5, f"{hi / max(1, lo):.1f}x")
    fb_ = book("Mage")["mage_fireball"]
    top = at(fb_, 60).effect_value
    check(f"Fireball's top rank is {top} (~25x rank 1, like Classic's Lightning Bolt 16 -> 452)", 900 <= top <= 1300)
    import json
    raw = json.load(open("data/abilities/mage.json", encoding="utf-8"))
    raw = raw if isinstance(raw, list) else raw.get("abilities", raw)
    raw = {e["ability_id"]: e for e in (raw.values() if isinstance(raw, dict) else raw) if isinstance(e, dict)}
    buffs = [a for a in book("Mage").values() if a.effect_type == "buff" and a.ability_id in raw]
    check(f"a buff's effect_value is not curved ({len(buffs)} Mage buffs)", buffs and all(
        a.ranks[-1]["effect_value"] == raw[a.ability_id]["ranks"][-1]["effect_value"] for a in buffs))

    # playtest backlog 14 Nov, item 2: "CoA classes cap out FAST with their skills"
    import glob
    early = []
    for path in sorted(glob.glob("data/abilities/*.json")):
        if os.path.basename(path) in ("_universal.json", "asher_unique.json"):
            continue
        d = json.load(open(path, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for e in (L.values() if isinstance(L, dict) else L):
            if (isinstance(e, dict) and e.get("effect_type") in S.CURVED and e.get("ranks")
                    and not e["ability_id"].endswith("_attack") and e["ranks"][0]["level_req"] <= 44
                    and e["ranks"][-1]["level_req"] < 50):
                early.append(f"{e['name']} {[r['level_req'] for r in e['ranks']]}")
    check(f"every damage and healing ability learned by 44 keeps ranking up to 50+ ({len(early)} don't)",
          not early, "; ".join(early[:5]))

    print("2. coefficients follow the ability")
    m = book("Mage")
    fb, ae = m["mage_fireball"], m["mage_arcane_explosion"]
    check("Arcane Explosion (an AoE) takes less spell power than Fireball",
          ae.sp_coefficient < fb.sp_coefficient, f"{ae.sp_coefficient:.2f} vs {fb.sp_coefficient:.2f}")
    big = max((a for a in m.values() if a.effect_type == "spell_damage" and a.target_type != "enemy_aoe"),
              key=lambda a: a.cooldown or 0)
    check(f"a big cooldown ({big.name}, cd {big.cooldown}) takes more than a spammable cast",
          big.sp_coefficient > fb.sp_coefficient or (fb.cooldown or 0) >= (big.cooldown or 0),
          f"{big.sp_coefficient:.2f} vs {fb.sp_coefficient:.2f}")
    p = book("Priest")
    party = [a for a in p.values() if a.effect_type == "heal" and (a.target_type == "party" or
                                                                    getattr(a, "heal_scope", None) == "party")]
    single = p.get("priest_heal")
    if party and single:
        check(f"a party heal ({party[0].name}) takes less healing power per target than Heal",
              party[0].heal_coefficient < single.heal_coefficient * S.cooldown_weight(party[0].cooldown),
              f"{party[0].heal_coefficient:.2f} vs {single.heal_coefficient:.2f}")

    print("3. higher ranks take more of your power (Classic's low-level and downrank penalties)")
    # Kyle, 15 Nov 2026: "Higher rank spells scale more from spell power, attack power, and healing power than low
    # rank ones do. Wow also does this"
    r1 = S.coefficient(at(fb, 1), "sp")
    hi = S.coefficient(at(fb, 60), "sp")
    check(f"Fireball rank 1 takes {r1 / hi:.0%} of the top rank's spell power share (Classic: ~29%)",
          0.25 <= r1 / hi <= 0.33)
    mid = S.coefficient(at(fb, 20), "sp")
    check("a rank learned at 20 or later takes the full share", abs(mid - hi) < 1e-9 or at(fb, 20).current_rank[
        "level_req"] < 20)

    class _Lv:
        def __init__(self, level):
            self.level = level
    right = S.coefficient(at(fb, 40), "sp", _Lv(40))
    old = S.coefficient(at(fb, 1), "sp", _Lv(40))
    check(f"rank 1 cast at 40 takes {old / right:.0%} of what the right rank at 40 does (downranked)",
          old / right < 0.15)
    check("the rank you should have at your level is never downrank-penalized",
          all(abs(S.downrank_penalty(at(fb, lv), lv) - 1) < 1e-9 for lv in range(1, 61)))
    wand = next((e for e in _load_universal_ability_data() if e.get("sp_coefficient") is not None), None)
    if wand:
        w = _ability_from_data(wand)
        check("the Wand's own 0.3 is used exactly", abs(S.coefficient(w, "sp") - 0.3) < 1e-9)

    print("4. a real cast")
    from entities.character import Character
    from entities.monster import Monster

    def gain(level):
        c = Character(name="Mage", char_class="Mage", level=level)
        ab = c.ability_book.get_ability("mage_fireball")
        dummy = Monster("Target Dummy", "beast_basic", level=level)
        dummy.max_health = dummy.current_health = 10 ** 7
        # what the spell sends, before the target's resistances: this measures the coefficient, not the mob
        sent = []

        def take(amount, *a, **k):
            sent.append(amount)
            return amount
        dummy.take_damage = take

        def avg(sp):
            import random as _r
            _r.seed(11)                      # the same dice for both, so the difference is the spell power alone
            c.spell_power = sp
            c.crit_chance_spell = 0.0       # crits swing a 40-cast mean by more than the effect being measured
            out = []
            for _ in range(40):
                ab.turns_remaining = 0
                c.current_mana = c.mana
                sent.clear()
                ab.use(c, dummy, party=[c])
                out.append(sum(sent))
            return sum(out) / len(out)
        base = c.spell_power
        return avg(base + 100) - avg(base)
    g15, g60 = gain(15), gain(60)
    check(f"+100 spell power adds {g15:.0f} to Fireball at 15 and {g60:.0f} at 60 (the higher rank takes more)",
          g60 > g15 * 1.1)

    if BAD:
        print(f"\nFAILED - {len(BAD)}")
        return 1
    print("\nability scaling OK - ranks grow with level, and power feeds each ability by what it is.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
