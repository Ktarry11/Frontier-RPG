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
    # ---- trainers and the keeper (14 Nov 2026) ----
    "ct_cinderwharf": (
        "Battlemaster Ingra Coalbeard", "dwarf", "female", 10,
        "I train fighters of every kind, and I don't much care which kind you are.\n\nThe "
        "Thane brought me over to teach his own people before they went into the hall. Most of "
        "them have gone in now, so I've got time for anyone who can pay. Show me what you can "
        "do and I'll show you what comes next."),
    "pt_cinderwharf_forge": (
        "Forgemaster Ulfa Hammerdeep", "dwarf", "female", 11,
        "If you want to mine Khaz Varun's iron or work it, I can teach you both.\n\nThe ore "
        "on this island is better than anything on the mainland, and dark iron's the best of "
        "it. It's also the fussiest metal you'll ever put in a fire, so learn it from someone "
        "who's ruined plenty of it."),
    "pt_cinderwharf_herbs": (
        "Herbalist Zinnia Sporewick", "goblin", "female", 21,
        "I can teach you which plants on this island are worth picking and what to do with them "
        "once you've got them.\n\nThe Green Belt's full of things the mainland's never seen. "
        "Half of them will heal you and the other half will put you in Dr. Mwangi's tent, so "
        "it's worth paying someone to tell you which half is which."),
    "pt_cinderwharf_hide": (
        "Tanner Brog Ashpelt", "dwarf", "male", 5,
        "I work hides, leather and cloth, and I cook, because nobody else on this wharf will do "
        "it properly.\n\nA basilisk hide off the Cinder Flats makes the best leather I've ever "
        "handled. I'll teach you to skin it, cure it and stitch it, and I'll teach you what to "
        "do with the meat while you're at it."),
    "pt_cinderwharf_wood": (
        "Woodwright Kibble Sawtooth", "goblin", "male", 13,
        "I can teach you to cut timber and work it, and on this island that mostly means "
        "bloodwood and felbark.\n\nThe jungle wood's too green for hulls, so I use it for "
        "everything else. If you want to know which trees are worth felling, I've felled most "
        "of the wrong ones already."),
    "pt_cinderwharf_essence": (
        "Tinker Fezzik Coilspring", "goblin", "male", 17,
        "I teach engineering, and I'll tell you now that the vents on this island will try to "
        "eat everything you build.\n\nI keep the town's pumps running when Tobble at the "
        "Works can spare me a gasket. If you want to learn how to build something that lasts "
        "out here, I'm the one to ask."),
    "ak_cinderwharf": (
        "Artifact Keeper Hilde Ironveil", "dwarf", "female", 1,
        "I can change a set piece you're wearing into the version that suits the way you fight "
        "now, and I don't charge for it.\n\nIf you've brought a token up from the old city or "
        "out of the Emberdeep, I'll turn that into a piece for you as well. The Keepers sent me "
        "here because this is where the tokens are being found."),
}

#: Extra fields a record carries beyond the roster shape: what a trainer teaches.
EXTRA = {
    "ct_cinderwharf": {"trains_class": "*"},
    "pt_cinderwharf_forge": {"trains_profession": ["mining", "blacksmithing"]},
    "pt_cinderwharf_herbs": {"trains_profession": ["herbalism", "alchemy"]},
    "pt_cinderwharf_hide": {"trains_profession": ["skinning", "leatherworking", "tailoring",
                                                  "cooking"]},
    "pt_cinderwharf_wood": {"trains_profession": ["woodcutting", "woodworking"]},
    "pt_cinderwharf_essence": {"trains_profession": ["engineering"]},
}

