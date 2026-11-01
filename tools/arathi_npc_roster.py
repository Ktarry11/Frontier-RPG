"""
The people of the Arathi Highlands (32). Data only.

tools/sync_arathi_npcs.py writes these into data/npcs/*.json and takes every coordinate from the
three zone modules' NPC_POSITIONS, so the layout stays the only place a position is decided.
Class and profession trainers come from the shared pipelines (build_class_trainers.TOWNS,
build_profession_trainers), as they do in every other town.

THREE SETTLEMENTS, THREE DIFFERENT RELATIONSHIPS TO THE GROUND THEY ARE ON.

  REFUGE POINTE (West, 28-33) is a Horde forward camp inside a human ruin, and it kept the ruin's
  name because the name was already painted on the gate and nobody wanted to be the one to argue
  about it. Tents against standing walls. Everything here is temporary and has been for two years.

  HAMMERFALL (Central, 33-37) is a hold. Orcs took the ground and the Forsaken moved in beside
  them, and a tauren delegation arrived afterwards and has not left - see
  claude/orc_building_prompts.md, which is where the mixed-hold decision is written down. It has
  a longhouse, a war forge, a wind rider roost, an apothecary and an inn, because Kyle asked for
  a full town and a full town is the difference between a place people are holding and a place
  people live.

  SALTSPUR LANDING (East, 37-40) is four buildings and a jetty on an archipelago full of
  Bloodsail. It is a beachhead, run by a bosun rather than an officer, and everyone there knows
  the Horde has not decided whether to reinforce it or forget about it.

REPUTATION IS SPLIT BY WHO ASKS, NOT BY WHERE. Kyle: "quest rep will be mixture of orgrimmar,
undercity, and thunderbliff depending on npcs. We can have a mixture." So the orcs' work pays
Orgrimmar, the apothecary's and the Deathguard's pays the Forsaken, and the tauren delegation's
pays Thunder Bluff - wired per quest id through factions.json's `also` lists, which beat the
zone default. tools/build_arathi_quests.py owns that mapping.

VOICE. Orcs here are garrison soldiers, not warriors in a saga: dry, procedural, tired of the
moor. The Forsaken are bureaucratic about horrifying things. The tauren are patient and are not
being listened to. The one human and the one goblin are both opportunists who stayed.

(record shapes: VENDORS  -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT  -> name, race, gender, variant, greeting)
"""

# ==================================================================== ARATHI WEST - 28-33
# Refuge Pointe, Thoradin's Wall, the moor, and a farm the Syndicate is working.

WEST_AMBIENT = {
    "arathi_refuge_commander": (
        "Commander Zel Raskal", "orc", "female", 4,
        "Two years on this moor. We hold the road, the wall and this pile of somebody else's "
        "masonry, and I have stopped asking Orgrimmar for a third thing."),
    "arathi_refuge_scout": (
        "Scout Grim Hollowfoot", "forsaken", "male", 9,
        "The moor looks empty. It is not empty. It is just very good at being wide."),
    "arathi_wall_warden": (
        "Warden Ada Rook", "human", "female", 2,
        "I stood at this gap for a year and a half before anyone came through it, and then it was "
        "you. Go on, then. It is open."),
    "arathi_stromgarde_antiquarian": (
        "Antiquarian Vesh", "forsaken", "female", 14,
        "Stromgarde is a ruin with a ruin under it. The Syndicate is squatting in the upper one "
        "and has not noticed the stair."),
    "arathi_moor_shepherd": (
        "Shepherd Ogrin", "orc", "male", 11,
        "Somebody has to keep the stag herd off the road, and it turns out somebody is me. I was "
        "an axethrower. Ask me about it and I will tell you at length."),
    "arathi_goshek_informant": (
        "Nalla Deeps", "goblin", "female", 6,
        "Go'Shek Farm still brings in a harvest. The Syndicate took the farm, not the farming, "
        "and somebody is buying the grain. I am interested in who."),
}

