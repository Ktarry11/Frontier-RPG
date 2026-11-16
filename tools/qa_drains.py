#!/usr/bin/env python3
"""Every drain takes life (or mana) and gives it to whoever cast it, in a real fight.

    PYTHONPATH=. python3 tools/qa_drains.py

Kyle, 15 Nov 2026, from a friend's playtest: "Drain life doesn't take life. Check to ensure drain life and drain mana
or siphon life work as intended. Vampiric embrace too", "And coa drain skills as appropriate".

CLAIMS
  1. Drain Life hurts the target and heals the Warlock for what it dealt.
  2. (No player Drain Mana: Kyle, 15 Nov 2026, "No drain mana." A monster's is checked in 7.)
  3. Siphon Life (talent): Corruption's ticks heal the Warlock for 40% of each tick.
  4. Vampiric Embrace (talent): Shadow damage heals the Priest for 20%, a Shadow DoT's ticks too, and Holy damage
     doesn't.
  5. Soul Leech (talent): when it fires, a Destruction spell heals for 20% of its damage.
  6. Every "deals damage and heals you" ability of all thirty classes (damage_and_heal) heals its caster.
  7. Monsters: a Drain Life or Life Drain hurts its target and heals the monster; Mana Drain burns the target's
     mana and feeds the monster's.
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

bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)
    return ok


def main():
    from entities.character import Character
    from entities.monster import Monster

    def hero(cls, level=40):
        c = Character(name=f"T{cls}", char_class=cls, level=level)
        c.hit_chance_vs = lambda *a, **k: 100.0          # these are about drains, not about missing
        for attr in ("current_mana", "current_energy", "current_rage"):
            if hasattr(c, attr):
                setattr(c, attr, 10 ** 6)
        if hasattr(c, "mana"):
            c.mana = max(getattr(c, "mana", 0), 10 ** 6)
        c.current_health = c.health // 3
        return c

    def mob(level=40, mana=0):
        m = Monster("Mottled Boar", "beast_basic", level=level)
        m.health = m.current_health = 10 ** 6
        if mana:
            m.mana = m.max_mana = m.current_mana = mana
        return m

    entries = {}
    for f in (ROOT / "data/abilities").glob("*.json"):
        doc = json.loads(f.read_text(encoding="utf-8"))
        rows = doc.get("abilities", doc)
        for a in (rows if isinstance(rows, list) else list(rows.values())):
            if isinstance(a, dict) and a.get("ability_id"):
                entries[a["ability_id"]] = a

    def ability(c, aid):
        ab = c.ability_book.get_ability(aid)
        if ab is None and aid in entries:
            from combat.abilities import _ability_from_data
            ab = _ability_from_data(entries[aid])
            c.ability_book.add_ability(ab)
        if ab is not None:
            ab.refresh_rank_for_level(c.level)      # the highest rank this level allows
            ab.is_learned = True
            ab.turns_remaining = 0
        return ab

    def talent(c, tid):
        for tree in c.talent_trees.values():
            node = tree.get_node(tid)
            if node is not None:
                node.points_spent = node.max_points
                c._recalculate_derived_stats()
                c._sync_talent_unlocked_abilities()
                c._sync_talent_procs()
                return True
        return False

    def cast(c, ab, m):
        ab.turns_remaining = 0
        h0, hp0 = c.current_health, m.current_health
        ab.use(c, m, party=[c], free=True)
        return c.current_health - h0, hp0 - m.current_health

    random.seed(5)

    # ---- 1. Drain Life
    w = hero("Warlock")
    ab = ability(w, "warlock_drain_life")
    if check(ab is not None, "no Drain Life"):
        healed, dealt = cast(w, ab, mob())
        check(dealt > 0, "Drain Life did no damage")
        check(healed > 0 and abs(healed - dealt) <= max(2, dealt * 0.05),
              f"Drain Life dealt {dealt} and healed {healed} (should heal what it deals)")

    # ---- 3. Siphon Life
    w = hero("Warlock")
    check(talent(w, "warlock_affliction_siphon_life"), "couldn't learn Siphon Life")
    ab = ability(w, "warlock_corruption")
    if check(ab is not None, "no Corruption"):
        m = mob()
        ab.use(w, m, party=[w], free=True)
        h0, hp0 = w.current_health, m.current_health
        m.tick_status_effects()
        tick = hp0 - m.current_health
        healed = w.current_health - h0
        check(tick > 0, "Corruption didn't tick")
        check(healed > 0 and abs(healed - int(tick * 0.4)) <= 2,
              f"a Corruption tick of {tick} healed {healed} with Siphon Life (want 40%)")
    w2 = hero("Warlock")
    ab2 = ability(w2, "warlock_corruption")
    m = mob()
    ab2.use(w2, m, party=[w2], free=True)
    h0 = w2.current_health
    m.tick_status_effects()
    check(w2.current_health == h0, "Corruption healed a Warlock without Siphon Life")

    # ---- 4. Vampiric Embrace
    p = hero("Priest")
    check(talent(p, "priest_shadow_vampiric_embrace"), "couldn't learn Vampiric Embrace")
    mb = ability(p, "priest_mind_blast")
    if check(mb is not None, "no Mind Blast"):
        healed, dealt = cast(p, mb, mob())
        check(dealt > 0 and abs(healed - int(dealt * 0.2)) <= 2,
              f"Mind Blast dealt {dealt} and healed {healed} with Vampiric Embrace (want 20%)")
    smite = ability(p, "priest_smite")
    if check(smite is not None, "no Smite"):
        healed, dealt = cast(p, smite, mob())
        check(dealt > 0 and healed == 0, f"Smite (Holy) healed {healed} with Vampiric Embrace (Shadow only)")
    swp = ability(p, "priest_shadow_word_pain")
    if check(swp is not None, "no Shadow Word: Pain"):
        m = mob()
        swp.use(p, m, party=[p], free=True)
        h0, hp0 = p.current_health, m.current_health
        m.tick_status_effects()
        tick = hp0 - m.current_health
        check(tick > 0 and abs((p.current_health - h0) - int(tick * 0.2)) <= 2,
              f"a Shadow Word: Pain tick of {tick} healed {p.current_health - h0} (want 20%)")

    # ---- 5. Soul Leech, forced to fire
    w = hero("Warlock")
    check(talent(w, "warlock_destruction_soul_leech"), "couldn't learn Soul Leech")
    for e in w._effects():
        if getattr(e, "proc", None) and e.proc.get("leech_pct") == 0.2:
            e.proc["chance"] = 100
    sb = ability(w, "warlock_shadow_bolt")
    if check(sb is not None, "no Shadow Bolt"):
        healed, dealt = cast(w, sb, mob())
        check(dealt > 0 and abs(healed - int(dealt * 0.2)) <= 2,
              f"Shadow Bolt dealt {dealt} and Soul Leech healed {healed} (want 20%)")

    # ---- 6. every damage_and_heal
    n6 = 0
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        rows = doc.get("abilities", doc)
        rows = rows if isinstance(rows, list) else list(rows.values())
        cls = None
        for a in rows:
            if a.get("effect_type") != "damage_and_heal":
                continue
            if cls is None:
                cls = f.stem.replace("_", " ").title().replace("Of", "of")
            try:
                c = hero(cls, level=60)
            except Exception as exc:
                check(False, f"couldn't make a {cls}: {exc}")
                break
            c.current_health = 10              # well under any "usable below X% health" gate
            ab = ability(c, a["ability_id"])
            if ab is None:
                check(False, f"{a['ability_id']}: couldn't build it")
                continue
            m = mob(60)
            m.current_health = m.health // 5          # under every "requires a wounded target" gate
            party = [c, hero(cls, level=60)]
            party[1].current_health = 1
            h_before = [x.current_health for x in party]
            hp0 = m.current_health
            ab.use(c, m, party=party, free=True)
            n6 += 1
            check(hp0 > m.current_health, f"{a['ability_id']} did no damage")
            check(any(x.current_health > h for x, h in zip(party, h_before)),
                  f"{a['ability_id']} ({a.get('name')}) healed nobody")

    # ---- 7. monsters
    from entities.monster import MonsterAbility
    for name in ("Drain Life", "Life Drain", "Siphon Soul"):
        caster = mob(40)
        caster.current_health = caster.health // 2
        victim = hero("Warrior")
        victim.current_health = victim.health
        a = MonsterAbility(name, "heal", 60, cooldown=0, mana_cost=0, school="shadow")
        h0, v0 = caster.current_health, victim.current_health
        a.use(caster, victim)
        took = v0 - victim.current_health
        check(took > 0, f"a monster's {name} didn't hurt its target")
        check(caster.current_health - h0 >= took > 0, f"a monster's {name} took {took} and healed "
                                                        f"{caster.current_health - h0}")
    caster = mob(40, mana=1000)
    caster.current_mana = 100
    victim = hero("Priest")
    victim.current_mana = getattr(victim, "max_mana", 1000)
    a = MonsterAbility("Mana Drain", "debuff", 0, cooldown=0, mana_cost=0, school="shadow", duration=3,
                       stat_mods={"intellect": -14})
    v0, c0 = victim.current_mana, caster.current_mana
    a.use(caster, victim)
    check(victim.current_mana < v0 and caster.current_mana > c0,
          f"a monster's Mana Drain moved no mana ({v0}->{victim.current_mana}, {c0}->{caster.current_mana})")

    print(f"{n6} damage-and-heal abilities cast")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  - " + b)
        return 1
    print("drains OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
