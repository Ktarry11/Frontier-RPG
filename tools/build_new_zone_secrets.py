#!/usr/bin/env python3
"""Secrets for the newest maps: hidden hollows with a cache in each, placed blind. Idempotent; ADDS to
data/world/secrets.json and never touches an older secret.

    PYTHONPATH=. python3 tools/build_new_zone_secrets.py [--check]

Kyle, 19 Nov 2026: "Dont forget we need complete zones, so include secrets, gatherables etc." Rootwater Isle gets its
secrets, and so do Feralas's three open maps, which went in without any. The standing rules hold: hidden is truly
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
WANT = {"Rootwater Isle": 2, "The High Wilderness": 2, "The Forgotten Coast": 2, "The Twin Colossals": 2}


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
            cands = P3.glades(tm, taken) or P3.nooks(tm, taken)
            if not cands:
                short.append(zone)
                break
            c = max(cands, key=lambda c: c["depth"])
            sid = f"secret_nz_{zone.lower().replace(' ', '_').replace(chr(39), '')}_{i + 1}"
            if sid in have:
                continue
            spot = c["spot"]
            secrets.append({"id": sid, "zone": zone, "kind": "glade", "passage": c["passage"], "area": c["area"],
                            "mask": c["mask"], "ground": c["ground"], "vendor": None, "door": None,
                            "cache": {"x": spot[0], "y": spot[1], "level": P3.zone_level(levels, zone)},
                            "found_text": rnd.choice(P3.FOUND), TAG: True})
            have.add(sid)
            added += 1
    if not check:
        P3.SECRETS.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{added} secrets added over {len(WANT)} maps{' (check only)' if check else ''}"
          + (f"; no room on {len(short)} map(s)" if short else "") + f"; {len(secrets)} secrets in all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
