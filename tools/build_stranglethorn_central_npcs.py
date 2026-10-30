#!/usr/bin/env python3
"""Six wilderness NPCs for Central Stranglethorn. Idempotent, append-only.

    PYTHONPATH=. python3 tools/build_stranglethorn_central_npcs.py

WHY THIS FILE EXISTS. Central Stranglethorn is the only Stranglethorn zone with no town, so
tools/handbuilt_stranglethorn_central.py ships NPC_POSITIONS = {} with the comment "wilderness: its
quests come from Grom'gol in the north and Booty Bay in the south". That is true of MOST of the zone's
quests and it leaves a hole: a zone you walk for forty minutes with nobody standing in it reads as
scenery, and three of the zone's threads (the basin, the marsh, the shelf) are about people who live
out here and would not be found in either town.

So: six people camped on the road and the clearings, and NOT a town. No vendors, no innkeeper, no
services. Everyone here is working.

POSITIONS ARE SNAPPED, NOT TYPED. Every earlier roster in this repo drifted because the layout and the
NPC list were authored in two places (see tools/build_stranglethorn_npcs.py's docstring for the list of
towns it happened to). Here the layout module is the only source of truth and it does not have a
position dict to read, so this script does the next best thing: each NPC carries an ANCHOR - a place in
the fiction, "the fork where the arena road leaves the Vine Road" - and the script builds the real zone,
floods it from the player's start tile, and snaps the anchor to the nearest tile that is both walkable
and reachable. The written coordinate is the zone's answer, not mine.

It is also the test. If a prop moves, a clearing shrinks or the thicket noise reseeds, the snap moves
with it; and if an anchor ends up more than SNAP_LIMIT tiles from a usable tile the script raises rather
than writing somebody into a cliff.

Shared file: data/npcs/ambient_npcs.json is written by every town pass in the game, so this re-reads it
at write time and merges by npc_id.
"""
import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_stranglethorn_central as M     # noqa: E402

ZONE_KEY = "central_stranglethorn"       # world/ambient_npc_manager._zone_key("Central Stranglethorn")
SNAP_LIMIT = 9

#: npc_id -> (name, race, gender, anchor, greeting)
#:
#: The anchors are the zone's own landmarks, named in its docstring: the Vine Road / arena fork at
#: (92,88), the staging apron at (152,112), the gate apron at (150,100), the cave mouth on the dry
#: shoulder of the Veilfall lip at (40,58), the marsh landing at (48,156), and the shelf road's last
#: bend at (158,34).
ROSTER = {
    # ---- THE VINE ROAD ---------------------------------------------------------------------------
    # A Gurbashi contractor, not a Gurbashi warrior. The arena needs a crowd, a crowd needs a road,
    # and somebody has to be paid to keep nine days of bloodvine off it.
    "stvc_road_ganger": ("Road-Ganger Dubo", "troll", "male", (90, 90),
                         "Road's cut as far as the ford. After the ford it is cut as far as I was paid to."),

    # ---- GURBASHI FLATS --------------------------------------------------------------------------
    # Booty Bay's woman on the ground. She does not work for the arena; she works the board, and the
    # board is in the Bay.
    "stvc_arena_tout": ("Tout Bexxil", "goblin", "female", (154, 114),
                        "You are on the board already. You were on it before you got here."),
    # The Gurbashi keep their own list and he keeps it. Three generations of gatehouse in one family
    # and he can tell you what every course of that wall is for.
    "stvc_gurbashi_broker": ("Gatehouse Broker Zul'tamo", "troll", "male", (147, 106),
                             "The ring runs one way. That is not a custom. That is masonry."),

    # ---- VEILFALL BASIN --------------------------------------------------------------------------
    # The zone's one person who is simply pleased to see somebody. Camped two years on the dry
    # shoulder of a waterfall with a drying rack and no conversation.
    "stvc_basin_herbalist": ("Ordek Fenn", "orc", "male", (38, 52),
                             "Sit down, sit down. I have not had anyone to be wrong at in weeks."),

    # ---- THE SNAPJAW MARSH -----------------------------------------------------------------------
    # Sets nets in standing water, has done her whole life, and is not discussing her hands.
    "stvc_marsh_fisher": ("Netsetter Ulua", "troll", "female", (49, 152),
                          "Nets are set. Nets have been set since before you were a rumour."),

    # ---- MOSH'OGG SHELF --------------------------------------------------------------------------
    # Posted from Grom'gol to watch the one road up. Eleven weeks, nine reports, and all nine say the
    # same thing, which is the part she would rather you did not notice.
    "stvc_shelf_watcher": ("Watcher Garza", "orc", "female", (157, 36),
                           "One road up and I am sitting on it. Write that down, it is the whole post."),
}


