#!/usr/bin/env python3
"""Class trainers: ONE trainer per town, and it trains every class (idempotent).

Kyle, 2026-10-27: "class trainer should train everyone."

WHAT THIS REPLACED. Every town used to get seventeen NPC records - one per class - all standing on the
SAME tile, with AmbientNPCManager.set_viewer_class hiding the sixteen that were not yours. So the plaza
never actually looked crowded; the player always saw exactly one trainer. But it was 272 records
describing 16 people, it meant adding a class touched every town, and the viewer-class filter existed
solely to clean up after it.

One universal trainer per town does the same job with 16 records and no filter. A trainer whose
trains_class is "*" is shown to everybody and teaches whoever walks up.

THE FLAVOUR COST, stated plainly: the old records were class-flavoured ("Warrior Trainer Grik", with a
line about what a warrior is worth). A universal trainer cannot be, so the greeting is written to make a
virtue of it - these are veterans who have taught all of it and are not precious about which.

Writes: data/npcs/ambient_npcs.json  (npc ids  ct_<town>)   and   data/training/trainers.json
    class_trainers maps npc_id -> "*" (universal) or a class name (older data still works).
Run from the repo root:   python3 tools/build_class_trainers.py [--dry-run]
AFTER RUNNING THIS, run tools/place_trainers_at_trades.py. This script scatters trainers near the inn;
that one stands each at the building of their trade (the forge, the tannery, the training hall).
"""
import json
import os
import sys
from collections import Counter, deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CLASSES = ["Warrior", "Rogue", "Hunter", "Mage", "Warlock", "Priest", "Druid", "Shaman", "Paladin",
           "Stormbringer", "Tinker", "Venomancer", "Primalist", "Runemaster", "Cultist", "Starcaller", "Sun Cleric"]

# zone display name -> (npc slug, anchor npc id)
TOWNS = {
    "Valley of Trials": ("vot", None),
    "Echo Isles": ("echo", None),
    "Razor Hill": ("razorhill", "razorhill_innkeep"),
    "Orgrimmar": ("org", "org_innkeeper"),
    "Crossroads": ("crossroads", "crossroads_innkeeper"),
    "Camp Taurajo": ("taurajo", "taurajo_innkeeper"),
    "Ratchet": ("ratchet", "ratchet_tavern_keeper"),
    "Southern Barrens": ("sbarrens", "sb_innkeeper"),
    "Splintertree Post": ("splintertree", "splintertree_innkeeper"),
    "Astranaar": ("astranaar", "astranaar_innkeeper"),
    "Zoram Strand": ("zoram", None),
    "Deathknell": ("deathknell", None),
    "Brill": ("brill", "brill_innkeeper"),
    "The Sepulcher": ("sepulcher", "sepulcher_innkeeper"),
    "Undercity": ("uc", "uc_innkeeper"),
    "Silverpine South": ("spsouth", "sp_south_flight_master"),
    # The tauren capital-in-exile. A capital gets its trainers from the same pipeline as
    # everywhere else - it would be strange for the biggest tauren settlement in the world to
    # be the one place you cannot learn anything.
    "Freewind Post": ("freewind", "fw_innkeeper"),
    # Hammerfall is the only full town between Tarren Mill and the far side of Arathi, and it is
    # the hub of a 28-40 region. Refuge Pointe and Saltspur deliberately get none - a forward camp
    # and a beachhead do not teach, and making the player come back to the hold to train is the
    # thing that makes Hammerfall feel like the middle of the region rather than one more camp.
    "Hammerfall": ("hammerfall", "hammerfall_innkeeper"),
}

CLASS_TITLE = {c: c for c in CLASSES}

# Names by race pool (deterministic pick by town+class)
NAMES = {
    "orc": ["Grokk", "Thurgan", "Durza", "Kagra", "Mogor", "Vashka", "Brakka", "Zogar", "Hulda", "Garrek", "Naruk",
            "Shazra", "Drogan", "Urzul", "Karga", "Rokan", "Bruga", "Tazgul", "Orgha", "Skarn"],
    "troll": ["Zul'jin", "Vol'ka", "Sen'zo", "Mojari", "Tor'jan", "Zalara", "Jin'ta", "Ras'kal", "Nezla", "Vanjo",
              "Sa'rok", "Kazu", "Mala'ki", "Dazo", "Zephra"],
    "tauren": ["Baine", "Ahnu", "Kaga", "Moonfeather", "Tahn", "Runetotem", "Hamuul", "Greyhoof", "Nara", "Omak",
               "Sunwalker", "Stonehorn", "Bloodhoof", "Mistpaw"],
    "goblin": ["Fizzbolt", "Snicker", "Grimble", "Zippo", "Nix", "Gadget", "Sprocket", "Wrenchy", "Bazil", "Kaz",
               "Tinkle", "Gizmo", "Cogsworth", "Vexa"],
    "forsaken": ["Caldwell", "Mortimer", "Ysolde", "Harken", "Veyra", "Osric", "Thessaly", "Grimsby", "Lenore",
                 "Aldous", "Mirela", "Corvin", "Edda", "Rothgar", "Verity", "Bleak"],
    "human": ["Alden", "Marta", "Corwin", "Elara", "Thomas", "Ingrid", "Gareth", "Lysa"],
    "night_elf": ["Shandris", "Tyrande", "Elaria", "Maiev", "Ilyenna", "Valen", "Thalanil"],
}
RACE_FOR_ZONE_FALLBACK = "orc"
# the zone field existing ambient NPCs use where it differs from the display name
ZONE_FIELD = {"The Sepulcher": "sepulcher", "Hammerfall": "hammerfall"}
DRY = "--dry-run" in sys.argv


