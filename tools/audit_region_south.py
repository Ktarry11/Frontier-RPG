#!/usr/bin/env python3
"""Is anything broken in the south of Kalimdor? One pass over nineteen maps.

    PYTHONPATH=. python3 tools/audit_region_south.py

Kyle, 13 Nov 2026, after the zones from the Aspen down to Tanaris were re-dressed: "we need to
still ensure subzones, quests, npcs, and everything are not broken. This will be similar to the
pass with Tanaris region (including abyssal sands and glittervein etc). But obviously one step at
a time". This is that pass, as something that can be run again after the next change.

Read from the LIVE game (the zone manager with its NPCs, chests and nodes placed), not from the
zone modules, because what breaks is the join between them.

FOR EVERY MAP:
  1. GROUND     every walkable tile can be reached from a way in; every door, chest, boss marker
                and NPC tile can be stood beside.
  2. DOORS      every portal leads somewhere, and lands on a tile you can stand on.
  3. SUBZONES   every subzone the map declares has an encounter table or is flagged safe, and
                every table names a subzone the map has. No rare in an open-zone table.
  4. MOBS       every creature in a table exists and has abilities.
  5. PEOPLE     every NPC and vendor filed in the zone stands on the map, on its npc tile, and is
                not under a building.
  6. QUESTS     every quest whose giver stands here: giver and turn-in exist, kill targets spawn
                somewhere, fetch items drop from something.
"""
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

