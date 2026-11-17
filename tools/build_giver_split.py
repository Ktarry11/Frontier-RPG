#!/usr/bin/env python3
"""Spread quests off overloaded givers: new people where a town needs them, and each moved quest in its new voice.

    PYTHONPATH=. python3 tools/build_giver_split.py            # check only
    PYTHONPATH=. python3 tools/build_giver_split.py --write    # check, then write

Kyle, 17 Nov 2026: "if there are NPCs who give too many quests, add new NPCs to account for it", then "Aim for 4
please". tools/qa_quest_givers.py holds the ceiling at 4.

The data is tools/giver_split_data.py:
  NEW_NPCS  {npc_id: dict(name, zone, near=(x, y) or at=(x, y), race, gender, variant, greeting)}
            A new person stands at `at`, or at the nearest free spot to `near`: walkable, not a door, not under a
            prop, and three tiles from everyone else in the zone.
  MOVES     {quest_id: dict(giver, why, D, A, T)}: who gives it now, why them, and the quest's text in their voice
            (any of D/A/T may be left out where the old line still fits the new speaker).
  TEXT      {quest_id: dict(D, A, T)}: text for quests that stay where they are but now have to point somewhere new,
            such as the step before a moved chain end saying who to see next. Optional.

What --write does, in order:
  1. adds each new NPC to data/npcs/ambient_npcs.json (an NPC already there is left where it is);
  2. merges MOVES into data/reference/quest_giver_moves.json and runs tools/apply_giver_moves.py, which writes the
     new giver into the zone quest files (and the turn-in, where it named the old giver);
  3. writes the new text into data/quests/text/zzzzzz_giver_moves.json, the overlay the moves already use.
It refuses to write if a line fails the voice bar (tools/audit_quest_voice), a quest or giver doesn't exist, or a new
NPC can't be placed.
"""
import contextlib
import io
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

AMB = ROOT / "data/npcs/ambient_npcs.json"
VEN = ROOT / "data/npcs/vendors.json"
MOVES = ROOT / "data/reference/quest_giver_moves.json"
VOICE = ROOT / "data/quests/text/zzzzzz_giver_moves.json"


class _Q:
    def __init__(self, qid, d, a, t):
        self.quest_id, self.description, self.accept_text, self.turn_in_text = qid, d or "x x x", a or "x x x", t or "x x x"


def _dump(path, doc, src):
    """Write JSON in the layout the file already has, so a diff shows only what changed."""
    for ind in (2, 1, 4):
        for ea in (False, True):
            for tail in ("\n", ""):
                if json.dumps(json.loads(src), indent=ind, ensure_ascii=ea) + tail == src:
                    path.write_text(json.dumps(doc, indent=ind, ensure_ascii=ea) + tail, encoding="utf-8")
                    return
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _zone_maps():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_generator import create_all_zones
        zones = create_all_zones()
    by_key = {}
    for name, z in zones.items():
        key = name.lower().replace(" ", "_").replace("'", "")
        by_key[key] = z
        if key.startswith("the_"):                 # NPC files say "pale_watch" for "The Pale Watch"
            by_key.setdefault(key[4:], z)
    return by_key


