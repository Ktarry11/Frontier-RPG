#!/usr/bin/env python3
"""A drop refused for a full bag must be reported on the VICTORY SCREEN.

Kyle, 2026-10-31: he reported that none of the six Grom's Rest bosses dropped
loot. They all did. His bags were full, and the game said so only in the combat
log - "the combat log is also buried under everything" - while the victory
panel he was looking at showed nothing at all.

That made "nothing dropped" and "something dropped and you cannot carry it"
render identically, which is how a full bag reads as six broken bosses. It cost
a full audit of all 334 bosses in the game to find out the game was working.

combat_engine now records every refused drop in loot_missed (all FIVE bag-full
branches - gear, epics, recipe scrolls, quest/material drops and vendor trash -
which were five copies of one rule), and combat_screen draws it as a banner.

NEGATIVE CONTROL INCLUDED, because a test that only checks the full-bag case
would also pass if loot_missed were populated unconditionally.
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.character import Character
from world.creature_manager import CreatureManager
from combat.combat_engine import CombatEngine

BOSSES = ["Satyr Warlord", "Void Handmaiden", "Doomguard Sentinel",
          "Corrupted Ancient", "Felguard Overseer", "Lord Nightmare"]


def kill(boss_name, fill_bag):
    cm = CreatureManager()
    player = Character("Bag QA", "shaman", level=30)
    if fill_bag:
        # Fill to the real cap rather than guessing a number: keep adding until
        # the game itself refuses, which is what the player hit.
        from entities.loot_generator import LootGenerator
        lg = LootGenerator()
        guard = 0
        while guard < 500:
            it = lg.generate_boss_loot(creature_level=20, char_class="shaman",
                                       player_level=30)
            if it is None or not player.add_to_inventory(it):
                break
            guard += 1
    m = cm.spawn_creature(boss_name, zone_name="Ashenvale East")
    ce = CombatEngine(player, m, zone="Grom's Rest")
    for e in ce.enemies:
        e.current_health = 0
    ce._resolve_victory()
    return ce


def main():
    random.seed(99)
    ok = True

    print("  bags FULL - the case Kyle hit:")
    any_missed = False
    for b in BOSSES:
        ce = kill(b, fill_bag=True)
        missed = list(getattr(ce, "loot_missed", []))
        gained = [getattr(l, "name", str(l)) for l in getattr(ce, "loot_gained", [])]
        if missed:
            any_missed = True
        print(f"    {b:22s} missed={missed or '-'}  gained={gained or '-'}")
    if not any_missed:
        ok = False
        print("\n    FAIL - bags were full and nothing was recorded as missed.")
        print("    The victory screen would again show nothing at all.")
    else:
        print("\n    ok - the victory screen now names what was left behind")

    print("\n  NEGATIVE CONTROL, bags EMPTY - nothing may be reported missed:")
    bad = []
    for b in BOSSES:
        ce = kill(b, fill_bag=False)
        missed = list(getattr(ce, "loot_missed", []))
        gained = [getattr(l, "name", str(l)) for l in getattr(ce, "loot_gained", [])]
        if missed:
            bad.append((b, missed))
        print(f"    {b:22s} missed={missed or '-'}  gained={gained or '-'}")
    if bad:
        ok = False
        print(f"\n    FAIL (control) - reported a miss on an EMPTY bag: {bad}")
        print("    A warning that always fires is a warning nobody reads.")
    else:
        print("\n    ok (control) - silent when the player can carry the drop")

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
