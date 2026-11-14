"""
Create and position every Hillsbrad NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_hillsbrad_npcs.py

Covers all three maps: Western Hillsbrad, Eastern Hillsbrad and Tarren Mill. Unlike
tools/sync_barrens_town_npcs.py, which only MOVES records that already exist, this one also creates them -
Hillsbrad shipped with zero NPCs in any of its maps, so there was nothing to move.

Who the people ARE lives in tools/hillsbrad_npc_roster.py. WHERE they stand comes from each zone module's
NPC_POSITIONS and is never written here, so the layout stays the single source of truth for a coordinate - the
same reason the baker reads the layout's own fields instead of keeping a copy.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_hillsbrad_east as HE  # noqa: E402
import tools.handbuilt_hillsbrad_west as HW  # noqa: E402
import tools.handbuilt_tarren_mill as TM  # noqa: E402
from tools import hillsbrad_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: gear_level tracks the band: the west is the 20-24 door into Hillsbrad, the east and the town run 23-27.
#: Brill, a 10-12 town, sits at 8 for comparison.
ZONES = [
    # were 14 / 16 / 16, under their own zones' bands (tools/overhaul_vendor_stock.py --check,
    # fixed 14 Nov 2026)
    ("western_hillsbrad", HW, R.WEST_VENDORS, R.WEST_AMBIENT, 23),
    ("eastern_hillsbrad", HE, R.EAST_VENDORS, R.EAST_AMBIENT, 24),
    ("tarren_mill", TM, R.TOWN_VENDORS, R.TOWN_AMBIENT, 24),
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
                                "faction": "forsaken" if race == "forsaken" else "neutral",
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

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Hillsbrad: {made} records created, {moved} moved ({total} people across 3 maps)")


if __name__ == "__main__":
    main()
