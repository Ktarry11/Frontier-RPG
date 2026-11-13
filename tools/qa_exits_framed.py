#!/usr/bin/env python3
"""Every way out of every map is framed by entrance art, and the frame is in the right place.

    PYTHONPATH=. python3 tools/qa_exits_framed.py

Kyle, 10 Nov 2026: entrance art is MISSING for most exits. Measured 12 Nov: 183 links were a
glowing tile in open ground. world/exit_frames.py now frames whatever the hand-built zones did
not, as a pass over the finished world.

SIX CLAIMS:

  1. NO EXIT IS BARE. Every (map -> destination) link has entrance art on it, bar the short
     list below of links with no room for any.
  2. THE DOOR IS IN THE FRAME. Each placed frame covers a portal tile of its own link.
  3. NO FRAME COVERS SOMEBODY ELSE'S DOOR, or overlaps another piece of entrance art.
  4. A FRAME BLOCKS NOTHING. These go onto finished maps; one that seals a road is worse than
     the bare tile it replaced. Checked as: placing them added no collision.
  5. EVERY PIECE NAMED IN THE TABLES EXISTS ON DISK. A table naming art nobody drew silently
     falls back to something generic, and nobody finds out.
  6. A WAY OUT LOOKS LIKE A WAY OUT, AND A WAY IN LIKE A WAY IN. Leaving a dungeon for the open
     world never gets a dark doorway that reads as "deeper", and inside a dungeon the art is
     matched to the room's own colours (Kyle: "try to match the boat colour with the stairs").
"""
import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

#: Links allowed to stay bare, each with its reason. Anything else bare is a failure.
MAY_BE_BARE = {
    ("Arathi Central", "Hammerfall"): "no room: even the smallest frame would cover another door or another frame",
    ("Arathi East", "Saltspur Landing"): "no room: even the smallest frame would cover another door or another frame",
}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_manager import ZoneManager
        from world import exit_frames as EF
        from world.exit_frames import _is_a_gate as is_entrance_art     # a hand-placed gate counts
        import world.exit_frames, world.portal_art
        # collision before frames: build the world once with the pass switched off
        real = world.exit_frames.frame_exits
        world.exit_frames.frame_exits = lambda *a, **k: {"placed": 0, "skipped": []}
        try:
            plain = ZoneManager()
        finally:
            world.exit_frames.frame_exits = real
        zm = ZoneManager()
    bad = []

    by_src = {}
    for (src, x, y), dest in zm.portal_manager._lookup.items():
        by_src.setdefault(src, {}).setdefault(dest[0], []).append((x, y))

    def art_on(tm, tiles):
        for lm in tm.landmarks:
            if is_entrance_art(lm["sprite_key"]) and any(
                    lm["anchor_x"] - 1 <= x <= lm["anchor_x"] + lm["width_tiles"]
                    and lm["anchor_y"] - 1 <= y <= lm["anchor_y"] + lm["height_tiles"] for x, y in tiles):
                return lm
        return None

    # ---- 1. nothing bare
    links = bare = 0
    for src, dests in by_src.items():
        if src not in zm.zones:
            continue
        tm = zm.zones[src]["tilemap"]
        for dest, tiles in dests.items():
            links += 1
            if art_on(tm, tiles) is None:
                bare += 1
                if (src, dest) not in MAY_BE_BARE:
                    bad.append(f"{src} -> {dest} has no entrance art")
    for pair in MAY_BE_BARE:
        tm = zm.zones.get(pair[0], {}).get("tilemap")
        if tm is not None and pair[1] in by_src.get(pair[0], {}) and art_on(tm, by_src[pair[0]][pair[1]]):
            bad.append(f"{pair[0]} -> {pair[1]} is listed as allowed-bare and is now framed - "
                       f"take it off the list")

    # ---- 2, 3, 6. each placed frame
    frames = 0
    for src, entry in zm.zones.items():
        tm = entry["tilemap"]
        mine = [lm for lm in tm.landmarks if lm.get("exit_frame")]
        doors = by_src.get(src, {})
        all_tiles = {t: d for d, ts in doors.items() for t in ts}
        for lm in mine:
            frames += 1
            name = os.path.basename(lm["sprite_key"])[:-4]
            inside = [(t, d) for t, d in all_tiles.items()
                      if lm["anchor_x"] <= t[0] < lm["anchor_x"] + lm["width_tiles"]
                      and lm["anchor_y"] <= t[1] < lm["anchor_y"] + lm["height_tiles"]]
            if not inside:
                bad.append(f"{src}: {name} at {(lm['anchor_x'], lm['anchor_y'])} has no door in it")
                continue
            if len({d for _t, d in inside}) > 1:
                bad.append(f"{src}: {name} covers doors to {sorted({d for _t, d in inside})}")
            for other in tm.landmarks:
                if other is lm or not world.portal_art.is_entrance_art(other["sprite_key"]):
                    continue
                if EF._rect_hits(lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"], other):
                    bad.append(f"{src}: {name} overlaps {os.path.basename(other['sprite_key'])}")
            dest = inside[0][1]
            if src in zm.cave_names and dest not in zm.cave_names and name.startswith("ent_door_"):
                bad.append(f"{src} -> {dest}: the way out to the open world is drawn as {name}, "
                           f"a dark door that reads as going deeper")
            if bool(lm.get("match_ground")) != (src in zm.cave_names):
                bad.append(f"{src}: {name} match_ground is {lm.get('match_ground')} - art inside a "
                           f"dungeon is matched to the room, art outdoors is not")
    if frames != zm.exit_frames["placed"]:
        bad.append(f"the pass says it placed {zm.exit_frames['placed']} and {frames} are on the maps")

    # ---- 4. no new walls
    sealed = 0
    for name, entry in zm.zones.items():
        a, b = plain.zones[name]["tilemap"], entry["tilemap"]
        for y in range(a.height):
            ra, rb = a.collision_layer[y], b.collision_layer[y]
            if ra != rb:
                sealed += sum(1 for u, v in zip(ra, rb) if v is not None and u is None)
    if sealed:
        bad.append(f"framing the exits made {sealed} walkable tile(s) solid")

    # ---- 5. the tables name real art
    missing = sorted({look for table in (EF.OUT_OF, EF.INTO, EF.TOWN, EF.REGION, EF.DOCK)
                      for _p, looks in table for look in looks
                      if not os.path.exists(f"{EF.ART}{look}.png")})
    if missing:
        bad.append(f"{len(missing)} piece(s) named in the tables are not on disk: {missing}")

    # the renderer really does the colour match
    src_r = Path("ui/tilemap_renderer.py").read_text()
    if 'lm.get("match_ground")' not in src_r or "_matched_to_ground" not in src_r:
        bad.append("the renderer ignores match_ground, so dungeon exits keep their painted colours")

    used = {os.path.basename(lm["sprite_key"]) for e in zm.zones.values()
            for lm in e["tilemap"].landmarks if lm.get("exit_frame")}
    print(f"{links} links, {links - bare} framed ({frames} by the pass, {len(used)} different pieces), "
          f"{bare} left bare on purpose")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad[:25]:
            print("  -", line)
        return 1
    print("\nexits OK - every way out is framed, each frame holds its own door and nobody "
          "else's, nothing was walled off, and every piece in the tables is on disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