WEST_VENDORS = {
    "arathi_refuge_quartermaster": (
        "Quartermaster Horg", "orc", "male", 7,
        ["healing_potion_standard", "mana_potion_standard", "meal_trailbread", "drink_barley_beer",
         "whetstone", "vial_empty", "thread_fine", "small_burlap_sack"], True,
        "Camp stores. I requisition for a garrison of forty and I am supplied for a garrison of "
        "twelve, so take what you need and do not take more."),
    "arathi_refuge_innkeeper": (
        "Innkeeper Mura Flint", "forsaken", "female", 3,
        ["meal_trailbread", "drink_barley_beer", "bread_and_cheese", "spiced_wine",
         "meal_river_fish", "drink_spring_flask"], False,
        "There is a roof in the north corner that has held three winters. That is the inn. Set "
        "your hearth by the fire and I will not ask you anything else."),
    "arathi_refuge_flightmaster": (
        "Wind Rider Keeper Sharzak", "orc", "male", 16,
        ["meal_tough_jerky", "drink_waterskin"], False,
        "Two wyverns. One of them will take you to Hammerfall and one of them will take you to "
        "Tarren Mill, and which is which changes depending on their mood."),
}

# ================================================================= ARATHI CENTRAL - 33-37
# Hammerfall: a full town, orc-built, Forsaken-tenanted, with tauren guests who stayed.

CENTRAL_AMBIENT = {
    "hammerfall_commander": (
        "Overlord Gath'rok", "orc", "male", 1,
        "Hammerfall holds the middle of this region and the middle is the only part that matters. "
        "Everything that crosses Arathi crosses in front of me."),
    "hammerfall_sergeant": (
        "Sergeant Mok Blackstone", "orc", "female", 8,
        "Drill at dawn, wall at noon, drill again. The ogres come up out of the hold every few "
        "weeks and find us standing in the same place, which is the entire idea."),
    "hammerfall_stablemaster": (
        "Stablemaster Rukka", "orc", "female", 12,
        "Kodo on the left, wolves on the right, and never the other way round. I learned that "
        "the hard way and the kodo learned it harder."),
    "hammerfall_apothecary": (
        "Apothecary Dellwyn Voss", "forsaken", "male", 5,
        "The mere water in the basin has something living in it. I have written four reports. "
        "Undercity has acknowledged receipt of three."),
    "hammerfall_deathguard": (
        "Deathguard Olen", "forsaken", "male", 18,
        "I watch the east gate. Everything that has come through it in two years has been "
        "kobold, ogre, or a man with a very good reason, and the third kind is the problem."),
    "hammerfall_tauren_envoy": (
        "High Envoy Tamka Stillwater", "tauren", "female", 15,
        "The stone rings in this basin were raised by people who are gone, and the ogres are "
        "taking them down for wall stone. I have asked twice. I will ask a third time."),
    "arathi_ring_scholar": (
        "Scholar Innik Barrowmouth", "forsaken", "male", 21,
        "Four circles, one line, and the line is the road - which means the road is older than "
        "anyone who has ever walked it, including the people who think they built it."),
    "arathi_gorge_prospector": (
        "Prospector Thugg", "orc", "male", 19,
        "Drywhisker was a mine before the kobolds got it and it is a mine now. The difference is "
        "that the kobolds dug past the ore."),
    "arathi_refuge_runner": (
        "Runner Keska", "orc", "female", 22,
        "Refuge Pointe to Hammerfall and back, twice a week, on foot, because wyverns are for "
        "officers. Ask me what the road is doing and I will actually know."),
}

