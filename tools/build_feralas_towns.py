#!/usr/bin/env python3
"""Feralas's people: Camp Mojache, Feathermoon Stronghold, and the few who live out on the three maps (the settlers
of Cedar Hollow, the Sentinels' Watch, Mojache's scout). Inns, the two flight paths, the trainers and the shops.
Idempotent.

    PYTHONPATH=. python3 tools/build_feralas_towns.py

docs/feralas_brief.md and docs/feralas_quest_plan.md. Kyle, 19 Nov 2026: Mojache is "grown with refugees" and answers
to Elder Longtread at Camp Taurajo; Feathermoon is the Sentinels' and their new faction's home, led by Shandris
Feathermoon; every town has an inn and a flight master, and a zone never gets two flight paths (each town is its own
map, and the Twin Colossals has none).

THE QUARTERMASTER CAN MOVE. fm_quartermaster gives and takes no quests (the same rule as the Sunreach Conclave's), so
the Sentinels' shelf can be placed or moved without touching a quest. Her shelf comes with the faction's rewards.

Every person stands where their map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_camp_mojache as MJ  # noqa: E402
from tools import handbuilt_feathermoon_stronghold as FM  # noqa: E402
from tools import handbuilt_feralas_forgotten_coast as FC  # noqa: E402
from tools import handbuilt_feralas_high_wilderness as HW  # noqa: E402
from tools import handbuilt_feralas_twin_colossals as TC  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"
MAPS = {"mojache": MJ, "feathermoon": FM, "coast": FC, "wilderness": HW, "colossals": TC}

SERVICES = {"moj_innkeeper": ["inn"], "moj_flight_master": ["flight"], "fm_innkeeper": ["inn"],
            "fm_flight_master": ["flight"]}
FLIGHT_NODES = [
    ("camp_mojache", {"name": "Camp Mojache", "zone": MJ.NAME, "master": "moj_flight_master", "pos": [-62, 142],
                      "continent": "kalimdor"}),
    ("feathermoon_stronghold", {"name": "Feathermoon Stronghold", "zone": FM.NAME, "master": "fm_flight_master",
                                "pos": [-98, 120], "continent": "kalimdor"}),
]
CLASS_TRAINERS = ("ct_mojache", "ct_feathermoon")
TRAINERS = {
    "pt_moj_hide": ["skinning", "leatherworking"],
    "pt_moj_herbs": ["herbalism", "alchemy"],
    "pt_fm_herbs": ["herbalism", "alchemy"],
    "pt_fm_fish": ["cooking", "fishing"],
}
MOVABLE = ("fm_quartermaster",)

#: vendor_id -> (map, name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "moj_smith": ("mojache", "Forgewright Taima Stonehoof", "tauren", F, 6, "left", 46, True,
                  ["whetstone", "flux_strong", "coal", "kit_field_repair", "bs_mithril_shield"],
                  "I left my anvil in Thunder Bluff. This one's a rock we dragged out of the river, and it rings "
                  "almost as true. Bring me what's broken."),
    "moj_provisioner": ("mojache", "Provisioner Wahya Tallhorn", "tauren", F, 9, "down", 45, False,
                        ["meal_kodo_ribs", "meal_saltback_roast", "drink_birch_wine", "drink_deepwell_cordial",
                         "hunters_brace_platter", "cook_flour", "cook_spice", "cook_water", "cook_mushroom"],
                        "We feed twice as many as this camp was built for, and nobody's gone hungry yet. The hunters "
                        "bring in the elk and I make it stretch."),
    "fm_smith": ("feathermoon", "Armourer Elanis Starblade", "night_elf", F, 3, "left", 47, True,
                 ["whetstone", "flux_strong", "kit_field_repair", "bs_mithril_shield"],
                 "The Sentinels' armoury keeps every glaive on this island sharp. I'll do yours too, as long as you "
                 "don't let it get that bad again."),
    "fm_provisioner": ("feathermoon", "Provisioner Ralanna Leafsong", "night_elf", F, 5, "down", 47, False,
                       ["meal_cooked_nightfin_soup", "meal_saltback_roast", "drink_deepwell_cordial",
                        "drink_birch_wine", "cook_flour", "cook_spice", "cook_water", "cook_mushroom"],
                       "Nightfin soup, fresh from the boats this morning. The Sentinels eat it every night and "
                       "complain about it every night, and they'd riot if I stopped."),
    "fm_quartermaster": ("feathermoon", "Quartermaster Lyriel Dawnbough", "night_elf", F, 4, "down", 48, True,
                         ["kit_field_repair", "healing_potion_sansam", "mana_potion_dreamfoil", "barbed_arrows"],
                         "The Sentinels' stores. Most of what's on these shelves goes to the women on the walls, and "
                         "the rest goes to people who've earned Shandris's trust. Earn it and we'll talk."),
}
#: npc_id -> (map, name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---------------------------------------------------------------- Camp Mojache
    "moj_innkeeper": ("mojache", "Innkeeper Greul", "tauren", M, 7, "down",
                      "There are more bedrolls than beds now, but there's a fire and a roof for everyone. I'll bind "
                      "your hearth here if you want to come back to us."),
    "moj_flight_master": ("mojache", "Wind Rider Master Shyn", "tauren", F, 4, "down",
                          "The wind riders carried half the camp out of the Needles on their backs. They'll carry "
                          "you anywhere you've already been."),
    "moj_gate_brave": ("mojache", "Brave Takoda Mistrunner", "tauren", M, 5, "down",
                       "Welcome to Mojache. Keep your weapons sheathed inside the totems, and don't ask the new "
                       "arrivals where they came from. If they want to tell you, they will."),
    "moj_chieftain": ("mojache", "Chieftain Ahanu Swiftstrider", "tauren", F, 10, "down",
                      "When the first of them walked in out of the Needles, half starved, I didn't count them. I "
                      "just opened the gate. Mojache is twice what it was, and I'd do it again."),
    "moj_hadoken": ("mojache", "Hadoken Swiftstrider", "tauren", M, 8, "right",
                    "My sister runs the camp and I keep it fed. The forest gives plenty, if the gnolls and the "
                    "Grimtotem would leave us enough of it to hunt."),
    "moj_elder_nayeli": ("mojache", "Elder Nayeli Cloudhoof", "tauren", F, 13, "down",
                         "I walked out of Mulgore with forty others and a cart of totems. Thirty-one of us got here. I "
                         "say the names of the other nine every night, so the forest learns them too."),
    "moj_krueg": ("mojache", "Krueg Skullsplitter", "orc", M, 4, "down",
                  "Orgrimmar keeps an eye on this camp, and I'm the eye. Mostly I watch the ogres at Dire Maul's "
                  "gate, and lately they've been watching back."),
    "moj_orwin": ("mojache", "Orwin Gizzmick", "goblin", M, 3, "down",
                  "I came out here to buy silithid resin, because it sells. Then I found out where it comes from, and "
                  "now I'm the one asking adventurers to go and look. Business has its days."),
    "ct_mojache": ("mojache", "Trainer Ishana Brightmane", "tauren", F, 6, "down",
                   "Whatever you came here as, I can teach you the next of it. The camp needs everyone at their best, "
                   "and that includes you."),
    "moj_brann": ("mojache", "Brann Tallgrass", "tauren", M, 2, "down",
                  "I keep the list. Everyone who walked in, where they came from, who they're looking for. It's a long "
                  "list, and the part with the names crossed off is getting longer."),
    "pt_moj_hide": ("mojache", "Hidewright Onawa Redcloud", "tauren", F, 11, "left",
                    "Skinning and leather. Nothing that dies in this forest goes to waste in this camp, not while "
                    "there are people sleeping under bare poles."),
    "pt_moj_herbs": ("mojache", "Herbalist Kele Windsong", "tauren", M, 9, "down",
                     "Herbs and alchemy. The forest here grows things I'd never seen in Mulgore, and a few I'd never "
                     "seen anywhere, from where the strange trees came in."),
    # ---------------------------------------------------------------- Feathermoon Stronghold
    "fm_harbour_sentinel": ("feathermoon", "Sentinel Aelyra Tidewatch", "night_elf", F, 3, "down",
                            "Welcome to Feathermoon. Transplants may land, and plenty have. Keep to the paths and "
                            "speak to the General if you're looking for work."),
    "fm_innkeeper": ("feathermoon", "Innkeeper Shyria", "night_elf", F, 2, "down",
                     "The inn's small and the walls are thick, and nobody's ever been cold in here. I'll bind your "
                     "hearth to the island if you'd like."),
    "fm_shandris": ("feathermoon", "Shandris Feathermoon", "night_elf", F, 8, "down",
                    "I've held this island through wars that would have ended your world twice over. The sea has been "
                    "restless since the merge, and so has the coast. If you're here to help, there's work."),
    "fm_latronicus": ("feathermoon", "Latronicus Moonspear", "night_elf", M, 6, "down",
                      "I keep the record of the Highborne ruins on this coast, what's standing and what's been taken. "
                      "Lately the second list grows faster than I can write it."),
    "fm_selarin": ("feathermoon", "Sentinel Selarin", "night_elf", F, 4, "right",
                   "I watch the coast from here to Sardor Isle. The Hatecrest come up the beaches at night now, and "
                   "they don't come to raid. They come to dig."),
    "fm_kindal": ("feathermoon", "Kindal Moonweaver", "night_elf", F, 7, "down",
                  "There's a forest on the coast that wasn't there three years ago. The trees are older than they "
                  "should be, and they don't answer when I speak to them. The people living under them do."),
    "fm_jalara": ("feathermoon", "Huntress Jalara Nightwind", "night_elf", F, 5, "left",
                  "The chimaeras on the Isle of Dread have started going for the boats. A chimaera doesn't change "
                  "its hunting ground without a reason, and I'd like to know what it is."),
    "ct_feathermoon": ("feathermoon", "Trainer Nalia Moonbrow", "night_elf", F, 3, "down",
                       "The Sentinels train every sister on this island, and the General says we train you too. Tell "
                       "me what you are and I'll show you what's next."),
    "pt_fm_herbs": ("feathermoon", "Herbalist Taelan Greenleaf", "night_elf", M, 4, "down",
                    "Herbs and alchemy. The coast grows lotus and sungrass for anyone patient enough to look, and the "
                    "Sentinels go through healing draughts faster than I can brew them."),
    "pt_fm_fish": ("feathermoon", "Fisherwoman Elyssa Gullwind", "night_elf", F, 6, "down",
                   "Cooking and fishing. The nightfin run off this island every evening, and if you can't catch one "
                   "here, you can't catch one anywhere."),
    "fm_flight_master": ("feathermoon", "Fyldren Moonfeather", "night_elf", M, 4, "down",
                         "The hippogryphs fly the coast and inland as far as you've been. They don't fly over the "
                         "Isle of Dread, and neither would you if you'd seen what nests there."),
    # ---------------------------------------------------------------- the High Wilderness
    "fe_scout_wapi": ("wilderness", "Scout Wapi Longstride", "tauren", M, 5, "left",
                      "You came down off the mountain? So did half my camp. Camp Mojache is just west of here, inside "
                      "the totems. Tell them Wapi sent you."),
    # ---------------------------------------------------------------- the Forgotten Coast: Cedar Hollow and the landing
    "fe_settler_june": ("coast", "June Nakamura", "human", F, 4, "down",
                        "I was a ranger in Olympic National Park for sixteen years. I know every one of these trees by "
                        "name, and none of them should be on this continent."),
    "fe_settler_walt": ("coast", "Walt Hollis", "human", M, 9, "down",
                        "I logged out of Forks for thirty years. Then I woke up under the same trees on the other side "
                        "of the world, and I haven't cut a single one. Felt like I owed them that."),
    "fe_settler_rosa": ("coast", "Rosa Ibarra", "human", F, 3, "down",
                        "I was an ER nurse in Tacoma. Out here I'm the only nurse, and the closest thing to a pharmacy "
                        "is whatever grows by the creek. So I've learned what grows by the creek."),
    "fe_settler_sam": ("coast", "Sam Okonkwo", "human", M, 5, "down",
                       "I studied fungus at Portland State. The mushrooms in these groves came with the trees, and "
                       "some of them are spreading into the old forest. Nobody here knows what that means yet, "
                       "including me."),
    "fe_landing_sentinel": ("coast", "Sentinel Mirael Duskbrook", "night_elf", F, 3, "down",
                            "The boats leave for Feathermoon from this pier. Step aboard if the General's expecting "
                            "you, or if you want her to be."),
    # ---------------------------------------------------------------- the Twin Colossals
    "fe_watch_captain": ("colossals", "Sentinel Aerwyn Starbrook", "night_elf", F, 6, "down",
                         "This is the Sentinels' Watch, as far north as Feathermoon reaches. From here we can see the "
                         "Colossals, Ravenwind and the Bough, and lately none of them are quiet."),
    "fe_watch_tahu": ("colossals", "Tahu Swiftrunner", "tauren", M, 6, "down",
                      "Mojache sent me north after the Rage Scar. The yetis have come down out of their hold, and a "
                      "yeti doesn't leave its hold for nothing."),
    "fe_dreamwatcher": ("colossals", "Dreamwatcher Sylanna", "night_elf", F, 9, "left",
                        "The Circle sent me from Moonglade. The stones there are warm at night, and so are this tree's "
                        "roots. I'd like to know whether it's the same warmth."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    for key, mod in MAPS.items():
        mine = {k for k, v in list(VENDORS.items()) + list(AMBIENT.items()) if v[0] == key}
        if mine != set(mod.NPC_POSITIONS):
            bad.append(f"{mod.NAME}: roster and layout disagree: {sorted(mine ^ set(mod.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    for sid in TRAINERS:
        if sid not in AMBIENT:
            bad.append(f"trainer {sid} has no record")
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (key, name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        mod = MAPS[key]
        zone = zone_key(mod.NAME)
        x, y = mod.NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
            vby[vid]["zone"] = zone
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (key, name, race, gender, var, facing, greet) in AMBIENT.items():
        mod = MAPS[key]
        zone = zone_key(mod.NAME)
        x, y = mod.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in CLASS_TRAINERS:
            rec["trains_class"] = "*"
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
            aby[nid]["zone"] = zone
        else:
            ad["npcs"].append(rec)
            made += 1
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)

    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    tr = load("data/training/trainers.json")
    for ct in CLASS_TRAINERS:
        tr["class_trainers"].setdefault(ct, "*")
    for k, v in TRAINERS.items():
        tr["profession_trainers"][k] = list(v)
    (ROOT / "data/training/trainers.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")

    tied = []
    for qf in sorted((ROOT / "data/quests").glob("*.json")):
        d = json.loads(qf.read_text(encoding="utf-8"))
        for q in d.get("quests", []) if isinstance(d, dict) else []:
            for k in ("giver_npc_id", "turn_in_npc_id"):
                if q.get(k) in MOVABLE:
                    tied.append(f"{qf.name}: {q.get('quest_id')} {k}={q.get(k)}")
    if tied:
        raise SystemExit("the movable quartermaster is tied to quests:\n  " + "\n  ".join(tied))
    print(f"Feralas: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
