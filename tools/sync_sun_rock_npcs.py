#!/usr/bin/env python3
"""Create and position Sun Rock Retreat's people (docs/stonetalon_brief.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_sun_rock_npcs.py

Sun Rock is a tauren hold that got bigger when Thunder Bluff fell. Its quest givers pay four reputations (Kyle,
15 Nov 2026: "Thunder bluff, steamwheedle, and orgrimmar. Maybe one or two forsaken"), so the envoys of the other
three stand in it as well. Every town has an inn, a flight master and one class trainer for every class, and the
trades are taught in themed pairs. Shops are the town's own (Kyle: "NEVER EVER default to garbage generic
shops"): tauren arms and armour, a trading post, a provisioner. Tiered to level 30 by
tools/overhaul_vendor_stock.py --vendors after this runs.

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_sun_rock_retreat import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "sun_rock_retreat"
M, F = "male", "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "sr_elder": ("Elder Muhana Windhoof", "tauren", F, 6, "down",
                 "Sun Rock used to be a quiet place to sit and watch the mountain. Now half of Thunder Bluff sleeps "
                 "on it, and I'm the one they come to when something goes wrong."),
    "sr_spirit_walker": ("Spiritwalker Tohana", "tauren", M, 11, "down",
                         "The spirits here are restless. They were restless before the mountain blew, and it hasn't "
                         "helped."),
    "sr_watch_captain": ("Watch Captain Ahrok Stonemane", "tauren", M, 3, "right",
                         "From this tower you can see the whole Blowdown. You can also see the Venture Co. carting "
                         "it away, which I'd rather not watch."),
    "sr_rim_watcher": ("Kuna Ashhorn", "tauren", F, 9, "right",
                       "That's Mulgore out there. You can see where the daylight stops. I watch it so the people "
                       "who came from there don't have to."),
    "sr_refugee_mother": ("Halona Stillwater", "tauren", F, 12, "down",
                          "We carried out what we could. It turned out to be less than we thought, and more than "
                          "some people managed."),
    "sr_refugee_hunter": ("Tavo Longrun", "tauren", M, 5, "down",
                          "I hunted Mulgore my whole life. I know every trail in it. I'm not going back to see what's "
                          "walking them now."),
    "sr_orgrimmar_envoy": ("Envoy Garnak", "orc", M, 4, "left",
                           "Orgrimmar sent me to make sure Sun Rock holds. The Grimtotem think it won't. I'd like to "
                           "prove them wrong before they try."),
    "sr_steamwheedle_agent": ("Pixie Brightcog", "goblin", F, 2, "down",
                              "The Cartel and the Venture Co. aren't friends, whatever the tauren think. They're "
                              "ruining a perfectly good forest and a perfectly good reputation for goblins."),
    "sr_forsaken_apothecary": ("Apothecary Merrow Vane", "forsaken", M, 3, "left",
                               "The tauren don't want me here, and I understand that. But something in Mulgore is "
                               "getting the dead back on their feet, and that's my field."),
    "sr_transplant_geologist": ("Dr. Hannah Lindqvist", "human", F, 3, "down",
                                "I studied volcanoes in Washington State before all this. The one up there looks "
                                "exactly like one I worked on, and it shouldn't be here at all."),
    "sr_innkeeper": ("Innkeeper Kauwa", "tauren", F, 4, "down",
                     "There's a bed, a fire and a hot meal. It's crowded, so if somebody's asleep in your bed, "
                     "wake them gently."),
    "sr_flight_master": ("Tal Windstrider", "tauren", M, 7, "right",
                         "The wind riders fly anywhere you've been. They don't like the air over the Blowdown, "
                         "with all that ash in it, so it's a bumpy ride."),
    "ct_sun_rock": ("Trainer Mesa Proudhorn", "tauren", F, 1, "down",
                    "I've trained every kind of fighter and caster that's come up this rock. Tell me what you are "
                    "and I'll show you what's next."),
    "pt_sun_rock_forge": ("Forgemaster Brak Ironhoof", "tauren", M, 8, "down",
                          "I teach mining and the forge together, and gems if you've got the patience. There's good "
                          "iron in the Blowdown now that the trees aren't sitting on it."),
    "pt_sun_rock_hide": ("Tanner Ohanzee", "tauren", M, 14, "down",
                         "Skinning, leather, cloth and cooking, all from the same kill. Pay once and I'll teach you "
                         "the lot."),
    "pt_sun_rock_herbs": ("Herbalist Nawa Greenmane", "tauren", F, 15, "down",
                          "Herbs and alchemy. Fireweed's the first thing to grow back after a burn, and it turns "
                          "out it's good for more than looking pretty."),
    "pt_sun_rock_wood": ("Woodwright Kesh Highfeather", "tauren", M, 6, "left",
                         "Woodcutting and woodworking. I won't teach you to fell the standing giants. Fallen wood's "
                         "fair; the living trees aren't."),
}

#: id -> (name, race, gender, variant, facing, greeting, sells, sells_gear)
VENDORS = {
    "sr_trader": ("Trader Hania Swiftbrook", "tauren", F, 10, "down",
                  "Rope, salt, thread, lures. Everything you need to live on a mountain, and a few things you don't.",
                  ["parchment", "component_string", "salt", "tanning_reagent", "sinew", "vial_empty",
                   "kit_field_repair", "beast_lure_lesser", "beast_lure", "healing_potion_greater",
                   "mana_potion_greater"], False),
    "sr_armsmith": ("Armsmith Ruuk Bloodmane", "tauren", M, 2, "down",
                    "Tauren steel and tauren leather. It's heavy, it's honest, and it doesn't break.",
                    ["whetstone", "flux_medium", "coal", "kit_field_repair"], True),
    "sr_provisioner": ("Provisioner Wahya", "tauren", F, 13, "down",
                       "Food's simple up here. Roast, bread, stew, and water from the spring. Nobody's complained "
                       "yet.",
                       ["roasted_meat", "bread_and_cheese", "spiced_stew", "meal_trailbread", "meal_spiced_haunch",
                        "drink_waterskin", "drink_spring_flask", "drink_barley_beer", "cook_flour", "cook_water",
                        "cook_spice", "cook_roots"], False),
}

SERVICES = {"sr_innkeeper": ["inn"], "sr_flight_master": ["flight"]}
#: between Astranaar (-45,-50) to the north-east, the Crossroads (-8,40) to the east and Camp Taurajo (-5,85)
FLIGHT_NODE = ("sun_rock_retreat", {"name": "Sun Rock Retreat", "zone": "Sun Rock Retreat",
                                    "master": "sr_flight_master", "pos": [-62, 10], "continent": "kalimdor"})
TRAINERS = {
    "pt_sun_rock_forge": ["mining", "blacksmithing", "jewelcrafting"],
    "pt_sun_rock_hide": ["skinning", "leatherworking", "tailoring", "cooking", "fishing"],
    "pt_sun_rock_herbs": ["herbalism", "alchemy"],
    "pt_sun_rock_wood": ["woodcutting", "woodworking"],
}
GEAR_LEVEL = 30


def main():
    names = set(AMBIENT) | set(VENDORS)
    if names != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(names ^ set(NPC_POSITIONS))}")
    ap, vp = ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"
    ad, vd = json.loads(ap.read_text(encoding="utf-8")), json.loads(vp.read_text(encoding="utf-8"))
    by_n = {r["npc_id"]: r for r in ad["npcs"]}
    by_v = {r["vendor_id"]: r for r in vd["vendors"]}
    made = moved = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=ZONE, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid == "ct_sun_rock":
            rec["trains_class"] = "*"
        if nid in TRAINERS:
            rec["trains_profession"] = TRAINERS[nid]
        if nid in by_n:
            moved += bool(safe_update(by_n[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    for vid, (name, race, gender, var, facing, greet, sells, sg) in VENDORS.items():
        x, y = NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=ZONE, x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=True, faction="neutral", gear_level=GEAR_LEVEL, sells_gear=sg, race=race,
                   appearance_variant=var, gender=gender, greeting=greet, facing=facing)
        if vid in by_v:
            moved += bool(safe_update(by_v[vid], rec))
        else:
            vd["vendors"].append(rec)
            made += 1
    tr = ROOT / "data/training/trainers.json"
    td_ = json.loads(tr.read_text(encoding="utf-8"))
    td_["class_trainers"].setdefault("ct_sun_rock", "*")
    for k, v in TRAINERS.items():
        td_["profession_trainers"].setdefault(k, v)
    tr.write_text(json.dumps(td_, indent=2) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    td["flight_nodes"].setdefault(*FLIGHT_NODE)
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Sun Rock Retreat: {made} created, {moved} moved ({len(names)} people), inn, flight and trainers registered")


if __name__ == "__main__":
    main()
