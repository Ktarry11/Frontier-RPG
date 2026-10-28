"""
Create and position every Aspen Wilderness NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_aspen_npcs.py

Covers the open zone (13: 11 ambient, 2 vendors). The zone shipped with nobody in it, so this CREATES
records as well as moving them.

Who the people ARE lives in tools/aspen_npc_roster.py. WHERE they stand comes from the zone module's
NPC_POSITIONS and is never written here, so the layout stays the single source of truth for a coordinate -
the same reason the baker reads the layout's own fields instead of keeping a copy.

The asserts below are the useful part: the roster and the layout must name exactly the same people. A name
in the roster with no spot would be a person who exists and cannot be found; a spot with no name would be an
empty tile the player walks to for nothing. Both have happened before, so both are fatal here.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_aspen_wilderness as ASP  # noqa: E402
from tools import aspen_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band. Hillsbrad's 23-27 towns sit at 16 and the Underdark's 33-40 cluster at 20-22;
#: this zone runs 25-30, so 17 - and Longstand is a logging camp rather than a town, which is the other
#: reason its shelves are thin.
ZONES = [
    ("the_aspen_wilderness", ASP, R.ASPEN_VENDORS, R.ASPEN_AMBIENT, 17),
]


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
                                "faction": "horde",
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

    # PRUNE GHOSTS BEFORE WRITING.
    #
    # This sync adds records and moves them and never used to remove any, so every time somebody moved an
    # id between the ambient and vendor lists - or dropped one from the roster - the old record stayed in
    # the world. Freewind hit this first - it ended up with two fw_tanners, a vendor at the old coordinates
    # and an ambient at the new ones, both standing in the city. Anything in one of our zones that the roster
    # no longer names is a person who should not be there.
    #
    # Trainers (ct_*, pt_*) are owned by build_class_trainers / build_profession_trainers, not by this
    # roster, so they are never pruned here.
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
    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Aspen: {made} records created, {moved} moved ({total} people)")


if __name__ == "__main__":
    main()
