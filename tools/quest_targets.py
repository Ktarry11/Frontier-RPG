#!/usr/bin/env python3
"""Where each objective of a zone's quests really is, from the giver: place, compass bearing, distance.

    PYTHONPATH=. python3 tools/quest_targets.py stranglethorn_central [...]

For writing passes (Kyle, 17 Nov 2026: the quest writing pass). A rewrite has to say true directions, and the
truth is the live map, so this reads it with tools/audit_quest_directions.World, the same reader the direction
audit judges by. Prints, per quest: giver and where they stand, then each objective with its nearest place,
its bearing from the giver and how far it is ("near" under the audit's NEAR, where no direction is needed).
"""
import contextlib
import io
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    import audit_quest_directions as A


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        world = A.World()
    for stem in sys.argv[1:]:
        quests = json.load(open(f"data/quests/{stem}.json", encoding="utf-8"))["quests"]
        for q in quests:
            giver = world.npcs.get(q.get("giver_npc_id"))
            print(f"## {q['quest_id']} | {q.get('title')} | L{q.get('level_min')}")
            if giver is None:
                print(f"   giver {q.get('giver_npc_id')}: not on a map")
                continue
            gmap, gx, gy, gname = giver
            hand = q.get("collector_npc_id")
            print(f"   giver {gname} @ {gmap} ({gx},{gy})" + (f"  hand-in {hand}" if hand and hand != q.get("giver_npc_id") else ""))
            world._from = (gx, gy)
            for o in q["objectives"]:
                kind, tgt, n = o.get("type"), o.get("target"), o.get("count", 1)
                places = []
                if kind == "explore" and o.get("target_x") is not None:
                    places = [(o.get("label") or "(no label)", o["target_x"], o["target_y"])]
                    where_map = A.slug(tgt)
                else:
                    creatures = []
                    if kind in ("kill", "kill_boss") and tgt:
                        creatures = [tgt] + list(o.get("alt_targets") or [])
                    elif kind in ("fetch", "gather") and tgt:
                        creatures = sorted(world.carriers.get(tgt, ()))
                    for c in creatures:
                        with contextlib.redirect_stdout(io.StringIO()):
                            w = world.places(gmap, c)
                            if w is None:
                                w = world.next_door(gmap, c) or []
                        places += [(f"{lab} [{c}]", x, y) for lab, x, y in w]
                    where_map = gmap
                line = f"   - {kind} {n} {tgt}"
                if o.get("label"):
                    line += f"  label='{o['label']}'"
                if kind in ("fetch", "gather"):
                    line += f"  from {sorted(world.carriers.get(tgt, ())) or 'NOTHING'}"
                if not places:
                    print(line + "  (no place on the giver's map)")
                    continue
                best = min(places, key=lambda p: math.hypot(p[1] - gx, p[2] - gy))
                d = math.hypot(best[1] - gx, best[2] - gy)
                print(line + f"\n       nearest: {best[0]} ({best[1]},{best[2]}) "
                      + (f"{A.bearing(best[1] - gx, best[2] - gy)} {int(d)} tiles" if d >= A.NEAR else f"near ({int(d)} tiles)"))


if __name__ == "__main__":
    main()
