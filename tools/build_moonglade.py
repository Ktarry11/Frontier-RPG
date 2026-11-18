#!/usr/bin/env python3
"""Moonglade's people and its two factions: Nighthaven's Cenarion Circle, the Wakened on the west shore, the inn, the
roost, the trainers, and both quartermasters' shelves. Idempotent.

    PYTHONPATH=. python3 tools/build_moonglade.py

docs/moonglade_brief.md. Kyle, 18 Nov 2026: "moonglade can be quite a decent size but is still a town and hub. there
will be an inn and a flight path. no monsters", and "we have two factions, the cenarion circle is still there and the
Wakened. They are in good standing with each other. The wakened is transplant led while cenarion circle is true to
lore. Moonglade looks similar but 'something else is waking up'". He picked the Cenarion Circle as a reputation
faction; the Wakened are the second.

Every person stands where tools/handbuilt_moonglade.py NPC_POSITIONS says; a person in one and not the other stops
the script. The two sheet-5 recruits (Valentina, Faris) are placed by tools/build_sheet5_recruits.py, not here.

THE SHELVES are TBC-style like every other faction (tools/build_faction_rewards.author_unique() and the crafted gear's
author(), neither of those scripts re-run): friendly a supply of the faction's own, honored a neck piece and a pattern,
revered six ilvl 67 blues and a pattern, exalted three ilvl 73 epics and two recipes. A direction, not a cage (Kyle,
15 Nov 2026): the Circle leans to nature, healers and ferals and the Wakened to practical gear, and both serve tanks,
healers, casters and fighters. Reputation comes from Moonglade's quests (tools/build_moonglade_quests.py, by giver);
the three dungeons, when they're built, are the road to exalted.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_faction_rewards as BFR  # noqa: E402
from tools import handbuilt_moonglade as MG  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"
HOME = zone_key(MG.NAME)

SERVICES = {"mg_innkeeper": ["inn"], "mg_bunthen": ["flight"]}
FLIGHT_NODES = [
    ("moonglade", {"name": "Moonglade", "zone": MG.NAME, "master": "mg_bunthen", "pos": [-30, -128],
                   "continent": "kalimdor"}),
]
CLASS_TRAINER = "ct_moonglade"
TRAINERS = {
    "pt_mg_herbs": ["herbalism", "alchemy"],
    "pt_mg_hide": ["skinning", "leatherworking"],
    "pt_mg_fish": ["cooking", "fishing"],
}

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "mg_circle_qm": ("Quartermaster Ellandris Dawnleaf", "night_elf", F, 4, "down", 58, True,
                     ["kit_field_repair", "healing_potion_masterwork", "mana_potion_masterwork"],
                     "The Circle doesn't sell what it makes to strangers. Help us for a while and you won't be a "
                     "stranger, and then my shelf is yours."),
    "mg_wakened_qm": ("Quartermaster Tomas Ribeiro", "human", M, 4, "down", 58, True,
                      ["kit_field_repair", "healing_potion_masterwork", "parchment"],
                      "I ran a hardware shop in Porto for nineteen years. Here I run the Wakened's stores, and it's "
                      "the same job: know what people need before they ask. Earn their trust and I'll open the back "
                      "room for you."),
    "mg_provisioner": ("Provisioner Kesha Windmane", "tauren", F, 6, "down", 56, False,
                       ["meal_ember_glazed_ribs", "drink_starfall_wine", "high_table_feast", "cook_flour",
                        "cook_spice", "cook_water", "cook_mushroom"],
                       "We fed a whole lodge on the plains from one kodo, and nobody went to bed hungry. Up here I "
                       "feed night elves, tauren and transplants, and every one of them eats like it's the last "
                       "night of the world."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Cenarion Circle, Nighthaven
    "mg_rabine": ("Rabine Saturna", "night_elf", M, 6, "down",
                  "Welcome to Nighthaven. The Circle has kept this glade for ten thousand years, and it still looks the "
                  "way it always has, which is exactly what worries me. Something here is waking, and I'd like to know "
                  "what before it opens its eyes."),
    "mg_hamuul": ("Archdruid Hamuul Runetotem", "tauren", M, 8, "down",
                  "I led what was left of Thunder Bluff's druids up the mountain to this glade. We carried the ones who "
                  "couldn't walk, and we left the ones we couldn't carry. Moonglade took us in, and I won't forget it."),
    "mg_bunthen": ("Bunthen Plainswind", "tauren", M, 3, "down",
                   "The wind riders and the hippogryphs share a roost now, and they've mostly stopped biting each "
                   "other. I flew the Thunder Bluff road every day for twenty years, and I still fly it most nights in "
                   "my sleep. Where can I take you?"),
    "mg_innkeeper": ("Innkeeper Talowyn Nightbreeze", "night_elf", F, 2, "down",
                     "Every bed in Nighthaven faces the lake, so you'll fall asleep to the moon on the water. I'll bind "
                     "your hearth here if you want to come back to it."),
    "ct_moonglade": ("Trainer Loganaar", "night_elf", M, 3, "down",
                     "The Circle trains druids, and lately it trains everyone else too, because everyone else keeps "
                     "arriving. Tell me what you are and I'll show you what's next."),
    "pt_mg_herbs": ("Herbwarden Mylla Starbloom", "night_elf", F, 5, "down",
                    "Herbs and alchemy. Nothing grows in this glade that the Circle hasn't tended, so I'll teach you "
                    "here and you'll gather out in the world."),
    "pt_mg_hide": ("Hidewright Tannar Proudhoof", "tauren", M, 11, "left",
                   "Skinning and leather. My people wasted nothing from a kill on the plains, and I won't have you "
                   "wasting anything here either."),
    "pt_mg_fish": ("Ilyssa Moonwater", "night_elf", F, 7, "down",
                   "Cooking and fishing. The lake's fish have never once been hungry enough to bite in a hurry, so "
                   "you'll learn patience before you learn anything else."),
    "mg_moonwell_keeper": ("Moonwell Keeper Aedris Silverbrook", "night_elf", F, 8, "down",
                           "The great moonwell has never run dry, not in ten thousand years. Lately it runs over at "
                           "night, a finger's width, and then it settles again by morning. I've started writing down "
                           "when."),
    "mg_tauren_elder": ("Elder Mahala Dawnhorn", "tauren", F, 14, "down",
                        "We brought the totems out of Thunder Bluff on our backs, and we haven't raised them yet. "
                        "Raising them here would mean we'd stopped hoping to go home."),
    # ---- the Shrine of Remulos and the north woods
    "mg_remulos": ("Keeper Remulos", "night_elf", M, 10, "down",
                   "I've walked the Dream since before your world's first city was built. Lately the Dream has been "
                   "turning over inside me, the way a sleeper does before he wakes. I'm not afraid of it, and I'm "
                   "listening hard."),
    "mg_arch_watcher": ("Dreamwatcher Lethiel", "night_elf", F, 9, "left",
                        "The stones of this arch are warm at night. They were cold for ten thousand years, and now "
                        "they're warm, and nobody in the Circle will tell me why. So I sit with them."),
    # ---- the Barrow Dens
    "mg_barrow_warden": ("Warden Taerenas", "night_elf", M, 4, "left",
                         "The Barrow Dens are closed. The sleepers inside have started talking in their sleep, and the "
                         "Circle wants nobody listening at the door until we know who they're talking to."),
    "mg_barrow_warden_b": ("Warden Torin Grayhoof", "tauren", M, 5, "right",
                           "I stand here so the sleepers aren't alone. I knew some of them on the plains. One of them "
                           "still owes me a game of stones, and I mean to collect."),
    # ---- the Wakened, west shore
    "mg_sandvik": ("Dr. Ingrid Sandvik", "human", F, 5, "down",
                   "I studied sleep in Trondheim for twenty years, what the brain does at night and why it dreams. Then "
                   "I woke up on the grass beside that lake with a druid standing over me, and I've been studying it "
                   "from the inside ever since. Welcome to the Wakened."),
    "mg_infirmary": ("Nurse Adaeze Okafor", "human", F, 3, "down",
                     "I was a night nurse in Lagos. When I woke up here I went looking for the sick before I'd even "
                     "asked where I was. Some of us wake badly, and I sit with them until they're sure which world "
                     "they're in."),
    "mg_carver": ("Hamish MacLeod", "human", M, 4, "left",
                  "The first thing I remembered when I woke was my mother's kitchen on Lewis, so I carved it into a "
                  "plank. Now everybody carves the last thing they remember, and the wall's longer than the longhouse."),
    "mg_gardener": ("Mei-Lin Zhou", "human", F, 2, "down",
                    "My grandmother grew chillies on a balcony in Chengdu. The druids say nothing here needs my help to "
                    "grow, and they're right, but I plant things anyway. It's how I know where I am."),
    "mg_dreamer": ("Danny Kowalczyk", "human", M, 6, "right",
                   "I had a wife and two boys in Buffalo, and I was asleep when it happened. If I fall asleep the right "
                   "way, I think I'll wake up back there. Ingrid says it doesn't work like that. I keep trying anyway."),
}

# ---------------------------------------------------------------------------------------------- the factions
CIRCLE, WAKENED = "cenarion_circle", "the_wakened"
FACTIONS = {
    CIRCLE: {
        "name": "The Cenarion Circle",
        "description": ("The druids of Moonglade, night elf and tauren together, keeping the glade and watching over "
                        "every land that's fallen sick."),
        "home_zone": HOME,
        "home_name": "Nighthaven, in Moonglade",
        "leader": {
            "title": "Keeper of Nighthaven",
            "name": "Rabine Saturna",
            "npc_id": "mg_rabine",
            "location": "The Cenarion Circle's hall, Nighthaven",
            "line": ("The Circle was here before the worlds came together, and it'll be here after whatever's waking "
                     "has finished waking. That's not a boast. It's a promise we made a long time ago."),
        },
        "_lore_note": "Kyle, 18 Nov 2026: 'the cenarion circle is still there' and 'true to lore'.",
        "lore": [
            "The Cenarion Circle is the druids' order, night elf and tauren together, and Moonglade is its home. Keeper "
            "Remulos stands at his shrine on the lake's north-west shore, and the druids who walk the Emerald Dream "
            "sleep in the Barrow Dens.",
            "When Thunder Bluff fell, the tauren druids who survived came up the mountain to the glade, and the "
            "Circle took them in. Archdruid Hamuul Runetotem leads them. The tauren half of Nighthaven is crowded "
            "and grieving and still makes room for anyone who comes.",
            "The Circle watches the sick lands: Felwood, Azshara's rot, the Plaguelands and the wound in Deadwind. "
            "Lately it's been watching its own glade too, because something in Moonglade is waking up.",
            "It's in good standing with the Wakened, the transplants who woke on its shore, and it argues with them "
            "about the Dream the way old friends argue.",
        ],
        "quest_rep": {"_comment": "Per quest, paid by giver (tools/build_moonglade_quests.py).",
                      "default": 325, "boss": 350, "capstones": {}, "zones": []},
    },
    WAKENED: {
        "name": "The Wakened",
        "description": ("Transplants who arrived asleep in Moonglade's grass, were woken by the druids, and stayed "
                        "to understand the Dream from the outside."),
        "home_zone": HOME,
        "home_name": "The Wakened's settlement, on Moonglade's west shore",
        "leader": {
            "title": "Dr.",
            "name": "Ingrid Sandvik",
            "npc_id": "mg_sandvik",
            "location": "The longhouse, the Wakened's settlement",
            "line": ("Everyone here woke up in the same place, in the same grass, with a druid standing over them. "
                     "What we do about that is up to us, and we've decided to do it together."),
        },
        "_lore_note": "Kyle, 18 Nov 2026: 'the Wakened ... transplant led ... in good standing' with the Circle.",
        "lore": [
            "When the worlds came together, the Emerald Dream bled into Moonglade for a moment, and every transplant "
            "who came through anywhere near the glade arrived asleep. The druids found them lying in the grass round "
            "the lake and woke them one at a time.",
            "Most of them stayed. They built a settlement on the west shore with their own hands, badly at first, "
            "and they carved the last thing each of them remembered from Earth into a wall that's now longer than "
            "their longhouse.",
            "Not everyone woke. The ones who didn't sleep on in the Barrow Dens beside the druids, and the Wakened "
            "visit them.",
            "Dr. Ingrid Sandvik leads them. She spent twenty years in Trondheim studying what people's brains do at "
            "night, and now she's studying the Dream from the only angle the druids never had: the outside.",
        ],
        "quest_rep": {"_comment": "Per quest, paid by giver (tools/build_moonglade_quests.py).",
                      "default": 325, "boss": 350, "capstones": {}, "zones": []},
    },
}
QM = {CIRCLE: "mg_circle_qm", WAKENED: "mg_wakened_qm"}

#: (id, name, slot, kind, type, identity, price in gold, flavour)
HONORED = {
    CIRCLE: [("cc_moonbough_pendant", "Moonwell Rim Pendant", "neck", "armor", None, "healer", 40,
              "A sliver of the great moonwell's rim, set in living wood. It's warm in the morning and cold at night.")],
    WAKENED: [("wk_locket_of_the_last_memory", "Locket of the Last Memory", "neck", "armor", None, "tank_any", 40,
               "Every Wakened carries one. There's nothing inside it until you put something there.")],
}
REVERED = {
    CIRCLE: [
        ("cc_grove_wardens_vest", "Grove Warden's Vest", "chest", "armor", "leather", "feral", 66,
         "Bark-tanned leather the Circle's wardens wear on the Barrow Dens' door, lined for long nights."),
        ("cc_moonwell_keepers_cowl", "Moonwell Keeper's Cowl", "head", "armor", "cloth", "spirit_healer", 58,
         "Aedris Silverbrook sews one for every keeper she trains, and she's trained a great many."),
        ("cc_thornward_greaves", "Thornward Greaves", "legs", "armor", "plate", "tank", 62,
         "Plate grown over with a living ward of thorn, so whoever stands in them stands like a hedge."),
        ("cc_stormcrow_mantle", "Stormcrow Mantle", "shoulder", "armor", "mail", "mail_caster", 58,
         "Feathers from the crows that roost over the Shrine of Remulos, worked into mail by tauren hands."),
        ("cc_band_of_the_glade", "Band of the Glade", "ring", "armor", None, "healer", 55,
         "A ring of pale wood from a branch the great tree dropped the night the worlds came together."),
        ("cc_barrow_wardens_bracers", "Barrow Warden's Bracers", "wrist", "armor", "mail", "hunter", 52,
         "Warden Grayhoof's own pattern. He says they're for leaning on a door all night, and he isn't joking."),
    ],
    WAKENED: [
        ("wk_longhouse_jerkin", "Longhouse Jerkin", "chest", "armor", "leather", "agility", 64,
         "Cut by people who'd never cut leather before, and refitted until it was right."),
        ("wk_night_nurses_robes", "Night Nurse's Robes", "chest", "armor", "cloth", "high_healer", 66,
         "Adaeze Okafor's pattern: deep pockets, no loose sleeves, and a hood for sitting up through the night."),
        ("wk_boots_of_the_first_morning", "Boots of the First Morning", "feet", "armor", "mail", "tide_healer", 56,
         "The Wakened all remember their first morning here. These are for walking into the next one."),
        ("wk_carvers_gauntlets", "Carver's Gauntlets", "hands", "armor", "plate", "strength", 58,
         "Hamish MacLeod's, worn thin at the fingertips from carving the wall of last memories."),
        ("wk_sleepwalkers_cord", "Sleepwalker's Cord", "waist", "armor", "cloth", "caster", 52,
         "Tied round the waist of anyone who walks in their sleep, so the night watch can find them by morning."),
        ("wk_night_watch_shield", "Night Watch Shield", "off_hand", "weapon", "shield", "shield_tank", 60,
         "The Wakened keep a watch every night by the dream cots. Somebody has to be awake."),
    ],
}
EXALTED = {
    CIRCLE: [
        ("cc_staff_of_the_moonglade", "Staff of the Moonglade", "main_hand", "weapon", "staff", "high_healer", 320,
         "Cut from the great tree with Remulos's leave, and it still grows a leaf in spring."),
        ("cc_thornheart_maul", "Thornheart Maul", "main_hand", "weapon", "mace_2h", "bear_weapon", 310,
         "Hamuul Runetotem carried it out of Thunder Bluff. He says it's for a bear's paw, not a tauren's hand."),
        ("cc_nighthaven_longbow", "Nighthaven Longbow", "ranged", "weapon", "bow", "hunter_crit", 290,
         "Strung with moonwell-soaked gut. The Circle's wardens have never once missed a shot at night with one."),
    ],
    WAKENED: [
        ("wk_the_waking_ledger", "The Waking Ledger", "off_hand", "weapon", "tome", "spirit_caster", 280,
         "Ingrid Sandvik's notebook of every dream the Wakened have told her. She made a copy for you."),
        ("wk_ribeiros_hammer", "Ribeiro's Hammer", "main_hand", "weapon", "mace_1h", "tank_weapon", 300,
         "Tomas Ribeiro made it with the first iron the Wakened ever smelted. It's ugly and it's never broken."),
        ("wk_blade_of_the_wakeful", "Blade of the Wakeful", "main_hand", "weapon", "sword_1h", "rogue_crit", 300,
         "For the ones who keep the night watch. It's light enough to hold all night and sharp enough to matter."),
    ],
}
#: (id, trade, name, slot, kind, type, identity, flavour, icon): the icon is the pack's, for no crafted epic shares one
EXALTED_RECIPES = {
    CIRCLE: [
        ("rep_cc_grovewalkers_harness", "leatherworking", "Grovewalker's Harness", "chest", "armor", "leather", "feral",
         "The Circle's own pattern for the druids who walk out to the sick lands, cut to shift with them.",
         "gear_wow_chest_leather_09_1"),
        ("rep_cc_moonbough_longbow", "woodworking", "Greatbough Longbow", "ranged", "weapon", "bow", "hunter_crit",
         "Shaped from a fallen bough of the great tree and cured in the moonwell for a full year.",
         "gear_wow_bow_bow_45"),
    ],
    WAKENED: [
        ("rep_wk_dreamwoven_robe", "tailoring", "Dreamwoven Robe", "chest", "armor", "cloth", "spirit_healer",
         "Woven on the Wakened's first loom from linen the druids grew for them. The pattern came to Mei-Lin in a dream.",
         "gear_inv_chest_cloth_45"),
        ("rep_wk_night_watch_breastplate", "blacksmithing", "Night Watch Breastplate", "chest", "armor", "plate",
         "tank", "The Wakened's smiths learned on this one. They say if you can make it, you can make anything.",
         "gear_inv_chest_plate13"),
    ],
}
#: (id, trade, name, slot, kind, type, identity, flavour, icon, tier): the patterns before exalted, blue
SHELF_PATTERNS = {
    CIRCLE: [
        ("rep_cc_moonleaf_bracers", "leatherworking", "Moonleaf Bracers", "wrist", "armor", "leather", "agility",
         "Leather pressed with moonleaf, the way the Circle's scouts have worn it since the War of the Ancients.",
         "gear_wow_wrist_desecrated_leatherbracer", "honored"),
        ("rep_cc_barrowguard_gloves", "leatherworking", "Barrowguard Gloves", "hands", "armor", "leather", "bear",
         "Heavy gloves for the wardens at the Barrow Dens, thick enough to hold back a thorn ward.",
         "gear_wow_hands_85_1", "revered"),
    ],
    WAKENED: [
        ("rep_wk_sleepers_handwraps", "tailoring", "Sleeper's Handwraps", "hands", "armor", "cloth", "caster",
         "Soft linen for the hands of anyone who sleeps in the Dens. The Wakened make them for strangers too.",
         "gear_wow_hands_90_2", "honored"),
        ("rep_wk_longhouse_bracers", "blacksmithing", "Longhouse Bracers", "wrist", "armor", "plate", "strength",
         "Plain iron bands from the Wakened's forge, the first thing every new smith there learns to make.",
         "gear_wow_wrist_82", "revered"),
    ],
}
#: the factions' own supplies, written into data/consumables/consumable_types.json
CONSUMABLES = {
    CIRCLE: ("mana_potions", {
        "consumable_id": "cc_moonwell_draught", "name": "Moonwell Draught", "consumable_type": "mana_potion",
        "description": "A stoppered flask of water from Nighthaven's great moonwell. Restores mana at once.",
        "effect_value": 1050, "effect_duration": 0, "level_multiplier": 0.0, "required_level": 52,
        "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 90, "buff_category": None,
    }),
    WAKENED: ("elixirs", {
        "consumable_id": "wk_waking_tea", "name": "Waking Tea", "consumable_type": "elixir",
        "description": ("Strong black tea the way the Wakened make it, to keep the night watch awake. +25 Spirit for "
                        "30 minutes. Battle elixir: one at a time."),
        "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": 52,
        "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 90, "buff_category": "battle",
        "stat_bonuses": {"spirit": 25},
    }),
}
HONORED_SUPPLIES = {CIRCLE: ["flask_mending"], WAKENED: ["flask_mending"]}
#: an epic's icon is its own (Kyle, 16 Nov 2026: "every unique item in the game can only have ONE icon"): where the
#: picker's choice belongs to something else already, the pack icon named here
EPIC_ICONS = {"cc_nighthaven_longbow": "gear_inv_weapon_bow_12"}
#: names the shelf used before (18 Nov 2026), dropped from the icon picks when it's rebuilt
OLD_NAMES = ["Moonbough Longbow"]


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def people(bad):
    from tools.build_tempest_quests import voice_problems
    roster = set(VENDORS) | set(AMBIENT)
    if roster != set(MG.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(roster ^ set(MG.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    for sid, trades in TRAINERS.items():
        if sid not in AMBIENT:
            bad.append(f"trainer {sid} has no record")


def write_people():
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = MG.NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=HOME, x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
            vby[vid]["zone"] = HOME
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = MG.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=HOME, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid == CLASS_TRAINER:
            rec["trains_class"] = "*"
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
            aby[nid]["zone"] = HOME
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
    tr["class_trainers"].setdefault(CLASS_TRAINER, "*")
    for k, v in TRAINERS.items():
        tr["profession_trainers"][k] = list(v)
    (ROOT / "data/training/trainers.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
    return made, moved


def shelves(bad):
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.reward_icons import unclash
    C.PICKER = Picker()
    cd = load("data/consumables/consumable_types.json")
    fr = load("data/items/faction_rewards.json")
    picks = load("data/items/crafted_icons.json")
    items = fr["items"]
    docs = {}
    for fid in FACTIONS:
        cat, rec = CONSUMABLES[fid]
        cd[cat][:] = [x for x in cd[cat] if x.get("consumable_id") != rec["consumable_id"]] + [dict(rec)]
        for (iid, name, slot, kind, typ, ident, price, flav) in HONORED[fid] + REVERED[fid]:
            items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.BLUE_ILVL, "rare", flav, price)
            items[iid]["faction"] = fid
            unclash(items[iid])
            bad += b
        for (iid, name, slot, kind, typ, ident, price, flav) in EXALTED[fid]:
            items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.EPIC_ILVL, "epic", flav, price)
            items[iid]["faction"] = fid
            if iid in EPIC_ICONS:
                items[iid]["icon_id"] = EPIC_ICONS[iid]
            bad += b
        for rid, trade, name, slot, kind, typ, ident, flav, icon, *tier in (EXALTED_RECIPES[fid]
                                                                            + SHELF_PATTERNS[fid]):
            blue = bool(tier)
            path = ROOT / "data" / BFR.TRADE_FILE[trade] / "recipes.json"
            d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
            book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
            inputs, mtier = BFR.PLACEHOLDER[trade]
            out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1],
                   "item_level": BFR.BLUE_ILVL if blue else BFR.EPIC_ILVL, "rarity": "rare" if blue else "epic",
                   "material_tier": mtier, "identity": ident, "flavor": flav,
                   "fixed_item_level": True, "required_level": BFR.WORN_AT}
            if kind == "weapon":
                out["weapon_type"] = typ
                ident = C.weapon_identity(typ, ident)
            else:
                out["armor_type"] = typ
            item = C.author(rid, {"name": name, "output": dict(out)}, ident, flav)
            bad += C.audit_item("reputation recipe", rid, item)
            item["required_level"] = BFR.WORN_AT
            item["icon_id"] = icon
            out["item"] = item
            book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300, "output": out,
                         "skill_range": [300, 305, 310, 315], "source": "vendor", "faction": fid,
                         "_rare_ingredients_todo": True}
            picks["icons"][name] = icon
    for old in OLD_NAMES:
        picks["icons"].pop(old, None)
    return cd, fr, picks, docs


def write_factions(fd):
    for fid, base in FACTIONS.items():
        rec = fd["factions"].get(fid, {})
        keep_rewards = rec.get("rewards")
        keep_also = (rec.get("quest_rep") or {}).get("also")
        rec.update(json.loads(json.dumps(base)))
        if keep_also:
            rec["quest_rep"]["also"] = keep_also
        rw = keep_rewards or {}
        qm = QM[fid]
        rw["vendor_stock"] = {qm: {
            "friendly": [CONSUMABLES[fid][1]["consumable_id"]],
            "honored": list(HONORED_SUPPLIES[fid]) + [f"unique:{r[0]}" for r in HONORED[fid]]
                       + [r[0] for r in SHELF_PATTERNS[fid] if r[-1] == "honored"],
            "revered": [f"unique:{r[0]}" for r in REVERED[fid]]
                       + [r[0] for r in SHELF_PATTERNS[fid] if r[-1] == "revered"],
            "exalted": [f"unique:{r[0]}" for r in EXALTED[fid]] + [r[0] for r in EXALTED_RECIPES[fid]],
        }}
        rw["_comment"] = ["Gates, not a displayed ladder (the faction panel stays information only).",
                          "TBC-style shelf (tools/build_moonglade.py, 18 Nov 2026): friendly the faction's supply, "
                          "honored a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three "
                          "ilvl 73 epics and two recipes."]
        rw.setdefault("quests", {})
        rec["rewards"] = rw
        fd["factions"][fid] = rec


def main():
    bad = []
    people(bad)
    cd, fr, picks, docs = shelves(bad)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    made, moved = write_people()
    fd = load("data/factions/factions.json")
    write_factions(fd)
    save("data/factions/factions.json", fd)
    save("data/items/faction_rewards.json", fr)
    save("data/items/crafted_icons.json", picks)
    save("data/consumables/consumable_types.json", cd)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Moonglade: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people); "
          f"{len(FACTIONS)} factions, each with 7 blues, 3 epics, 2 recipes, 2 patterns and a supply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
