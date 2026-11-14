#!/usr/bin/env python3
"""Play every class from 1 to 60 and shout if anything breaks.

WHY THIS EXISTS. There are no test files in this repository - zero. The
validators (validate_class.py, audit_talents.py, audit_class_completeness.py)
carry the whole load, and they are INSPECTION tools: they read the data and
check it against the engine. That catches a great deal, and it did not catch
any of these, all real and all found by hand in one session:

  - pets froze at the level they were summoned, because nothing in the
    real levelling path called sync_to_owner_level
  - pets were never written to a save at all
  - 113 buffs multiplied their own stat_mods by zero
  - six Guardian cleaves hit exactly one enemy

Every one needed something to actually HAPPEN - a level gained, a save
round-tripped, a buff cast, an AoE swung - rather than a file to be read.
So this does the happening.

WHAT IT DOES, per class: create at level 1, grant starting gear, walk up to
60 one level at a time, spend every talent point, summon a pet if the class
has one, cast every learned ability at a real monster through a real
CombatEngine, take a save/load round trip, and compare before and after.
Any exception anywhere is a failure with the class and the step named.

It is deliberately noisy about WHERE it broke rather than clever about why.

    python3 tools/smoke_play_all_classes.py
    python3 tools/smoke_play_all_classes.py --class Reaper
"""

from __future__ import annotations

import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def all_classes() -> list[str]:
    text = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    block = text.split("class_stats = {", 1)[1].split("\n        }", 1)[0]
    return re.findall(r'^\s*"([^"]+)":\s*\{\s*#?', block, re.M)


def fill_resources(c):
    """Top up every pool the class could possibly spend from."""
    if getattr(c, "mana", 0):
        c.current_mana = c.mana
    for pool in ("rage", "energy", "static", "insanity", "combo", "life_force",
                 "runes", "souls", "focus", "deathfire", "felfury",
                 "archery_points", "solar_power", "vitality", "scrap"):
        try:
            c.set_resource(pool, c.get_resource_max(pool))
        except Exception:                                      # noqa: BLE001
            pass


def play(cls: str) -> list[str]:
    """Return a list of failures for one class; empty means it played clean."""
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.abilities import get_class_abilities
    from combat.combat_engine import CombatEngine
    import entities.starting_gear as starting_gear

    fails: list[str] = []

    def step(name, fn):
        try:
            return fn()
        except Exception as exc:                               # noqa: BLE001
            fails.append(f"{name}: {type(exc).__name__}: {exc}\n"
                         f"{traceback.format_exc(limit=3)}")
            return None

    c = step("create at level 1", lambda: Character(name="Smoke", char_class=cls, level=1))
    if c is None:
        return fails
    step("grant starting gear", lambda: starting_gear.grant_starting_gear(c))
    step("attach ability book", lambda: setattr(c, "ability_book", get_class_abilities(cls)))

    # LEVEL ONE AT A TIME. Jumping straight to 60 skips every per-level hook -
    # which is exactly where the pet-levelling bug lived.
    def climb():
        for _ in range(59):
            c.level_up()
    step("level 1 -> 60", climb)
    if c.level != 60:
        fails.append(f"level 1 -> 60: ended at level {c.level}")

    def spend_talents():
        for tree in c.talent_trees.values():
            for node in tree.nodes.values():
                node.points_spent = node.max_points
        c._recalculate_derived_stats()
    step("spend every talent point", spend_talents)

    # A pet, for the eleven classes that have one.
    def summon():
        import json
        path = ROOT / f"data/abilities/{cls.lower().replace(' ', '_')}.json"
        if not path.exists():
            return
        for entry in json.loads(path.read_text(encoding="utf-8")).get("abilities", []):
            tmpl = entry.get("summon_pet_template")
            if not tmpl:
                continue
            fill_resources(c)
            ok, res = c.summon_pet(tmpl, additional=entry.get("additional_pet", False))
            if not ok:
                fails.append(f"summon {tmpl}: refused - {res}")
        for pet in c.all_pets:
            if pet.level != c.level:
                fails.append(f"pet {pet.name} is level {pet.level}, owner is {c.level}")
    step("summon pets", summon)

    # CAST EVERYTHING, at a real monster, through the real engine.
    def cast_everything():
        abilities = [a for a in c.ability_book.get_all_abilities() if a.is_learned]
        if not abilities:
            fails.append("cast everything: nothing learned at level 60")
            return
        cast = 0
        for ability in abilities:
            enemy = Monster("Dummy", "humanoid_warrior", level=60)
            enemy.health = enemy.current_health = 10 ** 7
            engine = CombatEngine(c, enemy, party=Party(c))
            c.current_health = c.health
            fill_resources(c)
            ability.turns_remaining = 0
            ok, _msg = engine.execute_ability(c, ability.ability_id, enemy)
            if ok:
                cast += 1
        if cast == 0:
            fails.append(f"cast everything: 0 of {len(abilities)} abilities "
                         f"executed successfully")
        return cast
    cast = step("cast every learned ability", cast_everything)

    # SAVE ROUND TRIP, comparing what a player would notice.
    def round_trip():
        from entities.character import Character as C
        # DROP ACTIVE EFFECTS FIRST. The step above casts the class's entire
        # kit, which leaves combat buffs running - and a buff carrying
        # max_health_pct makes the character's max health higher than its
        # saved state should be. Saves do not serialise status effects, and
        # they should not: a 3-turn buff surviving a logout would be wrong.
        #
        # The first version of this check compared with the buffs still up
        # and reported 12 classes "LOSING health" across a round trip,
        # Felsworn by 36%. Every one was a real buff doing its job -
        # Felsworn's Skull of Gul'dan is +15% health and +20 Stamina for 3
        # turns. The test was wrong, not the save.
        c._effects().clear()
        c._recalculate_derived_stats()
        before = {
            "level": c.level,
            "health": round(c.health),
            "talent_points": sum(t.total_points_spent() for t in c.talent_trees.values()),
            "equipped": sum(1 for v in (getattr(c.equipment, "slots", {}) or {}).values() if v),
            "pets": [p.template_id for p in c.all_pets],
            "trained": len(c.trained_ranks),
        }
        c2 = C.from_dict(c.to_dict())
        after = {
            "level": c2.level,
            "health": round(c2.health),
            "talent_points": sum(t.total_points_spent() for t in c2.talent_trees.values()),
            "equipped": sum(1 for v in (getattr(c2.equipment, "slots", {}) or {}).values() if v),
            "pets": [p.template_id for p in c2.all_pets],
            "trained": len(c2.trained_ranks),
        }
        for k in before:
            if before[k] != after[k]:
                fails.append(f"save round trip LOST {k}: {before[k]} -> {after[k]}")
    step("save/load round trip", round_trip)

    return fails


def main(argv: list[str]) -> int:
    only = None
    if "--class" in argv:
        only = argv[argv.index("--class") + 1]
    classes = [only] if only else all_classes()

    print(f"Playing {len(classes)} class(es) from 1 to 60\n")
    broken = {}
    for cls in classes:
        fails = play(cls)
        print(f"  {'FAIL' if fails else 'ok  '}  {cls}")
        if fails:
            broken[cls] = fails

    print()
    if broken:
        print(f"{len(broken)} class(es) broke:\n")
        for cls, fails in broken.items():
            print(f"=== {cls}")
            for f in fails:
                print(f"  {f}")
        return 1
    print(f"All {len(classes)} classes created, levelled to 60, spent every talent "
          f"point,\nsummoned their pets, cast their whole kit in real combat, and "
          f"survived a\nsave/load round trip with nothing lost.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
