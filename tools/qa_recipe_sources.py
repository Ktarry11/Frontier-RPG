#!/usr/bin/env python3
"""A recipe that says it comes from the world has to actually come from the world.

    PYTHONPATH=. python3 tools/qa_recipe_sources.py

Kyle, 2026-10-28: "ensure there are nice rare drops of useful recipies to learn etc. or still reward
some through quests."

THE BUG THIS EXISTS TO CATCH ALREADY HAPPENED, SILENTLY, FOR 192 RECIPES. world/recipe_manager had a
working make_recipe_scroll() and a docstring claiming "the loot system, vendor system, and quest
system all call make_recipe_scroll()". Nothing called it - zero callers in the whole codebase. So 135
recipes carried source "drop" and 57 carried "vendor", every one of them was labelled as something
you find or buy, and not one could be found or bought. Nothing failed, nothing warned; the labels
were simply decoration.

Which is why this does not check that the plumbing exists. It checks, for every single recipe, that
there is a concrete route by which a player ends up holding it:

  trainer  -> learn_trainer_recipes teaches it on a visit, so the skill number is the only gate
  vendor   -> some vendor's sells list names it AND the stock resolver can build a scroll from it
  drop     -> it is inside the eligible pool for some creature level the game actually contains
  quest    -> a quest's reward_recipe names it

A recipe may have more than one route; it must have at least one.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from entities.recipe_drops import eligible
    from world.recipe_manager import _load_all_recipes, make_recipe_scroll

    recipes = _load_all_recipes()

    # ---- what each route can actually deliver
    vendor_stock = set()
    for v in json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]:
        vendor_stock |= {s for s in v.get("sells", []) if s in recipes}

    quest_rewards = set()
    for p in sorted((ROOT / "data/quests").glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for q in doc.get("quests") or []:
            if isinstance(q, dict) and q.get("reward_recipe"):
                quest_rewards.add(q["reward_recipe"])

    # The highest level any creature in the game actually reaches - a drop pool that only opens at
    # level 70 is not a route while nothing is level 70.
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    top_level = max((max(c.get("level_range") or [1]) for c in creatures.values()), default=1)
    droppable = set(eligible(top_level))

    fails, routes = [], {"trainer": 0, "vendor": 0, "drop": 0, "quest": 0}
    for rid, (prof, r) in sorted(recipes.items()):
        source = r.get("source", "trainer")
        got = []
        if source == "trainer":
            got.append("trainer")
        if rid in vendor_stock:
            got.append("vendor")
        if rid in droppable:
            got.append("drop")
        if rid in quest_rewards:
            got.append("quest")
        if not got:
            fails.append(f"{rid} ({prof}, source={source}, skill "
                         f"{r.get('skill_required', 0)}) has no route to a player")
            continue
        for g in got:
            routes[g] += 1
        # and the scroll itself has to build
        if source != "trainer" or rid in vendor_stock or rid in quest_rewards:
            if make_recipe_scroll(rid) is None:
                fails.append(f"{rid} is obtainable but make_recipe_scroll returns None")

    # ---- the hidden vendors have to be standing somewhere a player can reach
    from world.vendor_manager import VendorManager
    from world.zone_manager import ZoneManager
    vm, zm = VendorManager(), ZoneManager()
    hidden = [v for v in json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
              if v.get("hidden")]
    for v in hidden:
        zone = next((z for z in zm.zones
                     if vm._zone_key(z) == vm._zone_key(v["zone"])), None)
        if zone is None:
            fails.append(f"hidden vendor {v['name']} is in zone {v['zone']!r}, which has no tilemap")
            continue
        tm = zm.zones[zone]["tilemap"]
        x, y = v["x"], v["y"]
        blocked = [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                   if not tm.is_walkable(x + dx, y + dy)]
        if blocked:
            fails.append(f"hidden vendor {v['name']} at ({x},{y}) in {zone} has unwalkable tiles "
                         f"around them: {blocked}")

    print(f"== {len(recipes)} recipes; routes found: "
          + ", ".join(f"{n} by {k}" for k, n in routes.items() if n))
    print(f"== creatures top out at level {top_level}, so {len(droppable)} recipes are inside a "
          f"live drop pool")
    print(f"== {len(vendor_stock)} stocked by a vendor, {len(quest_rewards)} given by a quest, "
          f"{len(hidden)} hidden vendors checked\n")
    # HALF FROM THE TRAINER, HALF FROM THE WORLD. Kyle, 12 Nov: "i still want only 50-55% from
    # trainer and 50-55% from world...hidden vendors, quests, bosses, random world drops" - "for
    # ALL crafting". The sawmill (woodcutting) is processing, like smelting, and stays taught.
    share = {}
    for rid, (prof, r) in recipes.items():
        t = share.setdefault(prof, [0, 0])
        t[0] += 1
        t[1] += r.get("source", "trainer") == "trainer"
    for prof, (total, taught) in sorted(share.items()):
        if prof == "woodcutting" or total < 20:
            continue
        pct = taught / total
        print(f"   {prof:16s} {pct:.0%} trainer-taught")
        if not 0.495 <= pct <= 0.555:
            fails.append(f"{prof}: {pct:.0%} of its recipes come from the trainer; the band is 50-55%")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS - every recipe has a route to a player")
    return 0


if __name__ == "__main__":
    sys.exit(main())