def flood(z, start):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < z.width and 0 <= n[1] < z.height and z.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from world.zone_generator import create_all_zones
    from world.race_registry import get_zone_default_race, get_race
    zones = create_all_zones()

    amb_path = ROOT / "data" / "npcs" / "ambient_npcs.json"
    amb = json.loads(amb_path.read_text(encoding="utf-8"))
    npcs = [n for n in amb["npcs"] if not n["npc_id"].startswith("ct_")]
    vend = json.loads((ROOT / "data" / "npcs" / "vendors.json").read_text(encoding="utf-8"))["vendors"]
    forges = json.loads((ROOT / "data" / "npcs" / "forges.json").read_text(encoding="utf-8")).get("forges", [])

    def norm(s):
        return s.lower().replace(" ", "_").replace("'", "")

    new_npcs, class_trainers, report = [], {}, []
    for zone_name, (slug, anchor_id) in TOWNS.items():
        z = zones.get(zone_name)
        if z is None:
            print("MISSING ZONE", zone_name)
            continue
        zk = ZONE_FIELD.get(zone_name, norm(zone_name))
        here = [n for n in npcs if norm(n["zone"]) == zk]
        here_v = [v for v in vend if norm(v.get("zone", "")) == zk]
        occupied = {(n["x"], n["y"]) for n in here} | {(v["x"], v["y"]) for v in here_v if "x" in v}
        occupied |= {(f["x"], f["y"]) for f in forges if norm(f["zone"]) == zk}
        anchor = None
        if anchor_id:
            for n in here + here_v:
                if n.get("npc_id", n.get("vendor_id")) == anchor_id:
                    anchor = (n["x"], n["y"])
        if anchor is None:
            pool = [(n["x"], n["y"]) for n in here + here_v if "x" in n]
            if not pool:
                print("NO ANCHOR", zone_name)
                continue
            cx = sorted(p[0] for p in pool)[len(pool) // 2]
            cy = sorted(p[1] for p in pool)[len(pool) // 2]
            anchor = min(pool, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        # connected region around the anchor
        start = next(((anchor[0] + dx, anchor[1] + dy) for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (2, 0))
                      if z.is_walkable(anchor[0] + dx, anchor[1] + dy)), None)
        if start is None:
            print("ANCHOR UNREACHABLE", zone_name, anchor)
            continue
        region = flood(z, start)
        best, best_score = None, -1e9
        for (x, y) in region:
            d = abs(x - anchor[0]) + abs(y - anchor[1])
            if d < 2 or d > 8 or (x, y) in occupied:
                continue
            if z.interaction_layer[y][x]:
                continue
            open_n = sum((x + dx, y + dy) in region for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy))
            near_npc = min([abs(x - ox) + abs(y - oy) for ox, oy in occupied] or [9])
            if open_n < 7 or near_npc < 2:
                continue
            score = -abs(d - 4) * 2 + open_n * 0.5 + min(near_npc, 4)
            if score > best_score:
                best, best_score = (x, y), score
        if best is None:
            print("NO TILE", zone_name, anchor)
            continue
        races = Counter(n.get("race") for n in here if n.get("race"))
        race = races.most_common(1)[0][0] if races else (get_zone_default_race(zone_name) or RACE_FOR_ZONE_FALLBACK)
        pool = NAMES.get(race, NAMES[RACE_FOR_ZONE_FALLBACK])
        opt = get_race(race)
        genders = [g for g in (opt.genders if opt else [])] or []
        i = len(slug)
        nid = f"ct_{slug}"
        name = f"Trainer {pool[(i * 3) % len(pool)]}"
        g = genders[i % len(genders)] if genders else None
        gender = g.gender_id if g else "male"
        nvar = len(g.variants) if g and g.variants else 1
        rec = {"npc_id": nid, "name": name,
               "zone": ZONE_FIELD.get(zone_name, zone_name if " " not in zone_name else norm(zone_name)),
               "x": best[0], "y": best[1],
               "greeting": "I have taught every one of the disciplines at one time or another, and I am "
                           "not precious about which you picked. Show me where you are and bring gold.",
               "gender": gender, "race": race, "appearance_variant": (i * 5) % nvar,
               "facing": "down", "trains_class": "*"}
        new_npcs.append(rec)
        class_trainers[nid] = "*"
        report.append((zone_name, anchor, best, race, len(region)))
    for r in report:
        print("%-20s anchor %-10s trainer %-10s %-9s region %d" % (r[0], r[1], r[2], r[3], r[4]))
    if DRY:
        print("dry run: would add", len(new_npcs), "trainer NPCs")
        return
    amb["npcs"] = npcs + new_npcs
    amb_path.write_text(json.dumps(amb, indent=2) + "\n", encoding="utf-8")
    tdir = ROOT / "data" / "training"
    tdir.mkdir(exist_ok=True)
    tpath = tdir / "trainers.json"
    cur = json.loads(tpath.read_text(encoding="utf-8")) if tpath.exists() else {}
    cur["class_trainers"] = class_trainers
    tpath.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")
    print("wrote", len(new_npcs), "trainer NPCs")


if __name__ == "__main__":
    main()
