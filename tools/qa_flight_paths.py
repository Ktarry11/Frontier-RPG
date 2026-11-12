"""
Every flight node has a flight master you can find, land beside, and see on the map.

Kyle, 10 Nov: "some flight masters not showing on map (like zoram strand)."

Checking that turned up worse: two nodes (Hammerfall, Saltspur Landing) named the open zone
around the town instead of the town, and the flight screen only looked for masters among
ambient NPCs when those two are vendors - so flying to either failed outright.

For every node in travel_data.json:
  - its zone is a real map
  - its master resolves through find_flight_master (the lookup the flight screen uses)
  - the master stands inside that map, on an NPC tile
  - the map screen's own scan (ambient NPCs + vendors in the zone, services_for_npc) finds
    them as a flight master - which is what draws the icon
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from world.travel_manager import travel_data, services_for_npc, find_flight_master
    from world.ambient_npc_manager import get_ambient_npc_manager
    from world.zone_manager import ZoneManager

    zm = ZoneManager()
    nodes = travel_data()["flight_nodes"]
    if len(nodes) < 15:
        print(f"FAIL only {len(nodes)} flight nodes loaded")
        return 1
    bad = []
    for nid, node in nodes.items():
        zone = node.get("zone")
        entry = zm.zones.get(zone)
        if entry is None:
            bad.append(f"{nid}: zone {zone!r} is not a map")
            continue
        t = entry["tilemap"]
        master = find_flight_master(node, zm.vendor_manager)
        if master is None:
            bad.append(f"{nid}: master {node.get('master')!r} is not an NPC anywhere")
            continue
        if not (0 <= master.x < t.width and 0 <= master.y < t.height):
            bad.append(f"{nid}: master stands at ({master.x},{master.y}), off the "
                       f"{t.width}x{t.height} map of {zone}")
            continue
        if t.get_interaction(master.x, master.y) != "npc":
            bad.append(f"{nid}: no NPC tile at the master's position ({master.x},{master.y}) "
                       f"in {zone} - the flight would land on nobody")
        scanned = (list(get_ambient_npc_manager().get_npcs_in_zone(t.name))
                   + list(zm.vendor_manager.get_vendors_in_zone(t.name)))
        marked = [n for n in scanned if "flight" in services_for_npc(n)]
        if not any(n is master for n in marked):
            bad.append(f"{nid}: the map's scan of {zone} does not find the master as a flight "
                       f"master - no icon would be drawn")
    print(f"{len(nodes)} flight nodes checked")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print("flight paths OK - every node has a master you can land beside and see on the map.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
