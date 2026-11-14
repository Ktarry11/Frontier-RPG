"""
Create and position every Arathi Highlands NPC and vendor in data/npcs/*.json. Idempotent.

    PYTHONPATH=. python3 tools/sync_arathi_npcs.py

Covers the three Arathi zones (32: 20 ambient, 12 vendors). The zones shipped with nobody in
them, so this CREATES records as well as moving them.

Who the people ARE lives in tools/arathi_npc_roster.py. WHERE they stand comes from each zone
module's NPC_POSITIONS and is never written here, so the layout stays the single source of truth
for a coordinate - the same reason the baker reads the layout's own fields instead of keeping a
copy of them.

Same asserts and same ghost-prune as sync_freewind_npcs.py, for the same reasons: a roster name
with no spot is a person who exists and cannot be found, a spot with no name is an empty tile the
player walks to for nothing, and a record the roster no longer names is a second copy of somebody
standing at their old coordinates. All three have happened in this project before.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_arathi_west as AW  # noqa: E402
import tools.handbuilt_arathi_central as AC  # noqa: E402
import tools.handbuilt_arathi_east as AE  # noqa: E402
from tools import arathi_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band, as it does everywhere else: Hillsbrad's 23-27 towns sit at 16 and
#: the Underdark's 33-40 cluster at 20-22, so 28-33 is 19, 33-37 is 21, 37-40 is 22. Saltspur is
#: a beachhead rather than a town, but it is the only shop in its band, so its shelves are not
#: thinned the way a logging camp's would be.
ZONES = [
    ("arathi_west", AW, R.WEST_VENDORS, R.WEST_AMBIENT, 19),
    ("arathi_central", AC, R.CENTRAL_VENDORS, R.CENTRAL_AMBIENT, 21),
    ("arathi_east", AE, R.EAST_VENDORS, R.EAST_AMBIENT, 22),
]


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
    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Arathi: {made} records created, {moved} moved ({total} people)")


if __name__ == "__main__":
    main()
