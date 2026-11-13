#!/usr/bin/env python3
"""Glittervein is finished: an inn, a flight point, and a dungeon with one way in.

    PYTHONPATH=. python3 tools/qa_glittervein_complete.py

Kyle, 13 Nov 2026: "ensure that glittervein is completed. It'll need an inn and a flight path. Then
ensure the dungeon only has one entrance but the second floor can bring you to the surface."
And 10 Nov, of the same dungeon: "i didnt mean that you can ALSO enter at the END of the dungeon
....the portal outside is one way."

SIX CLAIMS:
  1. LASTWATER HAS AN INN: a building on the map, an innkeeper registered for the hearth, standing
     where a player can reach him and not under the roof.
  2. LASTWATER HAS A FLIGHT POINT: a node, a ["flight"] service and a flight master on the map,
     on the same continent as Steamwheedle so there is somewhere to fly to.
  3. THE DUNGEON HAS ONE ENTRANCE: exactly one portal on the surface map leads underground, and
     it leads to the first floor (The Mother Vein).
  4. THE SECOND FLOOR IS ONLY REACHED FROM THE FIRST.
  5. THE SECOND FLOOR BRINGS YOU TO THE SURFACE, at the camp, on ground you can stand on.
  6. AND THAT WAY OUT IS ONE WAY: where it sets you down is not a door back in.
  7. THE HAUL ROAD IS PAINTED WHERE THE RAMP IS and nowhere else.
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

with contextlib.redirect_stdout(io.StringIO()):
    import numpy as np
    from tools import handbuilt_glittervein as G
    from tools import tirisfal_kit as T
    from world.portal_manager import PortalManager
    from world.npc_clearance import covered

SURFACE, FLOOR1, FLOOR2 = "Glittervein", "The Mother Vein", "The Cistern"


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        zone = T.build(G).zone
        pm = PortalManager()
    seen, q = {G.START}, deque([G.START])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < G.W and 0 <= n[1] < G.H and n not in seen and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)

    def beside(p):
        return any((p[0] + dx, p[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    def clear(nid):
        x, y = G.NPC_POSITIONS[nid]
        over = [lm["sprite_key"].split("/")[-1] for lm in zone.landmarks if covered(lm, x, y) > 0.5]
        if not beside((x, y)):
            bad.append(f"{nid} cannot be reached")
        if over:
            bad.append(f"{nid} is drawn under {over}")

    td = json.load(open("data/travel/travel_data.json"))
    drawn = [lm["sprite_key"] for lm in zone.landmarks]

    # 1
    if not any("_inn" in d and "assets/buildings" in d for d in drawn):
        bad.append("no inn building on the map")
    if "inn" not in td["services"].get("gv_innkeeper", []):
        bad.append("the innkeeper is not registered as an inn")
    clear("gv_innkeeper")

    # 2
    node = td["flight_nodes"].get("lastwater")
    if not node or node.get("master") != "gv_flight_master" or node.get("zone") != SURFACE:
        bad.append(f"flight node: {node}")
    elif node.get("continent") != td["flight_nodes"]["steamwheedle_port"]["continent"]:
        bad.append("the flight node is on a different continent from Steamwheedle")
    if "flight" not in td["services"].get("gv_flight_master", []):
        bad.append("the flight master has no flight service")
    if "gv_flight_master" not in G.NPC_POSITIONS:
        bad.append("the flight master is not on the map")
    else:
        clear("gv_flight_master")
    npcs = {n["npc_id"]: n for n in json.load(open("data/npcs/ambient_npcs.json"))["npcs"]}
    rec = npcs.get("gv_flight_master")
    if not rec or (rec["x"], rec["y"]) != G.NPC_POSITIONS.get("gv_flight_master"):
        bad.append("the flight master's record is missing or filed somewhere else")

    # 3-6
    def doors(z):
        return {p: pm.get_destination(z, *p) for p in pm.get_portal_positions(z)}

    def dest_zone(d):
        return d[0] if d else None

    down = {p: d for p, d in doors(SURFACE).items() if dest_zone(d) in (FLOOR1, FLOOR2)}
    if len(down) != 1 or dest_zone(next(iter(down.values()))) != FLOOR1:
        bad.append(f"ways into the dungeon from the surface: {down}")
    into_f2 = [(z, p) for z in pm._links for p, d in doors(z).items() if dest_zone(d) == FLOOR2]
    if {z for z, _p in into_f2} != {FLOOR1}:
        bad.append(f"the second floor is entered from {into_f2}")
    up = [d for d in doors(FLOOR2).values() if dest_zone(d) == SURFACE]
    if len(up) != 1:
        bad.append(f"the second floor has {len(up)} ways to the surface")
    else:
        ax, ay = up[0][1], up[0][2]
        if not beside((ax, ay)):
            bad.append(f"the way out sets you down at ({ax},{ay}), which cannot be stood on")
        sz = zone.get_subzone_at(ax, ay)
        if not sz or sz["name"] != "Lastwater":
            bad.append(f"the way out surfaces in {sz and sz['name']}, not at the camp")
        near = [p for p in doors(SURFACE) if abs(p[0] - ax) <= 1 and abs(p[1] - ay) <= 1]
        if near:
            bad.append(f"the way out sets you down on a door back in: {near}")

    # 7
    ys, xs = np.mgrid[0:G.H, 0:G.W]
    lane = G._ramp_lane(xs + 0.5, ys + 0.5)
    _r, _rc, t = G._spiral_geom(xs + 0.5, ys + 0.5)
    stray = int((lane & ~((t > 0) & (t < 1))).sum())
    if stray or lane.sum() > 900:
        bad.append(f"the haul road is painted off the ramp: {stray} stray tiles, {int(lane.sum())} in all")

    print(f"inn and flight point at Lastwater; {len(down)} way in, {len(up)} way out; "
          f"haul road {int(lane.sum())} tiles")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nGlittervein OK - an inn, a flight point, one way into the dungeon and one way back up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
