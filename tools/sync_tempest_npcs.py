"""
Create and position every Tempest Isle NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_tempest_npcs.py

Who the people ARE lives in tools/tempest_npc_roster.py. WHERE they stand comes from the three
layout modules' NPC_POSITIONS and is never written here.

WHAT THIS FIXED WHEN IT WAS WRITTEN (14 Nov 2026):
  - the six people at Ashclaim Landing were recorded at coordinates from an older layout (the bosun
    at 38,102 when the jetty is at 84,64), so they stood in the wrong place;
  - the six people of the Ashen Reach had spots in the layout and no records at all;
  - nobody on the island sold anything: every shopkeeper was an ambient NPC with a greeting;
  - Cinderwharf had an innkeeper with no inn and a flight master with no flight point, so the town
    was missing from the teleport list and from the flight map;
  - the Ashclaim faction owned no zones, so no quest on the island could pay standing.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_tempest_shallows as TS  # noqa: E402
import tools.handbuilt_ashen_reach as AR       # noqa: E402
import tools.handbuilt_cinderwharf as CW       # noqa: E402
from tools import tempest_npc_roster as R      # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level)
ZONES = [
    ("tempest_shallows", TS, R.SHALLOWS_VENDORS, R.SHALLOWS_AMBIENT, 54),
    ("the_ashen_reach", AR, R.REACH_VENDORS, R.REACH_AMBIENT, 57),
    ("cinderwharf", CW, R.CINDERWHARF_VENDORS, R.CINDERWHARF_AMBIENT, 58),
]
INNS = ["ts_landing_cook", "cw_innkeeper"]
FLIGHT = ("cinderwharf", {"name": "Cinderwharf", "zone": "Cinderwharf",
                          "master": "cw_flight_master", "pos": [66, 122],
                          "continent": "eastern_kingdoms"})
FACTION = "the_ashclaim"
FACTION_ZONES = ["tempest_shallows", "the_ashen_reach", "cinderwharf"]
#: Only what the Ashclaim has a stake in (the faction's own note): the squatters in the gate,
#: rivals after the same wrecks, and the elementals breaking the Works. Wildlife pays nothing.
KILL_REP = {
    "Gate-Squatter Brawler": 10, "Gate-Squatter Ashpreacher": 12, "Wreckpicker Murloc": 8,
    "Stormscale Naga Raider": 10, "Scoria Fire Elemental": 8, "Ventborn Flame Spirit": 8,
    "Borrik the Unhoused": 60, "Wreck-Captain Vess'ira": 60, "Karrath the Ventlord": 60,
}
#: What is "behind" Quartermaster Vela. Existing consumables only; nothing here is new power.
REP_STOCK = R.REP_STOCK


def _check_variants(records):
    bad = []
    for (name, race, _gender, var, *_rest) in records:
        d = os.path.join("assets", "npcs", race)
        if not os.path.isdir(d):
            continue
        have = {int(m.group(1)) for n in os.listdir(d)
                if (m := re.fullmatch(rf"{race}_(\d+)", n))}
        if have and var not in have:
            bad.append(f"{name}: {race} variant {var}, art exists only for {min(have)}-{max(have)}")
    if bad:
        raise SystemExit("appearance variants with no art:\n  " + "\n  ".join(bad))


def main():
    vp, ap = Path("data/npcs/vendors.json"), Path("data/npcs/ambient_npcs.json")
    vd = json.loads(vp.read_text(encoding="utf-8"))
    ad = json.loads(ap.read_text(encoding="utf-8"))
    vendors, npcs = vd["vendors"], ad["npcs"]
    made = changed = 0

    for (zone, M, VEND, AMB, gear) in ZONES:
        _check_variants(list(VEND.values()) + list(AMB.values()))
        pos = M.NPC_POSITIONS
        missing = [k for k in list(VEND) + list(AMB) if k not in pos]
        spare = [k for k in pos if k not in VEND and k not in AMB]
        if missing or spare:
            raise SystemExit(f"{zone}: no spot for {missing}; spots with nobody {spare}")

        # someone who became a shopkeeper stops being an ambient record, and the reverse
        for r in [r for r in npcs if r["npc_id"] in VEND]:
            npcs.remove(r)
        for r in [r for r in vendors if r["vendor_id"] in AMB]:
            vendors.remove(r)
        by_vid = {r["vendor_id"]: r for r in vendors}
        by_nid = {r["npc_id"]: r for r in npcs}

        for vid, (name, race, gender, var, sells, sells_gear, greet) in VEND.items():
            greet = R.GREETINGS.get(vid, greet)
            sells, sells_gear = R.STOCK.get(vid, (sells, sells_gear))
            want = {"name": name, "zone": zone, "x": pos[vid][0], "y": pos[vid][1],
                    "tile_sprite": "npc", "sells": sells, "buys_from_player": True,
                    "faction": "neutral", "gear_level": gear, "sells_gear": sells_gear,
                    "race": race, "gender": gender, "appearance_variant": var, "greeting": greet}
            rec = by_vid.get(vid)
            if rec is None:
                vendors.append({"vendor_id": vid, **want})
                made += 1
            elif any(rec.get(k) != v for k, v in want.items()):
                rec.update(want)
                changed += 1

        for nid, (name, race, gender, var, greet) in AMB.items():
            greet = R.GREETINGS.get(nid, greet)
            want = {"name": name, "zone": zone, "x": pos[nid][0], "y": pos[nid][1],
                    "greeting": greet, "gender": gender, "race": race,
                    "appearance_variant": var, "facing": "down", **R.EXTRA.get(nid, {})}
            rec = by_nid.get(nid)
            if rec is None:
                npcs.append({"npc_id": nid, **want})
                made += 1
            elif any(rec.get(k) != v for k, v in want.items()):
                rec.update(want)
                changed += 1

        # ghosts: anybody recorded in this zone that the roster no longer names
        for r in [r for r in vendors if r.get("zone") == zone and r["vendor_id"] not in VEND]:
            vendors.remove(r)
        for r in [r for r in npcs if r.get("zone") == zone and r["npc_id"] not in AMB]:
            npcs.remove(r)

    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== beds and the bird =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text(encoding="utf-8"))
    svc = td["services"]
    for inn in INNS:
        svc[inn] = sorted(set(svc.get(inn, [])) | {"inn"})
    node_id, node = FLIGHT
    td["flight_nodes"][node_id] = node
    svc[node["master"]] = sorted(set(svc.get(node["master"], [])) | {"flight"})
    svc["ak_cinderwharf"] = ["set_exchange"]
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== the trainers teach, and the forge is a forge =====
    trp = Path("data/training/trainers.json")
    tr = json.loads(trp.read_text(encoding="utf-8"))
    for nid, extra in R.EXTRA.items():
        if "trains_class" in extra:
            tr["class_trainers"][nid] = extra["trains_class"]
        if "trains_profession" in extra:
            tr["profession_trainers"][nid] = extra["trains_profession"]
    trp.write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
    fp_ = Path("data/npcs/forges.json")
    fdoc = json.loads(fp_.read_text(encoding="utf-8"))
    fdoc["forges"] = [f for f in fdoc["forges"] if f["forge_id"] != "cinderwharf_forge"]
    fdoc["forges"].append({"forge_id": "cinderwharf_forge", "name": "Cinderwharf Forge",
                           "zone": "cinderwharf", "x": CW.FORGE[0], "y": CW.FORGE[1]})
    fp_.write_text(json.dumps(fdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== the Ashclaim owns its island =====
    fp = Path("data/factions/factions.json")
    fd = json.loads(fp.read_text(encoding="utf-8"))
    f = fd["factions"][FACTION]
    f["quest_rep"]["zones"] = FACTION_ZONES
    f["kill_rep"]["creatures"] = KILL_REP
    f["rewards"]["vendor_stock"] = REP_STOCK
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Tempest Isle: {made} records created, {changed} changed ({total} people), "
          f"{len(INNS)} inns, flight point at Cinderwharf, Ashclaim owns {len(FACTION_ZONES)} zones.")


if __name__ == "__main__":
    main()
