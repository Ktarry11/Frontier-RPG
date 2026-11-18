#!/usr/bin/env python3
"""Trainers, vendors, innkeepers and flight masters stand in towns.

    PYTHONPATH=. python3 tools/qa_service_npcs_in_towns.py

Backlog, "NPCs into towns, part two": quest givers meet the 70/30 rule (tools/qa_quest_hubs.py), but the rest of a
town's people (trainers, vendors, innkeepers) had no check, so one could end up standing alone in the wild. Measured
18 Nov 2026: of 174 service NPCs none is, so this is the guard that keeps it that way.

A service NPC passes if it stands
  1. on a town map: any map with an innkeeper on it (data/travel/travel_data.json), or a class trainer (a starting
     valley like the Valley of Trials is one camp end to end), or a hub in qa_quest_hubs.REGIONS;
  2. or inside one of the camps qa_quest_hubs.REGIONS marks inside a bigger map (within half again its radius);
  3. or among at least three other people (anyone: quest givers, guards, trainers) within 12 tiles: a camp of its own,
     like a starting village.
"""
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

CLUSTER_RADIUS = 12
CLUSTER_SIZE = 4         # counting itself


def main():
    import qa_quest_hubs as QH
    from world.zone_keys import zone_key
    hubs, camps = set(), {}
    for _r, (_qz, hz, inside) in QH.REGIONS.items():
        hubs |= set(hz)
        for z, pts in inside.items():
            camps.setdefault(z, []).extend(pts)
    services = json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))["services"]
    npcs = {}
    for f in glob.glob(str(ROOT / "data/npcs/*.json")):
        def walk(o):
            if isinstance(o, dict):
                if o.get("npc_id") and o.get("zone") is not None:
                    npcs.setdefault(o["npc_id"], o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(json.loads(Path(f).read_text(encoding="utf-8")))
    towns = set(hubs)
    for nid, kinds in services.items():
        if "inn" in kinds and nid in npcs:
            towns.add(zone_key(npcs[nid]["zone"]))
    towns |= {zone_key(o["zone"]) for nid, o in npcs.items() if nid.startswith("ct_")}

    role = {}
    for nid in npcs:
        if nid.startswith("pt_") or "trainer" in nid:
            role[nid] = "trainer"
    for nid, kinds in services.items():
        if nid in npcs:
            role[nid] = "/".join(kinds)
    vend = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))
    vl = vend.get("vendors", vend)
    for v in (vl.values() if isinstance(vl, dict) else vl):
        if isinstance(v, dict) and v.get("npc_id"):
            role.setdefault(v["npc_id"], "vendor")

    placed = [(nid, zone_key(npcs[nid]["zone"]), npcs[nid].get("x"), npcs[nid].get("y")) for nid in role if nid in npcs]
    bad, where = [], {"town": 0, "camp": 0, "cluster": 0}
    for nid, z, x, y in placed:
        if z in towns:
            where["town"] += 1
            continue
        if x is not None and any(abs(x - cx) + abs(y - cy) <= r * 1.5 for cx, cy, r in camps.get(z, [])):
            where["camp"] += 1
            continue
        near = sum(1 for o in npcs.values() if zone_key(o.get("zone") or "") == z and o.get("x") is not None
                   and x is not None and abs(o["x"] - x) + abs(o["y"] - y) <= CLUSTER_RADIUS)
        if near >= CLUSTER_SIZE:
            where["cluster"] += 1
            continue
        bad.append(f"{role[nid]} {nid} ({npcs[nid].get('name')}) stands alone on {z} at ({x},{y})")
    print(f"{len(placed)} service NPCs: {where}")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:20]:
            print("  ", b)
        return 1
    print("service NPCs OK - every trainer, vendor and innkeeper stands in a town or a camp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
