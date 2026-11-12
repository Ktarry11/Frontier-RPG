"""
Gathering nodes do not spawn in settlements.

Kyle, 10 Nov: "gatherables shouldn't spawn in towns."

A town with its own map was already excluded. A settlement INSIDE an open zone - a camp, a
crossroads, a quest hub - was not, because nothing told the node roller it was there.

For every open zone with a node pool, enter it through the real ZoneManager 8 times and check
every node that spawned:
  - none within NPC_CLEARANCE of an NPC
  - none within SETTLEMENT_RADIUS of a cluster of SETTLEMENT_NPCS or more
  - none inside a subzone flagged safe
and that zones still GET nodes - a rule that quietly empties a zone is its own bug.

Rolled against each zone's tile grid without entering it: entering loads the baked art, and
35 zones of that runs the box out of memory.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from world.zone_manager import ZoneManager
    from world.gathering_manager import get_gathering_node_manager, _zk

    zm = ZoneManager()
    g = get_gathering_node_manager()
    pooled = [z for z in zm.zones if _zk(z) in g.node_pools]
    if len(pooled) < 20:
        print(f"FAIL only {len(pooled)} zones with node pools matched - the rig is off")
        return 1
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]

    bad, empty, with_camps, total = [], [], 0, 0
    for zone in pooled:
        # The tilemap straight from the manager, NOT transition_to_zone: entering a zone loads
        # its baked art, and 35 zones of that is what ran the box out of memory. Nodes are
        # rolled against the tile grid, which is all this needs. NPC tiles are already on it -
        # ZoneManager stamps them at construction.
        t = zm.zones[zone]["tilemap"]
        if getattr(t, "is_town", False):
            continue
        npcs = [(x, y) for y, row in enumerate(t.interaction_layer)
                for x, kind in enumerate(row) if kind == "npc"]
        safe = {k for k, sz in enc.get(zone, {}).get("subzones", {}).items()
                if isinstance(sz, dict) and sz.get("safe")}
        clustered = any(sum(1 for (ax, ay) in npcs
                            if max(abs(ax - nx), abs(ay - ny)) <= g.SETTLEMENT_RADIUS)
                        >= g.SETTLEMENT_NPCS for (nx, ny) in npcs)
        with_camps += 1 if clustered else 0
        seen = 0
        for _ in range(8):
            g.populate(t, zone)
            for node in g.active_nodes:
                seen += 1
                dists = [max(abs(nx - node.x), abs(ny - node.y)) for (nx, ny) in npcs]
                if any(d <= g.NPC_CLEARANCE for d in dists):
                    bad.append(f"{zone}: {node.material_id} at ({node.x},{node.y}) is beside an NPC")
                elif sum(1 for d in dists if d <= g.SETTLEMENT_RADIUS) >= g.SETTLEMENT_NPCS:
                    bad.append(f"{zone}: {node.material_id} at ({node.x},{node.y}) is inside a camp")
                sz = t.get_subzone_at(node.x, node.y)
                if sz and sz.get("table_key") in safe:
                    bad.append(f"{zone}: {node.material_id} at ({node.x},{node.y}) is in the "
                               f"safe subzone {sz['table_key']}")
        total += seen
        if seen == 0:
            empty.append(zone)
        g.clear()

    print(f"{len(pooled)} zones with node pools, {with_camps} of them contain a camp, "
          f"{total} nodes rolled")
    if with_camps == 0:
        print("FAIL no zone has an NPC cluster - the rig is not seeing NPC tiles")
        return 1
    if empty:
        print(f"FAIL {len(empty)} zone(s) rolled no nodes at all: {empty}")
        return 1
    if bad:
        print(f"FAIL {len(bad)} node(s) in a settlement:")
        for b in bad[:15]:
            print("  ", b)
        return 1
    print("nodes OK - none beside an NPC, in a camp, or in a safe subzone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
