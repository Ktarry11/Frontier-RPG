"""Give every unnamed explore objective a place name taken from the map it is on.

    python3 tools/name_explore_places.py [--apply] stem [stem ...]

An explore objective without a `label` shows as bare coordinates' worth of nothing: "Explore
Northern Stranglethorn". This names each from what is actually at that spot, in this order:
a door within 6 tiles ("the way into Zul'Marosh"), the subzone the point is inside ("the
Mistvale Shallows"), or the nearest subzone and the bearing from it ("the ground south of
Kurzen's Compound"). Hand-written labels (tools/quest_patches) are never overwritten; this is
the floor under them, so that no objective is left without a name.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def the(name):
    return ("the " + name[4:]) if name.startswith("The ") else name


def main():
    import audit_quest_directions as A
    apply = "--apply" in sys.argv
    stems = [a for a in sys.argv[1:] if not a.startswith("--")]
    w = A.World()
    left = 0
    for stem in stems:
        path = ROOT / f"data/quests/{stem}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        n = 0
        for q in data["quests"]:
            for o in q["objectives"]:
                if o.get("type") != "explore" or o.get("label") or o.get("target_x") is None:
                    continue
                key = A.slug(o.get("target"))
                if key not in w.maps:
                    print(f"  ?? {q['quest_id']}: no map {o.get('target')}")
                    left += 1
                    continue
                name, tm = w.maps[key]
                x, y = o["target_x"], o["target_y"]
                label = None
                for (px, py) in w.zm.portal_manager.get_portal_positions(name) or []:
                    dest = w.zm.portal_manager.get_destination(name, px, py)
                    if dest and math.hypot(px - x, py - y) <= 6:
                        label = "the way into " + the(dest[0])
                if label is None:
                    inside = [s for s in tm.subzones if s["x"] <= x <= s["x"] + s["w"] and s["y"] <= y <= s["y"] + s["h"]]
                    if inside:
                        label = the(min(inside, key=lambda s: s["w"] * s["h"])["name"])
                    elif tm.subzones:
                        s = min(tm.subzones, key=lambda s: math.hypot(s["x"] + s["w"] / 2 - x, s["y"] + s["h"] / 2 - y))
                        cx, cy = s["x"] + s["w"] / 2, s["y"] + s["h"] / 2
                        label = f"the ground {A.bearing(x - cx, y - cy)} of {the(s['name'])}"
                    else:
                        label = the(name)
                print(f"  {q['quest_id']:34s} {name} {x},{y} -> {label}")
                if apply:
                    o["label"] = label
                n += 1
        if apply and n:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{stem}: {n} places named{'' if apply else ' (dry run)'}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