#: SECOND DRAFT of every greeting (14 Nov 2026), laid over the tuples above by the sync. Same rule
#: as the quest text (tools/tempest_quest_text.py): who they are, what they do here, and what's
#: on their mind, said plainly. No little jokes and no closing line written to land.
GREETINGS = {
    # ---- Ashclaim Landing
    "ts_landing_bosun":
        "Welcome to Ashclaim Landing. Watch your step on the jetty, some of the planks are "
        "loose.\n\nI run the jetty and the boat to Saltspur. The Thane's old city is under the "
        "hill to the south-east, and the town is round the far side of the volcano. Most of the "
        "work here is getting things from one to the other.",
    "ts_landing_quartermaster":
        "I keep the landing's stores. Everything on these shelves was carried up from the "
        "jetty by hand, so it costs a bit more than on the mainland.\n\nI kept the stores for a "
        "mining company for thirty years before the Thane asked me to come out here.",
    "ts_landing_cook":
        "There's food in the pot and bedrolls in the long tent, and you're welcome to both.\n\n"
        "The supply boat mostly brings flour and salt, so a lot of what I cook comes out of the "
        "shallows to the east. I hope you like crab.",
    "ts_landing_surveyor":
        "I'm surveying this island for the underwriters. Every tree, every seam of ore and "
        "every hole in the ground needs a value written down.\n\nMy cousin Nix holds the "
        "Ashclaim's paper in Cinderwharf. I do the walking.",
    "ts_landing_medic":
        "If you're hurt, sit down on the crate and I'll have a look.\n\nI ran the clinic on the "
        "Likoni ferry in Mombasa for eleven years. Three years ago the ferry docked at a pier "
        "that hadn't been there that morning, and I've been treating dwarves and goblins ever "
        "since. Most of what I see here is burns.",
    "ts_landing_shipwright":
        "I build the barges that carry ore round the island.\n\nThey gave me this beach, a saw "
        "pit and a crew of four. I've launched six hulls since spring and I've only got two "
        "left. Something out in the shallows keeps sinking them.",
    "ts_gate_watch":
        "That arch is the front gate of Khaz Varun. My family kept it for nine generations "
        "before the city went dark.\n\nThe Thane has me here to count who goes in and who comes "
        "out. I've never been inside myself.",
    "ts_belt_prospector":
        "This is good ground for ore. There's mithril near the surface and truesilver if you "
        "know what rock to look for.\n\nThe gorillas keep throwing my samples back at me, so "
        "it's slow work.",
    "ts_belt_botanist":
        "Please watch where you step. Half of what's growing here hasn't been named yet.\n\nI "
        "taught botany at the university in Quito before I came through. The Ashclaim pays me "
        "to tell them which plants on this island are worth money. Nothing here is in any of "
        "my books.",
    "ts_shallows_wader":
        "The water's only waist deep all the way out to the last rock, so you can walk to most "
        "of the wrecks.\n\nA lot of them still have cargo on board. I'd go out myself, but the "
        "crabs took my boots.",
    # ---- The Ashen Reach
    "ar_gate_factor":
        "Every cart of ore that goes through this gate gets weighed, and I'm the one who weighs "
        "it.\n\nCinderwharf is through the arch. I keep a few supplies for people heading out "
        "to the Works, because it's a long walk.",
    "ar_works_foreman":
        "This is the Ashclaim Works. The smelter behind me is the only thing on the island "
        "making money right now.\n\nI've got sixty people working here. The ground shakes twice "
        "a day and the Cinder Flats are full of fire elementals, so keeping all sixty of them "
        "alive takes most of my time.",
    "ar_works_enginewright":
        "I keep the pump engine and the winding gear at the mine head running.\n\nThe air off "
        "the vents eats brass in a month and iron in a season, so I spend most of my time "
        "rebuilding things I've already built.",
    "ar_works_assayer":
        "I weigh and test every load of ore that comes out of the mine.\n\nThe dwarves get paid "
        "by what I weigh, so a lot of them think I'm cheating them. I'm not, and I'm the reason "
        "the goblins aren't either.",
    "ar_works_powderman":
        "I set the blasting charges at the mine head. Please don't smoke near the red shed.\n\n"
        "Blasting inside a volcano takes a lot of care. The last blaster here lost both his "
        "hands.",
    "ar_works_volcanologist":
        "I watch the volcano for the Ashclaim and tell them when it's dangerous.\n\nI worked at "
        "the observatory in Kagoshima for twenty years, watching Sakurajima. Three years ago I "
        "walked out of the building and the bay was gone. This mountain doesn't behave like "
        "any volcano I've studied.",
    "ar_door_warden":
        "That opening goes down into the Emberdeep. I'm here to tell people what's down there "
        "before they go in.\n\nThere's a lake of molten rock with islands of cooled stone in it, "
        "and everything living down there came out of the lake. The Thane's people sealed this "
        "door a long time ago. It broke open three years ago.",
    "ar_coast_surveyor":
        "I'm charting this coast for a harbour, and I've lost two boats doing it.\n\nThe wrecks "
        "along this shore are older than the Ashclaim. Somebody was sailing here long before "
        "the goblins came, and the naga have moved into what's left of their ships.",
    "ar_flats_scout":
        "Stay on the dark ground out here. The pale crust is thin and there's steam under "
        "it.\n\nI walk the Cinder Flats for the Foreman and mark where the vents have moved, so "
        "the ore carts know which way is safe. They move most weeks.",
    # ---- Cinderwharf
    "cw_thane_ashhold":
        "I'm Durgan Ashhold, Thane of Khaz Varun.\n\nMy great-grandfather's hall is under the "
        "south shore, and it's full of what's left of my family. The Underwriter pays for the "
        "work. I want the hall cleared and my people laid to rest.",
    "cw_quartermaster":
        "The front shelf is for anyone with coin. What's behind me is for people the Ashclaim "
        "trusts.\n\nYou earn that trust by working for the Thane or the Underwriter. I don't "
        "mind which.",
    "cw_blacksmith":
        "I work plate and mail, made from ore that came up through the old city's gate.\n\nThe "
        "forge behind me is yours to use if you know the trade. If you want leather, try the "
        "goblins down by the water.",
    "cw_armoursmith":
        "Everything I make is forged from Khaz Varun's own iron.\n\nMy grandmother was an "
        "armoursmith in the old city. Her work is still down there somewhere, and I'd like to "
        "see a piece of it one day.",
    "cw_innkeeper":
        "Welcome to the Tapped Vein. The dwarves sit on the left and my lot sit on the "
        "right.\n\nThe middle table is where the contracts get signed. Beds are upstairs, and "
        "the stew is whatever came in on the last boat.",
    "cw_general_goods":
        "I sell blasting charges, glue, resin and parchment.\n\nI'd rather you didn't ask where "
        "my powder comes from. The Thane's people don't like it, so I keep the hatch shut when "
        "they walk past.",
    "cw_alchemist":
        "I sell potions, vials and a few recipes, including one for a fire ward that you'll want "
        "in the Emberdeep.\n\nThe yellow "
        "crust round the fissures is worth more than the ore. I'd be grateful if you didn't "
        "tell the dwarves that.",
    "cw_salvage_broker":
        "If you've brought anything up out of the old city, I'll buy it, and I pay well.\n\nDark "
        "Iron work sells for a lot on the mainland. The Thane calls it grave robbing.\n\nI "
        "also sell leather and cloth supplies, and a couple of patterns for the rugged hides "
        "out of the Reach, because nobody else in town bothers.",
    "cw_shrine_keeper":
        "I keep a flame on this terrace for everyone who's still down in the city.\n\nMy cousin "
        "Durgan is the Thane. He looks after the claim and I look after the dead.",
    "cw_underwriter":
        "I hold the paper on the Ashclaim, which means my partners paid for all of this.\n\nThe "
        "Thane wants his ancestors laid to rest and I want a working foundry. Both need the "
        "same doors opened, so we work well enough together.",
    "cw_flight_master":
        "The pad is out over the water so the wind from the wings doesn't damage the roofs.\n\n"
        "I can fly you to Saltspur whenever you like, and you can get anywhere from there.",
    "cw_harbourmaster":
        "I run the berths. Every boat that ties up here pays a fee.\n\nI've lost four barges "
        "between here and the landing this season, and the Underwriter wants to know why. So "
        "do I.",
    "cw_archivist":
        "I keep the rolls of Khaz Varun, the records of every birth, oath and debt from before "
        "the city went dark.\n\nThe Thane's claim depends on these rolls, so I keep the key on "
        "a cord round my neck.",
    "cw_claims_clerk":
        "I assess losses for the Underwriter. When a barge sinks, I work out whether it was bad "
        "luck or bad seamanship.\n\nI did the same job for a marine insurer in Singapore. Three "
        "years ago I was inspecting a container ship when the harbour changed around it. The "
        "goblins understand insurance better than anyone I worked with there.",
}

