#!/usr/bin/env python3
"""Recruits arrive with their talents spent, and Asher arrives unchanged.

    PYTHONPATH=. python3 tools/qa_recruit_talents.py

Kyle: "Sure auto spend is fine bro."

A companion earns a talent point per level from 5 on, and before this nothing placed them. A
recruit hired at their authored level 38, or caught up from 20 to 46, joined the party with
thirty-odd unspent points and a completely empty tree - a level 46 healer missing most of their
healing, in a party the player is leaning on. Nothing warned about it because an unspent point is
not an error.

FIVE CLAIMS:

  1. EVERY RECRUIT SPENDS EVERYTHING. At their authored level and at a caught-up one.
  2. EVERY POINT LANDS IN THEIR LOCKED SPEC. They are spec locked; an auto-spend that wandered
     into another tree would hand the player a build the game forbids them to make by hand.
  3. THE POINTS ACTUALLY DID SOMETHING. Points spent must equal points granted, and the tree's
     own total must agree - the accounting has to close, not just look empty-ish.
  4. ASHER COLEMAN IS BYTE-IDENTICAL. He is fixed and hand-authored, through both doors:
     a fresh build and a re-hire catch-up.
  5. A FREE RESET STILL REFUNDS THE LOT. The whole reason auto-spending is safe is that the
     player can undo it, so that has to be true rather than assumed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from world.recruit_manager import RecruitManager, CATCHUP  # noqa: E402


def snapshot(char):
    """Everything about Asher that must not move.

    item_id is excluded, and ONLY item_id. It is a per-instance unique (`asher_chest_<6 hex>`),
    the same kind every other recruit's generated gear carries, so two Asher objects having
    different ones is correct rather than drift - two copies of a thing are two things.

    Everything else is in: name, stats, level, icons, abilities, hotbar, talents. The first
    version of this excluded nothing and failed, which is how the real bug under it surfaced -
    his armour ICONS were re-rolling too, on a loadout documented as fixed and unalterable, so
    his breastplate was plate11 on one build and plate14 on the next. That is now seeded. Had
    this been written loosely enough to pass first time, it would have hidden it.
    """
    def strip(node):
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k != "item_id"}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    return json.dumps(strip(char.to_dict()), sort_keys=True, default=str)


def main():
    bad = []
    rm = RecruitManager()
    recruits = list(rm.recruits.values()) if hasattr(rm, "recruits") else list(rm.all_recruits())
    if not recruits:
        print("no recruits found - the roster lookup in this tool is wrong, not the game")
        return 1

    checked = 0
    for rec in recruits:
        if rec.recruit_id == "asher_coleman":
            continue
        for player_level in (None, rec.level + 20):
            char = rec.build_character(player_level)
            if char.level < 5:
                continue        # no points exist below 5; nothing to spend
            checked += 1
            granted = char.level - 4
            spent_here = char.talent_trees[char.locked_spec].total_points_spent() \
                if char.locked_spec in char.talent_trees else 0
            spent_all = sum(t.total_points_spent() for t in char.talent_trees.values())

            # 1. nothing left over
            if char.talent_points_available != 0:
                bad.append(f"{rec.name} at level {char.level} joins with "
                           f"{char.talent_points_available} unspent talent point(s)")
            # 2. all of it in the locked tree
            if spent_all != spent_here:
                bad.append(f"{rec.name} spent {spent_all - spent_here} point(s) OUTSIDE their "
                           f"locked spec {char.locked_spec!r}, which the player cannot do by hand")
            # 3. the accounting closes
            if spent_all != granted:
                bad.append(f"{rec.name} at level {char.level} was granted {granted} point(s) but "
                           f"{spent_all} are accounted for in their trees")

    # 4. Asher, through both doors
    asher = next((r for r in recruits if r.recruit_id == "asher_coleman"), None)
    if asher is None:
        bad.append("asher_coleman is not in the roster at all")
    else:
        base = asher.build_character()
        again = asher.build_character()
        if snapshot(base) != snapshot(again):
            bad.append("Asher does not even build identically twice - something else is wrong")
        caught = RecruitManager._catch_up(asher.build_character(), base.level, regear=False)
        if snapshot(caught) != snapshot(base):
            bad.append("Asher changed going through _catch_up; he is supposed to come back "
                       "exactly as he left")
        if sum(t.total_points_spent() for t in base.talent_trees.values()) != 0:
            bad.append("Asher had talents auto-spent; he is hand-authored and must not be")

    # 5. a reset really refunds it
    probe = next((r for r in recruits if r.recruit_id != "asher_coleman"), None)
    if probe is not None:
        c = probe.build_character(probe.level + 20)
        before = sum(t.total_points_spent() for t in c.talent_trees.values())
        for t in c.talent_trees.values():
            t.reset_all()
        c._grant_talent_points()
        if before and c.talent_points_available != c.level - 4:
            bad.append(f"after a reset {probe.name} has {c.talent_points_available} point(s), "
                       f"not the {c.level - 4} they earned - the undo that makes auto-spend safe "
                       f"does not fully work")

    print(f"{checked} recruit build(s) checked across {len(recruits) - 1} recruits "
          f"(+ Asher, who must not move); catch-up window is {CATCHUP} levels")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("\nrecruit talents OK - every recruit joins fully built down their own locked spec, "
          "the point accounting closes, a free reset gives all of it back, and Asher Coleman is "
          "byte-identical through both a fresh build and a re-hire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
