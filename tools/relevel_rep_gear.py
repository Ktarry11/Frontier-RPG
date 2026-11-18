#!/usr/bin/env python3
"""Put the reputation quartermasters' gear on the level-60 ladder Kyle set on 18 Nov 2026.

    PYTHONPATH=. python3 tools/relevel_rep_gear.py           # report
    PYTHONPATH=. python3 tools/relevel_rep_gear.py --write   # data/items/faction_rewards.json and the rep recipes

Kyle: "Lower rep gear. Revered can be 64, exalted can be 68. Heroics are 66 (skull zones and frontier zones can be 68
and 69 heroics...so different) and T1 can be epic lvl 68 and cairne is 71." Honored drops to 62, under Revered.

The ladder (docs/backlog_nov17_onwards.md, section 3a): normal level-60 dungeons 60-63, Honored rep 62, Revered rep 64,
heroics 66 (68 and 69 for the two special kinds), Exalted rep 68, the Fallen Bluff (T1) 68, Cairne Unmade 71.

A quartermaster's own item keeps its stat mix and how strong it was for its level: its budget stats are refitted at
the new level to the same budget ratio (entities/item_budget.fit_to_curve), and its armour and weapon damage scale by
the level change. A rep recipe's item is made from its stat template at craft time, so only its level changes.
Prices don't move: Kyle, "Exalted takes time and should reward. Also raid gear doesn't cost 300g+".

tools/build_faction_rewards.py authored these at 67 and 73; don't re-run it. This replaces its numbers.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TARGET = {"honored": 62, "revered": 64, "exalted": 68}
REWARDS = ROOT / "data/items/faction_rewards.json"
FACTIONS = ROOT / "data/factions/factions.json"
RECIPE_FILES = sorted(ROOT.glob("data/*/recipes.json"))


def tiers():
    """{unique id or recipe id: the tier its quartermaster sells it at}"""
    out = {}
    for f in json.loads(FACTIONS.read_text(encoding="utf-8"))["factions"].values():
        for stock in ((f.get("rewards") or {}).get("vendor_stock") or {}).values():
            for tier, items in stock.items():
                for e in items:
                    if isinstance(e, str):
                        out[e[len("unique:"):] if e.startswith("unique:") else e] = tier
    return out


def relevel_unique(d, new):
    from entities.item_budget import budget_ratio, fit_to_curve
    old = d["item_level"]
    if old == new:
        return False
    ratio = budget_ratio(d)
    k = new / old
    d["item_level"] = new
    if ratio:
        fit_to_curve(d, target=ratio)
    if d.get("armor_value"):
        d["armor_value"] = max(1, int(round(d["armor_value"] * k)))
    for key in ("weapon_damage_min", "weapon_damage_max"):
        if d.get(key):
            d[key] = max(1, int(round(d[key] * k)))
    return True


def main():
    write = "--write" in sys.argv
    tier_of = tiers()
    data = json.loads(REWARDS.read_text(encoding="utf-8"))
    moved = {}
    for uid, d in data["items"].items():
        t = tier_of.get(uid)
        if t in TARGET and d.get("slot") != "tabard":
            before = d["item_level"]
            if relevel_unique(d, TARGET[t]):
                moved[(t, "item", before, TARGET[t])] = moved.get((t, "item", before, TARGET[t]), 0) + 1
    recipe_docs = {}
    for path in RECIPE_FILES:
        doc = json.loads(path.read_text(encoding="utf-8"))
        rs = doc.get("recipes", doc)
        changed = False
        for rid, r in (rs.items() if isinstance(rs, dict) else []):
            t = tier_of.get(rid)
            out = r.get("output") if isinstance(r, dict) else None
            if not rid.startswith("rep_") or t not in TARGET or not isinstance(out, dict) or not out.get("item_level"):
                continue
            if out["item_level"] != TARGET[t]:
                key = (t, "recipe", out["item_level"], TARGET[t])
                moved[key] = moved.get(key, 0) + 1
                out["item_level"] = TARGET[t]
                changed = True
        if changed:
            recipe_docs[path] = doc
    for (t, what, a, b), n in sorted(moved.items()):
        print(f"  {t:8} {what:6} {a} -> {b}: {n}")
    if not moved:
        print("  already on the ladder")
    if write and moved:
        REWARDS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        for path, doc in recipe_docs.items():
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  written {REWARDS.relative_to(ROOT)} and {len(recipe_docs)} recipe files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
