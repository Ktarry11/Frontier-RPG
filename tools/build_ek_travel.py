#!/usr/bin/env python3
"""Eastern Kingdoms flight network + innkeeper services (idempotent).

- Tags every flight node with a "continent" ("kalimdor" / "eastern_kingdoms").
  Flights only run between nodes on the same continent; the only road between
  continents is the Orgrimmar <-> Undercity zeppelin.
- Adds Forsaken bat handlers (flight masters) at Undercity, Brill, The Sepulcher
  and Silverpine South, and registers them (plus the Brill / Sepulcher innkeepers)
  in the travel "services" table.

Run from the repo root:  python3 tools/build_ek_travel.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAVEL = ROOT / "data" / "travel" / "travel_data.json"
AMBIENT = ROOT / "data" / "npcs" / "ambient_npcs.json"

# pos only needs to be consistent inside one network (flight cost = base + per_unit * distance)
EK_NODES = {
    "undercity": {"name": "Undercity", "zone": "Undercity", "master": "uc_flight_master", "pos": [0, 0]},
    "brill": {"name": "Brill", "zone": "Brill", "master": "brill_flight_master", "pos": [10, -32]},
    "sepulcher": {"name": "The Sepulcher", "zone": "The Sepulcher", "master": "sepulcher_flight_master",
                  "pos": [-24, 26]},
    "silverpine_south": {"name": "Silverpine South (Forsaken Rearguard)", "zone": "Silverpine South",
                         "master": "sp_south_flight_master", "pos": [-30, 58]},
}

# npc_id -> (name, zone slug, x, y, variant, gender, facing, greeting)
BAT_HANDLERS = {
    "uc_flight_master": ("Bat Handler Skrel", "Undercity", 128, 135, 4, "male", "left",
                         "The bats don't mind the smell down here. They're the only ones. Where to?"),
    "brill_flight_master": ("Bat Handler Mirren", "brill", 42, 45, 9, "female", "down",
                            "Fed, saddled and only mildly hungry for you. Name your destination."),
    "sepulcher_flight_master": ("Bat Handler Odo", "sepulcher", 38, 58, 12, "male", "down",
                                "Fly the Rearguard's route and you'll never see the Dalaran wall from the ground. Where to?"),
    "sp_south_flight_master": ("Bat Handler Veshka", "silverpine_south", 72, 49, 6, "female", "right",
                               "Forest roads are for the careless. Hold the straps and pick a roost."),
}

SERVICES = {
    "uc_flight_master": ["flight"],
    "brill_flight_master": ["flight"],
    "sepulcher_flight_master": ["flight"],
    "sp_south_flight_master": ["flight"],
    "brill_innkeeper": ["inn"],
    "sepulcher_innkeeper": ["inn"],
}


def main():
    t = json.loads(TRAVEL.read_text(encoding="utf-8"))
    for node in t["flight_nodes"].values():
        node.setdefault("continent", "kalimdor")
    for nid, node in EK_NODES.items():
        t["flight_nodes"][nid] = {**node, "continent": "eastern_kingdoms"}
    for k, v in SERVICES.items():
        t["services"][k] = v
    TRAVEL.write_text(json.dumps(t, indent=1) + "\n", encoding="utf-8")

    a = json.loads(AMBIENT.read_text(encoding="utf-8"))
    have = {n["npc_id"]: i for i, n in enumerate(a["npcs"])}
    for nid, (name, zone, x, y, var, gender, facing, greet) in BAT_HANDLERS.items():
        rec = {"npc_id": nid, "name": name, "zone": zone, "x": x, "y": y, "greeting": greet,
               "gender": gender, "race": "forsaken", "appearance_variant": var, "facing": facing}
        if nid in have:
            a["npcs"][have[nid]] = rec
        else:
            a["npcs"].append(rec)
    AMBIENT.write_text(json.dumps(a, indent=2) + "\n", encoding="utf-8")
    print("ok:", len(EK_NODES), "EK nodes,", len(BAT_HANDLERS), "bat handlers")


if __name__ == "__main__":
    main()
