#!/usr/bin/env python3
"""Add the spell-hit gem cuts (Great, Vivid, Serene, Piercing) in place, by build_jewelcrafting's own formulas.

    PYTHONPATH=. python3 tools/add_spell_hit_gems.py && PYTHONPATH=. python3 tools/build_cut_gem_icons.py \
        && PYTHONPATH=. python3 tools/build_recipe_vendors.py

Kyle, 15 Nov 2026: "add a spell hit gem and also some variations of gems that include spell hit + other."

WHY NOT JUST RE-RUN THE BUILDER. tools/build_jewelcrafting.py rewrites every cut gem, recipe and setting, and
the chain after it (enchanting, runecrafting, vendor trades, secrets, crafted gear) doesn't reproduce today's
data: hand edits since (the Regal re-cuts, gem descriptions, the 300 pass's extra recipes) would be lost. So the
four cuts are added to its CUTS table (so a rebuild keeps them) and written here with its exact loop: the same
budget, the same rating floor, the same order-based source rule (SOURCE_FOR overrides), the same skill offsets.
Nothing that exists is touched; it's idempotent.

The new cuts:
    Great     yellow  spell hit                    (TBC's spell-hit Dawnstone; taught)
    Vivid     green   spell hit + Stamina          (TBC's Vivid)
    Serene    green   spell hit + Spirit
    Piercing  green   spell hit + spell penetration
with Veiled (orange: spell power + spell hit) and Lambent (green: spell hit + mp5) already in. Intellect is a
yellow stat, like spell hit, so an Intellect + spell hit gem would be a yellow two-stat cut, which no colour
has; it isn't made.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_jewelcrafting as B  # noqa: E402

NEW = {"Great", "Vivid", "Serene", "Piercing"}


def main():
    from world import jewelcrafting as J
    mdoc = B.load(B.MATS)
    mats = mdoc["materials"]
    gdoc = json.loads((ROOT / "data/jewelcrafting/gems.json").read_text(encoding="utf-8"))
    rdoc = json.loads((ROOT / "data/jewelcrafting/recipes.json").read_text(encoding="utf-8"))
    cuts, recipes = gdoc["cut_gems"], rdoc["recipes"]
    added = []
    for gid, raw in gdoc["raw_gems"].items():
        colour = raw["color"]
        if colour not in ("yellow", "green"):
            continue
        key, m = gid[4:], mats[gid]
        tier, quality, skill = raw["tier"], raw["quality"], raw["skill"]
        budget = J.gem_budget(tier, quality, cap=None)
        n = -1
        for cut, weights in B.CUTS[colour]:
            costs = J.stat_costs()
            raw_vals = {st: budget * w / costs.get(st, 1.0) for st, w in weights.items()}
            if min(raw_vals.values()) < 0.5 or any(
                    v < B.RATING_GEM_FLOOR for st, v in raw_vals.items() if st in B.RATING_KEYS):
                continue
            n += 1
            if cut not in NEW:
                continue
            cid = f"cut_{cut.lower()}_{key}"
            name = f"{cut} {m['name']}"
            stats = J.stats_for(weights, budget)
            cuts[cid] = {"name": name, "color": colour, "quality": quality, "level": raw["level"], "tier": tier,
                         "stats": stats, "raw": gid, "cut": cut}
            fits = " or ".join(sorted(J.FITS[colour]))
            icon = f"cut_{cid[4:]}"
            mats[cid] = {
                "name": name, "material_type": "cut_gem", "profession": "jewelcrafting", "tier": m["tier"],
                "description": f"A cut {colour} gem: {J.stat_text(stats)}. Fits a {fits} socket.",
                "stack_limit": 20, "sell_price": int(m["sell_price"] * 1.5),
                "icon_id": icon if (ROOT / "assets/gathering_nodes/gems" / f"{icon}.png").exists() else m["icon_id"],
                "skill_range": list(m["skill_range"]),
            }
            if skill > B.MAX_SKILL:
                continue
            source = B.SOURCE_FOR.get(cut) or (
                "trainer" if n == 0 or (n == 3 and tier >= 25) else ("vendor" if n % 2 == 1 else "drop"))
            rskill = max(1, skill) + (0 if n == 0 else 10)
            recipes[f"jc_{cid}"] = {
                "name": name, "inputs": {gid: 1}, "skill_required": rskill,
                "output": {"kind": "material", "material_id": cid}, "tool": "jewelers_kit",
                "skill_range": B.skill_range(rskill), "source": source,
            }
            added.append((name, stats, source if skill <= B.MAX_SKILL else "-"))
    B.save(B.MATS, mdoc)
    B.save(ROOT / "data/jewelcrafting/gems.json", gdoc)
    B.save(ROOT / "data/jewelcrafting/recipes.json", rdoc)
    for a in added:
        print(*a)
    print(f"{len(added)} gems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
