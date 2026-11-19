#!/usr/bin/env python3
"""Nothing under level 60 is made of a level-60 material, in any trade.

    PYTHONPATH=. python3 tools/qa_no_level60_materials_below_60.py

Kyle, 18 Nov 2026: "Fix up woodworking. Nothing sub 60 should use lvl 60 materials." A level-60 material is one
above the pre-60 line (entities/material_tiers.PRE_60_SKILL_CEILING, skill 300), or anything a recipe makes out of
one. Checks, for every recipe in every trade:
  1. a recipe that takes a level-60 material makes either gear worn at 60, or another level-60 material
  2. every material a pre-60 recipe needs can be gathered, dropped or made somewhere (so a pre-60 recipe is never
     dead for want of something no map has)
  3. level 60's own two per kind (material_tiers.LEVEL60_TOP) are all above the line
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recipe_manager import _load_all_recipes
    from entities.material_tiers import PRE_60_SKILL_CEILING, LEVEL60_TOP
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))
    mats = mats.get("materials", mats)

    def skill(mid):
        return ((mats.get(mid) or {}).get("skill_range") or [0])[0]

    recipes = _load_all_recipes()
    # which made materials are level-60, to a fixed point (a stick made of a level-60 plank is level-60 too)
    hi = {m for m in mats if skill(m) > PRE_60_SKILL_CEILING}
    makes = {}
    for rid, (prof, r) in recipes.items():
        o = r.get("output") or {}
        if o.get("kind") == "material":
            makes.setdefault(o.get("material_id") or o.get("id") or rid, []).append((rid, r))
    grew = True
    while grew:
        grew = False
        for mid, rs in makes.items():
            if mid not in hi and rs and all(any(i in hi for i in (r.get("inputs") or {})) for _rid, r in rs):
                hi.add(mid)
                grew = True

    # 1
    bad = []
    for rid, (prof, r) in recipes.items():
        ins = r.get("inputs") or {}
        used = sorted(i for i in ins if i in hi)
        if not used:
            continue
        o = r.get("output") or {}
        if o.get("kind") == "material":
            out = o.get("material_id") or o.get("id") or rid
            if out not in hi and skill(out) <= PRE_60_SKILL_CEILING:
                # a pre-60 material with a level-60 way to make it is fine as long as a pre-60 way exists too
                if all(any(i in hi for i in (rr.get("inputs") or {})) for _r, rr in makes.get(out, [])):
                    bad.append(f"{prof} {rid}: makes pre-60 {out} only from {used}")
            continue
        item = o.get("item") if isinstance(o.get("item"), dict) else o
        worn = item.get("required_level") or max(1, (item.get("item_level") or 0) - 2)
        if worn < 60:
            bad.append(f"{prof} {rid}: {item.get('name') or rid} worn at {worn} needs {used}")
    for b in bad:
        check(False, b)

    # 2. every material a pre-60 recipe needs exists somewhere
    pools = json.dumps(json.loads((ROOT / "data/gathering/node_pools.json").read_text(encoding="utf-8")))
    gathered_kinds = ("wood", "ore", "herb")
    dead = set()
    for rid, (prof, r) in recipes.items():
        for i in (r.get("inputs") or {}):
            m = mats.get(i) or {}
            if m.get("material_type") in gathered_kinds and skill(i) <= PRE_60_SKILL_CEILING \
                    and f'"{i}"' not in pools:
                dead.add(i)
    check(not dead, f"pre-60 materials a recipe needs that grow on no map: {sorted(dead)}")

    # 3
    for kind, two in LEVEL60_TOP.items():
        check(len(two) == 2 and all(skill(m) > PRE_60_SKILL_CEILING for m in two), f"level 60's {kind}: {two}")

    print(f"{len(recipes)} recipes, {len(hi)} level-60 materials; level 60 gets "
          + ", ".join(f"{k} {'/'.join(v)}" for k, v in LEVEL60_TOP.items()))
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:40]:
            print("  ", x)
        return 1
    print("nothing under level 60 is made of a level-60 material.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
