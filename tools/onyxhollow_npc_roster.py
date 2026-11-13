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

VOICE: craftsmen. Short sentences, exact about weights and tempers, no interest in the surface.
They say "topside" the way a sailor says "ashore". They do not explain themselves to visitors and
they do not turn away anyone who can pay or carry.

THE CASTOUTS are the one thing nobody will discuss past a sentence. People were put out of the
gate. They are in the old diggings. That is all a visitor gets, and the quests are where the rest
of it comes out.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

ONYXHOLLOW_VENDORS = {
    "oh_innkeeper": (
        "Innkeeper Brenna Coalcask", "dwarf", "female", 3,
        ["bread_and_cheese", "roasted_meat", "meal_kodo_ribs", "meal_spiced_haunch",
         "drink_barley_beer", "drink_honeyed_mead", "healing_potion_mega", "mana_potion_mega",
         "spiced_stew", "cook_flour", "cook_spice", "cook_mushroom", "cook_ale", "cook_water"],
        False,
        "The Banked Fire. Beds are stone with wool on them and the ale is brewed down here, from "
        "what grows down here. You will get used to it or you will not.\n\nRest by the hearth and "
        "the hearth will know you. Come back to it from anywhere - topside, the sand, wherever "
        "your business takes you. That is worth more than the bed."),
    "oh_quartermaster": (
        "Quartermaster Dolf Ironledger", "dwarf", "male", 7,
        ["runeforged_strongbox", "healing_potion_mega", "mana_potion_mega", "meal_kodo_ribs",
         "drink_birch_wine", "whetstone", "flux_strong", "component_string", "glue", "parchment", "coal",
         "thread_fine", "resin", "spiced_stew", "hunters_brace_platter"],
        True,
        "Company store. Everything in it came down a rope or out of the rock, and the price tells "
        "you which.\n\nIf it is on the shelf it is for sale. If it is not on the shelf, I do not "
        "have it, and asking twice will not put it there."),
    "oh_smith": (
        "Smith Hulda Emberfall", "dwarf", "female", 5,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin",
         "healing_potion_mega", "mana_potion_mega", "bs300_deepearth_axe_1h",
         "bs300_bloodiron_feet", "bs300_bloodiron_legs", "bs_mithril_shield"],
        True,
        "Dark iron does not forgive a cold strike. You hit it right, at the right heat, or you "
        "start again with less of it.\n\nWhat is on the rack is mine and it is sound. If you "
        "want to make your own, the anvil in the yard is free to anyone who can use it and "
        "Forgemaster Garrun will tell you whether you can."),
    "oh_armorer": (
        "Armorer Thrain Runehammer", "dwarf", "male", 9,
        ["whetstone", "flux_strong", "coal", "thread_fine", "healing_potion_mega",
         "mana_potion_mega", "bs300_truesilver_wrist", "bs300_kit_deepearth",
         "bs300_bloodiron_legs", "bs_mithril_shield"],
        True,
        "Plate, mail, and the rune that makes either of them worth wearing. In that order of "
        "price.\n\nI will not fit topside work. I will sell you something better than what you "
        "came in with and you can carry the old set out yourself."),
    "oh_mining_supplier": (
        "Shaft-Warden Kelda Deepvein", "dwarf", "female", 1,
        ["coal", "flux_strong", "whetstone", "component_string", "resin", "glue",
         "healing_potion_mega", "drink_waterskin", "meal_trailbread"],
        False,
        "Nobody goes down the head without signing the board and nobody comes up without "
        "signing it again. That is the whole of my rule and I have never needed a second "
        "one.\n\nDark iron runs in the sand out there as well as in our rock. The seam does not "
        "care whose side of the gate it is on. If you are digging it, dig it properly."),
    "oh_reagents": (
        "Alchemist Sigrun Vialwright", "dwarf", "female", 11,
        ["healing_potion_mega", "mana_potion_mega", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_leaded", "vial_empty"],
        False,
        "Everything green in these bottles started as something blue out on the sand. The caps "
        "are good for more than light, if you know which ones and you pick them before they "
        "open.\n\nI buy them. I am the only one in this town who will admit to wanting anything "
        "from the other side of the gate."),
    "oh_powder": (
        "Powderman Brokk Shortfuse", "dwarf", "male", 2,
        ["bomb_sapper", "coal", "glue", "component_string", "flux_strong",
         "healing_potion_mega", "vial_empty"],
        False,
        "Stand where you like. If I thought it was going to go off I would not be standing "
        "here either.\n\nBlasting charges for the face, and the smaller sort for whatever comes "
        "up the face after you have opened it. Same powder. Different amount of running."),
}

