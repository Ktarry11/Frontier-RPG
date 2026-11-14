"""
The last of the level 5-14 companions' abilities, bar the two that need enemies to telegraph.

  Freja Lindqvist  She Taught Four Women   20% of what the ally deals heals the worst-hurt
  Ama Boateng      No Limit At All         30% of her health; three turns of spells at a tenth the mana, +50% healing
  Marcus Okafor    Right Early             the party takes 25% less for two turns
  Esteban Ruiz     He Asks. Every Time.    what was left of the removed effect hits its owner
  Ryan Murphy      Clause by Clause        lands on his DEMON - it used to buff Ryan
  Marta            Forty Machines, One Toolkit   every pet in the party, fully repaired

"pet" was a target type in the data that nothing read: the cast fell through to the caster.
Left for the enemy-intent work: Marcus's reveal, Berat's To See Round a Corner.
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
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat import rows
    from combat.status_effects import StatusEffect, EffectType
    rm = get_recruit_manager()
    built = {}
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is not None:
            built[c.name] = c
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
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
        for attr in ("current_mana", "current_energy", "current_rage", "current_focus"):
            if hasattr(c, attr):
                setattr(c, attr, 10 ** 5)
        check(not str(entry.get("engine", "")).startswith("needs"), f"{title} is still marked {entry.get('engine')!r}")
        return c, ab

    def mob(row="front", armor=None):
        m = Monster("Mottled Boar", "beast_basic", level=60)
        m.row = row
        m.health = m.current_health = 10 ** 6
        if armor is not None:
            m.armor = armor
        return m


    def engine_for(a, b, m):
        party = Party(a)
        if b not in party.members:
            party.members.append(b)
        return CombatEngine(a, m, party=party, enemies=[m])

    def pet_for(c):
        from combat.pet_templates import PET_TEMPLATES
        for template_id in PET_TEMPLATES:
            ok, _res = c.summon_pet(template_id)
            if ok:
                return [p for p in c.all_pets if p is not None][0]
        return None

    ally = built.get("Dan Okafor")

    c, ab = kit("Freja Lindqvist", "She Taught Four Women")
    if ab:
        m = mob()
        eng = engine_for(c, ally, m)
        ab.use(c, ally, party=[c, ally], free=True)
        ally.current_health = ally.health
        c.current_health = int(c.health * 0.3)
        before, foe = c.current_health, m.current_health
        attack = [a for a in ally.ability_book.get_all_abilities()
                  if a.effect_type == "damage" and a.target_type == "enemy"][0]
        attack.is_learned, attack.turns_remaining = True, 0
        for attr in ("current_mana", "current_energy", "current_rage", "current_focus"):
            if hasattr(ally, attr):
                setattr(ally, attr, 10 ** 5)
        eng.execute_ability(ally, attack.ability_id, m)
        dealt, healed = foe - m.current_health, c.current_health - before
        check(dealt > 0 and abs(healed - dealt * 0.2) <= 2,
              f"She Taught Four Women: Dan dealt {dealt}, the worst-hurt was healed {healed}, expected 20%")
        ally.clear_combat_effects()
        check(not [e for e in ally._effects() if e.effect_id == ab.ability_id], "Freja's buff outlived the fight")

    c, ab = kit("Ama Boateng", "No Limit At All")
    if ab:
        before = c.current_health
        ok, msg = ab.use(c, c, party=[c, ally])
        check(ok and abs((before - c.current_health) - c.health * 0.3) <= 2,
              f"No Limit At All cost {before - c.current_health} health of {c.health}, expected 30%")
        heal = [a for a in c.ability_book.get_all_abilities() if a.effect_type == "heal" and a.cost > 0][0]
        check(heal.talented_cost(c) <= heal.cost * 0.11, f"Ama's heals still cost {heal.talented_cost(c)} of {heal.cost} mana")
        check(c.get_status_stat_mod("healing_done_pct") == 50, "Ama's heals are not +50%")
        check("-90%" in msg, f"the cast line does not say spells are 90% cheaper: {msg}")
        c.clear_combat_effects()

    c, ab = kit("Marcus Okafor", "Right Early")
    if ab:
        ab.use(c, [c, ally], party=[c, ally], free=True)
        check(abs(ally.get_status_stat_mod("damage_taken_pct") + 0.25) < 0.001, "Right Early is not 25% less damage")
        mine = [e for e in ally._effects() if e.effect_id == ab.ability_id]
        check(mine and mine[0].duration == 2 and mine[0].real_time_seconds is None, "Right Early is not two turns")
        ally.clear_combat_effects(); c.clear_combat_effects()

    c, ab = kit("Esteban Ruiz", "He Asks. Every Time.")
    if ab:
        m = mob()
        eng = engine_for(c, ally, m)
        ally.apply_status_effect(StatusEffect("t_rot", "Rot", EffectType.DOT, 4, potency=200,
                                              damage_school="nature", source_name=m.name, dispel_type="poison"))
        foe = m.current_health
        ok, msg = ab.use(c, ally, party=[c, ally], free=True, engine=eng)
        check(ok and not [e for e in ally._effects() if e.effect_id == "t_rot"], "He Asks did not remove the effect")
        check(foe - m.current_health > 300, f"He Asks sent back {foe - m.current_health} of 800 owed")

    c, ab = kit("Ryan Murphy", "Clause by Clause")
    if ab:
        for pet in list(getattr(c, "all_pets", []) or []):
            if pet is not None:
                pet.current_health = 0
        ok, msg = ab.use(c, None, party=[c], free=True)
        check(not ok and "no pet" in msg, f"Clause by Clause was cast with no demon out: {msg}")
        check(c.get_status_stat_mod("damage_dealt_pct") == 0, "Clause by Clause buffed Ryan himself")
        pet = pet_for(c)
        if check(pet is not None, "rig: Ryan could not summon anything"):
            ab.turns_remaining = 0
            ok, msg = ab.use(c, None, party=[c], free=True)
            check(ok and pet.get_status_stat_mod("damage_dealt_pct") == 30, f"the demon did not get +30%: {msg}")
            check(c.get_status_stat_mod("damage_dealt_pct") == 0, "Clause by Clause landed on Ryan as well")

    marta = next((n for n, r in ((c.name, getattr(c, "recruit_id", "")) for c in built.values())
                  if by_name["Forty Machines, One Toolkit"]["ability_id"].split("_")[1] in str(r)), None)
    c, ab = kit(marta, "Forty Machines, One Toolkit")
    ryan = built.get("Ryan Murphy")
    if ab and ryan is not None:
        pet = next((p for p in (ryan.all_pets or []) if p is not None and p.is_alive()), None) or pet_for(ryan)
        if check(pet is not None, "rig: no pet to repair"):
            pet.current_health = max(1, int(pet.health * 0.2))
            ok, msg = ab.use(c, None, party=[c, ryan], free=True)
            check(ok and pet.current_health == pet.health, f"Forty Machines left a party pet at {pet.current_health}/{pet.health}: {msg}")

    from combat.stat_text import stat_text
    check(stat_text("all_ability_cost_pct", 1.0) == "Ability costs -100%", f"free reads as {stat_text('all_ability_cost_pct', 1.0)!r}")

    if fails:
        print(f"{len(fails)} problem(s):")
        for f in fails:
            print("  -", f)
        return 1
    print("kit abilities batch 6 OK - the early companions' abilities do what they say; pets can be aimed at.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
