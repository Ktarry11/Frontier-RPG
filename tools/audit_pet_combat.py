#!/usr/bin/env python3
"""Put every pet through a real fight and report what it actually did.

WHY THIS EXISTS. The inspection tools cannot see any of this. A pet's
template can be perfectly well-formed data - right stats, right abilities,
right schools - and the pet can still spend a whole fight auto-attacking,
because what a pet DOES is decided by Pet.choose_action and
CombatEngine.execute_pet_action, not by the template. Every pet bug found
so far needed a fight to happen:

  - pets froze at the level they were summoned
  - pets were never written to a save
  - pet AoE was not expressible at all (is_aoe was never accepted)
  - fourteen summons handed the player another class's pet

So this runs the fight. Per template: summon it on a real owner of the
right class, put it in a real CombatEngine against a target that cannot
die, and let it take twenty turns. Then report:

  acted     how many of those turns it used an ability at all
  basic     how many were the slot-0 fallback (choose_action's last resort)
  dry       the first turn of the terminal run where it could no longer
            act at all - it hesitated from here to the end of the fight
  unreached abilities it has learned, is paying for, and never once cast

The last two columns are the point. A pet that reports "dry at turn 5" has
a resource bug, not a tuning problem: nothing in the engine regenerates a
pet's pool. A pet with unreached abilities is paying design attention and
authoring effort for a button that cannot be pressed.

    python3 tools/audit_pet_combat.py
    python3 tools/audit_pet_combat.py --pet ziggi_6k
    python3 tools/audit_pet_combat.py --turns 40
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TURNS = 20

# Which class can actually summon each template, so the owner is real. A
# pet's stats scale off owner talents, so summoning a Necromancer's Ghoul
# onto a Hunter would measure a pet nobody can field.
OWNER_FOR_PET_TYPE = {
    "hunter": "Hunter", "warlock": "Warlock", "primalist": "Primalist",
    "tinker": "Tinker", "necromancer": "Necromancer", "reaper": "Reaper",
    "cultist": "Cultist", "felsworn": "Felsworn", "stormbringer": "Stormbringer",
    "knight_of_xoroth": "Knight of Xoroth", "witch_hunter": "Witch Hunter",
    "barbarian": "Barbarian", "ranger": "Ranger",
}


def run_one(template_id, template, turns=TURNS):
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine

    cls = OWNER_FOR_PET_TYPE.get(template.get("pet_type"))
    if cls is None:
        return {"skip": f"no owner class maps to pet_type {template.get('pet_type')!r}"}

    # LEVEL 60, not the template's minimum. An ability gated to a later
    # level_req is not learned at the minimum, so it cannot be reported
    # as never-cast - the first run of this summoned at level 10 and
    # found 9 unreachable abilities when the real number across full
    # kits was 14 (Furious Howl is level_req 20 on a level_req 1 Wolf).
    level = 60
    owner = Character(name="Owner", char_class=cls, level=level)
    ok, pet = owner.summon_pet(template_id)
    if not ok:
        return {"skip": f"summon refused: {pet}"}

    enemy = Monster("Dummy", "humanoid_warrior", level=level)
    enemy.health = enemy.current_health = 10 ** 9
    engine = CombatEngine(owner, enemy, party=Party(owner))

    # GIVE EVERY ABILITY A REASON TO FIRE, or "never cast" cannot be told
    # apart from "correctly declined". A healing pet in a fight where
    # nobody is hurt SHOULD never heal, and Devour Magic SHOULD never fire
    # into a target carrying nothing - reporting those as dead abilities
    # would be the instrument accusing correct behaviour, which is the way
    # this has gone wrong before. So the fight is set up the way a real one
    # looks by the time a support pet matters:
    #   - the owner is hurt, so a party or ally heal has someone to heal
    #   - the target carries a dispellable Magic buff, so a dispel has
    #     something to strip
    owner.current_health = max(1, int(owner.health * 0.5))
    from combat.status_effects import StatusEffect, EffectType, DispelType
    enemy.apply_status_effect(StatusEffect(
        effect_id="audit_dispel_bait", name="Audit Bait",
        effect_type=EffectType.BUFF, duration=999,
        stat_mods={"attack_power": 1}, dispel_type=DispelType.MAGIC,
        source_name="audit", real_time_seconds=None))

    learned = {a.ability_id for a in pet.ability_book.get_all_abilities()
               if a.is_learned}
    slot0 = next((aid for aid in pet.hotbar if aid), None)

    # COUNT SUCCESSES, NOT CASTS. The first version of this appended the
    # chosen ability_id every turn and reported every pet "acted" 20 of 20
    # turns - while half of them finished the fight sitting at 0 resource.
    # choose_action's last resort is slot 0 whether or not slot 0 is
    # affordable, and execute_pet_action logs "hesitates" when use() fails.
    # A pet that hesitates seventeen turns running is the bug; a pet that
    # "acted" twenty times is the instrument flattering the engine.
    used, dry_at = [], None
    for turn in range(1, turns + 1):
        chosen = pet.choose_action(enemy, allies=engine.living_allies())
        before = len(engine.combat_log)
        # execute_pet_action takes its pet from current_actor and calls
        # _end_turn itself, which is where cooldowns tick and where a
        # combatant's resources would regen if anything regenerated a
        # pet's. Driving it this way rather than reimplementing the turn
        # is the whole point: the housekeeping under test is the engine's.
        engine.current_actor = pet
        engine.execute_pet_action()
        tail = " ".join(engine.combat_log[before:])
        failed = (chosen is None or "hesitates" in tail
                  or "no action to take" in tail)
        if failed:
            used.append(None)
            if dry_at is None:
                dry_at = turn
        else:
            used.append(chosen.ability_id)
            dry_at = None          # it recovered; only a terminal run counts

    acted = [u for u in used if u]
    basic = [u for u in acted if u == slot0]
    unreached = sorted(learned - set(acted))
    return {
        "pet": pet,
        "level": level,
        "owner": owner,
        "owner_class": cls,
        "acted": len(acted),
        "basic": len(basic),
        "turns": turns,
        "dry_at": dry_at,
        "resource": f"{pet.get_resource(pet.resource_type):.0f}/"
                    f"{pet.get_resource_max(pet.resource_type):.0f} "
                    f"{pet.resource_type}",
        "unreached": unreached,
        "learned": len(learned),
    }


#: effect_types Pet.choose_action has a step for. Kept here rather than
#: imported so that adding a branch to the AI without adding it here shows
#: up as a reported "no AI branch" rather than passing silently.
HANDLED_EFFECT_TYPES = frozenset({
    "heal", "hot", "restore_resource", "dispel", "buff",
    "dot", "spell_dot", "debuff",
    "damage", "spell_damage", "ranged_damage",
    "damage_and_heal", "damage_and_restore_mana",
})


def measure_damage(pet, owner, ability, level, samples=24):
    """Average real damage dealt by one cast, through the real engine."""
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    total = 0
    for _ in range(samples):
        enemy = Monster("Rank", "humanoid_warrior", level=level)
        enemy.health = enemy.current_health = 10 ** 9
        engine = CombatEngine(owner, enemy, party=Party(owner))
        pet.current_mana = getattr(pet, "max_mana", 0)
        pet.current_energy = getattr(pet, "max_energy", 0)
        ability.turns_remaining = 0
        before = enemy.current_health
        ability.use(pet, enemy, party=[owner], engine=engine)
        for _ in range(6):                  # tick any DoT out
            try:
                enemy.tick_status_effects()
            except Exception:               # noqa: BLE001
                pass
        total += before - enemy.current_health
    return total / samples


def check_ranking(tid, r):
    """Does effect_value order match measured damage order?

    choose_action ranks damage abilities by effect_value, which is NOT a
    damage estimate: an AP-scaled `damage` and an SP-scaled `spell_damage`
    carrying the same number hit for different amounts, and three templates
    (abomination, hellfire_abyssal, infernal) pair one of each on a pet
    whose spell power is well under its attack power. Measured when this
    was written, the effect_value order was correct on every template - so
    the ranking is deliberately left alone and this checks that it stays
    correct, rather than a second copy of the engine's damage maths being
    put in the AI to rank two buttons.
    """
    DAMAGE = {"damage", "spell_damage", "ranged_damage",
              "damage_and_heal", "damage_and_restore_mana"}
    pet, owner = r["pet"], r["owner"]
    options = [a for a in pet.ability_book.get_all_abilities()
               if a.is_learned and a.effect_type in DAMAGE]
    if len(options) < 2:
        return None
    measured = {a.ability_id: measure_damage(pet, owner, a, r["level"])
                for a in options}
    by_ev = max(options, key=lambda a: a.effect_value)
    by_real = max(options, key=lambda a: measured[a.ability_id])
    if by_ev.ability_id == by_real.ability_id:
        return None
    return (f"picks {by_ev.name} (ev={by_ev.effect_value}, "
            f"hits {measured[by_ev.ability_id]:.0f}) over {by_real.name} "
            f"(ev={by_real.effect_value}, hits {measured[by_real.ability_id]:.0f})")


def main(argv):
    from combat.pet_templates import PET_TEMPLATES

    only = argv[argv.index("--pet") + 1] if "--pet" in argv else None
    turns = int(argv[argv.index("--turns") + 1]) if "--turns" in argv else TURNS
    items = ([(only, PET_TEMPLATES[only])] if only
             else sorted(PET_TEMPLATES.items()))

    print(f"{len(items)} pet(s), {turns} turns each\n")
    print(f"{'template':24} {'acted':>5} {'basic':>5} {'dry':>5}  "
          f"{'resource left':>18}  unreached")
    print("-" * 100)

    starved, unreached_total, rows = [], 0, []
    ranking_disagreements = []
    for tid, t in items:
        r = run_one(tid, t, turns)
        if "skip" in r:
            print(f"{tid:24} SKIPPED - {r['skip']}")
            continue
        rows.append((tid, r))
        dry = str(r["dry_at"]) if r["dry_at"] else "-"
        if r["dry_at"]:
            starved.append((tid, r["dry_at"]))
        unreached_total += len(r["unreached"])
        print(f"{tid:24} {r['acted']:>5} {r['basic']:>5} {dry:>5}  "
              f"{r['resource']:>18}  "
              f"{', '.join(r['unreached']) if r['unreached'] else '-'}")
        detail = check_ranking(tid, r)
        if detail:
            ranking_disagreements.append((tid, detail))

    print()
    if starved:
        print(f"RAN DRY: {len(starved)} of {len(rows)} pets spent the rest of "
              f"the fight unable to act at all.")
        for tid, turn in sorted(starved, key=lambda x: x[1]):
            print(f"    {tid:24} at turn {turn}")
        print("    Nothing in the engine regenerates a pet's resource pool:")
        print("    CombatEngine._end_turn_housekeeping calls")
        print("    restore_resources_between_turns when the actor HAS it, and")
        print("    Character and Monster both do. Pet does not.")
        print()
    if unreached_total:
        # SAY WHICH KIND OF NEVER. An ability whose effect_type the AI has
        # no branch for can never fire at all; one the AI handles but whose
        # firing condition did not arise is working correctly and only
        # needs the condition judged. Reporting both as "dead" is how an
        # audit ends up accusing correct behaviour.
        print(f"NEVER CAST: {unreached_total} learned ability(ies) were never")
        print("    chosen, with the fight set up so each one had a reason to")
        print("    fire (owner at 50% health, target carrying a dispellable")
        print("    Magic buff). Split by cause:")
        no_branch, condition = [], []
        for tid, r in rows:
            for aid in r["unreached"]:
                ab = r["pet"].ability_book.get_ability(aid)
                et = getattr(ab, "effect_type", "?")
                (condition if et in HANDLED_EFFECT_TYPES
                 else no_branch).append((tid, aid, et))
        if no_branch:
            print("\n    NO AI BRANCH - cannot fire on any turn of any fight:")
            for tid, aid, et in no_branch:
                print(f"        {tid:22} {aid:38} effect_type={et}")
            print("        Pet.choose_action has no step that returns this")
            print("        effect_type, so the ability is authored, learned,")
            print("        slotted, paid for and unreachable.")
        if condition:
            print("\n    CONDITION NEVER AROSE - the AI handles it; judge the gate:")
            for tid, aid, et in condition:
                print(f"        {tid:22} {aid:38} effect_type={et}")
    if ranking_disagreements:
        print(f"\nRANKING: {len(ranking_disagreements)} pet(s) where the")
        print("    effect_value order of the damage abilities disagrees with")
        print("    the measured damage order, so choose_action picks the")
        print("    weaker button. effect_value is not a damage estimate - the")
        print("    same number means different things to an AP-scaled")
        print("    `damage` and an SP-scaled `spell_damage`. This was true of")
        print("    no template when the check was written; a name here means")
        print("    it has become true and the ranking needs a real estimate.")
        for tid, detail in ranking_disagreements:
            print(f"        {tid:22} {detail}")
    if not starved and not unreached_total and not ranking_disagreements:
        print("Every pet acted every turn, cast every ability it knows, and")
        print("ranks its damage abilities in the order they actually hit.")
    return 1 if (starved or unreached_total or ranking_disagreements) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
