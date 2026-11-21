#!/usr/bin/env python3
"""Heroic stage 2: the Frontier Mark, the Frontier Quartermasters' shelf, and one heroic-only item per dungeon.

    PYTHONPATH=. python3 tools/qa_heroic_rewards.py

Kyle, 21 Nov 2026: "Yeah build stage 2", "organize it by armor slot and type and weapon slot", "Make the more
expensive blues higher ilvl", "Don't call them badge of honor. We are Frontier RPG", "quartermaster to sell will be in
capital cities only. Org, UC, and Auerlion", "we should have an icon for them on the map". Checks, through the real code:
  1. the mark is a material with its own icon, and world/heroic.frontier_mark hands one out
  2. a quartermaster stands in Orgrimmar, the Undercity and Aurelion and nowhere else, on a walkable tile, trading
     for marks; every item on the shelf resolves, has a whole positive price in marks and lands in one of the shelf's
     tabs, and no tab is empty
  3. the Pathfinder line is item level 66 and the Horizon line 68 and dearer, all worn at 60
  4. every dungeon's last boss (the last floor of every dungeon chain) has a heroic-only item at 66, and the roll
     gives it at its chance and never to a boss that isn't a last boss
  5. nothing the quartermasters sell and no heroic-only item can go on the auction house or in the mail
  6. combat drops the mark and rolls the heroic-only item on a heroic boss; the map shows the quartermasters
     with the mark's glyph; the word "badge" appears nowhere a player reads
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)


#: a dungeon chain: the floors that make one heroic run, the last of them holding its last boss. Floors are grouped
#: by the name before the colon, except the Scarlet Monastery's wings (four dungeons) and Stratholme, whose Scarlet
#: side is its own dungeon apart from the Scourge side's two floors.
def chains():
    from world.zone_classification import DUNGEONS
    out = {}
    for d in DUNGEONS:
        if d.startswith("Scarlet Monastery") or d == "Stratholme":
            key = d
        elif d.startswith("Stratholme:"):
            key = "Stratholme (the Scourge side)"
        else:
            key = d.split(":")[0]
        out.setdefault(key, []).append(d)
    return out


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from world import heroic as HR
    from world.zone_keys import zone_key
    rw = HR.rewards()
    items = rw.get("items") or {}
    check(items, "data/items/heroic_rewards.json is missing or empty")

    # 1. the mark
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    md = mats.get(rw.get("mark"))
    check(md is not None and md["name"] == "Frontier Mark", "the Frontier Mark isn't a material")
    check((ROOT / "assets/gathering_nodes/reagents/frontier_mark.png").exists(), "the mark has no material icon")
    check((ROOT / "assets/icons/ui/frontier_mark.png").exists(), "the mark has no UI icon")
    m = HR.frontier_mark()
    check(m is not None and m.quantity == 1 and m.material_id == "frontier_mark", "frontier_mark() gave no mark")

    # 2. the quartermasters and their shelf
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    fq = [v for v in vendors if v.get("shelf") == "frontier"]
    check(sorted(zone_key(v["zone"]) for v in fq) == sorted(zone_key(z) for z in ("Orgrimmar", "Undercity",
                                                                                  "Aurelion")),
          f"quartermasters stand in {sorted(v['zone'] for v in fq)}, not the three capitals")
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        Z = {zone_key(k): v for k, v in create_all_zones().items()}
    for v in fq:
        z = Z.get(zone_key(v["zone"]))
        check(z is not None and z.is_walkable(v["x"], v["y"]), f"{v['name']} stands on an unwalkable tile")
        check((v.get("barter") or {}).get("currency") == "frontier_mark", f"{v['name']} doesn't trade for marks")
        check("badge" not in (v["name"] + v.get("greeting", "")).lower(), f"{v['name']} says badge")
    from ui.screens.vendor_screen import VendorScreen
    from world.vendor_manager import VendorManager
    from entities.character import Character
    from entities.party import Party

    class SM:
        def __init__(self):
            self.player = Character(name="QA", char_class="Warrior", level=60)
            self._party = Party(self.player)

        def get_party(self):
            return self._party

    vm = VendorManager()
    for v in fq:
        vend = vm.get_vendor(v["vendor_id"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            scr = VendorScreen(SM(), vend)
        check("WARNING" not in out.getvalue(), f"{v['name']}'s shelf has an id nothing answers to")
        check(len(scr.vendor_inventory) == len(v["sells"]), f"{v['name']}: {len(scr.vendor_inventory)} of "
                                                            f"{len(v['sells'])} items resolved")
        keys = [k for k, _l in scr.BUY_FILTERS]
        counts = {k: 0 for k in keys}
        for it in scr.vendor_inventory:
            cat = scr._vendor_category(it)
            check(cat in keys, f"{it.name} lands in no tab ({cat})")
            counts[cat] = counts.get(cat, 0) + 1
            p = scr._unit_price(it)
            check(isinstance(p, int) and p > 0, f"{it.name} costs {p!r} marks")
        check(all(n for k, n in counts.items() if k != "all"), f"{v['name']} has an empty tab: {counts}")
        check(scr.vendor_inventory == sorted(scr.vendor_inventory, key=scr._shelf_key),
              f"{v['name']}'s shelf isn't sorted by tab and slot")

    # 3. the two lines
    path = [d for d in items.values() if d.get("frontier_line") == "path"]
    hor = [d for d in items.values() if d.get("frontier_line") == "horizon"]
    check(path and all(d["item_level"] == 66 for d in path), "a Pathfinder piece isn't item level 66")
    check(hor and all(d["item_level"] == 68 for d in hor), "a Horizon piece isn't item level 68")
    check(all(d.get("required_level") == 60 for d in path + hor), "a quartermaster piece isn't worn at 60")
    by_slot = {}
    for d in path:
        by_slot.setdefault(d["slot"], []).append(d["frontier_price"])
    for d in hor:
        if d["slot"] in by_slot:
            check(d["frontier_price"] > max(by_slot[d["slot"]]), f"{d['name']} isn't dearer than the Pathfinder "
                                                                 f"pieces in its slot")
    check(not any("badge" in d["name"].lower() for d in items.values()), "an item is called a badge")

    # 4. heroic-only items, one per dungeon's last boss
    only = rw.get("heroic_only") or {}
    finals = {}
    for key, floors in chains().items():
        last = Z.get(zone_key(floors[-1]))
        bp = tuple(getattr(last, "boss_position", None) or ())[:2]
        name = next((b[2] for b in (getattr(last, "boss_positions", None) or []) if tuple(b[:2]) == bp), None)
        finals[key] = name
        check(name in only, f"{key}: its last boss {name} has no heroic-only item")
    extra = set(only) - set(finals.values())
    check(not extra, f"heroic-only items for bosses that aren't a dungeon's last: {sorted(extra)}")
    for boss, iid in only.items():
        d = items.get(iid) or {}
        check(d.get("item_level") == 66 and d.get("heroic_only") == boss, f"{iid} isn't a 66 heroic-only for {boss}")
    rng = random.Random(4)
    boss = next(iter(only))
    got = sum(HR.roll_heroic_only(boss, rng) is not None for _ in range(4000)) / 4000
    want = float(rw.get("heroic_only_chance", 0))
    check(abs(got - want) < 0.03, f"the heroic-only roll lands {got:.0%} of the time, wanted {want:.0%}")
    check(HR.roll_heroic_only("Hogger", random.Random(1)) is None, "a boss with no heroic-only item rolled one")

    # 5. bound to whoever earned them
    from world.market.goods import can_trade
    from world.vendor_stock import make_unique
    for iid in list(items)[:: max(1, len(items) // 12)]:
        it = make_unique(iid)
        check(it is not None and not can_trade(it)[0], f"{iid} could go on the auction house")

    # 6. the hooks
    src = (ROOT / "combat/combat_engine.py").read_text(encoding="utf-8")
    check("frontier_mark()" in src and "roll_heroic_only(enemy.name)" in src, "combat doesn't drop marks or roll the "
                                                                              "heroic-only item")
    ms = (ROOT / "ui/screens/map_screen.py").read_text(encoding="utf-8")
    check('"frontier"' in ms and "frontier_mark.png" in ms, "the map has no glyph for the quartermasters")

    print(f"{len(fq)} Frontier Quartermasters; {len(path)} Pathfinder (66) and {len(hor)} Horizon (68) pieces; "
          f"{len(only)} heroic-only items for {len(finals)} dungeons")
    if FAILS:
        print(f"FAIL ({len(FAILS)})")
        for f in FAILS:
            print("  -", f)
        return 1
    print("heroic rewards OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
