#!/usr/bin/env python3
"""Create and position East Eastern Plaguelands' people (docs/plaguelands_design.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_epl_east_npcs.py

LIGHT'S HOPE CHAPEL is its own town map now (tools/handbuilt_lights_hope.py, docs/plaguelands_towns_plan.md), the Argent
Dawn's heart (Kyle chose the Argent Dawn as its own faction): Commander Eligor Dawnbringer, the Scourgestone turn-ins and
the order's quartermaster. CROWN GUARD CAMP's people moved in with them (Kyle, 16 Nov 2026: "Also fold Crown Guard Camp
into Lights Hope"); the tower stands empty on the road. One inn and one flight master, the chapel's: Crown Guard's
innkeeper and bat handler help where they're needed.

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_epl_east import NAME as EAST, NPC_POSITIONS as EAST_AT  # noqa: E402
from tools.handbuilt_lights_hope import NAME as LIGHTS_HOPE, NPC_POSITIONS as TOWN_AT  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

#: id -> (zone key, (x, y)): Light's Hope's people and Crown Guard's in the town, the rest out on the map
NPC_POSITIONS = {nid: (zone_key(LIGHTS_HOPE), xy) for nid, xy in TOWN_AT.items()}
NPC_POSITIONS.update({nid: (zone_key(EAST), xy) for nid, xy in EAST_AT.items()})
#: the two whose job changed when Crown Guard moved in: their greeting is rewritten, not kept
REWRITE_GREETING = {"epl_cg_innkeeper", "epl_cg_flight", "epl_cg_captain", "epl_cg_corporal"}
M, F = "male", "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the quest givers added with the quest pass (tools/plaguelands_quests_epl_east.py, _epl_west.py)
    "epl_cg_corporal": ("Corporal Ines Duarte", "human", F, 4, "down",
                        "I keep the chapel's water clean, which out here means I keep everyone alive. I ran water "
                        "treatment in Lisbon before the Integration. It's the same job, it's just missing the pipes."),
    "epl_cg_outrider": ("Outrider Bram Tolliver", "human", M, 6, "right",
                        "I ride the road west to the river and back, every day. Somebody has to, and the horse "
                        "doesn't seem to mind."),
    "epl_cg_widow": ("Edda Marris", "human", F, 2, "down",
                     "My husband's family farm is out west, at the stead. They're all still there. I come up here so "
                     "I don't have to watch them."),
    "epl_cg_mycologist": ("Dr. Sun Li", "human", F, 5, "left",
                          "I studied fungi in Kunming for twenty years, and I thought I'd seen everything a mushroom "
                          "could do. The vale out west has taught me otherwise."),
    "epl_cg_gravewarden": ("Gravewarden Osric Vey", "human", M, 3, "down",
                           "The Dawn buries its own, and anyone else who needs it. Terrordale's full of people "
                           "nobody buried, and I mean to change that."),
    "epl_lh_lightwarden": ("Lightwarden Ysolde Carrow", "human", F, 6, "down",
                           "We pray for the dead here, all of them, because nobody else in the east will. Sit a "
                           "while, if you need to."),
    "epl_lh_volunteer": ("Sergeant Marisol Reyes", "human", F, 3, "down",
                         "I was a paramedic in Monterrey. Now I run the chapel's infirmary, and I've got more "
                         "patients than beds. If you're bleeding, sit down. If you're not, can you carry something?"),
    "epl_lh_ranger": ("Ranger Faelis Dawnreach", "blood_elf", M, 4, "right",
                      "I served at Quel'Lithien Lodge, in the north. Everyone I served with is still there, and none "
                      "of them are resting."),
    "epl_lh_knight": ("Ser Roland Ashcombe", "human", M, 5, "left",
                      "I was a knight of Lordaeron before Stratholme fell. Now I watch the city for the Dawn, and I "
                      "try not to recognise the faces at the gate."),
    "epl_lh_huntress": ("Huntress Kaia Lindgren", "human", F, 4, "down",
                        "I herded reindeer outside Tromso before all this. The hunting's worse here, and so's the "
                        "weather, oddly enough."),
    "epl_ds_pamela": ("Pamela Redpath", "human", F, 1, "down",
                      "Have you seen my daddy? He went to fight the bad men and he hasn't come home yet. I'm being "
                      "ever so good while he's gone."),
    "epl_cg_captain": ("Captain Joss Varden", "human", M, 5, "down",
                       "Crown Guard's been knocked down twice and put back up twice, and it's standing empty now that "
                       "we're in here. Somebody still has to keep the road to Stratholme open, and that's us."),
    "epl_cg_innkeeper": ("Greta Lowe", "human", F, 3, "down",
                         "I kept the beds at Crown Guard. Jessa's got the beds here, so I've got the kitchen, and "
                         "nobody's complained yet. Mostly because they're eating."),
    "epl_cg_flight": ("Gwen Pike", "human", F, 6, "right",
                      "I flew Crown Guard's bats. Aldous has the perch here, so I look after the ones that come in "
                      "hurt. If you want to fly, he's the one to ask."),
    "epl_lh_commander": ("Commander Eligor Dawnbringer", "human", M, 7, "down",
                         "We don't ask where you came from. We ask whether you'll stand on the wall tonight, and most "
                         "people say yes."),
    "epl_lh_innkeeper": ("Innkeeper Jessa Moonfield", "human", F, 2, "down",
                         "The chapel's ground is holy and the dead won't cross it. You'll sleep better here than "
                         "anywhere else in the east."),
    "epl_lh_flight": ("Flight Master Aldous Grey", "human", M, 4, "right",
                      "The bats know every road you've walked. I'd fly over Stratholme rather than past it, if I "
                      "were you."),
    "epl_lh_scourgestones": ("Archmage Lysander Hale", "human", M, 6, "left",
                             "The Scourge carry shards of the necromancy that moves them. Bring me the stones and the "
                             "Dawn will remember who brought them."),
}

#: id -> (name, race, gender, variant, facing, greeting, sells, sells_gear)
VENDORS = {
    "epl_lh_quartermaster": ("Quartermaster Hasana Reed", "human", F, 5, "down",
                             "Argent steel and holy water, mostly. The good gear's for people the Dawn knows, and the "
                             "Dawn's got a long memory.",
                             ["healing_potion_masterwork", "mana_potion_masterwork", "kit_field_repair", "whetstone",
                              "bread_and_cheese", "drink_waterskin"], True),
}

SERVICES = {"epl_lh_innkeeper": ["inn"], "epl_lh_flight": ["flight"]}
#: Crown Guard's inn and roost closed when the camp moved in; those two offer nothing now
RETIRED_SERVICES = {"epl_cg_innkeeper": "inn", "epl_cg_flight": "flight"}
FLIGHT_NODES = [
    ("lights_hope", {"name": "Light's Hope Chapel", "zone": LIGHTS_HOPE, "master": "epl_lh_flight",
                     "pos": [158, 10], "continent": "eastern_kingdoms"}),
]
RETIRED_NODES = ["crown_guard"]
GEAR_LEVEL = 58


def main():
    names = set(AMBIENT) | set(VENDORS)
    if names != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(names ^ set(NPC_POSITIONS))}")
    ap, vp = ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"
    ad, vd = json.loads(ap.read_text(encoding="utf-8")), json.loads(vp.read_text(encoding="utf-8"))
    by_n = {r["npc_id"]: r for r in ad["npcs"]}
    by_v = {r["vendor_id"]: r for r in vd["vendors"]}
    from entities.consumable_manager import get_consumable_manager
    cm = get_consumable_manager()
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    made = moved = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        zone, (x, y) = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in by_n:
            moved += bool(safe_update(by_n[nid], rec))
            by_n[nid]["zone"] = zone                 # a move to another map is the layout's to make
            if nid in REWRITE_GREETING:
                by_n[nid]["greeting"] = greet
                by_n[nid]["name"] = name             # the title went with the job
        else:
            ad["npcs"].append(rec)
            made += 1
    for vid, (name, race, gender, var, facing, greet, sells, sg) in VENDORS.items():
        missing = [s for s in sells if not cm.has_consumable(s) and s not in mats]
        if missing:
            raise SystemExit(f"{vid} sells things that don't exist: {missing}")
        zone, (x, y) = NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=True, faction="neutral", gear_level=GEAR_LEVEL, sells_gear=sg, race=race,
                   appearance_variant=var, gender=gender, greeting=greet, facing=facing)
        if vid in by_v:
            moved += bool(safe_update(by_v[vid], rec))
            by_v[vid]["zone"] = zone
        else:
            vd["vendors"].append(rec)
            made += 1
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for nid, svc in RETIRED_SERVICES.items():
        left = [x for x in td["services"].get(nid, []) if x != svc]
        if left:
            td["services"][nid] = left
        else:
            td["services"].pop(nid, None)
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    for key in RETIRED_NODES:
        td["flight_nodes"].pop(key, None)
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Light's Hope Chapel and East EPL: {made} created, {moved} moved ({len(names)} people); one inn, one flight point")


if __name__ == "__main__":
    main()
