#!/usr/bin/env python3
"""Give every class buff and debuff that carries flat stats a rank about every ten levels, up to the late 50s.

    PYTHONPATH=. python3 tools/regrade_buff_ranks.py --check
    PYTHONPATH=. python3 tools/regrade_buff_ranks.py

Kyle, 16 Nov 2026: "support skills and them not actually benefiting from ranking up and being obsolete" and "Make
sure support skills and buffs are actually properly done with proper skill levels too". Measured: of the 228 class
buffs and debuffs that carry flat stats (stamina, attack power, armour...), 165 had ONE rank, so whatever they gave at
the level you learned them they gave at 60; the rest mostly had four, the last at 47-56.

combat/support_formula.py now sizes those stats from the level a rank is learned at, so a rank is worth training
again. This gives each of them the ranks to train:

  - The first rank stays exactly as authored: its level, cost and value.
  - Then a rank every STEP levels after it, while that's at or under TOP. The last rank is pulled to TOP if it would
    land more than 4 levels short of it, so nothing tops out in the early 50s.
  - A buff already ranked at least that densely is left alone (Sunder Armor's eight ranks).
  - effect_value (which still scales any percentage stats it carries, 33% -> 100%) runs from the first rank's value
    to 100 at the last. The mana cost stays the first rank's: the class mana table already grows costs by level
    (combat/ability_scaling.mana_cost_multiplier).

Only class files (data/abilities/<class>.json). Idempotent: a second run changes nothing.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

STEP = 10
TOP = 58
SKIP_FILES = {"_universal.json", "asher_unique.json"}
NOTE = ("16 Nov 2026, support pass: a rank every {step} levels to {top} (tools/regrade_buff_ranks.py); its flat stats "
        "are sized from each rank's level (combat/support_formula.py)")


def ladder(first):
    lv = [first]
    while lv[-1] + STEP <= TOP:
        lv.append(lv[-1] + STEP)
    if TOP - lv[-1] > 4 and lv[-1] < TOP:
        lv.append(TOP)
    return lv


def regrade(a):
    from combat import support_formula as SF
    if a.get("effect_type") not in ("buff", "debuff") or not SF.scaled_keys(a.get("stat_mods")):
        return None
    ranks = sorted(a.get("ranks") or [], key=lambda r: r.get("level_req", 1))
    if not ranks:
        return None
    want = ladder(ranks[0].get("level_req", 1) or 1)
    if len(ranks) >= len(want):
        return None
    first = ranks[0]
    v0 = first.get("effect_value", 100) or 100
    out = []
    for i, lv in enumerate(want):
        r = dict(first) if i == 0 else {k: v for k, v in first.items() if k not in ("rank", "level_req", "effect_value")}
        r["rank"] = i + 1
        r["level_req"] = lv
        t = i / max(1, len(want) - 1)
        r["effect_value"] = v0 if i == 0 else int(round(v0 + (100 - v0) * t))
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    changed, files = 0, 0
    for fn in sorted((ROOT / "data/abilities").glob("*.json")):
        if fn.name in SKIP_FILES:
            continue
        raw = fn.read_text(encoding="utf-8")
        d = json.loads(raw)
        rows = d.get("abilities", d) if isinstance(d, dict) else d
        if isinstance(rows, dict):
            rows = list(rows.values())
        n = 0
        for a in rows:
            if not isinstance(a, dict):
                continue
            new = regrade(a)
            if new is None:
                continue
            n += 1
            if args.check:
                print(f"  {a['ability_id']:44s} {len(a.get('ranks') or [])} rank(s) -> {len(new)} "
                      f"({', '.join(str(r['level_req']) for r in new)})")
                continue
            a["ranks"] = new
            note = NOTE.format(step=STEP, top=TOP)
            t = a.setdefault("_tuning", [])
            if note not in t:
                t.append(note)
        if n and not args.check:
            fn.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            files += 1
        changed += n
    print(f"{changed} buffs and debuffs {'would be' if args.check else 'were'} re-ranked"
          + ("" if args.check else f" across {files} files"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
