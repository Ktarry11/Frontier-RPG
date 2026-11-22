#!/usr/bin/env python3
"""Townsfolk: the people who live in a town and aren't there to hand you anything.

    PYTHONPATH=. python3 tools/build_townsfolk.py            # check only
    PYTHONPATH=. python3 tools/build_townsfolk.py --write    # place them and write data/npcs/ambient_npcs.json

Kyle, 21 Nov 2026: "Brrrrrroooooooooooooo why is a captial so fucking empty? And everyone is in two districts", then
"we need towns as hubs...POPULATED towns....not wastelands", and "a lot of towns you make have like.... only quest givers
or like 3NPCs in a town...they dont feel a live, just quest givers or vendors, we need more life".

Each town's people live in tools/townsfolk/<town>.py as PEOPLE = [(npc_id, name, race, gender, district, greeting)].
The district is a subzone name on the town's map, and this script finds each person a tile in it: walkable, reachable
from the town's way in, off every road-blocking prop, door and arrival tile, and as far from everyone already standing
there as it can manage, so a district fills out instead of bunching. A person already placed keeps their tile while
it's still good. Looks are picked from the race's drawn looks by a hash of the id, so they're stable across runs.

Nothing here gives a quest, sells or trains. Greetings are held to the voice bar (no dashes, no one- or two-word
sentences, contractions).
"""
import contextlib
import collections
import hashlib
import importlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from world.zone_keys import zone_key                 # noqa: E402

#: town module (tools/townsfolk/<stem>.py) -> the map's display name
TOWNS = {
    "aurelion": "Aurelion",
    "timbermaw_hold": "Timbermaw Hold",
    "great_settlement": "The Great Settlement",
    "brill": "Brill",
    "undercity": "Undercity",
    "halcyon_rest": "Halcyon Rest",
    "keelstone": "Keelstone",
    "dawnspear_wreck": "Dawnspear Wreck",
}
SPACING = 3          # nobody stands closer than this to anyone else, if the district has room


def _look(race, gender, nid):
    from world.race_registry import get_gender, look_is_missing
    g = get_gender(race, gender)
    places = [i for i in range(len(g.variants) if g else 0) if not look_is_missing(race, gender, i)]
    if not places:
        return 0
    h = int(hashlib.md5(nid.encode()).hexdigest(), 16)
    return places[h % len(places)]


def _reach(z, portals):
    seen, todo = set(), []
    for p in portals:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (p[0] + dx, p[1] + dy)
            if 0 <= q[0] < z.width and 0 <= q[1] < z.height and z.is_walkable(*q):
                seen.add(q)
                todo.append(q)
    while todo:
        x, y = todo.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and 0 <= nx < z.width and 0 <= ny < z.height and z.is_walkable(nx, ny):
                seen.add((nx, ny))
                todo.append((nx, ny))
    return seen


def place(z, people, taken, existing_pos):
    """{npc_id: (x, y)} for every person, or raises with the ones that wouldn't fit."""
    portals = [(x, y) for y in range(z.height) for x in range(z.width)
               if z.interaction_layer[y][x] in ("portal", "boat", "link")]
    reach = _reach(z, portals)
    subs = {s["name"]: s for s in z.subzones}
    out, missing = {}, []
    occupied = list(taken)

    # never standing on a building's picture (tools/qa_npcs_clear_of_props.py holds that at zero)
    under = set()
    for lm in z.landmarks:
        if "buildings/" in str(lm.get("sprite_key", "")):
            for yy in range(lm["anchor_y"], lm["anchor_y"] + lm["height_tiles"]):
                for xx in range(lm["anchor_x"], lm["anchor_x"] + lm["width_tiles"]):
                    under.add((xx, yy))

    def good(x, y):
        if (x, y) in under:
            return False
        if (x, y) not in reach or z.collision_layer[y][x] is not None or z.interaction_layer[y][x] is not None:
            return False
        if any(abs(x - px) <= 3 and abs(y - py) <= 3 for px, py in portals):
            return False
        return True

    for nid, _name, _race, _g, district, _greet in people:
        s = subs.get(district)
        if s is None:
            missing.append(f"{nid}: no district called {district!r} on {z.name} ({sorted(subs)})")
            continue
        old = existing_pos.get(nid)
        if old and good(*old) and s["x"] <= old[0] < s["x"] + s["w"] and s["y"] <= old[1] < s["y"] + s["h"] \
                and all(max(abs(old[0] - ox), abs(old[1] - oy)) >= 2 for ox, oy in occupied):
            out[nid] = old
            occupied.append(old)
            continue
        best, best_d = None, -1
        h = int(hashlib.md5(nid.encode()).hexdigest(), 16)
        for y in range(s["y"], s["y"] + s["h"]):
            for x in range(s["x"], s["x"] + s["w"]):
                if not (0 <= x < z.width and 0 <= y < z.height) or not good(x, y):
                    continue
                d = min((max(abs(x - ox), abs(y - oy)) for ox, oy in occupied), default=99)
                d = min(d, 12) * 1000 + ((x * 31 + y * 17 + h) % 997)     # spread first, then a stable shuffle
                if d > best_d:
                    best, best_d = (x, y), d
        if best is None or best_d < 2000:
            missing.append(f"{nid}: no free tile in {district} on {z.name}")
            continue
        out[nid] = best
        occupied.append(best)
    if missing:
        raise SystemExit("couldn't place:\n  " + "\n  ".join(missing))
    return out


