#!/usr/bin/env python3
"""Heroic dungeons, stage 1 (docs/heroic_design.md, world/heroic.py).

    PYTHONPATH=. python3 tools/qa_heroic.py

Kyle, 18 Nov 2026: every dungeon gets a level-60 heroic; pick Normal or Heroic at the door; once per market day;
level-60 elites; the same loot with better stats at item level 66; "Ensure vendor trash Is also appropriately
improved in heroics as are chests drops"; rep past Revered, and a tabard takes the kill rep.
Checks, through the real code:
  1. the door asks only when walking into a dungeon from outside, at 60
  2. a run starts, locks for the market day, opens again the next, survives a save, and ends on walking out
  3. a run is live in its dungeons by display name and by the key combat uses, and nowhere else
  4. a monster made in a heroic is level 60 and elite (more health than the same monster made normally at 60)
  5. a boss's fixed drop comes back as its heroic version: same name, item level 66, worn at 60, on the curve;
     out of a heroic it's untouched
  6. heroic coin and vendor trash pay COIN_MULT more; a heroic boss chest rolls at 66 and a side chest at 63,
     worn at 60
  7. rep: with the combat key a normal dungeon stops at Revered, a heroic doesn't, and a tabard takes the kill
  8. a heroic adds only the two lowest top-tier cloths and leathers (Kyle: "Only TWO of the top tier crafting
     materials each"), never the rest, and isn't "pure 60" (so no post-60 recipes); the door and combat wiring are in
"""
import os
import random
import sys
import types
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from world import heroic as H
    from world import zone_manager as ZM
    from world.travel_manager import TravelManager, get_travel_manager

    tm = get_travel_manager()
    saved = (tm.heroic_run, dict(tm.heroic_locks))
    old_live = getattr(ZM, "LIVE", None)
    try:
        # 1
        lead60, lead59 = types.SimpleNamespace(level=60), types.SimpleNamespace(level=59)
        check(H.offers_choice("Wailing Caverns", "Southern Barrens", lead60), "no choice at the Wailing Caverns door")
        check(not H.offers_choice("Wailing Caverns", "Southern Barrens", lead59), "the door asked a level 59")
        check(not H.offers_choice("Stratholme: Service Entrance", "Stratholme", lead60),
              "the door asked again between two floors of one dungeon")
        check(not H.offers_choice("Orgrimmar", "Durotar", lead60), "the door asked outside a dungeon")

        # 2
        tm.heroic_run, tm.heroic_locks = None, {}
        ok, _m = H.start("Wailing Caverns", 30.0, tm)
        check(ok and tm.heroic_run == "Wailing Caverns", "a heroic didn't start")
        ok2, msg = H.start("Wailing Caverns", 40.0, tm)
        check(not ok2 and "today" in msg, f"the same heroic ran twice in a market day: {msg}")
        check(H.start("Razorfen Kraul", 40.0, tm)[0], "a different heroic was locked out")
        tm.heroic_run = "Wailing Caverns"
        again = TravelManager()
        again.load_from_dict(tm.to_dict())
        check(again.heroic_run == "Wailing Caverns" and again.heroic_locks == tm.heroic_locks,
              "a save lost the heroic run or its lockouts")
        check(H.start("Wailing Caverns", 49.0, tm)[0], "the heroic didn't open the next market day")
        H.on_zone_change("Wailing Caverns", "Southern Barrens", tm)
        check(tm.heroic_run is None and "Wailing Caverns" in tm.heroic_locks, "walking out didn't end the run")

        # 3
        tm.heroic_run = "Wailing Caverns"
        check(H.active("Wailing Caverns") and H.active("wailing_caverns"), "a run isn't live in its dungeon")
        check(not H.active("Southern Barrens"), "a run is live outside the dungeons")
        tm.heroic_run = None
        check(not H.active("Wailing Caverns"), "a normal run counts as heroic")

        # 4. a Wailing Caverns monster, made in a heroic and made normally at 60
        from world.creature_manager import CreatureManager
        cm = CreatureManager()
        import json
        enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))
        names = []

        def walk(node, key):
            if isinstance(node, dict):
                if (node.get("name") or key) == "Wailing Caverns" and isinstance(node.get("creatures"), dict):
                    names.extend(node["creatures"])
                for k, v in node.items():
                    walk(v, k)
        walk(enc, None)
        trash = next((n for n in names if not cm.creatures.get(n, {}).get("is_boss")), None)
        if check(trash is not None, "no Wailing Caverns trash to test with"):
            ZM.LIVE = types.SimpleNamespace(current_zone=types.SimpleNamespace(name="Wailing Caverns"))
            tm.heroic_run = "Wailing Caverns"
            hm = cm.spawn_creature(trash)
            tm.heroic_run = None
            nm = cm.spawn_creature(trash, level=60)
            check(hm.level == 60 and getattr(hm, "_heroic", False), f"a heroic {trash} is level {hm.level}")
            check(hm.max_health > nm.max_health, f"a heroic {trash} ({hm.max_health}) isn't tougher than a "
                                                 f"normal one at 60 ({nm.max_health})")

        # 5. Lord Pythas's drops
        from entities.boss_loot import get_fixed_boss_loot_all, _load_boss_loot_tables
        from entities.item_budget import budget_ratio
        pool = _load_boss_loot_tables().get("Lord Pythas") or []
        if check(pool, "Lord Pythas has no fixed loot"):
            random.seed(3)
            normal = get_fixed_boss_loot_all("Lord Pythas")
            random.seed(3)
            hero = get_fixed_boss_loot_all("Lord Pythas", heroic_ilvl=H.ITEM_LEVEL)
            for a, b in zip(normal, hero):
                check(a.name == b.name, f"the heroic drop changed its name: {a.name} -> {b.name}")
                check(b.item_level == H.ITEM_LEVEL and b.required_level <= H.WORN_AT,
                      f"{b.name}: heroic item level {b.item_level}, worn at {b.required_level}")
                check(a.item_level < 40, f"{a.name}: the normal drop moved to {a.item_level}")
            for d in pool:
                r = budget_ratio(H.heroic_def(d))
                check(r is None or 0.9 <= r <= 1.1, f"{d['name']}: heroic version at {r:.2f} of the curve")

        # 6. trash, coin and chests
        from entities.vendor_trash import roll_drops
        mob = types.SimpleNamespace(name="Kolkar Wrangler", level=60, is_boss=False, location_type="cave")
        hob = types.SimpleNamespace(name="Kolkar Wrangler", level=60, is_boss=False, location_type="cave", _heroic=True)
        a = roll_drops(mob, random.Random(5))
        b = roll_drops(hob, random.Random(5))
        check(b["copper"] >= int(a["copper"] * H.COIN_MULT) - 1 and b["copper"] > a["copper"],
              f"heroic coin {b['copper']} against normal {a['copper']}")
        # a beast's trash: every heroic piece is worth COIN_MULT times the same piece from a normal kill
        base = {}
        for seed in range(30):
            for it in roll_drops(types.SimpleNamespace(name="Russet Boar", level=60, is_boss=True,
                                                       location_type="cave"), random.Random(seed))["items"]:
                base[it["item_id"]] = it["price"]
        seen = 0
        for seed in range(30):
            for it in roll_drops(types.SimpleNamespace(name="Russet Boar", level=60, is_boss=True, location_type="cave",
                                                       _heroic=True), random.Random(seed))["items"]:
                if it["item_id"] in base:
                    seen += 1
                    check(it["price"] >= int(base[it["item_id"]] * H.COIN_MULT) - 1,
                          f"heroic {it['name']} pays {it['price']}, normal {base[it['item_id']]}")
        check(seen, "no vendor trash to compare")
        from world.chest_manager import ChestManager
        chest = ChestManager()
        tile = types.SimpleNamespace(name="Wailing Caverns", set_tile=lambda *a, **k: None)
        tm.heroic_run = "Wailing Caverns"
        boss_item = chest.open_chest(tile, 3, 3, 60, is_boss_chest=True)
        side = None
        for i in range(40):
            side = chest.open_chest(tile, 10 + i, 4, 60)
            if side is not None:
                break
        tm.heroic_run = None
        check(boss_item is not None and boss_item.item_level == H.ITEM_LEVEL and boss_item.required_level <= 60,
              f"a heroic boss chest gave {getattr(boss_item, 'item_level', None)}")
        if side is not None:
            check(side.item_level <= H.TRASH_ITEM_LEVEL and side.item_level >= 60 and side.required_level <= 60,
                  f"a heroic side chest gave item level {side.item_level}, worn at {side.required_level}")

        # 7. rep, with the key combat really passes
        from world import faction_manager as FM
        fm = FM.get_faction_manager()
        tiers = {t["id"]: t["at"] for t in fm.tiers}
        fm.reset()
        fm.factions["orgrimmar"].standing = tiers["revered"] + 10
        got = {f: g for f, g, _t in fm.award_for_kill("QA Boss", zone="ragefire_chasm", is_boss=True)}
        check(got.get("orgrimmar", 0) == 0, "with the combat key a normal dungeon paid past Revered")
        got = {f: g for f, g, _t in fm.award_for_kill("QA Boss", zone="ragefire_chasm", is_boss=True, heroic=True)}
        check(got.get("orgrimmar", 0) > 0, "with the combat key a heroic paid nothing past Revered")
        got = {f: g for f, g, _t in fm.award_for_kill("QA Boss", zone="ragefire_chasm", is_boss=True, heroic=True,
                                                      tabard="the_wakened")}
        check(set(got) == {"the_wakened"}, f"with the combat key the tabard paid {got}")
        fm.reset()

        # 8. only the two lowest top-tier cloths and leathers, and no post-60 recipes
        from entities.material_tiers import HEROIC_TOP, HIGH_TIER, is_pure_60
        from entities.cloth_drops import roll_cloth
        from entities.skinning_drops import roll_leather
        got = set()
        for i in range(400):
            got |= {m for m, _q in roll_cloth(types.SimpleNamespace(name="Kolkar Wrangler", level=60, is_boss=True,
                                                                   _heroic=True), random.Random(i))}
            got |= {m for m, _q in roll_leather(types.SimpleNamespace(name="Russet Boar", level=60, is_boss=True,
                                                                     _heroic=True), None, random.Random(i))}
        allowed = set(HEROIC_TOP["cloth"]) | set(HEROIC_TOP["leather"])
        check(got & HIGH_TIER == allowed, f"a heroic dropped top tiers {sorted(got & HIGH_TIER)}, wanted "
                                          f"{sorted(allowed)}")
        normal = set()
        for i in range(400):
            normal |= {m for m, _q in roll_cloth(types.SimpleNamespace(name="Kolkar Wrangler", level=60,
                                                                      is_boss=True), random.Random(i))}
        check(not normal & HIGH_TIER, f"a normal level-60 dungeon dropped {sorted(normal & HIGH_TIER)}")
        tm.heroic_run = "Wailing Caverns"
        check(not is_pure_60("wailing_caverns"), "a heroic counts as pure 60, which opens every top tier")
        tm.heroic_run = None
        ow = (ROOT / "ui/screens/overworld_screen.py").read_text(encoding="utf-8")
        check("heroic.offers_choice(" in ow and "_render_heroic_door" in ow, "the overworld has no heroic door")
        ce = (ROOT / "combat/combat_engine.py").read_text(encoding="utf-8")
        check("heroic_ilvl=_HEROIC_ILVL if self.heroic" in ce and "TRASH_ITEM_LEVEL" in ce,
              "combat doesn't roll heroic loot")
    finally:
        tm.heroic_run, tm.heroic_locks = saved
        ZM.LIVE = old_live

    print("heroic doors, lockouts, monsters, loot, trash, chests, rep and materials checked")
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:25]:
            print("  ", x)
        return 1
    print("heroic dungeons OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
