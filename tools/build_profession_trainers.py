#!/usr/bin/env python3
"""Profession trainers + sawmills (idempotent).

TRAINERS COME IN THEMED PAIRS, NOT ONE PER PROFESSION.

Kyle, 2026-10-27, looking at Razor Hill: "Let's mix trainers bro. We don't need so many trainers. We can
have them in themes. Like herbalist and alchemy. or mining and blacksmith, woodworking and woodcutting."

He is right, and the game's own profession descriptions already say which ones belong together -
herbalism is "the ingredients for Alchemy", skinning is "the raw stock for Leatherworking", essence
harvesting draws the essences that engineering "binds into metal". Pairing a gathering profession with
the craft that consumes it is how a player thinks about them anyway, and it means one conversation
instead of two.

THE CONSOLIDATION ALSO FIXES A REAL BUG. Before this, four professions - skinning, leatherworking,
essence harvesting and engineering - had 58 trainer rows between them pointing at NPC ids that did not
exist in ambient_npcs.json. They were appended by a later pass that wrote the trainer entries and never
created the people. Those four professions were UNLEARNABLE ANYWHERE IN THE GAME. Folding them onto
trainers who do exist is what makes them teachable.

Net: a full town goes from SEVEN trainer NPCs teaching seven professions to FIVE teaching eleven.

The three starter towns (Valley of Trials, Echo Isles, Deathknell) still teach the gathering trio only -
a level-two player should not be handed blacksmithing - so they get the three gathering halves and
nothing else.

Writes: data/npcs/ambient_npcs.json (ids pt_<town>_<pair>), data/npcs/sawmills.json,
data/training/trainers.json (profession_trainers maps npc_id -> LIST of professions).
Run from the repo root:   python3 tools/build_profession_trainers.py [--dry-run]
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build_class_trainers as bct  # noqa: E402

#: (pair key, shown title, [professions taught], greeting). The gathering half is listed first in every
#: pair, because that is the order a player meets them in.
PAIRS = [
    ("forge", "Forge", ["mining", "blacksmithing"],
     "Ore in one hand, hammer in the other. I teach both halves or neither - no sense knowing where to "
     "dig if you cannot do anything with it."),
    ("herbs", "Apothecary", ["herbalism", "alchemy"],
     "Every weed is a medicine to someone. I will show you which to pull and what to do with it after, "
     "and the second part is where people go wrong."),
    ("wood", "Woodwright", ["woodcutting", "woodworking"],
     "Fell it, saw it, make something of it. A plank is just a bow that has not happened yet."),
    ("hide", "Tanner", ["skinning", "leatherworking", "tailoring"],
     "Hide, leather and cloth all come off the same bench in my trade. Pay once and I will teach you the "
     "lot of it."),
    ("essence", "Tinker", ["essence_harvesting", "engineering"],
     "Pry the essence out of a dead elemental, bind it into metal, and try not to be holding it when it "
     "decides it would rather not be."),
]
#: Starter towns teach the gathering halves only, and nothing else in the pair.
STARTER_PAIRS = {"forge": ["mining"], "herbs": ["herbalism"], "wood": ["woodcutting"]}
STARTER = {"Valley of Trials", "Echo Isles", "Deathknell"}

# sawmill sites: (zone display name, zone field in sawmills.json)
FORGE_ZONES = {"Valley of Trials": "valley_of_trials", "Durotar": "durotar", "Razor Hill": "razor_hill",
               "Orgrimmar": "orgrimmar", "Crossroads": "crossroads", "Ratchet": "ratchet",
               "Astranaar": "astranaar", "Splintertree Post": "splintertree_post", "Brill": "brill",
               "Undercity": "undercity"}
EXTRA_SAWMILLS = {"Deathknell": "deathknell", "Echo Isles": "echo_isles",
                  "Silverpine South": "silverpine_south", "Zoram Strand": "zoram_strand"}
DRY = "--dry-run" in sys.argv


def norm(s):
    return s.lower().replace(" ", "_").replace("'", "")


DRY = "--dry-run" in sys.argv


def norm(s):
    return s.lower().replace(" ", "_").replace("'", "")


def pick_tiles(z, region, anchor, occupied, want, dmin, dmax, spacing):
    cands = []
    for (x, y) in region:
        d = abs(x - anchor[0]) + abs(y - anchor[1])
        if d < dmin or d > dmax or (x, y) in occupied or z.interaction_layer[y][x]:
            continue
        open_n = sum((x + dx, y + dy) in region for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
        if open_n < 7:
            continue
        near = min([abs(x - ox) + abs(y - oy) for ox, oy in occupied] or [9])
        if near < 2:
            continue
        cands.append((-abs(d - (dmin + dmax) / 2) * 1.0 + open_n * 0.5 + min(near, 4), x, y))
    cands.sort(reverse=True)
    chosen = []
    for _, x, y in cands:
        if all(abs(x - cx) + abs(y - cy) >= spacing for cx, cy in chosen):
            chosen.append((x, y))
            if len(chosen) == want:
                break
    return chosen


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from world.zone_generator import create_all_zones
    from world.race_registry import get_zone_default_race, get_race
    zones = create_all_zones()

    amb_path = ROOT / "data" / "npcs" / "ambient_npcs.json"
    amb = json.loads(amb_path.read_text())
    npcs = [n for n in amb["npcs"] if not n["npc_id"].startswith("pt_")]
    vend = json.loads((ROOT / "data" / "npcs" / "vendors.json").read_text())["vendors"]
    forges = json.loads((ROOT / "data" / "npcs" / "forges.json").read_text()).get("forges", [])

    new_npcs, prof_trainers, sawmills, report = [], {}, [], []
    for zone_name, (slug, anchor_id) in bct.TOWNS.items():
        z = zones.get(zone_name)
        if z is None:
            print("MISSING ZONE", zone_name)
            continue
        zk = bct.ZONE_FIELD.get(zone_name, norm(zone_name))
        here = [n for n in npcs if norm(n["zone"]) == zk]
        here_v = [v for v in vend if norm(v.get("zone", "")) == zk]
        occupied = {(n["x"], n["y"]) for n in here} | {(v["x"], v["y"]) for v in here_v if "x" in v}
        zone_forges = [f for f in forges if norm(f["zone"]) == zk]
        occupied |= {(f["x"], f["y"]) for f in zone_forges}
        anchor = None
        if anchor_id:
            for n in here + here_v:
                if n.get("npc_id", n.get("vendor_id")) == anchor_id:
                    anchor = (n["x"], n["y"])
        if anchor is None:
            pool = [(n["x"], n["y"]) for n in here + here_v if "x" in n]
            cx = sorted(p[0] for p in pool)[len(pool) // 2]
            cy = sorted(p[1] for p in pool)[len(pool) // 2]
            anchor = min(pool, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        start = next(((anchor[0] + dx, anchor[1] + dy) for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (2, 0))
                      if z.is_walkable(anchor[0] + dx, anchor[1] + dy)), None)
        region = bct.flood(z, start)
        starter = zone_name in STARTER
        pairs = [(k, t, STARTER_PAIRS[k], g) for (k, t, _, g) in PAIRS if k in STARTER_PAIRS] if starter \
            else list(PAIRS)
        tiles = pick_tiles(z, region, anchor, occupied, len(pairs), 3, 12, 2)
        if len(tiles) < len(pairs):
            tiles += pick_tiles(z, region, anchor, occupied | set(tiles), len(pairs) - len(tiles), 3, 18, 2)
        races = Counter(n.get("race") for n in here if n.get("race"))
        race = races.most_common(1)[0][0] if races else (get_zone_default_race(zone_name) or bct.RACE_FOR_ZONE_FALLBACK)
        names = bct.NAMES.get(race, bct.NAMES[bct.RACE_FOR_ZONE_FALLBACK])
        opt = get_race(race)
        genders = list(opt.genders) if opt else []
        zone_field = bct.ZONE_FIELD.get(zone_name, zone_name if " " not in zone_name else norm(zone_name))
        for i, ((pkey, title, profs_here, greet), tile) in enumerate(zip(pairs, tiles)):
            g = genders[(i + len(slug)) % len(genders)] if genders else None
            nvar = len(g.variants) if g and g.variants else 1
            nid = f"pt_{slug}_{pkey}"
            new_npcs.append({"npc_id": nid,
                             "name": f"{title} {names[(i * 5 + len(slug) * 2) % len(names)]}",
                             "zone": zone_field, "x": tile[0], "y": tile[1], "greeting": greet,
                             "gender": g.gender_id if g else "male", "race": race,
                             "appearance_variant": (i * 3 + len(slug)) % nvar, "facing": "down",
                             # a LIST now. One NPC, several professions.
                             "trains_profession": list(profs_here)})
            prof_trainers[nid] = list(profs_here)
            occupied.add(tile)
        report.append((zone_name, len(tiles), len(pairs)))

    # sawmills
    sites = dict(FORGE_ZONES)
    sites.update(EXTRA_SAWMILLS)
    all_npcs = npcs + new_npcs
    for zone_name, field in sites.items():
        z = zones.get(zone_name)
        if z is None:
            print("MISSING ZONE (sawmill)", zone_name)
            continue
        zk = norm(field)
        zone_forges = [f for f in forges if norm(f["zone"]) == zk]
        here = [n for n in all_npcs if norm(n["zone"]) == zk or norm(n["zone"]) == bct.ZONE_FIELD.get(zone_name, "-")]
        occupied = {(n["x"], n["y"]) for n in here} | {(f["x"], f["y"]) for f in zone_forges}
        if zone_forges:
            anchor = (zone_forges[0]["x"], zone_forges[0]["y"])
            dmin, dmax = 6, 10
        else:
            pool = [(n["x"], n["y"]) for n in here]
            cx = sorted(p[0] for p in pool)[len(pool) // 2]
            cy = sorted(p[1] for p in pool)[len(pool) // 2]
            anchor = min(pool, key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
            dmin, dmax = 4, 10
        start = next(((anchor[0] + dx, anchor[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)
                      if z.is_walkable(anchor[0] + dx, anchor[1] + dy)), None)
        region = bct.flood(z, start)
        spot = pick_tiles(z, region, anchor, occupied, 1, dmin, dmax, 1)
        if not spot:
            spot = pick_tiles(z, region, anchor, occupied, 1, dmin, dmax + 8, 1)
        if not spot:
            print("NO SAWMILL TILE", zone_name)
            continue
        label = zone_name
        sawmills.append({"sawmill_id": f"{zk}_sawmill", "name": f"{label} Sawmill", "zone": zk, "x": spot[0][0], "y": spot[0][1]})

    for r in report:
        print("%-20s trainers placed %d/%d" % r)
    for s in sawmills:
        print("sawmill", s["sawmill_id"], s["x"], s["y"])
    if DRY:
        print("dry run: would add", len(new_npcs), "trainer NPCs and", len(sawmills), "sawmills")
        return
    amb["npcs"] = npcs + new_npcs
    amb_path.write_text(json.dumps(amb, indent=2) + "\n")
    (ROOT / "data" / "npcs" / "sawmills.json").write_text(json.dumps({
        "_comment": "Sawmills: logs -> planks (Woodcutting skill). Same fixed-object pattern and reach as forges.json. "
                    "Generated by tools/build_profession_trainers.py.",
        "sawmills": sawmills}, indent=2) + "\n")
    tpath = ROOT / "data" / "training" / "trainers.json"
    cur = json.loads(tpath.read_text()) if tpath.exists() else {}
    cur["profession_trainers"] = prof_trainers
    tpath.write_text(json.dumps(cur, indent=2) + "\n")
    print("wrote", len(new_npcs), "profession trainers,", len(sawmills), "sawmills")


if __name__ == "__main__":
    main()
