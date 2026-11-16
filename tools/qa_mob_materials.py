#!/usr/bin/env python3
"""Crafting materials that monsters drop are real, findable and wanted (tools/build_mob_materials.py).

    PYTHONPATH=. python3 tools/qa_mob_materials.py

Kyle, 15 Nov 2026: "add some bro and add some of it to crafting requirements", "you can do it for other zones
too", "the crafting will need to state where they are dropped", and one art sheet "for upwards of 48".

CLAIMS
  1. 48 materials, levels 1-58, each a "mob_reagent" in data/gathering/materials.json with an icon on disk.
  2. Every source creature exists, spawns in a zone the material names, and is in no hidden zone; no hidden
     zone is ever named as a source.
  3. A kill rolls them: a source drops its material some of the time, a boss source every time.
  4. Every material is asked for by at least two finished recipes (armour, weapons, potions, meals, gadgets,
     scrolls), with the counts the build recorded, across at least six trades in all. No recipe asks for two.
  5. The tooltip says where it drops (world/material_sources), so the recipe screen does too.
"""
import json
import os
import random
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    bad = []
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    drops = json.loads((ROOT / "data/creatures/mob_materials.json").read_text(encoding="utf-8"))["materials"]
    uses = json.loads((ROOT / "data/crafting/mob_material_uses.json").read_text(encoding="utf-8"))["uses"]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    from world.hidden_zones import registry, creature_kinds
    hidden, secret = set(registry()), set(creature_kinds())
    mob = {k: v for k, v in mats.items() if v.get("material_type") == "mob_reagent"}
    if len(mob) != 48 or set(mob) != set(drops):
        bad.append(f"{len(mob)} mob_reagent materials and {len(drops)} drop rows, not 48 of each")

    # ---- 1 and 2
    for mid, d in drops.items():
        m = mob.get(mid)
        if not m:
            continue
        if not (ROOT / "assets/gathering_nodes/mob_reagents" / f"{m['icon_id']}.png").exists():
            bad.append(f"{mid}: no icon")
        lo, hi = d["levels"]
        if lo < 1 or hi > 58:
            bad.append(f"{mid}: levels {lo}-{hi} outside 1-58")
        for z in d["zones"]:
            if z in hidden:
                bad.append(f"{mid}: names the hidden zone {z}")
        for c in d["creatures"]:
            if c not in creatures:
                bad.append(f"{mid}: {c} doesn't exist")
            if c in secret:
                bad.append(f"{mid}: {c} lives in a hidden zone")
            homes = []
            for z in d["zones"]:
                t = enc.get(z, {})
                names = set((t.get("open_zone") or {}).get("creatures", {}))
                tables = list((t.get("subzones") or {}).values())
                tables += [v for k, v in (t.get("caves") or {}).items() if k not in hidden]
                for s in tables:
                    names |= set(s["creatures"])
                if c in names:
                    homes.append(z)
            if not homes:
                bad.append(f"{mid}: {c} doesn't spawn in {d['zones']}")

    # ---- 3
    from entities.mob_materials import roll_mob_materials
    for mid, d in drops.items():
        c = d["creatures"][0]
        got = sum(1 for i in range(400) if any(m_ == mid for m_, _q in roll_mob_materials(
            types.SimpleNamespace(name=c, is_boss=False), random.Random(i))))
        if not 0.15 * 400 < got < 0.5 * 400:
            bad.append(f"{mid}: {c} dropped it {got} times in 400")
        if not any(m_ == mid and q >= 1 for m_, q in roll_mob_materials(types.SimpleNamespace(name=c, is_boss=True))):
            bad.append(f"{mid}: a boss {c} didn't drop it")

    # ---- 4
    rec = {}
    nested = json.loads((ROOT / "data/crafting/recipes.json").read_text(encoding="utf-8"))["professions"]
    for p, g in nested.items():
        for rid, r in g["recipes"].items():
            rec[rid] = (p, r)
    for p in ("leatherworking", "blacksmithing", "jewelcrafting", "enchanting", "runecrafting"):
        for rid, r in json.loads((ROOT / f"data/{p}/recipes.json").read_text(encoding="utf-8"))["recipes"].items():
            rec[rid] = (p, r)
    trades = set()
    for mid, u in uses.items():
        if len(u) < 2:
            bad.append(f"{mid}: asked for by {len(u)} recipes")
        for x in u:
            p, r = rec.get(x["recipe"], (None, None))
            if r is None:
                bad.append(f"{mid}: {x['recipe']} no longer exists")
                continue
            trades.add(p)
            if (r.get("inputs") or {}).get(mid) != x["count"]:
                bad.append(f"{mid}: {x['recipe']} doesn't ask for it any more (a recipe rebuild took it off? "
                           f"rerun tools/build_mob_materials.py)")
            o = r.get("output") or {}
            if o.get("kind") not in ("armor", "weapon", "consumable") and not (
                    p == "enchanting" and str(o.get("material_id", "")).startswith("enchant_")):
                bad.append(f"{mid}: {x['recipe']} makes an intermediate, not a finished thing")
    for rid, (p, r) in rec.items():
        n = sum(1 for k in (r.get("inputs") or {}) if k in mob)
        if n > 1:
            bad.append(f"{rid} asks for {n} creature materials")
    if len(trades) < 6:
        bad.append(f"only {len(trades)} trades use them")

    # ---- 5
    from world.material_sources import lines
    for mid in drops:
        if not any(t.startswith("Dropped by") for t in lines(mid)):
            bad.append(f"{mid}: the tooltip doesn't say where it drops")

    n_rec = sum(len(u) for u in uses.values())
    print(f"{len(mob)} creature materials from {len({c for d in drops.values() for c in d['creatures']})} creatures; "
          f"{n_rec} recipes in {len(trades)} trades ask for them")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  - " + b)
        return 1
    print("creature materials OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
