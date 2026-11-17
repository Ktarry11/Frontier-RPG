#!/usr/bin/env python3
"""Put the auction house and the mail in the world: auctioneers in the capitals and goblin ports, a mailbox by
every inn. Idempotent.

    python3 tools/place_market_npcs.py [--apply]

Kyle, 15 Nov 2026: "AH in capitals and goblin towns, mail everywhere" (every town with an inn). docs/
auction_house_design.md, sections 1 and 11.

A mailbox stands on the nearest clear tile to the innkeeper (in front of them first): walkable, nothing drawn
over it, not a door, nobody else within a tile, with a walkable neighbour. Same rules as
tools/move_npcs_off_buildings.py. It's drawn in its town's style: orc, troll, Forsaken, tauren or goblin
(Kyle's market prop sheet, assets/tiles/market/props/). A new auctioneer stands the same way beside the town's banker or innkeeper.
Writes data/npcs/ambient_npcs.json and the "auction" service in data/travel/travel_data.json.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

#: new auctioneers: id -> (name, beside whom, race, gender, greeting)
AUCTIONEERS = {
    "org_auctioneer": ("Auctioneer Grizzik", "org_banker", "goblin", "male",
                       "Bids, buyouts, the whole Horde's junk drawer. Step up, step up. The house takes five percent and none of the blame."),
    "bb_auctioneer": ("Auctioneer Fazzle", "bootybay_tavern_keeper", "goblin", "female",
                      "Steamwheedle rules, honey. Everybody trades, nobody fights, and the house takes fifteen percent off the top."),
    "ratchet_auctioneer": ("Auctioneer Snork", "ratchet_tavern_keeper", "goblin", "male",
                           "Whatever you've got, somebody wants it. Whatever you want, somebody's overcharging for it. Welcome to the block."),
    "stw_auctioneer": ("Auctioneer Kizzle", "stw_innkeeper", "goblin", "female",
                       "Neutral ground, neutral prices, very much not neutral cut. What are we selling?"),
}
#: auctioneers already in the world that only needed the service
EXISTING = ["uc_auctioneer", "fw_auctioneer"]

#: Kyle's market prop sheet (tools/slice_building_sheet.py market_props): each culture's mailbox. A town gets the
#: first; the second culture town gets the B version, and so on, so neighbouring towns don't match.
CULTURE = {"orc": ["mailbox_orc", "mailbox_orc_b"], "troll": ["mailbox_troll"],
           "undead": ["mailbox_forsaken", "mailbox_forsaken_b"], "forsaken": ["mailbox_forsaken", "mailbox_forsaken_b"],
           "tauren": ["mailbox_tauren", "mailbox_tauren_b"], "goblin": ["mailbox_goblin", "mail_tube_goblin"]}
GOBLIN_TOWNS = {"booty_bay", "ratchet", "steamwheedle_port", "saltwheel", "fourth_peg"}
#: towns whose zone default race isn't the people who run the inn (the default is "human" for most new zones)
TOWN_CULTURE = {"sepulcher": "forsaken", "freewind_post": "tauren", "sun_rock_retreat": "tauren", "gromgol": "troll",
                "splintertree_post": "orc", "hammerfall": "orc", "zoram_strand": "orc"}
#: Per inn, where a zone holds more than one culture. The Plaguelands' human hubs (the Pale Flame, the Argent Dawn,
#: Crown Guard) use the Forsaken box's grey iron until Kyle draws a human mailbox.
INN_CULTURE = {"wpl_bulwark_innkeeper": "forsaken", "wpl_pf_innkeeper": "forsaken", "epl_cg_innkeeper": "forsaken",
               "epl_lh_innkeeper": "forsaken"}


def main():
    apply = "--apply" in sys.argv
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from PIL import Image
    from core.game_state import GameStateManager
    from entities.character import Character
    from world.zone_keys import zone_key
    from world.race_registry import get_zone_default_race
    sm = GameStateManager(pygame.display.get_surface())
    sm.player = Character(name="H", char_class="Warrior", level=60)
    zm = sm._live_zone_manager()
    zones = {zone_key(n): (n, e["tilemap"] if isinstance(e, dict) else e) for n, e in zm.zones.items()}
    cache = {}

    def cover(l, x, y):
        ax, ay, w, h = l["anchor_x"], l["anchor_y"], l["width_tiles"], l["height_tiles"]
        if not (ax <= x < ax + w and ay <= y < ay + h):
            return 0.0
        key = (l["sprite_key"], w, h)
        if key not in cache:
            try:
                cache[key] = Image.open(l["sprite_key"]).convert("RGBA").resize((w * 16, h * 16)).getchannel("A")
            except Exception:
                cache[key] = None
        a = cache[key]
        if a is None:
            return 0.0
        px = list(a.crop(((x - ax) * 16, (y - ay) * 16, (x - ax) * 16 + 16, (y - ay) * 16 + 16)).getdata())
        return sum(1 for v in px if v > 128) / len(px)

    amb_path = ROOT / "data/npcs/ambient_npcs.json"
    amb = json.loads(amb_path.read_text(encoding="utf-8"))
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    travel_path = ROOT / "data/travel/travel_data.json"
    travel = json.loads(travel_path.read_text(encoding="utf-8"))
    by_id = {}
    for row in amb["npcs"]:
        by_id[row["npc_id"]] = row
    for row in vendors:
        by_id.setdefault(row["vendor_id"], row)
    taken = {}
    for row in list(amb["npcs"]) + list(vendors):
        if row.get("x") is not None and row.get("zone"):
            taken.setdefault(zone_key(row["zone"]), set()).add((row["x"], row["y"]))

    def spot(zk, x, y, avoid_ids=()):
        if zk not in zones:
            return None
        _n, t = zones[zk]
        lms = list(getattr(t, "landmarks", []) or [])
        people = {p for p in taken.get(zk, set())}
        npcs = {(i, j) for j in range(t.height) for i in range(t.width) if t.interaction_layer[j][i] == "npc"} | people
        for d in range(2, 10):
            ring = [(x + dx, y + dy) for dx in range(-d, d + 1) for dy in range(-d, d + 1) if max(abs(dx), abs(dy)) == d]
            ring.sort(key=lambda p: (-(p[1] - y), abs(p[0] - x)))
            for (nx, ny) in ring:
                if not (1 <= nx < t.width - 1 and 1 <= ny < t.height - 1):
                    continue
                if not t.is_walkable(nx, ny) or t.interaction_layer[ny][nx]:
                    continue
                if max([cover(l, nx, ny) for l in lms] or [0.0]) > 0.15:
                    continue
                if any(abs(nx - ox) <= 1 and abs(ny - oy) <= 1 for (ox, oy) in npcs):
                    continue
                if not any(t.is_walkable(nx + a, ny + b) for a, b in ((0, 1), (1, 0), (-1, 0), (0, -1))):
                    continue
                return nx, ny
        return None

    rows = {r["npc_id"]: r for r in amb["npcs"]}
    placed, missing = [], []
    # mailboxes
    for inn_id, services in travel["services"].items():
        if "inn" not in services:
            continue
        host = by_id.get(inn_id)
        mid = "mailbox_" + inn_id
        if host is None or host.get("x") is None:
            missing.append(f"{inn_id}: no position")
            continue
        zk = zone_key(host["zone"])
        if mid in rows:
            continue
        pos = spot(zk, host["x"], host["y"])
        if pos is None:
            missing.append(f"{inn_id} ({host['zone']}): no clear tile")
            continue
        race = "goblin" if zk in GOBLIN_TOWNS else TOWN_CULTURE.get(zk) or get_zone_default_race(host["zone"])
        race = INN_CULTURE.get(inn_id, race)
        opts = CULTURE.get(race, ["mailbox_orc_b"])
        n = sum(1 for r in amb["npcs"] if r.get("is_mailbox") and r.get("race") == race)
        prop = f"assets/tiles/market/props/{opts[n % len(opts)]}.png"
        row = {"npc_id": mid, "name": "Mailbox", "zone": host["zone"], "x": pos[0], "y": pos[1],
               "greeting": f"The inn's mailbox. {host.get('name', 'The innkeeper')} sorts the letters, parcels and "
                           f"whatever the auction house owes you.",
               "facing": "down", "race": race, "appearance_variant": 0, "is_mailbox": True,
               "prop": prop}
        amb["npcs"].append(row)
        rows[mid] = row
        taken.setdefault(zk, set()).add(pos)
        placed.append(f"mailbox by {inn_id}: {host['zone']} {pos}")
    # auctioneers
    for aid, (name, beside, race, gender, greeting) in AUCTIONEERS.items():
        if aid in rows:
            continue
        host = by_id.get(beside)
        if host is None or host.get("x") is None:
            missing.append(f"{aid}: {beside} not found")
            continue
        zk = zone_key(host["zone"])
        pos = spot(zk, host["x"], host["y"])
        if pos is None:
            missing.append(f"{aid}: no clear tile by {beside}")
            continue
        row = {"npc_id": aid, "name": name, "zone": host["zone"], "x": pos[0], "y": pos[1], "greeting": greeting,
               "facing": "down", "race": race, "gender": gender, "appearance_variant": 2}
        amb["npcs"].append(row)
        rows[aid] = row
        taken.setdefault(zk, set()).add(pos)
        placed.append(f"{name}: {host['zone']} {pos}")
    for aid in list(AUCTIONEERS) + EXISTING:
        sv = travel["services"].setdefault(aid, [])
        if "auction" not in sv:
            sv.append("auction")
    for p in placed:
        print("  " + p)
    for m in missing:
        print("  ?? " + m)
    if apply:
        amb_path.write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        travel_path.write_text(json.dumps(travel, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(placed)} placed{'' if apply else ' (dry run)'}, {len(missing)} not placed")


if __name__ == "__main__":
    main()
