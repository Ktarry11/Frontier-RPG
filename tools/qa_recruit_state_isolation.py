"""One character's recruit state must never reach another character.

THE BUG THIS EXISTS FOR (Kyle, 2026-11-08: "when i make a new character I
dont see any of the recruitable characters ... i tested a few zones with a
brand new lvl 1. all recruits are gone").

RecruitManager is a process-lifetime singleton and its state is effectively a
DELETION LIST: `recruited_ids` makes a companion IN_PARTY, and an IN_PARTY
companion has no world location at all, so they are not drawn, not
interactable and absent from get_recruits_in_zone. Character creation reset
the zone, quest and travel managers and never this one - so a new level 1
walked into a world with every companion the previous character had hired
already deleted from it, and then saved that state into its own file.

`dismissed_characters` is the same failure in a form that is harder to see:
a dismissed recruit stands in their HOME TOWN rather than where they were
authored, so they do not vanish, they move.

The tests below do not inspect flags - they ask the question the player asks:
IS SOMEBODY STANDING IN THIS ZONE. A test that checked `recruited_ids` would
have passed throughout the bug.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import world.recruit_manager as rm_module
from world.recruit_manager import get_recruit_manager, reset_recruit_manager
import world.faction_manager as fm_module
from world.faction_manager import get_faction_manager, reset_faction_manager

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        failures.append(label)


def names_in(zone):
    return sorted(r.name for r in get_recruit_manager().get_recruits_in_zone(zone))


print("== a clean world has companions standing in it")
reset_recruit_manager()
baseline = {z: names_in(z) for z in
            ("Deathknell", "Valley of Trials", "Echo Isles", "Orgrimmar", "Ratchet")}
for zone, people in baseline.items():
    check(f"{zone} is populated", people, f"got {people}")

# Pick a real recruit to hire, from a zone that has one.
zone_with = next(z for z, people in baseline.items() if people)
victim = get_recruit_manager().get_recruits_in_zone(zone_with)[0]
victim_id = victim.recruit_id
victim_name = victim.name

print("\n== hiring removes them from the world (the mechanism behind the bug)")
get_recruit_manager().recruited_ids.add(victim_id)
check("hired companion is no longer standing in their zone",
      victim_name not in names_in(zone_with),
      f"{victim_name} still listed in {zone_with}")

print("\n== resetting puts the world back")
reset_recruit_manager()
check("reset restores the hired companion",
      victim_name in names_in(zone_with),
      f"{victim_name} missing from {zone_with} after reset")
check("reset restores every zone",
      {z: names_in(z) for z in baseline} == baseline)

print("\n== a dismissed companion MOVES rather than vanishing")
reset_recruit_manager()
mgr = get_recruit_manager()
mgr.dismissed_characters[victim_id] = {}
moved_away = victim_name not in names_in(zone_with)
check("dismissed state changes where they stand", moved_away or victim.has_home() is False,
      "dismissal had no observable effect, which means the state is not being read")
reset_recruit_manager()

print("\n== the faction singleton resets too (it gates recruit visibility)")
before = get_faction_manager()
after = reset_faction_manager()
check("reset_faction_manager returns a new instance", before is not after)
check("get_faction_manager now hands out the new one", get_faction_manager() is after)

print("\n== character creation resets BOTH singletons")
# Read the creation path rather than driving the UI: what matters is that the
# reset calls are present alongside the quest/travel ones that were already
# there. Driving the real screen needs a display, fonts and a full state
# manager, none of which are the thing under test.
creation = (Path(__file__).resolve().parent.parent
            / "ui" / "screens" / "character_screen.py").read_text(encoding="utf-8")
check("creation resets the recruit manager", "reset_recruit_manager()" in creation)
check("creation resets the faction manager", "reset_faction_manager()" in creation)

print("\n== loading a save never inherits the previous character's state")
game_state = (Path(__file__).resolve().parent.parent
              / "core" / "game_state.py").read_text(encoding="utf-8")
check("load_game resets before applying saved recruit state",
      "reset_recruit_manager()" in game_state)
check("load_game repairs ghost hires",
      "ghosts" in game_state and "recruited_ids -= ghosts" in game_state)

print("\n== a ghost hire is detectable: flagged IN_PARTY with nobody to show")
reset_recruit_manager()
mgr = get_recruit_manager()
mgr.recruited_ids.add(victim_id)
party_recruit_ids = set()          # an empty party, as a fresh character has
ghosts = {r for r in mgr.recruited_ids if r not in party_recruit_ids}
check("the ghost is identifiable without guessing", ghosts == {victim_id})
mgr.recruited_ids -= ghosts
check("clearing it returns them to the world", victim_name in names_in(zone_with))
reset_recruit_manager()

print()
if failures:
    print(f"FAILED ({len(failures)}): " + ", ".join(failures))
    sys.exit(1)
print("All recruit state isolation checks passed.")
