#!/usr/bin/env python3
"""Every talent-gated ability must have a talent that unlocks it.

    PYTHONPATH=. python3 tools/qa_abilities_obtainable.py

WHY THIS EXISTS. An ability carrying "requires_talent": true is deliberately
NOT learned from level_req alone - combat/abilities.py marks it "do not
auto-learn", and Character._sync_talent_unlocked_abilities() only puts it in
the book if some spent talent declares {"unlock_ability": "<its id>"}. So a
gated ability with no unlocking talent anywhere is not merely hard to get:
it is unobtainable at every level, by every build, forever, and nothing
complains.

That is exactly what happened on 5 Nov 2026. Rebuilding Tinker's Mechanics
and Demolition trees from the CoA reference replaced their nodes wholesale
and silently dropped eight unlock_ability nodes with them, stranding
Mechsuit Form, Mechsuit Laser Beam, Mechsuit Combustion, Makeshift Dynamite,
Bomb Toss, Spider Bomb, Hyperblast Barrage and Rocket Launcher - the whole
mechsuit kit among them. Both commits passed audit_talents and
qa_ability_text, because neither of those asks the obtainability question;
the trees were internally consistent and the abilities were fine. The link
BETWEEN them was what broke, which is the one thing nothing was checking.

Same failure shape as the bags that no vendor sold. The rule is one rule, so
it gets one check, and it runs over every class rather than the one that
happened to break.
"""
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _rows(doc, key):
    block = doc.get(key, doc)
    if isinstance(block, dict):
        return [v for v in block.values() if isinstance(v, dict)]
    return [v for v in block if isinstance(v, dict)] if isinstance(block, list) else []


def main():
    # Every ability that refuses to be learned from level alone.
    gated = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data/abilities/*.json"))):
        doc = json.load(open(path))
        for ability in _rows(doc, "abilities"):
            aid = ability.get("ability_id")
            if aid and ability.get("requires_talent"):
                gated[aid] = os.path.basename(path)

    # Every ability some talent hands out, anywhere in the game.
    unlocked = defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "data/talents/*.json"))):
        doc = json.load(open(path))
        for node in doc.get("nodes", []):
            value = (node.get("effects") or {}).get("unlock_ability")
            for aid in ([value] if isinstance(value, str) else (value or [])):
                unlocked[aid].append(
                    f"{os.path.basename(path)}:{node.get('talent_id')}")

    orphans = sorted(a for a in gated if a not in unlocked)
    # An unlock pointing at an ability that does not exist is the mirror
    # failure: the node looks like it teaches something and teaches nothing.
    known = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "data/abilities/*.json"))):
        for ability in _rows(json.load(open(path)), "abilities"):
            if ability.get("ability_id"):
                known.add(ability["ability_id"])
    dangling = sorted(a for a in unlocked if a not in known)

    print(f"  {len(gated):5d} talent-gated abilities")
    print(f"  {len(unlocked):5d} abilities unlocked by some talent")
    print(f"  {len(orphans):5d} UNOBTAINABLE (gated, no talent unlocks them)")
    for aid in orphans:
        print(f"      [{gated[aid]}] {aid}")
    print(f"  {len(dangling):5d} unlock nodes naming an ability that does not exist")
    for aid in dangling:
        print(f"      {aid} <- {', '.join(unlocked[aid])}")

    ok = not orphans and not dangling
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
