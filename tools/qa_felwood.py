#!/usr/bin/env python3
"""Felwood is built: every map linked, every settlement lived in, the town's services, the faction's rewards
on a real shelf, the right backdrops, Jaedenar a dungeon, and the quests' people and places all real.

    PYTHONPATH=. python3 tools/qa_felwood.py

Kyle, 15 Nov 2026: "let's ensure that felwood is fully built". The audit that started this found:
  - the Emerald Reclamation's rewards were an empty placeholder ("Filled in with the Sanctuary's shops"),
    AND the vendor screen read the bare sells list, so no faction's standing ever put anything on a shelf;
  - Jaedenar wasn't in the dungeon list (nor were Khaz Varun, the Emberdeep or the Royal Hive);
  - North Felwood, the demon wastes, fought in the glowing woodland backdrop the reclaimed South uses;
  - Morlos'Aren is a safe settlement and a quest promises two Sentinels there, and nobody stood in it.
Locations are checked, never printed: hidden places stay hidden.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

OPEN = ("South Felwood", "North Felwood")
ALL = OPEN + ("Emerald Sanctuary", "Jaedenar")
KEY = {"South Felwood": "south_felwood", "North Felwood": "north_felwood",
       "Emerald Sanctuary": "emerald_sanctuary", "Jaedenar": "jaedenar"}
bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def main():
    from world.portal_manager import PortalManager
    from world.zone_classification import is_dungeon
    from world.combat_backgrounds import resolve_place
    from world.faction_manager import get_faction_manager, reward_stock
    from world.vendor_manager import get_vendor_manager
    from world.vendor_stock import resolve_vendor_item
    from world.gathering_manager import GatheringNodeManager
    from entities.consumable_manager import get_consumable_manager
    from entities.loot_generator import LootGenerator

    # ---- the maps, and the doors between them (both ways)
    pm = PortalManager()
    links = [("Ashenvale East", "South Felwood"), ("South Felwood", "Emerald Sanctuary"),
             ("South Felwood", "North Felwood"), ("North Felwood", "Jaedenar")]
    for a, b in links:
        ab = any((pm.get_destination(a, x, y) or (None,))[0] == b for x, y in pm.get_portal_positions(a))
        ba = any((pm.get_destination(b, x, y) or (None,))[0] == a for x, y in pm.get_portal_positions(b))
        check(ab and ba, f"{a} <-> {b}: not linked both ways")
    check(is_dungeon("Jaedenar"), "Jaedenar isn't classed as a dungeon")

    # ---- backdrops: the reclaimed South is woodland, the North and the Fel Line are dead country
    check(resolve_place("South Felwood")[0] == "fantasy_forest", "South Felwood's backdrop isn't woodland")
    check(resolve_place("North Felwood")[0] == "blighted", "North Felwood fights in a living forest")
    check(resolve_place("South Felwood", "The Fel Line")[0] == "blighted", "the Fel Line fights in a living forest")
    check("dungeon" in resolve_place("Jaedenar")[0], "Jaedenar's backdrop isn't a dungeon")

    # ---- every safe settlement in the open maps has somebody standing in it
    npcs = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    people = [(p.get("zone"), p["x"], p["y"]) for p in npcs + vendors if not p.get("hidden")]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    with contextlib.redirect_stdout(io.StringIO()):
        from tools.handbuilt_felwood_south import generate_felwood_south
        from tools.handbuilt_felwood_north import generate_felwood_north
        maps = {"South Felwood": generate_felwood_south(), "North Felwood": generate_felwood_north()}
    settled = 0
    for zone in OPEN:
        safe = {k for k, v in enc[zone]["subzones"].items() if v.get("safe")}
        for sz in getattr(maps[zone], "subzones", []) or []:
            if sz.get("table_key") not in safe:
                continue
            inside = [1 for z, x, y in people if z == KEY[zone]
                      and sz["x"] <= x < sz["x"] + sz["w"] and sz["y"] <= y < sz["y"] + sz["h"]]
            check(inside, f"{zone}: a safe settlement with nobody in it")
            settled += 1
        check(enc[zone]["open_zone"].get("creatures"), f"{zone}: no open-zone encounter table")

    # ---- the town
    t = json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))
    town = [p["npc_id"] for p in npcs if p.get("zone") == "emerald_sanctuary"]
    for svc in ("inn", "flight"):
        check(any(svc in t["services"].get(n, []) for n in town), f"Emerald Sanctuary has no {svc}")
    check(any(f["zone"] == "Emerald Sanctuary" for f in t["flight_nodes"].values()), "no flight node at the Sanctuary")

    # ---- the faction: rewards exist, resolve, sit on a Sanctuary shelf, and the shop SHOWS them at standing
    fm = get_faction_manager()
    f = fm.factions.get("emerald_reclamation")
    check(f is not None, "the Emerald Reclamation is missing")
    stock = {i: v for i, v in reward_stock().items() if v[0] == "emerald_reclamation"}
    check(len(stock) >= 6, f"the Emerald Reclamation rewards {len(stock)} things")
    town_vendors = {v["vendor_id"] for v in vendors if v.get("zone") == "emerald_sanctuary"}
    gm, cm, lg = GatheringNodeManager(), get_consumable_manager(), LootGenerator()
    for item, (_fid, vid, tier) in stock.items():
        check(vid in town_vendors, f"reward {item} is on a shelf outside the Sanctuary")
        with contextlib.redirect_stdout(io.StringIO()):
            got = resolve_vendor_item(item, consumable_manager=cm, gathering_manager=gm, loot_generator=lg)
        check(got is not None, f"reward {item} doesn't resolve to anything a shop can sell")
    if f is not None:
        import pygame
        pygame.init()
        pygame.display.set_mode((1280, 720))
        from entities.character import Character
        from entities.party import Party
        from ui.screens.vendor_screen import VendorScreen

        class SM:
            def __init__(self):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.player = Character(name="Buyer", char_class="Druid", level=55)
                self._party = Party(self.player)

            def get_party(self):
                return self._party

            def transition_to(self, *a, **k):
                pass

        vm = get_vendor_manager()
        before = f.standing
        for standing, want in ((0, False), (10 ** 6, True)):
            f.standing = standing
            for vid in {v[1] for v in stock.values()}:
                with contextlib.redirect_stdout(io.StringIO()):
                    scr = VendorScreen(SM(), vm.vendors[vid])
                shown = {getattr(i, "_sells_id", None) for i in scr.vendor_inventory}
                mine = {i for i, v in stock.items() if v[1] == vid}
                if want:
                    check(mine <= shown, f"{vid}: at exalted the shop doesn't show {sorted(mine - shown)}")
                else:
                    check(not (mine & shown), f"{vid}: at neutral the shop already shows {sorted(mine & shown)}")
        f.standing = before

    # ---- quests: the people who give them and the places they name are real
    quests = json.loads((ROOT / "data/quests/felwood.json").read_text(encoding="utf-8"))["quests"]
    ids = {p["npc_id"] for p in npcs} | {v["vendor_id"] for v in vendors}
    for q in quests:
        g = q.get("giver_npc_id", "")
        check(g.startswith("item:") or g in ids, f"{q['quest_id']}: giver {g} doesn't exist")
        ti = q.get("turn_in_npc_id")
        check(not ti or ti in ids, f"{q['quest_id']}: turn-in {ti} doesn't exist")
    check(len(quests) >= 50, f"only {len(quests)} Felwood quests")

    # ---- the world around it: secrets, fishing, gathering
    secrets = json.loads((ROOT / "data/world/secrets.json").read_text(encoding="utf-8"))["secrets"]
    pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text(encoding="utf-8"))["zones"]
    for zone in OPEN:
        check(sum(1 for s in secrets if s.get("zone") in (zone, KEY[zone])) >= 3, f"{zone}: fewer than 3 secrets")
        check(any(k in pools for k in (zone, KEY[zone])), f"{zone}: no gathering pool")
    src = (ROOT / "world/fishing_pools.py").read_text(encoding="utf-8")
    for zone in OPEN:
        check(f'"{KEY[zone]}"' in src, f"{zone}: no fishing pools")

    print(f"Felwood: {len(ALL)} maps, {len(links)} links, {settled} settlements, {len(stock)} faction rewards, "
          f"{len(quests)} quests")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
