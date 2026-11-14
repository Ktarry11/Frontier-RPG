#!/usr/bin/env python3
"""Every profession in the game must be learnable from somebody.

Written because I broke exactly this and nothing noticed.

Removing Essence Harvesting, I pruned data/training/trainers.json with a
SUBSTRING match on the key - `if 'essence' in key: delete` - and the fourteen
trainers who taught it were all keyed pt_<town>_essence. Every one of them also
taught ENGINEERING. So all 14 Engineering trainers were deleted at once and
Engineering became unlearnable across the entire game, with no error anywhere:
the data still had the recipes, the materials, the ladder, the ambient NPCs
still standing in fourteen towns saying they were Tinkers. Only the trainer
lookup was empty, and nothing asked it a question it could fail.

It surfaced by accident, while looking at an unrelated vendor list and noticing
two Tinkers had stopped reporting a service.

MEASURE THE BLAST RADIUS BEFORE DELETING. A substring is not an identifier. The
check below is the cheap version of that lesson.
"""
import sys, os, json, pathlib, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    profs = json.load(open(ROOT / "data/professions/professions.json", encoding="utf-8"))["professions"]
    trainers = json.load(open(ROOT / "data/training/trainers.json", encoding="utf-8"))["profession_trainers"]

    taught = collections.Counter()
    for npc_id, teaches in trainers.items():
        for p in (teaches or []):
            taught[p] += 1

    print(f"  {len(profs)} professions, {len(trainers)} profession trainers\n")
    ok = True
    for name in sorted(profs):
        n = taught.get(name, 0)
        flag = "" if n else "   <-- UNLEARNABLE: no trainer teaches this"
        if not n:
            ok = False
        print(f"    {name:24s} {n:3d} trainer(s){flag}")

    # The reverse: a trainer teaching something that is not a profession any
    # more. Harmless at runtime, but it is the fingerprint of a half-finished
    # deletion, which is what started all this.
    orphan = sorted(p for p in taught if p not in profs)
    if orphan:
        ok = False
        print(f"\n  BROKEN - trainers teach {len(orphan)} thing(s) that are not professions:")
        for p in orphan:
            print(f"    {p} (taught by {taught[p]})")

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
