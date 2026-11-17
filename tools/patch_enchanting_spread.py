#!/usr/bin/env python3
"""Write tools/build_enchanting's spread skills into the enchanting data, without rebuilding it.

    PYTHONPATH=. python3 tools/patch_enchanting_spread.py

Re-running build_enchanting would put back the recipes the faction pass moved onto quartermasters
(tools/build_faction_rewards.py), so this touches only the numbers that depend on skill: an enchant's "skill", and
its formula's skill_required, skill_range and the rods that will do.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def main():
    import build_enchanting as B
    from tools.build_jewelcrafting import skill_range
    ep, rp = ROOT / "data/enchanting/enchants.json", ROOT / "data/enchanting/recipes.json"
    ed, rd = json.loads(ep.read_text(encoding="utf-8")), json.loads(rp.read_text(encoding="utf-8"))
    moved = 0
    for eid, e in B.enchantments():
        if eid in ed["enchants"] and ed["enchants"][eid].get("skill") != e["skill"]:
            ed["enchants"][eid]["skill"] = e["skill"]
            moved += 1
        r = rd["recipes"].get(f"ench_{eid[8:]}")
        if r is not None:
            r["skill_required"] = e["skill"]
            r["skill_range"] = skill_range(e["skill"])
            if "tool" in r:
                r["tool"] = B.rods_for_tier(e["tier"])
    ep.write_text(json.dumps(ed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rp.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{moved} enchantments moved")


if __name__ == "__main__":
    main()
