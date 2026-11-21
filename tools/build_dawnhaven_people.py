#!/usr/bin/env python3
"""Dawnhaven's people (docs/dawnhaven_brief.md): Amberwatch, Dawnrest, the Withered Spires, Firstlight Spire, the
Durotar pier's dockhand, the services, the island's flight path, the Sunreach Conclave's move home, and the two
recruits. Idempotent; positions come from the maps' NPC_POSITIONS (a person in one and not the other stops it).

    PYTHONPATH=. python3 tools/build_dawnhaven_people.py

THE CONCLAVE MOVES HOME. Kyle, 21 Nov 2026: Firstlight Spire is the Sunreach Conclave's home. Grand Magister Velanthe
and Quartermaster Sylvaen move from Talrendis Landing to the Spire; they still give and take no quests, so either can
move again (checked here and in tools/build_talrendis_landing.py).

RECRUITS. Kyle: "We have some unused recruits. We always want at least a Healer at the start of the game." Liam
Hartigan (Sun Cleric, healer), the paramedic who meets new arrivals on the Waking Shore, and Haruto Nakamura (Runemaster,
melee), copying the outpost's runes at the Withered Spires before they fade.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.zone_keys import zone_key  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from tools import handbuilt_dawnhaven_amberleaf as AL  # noqa: E402
from tools import handbuilt_dawnhaven_duskfall as DF  # noqa: E402
from tools import handbuilt_firstlight_spire as FS  # noqa: E402

M, F = "male", "female"
MOVABLE = ("tl_sunreach_magister", "tl_sunreach_quartermaster")
DUROTAR_DOCK = (119, 84)

FOOD = ["bread_and_cheese", "roasted_meat", "meal_tough_jerky", "meal_trailbread", "drink_waterskin",
        "drink_barley_beer", "cook_flour", "cook_honey", "cook_spice", "cook_mushroom", "cook_fruit", "cook_water"]
GOODS = ["healing_potion_minor", "mana_potion_minor", "vial_empty", "parchment", "small_burlap_sack",
         "worn_leather_satchel", "beast_lure_lesser", "kit_field_repair", "healing_potion_standard"]

#: npc_id -> (zone module, name, race, gender, variant, facing, greeting, extra fields)
AMBIENT = {
    # ---- the Waking Shore and Amberwatch
    "dh_saelis": (AL, "Ranger-Captain Saelis Dawnbrook", "blood_elf", F, 3, "down",
                  "Take it easy, you're all right. You're on Dawnhaven, an island off the coast of Azshara, and you're safe. Everyone "
                  "wakes up on this shore confused. Sit until the sand stops moving.", {}),
    "dh_iriel": (AL, "Magistrix Iriel Brightleaf", "blood_elf", F, 5, "down",
                 "The wardstones kept this island hidden for a thousand years. Now they're broken, and things are "
                 "finding us. I mean to mend them, one stone at a time.", {}),
    "dh_thaelen": (AL, "Apothecary Thaelen", "blood_elf", M, 30, "left",
                   "Sit down if you're dizzy. The first day here does that to everyone. I've got tea for the shaking, "
                   "and something stronger for the dreams.", {}),
    "dh_rosa": (AL, "Rosa Quintero", "human", F, 6, "down",
                "I built houses in Valparaiso for twenty-two years, on hills worse than this one. The elves know "
                "magic. I know roofs, and right now the roofs are winning.", {}),
    "dh_kaelen": (AL, "Scout Kaelen Swiftarrow", "blood_elf", M, 19, "right",
                  "There are naga on the south-east beach, and they weren't there a month ago. Keep your voice down "
                  "near the cove.", {}),
    "dh_aldaria": (AL, "Priestess Aldaria Morningsong", "blood_elf", F, 22, "down",
                   "The outpost buried its own at the Silent Barrow, up the north-west road, and they don't sleep the "
                   "way they should. I keep their names here, and some nights they come asking for them.", {}),
    "ct_amberwatch": (AL, "Trainer Aelwyn Starsong", "blood_elf", F, 8, "down",
                      "Every one of the disciplines came through Amberwatch at one time or another, and I've taught "
                      "them all. Tell me which is yours, and we'll begin.", {"trains_class": "*"}),
    "pt_dawnhaven_herbs": (AL, "Herbalist Mireth", "blood_elf", F, 24, "down",
                           "Peacebloom in the grove, silverleaf by the mere, earthroot wherever the ground's been "
                           "turned. That's where to start, and I'll show you how.", {"trains_profession": ["herbalism"]}),
    "pt_dawnhaven_forge": (AL, "Prospector Daelan", "blood_elf", M, 22, "down",
                           "Copper in the stones at the wardstones, and there's more under the barrow, if you don't "
                           "mind the company. I'll teach you to dig it out.", {"trains_profession": ["mining"]}),
    "pt_dawnhaven_skins": (AL, "Tanner Ysolde", "blood_elf", F, 15, "down",
                           "Every boar and lynx on this island is a hide somebody needs. Learn to take it cleanly, and "
                           "Rosa will pay you in roofing.", {"trains_profession": ["skinning"]}),
    # ---- Dawnrest and the woods
    "dh_selanne": (DF, "Lightwarden Selanne Dawnsworn", "blood_elf", F, 8, "down",
                   "The Lightwell fed this whole outpost once, and it's dark now. Light it again, and Dawnhaven stops "
                   "being a ruin we're hiding in. It becomes a home.", {}),
    "dh_aeron": (DF, "Magister Aeron Ashveil", "blood_elf", M, 17, "left",
                 "The outpost's magic didn't die when the well went dark. It spilled out into the woods. Some of it has woken up in the "
                 "thicket, and it's hungry.", {}),
    "dh_lyra": (DF, "Huntress Lyra Swiftbough", "blood_elf", F, 9, "down",
                "The Red Hollow feeds us, if you hunt it properly. Something's made the bears bold this year, and "
                "the spiders bolder.", {}),
    "dh_halion": (DF, "Commander Halion Brightspear", "blood_elf", M, 10, "down",
                  "You can stand easy here. I held this outpost when it fell, and I've held it every day since. I'm not sure there's "
                  "much of me left to hold it with.", {}),
    "dh_scout_nerys": (DF, "Scout Nerys Duskmantle", "blood_elf", F, 7, "left",
                       "Keep your head down. That's the naga's main camp below us, and they've got sentries on the rocks. I've "
                       "been counting them for three days.", {}),
    # ---- Firstlight Spire
    "dh_lorien": (FS, "Spire-Keeper Lorien Ashbloom", "blood_elf", M, 37, "down",
                  "The founders raised this spire and lit it, and it burned for a thousand years. When it went out, the "
                  "outpost died with it. I've kept the stair swept ever since, waiting.", {}),
    "tl_sunreach_magister": (FS, "Grand Magister Velanthe Sunreach", "blood_elf", F, 4, "down",
                             "Welcome to Firstlight Spire. We lost the spires of Quel'Thalas, and the Conclave swore "
                             "we'd raise a light again somewhere. Here it is, and it's yours as much as ours.", {}),
    "dh_innkeeper": (FS, "Innkeeper Liriel Ambershade", "blood_elf", F, 19, "down",
                     "A bed, a fire and a hot meal, and nobody asks where you washed up from. That's the whole of the "
                     "Spire's hospitality, and it's more than most of us had a year ago.", {}),
    "dh_flight_master": (FS, "Hawkmaster Seraphel", "blood_elf", F, 14, "down",
                         "The dragonhawks will take you anywhere you've already been. They'll cross the strait to "
                         "Azshara on a calm day, and they think the boat is beneath them.", {}),
    "dh_banker": (FS, "MerchantTusk", "troll", M, 3, "down",
                  "Dere is only one bank, mon, and dere is only one me, even out here on de elves' island. Do not ask "
                  "how dat works. Hand me ya things.", {"is_banker": True, "sprite_scale": 2.0}),
    "mailbox_firstlight": (FS, "Mailbox", "blood_elf", M, 0, "down",
                           "The Spire's mailbox. The innkeeper sorts the letters and the parcels, and the boat brings the "
                           "rest from Durotar.", {"is_mailbox": True,
                                                  "prop": "assets/tiles/market/props/mailbox_orc_b.png"}),
    "ct_firstlight": (FS, "Trainer Elthas Dawnreach", "blood_elf", M, 29, "down",
                      "The library keeps every discipline's books, and I keep the library. Show me how far you've come "
                      "and we'll see how far you can go.", {"trains_class": "*"}),
    "pt_firstlight_forge": (FS, "Smith Torvael", "blood_elf", M, 27, "down",
                            "The Spire's forge is small, but the anvil came from Silvermoon. Bring me ore and I'll teach "
                            "you the hammer, or the pick if you'd rather.",
                            {"trains_profession": ["blacksmithing", "mining"]}),
    "pt_firstlight_alchemy": (FS, "Alchemist Sylvana Brightdew", "blood_elf", F, 23, "down",
                              "Mana potions, healing draughts, and a tea that stops the dreams. Learn the herbs first, "
                              "then the glass.", {"trains_profession": ["alchemy", "herbalism"]}),
    "pt_firstlight_cloth": (FS, "Tailor Marelle", "blood_elf", F, 29, "down",
                            "Red and gold, always. Everyone who comes ashore needs clothes that fit this place, and I "
                            "need hands. Sit down and I'll show you the needle.",
                            {"trains_profession": ["tailoring", "leatherworking", "skinning"]}),
    "pt_firstlight_enchanting": (FS, "Enchanter Vaelis", "blood_elf", M, 33, "down",
                                 "Every scrap of old magic on this island wants to go somewhere. Enchanting gives it "
                                 "somewhere to go.", {"trains_profession": ["enchanting", "cooking", "fishing"]}),
    "dh_joost": (FS, "Joost Achterberg", "human", M, 7, "right",
                 "Forty years I brought ships into Rotterdam, the biggest port in Europe. Now I've got one boat and one "
                 "crossing, and I'm prouder of it than I ever was of the big ones.", {}),
    # ---- townsfolk (Kyle, 21 Nov 2026: "Do we need additional blood elf NPCs? Might as well populate the world a
    # bit"). Looks from the BE-M and BE-W townsfolk sheets (world/race_registry.py: men 16-40, women 11-33).
    "dh_shore_newcomer_a": (AL, "Maren Eide", "human", F, 9, "right",
                            "I was on a night bus outside Bergen, and then I was here, wet to the knees. The elves keep "
                            "telling me that's normal. I don't think it's normal.", {}),
    "dh_shore_newcomer_b": (AL, "Tomasz Wrobel", "human", M, 11, "left",
                            "The ranger told me to sit until the sand stops moving. It's been an hour, and it's still "
                            "moving a little.", {}),
    "dh_amberwatch_gate": (AL, "Sentinel Daeron Highwind", "blood_elf", M, 18, "down",
                           "Amberwatch keeps its gate open from dawn to dusk. After dark it opens for anyone the shore "
                           "gives up, and for nobody the sea sends.", {}),
    "dh_amberwatch_sentry": (AL, "Sentinel Taelia Brightshore", "blood_elf", F, 13, "right",
                             "I watch the cove road. If you hear horns from the south-east, it's the naga, and you'd "
                             "best be inside the walls before the second one.", {}),
    "dh_amberwatch_hauler": (AL, "Caelan Ashgrove", "blood_elf", M, 31, "down",
                             "I carried this bundle out of Quel'Thalas, across the sea and up this hill. I keep meaning "
                             "to unpack it. I'll get round to it when there's a roof to unpack it under.", {}),
    "dh_rosa_helper": (AL, "Taelor Brightwood", "blood_elf", M, 21, "left",
                       "Rosa doesn't speak a word of Thalassian, and I'd never held a saw until this week. We "
                       "understand each other perfectly. She points, and I cut.", {}),
    "dh_dawnrest_guard": (DF, "Guard Valandor Emberleaf", "blood_elf", M, 3, "down",
                          "Dawnrest had no roof for a thousand years, and it's got one now. I'd rather nothing came "
                          "down the road to test it.", {}),
    "dh_dawnrest_carpenter": (DF, "Mirelle Oakensong", "blood_elf", F, 15, "down",
                              "We put the roof back on with timber from the Red Hollow. It leaks over the hearth, which "
                              "means it leaks over the cook, which means I hear about it every night.", {}),
    "dh_dawnrest_hunter": (DF, "Hunter Belathor Thornleaf", "blood_elf", M, 40, "right",
                           "Lyra takes the bears, and I take whatever she leaves. The stew's been good since you lot "
                           "started thinning the woods.", {}),
    "dh_dawnrest_newcomer": (DF, "Andrés Calderón", "human", M, 13, "down",
                             "I drove a lorry in Seville. Now I carry water for the elves, and honestly, the pay's about "
                             "the same. The view's a great deal better.", {}),
    "dh_spire_gate_south": (FS, "Spire Guard Lethandris", "blood_elf", M, 18, "down",
                            "Welcome to Firstlight Spire. Keep to the road, mind the stair, and don't stare at the light "
                            "too long. Everyone does on their first night.", {}),
    "dh_spire_gate_pier": (FS, "Spire Guard Caerwyn Dawnfeather", "blood_elf", F, 13, "right",
                           "The boat crosses when Joost says the sea's fit, and not before. Arguing with him doesn't "
                           "help. I've watched a magister try.", {}),
    "dh_spire_citizen": (FS, "Lady Elandris Vael", "blood_elf", F, 31, "down",
                         "I had a house in Silvermoon with forty windows. Here I've got one room with a single window, "
                         "and the spire's in it. I find I don't miss the other thirty-nine.", {}),
    "dh_spire_student": (FS, "Faeril Lightquill", "blood_elf", M, 38, "down",
                         "The library has more books than shelves, so we read them standing. I've got three on runes "
                         "and one on boats, in case the runes don't work out.", {}),
    "dh_pier_fisher": (FS, "Haldris Netweaver", "blood_elf", M, 23, "right",
                       "The fish here bite at dusk and sulk at noon, the same as the fishermen. Sit a while if you "
                       "like. They don't mind company.", {}),
    "dh_spire_settler": (FS, "Siobhan Reilly", "human", F, 4, "down",
                         "I came ashore half drowned in the spring. Now I've got a room over the bakery and a cat who "
                         "belongs to nobody. That's more of a home than I had in Galway, if I'm honest.", {}),
}

#: vendor_id -> (zone module, name, race, gender, variant, facing, gear level, sells gear, stock, greeting)
VENDORS = {
    "dh_amberwatch_trader": (AL, "Provisioner Faelin Sunleaf", "blood_elf", M, 26, "left", 4, False, FOOD + GOODS[:4],
                             "Food, water and the odd potion. Everything here came across on a boat or out of the "
                             "grove, and I'm not proud about which."),
    "dh_dawnrest_cook": (DF, "Giulia Ferraro", "human", F, 5, "down", 7, False, FOOD,
                         "I cooked in Bologna for thirty years, and I'll tell you what I tell the elves. Nobody fights "
                         "well on an empty stomach, so sit down and eat."),
    "dh_dawnrest_trader": (DF, "Quartermaster Ilyra Sunmantle", "blood_elf", F, 20, "down", 8, True, GOODS,
                           "Potions, bags and repairs. The Conclave keeps Dawnrest stocked for the people out in the "
                           "woods, and that's you now."),
    "dh_spire_provisioner": (FS, "Provisioner Aerith Goldmantle", "blood_elf", F, 18, "down", 9, False, FOOD + GOODS,
                             "The Spire's stores. Bread, wine and potions, and the boat brings more every week."),
    "tl_sunreach_quartermaster": (FS, "Quartermaster Sylvaen Dawnward", "blood_elf", M, 3, "left", 54, True,
                                  ["mana_potion_masterwork", "healing_potion_masterwork", "vial_crystal", "parchment",
                                   "kit_field_repair"],
                                  "The Conclave's stores, moved home at last. Everything you see came over on the first "
                                  "boats, so please don't haggle."),
}
#: the Durotar end of the crossing
DOCKHAND = ("dh_durotar_dockhand", "Dockhand Grezza", "orc", F, 4, "left",
            "The elves' boat comes in from Dawnhaven every few days. Orgrimmar's up the road to the north, and Razor "
            "Hill's south-west of here. Mind the scorpids.")

SERVICES = {"dh_innkeeper": ["inn"], "dh_flight_master": ["flight"]}
FLIGHT_NODES = [("firstlight_spire", {"name": "Firstlight Spire", "zone": FS.NAME, "master": "dh_flight_master",
                                       "pos": [62, -84], "continent": "kalimdor"})]

#: the two recruits: placed, with what they're doing here now
RECRUITS = {
    "liam_suncleric": dict(zone=AL.NAME, x=82, y=106, level=3,
                           now="Amberleaf Glade, on the Waking Shore, meeting whoever the sea gives up. He's the first "
                               "face most of them see.\n\nHe sits them down, gets them breathing, and walks them up to "
                               "Amberwatch. The elves call it a calling. He calls it a shift that doesn't end.",
                           forward="A crew, rostered and trained and able to do it without him standing there. It's the "
                                   "same thing he wanted on Earth and never got, and the reason he never got it was "
                                   "that he kept going in alone.\n\nThere are two kids at Amberwatch who woke up on "
                                   "the shore with nobody. He's been on Dawnhaven a year, and everybody who knows him "
                                   "can see what's happened except him."),
    "haruto_runemaster": dict(zone=DF.NAME, x=126, y=82, level=7,
                              now="Duskfall Woods, among the Withered Spires, where the outpost's founders cut runes "
                                  "into every stone and the runes are fading now the well is dark.\n\nHe's copying "
                                  "them before they're gone. It's slow and unrewarded, and his copies will be the only "
                                  "record there is.",
                              forward=None),
}


def _check():
    for mod in (AL, DF, FS):
        mine = {k for k, v in AMBIENT.items() if v[0] is mod} | {k for k, v in VENDORS.items() if v[0] is mod}
        if mine != set(mod.NPC_POSITIONS):
            raise SystemExit(f"{mod.NAME}: roster and layout disagree: {sorted(mine ^ set(mod.NPC_POSITIONS))}")
    from tools.build_tempest_quests import voice_problems
    texts = [(k, v[6]) for k, v in AMBIENT.items()] + [(k, v[9]) for k, v in VENDORS.items()] + [(DOCKHAND[0], DOCKHAND[6])]
    texts += [(k, v["now"]) for k, v in RECRUITS.items()] + [(k, v["forward"]) for k, v in RECRUITS.items() if v["forward"]]
    bad = [f"{k}: {p}" for k, t in texts for p in voice_problems(t)]
    if bad:
        raise SystemExit("FAILED, fix the words:\n  " + "\n  ".join(bad))


def main():
    _check()
    vp, ap = ROOT / "data/npcs/vendors.json", ROOT / "data/npcs/ambient_npcs.json"
    vd, ad = json.loads(vp.read_text(encoding="utf-8")), json.loads(ap.read_text(encoding="utf-8"))
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (mod, name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = mod.NPC_POSITIONS[vid]
        z = zone_key(mod.NAME)
        rec = dict(vendor_id=vid, name=name, zone=z, x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
            vby[vid].update(zone=z, x=x, y=y, greeting=greet, appearance_variant=var)  # looks: the BE townsfolk sheets
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    people = dict(AMBIENT)
    for nid, (mod, name, race, gender, var, facing, greet, extra) in people.items():
        x, y = mod.NPC_POSITIONS[nid]
        z = zone_key(mod.NAME) if mod is not FS else zone_key(FS.NAME)
        rec = dict(npc_id=nid, name=name, zone=z, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing, **extra)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
            aby[nid].update(zone=z, x=x, y=y, greeting=greet, appearance_variant=var)
        else:
            ad["npcs"].append(rec)
            made += 1
    nid, name, race, gender, var, facing, greet = DOCKHAND
    rec = dict(npc_id=nid, name=name, zone="durotar", x=DUROTAR_DOCK[0], y=DUROTAR_DOCK[1], greeting=greet,
               gender=gender, race=race, appearance_variant=var, facing=facing)
    if nid in aby:
        aby[nid].update(rec)
    else:
        ad["npcs"].append(rec)
        made += 1
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # services and the island's one flight path
    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # trainers
    trp = ROOT / "data/training/trainers.json"
    tr = json.loads(trp.read_text(encoding="utf-8"))
    for nid, v in AMBIENT.items():
        extra = v[7]
        if "trains_class" in extra:
            tr["class_trainers"][nid] = extra["trains_class"]
        if "trains_profession" in extra:
            tr["profession_trainers"][nid] = list(extra["trains_profession"])
    trp.write_text(json.dumps(tr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the recruits
    rp = ROOT / "data/npcs/recruits.json"
    rd = json.loads(rp.read_text(encoding="utf-8"))
    for r in rd["recruits"]:
        v = RECRUITS.get(r["recruit_id"])
        if not v:
            continue
        r.update(zone=v["zone"], x=v["x"], y=v["y"], level=v["level"], placed=True)
        r.pop("suggested_zone", None)
        bs = r.setdefault("background_sections", {})
        bs["now"] = v["now"]
        if v["forward"]:
            bs["forward"] = v["forward"]
    rp.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the Conclave's two still give and take no quests
    tied = []
    for qf in sorted((ROOT / "data/quests").glob("*.json")):
        d = json.loads(qf.read_text(encoding="utf-8"))
        for q in d.get("quests", []) if isinstance(d, dict) else []:
            for key in ("giver_npc_id", "turn_in_npc_id"):
                if q.get(key) in MOVABLE:
                    tied.append(f"{qf.name}: {q.get('quest_id')} {key}={q.get(key)}")
    if tied:
        raise SystemExit("the Conclave's movable people are tied to quests:\n  " + "\n  ".join(tied))
    print(f"Dawnhaven: {made} created, {moved} moved ({len(AMBIENT) + len(VENDORS) + 1} people), "
          f"{len(RECRUITS)} recruits placed")


if __name__ == "__main__":
    main()
