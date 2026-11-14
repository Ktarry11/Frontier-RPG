#!/usr/bin/env python3
"""Artifact Keepers: the NPCs who exchange a class set piece for another spec's version.

Kyle, 12 Nov 2026: "Exchange is free in capital cities, freewind post, and bootybay... Yes we
can have Kael's Bastion too. Also we need unique NPCs for exchange, i dont want them to be
banks or innkeepers. We can call them Artifact Keepers."

One per town below, stood a few tiles from that town's innkeeper on open ground, the same way
tools/build_class_trainers.py stands its trainers (and using its flood fill). Idempotent: every
run removes the keepers it wrote before and writes them again.

Writes: data/npcs/ambient_npcs.json  (npc ids  ak_<town>)
        data/travel/travel_data.json  services: ak_<town> -> ["set_exchange"], and takes
                                      set_exchange OFF anybody else.
Run from the repo root:   python3 tools/build_artifact_keepers.py [--dry-run]
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

#: zone display name -> (slug, anchor npc/vendor id, keeper's name)
TOWNS = {
    "Orgrimmar": ("org", "org_innkeeper", "Artifact Keeper Morgha"),
    "Undercity": ("uc", "uc_innkeeper", "Artifact Keeper Lenore Vance"),
    "Kael's Bastion": ("kb", "kb_innkeeper", "Artifact Keeper Selis Dawnmere"),
    "Freewind Post": ("freewind", "fw_innkeeper", "Artifact Keeper Tahu Stonehorn"),
    "Booty Bay": ("bootybay", "bootybay_tavern_keeper", "Artifact Keeper Vexa Coppercount"),
}
GREETING = ("The same hands made every version of your set. Leave the piece with me and take the "
            "one that suits how you fight now. No charge. Keepers do not sell.")
DRY = "--dry-run" in sys.argv


def norm(s):
    return s.lower().replace(" ", "_").replace("'", "")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from build_class_trainers import flood
    from world.zone_generator import create_all_zones
    from world.race_registry import get_zone_default_race, get_race
    zones = create_all_zones()

    amb_path = ROOT / "data" / "npcs" / "ambient_npcs.json"
    amb = json.loads(amb_path.read_text(encoding="utf-8"))
    npcs = [n for n in amb["npcs"] if not n["npc_id"].startswith("ak_")]
    vend = json.loads((ROOT / "data" / "npcs" / "vendors.json").read_text(encoding="utf-8"))["vendors"]
    forges = json.loads((ROOT / "data" / "npcs" / "forges.json").read_text(encoding="utf-8")).get("forges", [])
    everyone = {n.get("npc_id", n.get("vendor_id")): n for n in npcs + vend if "x" in n}

    new, failed = [], []
    for zone_name, (slug, anchor_id, name) in TOWNS.items():
        z = zones.get(zone_name)
        a = everyone.get(anchor_id)
        if z is None or a is None:
            failed.append(f"{zone_name}: no zone or no anchor {anchor_id}")
            continue
        zk = norm(a["zone"])
        here = [n for n in npcs + vend if "x" in n and norm(n.get("zone", "")) == zk]
        occupied = {(n["x"], n["y"]) for n in here}
        occupied |= {(f["x"], f["y"]) for f in forges if norm(f["zone"]) == zk}
        anchor = (a["x"], a["y"])
        start = next(((anchor[0] + dx, anchor[1] + dy)
                      for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (2, 0), (0, -2), (-2, 0))
                      if z.is_walkable(anchor[0] + dx, anchor[1] + dy)), None)
        if start is None:
            failed.append(f"{zone_name}: anchor {anchor} is walled in")
            continue
        region = flood(z, start)
        best, best_score = None, -1e9
        for (x, y) in region:
            d = abs(x - anchor[0]) + abs(y - anchor[1])
            if d < 3 or d > 10 or (x, y) in occupied or z.interaction_layer[y][x]:
                continue
            open_n = sum((x + dx, y + dy) in region for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy))
            near = min([abs(x - ox) + abs(y - oy) for ox, oy in occupied] or [9])
            if open_n < 7 or near < 2:
                continue
            score = -abs(d - 5) * 2 + open_n * 0.5 + min(near, 4)
            if score > best_score:
                best, best_score = (x, y), score
        if best is None:
            failed.append(f"{zone_name}: no open tile within ten of {anchor}")
            continue
        races = Counter(n.get("race") for n in here if n.get("race"))
        race = races.most_common(1)[0][0] if races else (get_zone_default_race(zone_name) or "orc")
        opt = get_race(race)
        genders = list(opt.genders) if opt else []
        g = genders[len(name) % len(genders)] if genders else None
        nvar = len(g.variants) if g and g.variants else 1
        new.append({"npc_id": f"ak_{slug}", "name": name, "zone": a["zone"], "x": best[0], "y": best[1],
                    "greeting": GREETING, "gender": g.gender_id if g else "female", "race": race,
                    "appearance_variant": (len(name) * 7) % nvar, "facing": "down"})
        print("%-16s anchor %-10s keeper %-10s %s" % (zone_name, anchor, best, race))
    for f in failed:
        print("FAILED", f)
    if DRY or failed:
        return 1 if failed else 0

    amb["npcs"] = npcs + new
    amb_path.write_text(json.dumps(amb, indent=2) + "\n", encoding="utf-8")
    tpath = ROOT / "data" / "travel" / "travel_data.json"
    raw = tpath.read_text(encoding="utf-8")
    travel = json.loads(raw)
    services = travel["services"]
    for who in list(services):
        services[who] = [s for s in services[who] if s != "set_exchange"]
        if not services[who]:
            del services[who]
    for n in new:
        services[n["npc_id"]] = ["set_exchange"]
    tpath.write_text(json.dumps(travel, indent=2 if raw.startswith('{\n  "') else 4) + "\n", encoding="utf-8")
    print("wrote", len(new), "Artifact Keepers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
