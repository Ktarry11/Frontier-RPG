"""The Teleport menu's list of towns.

Kyle, 13 Nov 2026: "change that 'stuck' option into a fast teleport. Basically you open it and it
lets me teleport to any town. So I don't need to run." It replaces the old Unstuck button, which
only ever went to Razor Hill.

WHAT COUNTS AS A TOWN: anywhere with an innkeeper (data/travel/travel_data.json, services "inn").
Every town must have an inn (standing rule), so the list keeps itself up to date: add an inn and
the place appears here. You land on the tile in front of the innkeeper.
"""
import json
from pathlib import Path

from world.zone_keys import zone_key

_DATA = Path(__file__).parent.parent / "data"

#: Camps that sit inside an open zone and have no flight point to borrow a name from.
_NAMES = {"abyssal_sands": "Fourth Peg", "tempest_shallows": "Ashclaim Landing"}
#: Continent for towns with no flight point to read it from.
_CONTINENTS = {"sepulcher": "eastern_kingdoms", "tempest_shallows": "eastern_kingdoms"}
CONTINENT_TITLES = {"kalimdor": "Kalimdor", "eastern_kingdoms": "Eastern Kingdoms"}


def destinations(zone_manager):
    """[{label, zone, x, y, continent}], sorted by continent then name. `zone` is the display
    name ZoneManager.transition_to_zone wants."""
    travel = json.loads((_DATA / "travel" / "travel_data.json").read_text(encoding="utf-8"))
    inns = {npc for npc, services in travel.get("services", {}).items() if "inn" in services}
    nodes = {zone_key(n["zone"]): n for n in travel.get("flight_nodes", {}).values()}
    display = {zone_key(name): name for name in zone_manager.zones}

    people = []
    for fname, id_key in (("vendors.json", "vendor_id"), ("ambient_npcs.json", "npc_id")):
        doc = json.loads((_DATA / "npcs" / fname).read_text(encoding="utf-8"))
        for value in doc.values():
            if isinstance(value, list):
                people += [(r, id_key) for r in value if isinstance(r, dict)]

    out, seen = [], set()
    for rec, id_key in people:
        if rec.get(id_key) not in inns:
            continue
        key = zone_key(rec["zone"])
        if key not in display or key in seen:
            continue
        seen.add(key)
        tilemap = zone_manager.zones[display[key]]["tilemap"]
        node = nodes.get(key)
        if getattr(tilemap, "is_town", False) or node is None:
            label = _NAMES.get(key, display[key])
        else:
            label = node["name"]                      # a camp inside an open zone: use its own name
        continent = (node or {}).get("continent") or _CONTINENTS.get(key, "kalimdor")
        out.append({"label": label, "zone": display[key], "x": rec["x"], "y": rec["y"] + 1,
                    "continent": continent})
    out.sort(key=lambda d: (d["continent"] != "kalimdor", d["label"].replace("The ", "")))
    return out
