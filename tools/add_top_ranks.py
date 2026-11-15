#!/usr/bin/env python3
"""Give every damage and healing ability whose last rank comes at 50-53 a top rank at 58-60.

    PYTHONPATH=. python3 tools/add_top_ranks.py            # show
    PYTHONPATH=. python3 tools/add_top_ranks.py --apply

Found 15 Nov 2026 (Kyle's Healing Wave vs Holy Light check): 68 damage and heal abilities learned by 44 top out
at 50-53 - Holy Light 50, Heal 50, Healing Wave 51, Eviscerate 51, Immolate 51, Earth Shock 53, Rejuvenation 53,
Bloodthirst 52 - so for the last 7-10 levels they stand still while the world grows ~30% (combat/world_curve.py:
3.5% a level). Classic gives its main buttons a rank at 56-60 (Healing Wave R10 and Holy Light R9 at 60).

Each gets ONE new rank at 58 (last rank at 50-52) or 60 (last rank at 53), on the authored line every ability now
sits on (tools/fix_rank_lines.py): value = last value x line(new) / line(last), and a mana cost grown the same
way (rage, energy and the built resources stay flat, as class attacks do). Same for heal_value and absorb.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURVED = {"damage", "spell_damage", "ranged_damage", "dot", "spell_dot", "heal", "hot", "damage_and_heal",
          "damage_and_restore_mana"}
SLOPE = 0.03636


def line(lv):
    return 1 + SLOPE * (max(1, lv) - 1)


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
            if e["ability_id"].endswith("_attack"):
                continue
            ranks = e["ranks"]
            first, last = ranks[0]["level_req"], ranks[-1]["level_req"]
            if first > 44 or not (50 <= last <= 53):
                continue
            new_lv = 60 if last == 53 else 58
            k = line(new_lv) / line(last)
            top = dict(ranks[-1])
            top["level_req"] = new_lv
            if "rank" in top:
                top["rank"] = (top.get("rank") or len(ranks)) + 1
            for key in ("effect_value", "heal_value", "absorb"):
                if top.get(key):
                    top[key] = max(1, round(top[key] * k))
            if top.get("cost") and (e.get("resource_type") or "mana") == "mana":
                top["cost"] = max(1, round(top["cost"] * k))
            ranks.append(top)
            e.setdefault("_tuning", []).append(
                f"15 Nov 2026, class pass: a top rank at {new_lv} added - its last rank came at {last}, leaving it "
                f"standing still while the world grows ~30% (Classic's main buttons rank at 56-60). "
                f"tools/add_top_ranks.py")
            print(f"  {e['ability_id']:40} last L{last} -> new rank L{new_lv}: {ranks[-2].get('effect_value')} -> "
                  f"{top.get('effect_value')}, cost {ranks[-2].get('cost')} -> {top.get('cost')}")
            n += 1
            changed = True
        if apply and changed:
            f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n} abilities {'given' if apply else 'would get'} a top rank")
    return 0


if __name__ == "__main__":
    sys.exit(main())
