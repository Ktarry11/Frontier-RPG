#!/usr/bin/env python3
"""Secrets for the newest maps: hidden hollows with a cache in each, placed blind. Idempotent; ADDS to
data/world/secrets.json and never touches an older secret.

    PYTHONPATH=. python3 tools/build_new_zone_secrets.py [--check]

Kyle, 19 Nov 2026: "Dont forget we need complete zones, so include secrets, gatherables etc." Rootwater Isle gets its
secrets, and so do Feralas's three open maps, which went in without any, and every tier of the tree after it. The standing rules hold: hidden is truly
hidden (world/secrets.py: the way in still looks like the rock or trees it's cut from), nothing touches a portal, an
NPC, a road or an older secret, and Kyle is never told where. This prints counts only.

Glades come from tools/find_secret_pockets.candidates() on the live maps (the same as tools/build_secrets_pass3.py);
a map whose walls are too thin for a glade gets a nook, a small room in the wall.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_secrets_pass3 as P3  # noqa: E402

TAG = "new_zones"
#: map -> how many secrets it should hold
WANT = {"Rootwater Isle": 2, "The Lower Boughs": 2, "The Middle Boughs": 2, "The Upper Boughs": 2, "The High Wilderness": 2, "The Forgotten Coast": 2, "The Twin Colossals": 2}


#: maps that stand over a drop (a module with DROP): their collision is mostly the void, and a hidden place cut into
#: that would be a room of open air. On these a secret has to be cut into the tree itself.
OVER_THE_DROP = {"The Lower Boughs": "tools.handbuilt_worldtree_lower_boughs",
                 "The Middle Boughs": "tools.handbuilt_worldtree_middle_boughs",
                 "The Upper Boughs": "tools.handbuilt_worldtree_upper_boughs"}


def _tiles(c):
    out = []
    for key in ("passage", "area", "mask"):
        for t in c.get(key) or []:
            if isinstance(t, (list, tuple)) and len(t) >= 2 and all(isinstance(a, int) for a in t[:2]):
                out.append((t[0], t[1]))
    return out


def solid_ground(zone, c):
    """False when any tile of the candidate hangs over the drop."""
    mod = OVER_THE_DROP.get(zone)
    if not mod:
        return True
    import importlib
    m = importlib.import_module(mod)
    return all(m.sea(x + 0.5, y + 0.5) <= 0 for (x, y) in _tiles(c))


def cut_doors(secrets, zones, have):
    """The secret doors to hidden zones on these maps (world/hidden_zones.py): a room in the wall of the parent, cut the
    way tools/build_secrets.py cuts them, and kept off the drop like every other secret here. A hidden zone reached
    from inside another (behind a great tree) gets its door from that zone's layout. Counts only, never where."""
    from tools.build_secrets import _hidden_doors, _placed_door_secrets, _is_frontier
    n = 0
    for zname, (parent, tx, ty) in _hidden_doors():
        sid = "door_" + "".join(ch for ch in zname.lower().replace(" ", "_") if ch.isalnum() or ch == "_")
        if parent not in WANT or sid in have or zones.get(parent) is None:
            continue
        tm = zones[parent]
        taken = P3.taken_tiles(secrets, parent)
        cands = [c for c in (P3.glades(tm, taken) or []) if solid_ground(parent, c)] or \
            [c for c in (P3.nooks(tm, taken) or []) if solid_ground(parent, c)]
        if not cands:
            continue
        c = max(cands, key=lambda c: c["depth"])
        sx, sy = c["spot"]
        secrets.append({"id": sid, "zone": parent, "kind": "glade", "passage": c["passage"], "area": c["area"],
                        "mask": c.get("mask"), "cache": None, "vendor": None,
                        "door": {"x": sx, "y": sy + 1, "to": zname, "tx": tx, "ty": ty},
                        "found_text": ("The air changes. Nobody has ever stood where you're standing, and the way on "
                                       "goes deeper than anything you know." if _is_frontier(zname) else
                                       "There's a way down here. It goes a long way down."), TAG: True})
        have.add(sid)
        n += 1
    for sec in _placed_door_secrets():
        if sec["id"] not in have:
            sec[TAG] = True
            secrets.append(sec)
            have.add(sec["id"])
            n += 1
    return n


def main():
    check = "--check" in sys.argv
    rnd = random.Random(19)
    doc = json.loads(P3.SECRETS.read_text(encoding="utf-8"))
    secrets = doc["secrets"]
    levels = json.loads(P3.LEVELS.read_text(encoding="utf-8"))["zones"]
    zones = P3.load_world()
    have = {s["id"] for s in secrets}
    added, short = 0, []
    for zone, n in WANT.items():
        tm = zones.get(zone)
        if tm is None:
            short.append(zone)
            continue
        for i in range(sum(1 for s in secrets if s["zone"] == zone), n):
            taken = P3.taken_tiles(secrets, zone)
            cands = [c for c in (P3.glades(tm, taken) or []) if solid_ground(zone, c)] or \
                [c for c in (P3.nooks(tm, taken) or []) if solid_ground(zone, c)]
            if not cands:
                short.append(zone)
                break
            c = max(cands, key=lambda c: c["depth"])
            # the first free name: a secret re-placed after a layout change keeps the numbering whole
            stem = f"secret_nz_{zone.lower().replace(' ', '_').replace(chr(39), '')}_"
            sid = next(f"{stem}{j}" for j in range(1, 99) if f"{stem}{j}" not in have)
            spot = c["spot"]
            secrets.append({"id": sid, "zone": zone, "kind": "glade", "passage": c["passage"], "area": c["area"],
                            "mask": c["mask"], "ground": c["ground"], "vendor": None, "door": None,
                            "cache": {"x": spot[0], "y": spot[1], "level": P3.zone_level(levels, zone)},
                            "found_text": rnd.choice(P3.FOUND), TAG: True})
            have.add(sid)
            added += 1
    doors = cut_doors(secrets, zones, have)
    if not check:
        P3.SECRETS.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{doors} hidden door(s) cut")
    print(f"{added} secrets added over {len(WANT)} maps{' (check only)' if check else ''}"
          + (f"; no room on {len(short)} map(s)" if short else "") + f"; {len(secrets)} secrets in all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
