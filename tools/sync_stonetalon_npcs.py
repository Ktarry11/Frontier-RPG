#!/usr/bin/env python3
"""Create and position Mistwalker Camp's people in Stonetalon West (docs/stonetalon_brief.md). Idempotent;
follows tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_stonetalon_npcs.py

Mistwalker Camp is the far side's quest camp: four people and a fire, no inn and no flight master (Kyle: "a
small group of quest givers outside towns is fine"). They give the West's quests that Sun Rock can't, and
they pay the same reputations as the town: Thunder Bluff by default, the Cartel and the Forsaken by giver
(tools/build_stonetalon_quests.py).

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_stonetalon_west import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "stonetalon_west"
M, F = "male", "female"

AMBIENT = {
    "mw_camp_leader": ("Mistwalker Iyana Rainsong", "tauren", F, 9, "down",
                       "We walk the fog so the giants don't have to stand alone. Keep your voice down near the old "
                       "ones. Some of them are awake."),
    "mw_arborist": ("Tamsin Reyes", "human", F, 4, "right",
                    "I climbed redwoods for a living back in Humboldt County. These ones are bigger than anything we "
                    "had, and I've never been happier to be wrong about a tree."),
    "mw_ex_venture": ("Nozzle Quickspan", "goblin", M, 3, "left",
                      "I ran a saw crew for the Venture Co. for six years. I quit the day they started on the living "
                      "giants. The Cartel took me in, and I've been making it up to the trees ever since."),
    "mw_forsaken_chem": ("Alchemist Rennick Toll", "forsaken", M, 2, "down",
                         "Undercity sent me for sulphur and ash. The mountain has plenty of both. I'm also told I'm "
                         "not welcome by the fire, so I stand over here."),
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
    print(f"Mistwalker Camp: {made} made, {moved} moved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
