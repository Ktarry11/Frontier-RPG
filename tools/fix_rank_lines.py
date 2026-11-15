#!/usr/bin/env python3
"""Put every ranked ability's rank-to-rank growth on the authored line, so the world curve gives it the same
front-loaded shape as every other ability.

    PYTHONPATH=. python3 tools/fix_rank_lines.py            # show
    PYTHONPATH=. python3 tools/fix_rank_lines.py --apply

Kyle, 15 Nov 2026: "We are ensuring that even coa classes have the proper ranks leveling up and follows the front
loaded increases in damage and healing and lower % increases at end level?"

The world curve multiplies each rank by rank_multiplier(level learned) = growth / the authored line (1 + 3.636% of
rank 1 a level). That assumes the AUTHORED ranks sit on that line, as the Classic ones do (Fireball 44 -> 132 over
1-56). ~130 abilities, nearly all CoA, were authored far steeper (Runeblade 24 at 1, 8x that by 56) or with bumps
(a +85% rank at 40 between +62% and +47%), and the curve then multiplied the steepness again: rank 1 at half a
normal spell and the top rank at 2-4x one. Each such ability is re-authored as ANCHOR x the line, where ANCHOR is
the geometric mean of its ranks' ratios to the line (so its overall size is kept and the spec auras handle the
rest). Its rank levels and count are not touched.

Judged: the ratio of its last rank to its first over the line's own ratio. Outside LOW..HIGH, or a single rank
more than JUMP off its neighbours' line, and it is put on the line.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
LOW, HIGH, JUMP = 0.80, 1.25, 1.35
SLOPE = 0.03636
CURVED = {"damage", "spell_damage", "ranged_damage", "dot", "spell_dot", "heal", "hot", "damage_and_heal",
          "damage_and_restore_mana"}
EXEMPT = {"hunter_revive_pet"}


def line(lv):
    return 1 + SLOPE * (max(1, lv) - 1)


def judge(ranks):
    rs = [r for r in ranks if r.get("effect_value")]
    if len(rs) < 2:
        return None
    a = [r["effect_value"] / line(r["level_req"]) for r in rs]
    spread = a[-1] / a[0]
    jump = max(max(a[i] / a[i - 1], a[i - 1] / a[i]) for i in range(1, len(a)))
    if LOW <= spread <= HIGH and jump <= JUMP:
        return None
    return math.exp(sum(math.log(x) for x in a) / len(a)), spread, jump


def main():
    apply = "--apply" in sys.argv
    n = 0
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        if f.name in ("_universal.json", "asher_unique.json"):
            continue
        doc = json.loads(f.read_text(encoding="utf-8"))
        L = doc if isinstance(doc, list) else doc.get("abilities", doc)
        changed = False
        for e in (L.values() if isinstance(L, dict) else L):
            if not isinstance(e, dict) or e.get("effect_type") not in CURVED or not e.get("ranks"):
                continue
            if e["ability_id"] in EXEMPT or e["ability_id"].endswith("_attack"):
                continue
            j = judge(e["ranks"])
            if not j:
                continue
            anchor, spread, jump = j
            before = [(r["level_req"], r.get("effect_value")) for r in e["ranks"] if r.get("effect_value")]
            for r in e["ranks"]:
                if r.get("effect_value"):
                    r["effect_value"] = max(1, round(anchor * line(r["level_req"])))
            after = [(r["level_req"], r.get("effect_value")) for r in e["ranks"] if r.get("effect_value")]
            e.setdefault("_tuning", []).append(
                f"15 Nov 2026, class pass: ranks put on the authored line (they ran {spread:.2f}x steeper than it, "
                f"biggest single-rank jump {jump:.2f}x); overall size kept. tools/fix_rank_lines.py")
            print(f"  {e['ability_id']:42} spread {spread:4.2f} jump {jump:4.2f}  {before[0]}..{before[-1]} -> "
                  f"{after[0]}..{after[-1]}")
            n += 1
            changed = True
        if apply and changed:
            f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} abilities {'put on the line' if apply else 'would be put on the line'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
