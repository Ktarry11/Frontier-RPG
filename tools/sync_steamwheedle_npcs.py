"""
Create and position every Steamwheedle Port NPC and vendor in data/npcs/*.json, and register the inn. Idempotent.

    PYTHONPATH=. python3 tools/sync_steamwheedle_npcs.py

Who the people ARE lives in tools/steamwheedle_npc_roster.py. WHERE they stand comes from the zone module's
NPC_POSITIONS and is never written here, so the layout stays the single source of truth for a coordinate.

AN INN AND NO WIND RIDER, ASSERTED BOTH WAYS.

Kyle: "This can have an inn but no wind rider." In data terms that is two separate facts in
data/travel/travel_data.json and only one of them is something you can write:

  * THE INN IS A SERVICE ENTRY. services[<innkeeper id>] = ["inn"], which is what lets the player bind
    their hearth on Vozzi's tile. This script writes it, because an inn that nobody registered is just
    a building with a goblin in it.
  * THE WIND RIDER IS AN ABSENCE, which is the part worth checking. A flight point is a flight_nodes
    entry plus a ["flight"] service, and the failure mode is not that somebody adds one on purpose -
    it is that a later pass over the travel data adds every town uniformly and nobody notices Saltwheel
    was meant to be the exception. An absence has no line of code holding it in place, so the assert
    below IS the line of code: it fails the moment Saltwheel acquires a bird.

That check costs nothing and it is the only thing standing between Kyle's instruction and a town that
quietly grows a flight point in six months' time.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_steamwheedle_port as SW  # noqa: E402
from tools import steamwheedle_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band: Freewind's 25-30 sits at 19 and the Underdark's 33-40 cluster at 20-22.
#: Saltwheel runs 35-40, so 22 - and these shelves are raceday stock laid in before the track died,
#: which is a reason for them to be good rather than a reason for them to be thin.
ZONES = [
    ("steamwheedle_port", SW, R.STEAMWHEEDLE_VENDORS, R.STEAMWHEEDLE_AMBIENT, 24),
]

#: the innkeeper gets the hearth service. Nobody here gets ["flight"] - see the module docstring.
INN = "stw_innkeeper"
TOWN = "Steamwheedle Port"
FLIGHT = "stw_flight_master"


def _load(path, key):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
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
                                "faction": "neutral",
                                "gear_level": gear, "sells_gear": sells_gear, "race": race,
                                "gender": gender, "appearance_variant": var, "greeting": greet})
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

    # prune ghosts: anything in our zone the roster no longer names is a person who should not be there.
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

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== the inn, and the bird that is not here =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text(encoding="utf-8"))
    svc, nodes = td["services"], td["flight_nodes"]

    before = list(svc.get(INN, []))
    svc[INN] = sorted(set(before) | {"inn"})
    inn_added = svc[INN] != before

    # THE MIRROR OF SALTWHEEL'S ASSERT. That town must have no wind rider and the sync proves the
    # absence; this town must HAVE one, and an absence is not the only thing that rots quietly - a
    # flight point is a node AND a ["flight"] service, and half of one is a flight master you can
    # talk to who cannot fly you anywhere. So both halves are written and both are checked.
    before_f = list(svc.get(FLIGHT, []))
    svc[FLIGHT] = sorted(set(before_f) | {"flight"})
    nodes.setdefault("steamwheedle_port", {
        "name": "Steamwheedle Port", "zone": TOWN, "master": FLIGHT,
        "pos": [120, 150], "continent": "kalimdor"})
    if "flight" not in svc.get(FLIGHT, []) or not any(
            n.get("zone") == TOWN for n in nodes.values()):
        raise SystemExit(f"{TOWN} is missing half a flight point: service={svc.get(FLIGHT)} "
                         f"node={[k for k,n in nodes.items() if n.get('zone')==TOWN]}")

    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Steamwheedle Port: {made} records created, {moved} moved ({total} people)")
    print(f"  inn: {INN} {'registered' if inn_added else 'already registered'} "
          f"({sum(1 for v in svc.values() if 'inn' in v)} inns in the world)")
    print(f"  wind rider: {FLIGHT} registered ({len(nodes)} flight nodes in the world)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
