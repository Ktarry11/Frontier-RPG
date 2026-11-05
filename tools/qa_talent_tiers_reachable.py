#!/usr/bin/env python3
"""Every talent tier must be reachable by spending points in its own tree.

    PYTHONPATH=. python3 tools/qa_talent_tiers_reachable.py

WHY THIS EXISTS. A tree's tier_requirements say how many points must be
spent IN THAT TREE before a tier unlocks ("6": 30). The tree also contains
only so many points - the sum of every node's max_points. If the points
available BELOW a tier are fewer than that tier's requirement, the tier can
never open, at any level, by any build. The capstone just sits there.

Found 5 Nov 2026, and not by looking: rebuilding Tinker's Demolition tree
left it with 27 total points and 24 below tier 5, against gates of 25 and
30. Both top tiers were dead. Mechanics lost its capstone the same way. The
symptom surfaced two steps away, in qa_recruit_talents - "Marta Kowalski at
level 31 joins with 3 unspent talent point(s)" - because the recruit
auto-spender had nowhere left to put them. Nothing said the tiers were
unreachable; one unrelated-looking recruit was just short.

That is the shape worth guarding: the tree was internally consistent, every
node was fine, and the arithmetic BETWEEN the node list and the tier gates
was what broke. Checked here directly, over every tree, so it reads as what
it is instead of arriving as a recruit's accounting error.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    problems = []
    checked = 0
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        doc = json.loads(path.read_text())
        nodes = doc.get("nodes") or []
        gates = doc.get("tier_requirements") or {}
        if not nodes or not gates:
            continue
        checked += 1

        per_tier = {}
        for node in nodes:
            per_tier[int(node.get("tier", 0))] = (
                per_tier.get(int(node.get("tier", 0)), 0)
                + int(node.get("max_points", 1)))
        total = sum(per_tier.values())

        for raw_tier, required in sorted(gates.items(), key=lambda kv: int(kv[0])):
            tier = int(raw_tier)
            required = int(required)
            if required <= 0:
                continue
            # Points that can be spent strictly BELOW this tier - the only
            # ones that can pay for its gate.
            below = sum(v for t, v in per_tier.items() if t < tier)
            if below < required:
                problems.append(
                    f"[{path.name}] tier {tier} needs {required} points spent "
                    f"but only {below} exist below it "
                    f"({total} in the whole tree) - UNREACHABLE")

    print(f"  {checked:5d} talent trees checked")
    print(f"  {len(problems):5d} unreachable tiers")
    for p in problems:
        print(f"      {p}")
    ok = not problems
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