def _free_spot(z, near, taken, radius=14):
    nx, ny = near
    best = None
    for y in range(max(1, ny - radius), min(z.height - 1, ny + radius + 1)):
        for x in range(max(1, nx - radius), min(z.width - 1, nx + radius + 1)):
            if not z.is_walkable(x, y):
                continue
            if any(not z.is_walkable(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            if any(math.dist((x, y), t) < 3 for t in taken):
                continue
            if z.interaction_layer[y][x] is not None:      # a door, an npc tile, a chest
                continue
            under = False
            for m in getattr(z, "landmarks", []) or []:
                ax, ay = m.get("anchor_x", 0), m.get("anchor_y", 0)
                if ax - 0.5 <= x < ax + m.get("width_tiles", 1) + 0.5 and ay - 0.5 <= y < ay + m.get("height_tiles", 1) + 0.5:
                    under = True
                    break
            if under:
                continue
            d = math.dist((x, y), near)
            if best is None or d < best[0]:
                best = (d, x, y)
    return None if best is None else (best[1], best[2])


def main():
    import importlib
    import giver_split_data as G
    importlib.reload(G)
    with contextlib.redirect_stdout(io.StringIO()):
        from audit_quest_voice import findings
    amb_src = AMB.read_text(encoding="utf-8")
    amb = json.loads(amb_src)
    ven = json.loads(VEN.read_text(encoding="utf-8"))
    people = {n["npc_id"]: n for n in amb["npcs"]}
    people.update({v["vendor_id"]: v for v in ven["vendors"] if v["vendor_id"] not in people})
    quests = {}
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        for q in json.loads(path.read_text(encoding="utf-8")).get("quests", []):
            quests[q["quest_id"]] = q

    problems, placed = [], {}
    new = {k: v for k, v in G.NEW_NPCS.items() if k not in people}
    if new:
        maps = _zone_maps()
    for nid, n in new.items():
        z = maps.get(n["zone"])
        if z is None:
            problems.append(f"new NPC {nid}: no map for zone {n['zone']}")
            continue
        taken = [(p.get("x"), p.get("y")) for p in people.values() if p.get("zone") == n["zone"]]
        taken += [xy for k, (zz, xy) in placed.items() if zz == n["zone"]]
        spot = tuple(n["at"]) if n.get("at") else _free_spot(z, tuple(n["near"]), taken)
        if spot is None or not z.is_walkable(*spot):
            problems.append(f"new NPC {nid}: nowhere free near {n.get('near') or n.get('at')} in {n['zone']}")
            continue
        placed[nid] = (n["zone"], spot)

    for qid, m in G.MOVES.items():
        if qid not in quests:
            problems.append(f"{qid}: no such quest")
            continue
        if m["giver"] not in people and m["giver"] not in G.NEW_NPCS:
            problems.append(f"{qid}: giver {m['giver']} doesn't exist")
        for field, p in findings(_Q(qid, m.get("D"), m.get("A"), m.get("T"))):
            problems.append(f"{qid} {field}: {p}")
    for qid, m in getattr(G, "TEXT", {}).items():
        if qid not in quests:
            problems.append(f"{qid}: no such quest")
            continue
        for field, p in findings(_Q(qid, m.get("D"), m.get("A"), m.get("T"))):
            problems.append(f"{qid} {field}: {p}")
    for nid, n in G.NEW_NPCS.items():
        for field, p in findings(_Q(nid, n.get("greeting"), None, None)):
            problems.append(f"{nid} greeting: {p}")

    after = {}
    for q in quests.values():
        g = G.MOVES.get(q["quest_id"], {}).get("giver") or q.get("giver_npc_id") or ""
        if not g.startswith("item:"):
            after[g] = after.get(g, 0) + 1
    print(f"  {len(G.MOVES)} quests moving, {len(new)} new people; "
          f"busiest after: {sorted(after.items(), key=lambda t: -t[1])[:5]}")
    for nid, (zz, xy) in placed.items():
        print(f"    new {nid} ({G.NEW_NPCS[nid]['name']}) at {zz} {xy}")
    for p in problems:
        print("  PROBLEM " + p)
    if "--write" not in sys.argv:
        return 1 if problems else 0
    if problems:
        print("  REFUSING TO WRITE")
        return 1

    for nid, (zz, (x, y)) in placed.items():
        n = G.NEW_NPCS[nid]
        amb["npcs"].append({"npc_id": nid, "name": n["name"], "zone": zz, "x": x, "y": y,
                            "greeting": n["greeting"], "facing": "down", "race": n["race"],
                            "gender": n["gender"], "appearance_variant": n.get("variant", 2)})
    _dump(AMB, amb, amb_src)

    msrc = MOVES.read_text(encoding="utf-8")
    mdoc = json.loads(msrc)
    for qid, m in G.MOVES.items():
        mdoc["moves"][qid] = {"giver": m["giver"], "why": m["why"]}
    _dump(MOVES, mdoc, msrc)

    vsrc = VOICE.read_text(encoding="utf-8")
    vdoc = json.loads(vsrc)
    for qid, m in list(G.MOVES.items()) + list(getattr(G, "TEXT", {}).items()):
        fields = {k: m[s] for s, k in (("D", "description"), ("A", "accept_text"), ("T", "turn_in_text")) if m.get(s)}
        if fields:
            vdoc[qid] = fields
    _dump(VOICE, vdoc, vsrc)

    from apply_giver_moves import apply
    todo, missing = apply(check=False)
    print(f"  written: {len(placed)} new people, {len(G.MOVES)} moves ({len(todo)} applied now)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
