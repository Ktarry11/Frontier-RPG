"""
The people of Tempest Isle (52-58): Ashclaim Landing, the Ashclaim Works and Cinderwharf.

Data only - tools/sync_tempest_npcs.py writes these into data/npcs/*.json and takes every
coordinate from the three layout modules' NPC_POSITIONS.

WHAT THE ISLAND IS. A Dark Iron city, Khaz Varun, went dark generations ago. Thane Durgan Ashhold
holds the deed to it and nothing else. The sea route opened after the Integration, the goblins
read the deed as an asset, and a joint venture called the Ashclaim put a town on the north-east
shore inside a season. The dwarves want their dead out of the hall. The goblins want the foundry
running. Both need the same doors opened, and that is the only reason they share a wharf.

THREE HUMANS FROM EARTH work here because the Ashclaim pays for what they know: a ferry doctor
from Mombasa at the landing, a botanist from Quito in the Green Belt, a volcanologist from
Kagoshima at the Works, and a marine loss adjuster from Singapore in the Merchant House. The
Integration was THREE YEARS AGO and each of them says what it cost.

VOICE (Kyle, 13 Nov 2026): whole sentences as a person says them across a table. No one-word or
two-word sentences, no lists of nouns standing in for a sentence, no short punchy closing line,
no dashes, and contractions throughout.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

_FOOD = ["meal_ember_glazed_ribs", "bread_and_cheese", "roasted_meat", "meal_kodo_ribs",
         "meal_spiced_haunch", "drink_barley_beer", "drink_honeyed_mead", "spiced_stew",
         "hunters_brace_platter"]
_POTS = ["healing_potion_mega", "mana_potion_mega", "healing_potion_masterwork",
         "mana_potion_masterwork"]
_SMITH = ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin"]

# ------------------------------------------------------------------ Tempest Shallows
SHALLOWS_VENDORS = {
    "ts_landing_quartermaster": (
        "Quartermaster Durn Slagbelt", "dwarf", "male", 4,
        _POTS + ["meal_kodo_ribs", "drink_birch_wine", "whetstone", "flux_strong",
                 "component_string", "glue", "parchment", "coal", "thread_fine", "resin"], True,
        "Everything on these shelves came off that jetty and was carried up here by hand, and "
        "the price reflects the carrying.\n\nI kept the stores for a mining company on the "
        "mainland for thirty years. The Thane asked for somebody who could count, and I was "
        "the only one of his people who'd never lost a crate."),
    "ts_landing_cook": (
        "Cook Halla Brinepot", "dwarf", "female", 9,
        _FOOD + ["cook_flour", "cook_spice", "cook_ale", "cook_water", "healing_potion_mega"],
        False,
        "There's a pot on and there are bedrolls in the long tent, and you're welcome to "
        "both.\n\nMost of what I cook comes out of the shallows east of here, because the "
        "supply boat only brings flour and complaints. You'll get used to crab."),
}
SHALLOWS_AMBIENT = {
    "ts_landing_bosun": (
        "Bosun Grekka Sparfall", "goblin", "female", 3,
        "Mind the planks when you come off the boat, because half of them were laid in the "
        "dark.\n\nThis is Ashclaim Landing. The Thane's city is four hundred feet under that "
        "hill to the south-east, and the only road to the town runs round the volcano through "
        "country that bites. I run the jetty, so if it floats or it's tied to something that "
        "floats, it's my business."),
    "ts_landing_surveyor": (
        "Surveyor Pim Brackwhistle", "goblin", "male", 5,
        "I'm costing this island for the underwriters, which means every tree, every seam "
        "and every hole in the ground gets a number.\n\nMy cousin Nix holds the paper on the "
        "claim over in Cinderwharf, and I hold the tape measure. He thinks his is the harder "
        "job because he has to talk to the Thane."),
    "ts_landing_medic": (
        "Dr. Imani Mwangi", "human", "female", 12,
        "If you're bleeding, sit down on the crate, and if you aren't, try to stay that way "
        "until the boat comes back.\n\nI ran the clinic on the Likoni ferry in Mombasa for "
        "eleven years. Three years ago the ferry docked at a pier that hadn't been there in "
        "the morning, and I've been patching up dwarves and goblins ever since. The burns "
        "here are worse than anything I saw at home, but the patients complain a lot less."),
    "ts_landing_shipwright": (
        "Shipwright Rozz Keelhaul", "goblin", "male", 14,
        "I build the barges that carry ore round the island, and something in the shallows "
        "keeps breaking them.\n\nThey gave me a beach, a saw pit and a crew of four. I've "
        "launched six hulls since spring and I've got two of them left."),
    "ts_gate_watch": (
        "Gatewatch Bron Emberhold", "dwarf", "male", 6,
        "That arch behind me is the front door of Khaz Varun, and my family kept it for nine "
        "generations before the city went dark.\n\nI've never been through it. The Thane "
        "posted me here to watch who goes in and to count who comes out, and the second "
        "number is always the smaller one."),
    "ts_belt_prospector": (
        "Prospector Hesta Ironwick", "dwarf", "female", 7,
        "This is good ground, with mithril near the surface and truesilver if you know the "
        "colour of the rock it hides in.\n\nI'd be richer if the gorillas didn't keep "
        "throwing my samples back at me. I've started to think they do it on purpose."),
    "ts_belt_botanist": (
        "Teodora Vasquez", "human", "female", 11,
        "Please watch where you put your feet, because I haven't named half of what's "
        "growing here yet.\n\nI taught botany at the university in Quito and I spent my "
        "summers counting orchids in the cloud forest. This jungle grows on ash that's still "
        "warm, and nothing in it matches my books. The Ashclaim pays me to tell them which "
        "plants are worth money. I'd have done it for the bedroll."),
    "ts_shallows_wader": (
        "Tidewalker Jex", "goblin", "male", 8,
        "The water's only waist deep all the way out to the last rock, so you can walk to "
        "most of the wrecks.\n\nHalf of them still have their cargo aboard. I'd be out there "
        "myself if the crabs hadn't taken my boots, and then tried for the feet inside "
        "them."),
}

# ------------------------------------------------------------------ The Ashen Reach
REACH_VENDORS = {
    "ar_gate_factor": (
        "Factor Grib Tallyman", "goblin", "male", 10,
        _POTS + ["bomb_sapper", "whetstone", "coal", "component_string", "glue",
                 "drink_barley_beer", "bread_and_cheese"], True,
        "Everything that goes through this gate gets weighed, and that includes you if "
        "you're carrying ore.\n\nCinderwharf is through the arch behind me. I sell a few "
        "things to people heading the other way, because the walk to the Works is long and "
        "people forget what they needed until they're past me."),
}
REACH_AMBIENT = {
    "ar_works_foreman": (
        "Foreman Brakka Sootmantle", "dwarf", "female", 10,
        "You're standing in the Ashclaim Works, and the smelter behind me is the only thing "
        "on this island that's making money.\n\nI've got sixty people here and I'd like to "
        "keep all sixty. The ground shakes twice a day, the flats to the north are full of "
        "things that walk through fire, and the goblins keep asking why we're behind."),
    "ar_works_enginewright": (
        "Enginewright Tobble Vantz", "goblin", "male", 12,
        "I keep the pump engine and the winding gear running at the mine head, and they "
        "both hate me.\n\nEverything here corrodes. The air off the vents eats brass in a "
        "month and iron in a season, so I spend half my time rebuilding what I built the "
        "month before."),
    "ar_door_warden": (
        "Doorwarden Kettil Grimstead", "dwarf", "male", 11,
        "The hole behind me goes down into the Emberdeep, and I'm here to tell you what's "
        "in it before you go.\n\nThere's a lake of fire with islands of cooled rock standing "
        "in it, and everything that lives down there was born in the lake. The Thane's "
        "people sealed this door once. The mountain opened it again the day the world "
        "changed."),
    "ar_coast_surveyor": (
        "Coast-Surveyor Mizzi Dredgeline", "goblin", "female", 15,
        "I'm charting this coast for a harbour, and so far the coast has sunk two of my "
        "boats.\n\nThe wrecks along here are older than the Ashclaim. Somebody was sailing "
        "to this island long before the goblins found it on a map, and the naga have "
        "moved into what those ships left behind."),
    "ar_flats_scout": (
        "Scout Varga Cinderstep", "dwarf", "female", 4,
        "Stay on the dark ground out here, because the pale crust is thin and there's "
        "steam under it.\n\nI walk the Cinder Flats for the Foreman and mark where the "
        "vents have moved. They move most weeks. My job is to make sure the ore carts "
        "find out from me and not from the ground."),
    "ar_works_assayer": (
        "Assayer Ruddi Halfweight", "goblin", "female", 18,
        "Bring me a rock and I'll tell you what it's worth, and I'll be right to the "
        "copper.\n\nThe Works pays the dwarves by what I weigh, so half the yard thinks "
        "I'm a thief. The other half knows I'm the reason the goblins haven't cheated "
        "them yet."),
    "ar_works_powderman": (
        "Blaster Orrin Slowmatch", "dwarf", "male", 2,
        "Don't smoke near the red shed, and don't ask me to explain why.\n\nI set the "
        "charges for the mine head. Blasting inside a volcano takes a steady hand, and "
        "I've still got both of mine, which is more than the last blaster could say."),
    "ar_works_volcanologist": (
        "Dr. Kenji Arakawa", "human", "male", 9,
        "I watch the mountain for the Ashclaim, and I tell them when to be afraid of "
        "it.\n\nI spent twenty years at the observatory in Kagoshima watching Sakurajima, "
        "which erupts most days and has never surprised me. Three years ago I walked out "
        "of the observatory and the bay was gone. This volcano doesn't behave like any "
        "I've studied. It has a pulse, and I mean that as a measurement."),
}

# ------------------------------------------------------------------ Cinderwharf
CINDERWHARF_VENDORS = {
    "cw_quartermaster": (
        "Quartermaster Vela Coalwright", "dwarf", "female", 2,
        _POTS + ["runeforged_strongbox", "duskwoven_carryall", "warden_reliquary",
                 "deepdelve_bearer", "whetstone", "flux_strong", "component_string",
                 "parchment", "coal", "thread_fine", "resin"], True,
        "What's on the front shelf is for anybody with coin, and what's behind me is for "
        "people the Ashclaim trusts.\n\nYou earn that by doing the Thane's work or the "
        "Underwriter's, and I don't much mind which. I've had people try to earn it with "
        "charm, and none of them got past the front shelf."),
    "cw_blacksmith": (
        "Smith Hogar Deepvein", "dwarf", "male", 3,
        _SMITH + _POTS + ["bs300_deepearth_axe_1h", "bs300_bloodiron_feet",
                          "bs300_bloodiron_legs", "bs_mithril_shield"], True,
        "I work plate and mail, and I work them out of ore that came up through the old "
        "city's gate.\n\nIf you want leather stitched, the goblins keep somebody for that "
        "down by the water. I wouldn't trust the stitching, but I'm told the price is "
        "fair."),
    "cw_armoursmith": (
        "Armoursmith Brenna Stonecast", "dwarf", "female", 5,
        _SMITH + _POTS + ["bs300_truesilver_wrist", "bs300_kit_deepearth",
                          "bs300_bloodiron_legs", "bs_mithril_shield"], True,
        "Everything I make is forged from Khaz Varun's own iron, and I think it knows the "
        "way home.\n\nMy grandmother's mark is on a breastplate somewhere under that "
        "hill. I'd like to see it before I'm too old to lift a hammer."),
    "cw_innkeeper": (
        "Innkeeper Dolla Pinchspark", "goblin", "female", 2,
        _FOOD + ["drink_starfall_wine", "cook_flour", "cook_spice", "cook_mushroom",
                 "cook_ale", "cook_water"] + _POTS, False,
        "Welcome to the Tapped Vein, where the dwarves drink on the left and my lot drink "
        "on the right.\n\nThe middle table is where the contracts get signed, so don't sit "
        "there unless you've brought a pen. Beds are upstairs and the stew is whatever "
        "came off the boat."),
    "cw_general_goods": (
        "Trader Gex Sootpocket", "goblin", "male", 6,
        ["bomb_sapper", "coal", "glue", "component_string", "flux_strong", "parchment",
         "vial_empty", "drink_waterskin", "meal_trailbread"] + _POTS, False,
        "I sell lamp oil, pipe fittings and blasting powder, and I ask no questions about "
        "the powder.\n\nI'd appreciate it if you didn't ask me any either. The hatch stays "
        "shut when the Thane's people walk past, and that suits both of us."),
    "cw_alchemist": (
        "Alchemist Pell Fizzlewick", "goblin", "male", 9,
        _POTS + ["battle_elixir_superior", "guardian_elixir_superior",
                 "elixir_of_greater_endurance", "vial_leaded", "vial_empty"], False,
        "I sell vials and reagents, and I buy whatever the vents cough up.\n\nThe yellow "
        "crust off the fissures is worth more than the ore, ounce for ounce. I haven't "
        "told the dwarves that, and I'd be grateful if you didn't either."),
    "cw_salvage_broker": (
        "Broker Tazz Hookfinger", "goblin", "male", 3,
        ["component_string", "glue", "resin", "coal", "whetstone"] + _POTS, True,
        "Whatever you dragged out of that hole, I'll take it off you and I'll pay over the "
        "odds for it.\n\nI pay well because I know what Dark Iron work fetches on the "
        "mainland. The Thane calls it grave robbing. I call it the reason his town has a "
        "roof."),
}
CINDERWHARF_AMBIENT = {
    "cw_thane_ashhold": (
        "Thane Durgan Ashhold", "dwarf", "male", 1,
        "I'm Durgan Ashhold, Thane of Khaz Varun, and the title is older than this wharf "
        "and worth a good deal less.\n\nMy great-grandfather's hall is four hundred feet "
        "under the south shore and it's full of things that used to be my kin. Speak to "
        "the Underwriter if you want to be paid. Speak to me if you want to help me empty "
        "that hall."),
    "cw_shrine_keeper": (
        "Keeper Morn Ashhold", "dwarf", "male", 8,
        "This flame is for the ones who are still down there, and I keep it lit for "
        "them.\n\nMy cousin Durgan keeps the claim and I keep the fire. Neither of us is "
        "sure which of the two matters more, and we've agreed not to argue about it in "
        "front of the goblins."),
    "cw_underwriter": (
        "Underwriter Nix Brackwhistle", "goblin", "male", 4,
        "I hold the paper on the claim, which is a polite way of saying that I hold the "
        "claim.\n\nThe Thane wants his ancestors laid to rest and I want a foundry that "
        "pours iron. Those turn out to need the same doors opened, so we get along better "
        "than either of us expected."),
    "cw_flight_master": (
        "Wind Rider Keeper Zazzi", "goblin", "female", 7,
        "The pad's built out over the water so the downdraft doesn't take the roofs off "
        "the wharf.\n\nWe learned that the expensive way. I can put you on a bird to "
        "Saltspur whenever you like, and from there you can get to anywhere."),
    "cw_harbourmaster": (
        "Harbourmaster Skezz Mooringline", "goblin", "female", 16,
        "Every hull that ties up here pays a berth fee, and every hull that sinks out "
        "there costs me one.\n\nI've lost four barges this season between the wharf and "
        "the landing. The Underwriter wants to know why, and I'd like to have an answer "
        "that isn't just the sea."),
    "cw_archivist": (
        "Deedkeeper Thora Runebrand", "dwarf", "female", 12,
        "I keep the rolls of Khaz Varun, which is every birth, every oath and every debt "
        "the city recorded before it went dark.\n\nThe Thane's claim rests on what's in "
        "these rolls. The goblins have offered to make me copies. I've read their copies "
        "of other things, so I keep the key on my neck."),
    "cw_claims_clerk": (
        "Adjuster Priya Raman", "human", "female", 6,
        "I assess losses for the Underwriter, so I'm the person who decides whether a "
        "sunk barge was bad luck or bad seamanship.\n\nI did the same job in Singapore "
        "for a marine insurer. Three years ago I was inspecting a container ship when "
        "the harbour changed around it, and my employer and my flat went with the old "
        "one. Goblins understand insurance better than anyone I worked with there."),
}
