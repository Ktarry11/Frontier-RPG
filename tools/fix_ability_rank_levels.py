#!/usr/bin/env python3
"""Fill the holes in every class's ability ranks.

    PYTHONPATH=. python3 tools/fix_ability_rank_levels.py          # dry run: prints every change
    PYTHONPATH=. python3 tools/fix_ability_rank_levels.py --write

Kyle, 15 Nov 2026: "You'll be spending almost all day fixing classes. All 9 classic classes and coa classes.
All specs, ability ranks....." tools/audit_ability_ranks.py found, across 573 abilities that scale:

  * 8 ranks above the level cap (60): Hammer of Wrath's third rank at 72, Fan of Knives at 62. Nobody can
    learn them, so the ability's last real rank comes early.
  * 35 gaps of 16 levels between two ranks (Execute 24 -> 40, Pyroblast 36 -> 52): a spell that doesn't
    grow for 16 levels while everything around it does.
  * abilities whose last rank comes early: Arm of Thorim learned at 11 with its last rank at 16, Sunslam
    one rank at 26, Thunder Clap's last at 42.

Rules (only abilities whose effect_value is a strength - damage, heals, DoTs, HoTs - are extended or filled):

  CLAMP    a rank above 60 moves to 60 (keeping its numbers); if that lands on the rank before it, the two
           merge into the stronger one.
  EXTEND   learned by 40 with a last rank before 48: add ranks every 12 levels up to 56 at most, each
           growing with level the way the ability already does (effect and cost x (level+10)/(prev+10)).
  FILL     a gap over 14 levels gets a rank midway, its numbers halfway between.

Every changed ability's OLD rank levels are written to data/abilities/rank_levels_before.json (first time
only), which Character._restore_trained_ranks uses to read an older save's trained rank NUMBERS correctly.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

CAP = 60
MAX_GAP = 14
EXTEND_UNTIL = 48
EXTEND_STEP = 12
EXTEND_TOP = 56
CURVED = {"damage", "spell_damage", "ranged_damage", "dot", "spell_dot", "heal", "hot", "damage_and_heal",
          "damage_and_restore_mana"}
NUMERIC = ("effect_value", "cost", "heal_value", "absorb", "mana_restore_pct", "on_damage_hot_potency")
BEFORE = "data/abilities/rank_levels_before.json"
#: Shoot and Wand take their damage from the weapon; Asher's kit is fixed by design
SKIP_FILES = {"_universal.json", "asher_unique.json"}


def between(lo, hi, level):
    """A rank at `level` with every number on the line from rank lo to rank hi."""
    t = (level - lo["level_req"]) / max(1, hi["level_req"] - lo["level_req"])
    r = dict(lo)
    for k in NUMERIC:
        if isinstance(lo.get(k), (int, float)) and isinstance(hi.get(k), (int, float)):
            v = lo[k] + (hi[k] - lo[k]) * t
            r[k] = round(v, 3) if isinstance(lo[k], float) and not float(lo[k]).is_integer() else int(round(v))
    r["level_req"] = level
    return r


def beyond(last, level):
    """A rank past the last one, grown with level."""
    g = (level + 10) / (last["level_req"] + 10)
    r = dict(last)
    for k in ("effect_value", "cost", "heal_value", "absorb"):
        if isinstance(last.get(k), (int, float)) and last.get(k):
            r[k] = int(round(last[k] * g))
    r["level_req"] = level
    return r


def fix(a):
    ranks = [dict(r) for r in a["ranks"]]
    notes = []
    # CLAMP
    if any(r["level_req"] > CAP for r in ranks):
        notes.append(f"clamp {[r['level_req'] for r in ranks]}")
        for r in ranks:
            r["level_req"] = min(CAP, r["level_req"])
        merged = []
        for r in ranks:
            if merged and merged[-1]["level_req"] == r["level_req"]:
                merged[-1] = r            # the later, stronger rank wins
            else:
                merged.append(r)
        ranks = merged
    if a.get("effect_type") in CURVED:
        # EXTEND
        if ranks[0]["level_req"] <= 40 and ranks[-1]["level_req"] < EXTEND_UNTIL:
            before = [r["level_req"] for r in ranks]
            while ranks[-1]["level_req"] + EXTEND_STEP <= EXTEND_TOP:
                ranks.append(beyond(ranks[-1], ranks[-1]["level_req"] + EXTEND_STEP))
            if ranks[-1]["level_req"] < EXTEND_UNTIL:
                ranks.append(beyond(ranks[-1], min(EXTEND_TOP, ranks[-1]["level_req"] + EXTEND_STEP)))
            notes.append(f"extend {before} -> {[r['level_req'] for r in ranks]}")
        # FILL
        i = 0
        filled = False
        while i < len(ranks) - 1:
            lo, hi = ranks[i], ranks[i + 1]
            if hi["level_req"] - lo["level_req"] > MAX_GAP:
                mid = (lo["level_req"] + hi["level_req"]) // 2
                ranks.insert(i + 1, between(lo, hi, mid))
                filled = True
                continue
            i += 1
        if filled:
            notes.append(f"fill -> {[r['level_req'] for r in ranks]}")
    for n, r in enumerate(ranks, start=1):
        r["rank"] = n
    return ranks, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    before = json.load(open(BEFORE, encoding="utf-8")) if os.path.exists(BEFORE) else {}
    changed_total = 0
    for path in sorted(glob.glob("data/abilities/*.json")):
        raw = open(path, encoding="utf-8").read()
        d = json.loads(raw)
        L = d if isinstance(d, list) else d.get("abilities", d)
        changed = 0
        for a in (L.values() if isinstance(L, dict) else L):
            if (not isinstance(a, dict) or not a.get("ranks") or str(a.get("ability_id", "")).endswith("_attack")
                    or os.path.basename(path) in SKIP_FILES):
                continue
            ranks, notes = fix(a)
            if not notes:
                continue
            print(f"  {os.path.basename(path)[:-5]:<16} {a['name']:<28} " + "; ".join(notes))
            before.setdefault(a["ability_id"], [r["level_req"] for r in a["ranks"]])
            a["ranks"] = ranks
            changed += 1
        changed_total += changed
        if args.write and changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
                f.write("\n")
    if args.write:
        with open(BEFORE, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(before.items())), f, indent=1)
            f.write("\n")
    print(f"\n{changed_total} abilities {'changed' if args.write else 'would change'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