#: WHAT EACH SHOP SELLS, second draft (14 Nov 2026). Kyle, the same evening: "Shop vendors are
#: boring and sell the SAME stuff." The first draft gave every shop on the island the same four
#: potions. Now each sells its own trade, and what fits the island: fire-ward and Black Lotus
#: recipes at the alchemist (the Lotus grows in the Ashen Reach), dark iron and truesilver plans at
#: the smiths, rugged leather patterns at the broker (the Reach's beasts give rugged leather), and
#: charges at the goblin who won't say where his powder comes from.
STOCK = {
    "ts_landing_quartermaster": (["runeforged_strongbox", "duskwoven_carryall", "whetstone",
                                  "coal", "flux_strong", "parchment", "component_string",
                                  "drink_waterskin", "meal_trailbread",
                                  "healing_potion_masterwork"], True),
    "ts_landing_cook": (["meal_ember_glazed_ribs", "meal_saltback_roast", "spiced_stew",
                         "hunters_brace_platter", "drink_deepwell_cordial", "drink_honeyed_mead",
                         "drink_barley_beer", "cook_flour", "cook_spice", "salt", "cook_water",
                         "cook_ale"], False),
    "ar_gate_factor": (["drink_waterskin", "meal_trailbread", "healing_potion_masterwork",
                        "mana_potion_masterwork", "coal", "salt"], False),
    "cw_quartermaster": (["runeforged_strongbox", "duskwoven_carryall", "warden_reliquary",
                          "deepdelve_bearer", "whetstone"], True),
    "cw_blacksmith": (["whetstone", "flux_strong", "coal", "bs300_deepearth_axe_1h",
                       "bs300_deepearth_head", "bs300_bloodiron_feet", "bs300_bloodiron_legs",
                       "bs_mithril_breastplate", "bs_mithril_shield"], True),
    "cw_armoursmith": (["whetstone", "flux_strong", "coal", "bs300_truesilver_wrist",
                        "bs300_kit_deepearth", "bs_runeplate_cuirass", "bs_runescale_leggings"],
                       True),
    "cw_innkeeper": (["meal_ember_glazed_ribs", "drink_starfall_wine", "meal_spiced_haunch",
                      "roasted_meat", "bread_and_cheese", "spiced_stew", "drink_barley_beer",
                      "drink_honeyed_mead", "cook_flour", "cook_spice", "cook_mushroom",
                      "cook_ale", "cook_water"], False),
    "cw_general_goods": (["bomb_sapper", "bomb_ember_cluster", "bomb_emberglass",
                          "device_repair_bot", "parchment", "glue", "resin", "component_string",
                          "vial_empty"], False),
    "cw_alchemist": (["healing_potion_masterwork", "mana_potion_masterwork",
                      "battle_elixir_superior", "guardian_elixir_superior", "vial_leaded",
                      "vial_crystal", "alch_elixir_of_greater_fire_ward", "alch_flask_black_lotus",
                      "alch_transmute_arcanite"], False),
    "cw_salvage_broker": (["tanning_reagent", "curing_salt", "sinew", "thread_silken",
                           "dye_bright", "bleach", "lw_rugged_leather_boots",
                           "lw_rugged_leather_gloves"], False),
}
REP_STOCK = {"cw_quartermaster": {
    "friendly": ["elixir_of_greater_endurance", "elixir_of_ironskin"],
    "honored": ["alch_potion_invulnerability_vendor"],
}}
