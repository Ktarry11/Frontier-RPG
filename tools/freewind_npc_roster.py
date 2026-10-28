"""
The people of Freewind Post (35). The tauren capital-in-exile.

Data only - tools/sync_freewind_npcs.py writes these into data/npcs/*.json and takes every coordinate
from handbuilt_freewind_post.NPC_POSITIONS, so the layout stays the only place a position is decided.
The six trainers come from the shared pipeline instead (Freewind is in build_class_trainers.TOWNS), as
they do in every other town.

A CAPITAL'S ROSTER, NOT A CAMP'S. Kyle: "This is supposed to be the defacto Tauren town. Should be like
a capital city." A camp has an elder, a cook and a few hunters. A capital has a market with named
traders in it, a craft row, a bank, an auction, a stable, a caravan master and somebody whose entire job
is counting what comes up the ramp. The difference between Camp Taurajo's roster and this one is the
difference between people sheltering somewhere and people running a place.

THEY ARE NOT REFUGEES ANY MORE AND THEY ARE NOT HOME EITHER.

Camp Taurajo is where the tauren went when Thunder Bluff fell - guests in somebody else's town. This is
what they BUILT, on ground nobody wanted, out of timber from a mountain that is not from this world.
There is pride in that and none of them quite trust it, because the last thing they built was Thunder
Bluff and it went into the ground with everyone in it.

ON THE CHIEFTAIN'S SEAT. Elder Longtread is Thunder Bluff's acting leader and he is still at Camp
Taurajo - see claude/factions_roster.md, where he has refused the title every time it has been offered,
because accepting it would settle a question that is not settled. He has refused to move here for the
same reason, and High Elder Namka runs the city in his absence and is extremely tired of explaining it.
That keeps the faction's leader where the data says he is while letting the capital have someone in
charge of it.

VOICE: tauren, patient, dry. They measure in winters. Nobody says "capital" without a pause before it.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

FREEWIND_AMBIENT = {
    # ================= THE LANDING - the caravan quarter =================
    "fw_gate_warden": (
        "Warden Hesk Stonefoot", "tauren", "male", 3,
        "Everything that reaches this city comes up that ramp and across this rock. Including you, so "
        "you will forgive me for looking."),
    "fw_bridge_keeper": (
        "Bridge-Keeper Oda", "tauren", "female", 7,
        "I check every rope on all three spans before anyone crosses. It takes two hours. Nobody asked "
        "me to start and nobody is going to get me to stop."),
    "fw_caravan_master": (
        "Caravan-Master Bohl", "tauren", "male", 14,
        "Four caravans a week up that ramp and not one of them on time. The road is fine. It is the "
        "ramp. It is always the ramp."),
    "fw_stablemaster": (
        "Stablemaster Reth", "tauren", "female", 16,
        "Kodo do not cross rope bridges. They learned that before we did, and one of them was right the "
        "first time."),
    "fw_kodo_wrangler": (
        "Wrangler Umak", "tauren", "male", 18,
        "They pen up here because up here is where the ramp ends. Anything with four legs lives on this "
        "top its whole life and never sees the rest of the city."),
    "fw_ramp_guard": (
        "Sentry Palla", "tauren", "female", 19,
        "One road in. That is the whole defence and it is a better one than Thunder Bluff had."),

    # ================= THE LONG MESA - the city =================
    "fw_high_elder": (
        "High Elder Namka Windhollow", "tauren", "female", 2,
        "Longtread will not come. He has refused the seat and he has refused this city, and he is right "
        "to, and I have stopped arguing about it.\n\nSo it is me. We built this. That is the part I "
        "cannot get used to - we built something again."),
    "fw_innkeeper": (
        "Innkeeper Tamu", "tauren", "male", 9,
        "First night up here nobody sleeps. The wind comes under the floor and you lie there doing "
        "arithmetic about rope. Second night you sleep fine. I have stopped asking why."),
    "fw_flight_master": (
        "Wind-Rider Kalo", "tauren", "male", 6,
        "Only road in is the ramp, and the ramp is slow. Everything in a hurry comes to me."),
    "fw_banker": (
        "Keeper of Coin Shaza", "tauren", "female", 20,
        "A vault on a mesa with one road up it. I did not design the city and I could not have designed "
        "it better."),
    "fw_auctioneer": (
        "Auctioneer Mott", "tauren", "male", 21,
        "Everything sold here was carried up a ramp, so everything here is priced like it was carried up "
        "a ramp. People complain. People also pay."),
    "fw_healer": (
        "Healer Ilna Softstep", "tauren", "female", 22,
        "Falls, mostly. Not off the edge - nobody falls off the edge, people are careful about the edge. "
        "Off ladders. Always off ladders."),
    "fw_rememberer": (
        "The Rememberer", "tauren", "male", 23,
        "I hold the names. Everyone who was in the city when the ground took it, in order, and I say "
        "them through once a season. It takes most of a night. I am not going to stop doing that either."),
    "fw_tanner": (
        "Tanner Yula", "tauren", "female", 8,
        "Hide, leather and cloth, same bench. Bring me something that was recently an animal and we will "
        "get along."),
    "fw_timberwright": (
        "Timberwright Gohn", "tauren", "male", 10,
        "Every plank in this city came off a mountain that was not here three years ago. I have stopped "
        "finding that strange, which I am told is the strange part."),
    "fw_bowyer": (
        "Bowyer Tesh", "tauren", "female", 24,
        "Aspen takes a bend and holds it. Nothing on the plain did that. I am building better bows than "
        "my mother did and I would rather she were here to be annoyed about it."),
    "fw_carver": (
        "Carver Oyat", "tauren", "male", 25,
        "Pale wood. Wrong wood. It carves like a dream and I have never once got used to the colour."),
    "fw_potter": (
        "Potter Hesha", "tauren", "female", 26,
        "Clay comes up the ramp in sacks. Everything comes up the ramp. If you ever want to understand "
        "this city, stand at the bottom of the ramp for a day."),

    # ================= WINDWARD - the high seat =================
    "fw_skywatcher": (
        "Skywatcher Rell", "tauren", "male", 5,
        "From here on a clear day you can see the aspen - a dark line along the north where the mountain "
        "starts. Three years ago that was sky."),
    "fw_totem_keeper": (
        "Totem-Keeper Ashti", "tauren", "female", 11,
        "The great totems are aspen. Pale wood, wrong wood, carried down out of a range that is not from "
        "here. The spirits have not objected. I asked for a long time before I stopped."),
    "fw_spirit_walker": (
        "Spirit-Walker Enu", "tauren", "male", 27,
        "The dead of Thunder Bluff are not restless. I have looked. Whatever took the city did not take "
        "them with it, and that is the only comfort I have been able to find in three years of looking."),
    "fw_council_1": (
        "Elder Grasswind", "tauren", "female", 28,
        "We meet on this top because it is the only ground up here with room for all of us. That is the "
        "whole reason. People read a great deal more into it."),
    "fw_council_2": (
        "Elder Tarn Blackhoof", "tauren", "male", 29,
        "Half the council wants to go back to Mulgore and half knows what is in Mulgore now. I sit "
        "between them and say very little, and that is considered wisdom."),
    "fw_lookout": (
        "Lookout Sima", "tauren", "female", 30,
        "Highest standing ground in Thousand Needles. I can see weather three days out. I cannot see "
        "home, and I have tried."),
}

FREEWIND_VENDORS = {
    # --- the Landing
    "fw_warehouse_keeper": (
        "Warehouse-Keeper Dral", "tauren", "male", 15,
        ["bread_and_cheese", "roasted_meat", "whetstone", "flux_medium", "thread_coarse"], False,
        "If it came up the ramp this season, I know where it is. If it did not, stop asking me about it."),
    "fw_tally_clerk": (
        "Tally-Clerk Nessa", "tauren", "female", 17,
        ["parchment", "vial_empty", "thread_fine"], False,
        "Everything that crosses this top gets written down. It is not suspicion. It is that we lost a "
        "city once without a list of what was in it."),
    # --- the Long Mesa: market row
    "fw_quartermaster": (
        "Quartermaster Bren Hollowhorn", "tauren", "female", 4,
        ["healing_potion_superior", "mana_potion_superior", "bread_and_cheese", "roasted_meat",
         "whetstone", "flux_medium"], True,
        "Everything on these shelves came up a ramp on somebody's back. The price reflects the back."),
    "fw_cook": (
        "Cook Dorn Steadyhand", "tauren", "male", 12,
        ["bread_and_cheese", "roasted_meat", "healing_potion_standard"], False,
        "Up here the fire wants watching. Wind takes the heat sideways and your supper with it."),
    "fw_market_herbs": (
        "Herb-Seller Winn", "tauren", "female", 31,
        ["healing_potion_standard", "mana_potion_standard", "vial_empty"], False,
        "Mesa herbs, aspen herbs and whatever the caravans bring. Three climates on one table, which is "
        "not something any herbalist before me had to price."),
    "fw_market_hides": (
        "Hide-Trader Molk", "tauren", "male", 32,
        ["thread_coarse", "thread_fine", "whetstone"], True,
        "Mountain hides from the north, mesa hides from below. The northern ones are thicker and nobody "
        "has worked out what to do with that yet."),
    "fw_market_spices": (
        "Spice-Trader Ovi", "tauren", "female", 33,
        ["bread_and_cheese", "roasted_meat"], False,
        "Salt from the flats, east of here. It is the one trade the Integration did not touch, and I "
        "have never been so glad to be boring."),
    "fw_market_relics": (
        "Relic-Keeper Dun", "tauren", "male", 34,
        ["parchment", "vial_empty"], False,
        "Things that came up out of the mesas and things that came down off the mountain. I can tell you "
        "which is which. I cannot always tell you what either one is."),
    "fw_smith": (
        "Smith Durga Ironhoof", "tauren", "female", 13,
        ["whetstone", "flux_medium", "thread_coarse", "vial_empty"], True,
        "Ore comes up the ramp in sacks and the charcoal comes up behind it. I forge the most expensive "
        "horseshoes on the continent and everybody here needs them."),
    "fw_weaponsmith": (
        "Weaponsmith Karr", "tauren", "male", 35,
        ["whetstone", "flux_medium"], True,
        "Three years ago I made tools. I would like to go back to making tools and I am not going to."),
    "fw_reagents": (
        "Reagent-Keeper Ulla", "tauren", "female", 36,
        ["mana_potion_standard", "vial_empty", "parchment"], False,
        "Spirit-work needs its materials and the spirits up here are not the ones we knew. Different "
        "herbs. Different smoke. Same asking."),
}
