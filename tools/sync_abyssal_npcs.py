"""
Create and position every Fourth Peg NPC and vendor in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_glittervein_npcs.py

The survey town on the Abyssal Sands (tools/handbuilt_fourth_peg.py): the eight who were in tents on the
northeast flat, trying to find out whether a road across this zone is possible, plus a wyvern-keeper and a gate
warden. Like the Saltwheel and Underdark
syncs and unlike the Barrens one, this CREATES records as well as moving them.

Who the people ARE lives in tools/abyssal_npc_roster.py. WHERE they stand comes from
handbuilt_fourth_peg.NPC_POSITIONS and is never written here, so the layout stays the single
source of truth for a coordinate.

The asserts are the useful part. Three of them:

  - the roster and the layout must name exactly the same people. A name with no spot is somebody
    who exists and cannot be found; a spot with no name is a tile the player walks to for nothing.
  - the cook gets the "inn" service. A dungeon doorway at the bottom of a forty-six-deep hole with
    no rest point is a cruelty, not a design.
  - EXACTLY ONE FLIGHT POINT. This used to assert there would be none, because Fourth Peg was a ten-person camp
    on a rock. It's a town now (Kyle, 16 Nov 2026: "an ACTUAL town"), with one inn and one wyvern, and the check
    holds it to one of each.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.npc_data_guard import report_extras, safe_update, may_write  # noqa: E402
import tools.handbuilt_fourth_peg as FP  # noqa: E402
from tools import abyssal_npc_roster as R  # noqa: E402

#: (zone key, layout module, vendors, ambient, vendor gear_level).
#: Steamwheedle (41-44) sits at 24 and Fourth Peg is 44-47, so it is one step above it -
#: and a step BELOW Lastwater at 26, because a survey camp on four carts does not out-stock the
#: outfitter at the bottom of the only crystal seam in the world.
ZONES = [
    # a town of its own now (tools/handbuilt_fourth_peg.py), so its people's zone is the town's
    ("fourth_peg", FP, R.ABYSSAL_VENDORS, R.ABYSSAL_AMBIENT, 25),
]

INN = "ab_cook"
FLIGHT = "ab_flight_master"
CAMP = "Fourth Peg"
#: the flight node (the flight map's pos is the world map, Tanaris's southwest, beside Steamwheedle Port's)
NODE = {"name": "Fourth Peg", "zone": "Fourth Peg", "master": FLIGHT, "pos": [104, 158], "continent": "kalimdor"}


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
    d = json.loads(Path(path).read_text(encoding="utf-8"))
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
                # RE-HOMED (16 Nov 2026): the camp became a town on its own map, so the town owns where they live.
                # npc_data_guard.may_write only lets a builder move x/y; the zone is set here on purpose, for
                # exactly this roster.
                if rec.get("zone") != zone:
                    rec["zone"] = zone
                    moved += 1
                for kk, vv in (("name", name), ("race", race), ("gender", gender),
                               ("appearance_variant", var), ("greeting", greet),
                               ("sells", sells), ("sells_gear", sells_gear), ("zone", zone)):
                    if rec.get(kk) != vv and may_write(rec, kk):
                        rec[kk] = vv
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
                # RE-HOMED (16 Nov 2026): the camp became a town on its own map, so the town owns where they live.
                # npc_data_guard.may_write only lets a builder move x/y; the zone is set here on purpose, for
                # exactly this roster.
                if rec.get("zone") != zone:
                    rec["zone"] = zone
                    moved += 1
                for kk, vv in (("name", name), ("race", race), ("gender", gender),
                               ("appearance_variant", var), ("greeting", greet)):
                    if rec.get(kk) != vv and may_write(rec, kk):
                        rec[kk] = vv
                        moved += 1

    # prune ghosts: anything in our zone the roster no longer names should not be standing there.
    # Trainers (ct_*, pt_*) belong to build_class_trainers / build_profession_trainers, never to us.
    for (zone, M, VEND, AMB, gear) in ZONES:
        keep_v, keep_a = set(VEND), set(AMB)
        ghosts_v = [r for r in vendors if r.get("zone") == zone and r["vendor_id"] not in keep_v]
        ghosts_a = [r for r in npcs if r.get("zone") == zone and r["npc_id"] not in keep_a
                    and not r["npc_id"].startswith(("ct_", "pt_"))]
        # Reported, never deleted (tools/npc_data_guard.py): a hidden seller, an Artifact Keeper or a
        # quest giver moved here by a later pass is not a ghost.
        report_extras([r.get("vendor_id") or r.get("npc_id") for r in ghosts_v + ghosts_a], zone)

    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ===== the bedrolls, and the bird that is not here =====
    tp = Path("data/travel/travel_data.json")
    td = json.loads(tp.read_text(encoding="utf-8"))
    svc, nodes = td["services"], td["flight_nodes"]

    before = list(svc.get(INN, []))
    svc[INN] = sorted(set(before) | {"inn"})
    inn_added = svc[INN] != before

    # THE WYVERN. This used to assert there would never be one ("a ten-person camp on a rock ... does not get a
    # wyvern"). Fourth Peg is a town now, and Kyle asked for one inn and one flight point (16 Nov 2026). A flight
    # point is a node PLUS a service: both are written here, and exactly one of each is checked for.
    svc[FLIGHT] = sorted(set(svc.get(FLIGHT, [])) | {"flight"})
    nodes["fourth_peg"] = dict(NODE)
    flighted = [k for k, v in svc.items() if k.startswith("ab_") and "flight" in v]
    nodes_here = [k for k, n in nodes.items() if n.get("zone") in (CAMP, "The Abyssal Sands")]
    if flighted != [FLIGHT] or nodes_here != ["fourth_peg"]:
        raise SystemExit(f"Fourth Peg should have exactly one flight point: services {flighted}, nodes {nodes_here}")

    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    total = sum(len(v) + len(a) for (_, _, v, a, _) in ZONES)
    print(f"Fourth Peg: {made} records created, {moved} moved ({total} people)"
          f"{', inn registered' if inn_added else ''}, one flight node.")


if __name__ == "__main__":
    main()
