#!/usr/bin/env python3
"""Talrendis Landing's people, its inn and its wind riders. Idempotent.

    PYTHONPATH=. python3 tools/build_talrendis_landing.py

The Landing is Azshara's Horde hub (docs/azshara_brief.md; the map is tools/handbuilt_talrendis_landing.py): an arcane
salvage camp where Orgrimmar provides the muscle and the Sunreach Conclave's blood elves provide the magisters. It has
an inn and Azshara's one flight master. Earth transplants work on the salvage crews (Kyle: Earth "shows up a lot"
in the 50s).

THE SUNREACH CONCLAVE'S PEOPLE ARE MOVABLE. Kyle, 17 Nov 2026: "Don't tie leader or anything to a quest so they can be
moved" and "The elves can get an island later". So tl_sunreach_magister (the Conclave's leader here) and
tl_sunreach_quartermaster give and take no quests, ever: the Conclave's quests come from other magisters. Its
reputation and shelf come with the quest pass; until then the quartermaster sells field supplies.

Positions come from the map's NPC_POSITIONS; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.handbuilt_talrendis_landing import NAME, NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

ZONE = zone_key(NAME)
SERVICES = {"tl_innkeeper": ["inn"], "tl_flight_master": ["flight"]}
FLIGHT_NODES = [
    ("talrendis_landing", {"name": "Talrendis Landing", "zone": NAME, "master": "tl_flight_master",
                           "pos": [30, -78], "continent": "kalimdor"}),
]
#: the people who must never give or take a quest (they move to the Conclave's island later)
MOVABLE = ("tl_sunreach_magister", "tl_sunreach_quartermaster")
M, F = "male", "female"

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "tl_smith": ("Forgemaster Gharza Ironbrow", "orc", F, 4, "right", 54, True,
                 ["kit_field_repair", "whetstone", "flux_strong", "healing_potion_masterwork"],
                 "Half of what comes out of that dig is Highborne steel ten thousand years old, and it still takes an "
                 "edge better than mine. I hate that. Bring me your gear and I'll fix it anyway."),
    "tl_provisioner": ("Provisioner Dana Whitfield", "human", F, 5, "down", 54, False,
                       ["meal_saltback_roast", "drink_deepwell_cordial", "hunters_brace_platter", "cook_flour",
                        "cook_spice", "cook_water", "cook_mushroom", "beast_lure"],
                       "I ran the canteen on an oil rig in the North Sea for nine years. Two crews who can't stand "
                       "each other, a long way from anywhere, and everyone gets fed the same. This is just warmer."),
    "tl_sunreach_quartermaster": ("Quartermaster Sylvaen Dawnward", "blood_elf", M, 3, "left", 54, True,
                                  ["mana_potion_masterwork", "healing_potion_masterwork", "vial_crystal", "parchment",
                                   "kit_field_repair"],
                                  "The Conclave keeps a field store for its own and for anyone who works beside us. "
                                  "Everything you see came by ship from Quel'Thalas, so please don't haggle."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "tl_innkeeper": ("Innkeeper Mohammed Saleh", "human", M, 4, "down",
                     "I had a guesthouse in Aqaba, on the Red Sea, before the Integration, and most of my guests "
                     "were divers. Now it's orcs who snore and elves who complain about them, and it's the same job. "
                     "Sleep while you can."),
    "tl_flight_master": ("Windrider Master Kragga", "orc", F, 2, "down",
                         "The wyverns go anywhere you've already been. They don't like the coast, because something "
                         "big moves out past the spires at night, and I don't make them fly over it."),
    "tl_gate_grunt": ("Grunt Mazkar", "orc", M, 3, "down",
                      "Orc on this side of the gate, elf on that side. We take turns being the one who's right."),
    "tl_gate_spellbreaker": ("Spellbreaker Ilanthe", "blood_elf", F, 2, "down",
                             "I watch the road for satyrs. The grunt watches the road for satyrs. Neither of us "
                             "watches the other, officially."),
    "tl_overseer": ("Overseer Durgash Stonejaw", "orc", M, 5, "down",
                    "Orgrimmar sent me to keep the dig honest. Everything that comes up out of the ground gets "
                    "counted twice, once by me and once by the elves, and the counts never match."),
    # the quest pass's people (docs/azshara_quest_plan.md): they give the Landing's quests, so the two above don't have to
    "tl_conclave_archivist": ("Magister Caelin Brightspire", "blood_elf", M, 2, "down",
                              "I catalogue everything that comes out of the ground. The orcs catalogue it too, and "
                              "then we compare lists, and then we argue about the lists."),
    "tl_conclave_dig_magister": ("Magistrix Ysolde Emberwind", "blood_elf", F, 3, "right",
                                 "There's a ward under this courtyard older than Silvermoon, and it's still awake. "
                                 "Mind where you put your feet."),
    "tl_salvage_boss": ("Salvage Boss Rukka Ironhide", "orc", F, 4, "down",
                        "My crews do the lifting and the elves do the pointing. If you've got arms and you're not "
                        "afraid of a ghost, I've got work."),
    "tl_archaeologist": ("Dr. Amara Okafor", "human", F, 3, "down",
                         "I dug Iron Age sites in Nigeria for twenty years and I've never seen anything like this. "
                         "Both sides pay me, and both sides think I'm theirs. I'm the dig's."),
    "tl_farseer": ("Farseer Thrag Windcaller", "orc", M, 5, "left",
                   "The leylines under this coast are pulling toward the sea. The elves say that's fine. The spirits "
                   "say it isn't."),
    "tl_sunreach_magister": ("Grand Magister Velanthe Sunreach", "blood_elf", F, 4, "down",
                             "Our ancestors lived on this coast before the Sundering, and now the sea is giving the "
                             "city back. The Conclave means to be standing on the shore when it does."),
}


def main():
    roster = set(VENDORS) | set(AMBIENT)
    if roster != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(roster ^ set(NPC_POSITIONS))}")
    from tools.build_tempest_quests import voice_problems
    bad = [f"{k}: {p}" for k, v in list(VENDORS.items()) + list(AMBIENT.items()) for p in voice_problems(v[-1])]
    if bad:
        raise SystemExit("FAILED - fix the greetings:\n  " + "\n  ".join(bad))

    vp, ap = ROOT / "data/npcs/vendors.json", ROOT / "data/npcs/ambient_npcs.json"
    vd, ad = json.loads(vp.read_text(encoding="utf-8")), json.loads(ap.read_text(encoding="utf-8"))
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=ZONE, x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
            vby[vid]["zone"] = ZONE
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=ZONE, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
            aby[nid]["zone"] = ZONE
        else:
            ad["npcs"].append(rec)
            made += 1
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the movable two: no quest may name them as giver or turn-in
    tied = []
    for qf in sorted((ROOT / "data/quests").glob("*.json")):
        d = json.loads(qf.read_text(encoding="utf-8"))
        for q in d.get("quests", []) if isinstance(d, dict) else []:
            for key in ("giver_npc_id", "turn_in_npc_id"):
                if q.get(key) in MOVABLE:
                    tied.append(f"{qf.name}: {q.get('quest_id')} {key}={q.get(key)}")
    if tied:
        raise SystemExit("the Conclave's movable people are tied to quests:\n  " + "\n  ".join(tied))
    print(f"Talrendis Landing: {made} created, {moved} moved ({len(roster)} people)")


if __name__ == "__main__":
    main()
