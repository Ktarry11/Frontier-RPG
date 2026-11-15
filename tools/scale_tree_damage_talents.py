#!/usr/bin/env python3
"""Scale one talent tree's damage-percentage talents by a factor, numbers in the text included.

    PYTHONPATH=. python3 tools/scale_tree_damage_talents.py necromancer_rime 0.5            # dry run
    PYTHONPATH=. python3 tools/scale_tree_damage_talents.py necromancer_rime 0.5 --write

For a tree whose own talents stack far past every other spec's (15 Nov 2026, the damage parity sim: Necromancer Rime
dealt 3.8x the median damage spec at 60 - +33% Frost, +24% Lichfrost, +40% Frost crit damage and more, on top of
the shared caster crit capstone). Scales every DAMAGE key in each talent's effects (…_damage, …_spell_damage,
dot_damage, all_damage, aoe_damage, <school>_crit_damage_pct, ability_<id>_crit_damage), leaving alone:
  crit_damage_spell / crit_damage_physical - Kyle's caster crit capstone (6 Nov: "all caster classes should have a
                                             5 point talent that increases their spell crit damage by 100%")
  anything that is not damage (crit chance, haste, cooldowns, costs, healing...)
Each changed number in the talent's description is rewritten to match (it states the full-rank total, so a 0.03
x 3 ranks talent says "9%"), and the description is left untouched if a number can't be matched. Each rank
stays a whole percent (the total is a multiple of the rank count). pet_damage is left alone.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP = {"crit_damage_spell", "crit_damage_physical", "pet_damage"}


def is_damage_key(k):
    if k in KEEP:
        return False
    return (k.endswith("_damage") or k.endswith("_spell_damage") or k in ("dot_damage", "all_damage", "aoe_damage")
            or k.endswith("_crit_damage_pct") or k.endswith("_crit_damage"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree")
    ap.add_argument("factor", type=float)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    path = ROOT / f"data/talents/{args.tree}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes") or data.get("talents") or data
    changed = 0
    for n in (nodes if isinstance(nodes, list) else nodes.values()):
        eff = n.get("effects") or {}
        pts = n.get("max_points") or 1
        desc = n.get("description") or ""
        new_desc = desc
        hit = False
        for k, v in list(eff.items()):
            if not isinstance(v, (int, float)) or not is_damage_key(k):
                continue
            old_total = round(v * pts * 100)
            # clean numbers: the full-rank total is a whole multiple of the rank count, so each rank is a whole
            # percent (Kyle: "3.33% per skill" is "dumb")
            new_total = pts * max(1, round(old_total * args.factor / pts))
            new_v = round(new_total / 100 / pts, 4)
            eff[k] = new_v
            hit = True
            # the description states the full-rank total; rewrite the first matching "N%"
            pat = rf"(?<![\d.]){old_total}%"
            if re.search(pat, new_desc):
                new_desc = re.sub(pat, f"{new_total}%", new_desc, count=1)
        if hit:
            changed += 1
            print(f"  {n['talent_id']}: {desc[:90]}\n      -> {new_desc[:90]}  {eff}")
            n["description"] = new_desc
            n.setdefault("_tuning", []).append(f"15 Nov 2026: damage talents x{args.factor} (tree far above the "
                                               f"other specs in tools/sim_dps_parity.py)")
    print(f"{changed} talents {'changed' if args.write else 'would change'}")
    if args.write:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
