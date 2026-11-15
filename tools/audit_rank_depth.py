#!/usr/bin/env python3
"""Do the CoA classes rank their spells, abilities and buffs as deeply as the Classic classes do?

    PYTHONPATH=. python3 tools/audit_rank_depth.py [--verbose]

Kyle, 15 Nov 2026: "We also need to deep dive into all classes to ensure there are appropriate ranks for spells,
abilities, buffs etc. This was something I commented about with CoA classes having so few ranks. We need to ensure
they're in line with Classic classes." (and 14 Nov: "CoA classes cap out FAST with their skills....rank 1/2 or 1/1???")

Every ability is put in a category by what it does - a direct hit, a damage-over-time, a direct heal, a heal-over-time,
a shield, a buff of FLAT stats (Fortitude, Arcane Intellect, Blessing of Might - Classic ranks these), or a buff
of PERCENTAGES / effects (30% more damage is 30% at any level: Classic does not rank those, nor should we). For
each category the Classic classes set the norm: how many ranks, how far apart, and the level of the last rank.
A CoA ability is THIN when it has fewer ranks than the Classic norm for an ability learned at its level, or its
last rank is below 50 (while it was learned by 44). Talent-unlocked abilities are held to a lower bar (Classic's own
talent spells - Mortal Strike, Shadowform's kit - have a few ranks, not nine).
"""
import argparse
import glob
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
CLASSIC = {"warrior", "paladin", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"}
SKIP = {"_universal.json", "asher_unique.json"}


def category(e):
    t = e.get("effect_type")
    if t in ("damage", "spell_damage", "ranged_damage", "damage_and_heal", "damage_and_restore_mana"):
        return "direct damage"
    if t in ("dot", "spell_dot"):
        return "damage over time"
    if t == "heal":
        return "direct heal"
    if t == "hot":
        return "heal over time"
    if any("absorb" in r for r in e.get("ranks") or []):
        return "shield"
    if (e.get("absorb_pct_max_health") or 0) > 0:
        return None           # a share of max health: grows with the bar, no ranks needed
    if t in ("buff", "debuff"):
        mods = e.get("stat_mods") or {}
        # FLAT stats the world curve does NOT grow (combat/world_curve.py, 15 Nov 2026): attack, spell and healing
        # power, mp5/hp5 and the primary stats (which feed health, mana and power) are all multiplied by the world
        # curve at the player's level, so a flat +60 attack power buff grows as you level without ranks - the job
        # Classic's buff ranks did. Armour does not (mitigation is level-keyed), so armour buffs still want ranks.
        # Resistances run on a flat 0-60 scale by design and flags (taunt, cc_immune) are not amounts.
        flat = {k: v for k, v in mods.items() if isinstance(v, (int, float)) and k in ("armor", "block_value")}
        return "flat-stat buff" if flat else "percent buff"
    return None


def unlocked_by_talent():
    out = set()
    for f in glob.glob("data/talents/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        nodes = d.get("nodes") or d.get("talents") or d
        for n in (nodes if isinstance(nodes, list) else nodes.values()):
            if isinstance(n, dict):
                u = (n.get("effects") or {}).get("unlock_ability")
                if u:
                    out.add(u)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()
    talented = unlocked_by_talent()
    rows = []
    for f in sorted(glob.glob("data/abilities/*.json")):
        if os.path.basename(f) in SKIP:
            continue
        cls = os.path.basename(f)[:-5]
        d = json.load(open(f, encoding="utf-8"))
        L = d if isinstance(d, list) else d.get("abilities", d)
        for e in (L.values() if isinstance(L, dict) else L):
            if not isinstance(e, dict) or not e.get("ranks") or e["ability_id"].endswith("_attack"):
                continue
            cat = category(e)
            if cat is None or cat == "percent buff":
                continue
            lv = [r["level_req"] for r in e["ranks"]]
            gaps = [b - a for a, b in zip(lv, lv[1:])]
            rows.append({"cls": cls, "classic": cls in CLASSIC, "id": e["ability_id"], "cat": cat,
                         "talent": e["ability_id"] in talented, "n": len(lv), "first": lv[0], "last": lv[-1],
                         "gap": statistics.mean(gaps) if gaps else None})
    # the Classic norm per category, for trainer-taught (non-talent) abilities: ranks per level of span
    norms = {}
    print("CLASSIC NORMS (trainer-taught abilities)")
    for cat in sorted({r["cat"] for r in rows}):
        cl = [r for r in rows if r["classic"] and r["cat"] == cat and not r["talent"]]
        if not cl:
            continue
        gap = statistics.median([r["gap"] for r in cl if r["gap"]] or [8])
        last = statistics.median([r["last"] for r in cl])
        n = statistics.median([r["n"] for r in cl])
        norms[cat] = (gap, last)
        print(f"  {cat:<18} {len(cl):>3} abilities  median ranks {n:>4.1f}  rank every {gap:>4.1f} levels  last rank at {last:.0f}")

    def expected(r):
        gap, last = norms.get(r["cat"], (8, 56))
        span = max(0, min(last, 60) - r["first"])
        want = 1 + int(span / gap)
        if r["talent"]:
            want = max(1, int(round(want * 0.5)))
        return want
    thin = []
    for r in rows:
        want = expected(r)
        if r["n"] < want - 1 or (r["first"] <= 44 and r["last"] < 50 and not r["talent"]):
            thin.append((r, want))
    print("\nDEPTH BY CLASS - abilities with fewer ranks than the Classic norm for when they're learned")
    by = {}
    for r in rows:
        by.setdefault(r["cls"], []).append(r)
    for cls in sorted(by, key=lambda c: (c not in CLASSIC, c)):
        rs = by[cls]
        t = [x for x, _w in thin if x["cls"] == cls]
        print(f"  {cls:<18} {'classic' if cls in CLASSIC else 'CoA':<8} {len(rs):>3} ranked-type abilities, "
              f"median ranks {statistics.median(x['n'] for x in rs):>4.1f}, thin: {len(t)}")
    print(f"\n{len(thin)} thin abilities in all; by category:")
    cats = {}
    for r, w in thin:
        cats.setdefault(r["cat"], []).append((r, w))
    for cat, lst in sorted(cats.items(), key=lambda kv: -len(kv[1])):
        print(f"  {cat:<18} {len(lst)}")
        for r, w in lst[: (None if args.verbose else 6)]:
            print(f"      {r['id']:<44} {r['n']} ranks (L{r['first']}-{r['last']}), norm {w}"
                  f"{'  [talent]' if r['talent'] else ''}")
    if args.json:
        Path(args.json).write_text(json.dumps([dict(r, want=w) for r, w in thin]), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