REGION = ["The Aspen Wilderness", "The Weeping Ice", "Rocky Pass", "Southern Thousand Needles",
          "Freewind Post", "The Shimmering Flats", "Saltwheel", "The Undercrust",
          "Northern Tanaris", "Steamwheedle Port", "The Drownbell", "The Abyssal Sands",
          "The Dry Deep", "The Black Strand", "Onyxhollow", "Glittervein", "The Mother Vein",
          "The Cistern", "The Lashings"]


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        from world.portal_manager import PortalManager
        from world.zone_keys import zone_key, zone_slug
        from world.npc_clearance import covered
        zones = create_all_zones()
        pm = PortalManager()

    enc = json.load(open("data/creatures/encounters.json"))["zones"]
    creatures = json.load(open("data/creatures/creatures.json"))["creatures"]
    kits = json.load(open("data/creatures/ability_kits.json"))["kits"]
    templates = json.load(open("data/creatures/templates.json"))["templates"]
    drops = json.load(open("data/creatures/quest_drops.json"))["drops"]
    drop_items = {r["item_id"] for rows in drops.values() for r in rows}
    vendors = json.load(open("data/npcs/vendors.json"))["vendors"]
    ambient = json.load(open("data/npcs/ambient_npcs.json"))["npcs"]
    people = {}
    for r in vendors:
        people[r["vendor_id"]] = r
    for r in ambient:
        people[r["npc_id"]] = r
    spawn_anywhere = set()
    for z in enc.values():
        for part in [z.get("open_zone", {})] + list(z.get("subzones", {}).values()) \
                + list(z.get("caves", {}).values()):
            spawn_anywhere |= set((part or {}).get("creatures", {}))
    quests = []
    for f in sorted(Path("data/quests").glob("*.json")):
        d = json.loads(f.read_text())
        quests += d["quests"] if isinstance(d, dict) else d

    total = 0
    for name in REGION:
        z = zones.get(name)
        bad = []
        if z is None:
            print(f"{name}: NOT IN THE GAME")
            total += 1
            continue
        W, H = z.width, z.height
        doors = pm.get_portal_positions(name)

        # ---- 1. ground
        starts = list(doors) + list(getattr(z, "arrivals", []) or [])
        seen, q = set(), deque()
        for (x, y) in starts:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if 0 <= n[0] < W and 0 <= n[1] < H and z.is_walkable(*n) and n not in seen:
                        seen.add(n)
                        q.append(n)
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen and z.is_walkable(*n):
                    seen.add(n)
                    q.append(n)
        walk = sum(z.is_walkable(x, y) for y in range(H) for x in range(W))
        if walk != len(seen):
            bad.append(f"ground: {walk - len(seen)} walkable tiles cannot be reached")

        def beside(p):
            return any((p[0] + dx, p[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1))

        for y in range(H):
            for x in range(W):
                kind = z.interaction_layer[y][x]
                if kind in ("portal", "chest", "boss_marker", "npc") and not beside((x, y)):
                    bad.append(f"ground: the {kind} at ({x},{y}) cannot be reached")

        # ---- 2. doors
        if not doors:
            bad.append("doors: no way in or out")
        for p in doors:
            d = pm.get_destination(name, *p)
            if not d or d[0] not in zones:
                bad.append(f"doors: {p} leads to {d and d[0]}, which is not a map")
                continue
            dz = zones[d[0]]
            # WHERE YOU ACTUALLY LAND, not the tile in the table. The table already holds the
            # portal tile minus two (PortalManager._offset_spawn), and ZoneManager adds three back
            # when you climb out of a cave onto open ground - so a cave exit sets you down one
            # tile SOUTH of the door it names. The first run of this audit checked the table's
            # tile and reported the Undercrust's east exit as solid rock when it is fine.
            ly = d[2] + (3 if getattr(z, "is_cave", False) and not getattr(dz, "is_cave", False) else 0)
            if not (0 <= ly < dz.height and dz.is_walkable(d[1], ly)):
                bad.append(f"doors: {p} lands at {d[0]} ({d[1]},{ly}), which is solid - the game "
                           f"will move you to the nearest floor, but the link is stale")

        # ---- 3, 4. subzones and mobs
        table = enc.get(name)
        if table is None:
            parent = next((zn for zn, zz in enc.items() if name in zz.get("caves", {})), None)
            parts = {name: enc[parent]["caves"][name]} if parent else {}
            declared = None
            if not parent and not getattr(z, "is_town", False):
                bad.append("subzones: no encounter table at all, and this is not a town")
        else:
            parts = dict(table.get("subzones", {}))
            declared = {s["name"] for s in getattr(z, "subzones", []) if s["name"] != name}
            for s in sorted(declared - set(parts)):
                bad.append(f"subzones: '{s}' is on the map with no table and no safe flag")
            for s in sorted(set(parts) - declared):
                bad.append(f"subzones: the table names '{s}', which the map does not have")
            for c in table.get("open_zone", {}).get("creatures", {}):
                if creatures.get(c, {}).get("is_boss"):
                    bad.append(f"subzones: the rare {c} is in the open-zone table")
            parts["(open zone)"] = table.get("open_zone", {})
        for sname, part in parts.items():
            cs = (part or {}).get("creatures", {})
            if not cs and not (part or {}).get("safe") and sname != "(open zone)":
                bad.append(f"subzones: '{sname}' has an empty table and is not flagged safe")
            for c in cs:
                d = creatures.get(c)
                if d is None:
                    bad.append(f"mobs: {c} ({sname}) does not exist")
                    continue
                kit = d.get("ability_kit") or templates.get(d["template"], {}).get("default_kit")
                if kit not in kits or not kits[kit]:
                    bad.append(f"mobs: {c} has no abilities")

        # ---- 5. people
        here = {i: r for i, r in people.items() if zone_key(str(r.get("zone", ""))) == zone_key(name)
                or zone_slug(str(r.get("zone", ""))) == zone_slug(name)}
        for i, r in here.items():
            x, y = r["x"], r["y"]
            if not (0 <= x < W and 0 <= y < H):
                bad.append(f"people: {i} is filed off the map at ({x},{y})")
                continue
            if not beside((x, y)):
                bad.append(f"people: {i} at ({x},{y}) cannot be reached")
            over = [lm["sprite_key"].split("/")[-1] for lm in z.landmarks
                    if "assets/buildings" in lm["sprite_key"] and covered(lm, x, y) > 0.5]
            if over:
                bad.append(f"people: {i} is drawn under {over[0]}")

        # ---- 6. quests given here
        mine = [qq for qq in quests if qq["giver_npc_id"] in here]
        for qq in mine:
            t = qq.get("turn_in_npc_id")
            if t and t not in people:
                bad.append(f"quests: {qq['quest_id']} turns in to {t}, who does not exist")
            for o in qq["objectives"]:
                if o["type"] in ("kill", "kill_boss") and o["target"] not in spawn_anywhere:
                    alts = o.get("alt_targets") or []
                    if not any(a in spawn_anywhere for a in alts):
                        bad.append(f"quests: {qq['quest_id']} wants {o['target']}, which spawns nowhere")
                if o["type"] == "fetch" and o["target"] not in drop_items:
                    bad.append(f"quests: {qq['quest_id']} fetches {o['target']}, which nothing drops")

        total += len(bad)
        print(f"{name}: {walk} tiles, {len(doors)} doors, {len(parts)} tables, {len(here)} people, "
              f"{len(mine)} quests - " + ("OK" if not bad else f"{len(bad)} PROBLEM(S)"))
        for line in bad[:14]:
            print("    -", line)
        if len(bad) > 14:
            print(f"    ... and {len(bad) - 14} more")
    print(f"\n{total} problem(s) across {len(REGION)} maps")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
