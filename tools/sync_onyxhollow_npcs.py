"""
Create and position every Onyxhollow NPC and vendor in data/npcs/*.json; register the inn, the one
trainer and the forge. Idempotent.

    PYTHONPATH=. python3 tools/sync_onyxhollow_npcs.py

Who the people ARE lives in tools/onyxhollow_npc_roster.py. WHERE they stand comes from the zone
module's NPC_POSITIONS and is never written here.

Kyle, 13 Nov 2026: "There wont be a flight master but this can have an inn" and "innkeeper for
hearth, level appropriate shops, this can be more of a mining town and Blacksmithing."

  * THE INN is services[oh_innkeeper] = ["inn"] in data/travel/travel_data.json - what lets a
    player bind their hearth here.
  * NO FLIGHT MASTER is an absence, so it is asserted: this fails if Onyxhollow ever has a flight
    node or a ["flight"] service (same check, same reason, as tools/sync_saltwheel_npcs.py).
  * ONE TRAINER, mining and blacksmithing, and A FORGE beside the smithy.
  * SHOP STOCK is tiered afterwards by tools/overhaul_vendor_stock.py from each vendor's
    gear_level (52), which is what makes it level appropriate.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_onyxhollow as OH  # noqa: E402
from tools import onyxhollow_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band: Freewind's 25-30 sits at 19 and the Underdark's 33-40 cluster at 20-22.
#: Saltwheel runs 35-40, so 22 - and these shelves are raceday stock laid in before the track died,
#: which is a reason for them to be good rather than a reason for them to be thin.
import tools.handbuilt_black_strand as BS  # noqa: E402

ZONES = [
    ("onyxhollow", OH, R.ONYXHOLLOW_VENDORS, R.ONYXHOLLOW_AMBIENT, 52),
    # the three people outside the gate. No vendors: the shops are in town.
    ("the_black_strand", BS, {}, R.BLACK_STRAND_AMBIENT, 52),
]

#: the innkeeper gets the hearth service. Nobody here gets ["flight"] - see the module docstring.
INN = "oh_innkeeper"
TOWN = "Onyxhollow"
TRAINER = "oh_forgemaster"
TRADES = ["mining", "blacksmithing", "jewelcrafting"]   # jewelcrafting joined the forge, 14 Nov 2026
FORGE_ID = "onyxhollow_forge"


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
            if rec is not None:
                rec["name"], rec["greeting"] = name, greet     # the roster owns the words
                # ...and anything the roster stocks that the shelf lacks. Added at the FRONT and
                # nothing removed, so the tiering overhaul_vendor_stock did is left alone.
                rec["sells"] = [i for i in sells if i not in rec["sells"]] + rec["sells"]

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
            if rec is not None:
                rec["name"], rec["greeting"] = name, greet

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

    # THE ONE TRAINER. He is this roster's person, not a pt_* row, so the town teaches exactly its
    # two trades and tools/build_profession_trainers.py (which keeps non-pt_ entries) leaves him be.
    by_nid = {r["npc_id"]: r for r in npcs}
    by_nid[TRAINER]["trains_profession"] = list(TRADES)
    trp = Path("data/training/trainers.json")
    tr = json.loads(trp.read_text(encoding="utf-8"))
    tr["profession_trainers"][TRAINER] = list(TRADES)
    trp.write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")

    # THE FORGE. A smithing town with nowhere to smith would be a joke at its own expense.
    fp = Path("data/npcs/forges.json")
    fd = json.loads(fp.read_text(encoding="utf-8"))
    fx, fy = OH.FORGE
    rec = next((f for f in fd["forges"] if f["forge_id"] == FORGE_ID), None)
    if rec is None:
        fd["forges"].append({"forge_id": FORGE_ID, "name": "Onyxhollow Forge", "zone": "onyxhollow",
                             "x": fx, "y": fy})
    else:
        rec["x"], rec["y"] = fx, fy
    fp.write_text(json.dumps(fd, indent=2) + "\n", encoding="utf-8")

    # ensure_ascii: this file stores its em dashes escaped, and writing them raw rewrites five
    # greetings that belong to other towns.
    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2) + "\n", encoding="utf-8")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== the inn, and the bird that is not here =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text(encoding="utf-8"))
    svc, nodes = td["services"], td["flight_nodes"]

    before = list(svc.get(INN, []))
    svc[INN] = sorted(set(before) | {"inn"})
    inn_added = svc[INN] != before

    # the assert that holds Kyle's instruction in place. A flight point is a node plus a service, so
    # check for both: either one alone is somebody halfway through adding one.
    flighted = [k for k, v in svc.items() if k.startswith("oh_") and "flight" in v]
    nodes_here = [k for k, n in nodes.items() if n.get("zone") == TOWN]
    if flighted or nodes_here:
        raise SystemExit(f"{TOWN} has a flight master and is not supposed to: "
                         f"services={flighted} flight_nodes={nodes_here}")

    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Onyxhollow: {made} records created, {moved} moved ({total} people)")
    print(f"  inn: {INN} {'registered' if inn_added else 'already registered'} "
          f"({sum(1 for v in svc.values() if 'inn' in v)} inns in the world)")
    print(f"  flight master: none, as specified ({len(nodes)} flight nodes, none in {TOWN})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
