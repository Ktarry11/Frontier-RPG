#!/usr/bin/env python3
"""Create and position North Western Plaguelands' people (docs/plaguelands_design.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_wpl_north_npcs.py

The Pale Watch is the Order of the Pale Flame's walled town on the road under Hearthglen, its own map now
(tools/handbuilt_pale_watch.py; Kyle, 16 Nov 2026: "when a town is made it's always a seperate map"). Its inn and its
hawks are its own: the first bed and the first flight this close to Hearthglen.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_pale_watch import NAME, NPC_POSITIONS as TOWN_AT  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

ZONE = zone_key(NAME)
NPC_POSITIONS = dict(TOWN_AT)
SERVICES = {"wpln_pf_innkeeper": ["inn"], "wpln_pf_roostkeeper": ["flight"]}
FLIGHT_NODES = [
    ("pale_watch", {"name": "The Pale Watch", "zone": NAME, "master": "wpln_pf_roostkeeper",
                    "pos": [84, -30], "continent": "eastern_kingdoms"}),
]
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
    "wpln_pf_innkeeper": ("Innkeeper Beatriz Couto", "human", F, 3, "down",
                          "I ran a cafe in Porto, by the river. This is the last bed before Hearthglen, and the walls "
                          "are thin, so if you snore, the Crusade will hear you."),
    "wpln_pf_roostkeeper": ("Roostkeeper Liam Doherty", "human", M, 5, "right",
                            "The hawks go anywhere you've been. They won't fly over Hearthglen, and I've stopped "
                            "asking them to."),
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
            by_n[nid]["zone"] = ZONE                 # a move to another map is the layout's to make
        else:
            ad["npcs"].append(rec)
            made += 1
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"The Pale Watch: {made} created, {moved} moved ({len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
