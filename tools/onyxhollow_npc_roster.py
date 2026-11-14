"""
The people of Onyxhollow (50-53). The Dark Iron town under the Abyssal Sands.

Data only - tools/sync_onyxhollow_npcs.py writes these into data/npcs/*.json and takes every
coordinate from handbuilt_onyxhollow.NPC_POSITIONS. Each one's picture is a figure from the Dark
Iron sheet, filed by tools/slice_dark_iron_dwarves.py.

Kyle, 13 Nov 2026: "innkeeper for hearth, level appropriate shops, this can be more of a mining town
and Blacksmithing."

THEY FOLLOWED A SEAM AND IT ENDED IN A BEACH. Onyxhollow is a working that kept going. The seam
ran down, they ran down after it, and one shift the face came away onto black sand and blue light
and something chitinous looking back at them. They did what miners do with a void: they timbered
it, put a gate on it and carried on digging the other way. The town is the gate's back yard.

SO THE TOWN FACES INWARD. The rock is theirs and the Strand is a nuisance that happens to be on the
other side of the door. Nobody here is frightened of it and nobody here is curious about it, with
two exceptions (the geomancer and the loremaster) who are tolerated.

VOICE: people at work, talking to a customer. Contractions, plain sentences, and the useful
thing first - what they sell, where to go, what to watch for. Kyle, 13 Nov 2026, of the first draft
of these: "Don't use weird AI tics". That draft had every dwarf speaking in stiff unshortened
sentences and signing off with a neat little saying. Nobody talks like that. One piece of
character each is plenty, and it should be something the person would actually mention.

THE CASTOUTS are the one thing nobody will discuss past a sentence. People were put out of the
gate. They are in the old diggings. That is all a visitor gets, and the quests are where the rest
of it comes out.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

ONYXHOLLOW_VENDORS = {
    # enchanter (tools/build_enchanters.py, 14 Nov 2026)
    "oh_enchanter": (
        "Enchanter Halvard Runeglow", "dwarf", "male", 5,
        ["runed_copper_rod", "runed_silver_rod", "runed_golden_rod", "runed_truesilver_rod", "vial_crystal"],
        False,
        "Garrun's people make the rods and I put the runes in them. Then I sell them back at a price that annoys him.\n\nIf you want to learn enchanting, I'll teach you. It starts with breaking good gear into dust, and nobody enjoys that part."),
    # gem seller (tools/build_gem_sellers.py, 14 Nov 2026)
    "oh_gem_trader": (
        "Gem-Trader Brynja Facetstone", "dwarf", "female", 2,
        ["cut_sovereign_deepearth_geode", "cut_shifting_deepearth_geode", "cut_glowing_deepearth_geode", "cut_enduring_huge_emerald", "cut_dazzling_huge_emerald", "cut_bold_black_diamond", "cut_delicate_black_diamond", "cut_runed_black_diamond", "cut_sovereign_amethyst", "cut_shifting_amethyst", "cut_glowing_amethyst", "cut_solid_blue_sapphire", "cut_sparkling_blue_sapphire", "cut_lustrous_blue_sapphire"],
        False,
        "These are cut from what comes up out of the deep veins. They're ready for a socket now. Garrun's people can cut you something better if you bring them the rough stone."),
    "oh_innkeeper": (
        "Innkeeper Brenna Coalcask", "dwarf", "female", 3,
        ["meal_ember_glazed_ribs", "drink_starfall_wine", "bread_and_cheese", "roasted_meat",
         "meal_kodo_ribs", "meal_spiced_haunch",
         "drink_barley_beer", "drink_honeyed_mead", "healing_potion_mega", "mana_potion_mega",
         "spiced_stew", "cook_flour", "cook_spice", "cook_mushroom", "cook_ale", "cook_water"],
        False,
        "Welcome to the Banked Fire. The beds are stone with wool on top and the ale's brewed "
        "down here, so it tastes like down here. Most people come round to it by the second "
        "mug.\n\nIf you want to bind your hearth, say so and I'll set you a place by the fire. "
        "It's a long walk back from topside otherwise."),
    "oh_quartermaster": (
        "Quartermaster Dolf Ironledger", "dwarf", "male", 7,
        ["runeforged_strongbox", "healing_potion_mega", "mana_potion_mega", "meal_kodo_ribs",
         "drink_birch_wine", "whetstone", "flux_strong", "component_string", "glue", "parchment",
         "coal", "thread_fine", "resin", "spiced_stew", "hunters_brace_platter"],
        True,
        "Company store. Everything on these shelves came down a rope or out of the rock, and "
        "the rope goods cost more.\n\nHave a look. If you need something I don't stock, tell me"
        " and I'll put it on the next order, but the next order is a month out."),
    "oh_smith": (
        "Smith Hulda Emberfall", "dwarf", "female", 5,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin",
         "healing_potion_mega", "mana_potion_mega", "bs300_deepearth_axe_1h",
         "bs300_bloodiron_feet", "bs300_bloodiron_legs", "bs_mithril_shield"],
        True,
        "Mind the quench trough, it's hot.\n\nEverything on the rack is dark iron and I made "
        "all of it. If you'd rather make your own, the anvil in the yard is open to anyone, and"
        " Forgemaster Garrun over at the smeltery teaches. He's hard on beginners but he's "
        "fair."),
    "oh_armorer": (
        "Armorer Thrain Runehammer", "dwarf", "male", 9,
        ["whetstone", "flux_strong", "coal", "thread_fine", "healing_potion_mega",
         "mana_potion_mega", "bs300_truesilver_wrist", "bs300_kit_deepearth",
         "bs300_bloodiron_legs", "bs_mithril_shield"],
        True,
        "Plate and mail, and I'll set a rune in either if you can pay for it.\n\nI don't repair"
        " topside armour. I'm not being rude, the steel's too soft to take our rivets. I can "
        "sell you something that'll last longer down here."),
    "oh_mining_supplier": (
        "Shaft-Warden Kelda Deepvein", "dwarf", "female", 1,
        ["coal", "flux_strong", "whetstone", "component_string", "resin", "glue",
         "healing_potion_mega", "drink_waterskin", "meal_trailbread"],
        False,
        "Sign the board before you go down the head and sign it again when you're back up. I "
        "check it every shift, and if a name's missing its second mark I send people "
        "looking.\n\nThere's dark iron in the sand outside the gate as well, if you'd rather "
        "dig there. Nobody here will stop you. Just watch for the hive while your head's down."),
    "oh_reagents": (
        "Alchemist Sigrun Vialwright", "dwarf", "female", 11,
        ["healing_potion_mega", "mana_potion_mega", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_leaded", "vial_empty"],
        False,
        "Careful with the blue jars, they stain.\n\nMost of what I brew starts as mushrooms "
        "from the Lantern Wood. The young caps are the good ones, before they open. I pay for "
        "them, if you're heading out that way. Nobody else in town will go."),
    "oh_powder": (
        "Powderman Brokk Shortfuse", "dwarf", "male", 2,
        ["bomb_sapper", "coal", "glue", "component_string", "flux_strong", "healing_potion_mega",
         "vial_empty"],
        False,
        "You can stand closer than that. If I thought any of this was going off I wouldn't be "
        "sat on it.\n\nBlasting charges for the mine, mostly. The small ones are for the hive. "
        "They dig up into our tunnels a few times a year and a charge down the hole is quicker "
        "than arguing."),
}

ONYXHOLLOW_AMBIENT = {
    "oh_thane": (
        "Thane Morgrim Onyxhand", "dwarf", "male", 0,
        "You came down through the Dry Deep. We don't get many who do.\n\nI'm Morgrim. I run "
        "the working, which means the mine, the forges and the gate. Trade's welcome and the "
        "shops are on the Row behind you. If you're looking for work as well, talk to Captain "
        "Yrsa at the gate. She always has more trouble than guards."),
    "oh_forgemaster": (
        "Forgemaster Garrun Slagborn", "dwarf", "male", 4,
        "I teach mining and smithing, and I teach them together. I've no use for a smith who "
        "can't tell good ore from bad.\n\nShow me what you already know and we'll start from "
        "there."),
    "oh_gate_captain": (
        "Gate-Captain Yrsa Stonebar", "dwarf", "female", 6,
        "The Thane says the gate opens for trade, so it opens for you. I'd still like to know "
        "your business before you go back out.\n\nThere are three things to watch for out "
        "there. The hive's to the south-east. The mushroom wood is south-west, and it's worse "
        "than it looks. North-east are the old diggings, and the people in them used to live "
        "here. Don't expect a welcome."),
    "oh_gate_guard_w": (
        "Gate-Guard Dunmar", "dwarf", "male", 8,
        "Knock the sand off your boots before you go up the Row, would you? Hulda found grit in"
        " her quench last week and we all heard about it."),
    "oh_gate_guard_e": (
        "Gate-Guard Oda", "dwarf", "female", 10,
        "Six years I've stood on this gate. I've seen the hive come right up to the towers "
        "twice. Both times they turned round at the braziers, so we keep the braziers lit."),
    "oh_wall_sentry": (
        "Sentry Rurik Boltwright", "dwarf", "male", 3,
        "Quiet a moment.\n\n...No. Thought I heard digging. The hive tunnels under the wall "
        "sometimes, so I spend most of my watch with an ear to the rock. You get so you can "
        "tell them from our own miners."),
    "oh_vault_keeper": (
        "Vault-Keeper Aldis Greylock", "dwarf", "female", 1,
        "Every bar poured in Onyxhollow gets weighed and written down here. I have the books "
        "going back to the first shaft.\n\nSome of the names in the early ones belong to people"
        " who were put out of the gate. The Thane wanted them struck from the record. I told "
        "him the weights were still true, and he let it go."),
    "oh_shrine_keeper": (
        "Ashkeeper Torvald", "dwarf", "male", 5,
        "This fire was lit from the first furnace we built, and it hasn't gone out since. "
        "Keeping it fed is my whole job.\n\nYou're welcome to warm your hands. Half the town "
        "does on their way to shift."),
    "oh_stoker": (
        "Stoker Hald Cinderlung", "dwarf", "male", 7,
        "The furnace takes a cart of coal a shift, and I'm the one who shovels it.\n\nGarrun "
        "says the heat is where the craft is. He's probably right, but I notice he says it from"
        " the other side of the yard."),
    "oh_loremaster": (
        "Loremaster Ingrid Pagewright", "dwarf", "female", 9,
        "Have you seen the walls out on the Strand? There are tide marks on them, high up. That"
        " was a sea once, with a shoreline, and somebody must have lived on it.\n\nI'd like to "
        "find out who. The Thane thinks it's a waste of lamp oil, so I mostly ask travellers. "
        "If you come across anything out there that looks made rather than grown, I'd be glad "
        "to hear about it."),
    "oh_geomancer": (
        "Geomancer Vigdis Stonesong", "dwarf", "female", 11,
        "You walked through the caves above us to get here, the dry ones with the holes up to "
        "the desert. That's our roof, and it's a lot thinner than people here like to think "
        "about.\n\nI listen to it for the Thane. It's holding, for now. I'd be happier if "
        "things stopped eating the pillars."),
}

#: The three people outside the gate, in The Black Strand (handbuilt_black_strand.NPC_POSITIONS).
#: The geologist is from Earth and is drawn as a human; the other two are Dark Iron.
BLACK_STRAND_AMBIENT = {
    "bs_lookout": (
        "Lookout Hervi Longstair", "dwarf", "male", 2,
        "You made it down. Sit a minute if you need to, it's a long stair.\n\nI'm posted here "
        "to see who comes down and send them on to the gate. Follow the slag road south-east "
        "and keep to it. You'll see the braziers. Onyxhollow's at the end, between the two "
        "towers."),
    "bs_geologist": (
        "Noor Haddad", "human", "female", 6,
        "Oh, hello. Sorry, I don't get many people coming past.\n\nI'm a geologist. I was one "
        "before all this, in Amman, and it turns out the job still exists if you don't mind who "
        "you work for. The surveyors up at Fourth Peg told me about the caves and I kept going "
        "down. I've been camped here about a month. The dwarves think I'm odd but they sell me "
        "bread."),
    "bs_castout": (
        "Brannoc", "dwarf", "male", 6,
        "I'm allowed as far as this brazier. Yrsa lets me sit here as long as I don't go near "
        "the gate.\n\nI lived in there for forty years. I was put out with the rest of my "
        "shift and I've been in the old diggings since. If you're going into town, don't tell "
        "them you spoke to me. It won't help you."),
}
