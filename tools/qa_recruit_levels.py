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
  5. A REHIRE IS CAUGHT UP TOO, BODY AND KIT. Kyle: "these are real people bro. They're not
     just sitting there doing nothing." Somebody dismissed at 20 and re-hired at 50 comes back
     at 46, with stats, talent points and gear to match, keeping the RARITY the player invested
     in them and carrying none of the level 20 kit they obviously sold years ago. The level has
     to come through Character.level_up() rather than an assignment, or they return with a level
     46 label on a level 20 body - so the health and talent points are checked, not just .level.

  6. THE GATE JUDGES THE LEVEL THEY WOULD ACTUALLY JOIN AT, snapshot included. Kyle: "a lvl 30
     player can't recruit a lvl 46. So they won't de-level, no." This file's first version asked
     RecruitNPC.effective_level, which knows only the AUTHORED level - so a Silas dismissed at 46
     read as a level 26 hire, a level 30 player sailed through the gate, and then got the level 46
     character anyway. The rule and the number it judges now both come from RecruitManager, and
     this claim re-hires a high-level veteran at every player level to prove it.

  7. THEIR GEAR MATCHES THE LEVEL THEY JOIN AT. The catch-up level is generated in one place and
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

MGR = get_recruit_manager()

PLAYER_LEVELS = range(1, 61)
#: building a Character is slow, so claim 5 samples rather than sweeping all 44.
GEAR_SAMPLE = 6


def main():
    recs = list(MGR.recruits.values())
    bad = []
    print(f"{len(recs)} recruits, CATCHUP = {CATCHUP}\n")

    for r in recs:
        for pl in PLAYER_LEVELS:
            lvl = MGR.join_level(r, pl)
            blocked = bool(MGR.block_reason(r, pl))

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
            if not MGR.block_reason(r, edge - 1):
                bad.append(f"{r.name} (level {r.level}) should refuse a player at {edge - 1}.")
            if MGR.block_reason(r, edge):
                bad.append(f"{r.name} (level {r.level}) should come with a player at {edge}.")

        # 4. anyone authored at or below the player is always reachable
        for pl in PLAYER_LEVELS:
            if r.level <= pl and MGR.block_reason(r, pl):
                bad.append(f"{r.name} (level {r.level}) is blocked for a player at {pl} who is "
                           f"already above them - the two rules have stopped interlocking.")
                break

    # 5. a rehire catches up, body and kit
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    mgr = MGR
    probe = next(r for r in recs if r.recruit_id != "asher_coleman" and r.level <= 20)
    left = probe.build_character(probe.level + CATCHUP)      # hired around their own level
    for sl in ("chest", "legs"):
        try:
            it = gen.generate_item_for_class(left.char_class, left.level, slot=sl, rarity="rare")
            left.inventory.append(it)
            left.equip_item(it)
        except Exception:
            pass
    junk = gen.generate_item_for_class(left.char_class, left.level, slot="feet", rarity="common")
    left.inventory.append(junk)
    def _spent(ch):
        """Talent points actually PLACED in the character's trees."""
        total = 0
        for tree in (getattr(ch, "talent_trees", None) or {}).values():
            total += getattr(tree, "total_points_spent", lambda: 0)()
        return total

    old_lvl, old_hp, old_tp = left.level, left.health, left.talent_points_available
    old_spent = _spent(left)
    mgr.mark_recruited(probe.recruit_id)
    mgr.dismiss(left)
    back = mgr.build_or_restore(probe, 50)

    want = probe.effective_level(50)
    if back.level != want:
        bad.append(f"rehire: {probe.name} left at {old_lvl}, returns at {back.level}, want {want}")
    # TALENT POINTS ARE SPENT, NOT BANKED. This used to assert that
    # talent_points_available went UP, which was right when it was written and stopped being
    # right the moment _catch_up gained its auto_spend_talents() call - a companion now comes
    # back BUILT, so every point they gained is immediately placed and the unspent pool is 0
    # both before and after. The check was failing on a feature working correctly. What it
    # actually wants to know is that the levels were GAINED through level_up() rather than
    # assigned, so it measures the two things level_up() produces that an assignment does not:
    # a bigger health pool, and more points placed in the trees.
    back_spent = _spent(back)
    if back.health <= old_hp or back_spent <= old_spent:
        bad.append(f"rehire: {probe.name} returns labelled level {back.level} but with a level "
                   f"{old_lvl} body - health {old_hp}->{back.health}, talent points spent "
                   f"{old_spent}->{back_spent}. The level was assigned rather "
                   f"than gained through level_up().")
    stale = sorted(i.item_level for i in back.equipment.slots.values()
                   if i and i.item_level < back.level - CATCHUP)
    if stale:
        bad.append(f"rehire: {probe.name} returns at {back.level} still wearing item levels "
                   f"{stale}")
    if any(getattr(i, "item_level", 10 ** 6) < back.level - CATCHUP for i in back.inventory):
        bad.append(f"rehire: {probe.name} came back still hauling their old kit in their pack.")
    if not any(i.rarity == "rare" for i in back.equipment.slots.values() if i):
        bad.append(f"rehire: {probe.name} was given rares and returned without any - the "
                   f"player's investment was not preserved.")
    mgr.recruited_ids.discard(probe.recruit_id)
    mgr.dismissed_characters.pop(probe.recruit_id, None)
    print(f"rehire probe: {probe.name} left at {old_lvl}, returns at {back.level} "
          f"(health {old_hp}->{back.health}, talent points spent {old_spent}->{back_spent}, "
          f"unspent {old_tp}->{back.talent_points_available})\n")

    # 6. the gate sees the snapshot, not just the authored level
    vet = next(r for r in recs if r.recruit_id != "asher_coleman" and r.level <= 20)
    high = vet.build_character(50)
    MGR.mark_recruited(vet.recruit_id)
    MGR.dismiss(high)
    for pl in PLAYER_LEVELS:
        jl = MGR.join_level(vet, pl)
        if jl < high.level:
            bad.append(f"gate: {vet.name} left at {high.level} but join_level says {jl} for a "
                       f"player at {pl} - they must not de-level to suit the player.")
        blocked = bool(MGR.block_reason(vet, pl))
        if blocked != (jl - pl > CATCHUP):
            bad.append(f"gate: {vet.name} (would join at {jl}) blocked={blocked} for a player at "
                       f"{pl}, rule says {jl - pl > CATCHUP}")
        got = MGR.build_or_restore(vet, pl)
        if blocked and got is not None:
            bad.append(f"gate: {vet.name} is blocked for a player at {pl} but build_or_restore "
                       f"still handed over a level {got.level} character.")
        if not blocked and got is None:
            bad.append(f"gate: {vet.name} is hireable at player {pl} but build_or_restore "
                       f"refused.")
    print(f"gate probe: {vet.name} dismissed at {high.level} is blocked below player "
          f"{high.level - CATCHUP}, and never de-levels\n")
    MGR.recruited_ids.discard(vet.recruit_id)
    MGR.dismissed_characters.pop(vet.recruit_id, None)

    # 7. gear follows the join level.
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
        ok = [r for r in recs if not MGR.block_reason(r, pl)]
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