def problems(stem, people, known_ids):
    from build_tempest_quests import voice_problems
    bad, seen = [], set()
    for row in people:
        if len(row) != 6:
            bad.append(f"{stem}: bad row {row[:2]}")
            continue
        nid, name, race, gender, district, greet = row
        if nid in seen:
            bad.append(f"{nid}: listed twice")
        seen.add(nid)
        if nid in known_ids:
            bad.append(f"{nid}: already a quest giver, vendor or someone else's id")
        if any(ord(c) > 127 for c in greet + name):
            bad.append(f"{nid}: non-ASCII")
        for p in voice_problems(greet):
            bad.append(f"{nid}: {p}")
        if len(greet) < 60:
            bad.append(f"{nid}: greeting too thin to say who they are")
    return bad


def main():
    write = "--write" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))
    ven = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))
    by_id = {r["npc_id"]: r for r in amb["npcs"]}
    mine_all = set()
    tables = {}
    for stem in TOWNS:
        if only and stem not in only:
            continue
        try:
            mod = importlib.import_module(f"townsfolk.{stem}")
        except ModuleNotFoundError:
            continue
        tables[stem] = mod.PEOPLE
        mine_all |= {row[0] for row in mod.PEOPLE}
    # anyone who isn't a townsfolk row of ours: a quest giver, a vendor, a trainer
    quest_people = set()
    for f in (ROOT / "data/quests").glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        for q in (d.get("quests") if isinstance(d, dict) else []) or []:
            quest_people |= {q.get("giver_npc_id"), q.get("turn_in_npc_id")}
    known = ({r["npc_id"] for r in amb["npcs"] if not r.get("townsfolk")} | {v["vendor_id"] for v in ven["vendors"]}
             | quest_people) - mine_all
    bad = []
    for stem, people in tables.items():
        bad += problems(stem, people, known)
    if bad:
        print("PROBLEMS:\n  " + "\n  ".join(bad))
        return 1
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        zones = create_all_zones()
    total = 0
    for stem, people in tables.items():
        name = TOWNS[stem]
        entry = zones[name]
        z = entry["tilemap"] if isinstance(entry, dict) else entry
        key = zone_key(name)
        # recruits stand in towns too, and nobody may share their tile (tools/qa_recruits.py)
        recs = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]
        for rr in recs:
            for zk, xk, yk in (("zone", "x", "y"), ("home_town", "home_x", "home_y")):
                if rr.get(zk) and rr.get(xk) is not None and zone_key(str(rr[zk])) == key:
                    old_pos = {p[0]: (by_id[p[0]]["x"], by_id[p[0]]["y"]) for p in people if p[0] in by_id}
                    for nid, pos in old_pos.items():
                        if abs(pos[0] - rr[xk]) <= 1 and abs(pos[1] - rr[yk]) <= 1:
                            by_id[nid]["x"] = -99          # move off a recruit's tile
        taken = [(r["x"], r["y"]) for r in amb["npcs"] + ven["vendors"] + [
                     {"zone": rr.get("zone"), "x": rr.get("x"), "y": rr.get("y")} for rr in recs] + [
                     {"zone": rr.get("home_town"), "x": rr.get("home_x"), "y": rr.get("home_y")} for rr in recs]
                 if zone_key(str(r.get("zone", ""))) == key and r.get("npc_id") not in {p[0] for p in people}
                 and r.get("x") is not None]
        old = {p[0]: (by_id[p[0]]["x"], by_id[p[0]]["y"]) for p in people if p[0] in by_id}
        spots = place(z, people, taken, old)
        per = collections.Counter(p[4] for p in people)
        print(f"  {name}: {len(people)} townsfolk across {len(per)} districts "
              + ", ".join(f"{d} {n}" for d, n in sorted(per.items())))
        total += len(people)
        if write:
            for nid, pname, race, gender, district, greet in people:
                x, y = spots[nid]
                rec = by_id.get(nid)
                if rec is None:
                    rec = {"npc_id": nid}
                    amb["npcs"].append(rec)
                    by_id[nid] = rec
                rec.update(name=pname, zone=key, x=x, y=y, race=race, gender=gender,
                           appearance_variant=_look(race, gender, nid),
                           facing=("down", "left", "right")[int(hashlib.md5(nid.encode()).hexdigest(), 16) % 3],
                           greeting=greet, townsfolk=True, district=district)
    if write:
        (ROOT / "data/npcs/ambient_npcs.json").write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n",
                                                           encoding="utf-8")
        print(f"  wrote {total} townsfolk")
    else:
        print(f"  {total} townsfolk check out (run with --write to place them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
