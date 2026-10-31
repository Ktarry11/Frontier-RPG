"""
Create and position every Fourth Peg NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_glittervein_npcs.py

Eight people in tents on the northeast flat of the Abyssal Sands, trying to find out
whether a road across this zone is possible. Like the Saltwheel and Underdark
syncs and unlike the Barrens one, this CREATES records as well as moving them.

Who the people ARE lives in tools/abyssal_npc_roster.py. WHERE they stand comes from
handbuilt_abyssal_sands.NPC_POSITIONS and is never written here, so the layout stays the single
source of truth for a coordinate.

The asserts are the useful part. Three of them:

  - the roster and the layout must name exactly the same people. A name with no spot is somebody
    who exists and cannot be found; a spot with no name is a tile the player walks to for nothing.
  - the cook gets the "inn" service. A dungeon doorway at the bottom of a forty-six-deep hole with
    no rest point is a cruelty, not a design.
  - NOBODY HERE GETS A FLIGHT POINT. Fourth Peg is a ten-person camp on a rock, and Kezzik in
    Steamwheedle has the standing line about who pays to feed a wyvern. This is the same assert
    Saltwheel carries, and it is here for the same reason: it is the kind of thing that gets added
    later by somebody being helpful, and the absence is the point.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_abyssal_sands as AB  # noqa: E402
from tools import abyssal_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: Steamwheedle (41-44) sits at 24 and Fourth Peg is 44-47, so it is one step above it -
#: and a step BELOW Lastwater at 26, because a survey camp on four carts does not out-stock the
#: outfitter at the bottom of the only crystal seam in the world.
ZONES = [
    ("the_abyssal_sands", AB, R.ABYSSAL_VENDORS, R.ABYSSAL_AMBIENT, 25),
]

INN = "ab_cook"
CAMP = "Fourth Peg"


def _load(path, key):
    d = json.loads(Path(path).read_text())
    return d, d[key]


def main():
    vd, vendors = _load("data/npcs/vendors.json", "vendors")
    ad, npcs = _load("data/npcs/ambient_npcs.json", "npcs")
    by_vid = {r["vendor_id"]: r for r in vendors}
    by_nid = {r["npc_id"]: r for r in npcs}
    made = moved = 0

    for (zone, M, VEND, AMB, gear) in ZONES:
        pos = M.NPC_POSITIONS
        missing = [k for k in list(VEND) + list(AMB) if k not in pos]
        spare = [k for k in pos if k not in VEND and k not in AMB]
        if missing:
            raise SystemExit(f"{zone}: roster names nobody the layout has a spot for: {missing}")
        if spare:
            raise SystemExit(f"{zone}: layout has spots with nobody to stand in them: {spare}")

        for vid, (name, race, gender, var, sells, sells_gear, greet) in VEND.items():
            x, y = pos[vid]
            rec = by_vid.get(vid)
            if rec is None:
                vendors.append({"vendor_id": vid, "name": name, "zone": zone, "x": x, "y": y,
                                "tile_sprite": "npc", "sells": sells, "buys_from_player": True,
                                "faction": "neutral", "gear_level": gear,
                                "sells_gear": sells_gear, "race": race, "gender": gender,
                                "appearance_variant": var, "greeting": greet})
                made += 1
            elif (rec["x"], rec["y"]) != (x, y):
                rec["x"], rec["y"] = x, y
                moved += 1

        for nid, (name, race, gender, var, greet) in AMB.items():
            x, y = pos[nid]
            rec = by_nid.get(nid)
            if rec is None:
                npcs.append({"npc_id": nid, "name": name, "zone": zone, "x": x, "y": y,
                             "greeting": greet, "gender": gender, "race": race,
                             "appearance_variant": var, "facing": "down"})
                made += 1
            elif (rec["x"], rec["y"]) != (x, y):
                rec["x"], rec["y"] = x, y
                moved += 1

    # prune ghosts: anything in our zone the roster no longer names should not be standing there.
    # Trainers (ct_*, pt_*) belong to build_class_trainers / build_profession_trainers, never to us.
    for (zone, M, VEND, AMB, gear) in ZONES:
        keep_v, keep_a = set(VEND), set(AMB)
        ghosts_v = [r for r in vendors if r.get("zone") == zone and r["vendor_id"] not in keep_v]
        ghosts_a = [r for r in npcs if r.get("zone") == zone and r["npc_id"] not in keep_a
                    and not r["npc_id"].startswith(("ct_", "pt_"))]
        for r in ghosts_v:
            vendors.remove(r)
        for r in ghosts_a:
            npcs.remove(r)
        if ghosts_v or ghosts_a:
            print(f"{zone}: pruned {len(ghosts_v) + len(ghosts_a)} stale record(s): "
                  f"{[r.get('vendor_id') or r.get('npc_id') for r in ghosts_v + ghosts_a]}")

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n")

    # ===== the bedrolls, and the bird that is not here =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text())
    svc, nodes = td["services"], td["flight_nodes"]

    before = list(svc.get(INN, []))
    svc[INN] = sorted(set(before) | {"inn"})
    inn_added = svc[INN] != before

    # a flight point is a node PLUS a service, so check for both: either one alone is somebody
    # halfway through adding one, and halfway is exactly how this gets in by accident.
    flighted = [k for k, v in svc.items() if k.startswith("ab_") and "flight" in v]
    nodes_here = [k for k, n in nodes.items() if n.get("zone") in (CAMP, "The Abyssal Sands")]
    if flighted or nodes_here:
        raise SystemExit(
            f"Fourth Peg has picked up a flight point - services {flighted}, nodes {nodes_here}. "
            f"It is a ten-person camp on a rock at the bottom of a sinkhole and it does not get a "
            f"wyvern. Remove it rather than relaxing this check.")

    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Fourth Peg: {made} records created, {moved} moved ({total} people)"
          f"{', inn registered' if inn_added else ''}, no flight node.")


if __name__ == "__main__":
    main()
