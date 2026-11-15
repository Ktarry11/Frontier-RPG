#!/usr/bin/env python3
"""Create and position South Felwood's people: the two Sentinels holding the old watch at Morlos'Aren.
Idempotent; follows tools/npc_data_guard.py (creates who it names, moves people to the layout's spot,
deletes nobody).

    PYTHONPATH=. python3 tools/sync_felwood_south_npcs.py

Felwood audit, 15 Nov 2026 (Kyle: "let's ensure that felwood is fully built"). Morlos'Aren is a safe
settlement in the encounter tables with a tower, a tent and lanterns, and "The Watch at Morlos'Aren" closes
with Captain Saranis promising two Sentinels and a lantern. Nobody was there. These two hold it. They give
no quests: Kyle, 14 Nov, "Keep most quest givers in hubs".

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_felwood_south import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "south_felwood"
F = "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "fs_morlosaren_sentinel": ("Sentinel Ilthara Swiftleaf", "night_elf", F, 5, "down",
                               "Captain Saranis sent two of us down with a lantern. It isn't much of a "
                               "garrison, but the road's watched again. The Sanctuary's north, then east at "
                               "the fork."),
    "fs_morlosaren_lookout": ("Sentinel Aeris Moonvale", "night_elf", F, 1, "left",
                              "I keep the lantern lit and my eyes on the road. Mostly it's travellers from "
                              "Ashenvale. Every so often it's something worse coming down from the north."),
}


def main():
    if set(AMBIENT) != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(set(AMBIENT) ^ set(NPC_POSITIONS))}")
    ap = ROOT / "data/npcs/ambient_npcs.json"
    ad = json.loads(ap.read_text(encoding="utf-8"))
    by_n = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=ZONE, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in by_n:
            moved += bool(safe_update(by_n[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"South Felwood: {made} created, {moved} moved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
