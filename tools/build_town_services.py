#!/usr/bin/env python3
"""Every town gets an inn and a flight master. Idempotent.

    PYTHONPATH=. python3 tools/build_town_services.py [--check]

Kyle, 29 Oct 2026: "each town should have an inn and a flight master."

WHY THIS WAS BROKEN, and why it never surfaced. An inn and a windrider roost are not built, they are
REGISTERED: an NPC becomes an innkeeper by having its id listed under `services` in
data/travel/travel_data.json, and a flight master additionally needs a `flight_nodes` entry naming it.
Nothing validates that a town has either. A town with an innkeeper standing in an inn, fully written,
fully placed, simply does not offer a hearth bind if nobody added one line to a JSON file - and the
only way to notice is to walk up to them in game and have nothing happen.

Four towns were short. Three different causes, which is why a sweep was worth more than a patch:

  Freewind Post    had BOTH NPCs already - fw_innkeeper and fw_flight_master, written, placed, with
                   greetings - and neither was registered. Forty-one NPCs and no hearth. Pure data gap.
  Tarren Mill      had an innkeeper (unregistered) and no flight master at all.
  Kael's Bastion   same shape: kb_innkeeper unregistered, no roost.
  Zoram Strand     had neither. The smallest of the four and the only one that needed both invented.

WHAT THIS DOES NOT DO: it does not add services to wilderness zones. Durotar, the Barrens, Echo Isles
and the rest have NPCs and no town, and an inn in the middle of a zone is not a gap, it is a mistake.
The list below is towns.

THE AUDIT IS THE POINT. --check reports every town's coverage and exits non-zero on a gap, so the next
town somebody builds fails this instead of shipping without a hearth.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.zone_keys import zone_key as _zk  # noqa: E402

#: npc zone key -> the zone's display name. These are the TOWNS; wilderness zones are deliberately out.
TOWNS = {
    "orgrimmar": "Orgrimmar", "razor_hill": "Razor Hill", "crossroads": "Crossroads",
    "camp_taurajo": "Camp Taurajo", "ratchet": "Ratchet", "southern_barrens": "Southern Barrens",
    "splintertree_post": "Splintertree Post", "astranaar": "Astranaar", "zoram_strand": "Zoram Strand",
    "freewind_post": "Freewind Post", "undercity": "Undercity", "brill": "Brill",
    "sepulcher": "The Sepulcher", "tarren_mill": "Tarren Mill", "kaels_bastion": "Kael's Bastion",
    "gromgol": "Grom'gol", "booty_bay": "Booty Bay",
}

#: Already-written NPCs that were never registered. Nothing to invent - just the missing line.
REGISTER_INN = ["fw_innkeeper", "tarren_mill_innkeeper", "kb_innkeeper"]
REGISTER_FLIGHT = ["fw_flight_master"]

#: npc_id -> (name, zone key, x, y, race, gender, greeting). Positions were picked off the built
#: zone - walkable, unoccupied, and clear of every existing NPC by two tiles.
NEW_NPCS = {
    "tarren_mill_flight_master": (
        "Wind-Rider Ghulrak", "tarren_mill", 42, 47, "orc", "male",
        "Hillsbrad from the air is all fences. You do not see how much of it is fences until you are over it."),
    "kb_flight_master": (
        "Skyward-Warden Thalyn", "kaels_bastion", 48, 46, "blood elf", "female",
        "The fissure is wide enough to fly out of. Getting a hippogryph to agree took most of a season."),
    "zoram_flight_master": (
        "Wind-Rider Aleris", "zoram_strand", 30, 23, "night elf", "female",
        "Astranaar inland, and nothing else from here. The coast road is for people with time."),
    "zoram_innkeeper": (
        "Innkeeper Lysaia", "zoram_strand", 28, 23, "night elf", "female",
        "Four beds and a fire that does not go out. It is not much, but it is dry and it is the last one west."),
}

#: node id -> (display name, zone, master npc_id, pos, continent). Positions drive the distance-based
#: fare, so they are placed relative to the nodes already on each continent rather than at random.
NEW_NODES = {
    "freewind_post": ("Freewind Post", "Freewind Post", "fw_flight_master", [-10, 145], "kalimdor"),
    "zoram_strand": ("Zoram Strand", "Zoram Strand", "zoram_flight_master", [-70, -55], "kalimdor"),
    "tarren_mill": ("Tarren Mill", "Tarren Mill", "tarren_mill_flight_master", [-18, 85], "eastern_kingdoms"),
    "kaels_bastion": ("Kael's Bastion", "Kael's Bastion", "kb_flight_master", [20, 40], "eastern_kingdoms"),
}


def coverage():
    """town key -> (has_inn, has_flight, node_id or None)."""
    td = json.loads((ROOT / "data/travel/travel_data.json").read_text())
    svc, nodes = td["services"], td["flight_nodes"]
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text())["npcs"]
    ven = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    # NORMALISE, do not compare raw. The first version of this audit grouped on the raw `zone`
    # string and reported Undercity as having no flight master - uc_flight_master is filed under the
    # display name "Undercity" while the rest of that roster uses the slug. An audit that disagrees
    # with the engine about what a zone is called will invent gaps and miss real ones.
    ids = {}
    for e in amb:
        ids.setdefault(_zk(e.get("zone")), []).append(e["npc_id"])
    for e in ven:
        ids.setdefault(_zk(e.get("zone")), []).append(e["vendor_id"])
    out = {}
    for key in TOWNS:
        here = ids.get(_zk(key), [])
        inn = next((i for i in here if "inn" in svc.get(i, [])), None)
        fly = next((i for i in here if "flight" in svc.get(i, [])), None)
        node = next((n for n, v in nodes.items() if v["master"] == fly), None) if fly else None
        out[key] = (inn, fly, node)
    return out


def report():
    cov = coverage()
    bad = 0
    print(f"{'town':26}{'inn':<28}{'flight master':<30}node")
    for key, label in sorted(TOWNS.items(), key=lambda kv: kv[1]):
        inn, fly, node = cov[key]
        gap = not (inn and fly and node)
        bad += gap
        print(f"  {label:24}{inn or '-- MISSING --':<28}{fly or '-- MISSING --':<30}{node or '--'}")
    print(f"\n{len(TOWNS) - bad}/{len(TOWNS)} towns have an inn, a flight master and a node")
    return bad


def main():
    if "--check" in sys.argv:
        raise SystemExit(1 if report() else 0)

    ap = ROOT / "data/npcs/ambient_npcs.json"
    # RE-READ IMMEDIATELY BEFORE WRITING. Other passes append to this file, and a stale read here
    # silently drops whatever they added between the two.
    adata = json.loads(ap.read_text())
    have = {e["npc_id"] for e in adata["npcs"]}
    added = 0
    for i, (nid, (name, zone, x, y, race, gender, line)) in enumerate(NEW_NPCS.items()):
        if nid in have:
            continue
        adata["npcs"].append({"npc_id": nid, "name": name, "zone": zone, "x": x, "y": y,
                              "greeting": line, "gender": gender, "race": race,
                              "appearance_variant": (i * 7 + 2) % 24, "facing": "down"})
        added += 1
    ap.write_text(json.dumps(adata, indent=2) + "\n")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text())
    for nid in REGISTER_INN + [k for k in NEW_NPCS if k.endswith("_innkeeper")]:
        td["services"].setdefault(nid, [])
        if "inn" not in td["services"][nid]:
            td["services"][nid].append("inn")
    for nid in REGISTER_FLIGHT + [k for k in NEW_NPCS if k.endswith("_flight_master")]:
        td["services"].setdefault(nid, [])
        if "flight" not in td["services"][nid]:
            td["services"][nid].append("flight")
    for node_id, (name, zone, master, pos, cont) in NEW_NODES.items():
        td["flight_nodes"][node_id] = {"name": name, "zone": zone, "master": master,
                                       "pos": pos, "continent": cont}
    tp.write_text(json.dumps(td, indent=2) + "\n")

    print(f"ambient NPCs +{added}, services {len(td['services'])}, flight nodes {len(td['flight_nodes'])}\n")
    if report():
        raise SystemExit("a town is still short after the pass")


if __name__ == "__main__":
    main()
