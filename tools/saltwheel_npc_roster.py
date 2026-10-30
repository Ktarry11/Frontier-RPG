"""
The people of Saltwheel (35-40). The goblin town on the start line.

Data only - tools/sync_saltwheel_npcs.py writes these into data/npcs/*.json and takes every coordinate
from handbuilt_saltwheel.NPC_POSITIONS, so the layout stays the only place a position is decided.

A TOWN THAT IS STILL OPEN, WHICH IS NOT THE SAME AS A TOWN THAT IS DOING WELL.

The pitch for everybody in this roster is the same and it is the whole town: the racetrack does not run
any more, the salt is eating the buildings, the hives are four miles out and closing, and nobody is
leaving. Every one of them has a reason, every reason is true, and not one of them is a reason. That is
the joke and it is also not a joke - this is what people are actually like about a place they have put
money into.

SO NOBODY HERE ADMITS THE PROBLEM AND EVERYBODY HERE IS WORKING AROUND IT. The marshal still posts
times. The pit boss still keeps a crew. The watcher on the east fence counts mounds for a living and is
the only one who says the number out loud, which is exactly why he stands at the fence and not in the
inn.

NO WIND RIDER. Kyle: "This can have an inn but no wind rider." Three of them bring it up unprompted,
because a town with a bed and no bird is a town you have to walk out of, and the player is about to find
that out. It is the single most informative thing about the place and it costs nothing to say.

ONE TRADE STILL WORKS: salt. It went out before the Integration, it goes out now, and Jixa Brinecount
has never been so relieved to be boring. (Freewind Post's spice-trader buys from her - see
tools/freewind_npc_roster.py, "Salt from the flats, east of here.")

NO BANK AND NO AUCTION, because the game has neither service and a dying pan town would be the last
place to get them. What it has is a strongbox nobody mentions and a clerk who writes everything down.

VOICE: goblin. Fast, mercantile, allergic to a straight answer about money and incapable of a crooked
one about engineering. They measure in seasons and in what things used to cost. Earth came through here
too - the racers were the first to find out an Earth engine out-accelerates anything with a goblin
boiler in it, which is one of the several things that killed the sport.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

SALTWHEEL_VENDORS = {
    # ================= THE TRADE ROW - the north side, facing the straight =================
    "sw_innkeeper": (
        "Innkeeper Vozzi Rimehand", "goblin", "female", 14,
        ["bread_and_cheese", "roasted_meat", "meal_spiced_haunch", "drink_barley_beer",
         "drink_waterskin", "healing_potion_superior"], False,
        "Bed, board, and a bind. That is the full list and I will not be upsold on your behalf.\n\n"
        "Before you ask: there is no wind rider. There was never a wind rider. You came in on your feet "
        "and that is how you are leaving, so eat something."),
    "sw_general_goods": (
        "Trader Grebbit Maul", "goblin", "male", 3,
        ["healing_potion_superior", "mana_potion_superior", "bread_and_cheese", "roasted_meat",
         "whetstone", "flux_strong", "thread_fine", "parchment"], True,
        "Everything on this table came across the pan on a cart with four bad wheels. The price is the "
        "wheels. It was always the wheels."),
    "sw_reagents": (
        "Brewer Nissa Tolk", "goblin", "female", 9,
        ["healing_potion_superior", "mana_potion_superior", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_leaded", "vial_empty"], False,
        "Salt air ruins a cork in a season, so I seal everything in lead and I charge you for the lead. "
        "Yes, I have heard what they say about lead. Drink it fast."),
    "sw_salt_buyer": (
        "Jixa Brinecount", "goblin", "female", 20,
        ["salt", "curing_salt", "meal_trailbread", "drink_waterskin"], False,
        "Salt. That is it, that is the whole business, and it is the only trade on this pan that the "
        "Integration did not touch.\n\nEverybody laughed at me for twenty years. They are not laughing "
        "now, they are just gone."),
    "sw_road_agent": (
        "Road-Agent Fenk Dustle", "goblin", "male", 7,
        ["meal_trailbread", "drink_waterskin", "elixir_of_swiftness", "healing_potion_superior",
         "thread_fine"], False,
        "I sell what you need to walk out of here, which is a thriving business, because walking out of "
        "here is the only option available to you.\n\nNo bird. Do not go looking for the post. There is "
        "a post. There has never been a bird on it."),
    "sw_quartermaster": (
        "Quartermaster Dral Wexx", "goblin", "male", 5,
        ["healing_potion_superior", "mana_potion_superior", "whetstone", "flux_strong", "coal",
         "heavy_bolts", "shot_charged"], True,
        "Raceday stock. We laid in eight seasons of it the year before the track died, so you are "
        "buying from a warehouse that was built for a crowd that is not coming."),

    # ================= THE PIT ROW - the south side, which is what the town was for =================
    "sw_mechanic": (
        "Mechanic Oyla Spannerwick", "goblin", "female", 4,
        ["glue", "resin", "coal", "device_repair_bot", "component_string", "flux_strong"], False,
        "Three years ago a human drove an Earth machine down that straight and it did the whole run on "
        "a thimble of fuel and no boiler at all.\n\nI have taken one apart since. I understand it now. "
        "That is worse."),
    "sw_fuel_trader": (
        "Fuel-Trader Mozz", "goblin", "male", 23,
        ["coal", "bomb_sapper", "eng_bomb_brine", "glue", "flux_strong"], False,
        "I have fuel for two hundred racers and six customers. Do the arithmetic and then make me an "
        "offer, because I have done the arithmetic and I am desperate."),
    "sw_salvager": (
        "Salvager Pim Gattle", "goblin", "female", 13,
        ["resin", "glue", "component_string", "thread_fine", "whetstone", "parchment"], True,
        "Everything out on that track is mine the day it stops moving. That is the rule, it is written "
        "down, and it has made me the richest wreck-picker on a pan with no wrecks left."),
    "sw_repair": (
        "Armourer Hett Grindle", "goblin", "male", 6,
        ["whetstone", "flux_strong", "coal", "thread_fine", "glue"], True,
        "Salt gets into a hinge and it is finished. I can slow it. I cannot stop it, and anyone who "
        "tells you they can stop it is selling you grease."),
}

SALTWHEEL_AMBIENT = {
    # ================= THE TRADE ROW =================
    "sw_barkeep": (
        "Barkeep Snod", "goblin", "male", 17,
        "Vozzi runs the beds. I run the bar. We have not spoken in two years and the business has never "
        "been better, so do not fix it."),

    # ================= THE PIT ROW - the sport, still being administered =================
    "sw_race_marshal": (
        "Race-Marshal Tozzik Brasswheel", "goblin", "male", 2,
        "The Saltwheel Open runs the first clear day after the winter wet. Entries at the gantry, "
        "scrutineering at noon, flag at two.\n\nNobody has entered for three seasons. I post the times "
        "anyway. Somebody has to hold the date or the date goes away, and then what is this."),
    "sw_pit_boss": (
        "Pit-Boss Grizzik Vane", "goblin", "female", 11,
        "I keep four hands on the payroll for a race that has not run since the Integration. Tozzik "
        "pays half, I pay half, and neither of us has said out loud what we are paying for."),
    "sw_old_racer": (
        "Old Nazzik", "goblin", "male", 21,
        "Course record. Mine. Eleven years and nobody has touched it.\n\nThat is because nobody has "
        "driven the course in three, which I am aware of, and which does not take the record off me."),
    "sw_tally_clerk": (
        "Tally-Clerk Winnow", "goblin", "female", 18,
        "Every cart in, every cart out, every barrel of salt, written down twice. The town is shrinking "
        "and I can tell you by exactly how much, which makes me the least popular person in it."),

    # ================= THE FENCE - where the town stops pretending =================
    "sw_hive_watcher": (
        "Watcher Brak Kesh", "goblin", "male", 15,
        "Five mounds I can see from this fence. Three years ago there were two, and the near one was "
        "twice as far out as it is now.\n\nI say the number every evening in the inn. They have started "
        "buying me drinks so I will say it quieter."),
    "sw_doctor": (
        "Doc Pellik", "goblin", "male", 24,
        "Salt sores, sun, and whatever the bugs do to a hand. Three complaints, in that order, every "
        "season, and I could do the whole job in my sleep if the third one would stop climbing."),
}
