"""
Sixteen more recruit signature abilities, each held to its own text.

Kyle, 12 Nov: "For dead keys (character recruit abilities) we should ensure they do what they
say."

Three needed something new:
  Kesten Ambrose   Reading His Own Entry            "spends 15% of his health" - it was free
  Karim Haddad     The Fastest Route to Being Useful "spends 20% of his health" - it was free
  Callum Reid      You're Enormous                  "Does not work on bosses" - it did
  Fiona Strachan   Unbearable Until Somebody Checks "Does not work on bosses" - it did
  Gianluca Ferri   A Running Commentary             "enemies target Gianluca first" - they did not

Five did nothing at all and now have the mechanic they describe:
  Hana Tamihana    Read the Break                   first hit on each ally lands 40% lighter
  Hana Tamihana    Never Turn Your Back On It       overhealing becomes a shield (cap 30%)
  Silas Vance      The Retainer                     that enemy cannot damage Silas
  Callum Reid      Professional Development         half damage from a repeat of the same school
  Ivan Petrov      He Never Hit One                 +15% (its friendly-fire half is gone: there is none)

Six were marked as broken in the data and are checked here to be working, because the engine
caught up with them (monsters read a damage-dealt percentage; an area effect is aimed at a
row; expertise and spell penetration are read):
  Pieter Malan     Exclusion Zone, Shouted At By Thousands
  Gianluca Ferri   Defused More Fights With a Joke
  Adrián Mendoza   The Least Popular Person on the Field
  Carolina Santos  Feel the Bottom
  Sondre Haugen    Control, Not Power
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
    from entities.character import Character
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    random.seed(8)
    rm = get_recruit_manager()
    built = {}
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is not None:
            built[c.name] = c
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
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
        for attr in ("current_mana", "current_energy", "current_rage"):
            setattr(c, attr, 10 ** 5)
        check(not str(entry.get("engine", "")).startswith("needs"), f"{title} is still marked {entry.get('engine')!r}")
        return c, ab

    def mob(boss=False, row="front"):
        m = Monster("Mottled Boar", "beast_basic", level=60)
        m.is_boss, m.row = boss, row
        return m

    def fight(c, foes):
        eng = CombatEngine(c, foes[0], party=Party(c), enemies=foes)
        eng.current_actor = c
        return eng

    # --- health costs ---------------------------------------------------------------------
    for who, title, pct in (("Kesten Ambrose", "Reading His Own Entry", 15),
                            ("Karim Haddad", "The Fastest Route to Being Useful", 20)):
        c, ab = kit(who, title)
        if not ab:
            continue
        full = c.health
        ok, msg = ab.use(c, c, free=True)
        paid = full - c.current_health
        check(ok, f"{title} would not cast ({msg})")
        check(abs(paid - int(full * pct / 100)) <= 1, f"{title}: paid {paid} health, {pct}% of {full} is {int(full * pct / 100)}")
        check(c.get_status_stat_mod("damage_dealt_pct") > 0, f"{title}: paid and got no damage bonus")
        c2, ab2 = kit(who, title)
        c2.current_health = 5
        ab2.use(c2, c2, free=True)
        check(c2.current_health >= 1, f"{title} killed its caster at 5 health")

    # --- does not work on bosses ----------------------------------------------------------
    c, ab = kit("Callum Reid", "You're Enormous")
    if ab:
        grunt, boss = mob(), mob(boss=True)
        ok, msg = ab.use(c, [grunt, boss], free=True)
        taunted = {t for (t, amt, flag) in (ab._last_threat_events or []) if amt >= 500}
        check(ok and grunt in taunted, f"You're Enormous did not pull an ordinary enemy ({msg})")
        check(boss not in taunted, "You're Enormous pulled a boss; its text says it does not work on bosses")
        c, ab = kit("Callum Reid", "You're Enormous")
        mana = (c.current_mana, c.current_energy)
        ok, msg = ab.use(c, [mob(boss=True)])
        check(not ok and "does not work" in str(msg), f"You're Enormous at a lone boss: ok={ok} {msg!r}")
        check((c.current_mana, c.current_energy) == mana and ab.is_available(), "a refused You're Enormous still cost something")

    c, ab = kit("Fiona Strachan", "Unbearable Until Somebody Checks")
    if ab:
        grunt = mob()
        ok, msg = ab.use(c, grunt, free=True)
        check(ok and grunt.get_status_stat_mod("damage_dealt_pct") == -20, f"Unbearable: target's damage is {grunt.get_status_stat_mod('damage_dealt_pct')}% ({msg})")
        check(any(t is grunt and amt >= 500 for (t, amt, flag) in (ab._last_threat_events or [])), "Unbearable did not taunt its target")
        c, ab = kit("Fiona Strachan", "Unbearable Until Somebody Checks")
        boss = mob(boss=True)
        ok, msg = ab.use(c, boss)
        check(not ok and not boss._effects(), f"Unbearable landed on a boss ({msg})")

    # --- Gianluca: party protected AND enemies on him --------------------------------------
    c, ab = kit("Gianluca Ferri", "A Running Commentary")
    if ab:
        foes = [mob(), mob(row="back")]
        ally = Character("Ally", "Mage", 60)
        party = Party(c)
        party.add_member(ally) if hasattr(party, "add_member") else party.members.append(ally)
        eng = CombatEngine(c, foes[0], party=party, enemies=foes)
        eng.current_actor = c
        for f in foes:
            eng.gain_threat(ally, f, 9000)
        ok, msg = eng.execute_ability(c, ab.ability_id, c)
        check(ok, f"A Running Commentary would not cast ({msg})")
        for f in foes:
            check(eng.highest_threat_target(f) is c, f"after A Running Commentary an enemy still targets {getattr(eng.highest_threat_target(f), 'name', None)}")
        check(c.get_status_stat_mod("physical_damage_taken_pct") == -20, "A Running Commentary: no damage reduction on Gianluca")

    c, ab = kit("Gianluca Ferri", "Defused More Fights With a Joke")
    if ab:
        foes = [mob(), mob(row="back"), mob()]
        ok, msg = ab.use(c, foes, free=True)
        check(ok and all(f.get_status_stat_mod("damage_dealt_pct") == -25 for f in foes), f"Defused: {[f.get_status_stat_mod('damage_dealt_pct') for f in foes]} ({msg})")
        victim = Character("V", "Mage", 60)
        victim.dodge = victim.parry = victim.block_chance = 0.0
        plain = mob()
        mult = [m.damage_output_multiplier for m in (foes[0], plain)]
        if True:
            check(abs(mult[0] / mult[1] - 0.75) < 0.001, f"a defused enemy deals {mult[0] / mult[1]:.2f}x, want 0.75x")

    # --- Pieter ---------------------------------------------------------------------------
    c, ab = kit("Pieter Malan", "Exclusion Zone")
    if ab:
        front, back = [mob(), mob()], [mob(row="back"), mob(row="back")]
        eng = fight(c, front + back)
        ok, msg = eng.execute_ability(c, ab.ability_id, back[0])
        check(ok and all(f.get_status_stat_mod("damage_dealt_pct") == -30 for f in back), f"Exclusion Zone did not cover the aimed row ({msg})")
        check(all(f.get_status_stat_mod("damage_dealt_pct") == 0 for f in front), "Exclusion Zone also landed on the other row")
    c, ab = kit("Pieter Malan", "Shouted At By Thousands")
    if ab:
        ok, msg = ab.use(c, c, free=True)
        check(ok and c.get_status_stat_mod("threat_generation_pct") == 200 and c.get_status_stat_mod("magic_damage_taken_pct") == -20,
              f"Shouted At By Thousands: threat {c.get_status_stat_mod('threat_generation_pct')}, magic taken {c.get_status_stat_mod('magic_damage_taken_pct')}")

    # --- Adrián ---------------------------------------------------------------------------
    c, ab = kit("Adrián Mendoza", "The Least Popular Person on the Field")
    if ab:
        foes = [mob(), mob(row="back"), mob()]
        ok, msg = ab.use(c, foes, free=True)
        taunted = {id(t) for (t, amt, flag) in (ab._last_threat_events or []) if amt >= 500}
        check(ok and all(id(f) in taunted for f in foes), f"The Least Popular Person pulled {len(taunted)} of {len(foes)} enemies ({msg})")

    # --- Carolina -------------------------------------------------------------------------
    c, ab = kit("Carolina Santos", "Feel the Bottom")
    if ab:
        def swings(caster):
            foe = mob()
            foe.dodge, foe.parry = 30.0, 15.0
            landed = 0
            for _ in range(400):
                foe.current_health = foe.max_health
                if (foe.take_damage(500, "physical", attacker_level=60, attacker=caster) or 0) > 0:
                    landed += 1
            return landed
        before = swings(c)
        ok, msg = ab.use(c, c, free=True)
        c._recalculate_derived_stats()
        after = swings(c)
        check(before < 340, f"rig: without the buff {before} of 400 swings landed on a 45% avoidance target")
        check(ok and after == 400, f"Feel the Bottom: {after} of 400 swings landed; none should be dodged or parried")

    # --- Sondre ---------------------------------------------------------------------------
    c, ab = kit("Sondre Haugen", "Control, Not Power")
    if ab:
        ok, msg = ab.use(c, c, free=True)
        c._recalculate_derived_stats()
        check(ok and c.hit_rating >= c.HIT_RATING_CAP, f"Control, Not Power: hit rating {c.hit_rating}")
        check(c.spell_penetration >= c.SPELL_PEN_USEFUL_MAX, f"Control, Not Power: spell penetration {c.spell_penetration}")
        check(c.get_status_stat_mod("damage_dealt_pct") == -20, "Control, Not Power: the 20% damage cost is missing")

    # ====================== five more that did nothing at all ==============================
    def hits(victim, attacker, n, school="physical", amount=1000):
        """Total damage of n identical hits, avoidance off, health topped up between."""
        victim.dodge = victim.parry = victim.block_chance = 0.0
        out = []
        for _ in range(n):
            victim.current_health = victim.health
            out.append(victim.take_damage(amount, school, attacker_level=60, attacker=attacker) or 0)
        return out

    # Hana - Read the Break: the FIRST hit on each ally is 40% lighter, the second is not
    c, ab = kit("Hana Tamihana", "Read the Break")
    if ab:
        ally = Character("Ally", "Warrior", 60)
        party = Party(c)
        party.add_member(ally) if hasattr(party, "add_member") else party.members.append(ally)
        base = hits(ally, mob(), 1)[0]
        ok, msg = ab.use(c, [c, ally], party=party, free=True)
        check(ok and ally.get_status_stat_mod("next_hit_taken_pct") == -40 and c.get_status_stat_mod("next_hit_taken_pct") == -40,
              f"Read the Break did not cover the whole party ({msg})")
        first, second = hits(ally, mob(), 2)
        check(base and abs(first / base - 0.6) < 0.03, f"Read the Break: the first hit was {first / max(1, base):.2f}x a normal one, want 0.60x")
        check(abs(second - base) <= 2, f"Read the Break: the second hit was {second}, a normal hit is {base} - it should not be reduced")

    # Silas - The Retainer: that enemy cannot hurt Silas; it can hurt anyone else; others can hurt Silas
    c, ab = kit("Silas Vance", "The Retainer")
    if ab:
        held, other = mob(), mob()
        ok, msg = ab.use(c, held, free=True)
        check(ok, f"The Retainer would not cast ({msg})")
        check(sum(hits(c, held, 30)) == 0 and sum(hits(c, held, 30, school="fire")) == 0, "the retained enemy still damaged Silas")
        check(sum(hits(c, other, 5)) > 0, "The Retainer made Silas immune to a different enemy")
        bystander = Character("B", "Warrior", 60)
        check(sum(hits(bystander, held, 5)) > 0, "The Retainer stopped the enemy hurting someone else")

    # Callum - Professional Development: half damage from a repeat of the same school
    c, ab = kit("Callum Reid", "Professional Development")
    if ab:
        foe = mob()
        plain = hits(c, foe, 1, school="fire")[0]
        ok, msg = ab.use(c, c, free=True)
        c._last_hit_school = None
        fire1, fire2, frost, fire3 = (hits(c, foe, 1, school=s)[0] for s in ("fire", "fire", "frost", "fire"))
        check(ok and abs(fire1 - plain) <= 2, f"Professional Development: the first fire hit was {fire1}, a normal one is {plain}")
        check(abs(fire2 / plain - 0.5) < 0.03, f"Professional Development: a repeated fire hit was {fire2 / plain:.2f}x, want 0.50x")
        check(abs(fire3 - plain) <= 2, f"Professional Development: fire after frost was {fire3}; the school changed, so no reduction")

    # Hana - Never Turn Your Back On It: overheal becomes a shield, capped
    c, ab = kit("Hana Tamihana", "Never Turn Your Back On It")
    if ab:
        ally = Character("Ally", "Warrior", 60)
        party = Party(c)
        party.add_member(ally) if hasattr(party, "add_member") else party.members.append(ally)
        ally.current_health = ally.health - 100
        ally.heal(300)
        check(not any(getattr(e, "absorb", 0) for e in ally._effects()), "overheal made a shield with no buff up")
        ok, msg = ab.use(c, [c, ally], party=party, free=True)
        ally.current_health = 1
        ally.heal(300)
        worth = ally.current_health - 1            # what a 300 heal is really worth to this ally
        for e in [e for e in ally._effects() if e.effect_id == "overheal_shield"]:
            ally._effects().remove(e)
        ally.current_health = ally.health - 250          # 300 into a 250 gap: 50 over, well under the cap
        ally.heal(300)
        shield = sum(getattr(e, "absorb", 0) or 0 for e in ally._effects())
        check(ok and ally.current_health == ally.health and abs(shield - (worth - 250)) <= 1,
              f"a heal worth {worth} into a 250 gap should leave a {worth - 250} shield; got {shield} ({msg})")
        ally.heal(10 ** 6)
        shield = sum(getattr(e, "absorb", 0) or 0 for e in ally._effects())
        check(shield == int(ally.health * ally.OVERHEAL_SHIELD_CAP), f"the overheal shield is {shield}, cap is {int(ally.health * ally.OVERHEAL_SHIELD_CAP)}")
        before = ally.current_health
        ally.dodge = ally.parry = ally.block_chance = 0.0
        ally.take_damage(50, "fire", attacker_level=60, attacker=mob())
        check(ally.current_health == before, "the overheal shield did not absorb a small hit")

    # Ivan - He Never Hit One: +15%, and no promise about friendly fire
    c, ab = kit("Ivan Petrov", "He Never Hit One")
    if ab:
        ok, msg = ab.use(c, c, free=True)
        check(ok and c.get_status_stat_mod("damage_dealt_pct") == 15, f"He Never Hit One: damage bonus is {c.get_status_stat_mod('damage_dealt_pct')} ({msg})")
        check("ally" not in by_name["He Never Hit One"]["description"].lower(), "He Never Hit One still talks about not hitting allies - there is no friendly fire")

    left = sum(1 for a in by_name.values() if str(a.get("engine", "")).startswith("needs"))
    print(f"16 abilities checked. Kit abilities still marked as needing engine work: {left}")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("kit abilities (batch 2) OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
