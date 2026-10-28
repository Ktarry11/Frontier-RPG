"""
Create and position every Freewind Post NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_freewind_npcs.py

Covers Freewind Post (11: 7 ambient, 4 vendors). The zone shipped with nobody in it, so this CREATES
records as well as moving them.

Who the people ARE lives in tools/freewind_npc_roster.py. WHERE they stand comes from the zone module's
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

import tools.handbuilt_freewind_post as FW  # noqa: E402
from tools import freewind_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band. Hillsbrad's 23-27 towns sit at 16 and the Underdark's 33-40 cluster at 20-22;
#: this zone runs 25-30, so 17 - and Longstand is a logging camp rather than a town, which is the other
#: reason its shelves are thin.
ZONES = [
    ("freewind_post", FW, R.FREEWIND_VENDORS, R.FREEWIND_AMBIENT, 19),
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

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n")
    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Freewind: {made} records created, {moved} moved ({total} people)")


if __name__ == "__main__":
    main()
