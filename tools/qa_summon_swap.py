"""
Summoning a demon costs mana, takes the turn, and REPLACES the demon already out.

Kyle, 10 Nov: "Warlock glitch - if i use summon demon, its instant, costs 0 mana, and doesnt
skip my turn. (if i summon 1 demon - i CANT USE SUMMON TO REPLACE IT WITH ANOTHER)."

Two separate faults. The data had every warlock summon free and instant. And the engine only
re-read the pet list when the NUMBER of pets changed, so swapping one demon for another was
never noticed: the dismissed demon stayed in the fight and the new one never joined it.

A real CombatEngine fight, every summon cast through execute_ability:
  - each warlock summon costs mana and ends the caster's turn
  - after each one the engine fields exactly the new demon - in pets AND in combatants - and
    the old one is in neither
  - the same swap check for every other class with a replacing (non-additional) summon
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROBLEMS = []


def fail(msg):
    PROBLEMS.append(msg)
    print(f"  FAIL {msg}")


def fight(cls, level=60):
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    c = Character(name="Summoner", char_class=cls, level=level)
    foe = Monster("Training Target", "humanoid_warrior", level=level)
    foe.current_health = foe.max_health = 999999
    return c, foe, CombatEngine(c, foe, party=Party(c), enemies=[foe])


def top_up(c):
    """Fill every pool through the generic API - the CoA pools are dict-backed and have no
    current_<name> attribute to poke."""
    for res in ("mana", "rage", "energy", "focus", "life_force", "souls", "felfury",
                "archery_points"):
        try:
            mx = c.get_resource_max(res)
            if mx:
                c.set_resource(res, mx)
        except Exception:
            pass


def cast(engine, c, foe, ability_id):
    ab = c.ability_book.get_ability(ability_id)
    ab.turns_remaining = 0
    top_up(c)
    engine.current_actor = c
    c.turn_meter = 100.0
    # MEASURE THE COST AT THE CAST, not across the turn. Ending a turn regenerates mana, and
    # from a full pool that regen is clamped away while from anywhere else it hides a small
    # cost entirely - a 10-mana Imp read as "cost 0" until the pool was read inside the cast.
    res = ab.resource_type
    seen = {}
    real_end = engine._end_turn

    def end_turn(actor, *a, **k):
        if actor is c and "after" not in seen:
            seen["after"] = c.get_resource(res) if res else 0
        return real_end(actor, *a, **k)
    engine._end_turn = end_turn
    before = c.get_resource(res) if res else 0
    try:
        ok, msg = engine.execute_ability(c, ability_id, foe)
    finally:
        engine._end_turn = real_end
    took_turn = "after" in seen
    spent = before - seen.get("after", c.get_resource(res) if res else 0)
    engine.update(0.0)
    return ok, msg, spent, took_turn


def check_warlock():
    print("\nwarlock")
    c, foe, engine = fight("Warlock")
    order = ["warlock_summon_imp", "warlock_summon_voidwalker", "warlock_summon_succubus",
             "warlock_summon_felhunter", "warlock_summon_imp"]
    previous = None
    for aid in order:
        ok, msg, spent, took_turn = cast(engine, c, foe, aid)
        if not ok:
            fail(f"{aid}: cast failed - {msg}")
            continue
        pet = c.active_pet
        problems = []
        if spent <= 0:
            problems.append(f"cost {spent} mana")
        if not took_turn:
            problems.append("did not use the turn")
        if [p for p in engine.pets] != [pet]:
            problems.append(f"engine fields {[p.name for p in engine.pets]}, owner has {pet.name}")
        if pet not in engine.combatants:
            problems.append("the new demon is not a combatant")
        if previous is not None and (previous in engine.pets or previous in engine.combatants):
            problems.append(f"the dismissed {previous.name} is still in the fight")
        if problems:
            fail(f"{aid}: " + "; ".join(problems))
        else:
            was = f", replacing the {previous.name}" if previous is not None else ""
            print(f"  ok   {pet.name}: {spent} mana, takes the turn{was}")
        previous = pet


def check_other_classes():
    print("\nother classes with a replacing summon")
    seen = 0
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        if path.stem == "warlock":
            continue
        blob = json.loads(path.read_text())
        entries = blob.get("abilities", blob) if isinstance(blob, dict) else blob
        if isinstance(entries, dict):
            entries = list(entries.values())
        summons = [a for a in entries if isinstance(a, dict)
                   and a.get("effect_type") == "summon_pet" and not a.get("additional_pet")]
        if len(summons) < 2:
            continue
        cls = " ".join(w.capitalize() for w in path.stem.split("_"))
        try:
            c, foe, engine = fight(cls)
        except Exception as exc:
            fail(f"{cls}: rig could not build the class - {type(exc).__name__}: {exc}")
            continue
        previous = None
        for a in summons:
            if c.ability_book.get_ability(a["ability_id"]) is None:
                continue
            ok, msg, spent, took_turn = cast(engine, c, foe, a["ability_id"])
            if not ok:
                continue                      # spec-gated or otherwise unavailable to this build
            pet = c.active_pet
            seen += 1
            if [p for p in engine.pets if p.owner is c and p is not pet and p not in
                    getattr(c, "extra_pets", [])]:
                fail(f"{cls} {a['name']}: a dismissed pet is still in the fight")
            elif pet not in engine.pets:
                fail(f"{cls} {a['name']}: the new pet never joined the fight")
            elif previous is not None and previous is not pet and previous in engine.combatants:
                fail(f"{cls} {a['name']}: the dismissed {previous.name} is still a combatant")
            previous = pet
        print(f"  ok   {cls}: swaps checked")
    if seen == 0:
        fail("no other class's summon could be cast - the rig is not reaching them")


def main():
    check_warlock()
    check_other_classes()
    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        return 1
    print("\nsummons OK - they cost, they take the turn, and they replace.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