ONYXHOLLOW_AMBIENT = {
    "oh_thane": (
        "Thane Morgrim Onyxhand", "dwarf", "male", 0,
        "You came down the long way. Nobody comes down the long way by accident.\n\nOnyxhollow "
        "is a working, not a kingdom, and I am the one who signs for it. We dig, we smelt, we "
        "forge, and we keep a gate shut on a beach we did not ask for. If you have trade, the "
        "Row is behind you. If you have trouble, it had better be somebody else's."),
    "oh_forgemaster": (
        "Forgemaster Garrun Slagborn", "dwarf", "male", 4,
        "Ore in one hand, hammer in the other. I teach both halves or neither. There is no "
        "sense knowing where to dig if you cannot do anything with what comes out.\n\nShow me "
        "what you know and I will show you what you do not."),
    "oh_gate_captain": (
        "Gate-Captain Yrsa Stonebar", "dwarf", "female", 6,
        "The gate opens for you because the Thane says it opens for trade. It shuts behind you "
        "because I say so.\n\nHive to the south-east, lights to the south-west, and the old "
        "diggings north-east. Do not bring any of the three back with you."),
    "oh_gate_guard_w": (
        "Gate-Guard Dunmar", "dwarf", "male", 8,
        "Sand on your boots. Knock it off before the Row. Hulda will not thank you for grit in "
        "her quench."),
    "oh_gate_guard_e": (
        "Gate-Guard Oda", "dwarf", "female", 10,
        "Six years on this door. The things outside have not got any prettier and the people "
        "coming in have not got any cleverer."),
    "oh_wall_sentry": (
        "Sentry Rurik Boltwright", "dwarf", "male", 3,
        "I watch the wall from the inside. You would think that was the easy posting.\n\nIt is "
        "the rock I am listening to. The hive digs, and it does not knock first."),
    "oh_vault_keeper": (
        "Vault-Keeper Aldis Greylock", "dwarf", "female", 1,
        "Every bar poured in this town is weighed here and written here. I have the book for "
        "every year since the first shaft.\n\nThere are names in the early pages that are not "
        "said aloud any more. They are still in the book. I do not strike a line through a "
        "weight just because the hand that poured it was sent away."),
    "oh_shrine_keeper": (
        "Ashkeeper Torvald", "dwarf", "male", 5,
        "The fire in the bowl was lit from the first furnace and it has not been out since. "
        "That is all the shrine is. We do not pray to it. We keep it.\n\nPut your hand near it "
        "if you are cold. That is what it is for."),
    "oh_stoker": (
        "Stoker Hald Cinderlung", "dwarf", "male", 7,
        "Furnace eats a cart of coal a shift and gives back a bar and a headache.\n\nGarrun "
        "says the heat is the craft. Garrun does not shovel."),
    "oh_loremaster": (
        "Loremaster Ingrid Pagewright", "dwarf", "female", 9,
        "A beach, under a desert, with the tide marks still on the wall. I have been told it is "
        "not our concern because it is not rock.\n\nIt was a sea. Seas have shores, and shores "
        "have people, and I would like to know who stood on this one before it was dark. Nobody "
        "else in Onyxhollow would."),
    "oh_geomancer": (
        "Geomancer Vigdis Stonesong", "dwarf", "female", 11,
        "The rock above us is hollow. You walked through it to get here - the dry caves, the "
        "holes in the desert. I can hear it settle.\n\nThe Thane asks me every month whether the "
        "roof will hold. Every month I tell him it will hold this month."),
}
