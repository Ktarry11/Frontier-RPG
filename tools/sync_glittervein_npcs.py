"""
Create and position every Lastwater NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_glittervein_npcs.py

Ten people on the isle at the bottom of the Glittervein cenote. Like the Saltwheel and Underdark
syncs and unlike the Barrens one, this CREATES records as well as moving them.

Who the people ARE lives in tools/glittervein_npc_roster.py. WHERE they stand comes from
handbuilt_glittervein.NPC_POSITIONS and is never written here, so the layout stays the single
source of truth for a coordinate.

The asserts are the useful part. Three of them:

  - the roster and the layout must name exactly the same people. A name with no spot is somebody
    who exists and cannot be found; a spot with no name is a tile the player walks to for nothing.
  - the cook gets the "inn" service. A dungeon doorway at the bottom of a forty-six-deep hole with
    no rest point is a cruelty, not a design.
  - NOBODY HERE GETS A FLIGHT POINT. Lastwater is a ten-person camp on a rock, and Kezzik in
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

import tools.handbuilt_glittervein as GV  # noqa: E402
from tools import glittervein_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: Steamwheedle (41-44) sits at 24. This is 46-49 and it is the last outfitter before the dungeon,
#: so it is a step above - and the crystal cutter is the only source of magic resistance in the
#: game, which is the whole reason the band withheld it until now.
ZONES = [
    ("glittervein", GV, R.GLITTERVEIN_VENDORS, R.GLITTERVEIN_AMBIENT, 26),
]

INN = "gv_innkeeper"
FLIGHT = "gv_flight_master"
CAMP = "Lastwater"


#: Appearance variants are art directories, not free integers: assets/npcs/<race>/<race>_<n>/.
#: Three of these shipped at 25 and 26 when the goblin sheet stops at 24, which does not crash -
#: the NPC just renders as whatever the loader falls back to, and nobody notices in a diff.
def _check_variants(records):
    import os, re as _re
    bad = []
    for (name, race, _gender, var, *_rest) in records:
        d = os.path.join("assets", "npcs", race)
        if not os.path.isdir(d):
            continue
        have = {int(m.group(1)) for n in os.listdir(d)
                if (m := _re.fullmatch(rf"{race}_(\d+)", n))}
        if have and var not in have:
            bad.append(f"{name}: {race} variant {var}, but art exists only for "
                       f"{min(have)}-{max(have)}")
    if bad:
        raise SystemExit("appearance variants with no art:\n  " + "\n  ".join(bad))


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
        _check_variants(list(VEND.values()) + list(AMB.values()))
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
            else:
                # THE ROSTER IS THE SOURCE OF TRUTH FOR WHO THEY ARE, not just where they stand.
                # This only moved x/y, so correcting three appearance variants in the roster
                # changed nothing at all and the sync cheerfully reported "0 moved".
                if (rec["x"], rec["y"]) != (x, y):
                    rec["x"], rec["y"] = x, y
                    moved += 1
                for kk, vv in (("name", name), ("race", race), ("gender", gender),
                               ("appearance_variant", var), ("greeting", greet),
                               ("sells_gear", sells_gear)):
                    if rec.get(kk) != vv:
                        rec[kk] = vv
                        moved += 1
                # STOCK IS ADDED TO, NEVER REPLACED. The shelf on file has been tiered to the
                # vendor's level by tools/overhaul_vendor_stock.py since this roster was written;
                # writing the roster's list back over it would put level-30 potions in a
                # level-48 camp.
                extra = [i for i in sells if i not in rec["sells"]]
                if extra:
                    rec["sells"] = extra + rec["sells"]
                    moved += 1

        for nid, (name, race, gender, var, greet) in AMB.items():
            x, y = pos[nid]
            rec = by_nid.get(nid)
            if rec is None:
                npcs.append({"npc_id": nid, "name": name, "zone": zone, "x": x, "y": y,
                             "greeting": greet, "gender": gender, "race": race,
                             "appearance_variant": var, "facing": "down"})
                made += 1
            else:
                if (rec["x"], rec["y"]) != (x, y):
                    rec["x"], rec["y"] = x, y
                    moved += 1
                for kk, vv in (("name", name), ("race", race), ("gender", gender),
                               ("appearance_variant", var), ("greeting", greet)):
                    if rec.get(kk) != vv:
                        rec[kk] = vv
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

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2) + "\n")   # this file keeps its dashes escaped
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n")

    # ===== the inn and the flight point =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text())
    svc, nodes = td["services"], td["flight_nodes"]

    before = list(svc.get(INN, []))
    svc[INN] = sorted(set(before) | {"inn"})
    inn_added = svc[INN] != before

    # LASTWATER HAS A FLIGHT POINT NOW. Kyle, 13 Nov 2026: "It'll need an inn and a flight path."
    # This script used to refuse to run if the camp had one ("it does not get a wyvern"), which
    # was the right check for the instruction of the day and is the wrong one now. A flight point
    # is a node AND a ["flight"] service; half of one is a flight master who cannot fly you
    # anywhere, so both are written and both are checked.
    svc[FLIGHT] = sorted(set(svc.get(FLIGHT, [])) | {"flight"})
    nodes.setdefault("lastwater", {
        "name": "Lastwater", "zone": "Glittervein", "master": FLIGHT,
        "pos": [118, 172], "continent": "kalimdor"})
    if "flight" not in svc[FLIGHT] or not any(n.get("master") == FLIGHT for n in nodes.values()):
        raise SystemExit("Lastwater is missing half a flight point")

    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Lastwater: {made} records created, {moved} moved ({total} people)"
          f"{', inn registered' if inn_added else ''}; flight point: {FLIGHT} at Lastwater.")


if __name__ == "__main__":
    main()
