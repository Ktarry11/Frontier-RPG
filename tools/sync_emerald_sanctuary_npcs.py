#!/usr/bin/env python3
"""Create and position Emerald Sanctuary's people (claude/felwood_brief.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_emerald_sanctuary_npcs.py

The Emerald Reclamation is four peoples (Kyle, 14 Nov: "its a group thing, whole new faction!"), so the
town is too: night elf Sentinels and druids, Timbermaw furbolgs, treants, and transplants. Kyle: "Lets
have some earth people in the emerald sanctuary, they wont be recruits... we should start having more
earth people throughout zones." The four transplants here are just people who came and stayed.

Shops are the town's own (Kyle: "NEVER EVER default to garbage generic shops"): Sentinel arms and
armour, Timbermaw goods, the druids' herbs, the volunteers' kitchen. Tiered to level 52 by
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

from tools.handbuilt_emerald_sanctuary import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "emerald_sanctuary"
M, F = "male", "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "es_arch_druid": ("Arch Druid Aelyra Moonbough", "night_elf", F, 6, "down",
                      "Welcome to the Sanctuary. Everyone here came for a different reason, and we've stopped "
                      "asking which."),
    "es_sentinel_captain": ("Captain Saranis Duskwhisper", "night_elf", F, 2, "down",
                            "The Fel Line's north of the barricade. We hold it, and every week it's a little "
                            "further north than it was."),
    "es_timbermaw_elder": ("Elder Grumhall Oakpelt", "furbolg", M, 3, "left",
                           "The Timbermaw remember when the Deadwood were our cousins. We'd like to remember it "
                           "with them again."),
    "es_treant_elder": ("Old Thornbark", "treant", M, 1, "down",
                        "I was standing here before the glade was cleansed. I'd like to still be standing here "
                        "after."),
    "es_innkeeper": ("Innkeeper Nelanthe Softbough", "night_elf", F, 9, "down",
                     "There's a bed and a hot meal, and nobody will ask you to plant anything until morning."),
    "es_flight_master": ("Faelin Skybough", "night_elf", M, 4, "right",
                         "The hippogryphs fly anywhere you've been. They won't go near the Fel Line, and neither "
                         "should you without a reason."),
    "es_volunteer_medic": ("Dr. Nkechi Adeyemi", "human", F, 2, "down",
                           "I was an emergency doctor in Lagos. The wounds here are stranger, but the work's the "
                           "same. Sit down if you're bleeding."),
    "es_volunteer_carpenter": ("Tomasz Wolny", "human", M, 5, "down",
                               "I built houses outside Kraków. Now I build barricades, and the Sentinels tell me "
                               "I'm slow. I tell them it's called doing it properly."),
    "es_volunteer_botanist": ("Yuki Hashimoto", "human", F, 4, "left",
                              "I'm cataloguing everything that grows back. Three years ago I didn't know any of "
                              "these plants existed, and now I know more of them than I know people here."),
    "es_volunteer_runner": ("Ana Lúcia Ferreira", "human", F, 7, "right",
                            "First time in the Sanctuary? The inn's on your left, the roost's past it, and the "
                            "Arch Druid's at the well if you want to be useful."),
    "pt_emerald_sanctuary_herbs": ("Druid Talenwe Rootsong", "night_elf", M, 5, "down",
                                   "I'll teach you what grows on cleansed ground and what to make of it. Most "
                                   "of it heals. The rest you'll want to keep away from the soup."),
    "es_treant_warden": ("Barkwarden Elm", "treant", M, 0, "down",
                         "The Sentinels stand on the line, and so do I. The difference is that they talk more."),
}

#: id -> (name, race, gender, variant, facing, greeting, sells, sells_gear)
VENDORS = {
    "es_quartermaster": ("Quartermaster Ilyssa Thornbough", "night_elf", F, 3, "down",
                         "This is Sentinel steel, made for the north. If it's good enough for the barricade, "
                         "it's good enough for you.",
                         ["whetstone", "flux_strong", "kit_field_repair", "healing_potion_masterwork",
                          "mana_potion_masterwork", "beast_lure"], True),
    "es_timbermaw_trader": ("Trader Burlrock", "furbolg", M, 4, "left",
                            "We sell honey, rope and good wood. The transplants say our honey's the best they've "
                            "had, and I've decided to believe them.",
                            ["parchment", "glue", "component_string", "cook_honey", "drink_honeyed_mead",
                             "meal_saltback_roast", "beast_lure_lesser"], False),
    "es_herbalist": ("Druid Mirelle Fernsong", "night_elf", F, 7, "down",
                     "Everything I sell grew on the cleansed ground. It comes up faster here than anywhere I've "
                     "worked, and I'm still not sure why.",
                     ["vial_empty", "vial_leaded", "vial_crystal", "healing_potion_masterwork",
                      "mana_potion_dreamfoil", "elixir_of_greater_endurance", "guardian_elixir_superior",
                      "battle_elixir_superior"], False),
    "es_camp_cook": ("Luis Ortega", "human", M, 3, "down",
                     "I cooked for a hotel in Valencia for twenty years. Now I cook for elves, bears and trees, "
                     "and the bears eat the most.",
                     ["bread_and_cheese", "roasted_meat", "spiced_stew", "meal_saltback_roast", "drink_waterskin",
                      "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_water", "cook_mushroom"], False),
}

SERVICES = {"es_innkeeper": ["inn"], "es_flight_master": ["flight"]}
FLIGHT_NODE = ("emerald_sanctuary", {"name": "Emerald Sanctuary", "zone": "Emerald Sanctuary",
                                      "master": "es_flight_master", "pos": [-25, -95], "continent": "kalimdor"})
GEAR_LEVEL = 52


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
    # the Sanctuary teaches one trade pair only (Kyle: herbalism and alchemy)
    for r in ad["npcs"]:
        if r["npc_id"] == "pt_emerald_sanctuary_herbs":
            r.setdefault("trains_profession", ["herbalism", "alchemy"])
    tr = ROOT / "data/training/trainers.json"
    td_ = json.loads(tr.read_text(encoding="utf-8"))
    td_["profession_trainers"].setdefault("pt_emerald_sanctuary_herbs", ["herbalism", "alchemy"])
    tr.write_text(json.dumps(td_, indent=2) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    td["flight_nodes"].setdefault(*FLIGHT_NODE)
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Emerald Sanctuary: {made} created, {moved} moved ({len(names)} people), inn and flight registered")


if __name__ == "__main__":
    main()
