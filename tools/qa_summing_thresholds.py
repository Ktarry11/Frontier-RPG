#!/usr/bin/env python3
"""At most one node per CLASS may set a summing threshold key.

    PYTHONPATH=. python3 tools/qa_summing_thresholds.py

WHAT THIS CATCHES, and why it has to be per class rather than per tree.

UNSCALED_EFFECT_KEYS (entities/talent_node.py:16) are the keys
get_effective_effects() passes through at their RAW value instead of
multiplying by points spent, because they are THRESHOLDS, not quantities -
"below 35% health" is a boundary, and a rank curve on a boundary is
meaningless. low_health_threshold_pct is the only one today.

But get_talent_effect still SUMS a key across every node that carries it.
So two nodes each setting 0.35 do not give 35%. They give 70%, which on an
execute conditional is most of a fight. Tinker once shipped two summing to
0.8 - "below 80% health" - and nothing flagged it.

A CHARACTER CAN SPEND POINTS IN MORE THAN ONE TREE OF THEIR CLASS, so
checking a single tree is not enough. Reaper Harvest's Executioner sets
0.35 and Reaper Soul's The Jailer's Call wants CoA's 20%; authored
literally, a Reaper who spends in both trees would get a 55% window, and
each tree would look perfectly correct on its own. That is exactly the
"one rule, N implementations" shape this project keeps hitting, except the
N implementations are in different files that never see each other.

The rule: ONE node per class sets the threshold, every other node that
needs it inherits that value, and the engine default (0.35) applies when
no node sets it at all.

VERIFIED AGAINST A PLANTED BREACH before being trusted: adding
low_health_threshold_pct to a second Reaper node makes this report Reaper
at 0.55 across two trees; removing it returns to PASS. The negative
control is that it passes on the real data rather than flagging
everything, while the ten legitimate single setters across ten classes are
left alone.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.talent_node import UNSCALED_EFFECT_KEYS  # noqa: E402

#: Ability-file stems, longest first, so a class name containing an
#: underscore (witch_doctor, knight_of_xoroth) is matched before the split.
#: Same approach as tools/qa_pet_keys.py, for the same reason.
def class_stems():
    return sorted((p.stem for p in (ROOT / "data/abilities").glob("*.json")),
                  key=len, reverse=True)


def tree_class(tree_id, stems):
    for stem in stems:
        if tree_id == stem or tree_id.startswith(stem + "_"):
            return stem
    return tree_id.split("_")[0]


def main():
    stems = class_stems()
    # class -> key -> [(tree_id, talent_id, value)]
    found = defaultdict(lambda: defaultdict(list))
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        tree = json.loads(path.read_text())
        tid = tree.get("tree_id", path.stem)
        cls = tree_class(tid, stems)
        for n in tree["nodes"]:
            for key, value in (n.get("effects") or {}).items():
                if key in UNSCALED_EFFECT_KEYS:
                    found[cls][key].append((tid, n["talent_id"], value))

    problems = []
    for cls in sorted(found):
        for key in sorted(found[cls]):
            rows = found[cls][key]
            if len(rows) > 1:
                total = sum(r[2] for r in rows)
                problems.append((cls, key, rows, total))

    singles = sum(1 for c in found for k in found[c] if len(found[c][k]) == 1)
    print(f"  checked {len(list((ROOT / 'data/talents').glob('*.json')))} trees "
          f"for {len(UNSCALED_EFFECT_KEYS)} summing threshold key(s)")
    print(f"  {singles} class(es) set one legitimately")

    if not problems:
        print("  0 CLASSES WITH TWO SETTERS\n\nPASS")
        return 0

    print(f"\n  {len(problems)} CLASS(ES) SUM A THRESHOLD ACROSS NODES")
    print("  These keys are UNSCALED (rank does not divide them) but "
          "get_talent_effect\n  still ADDS them, and a character can spend "
          "in several trees of their class.\n")
    for cls, key, rows, total in problems:
        print(f"    {cls}: {key} sums to {total}")
        for tid, talent, value in rows:
            print(f"        {value:<8} {talent}   (in {tid})")
    print("\n  Fix: keep ONE setter per class and let the other nodes "
          "inherit it.\n  The engine default is 0.35 when no node sets it.")
    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
