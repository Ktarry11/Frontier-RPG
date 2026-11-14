#!/usr/bin/env python3
"""Move recipes off the trainer and into the world, without walling anyone in.

    PYTHONPATH=. python3 tools/rebalance_recipe_sources.py [--apply] [profession ...]

Idempotent and deterministic - the same recipe always lands on the same source,
so re-running after a recipe pass does not reshuffle what a player already found.

=============================================================================
WHY
=============================================================================

Kyle, 7 Nov 2026: "I want only about 40-60% of the crafting stuff taught at a
vendor. The other recipes will be found through quests, Dungeons, rares, or
hidden vendors or just regular vendors."

The game was at 76% trainer-taught, and blacksmithing had just been pushed to
82% by tools/build_blacksmithing_300.py, which stamped source="trainer" on all
105 recipes it generated. A profession you can fill entirely by walking up to
one NPC has no reason to send you anywhere.

The four sources the code already supports (world/recipe_manager.py) cover
everything Kyle listed, so this needs no new machinery:

    trainer   taught on sight at a trainer
    drop      found on a corpse - dungeons and rares included. The pool is
              derived by level in entities/recipe_drops.py, so a recipe starts
              dropping the moment it is labelled, with no per-creature table.
    vendor    bought from someone who stocks patterns - hidden or otherwise
    quest     a quest reward

=============================================================================
THE CONSTRAINT THAT MATTERS MORE THAN THE PERCENTAGE
=============================================================================

A profession is levelled by crafting, so the TRAINER-TAUGHT recipes must still
form a continuous ladder. Strip the only recipes around skill 200 and a player
arriving at 200 cannot advance at all except by luck, and no percentage target
is worth that.

So this walks each profession's recipes in skill order and keeps a trainer
recipe at least every MAX_TRAINER_GAP skill BEFORE it considers the ratio. The
ratio is satisfied out of what is left over. If the two ever conflict, the
ladder wins and the tool says so rather than quietly producing an unlevellable
profession.

WHAT GOES WHERE. Prestige tracks rarity, because finding the recipe should feel
like the item does: epics lean to quest and drop, rares to drop and vendor,
uncommons to vendor. Recipes already labelled non-trainer are left exactly as
they are - this only ever moves things OFF the trainer.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCES = {
    "blacksmithing": ("data/blacksmithing/recipes.json", None),
    "leatherworking": ("data/leatherworking/recipes.json", None),
    "alchemy": ("data/crafting/recipes.json", "alchemy"),
    "tailoring": ("data/crafting/recipes.json", "tailoring"),
    "woodworking": ("data/crafting/recipes.json", "woodworking"),
    "engineering": ("data/crafting/recipes.json", "engineering"),
    "cooking": ("data/crafting/recipes.json", "cooking"),
    "woodcutting": ("data/crafting/recipes.json", "woodcutting"),
}

#: Kyle's band. The tool aims at the middle rather than an edge.
# Kyle, 12 Nov 2026, tightening it: "for recipies...i still want only 50-55% from trainer and
# 50-55% from world...hidden vendors, quests, bosses, random world drops etc." - "for ALL crafting".
TRAINER_MIN, TRAINER_TARGET, TRAINER_MAX = 0.50, 0.52, 0.55

#: Never leave the trainer: the things a cook makes in order to cook. A dropped recipe for
#: Bread would lock every dish that needs a slice.
PINNED = {"cookx_bread", "cookx_stock"}

#: Largest gap, in skill, allowed between consecutive TRAINER-taught recipes.
#: Any larger and a player who reaches that skill has nothing to train.
MAX_TRAINER_GAP = 15

#: Highest skill any trainer tier reaches (data/professions/professions.json).
#: Recipes above this are forward-authored and are left on the trainer.
SKILL_CEILING = 300

#: Where a recipe goes once it leaves the trainer, weighted by its rarity.
#: An epic recipe found on a vendor shelf is an anticlimax.
BY_RARITY = {
    "epic":     [("quest", 2), ("drop", 3)],
    "rare":     [("drop", 3), ("vendor", 2), ("quest", 1)],
    "uncommon": [("vendor", 3), ("drop", 2)],
    None:       [("vendor", 2), ("drop", 2), ("quest", 1)],
}


def deal(rid, weights):
    """Deterministic weighted pick, stable across runs and machines.

    hashlib, not hash() - the builtin is salted per process, so the same recipe
    would change source every time the tool ran and a player's world would
    reshuffle under them. This codebase has made that exact mistake before, in
    the background-image picker.
    """
    total = sum(w for _, w in weights)
    n = int(hashlib.md5(rid.encode()).hexdigest()[:8], 16) % total
    for name, w in weights:
        if n < w:
            return name
        n -= w
    return weights[-1][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("professions", nargs="*")
    args = ap.parse_args()

    want = set(args.professions) or set(SOURCES)
    docs, plan, warnings = {}, [], []

    for prof in sorted(want & set(SOURCES)):
        rel, key = SOURCES[prof]
        if rel not in docs:
            docs[rel] = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        recipes = (docs[rel]["professions"][key]["recipes"] if key
                   else docs[rel]["recipes"])
        items = [(rid, r) for rid, r in recipes.items() if isinstance(r, dict)]
        if not items:
            continue
        total = len(items)
        # NEVER move a recipe above the reachable ceiling. Those are
        # forward-authored for the endgame expansion, and no player can reach
        # their skill - but `trainer` still routes (the trainer simply never
        # offers it), while `drop` does NOT: entities/recipe_drops.py derives
        # its pool from creature level, which tops out around skill 300, so a
        # skill-374 plank labelled `drop` can never be found by anyone.
        # Moving them is how this pass stranded eleven woodcutting recipes.
        trainers = [(rid, r) for rid, r in items
                    if r.get("source", "trainer") == "trainer"
                    and r.get("skill_required", 0) <= SKILL_CEILING]
        trainers.sort(key=lambda t: t[1].get("skill_required", 0))

        # Pass 1 - keep the ladder, with the fewest recipes that still cover it.
        #
        # From the last kept rung, take the FARTHEST recipe still within
        # MAX_TRAINER_GAP of it, and repeat. An earlier version kept the first
        # recipe BEYOND the gap instead, which manufactured a gap of exactly
        # MAX_TRAINER_GAP at every step - the opposite of the job.
        keep = set()
        if trainers:
            i = 0
            keep.add(trainers[0][0])
            last = trainers[0][1].get("skill_required", 0)
            while True:
                reach = [j for j in range(i + 1, len(trainers))
                         if trainers[j][1].get("skill_required", 0) - last <= MAX_TRAINER_GAP]
                if not reach:
                    # nothing within reach: the next recipe is beyond the gap on
                    # its own, so the hole is in the content, not our doing.
                    # Keep that next one and carry on from there.
                    if i + 1 >= len(trainers):
                        break
                    i += 1
                else:
                    i = max(reach)
                keep.add(trainers[i][0])
                last = trainers[i][1].get("skill_required", 0)
        # the very top of the ladder always stays teachable
        if trainers:
            keep.add(trainers[-1][0])
        keep.update(rid for rid, _ in trainers if rid in PINNED)

        # Pass 2 - satisfy the ratio out of whatever is left.
        target_n = int(round(total * TRAINER_TARGET))
        spare = [rid for rid, _ in trainers if rid not in keep]
        for rid in spare:
            if len(keep) >= target_n:
                break
            keep.add(rid)

        moved = [(rid, r) for rid, r in trainers if rid not in keep]
        final_trainer = len(trainers) - len(moved) + (total - len(trainers)) * 0
        ratio = (len(trainers) - len(moved)) / total

        if ratio > TRAINER_MAX:
            warnings.append(
                f"{prof}: ladder needs {len(keep)} trainer recipes = {ratio:.0%}, "
                f"above the {TRAINER_MAX:.0%} ceiling. Ladder wins; add more "
                f"recipes in the sparse bands to bring it down.")
        if ratio < TRAINER_MIN:
            warnings.append(f"{prof}: {ratio:.0%} trainer is below the {TRAINER_MIN:.0%} floor.")

        for rid, r in moved:
            rarity = (r.get("output") or {}).get("rarity")
            dest = deal(rid, BY_RARITY.get(rarity, BY_RARITY[None]))
            plan.append((prof, rid, r.get("name", rid), r.get("skill_required", 0),
                         rarity, dest))
            if args.apply:
                r["source"] = dest
                if dest == "vendor":
                    r.setdefault("vendor_location", "Any pattern vendor")

    print(f"  target {TRAINER_MIN:.0%}-{TRAINER_MAX:.0%} trainer-taught, "
          f"aiming {TRAINER_TARGET:.0%}")
    print(f"  trainer ladder may not gap more than {MAX_TRAINER_GAP} skill\n")
    print(f"  {'profession':16}{'total':>6}{'trainer before':>16}{'after':>10}   moved to")
    for prof in sorted(want & set(SOURCES)):
        rel, key = SOURCES[prof]
        if rel not in docs:
            continue
        recipes = (docs[rel]["professions"][key]["recipes"] if key
                   else docs[rel]["recipes"])
        items = [r for r in recipes.values() if isinstance(r, dict)]
        if not items:
            continue
        total = len(items)
        mine = [p for p in plan if p[0] == prof]
        before = sum(1 for r in items if r.get("source", "trainer") == "trainer")
        before += 0 if args.apply else 0
        after = before - len(mine) if not args.apply else before
        dests = collections.Counter(p[5] for p in mine)
        print(f"  {prof:16}{total:>6}{f'{before - (0 if args.apply else 0)}':>16}"
              f"{f'{after} ({after/total:.0%})':>10}   "
              f"{', '.join(f'{k} {v}' for k, v in sorted(dests.items())) or '-'}")

    if warnings:
        print()
        for w in warnings:
            print(f"  WARNING  {w}")

    # the check that matters: can every profession still be levelled?
    print()
    ok = True
    for prof in sorted(want & set(SOURCES)):
        rel, key = SOURCES[prof]
        if rel not in docs:
            continue
        recipes = (docs[rel]["professions"][key]["recipes"] if key
                   else docs[rel]["recipes"])
        moved_ids = {p[1] for p in plan if p[0] == prof}
        # Compare against the gaps the profession ALREADY has across ALL its
        # recipes, whatever their source. Alchemy has no recipe of any kind
        # between skill 135 and 215, so a trainer gap there is inherent to the
        # content and nothing this tool does can close it. Only a gap this
        # rebalance CREATES is a failure - that is the difference between "the
        # ladder is thin here" and "I just broke the ladder".
        # Baseline is the recipes that were ALREADY trainer-taught, not every
        # recipe. This tool can only keep something on the trainer that was on
        # the trainer to begin with, so a band whose only recipes were already
        # drops or vendor patterns was never ours to cover, and flagging it
        # blames this pass for a hole it did not dig.
        allset = sorted({r.get("skill_required", 0) for rid, r in recipes.items()
                         if isinstance(r, dict)
                         and r.get("source", "trainer") == "trainer"})
        sk = sorted(r.get("skill_required", 0) for rid, r in recipes.items()
                    if isinstance(r, dict)
                    and r.get("source", "trainer") == "trainer"
                    and rid not in moved_ids)
        if not sk:
            print(f"  {prof}: NO trainer recipes left at all")
            ok = False
            continue
        # A trainer gap is INHERENT when no recipe of ANY source sits inside it -
        # there was nothing there to keep. It is a gap this tool CREATED when a
        # recipe does sit inside it and we moved it off the trainer. Comparing
        # gap tuples between the two ladders does not work: their endpoints
        # differ, so an identical hole reads as different gaps.
        gaps = [(a, b) for a, b in zip(sk, sk[1:])
                if b - a > MAX_TRAINER_GAP
                and any(a < x < b for x in allset)]
        inherent = [(a, b) for a, b in zip(sk, sk[1:])
                    if b - a > MAX_TRAINER_GAP and not any(a < x < b for x in allset)]
        if gaps:
            ok = False
            print(f"  {prof}: NEW trainer gaps over {MAX_TRAINER_GAP}: "
                  + ", ".join(f"{a}->{b}" for a, b in gaps[:6]))
        else:
            extra = f", {len(inherent)} pre-existing content gap(s)" if inherent else ""
            print(f"  {prof}: no new trainer gaps, {sk[0]}-{sk[-1]}, "
                  f"{len(sk)} recipes{extra}")

    if not ok:
        print("\n  REFUSING TO WRITE - a profession would have a skill band it "
              "cannot train past.")
        return 1

    if args.apply:
        for rel, doc in docs.items():
            (ROOT / rel).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"\n  moved {len(plan)} recipes; wrote {', '.join(sorted(docs))}")
    else:
        print(f"\n  {len(plan)} recipes would move. Dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