def built():
    """The real zone, plus the walkable/reachable mask the player actually moves on.

    z.is_walkable is the same call Party movement makes, and it is read AFTER build_layout has
    scattered props and run seal_unreachable twice - which is the only reason this is trustworthy.
    Reading tools/ashenvale_engine tile_kind instead would snap NPCs onto tiles the shipped zone has
    since sealed (tools/verify_aspen_wilderness.py has the long version of that mistake).
    """
    print("building Central Stranglethorn ...")
    L = M.build_layout()
    z = L.zone
    W, H = M.W, M.H
    walk = [[z.is_walkable(x, y) for x in range(W)] for y in range(H)]

    sx, sy = M.START
    seen = [[False] * W for _ in range(H)]
    q = deque([(sx, sy)])
    seen[sy][sx] = True
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and walk[ny][nx] and not seen[ny][nx]:
                seen[ny][nx] = True
                q.append((nx, ny))
    return z, seen


#: Tiles no NPC may stand on whatever the snap says: a portal tile swallows the interaction (the
#: overworld takes the zone change first) and an arrival tile puts somebody in the doorway of a cave.
BLOCKED = set(M.PORTALS) | set(M.ARRIVALS)


def snap(reach, ax, ay):
    """Nearest reachable tile to the anchor, searched in rings so the result is the closest one."""
    H, W = len(reach), len(reach[0])
    for r in range(SNAP_LIMIT + 1):
        best = None
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                x, y = ax + dx, ay + dy
                if not (0 <= x < W and 0 <= y < H) or (x, y) in BLOCKED:
                    continue
                if not reach[y][x]:
                    continue
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, x, y)
        if best:
            return best[1], best[2]
    raise SystemExit(f"no reachable tile within {SNAP_LIMIT} of anchor ({ax},{ay}) - "
                     f"the layout has moved under this roster")


def main():
    _zone, reach = built()

    rows, report = [], []
    for i, (nid, (name, race, gender, anchor, line)) in enumerate(ROSTER.items()):
        x, y = snap(reach, *anchor)
        rows.append({"npc_id": nid, "name": name, "zone": ZONE_KEY, "x": x, "y": y,
                     "greeting": line, "gender": gender, "race": race,
                     # offset so six people standing in one zone are not six copies of one sprite
                     "appearance_variant": (i * 7 + 2) % 24, "facing": "down"})
        report.append((nid, anchor, (x, y), max(abs(x - anchor[0]), abs(y - anchor[1]))))

    # APPEND-ONLY, RE-READ AT WRITE TIME. Three agents are writing Stranglethorn at once and this file
    # belongs to all of them, so it is read here and not a moment earlier.
    path = ROOT / "data/npcs/ambient_npcs.json"
    data = json.loads(path.read_text())
    by_id = {e["npc_id"]: e for e in data["npcs"]}
    added = sum(1 for e in rows if e["npc_id"] not in by_id)
    for e in rows:
        by_id[e["npc_id"]] = e
    data["npcs"] = list(by_id.values())
    path.write_text(json.dumps(data, indent=2) + "\n")

    print(f"Central Stranglethorn wilderness NPCs: +{added} new, {len(rows) - added} updated "
          f"({len(data['npcs'])} ambient NPCs in the game)")
    for nid, anchor, got, drift in report:
        print(f"  {nid:<24} anchor {str(anchor):<11} -> {str(got):<11} snapped {drift}")


if __name__ == "__main__":
    main()
