#!/usr/bin/env python3
"""Create and position North Western Plaguelands' people (docs/plaguelands_design.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_wpl_north_npcs.py

The Pale Watch is the Order of the Pale Flame's forward camp on the road under Hearthglen. It isn't a hub: quests
come from Sorrow Hill (Kyle: givers stay in the hubs). These three watch the road and say what they've seen.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_wpl_north import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "western_plaguelands_north"
M, F = "male", "female"

AMBIENT = {
    # ---- the quest givers added with the quest pass (tools/plaguelands_quests_north.py)
    "wpln_pf_sister": ("Sister Amalie Crane", "human", F, 5, "down",
                       "I was a priestess in Hearthglen. I stood in the room while they questioned the newcomers, "
                       "and then I walked out. I think I'm still walking."),
    "wpln_pf_woodwright": ("Woodwright Jonah Lind", "human", M, 6, "down",
                           "I built houses in Duluth before the Integration. Now I build palisades, and I'd build "
                           "them faster if anyone would let me near Hearthglen's timber."),
    "wpln_pf_angler": ("Oona Byrne", "human", F, 3, "right",
                       "I fish the river for the Watch's supper. I fished out of Galway for thirty years, and this is "
                       "the first river that's ever tried to eat me."),
    "wpln_pf_clerk": ("Clerk Wendel Ashby", "human", M, 2, "left",
                      "I kept Hearthglen's books until I read what I was writing down, and then I left. I still keep "
                      "books, because it's an old habit."),
    "wpln_pf_watch_captain": ("Watch Captain Lena Fischer", "human", F, 4, "down",
                              "Hearthglen's gate is up the road. They can see us from the walls, and we can see "
                              "them, and so far everyone's decided that's close enough."),
    "wpln_pf_scout": ("Scout Mateo Brandt", "human", M, 5, "right",
                      "Patrols leave the gate at dawn and come back at dusk, and the inquisitors walk the fields in "
                      "between. If you're going up there, go in the afternoon."),
    "wpln_pf_field_medic": ("Field Medic Noah Kowal", "human", M, 3, "down",
                            "I was a nurse in Winnipeg. Out here I patch up whoever makes it back down the hill, and "
                            "I don't ask which side they came from."),
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
    print(f"North WPL: {made} created, {moved} moved ({len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