CENTRAL_VENDORS = {
    "hammerfall_quartermaster": (
        "Quartermaster Urga Ironhand", "orc", "female", 2,
        ["healing_potion_standard", "mana_potion_standard", "guardian_elixir_standard",
         "battle_elixir_standard", "meal_spiced_haunch", "drink_honeyed_mead", "whetstone",
         "flux_medium", "buckled_saddlebag"], True,
        "The hold's stores, and the hold's stores are good, because we have been here long "
        "enough to build shelves."),
    "hammerfall_innkeeper": (
        "Innkeeper Grettha", "forsaken", "female", 11,
        ["meal_spiced_haunch", "drink_honeyed_mead", "bread_and_cheese", "spiced_wine",
         "meal_river_fish", "drink_spring_flask", "salt"], False,
        "A real inn, with a real fire, and I will tell anyone in Orgrimmar who asks that we "
        "built it before the second watchtower and we were right to."),
    "hammerfall_windrider_master": (
        "Wind Rider Master Dreka", "orc", "female", 20,
        ["meal_tough_jerky", "drink_waterskin"], False,
        "The roost is full and the routes are flown. Hammerfall is on the map now, whatever "
        "Orgrimmar's cartographers are still printing."),
    "hammerfall_weaponsmith": (
        "Weaponsmith Krol Anvilbrand", "orc", "male", 13,
        ["whetstone", "flux_medium", "coal", "bs_stonemace", "sturdy_arrows", "heavy_bolts"], True,
        "War forge. Not a camp fire with a rock next to it - a forge, with a chimney, built by "
        "someone who knew what they were doing. Me."),
    "hammerfall_general_goods": (
        "Trader Molg", "orc", "male", 17,
        ["bread_and_cheese", "drink_barley_beer", "parchment", "thread_fine", "vial_empty",
         "small_burlap_sack", "worn_leather_satchel", "salt"], False,
        "Everything a soldier forgets to pack and then needs on the moor at four in the "
        "afternoon. I have made a study of it."),
    "hammerfall_reagent_vendor": (
        "Reagent-Keeper Shelna", "forsaken", "female", 7,
        ["vial_empty", "vial_leaded", "parchment", "thread_fine", "dye_mild", "resin",
         "tanning_reagent", "curing_salt"], False,
        "Components. Measured, labelled and dated, because the alternative is Apothecary Voss "
        "guessing, and he has guessed before."),
    "hammerfall_tauren_herbalist": (
        "Herbalist Nahto Greenhoof", "tauren", "male", 9,
        ["mana_potion_standard", "guardian_elixir_standard", "elixir_of_warding",
         "mushroom_broth", "spiced_stew", "resin"], False,
        "There is good growing in the basin and nobody here is looking at it. They are all "
        "looking at the ogres. The ogres will still be there next season. So will the plants, "
        "if somebody tends them."),
}

# ==================================================================== ARATHI EAST - 37-40
# Saltspur Landing, the barrow, a wreck and a hermit on a rock.

EAST_AMBIENT = {
    "saltspur_bosun": (
        "Bosun Kaz Tidewright", "orc", "male", 3,
        "I am a bosun running a shore camp, which is not a job that exists. Orgrimmar sent four "
        "boats and no officer, so here we are and here I am."),
    "saltspur_shipwright": (
        "Shipwright Oona Keelsplice", "goblin", "female", 10,
        "Every hull on this archipelago is on the rocks and I can see six of them from where I "
        "am standing. Give me a crew and a tide and I will give you two of them back."),
    "saltspur_scout": (
        "Scout Vel Ashgrave", "forsaken", "female", 6,
        "The Bloodsail are not raiding. They are holding. There is a difference and the "
        "difference is that holding means they want something that is already here."),
    "arathi_barrow_warden": (
        "Barrow-Watcher Yelza", "troll", "female", 4,
        "Dat barrow full of Arathor dead and dey still standin' watch. Three t'ousand years. "
        "Nobody told dem de job was over, an' I not goin' in dere to say it."),
    "arathi_bothy_hermit": (
        "The Bothy Hermit", "human", "male", 8,
        "I was on the ferry. Then the water was a different water and the ferry was on a rock, "
        "and that was three years ago, and this is my rock now."),
}

EAST_VENDORS = {
    "saltspur_quartermaster": (
        "Quartermaster Dreg", "forsaken", "male", 12,
        ["healing_potion_superior", "mana_potion_superior", "meal_river_fish",
         "drink_spring_flask", "guardian_elixir_standard", "battle_elixir_standard",
         "whetstone", "vial_leaded"], True,
        "Landed stores. Everything here came off a boat and some of it came off somebody "
        "else's boat, and I am not going to pretend otherwise."),
    "arathi_wreck_salvager": (
        "Salvager Pik Bronzewhistle", "goblin", "male", 5,
        ["parchment", "resin", "glue", "component_string", "fletching", "sinew",
         "worn_leather_satchel"], True,
        "Six wrecks on the flats and the tide only lets you at them twice a day. I know which "
        "two. That knowledge is the business."),
}
