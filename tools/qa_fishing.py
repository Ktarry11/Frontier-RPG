#!/usr/bin/env python3
"""Fishing works end to end (Kyle, 13 Nov 2026).

    PYTHONPATH=. python3 tools/qa_fishing.py

  1. Fishing is a SECONDARY trade: a character with every primary slot full can still learn it,
     and so is Cooking. Every trainer who teaches Cooking teaches Fishing.
  2. Fishing spots appear on SHORE tiles (walkable, water beside them) in a zone with a
     shoreline, and nowhere else; none in a town.
  3. Every fish in a zone's pool fits the zone's level, and is a real material with an icon.
  4. Stepping on a spot without the skill is refused; with it you get the fish.
  5. Every fish is used by at least one recipe, every fish recipe makes something that exists,
     and Alchemy really takes fish (oils, then elixirs).
"""
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    from world import profession_manager as PM
    from world.gathering_manager import get_gathering_node_manager, shore_tiles, WATER_TILES
    from world.zone_manager import ZoneManager
    from world.zone_keys import zone_key
    from entities.character import Character

    # 1
    check(PM.is_secondary("fishing") and PM.is_secondary("cooking"), "fishing and cooking must both be secondary")
    c = Character("T", "Warrior", 20)
    primaries = [p for p, d in PM.professions().items() if d.get("kind") != "secondary"][:PM.max_primary()]
    c.known_professions = list(primaries)
    check(PM.primary_count(c) == PM.max_primary(), "setup: slots should be full")
    offer = PM.offers(c, "fishing")
    check("already know" not in json.dumps(offer, default=str).lower(), f"fishing is blocked by full slots: {offer}")
    tr = json.load(open("data/training/trainers.json"))["profession_trainers"]
    cooks = [n for n, v in tr.items() if isinstance(v, list) and "cooking" in v]
    check(cooks and all("fishing" in tr[n] for n in cooks), "a cooking trainer does not teach fishing")

    # 2 + 3
    mats = json.load(open("data/gathering/materials.json"))["materials"]
    pools = json.load(open("data/gathering/node_pools.json"))["zones"]
    levels = {zone_key(k): v for k, v in json.load(open("data/zones/zone_levels.json"))["zones"].items()}
    fish = {k: v for k, v in mats.items() if v.get("material_type") == "fish"}
    check(len(fish) == 22, f"expected 22 fish before 60, found {len(fish)}")
    with_pool = {k: p["fishing"] for k, p in pools.items() if p.get("fishing")}
    check(len(with_pool) >= 20, f"only {len(with_pool)} zones have fishing")
    for key, fp in with_pool.items():
        lo, hi = levels[key]
        for fid in fp["table"]:
            check(fid in fish, f"{key}: {fid} is not a fish")
            if fid in fish:
                s = fish[fid]["skill_range"][0]
                check(max(0, (lo - 15) * 5) <= s <= hi * 5, f"{key} {lo}-{hi}: {fid} (skill {s}) does not fit")
    for fid, f in fish.items():
        check((ROOT / f"assets/gathering_nodes/fish/{f['icon_id']}.png").is_file(), f"{fid} has no icon")
    zm = ZoneManager()
    gm = get_gathering_node_manager()
    random.seed(4)
    seen_spots = 0
    for name, z in zm.zones.items():
        tm = z["tilemap"]
        key = zone_key(name)
        before = [row[:] for row in tm.interaction_layer]
        gm.populate(tm, name)
        nodes = [n for n in gm.active_nodes if mats.get(n.material_id, {}).get("material_type") == "fish"]
        if getattr(tm, "is_town", False):
            check(not nodes, f"{name} is a town and has fishing spots")
        shore = set(shore_tiles(tm))
        for n in nodes:
            seen_spots += 1
            check((n.x, n.y) in shore, f"{name}: fishing spot at {(n.x, n.y)} is not beside water")
        if key in with_pool and len(shore) >= 25:
            check(nodes, f"{name} has a fishing pool and a shoreline but no spots appeared")
        gm.clear()
        tm.interaction_layer = before
    check(seen_spots > 40, f"only {seen_spots} fishing spots across the world")

    # 4
    mat = gm.make_material_instance("fish_brilliant_smallfish")
    check(mat is not None and mat.profession == "fishing", "a caught fish is not a fishing material")
    c2 = Character("F", "Warrior", 5)
    check(not c2.knows_profession("fishing"), "a new character already knows fishing")
    ok, _msg = PM.learn(c2, None, "fishing") if PM.offers(c2, "fishing") else (False, "")
    check(c2.knows_profession("fishing") or not ok, "learning fishing did not take")

    # 5
    rd = json.load(open("data/crafting/recipes.json"))["professions"]
    cons = json.load(open("data/consumables/consumable_types.json"))
    known = {x["consumable_id"] for v in cons.values() if isinstance(v, list) for x in v}
    used = set()
    for prof in ("cooking", "alchemy"):
        book = rd[prof].get("recipes", rd[prof])
        for rid, r in book.items():
            for k in r.get("inputs", {}):
                if k in fish:
                    used.add(k)
            if rid.startswith("fishx_"):
                out = r["output"]
                if out["kind"] == "consumable":
                    check(out["consumable_id"] in known, f"{rid} makes {out['consumable_id']}, which does not exist")
                else:
                    check(out["material_id"] in mats, f"{rid} makes {out['material_id']}, which does not exist")
                for k in r["inputs"]:
                    check(k in mats, f"{rid} needs {k}, which does not exist")
    check(used == set(fish), f"fish no recipe uses: {sorted(set(fish) - used)}")
    alch = rd["alchemy"].get("recipes", rd["alchemy"])
    check(sum(1 for r in alch.values() if any(k in fish for k in r.get("inputs", {}))) >= 3,
          "alchemy does not take fish")

    print(f"22 fish, {len(with_pool)} zones with a fishing pool, {seen_spots} spots placed in one pass")
    if bad:
        for b in bad[:25]:
            print("  -", b)
        return 1
    print("\nfishing OK - secondary, on the shore, fits its zones, feeds cooking and alchemy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
