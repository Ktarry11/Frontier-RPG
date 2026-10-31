#!/usr/bin/env python3
"""Companions keep pace with the player, and the player cannot skip ahead to them.

    PYTHONPATH=. python3 tools/qa_recruit_levels.py

Kyle, two rules that are halves of one idea:

  "make it so players can not recruit a party member if they're more than 4 levels below them.
   So we can't recruit Kaelen if we are level 31 as he starts at lvl 36."
  "all recruitable characters will have their starting level but never fall more than 4 levels
   below the player. So in this example when you find Silas in ratchet he will be level 26 or 27."

FIVE CLAIMS:

  1. NOBODY IS EVER MORE THAN CATCHUP BELOW THE PLAYER. The point of catch-up - deciding at level
     30 that you want to try a rogue should not mean levelling one from 14.
  2. NOBODY IS EVER BELOW THEIR AUTHORED LEVEL. Catch-up only ever raises. A companion written at
     36 is a statement about who they are, and meeting them at 20 must not shrink them.
  3. THE GATE BITES EXACTLY WHERE KYLE SAID. More than CATCHUP levels above you and they refuse;
     at exactly CATCHUP they come. The boundary is the whole rule, so it is tested at the
     boundary and one level either side, not somewhere comfortably inside it.
  4. CATCH-UP MAKES EVERY LOW COMPANION REACHABLE. Because catch-up raises anyone below you to
     within CATCHUP, the gate can only ever block a companion authored ABOVE you - never one you
     walked past twenty levels ago. If this ever fails, the two rules have stopped interlocking
     and somebody in the world has become permanently unhirable.
  5. THEIR GEAR MATCHES THE LEVEL THEY JOIN AT. The catch-up level is generated in one place and
     the starter kit's item level in another, and they have to agree - a level 46 Silas in the
     level 14 kit he was authored with is the bug this claim exists to catch.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()

from world.recruit_manager import get_recruit_manager, CATCHUP  # noqa: E402

PLAYER_LEVELS = range(1, 61)
#: building a Character is slow, so claim 5 samples rather than sweeping all 44.
GEAR_SAMPLE = 6


def main():
    recs = list(get_recruit_manager().recruits.values())
    bad = []
    print(f"{len(recs)} recruits, CATCHUP = {CATCHUP}\n")

    for r in recs:
        for pl in PLAYER_LEVELS:
            lvl = r.effective_level(pl)
            blocked = bool(r.recruit_block_reason(pl))

            # 2. never below the authored level
            if lvl < r.level:
                bad.append(f"{r.name}: at player {pl} they are level {lvl}, BELOW their authored "
                           f"{r.level} - catch-up must only ever raise.")
            # 1. never more than CATCHUP below the player, once they are hireable
            if not blocked and lvl < pl - CATCHUP:
                bad.append(f"{r.name}: at player {pl} they join at {lvl}, {pl - lvl} levels down.")
            # 3. the gate, stated directly
            if blocked != (lvl - pl > CATCHUP):
                bad.append(f"{r.name}: at player {pl} (they are {lvl}) blocked={blocked}, but the "
                           f"rule says {lvl - pl > CATCHUP}.")

        # 3. the boundary, named
        edge = r.level - CATCHUP
        if edge > 1:
            if not r.recruit_block_reason(edge - 1):
                bad.append(f"{r.name} (level {r.level}) should refuse a player at {edge - 1}.")
            if r.recruit_block_reason(edge):
                bad.append(f"{r.name} (level {r.level}) should come with a player at {edge}.")

        # 4. anyone authored at or below the player is always reachable
        for pl in PLAYER_LEVELS:
            if r.level <= pl and r.recruit_block_reason(pl):
                bad.append(f"{r.name} (level {r.level}) is blocked for a player at {pl} who is "
                           f"already above them - the two rules have stopped interlocking.")
                break

    # 5. gear follows the join level.
    #
    # ASHER IS EXEMPT, and only Asher. He does not wear a generated starter kit at all - he has a
    # fixed, hand-authored loadout the player can never alter (RecruitNPC._build_asher_kit), which
    # is the entire design of him, so his item levels are flavour and not a stat budget. Catch-up
    # still applies to his LEVEL, so a player who backtracks to the Burning Blade Coven chain late
    # does not get a level 5 companion; it is only this one claim he sits outside.
    for r in sorted((x for x in recs if x.recruit_id != "asher_coleman"),
                    key=lambda x: x.level)[:GEAR_SAMPLE]:
        for pl in (None, 30, 55):
            char = r.build_character(pl)
            want = r.effective_level(pl)
            if char.level != want:
                bad.append(f"{r.name}: build_character({pl}) made level {char.level}, want {want}")
            ilvls = {i.item_level for i in char.equipment.slots.values() if i}
            off = [v for v in ilvls if abs(v - char.level) > 2]
            if off:
                bad.append(f"{r.name} joins at level {char.level} wearing item levels {sorted(off)}"
                           f" - the kit is not being built at the catch-up level.")

    lo = min(r.level for r in recs)
    hi = max(r.level for r in recs)
    print(f"authored levels {lo}-{hi}")
    for pl in (10, 20, 30, 40, 50):
        ok = [r for r in recs if not r.recruit_block_reason(pl)]
        join = sorted({r.effective_level(pl) for r in ok})
        print(f"  player {pl:2}: {len(ok):2}/{len(recs)} hireable, they join at levels "
              f"{join[0]}-{join[-1]}")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\nrecruit levels OK - nobody falls more than "
          f"{CATCHUP} below the player, nobody drops under their authored level, the gate bites "
          "exactly at the boundary, every companion at or below the player is reachable, and "
          "their gear matches the level they join at.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
