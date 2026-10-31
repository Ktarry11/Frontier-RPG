"""
The people of Steamwheedle Port (41-44). The main town of Tanaris.

Data only - tools/sync_steamwheedle_npcs.py writes these into data/npcs/*.json and takes every
coordinate from handbuilt_steamwheedle_port.NPC_POSITIONS.

EIGHTEEN PEOPLE AND ONE ARGUMENT RUNNING THROUGH ALL OF THEM.

Half this town has been here four generations and half arrived three years ago from Gadgetzan with
what it could carry. That is the only social fact the place has, and it is in every record below:

  THE QUAY are old harbour goblins. Their complaint is that the town has doubled and the harbour has
  not, and that none of the new money is theirs. They are not cruel about it. They are TIRED, and
  several of them are quietly aware that they would have done exactly the same thing.
  THE UPPER YARD are Gadgetzan. Their complaint is that they are three years in, out-earning the
  quay, and still described as having arrived. One of them has been here longer than a quay goblin
  who was born here and will tell you the arithmetic.

NOBODY IS THE VILLAIN AND THE TOWN IS NOT DYING. This is the opposite of Saltwheel in every way that
matters, and it should feel like it - Saltwheel is people staying somewhere that is finished,
Steamwheedle is people doing well and finding it does not settle anything. A player who has walked
the pan arrives here and the first thing they should notice is NOISE.

THE WIND RIDER IS THE PLAYER'S REWARD for the walk, and Kezzik knows exactly what it is worth,
because he is the only flight master within a very long way and his prices reflect the geography.

VOICE: goblin, so fast and mercantile - but the two halves are pitched differently. The quay is
slower, drier, and talks about water and weather and whose grandfather did what. The yard is louder,
newer, and talks about throughput. Doc Pellik's opposite number here is a port surgeon who mostly
treats crush injuries, because that is what a working dock does to people.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

STEAMWHEEDLE_VENDORS = {
    # ================= THE QUAY =================
    "stw_innkeeper": (
        "Innkeeper Mirabel Sump", "goblin", "female", 9,
        ["bread_and_cheese", "roasted_meat", "meal_river_fish", "meal_spiced_haunch",
         "drink_barley_beer", "drink_honeyed_mead", "healing_potion_superior"], False,
        "Beds upstairs, board down here, and the hearth is yours the moment you touch it.\n\nI have "
        "forty beds and I have had forty beds since my mother ran this house. The town has twice the "
        "people it did three years ago and I have forty beds, so do the arithmetic and take the one "
        "at the end before somebody off the yard does."),
    "stw_fishmonger": (
        "Fishmonger Oda Brack", "goblin", "female", 17,
        ["meal_river_fish", "meal_trailbread", "drink_waterskin", "salt", "curing_salt"], False,
        "Everything on this slab came out of that water this morning and everything on it will be "
        "gone by noon.\n\nI buy my salt off a woman on the pan who has never once been late in "
        "eleven years. Her town is dying and my town is not and she still gets the cart out. That "
        "is the whole trade, really. Someone keeps turning up."),
    "stw_chandler": (
        "Chandler Vex Tarrow", "goblin", "male", 3,
        ["component_string", "glue", "resin", "thread_fine", "whetstone", "healing_potion_superior",
         "mana_potion_superior"], True,
        "Rope, pitch, canvas, lamp oil, and whatever else stops a ship coming apart.\n\nMy "
        "grandfather chandlered this quay and his father before him, and I will tell you what has "
        "changed: nothing, at this counter. Everything, forty yards that way."),
    "stw_shipwright": (
        "Shipwright Hald Keelmaker", "goblin", "male", 5,
        ["glue", "resin", "coal", "whetstone", "flux_strong", "thread_fine"], True,
        "A hull does one of two things out here. It gets looked after or it gets burned to the "
        "waterline for its nails.\n\nI have had more work in three years than in the twenty before "
        "them, and every job of it has come off that yard, and I am not going to pretend that is a "
        "coincidence or that I resent it."),
    "stw_banker": (
        "Strongbox-Keeper Pell", "goblin", "female", 20,
        ["parchment", "vial_empty", "thread_fine"], False,
        "I hold what people do not want to carry and I write down what they do not want to forget.\n\n"
        "There is more in this house than there has ever been and most of it belongs to people who "
        "walked here with nothing. You can take that as a sermon or as a fact. It is a fact."),

    # ================= THE UPPER YARD =================
    "stw_general_goods": (
        "Trader Bix Rannow", "goblin", "male", 13,
        ["healing_potion_superior", "mana_potion_superior", "bread_and_cheese", "roasted_meat",
         "whetstone", "flux_strong", "thread_fine", "parchment", "meal_trailbread"], True,
        "Everything, roughly, and if I do not have it I know who does and I will take a cut of "
        "telling you.\n\nI had a shop with a stone front and a name cut into the lintel. It is "
        "standing in a walled town with nobody in it four days west. This is a shed. The shed makes "
        "more money and I would still rather have the lintel."),
    "stw_smith": (
        "Smith Dorga Ironside", "goblin", "female", 4,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine"], True,
        "Hot work, and it is hot already, so I start before the sun does and stop when it is "
        "overhead.\n\nEverything I make here goes onto a ship or into the desert, and the two of "
        "them want opposite things from a piece of steel. Salt air or dry sand. Pick one and I will "
        "temper for it."),
    "stw_engineer": (
        "Engineer Faz Quill", "goblin", "male", 2,
        ["device_repair_bot", "bomb_sapper", "eng_bomb_brine", "coal", "glue", "component_string",
         "flux_strong"], False,
        "I build things that mostly work and I am honest about the mostly, which in this trade "
        "makes me a radical.\n\nMy whole workshop came out of Gadgetzan on three carts. Everything "
        "heavier than a cart is still in it. There is a press in that town I think about more than "
        "I think about most people."),
    "stw_reagents": (
        "Brewer Tansy Vohl", "goblin", "female", 23,
        ["healing_potion_superior", "mana_potion_superior", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_leaded", "vial_empty"], False,
        "Sealed against sea air, which is a different problem from sealed against dry air and costs "
        "more.\n\nThere is a woman out on the pan who seals in lead for the same reason and charges "
        "less. She also has six customers. I have four hundred. Neither of us is doing it wrong."),
    "stw_salvage_broker": (
        "Broker Nim Catchpenny", "goblin", "female", 11,
        ["resin", "glue", "component_string", "parchment", "whetstone"], True,
        "I buy what came off something and sell it to whoever needs it on something else.\n\nHalf "
        "of what crosses this counter came out of Gadgetzan and I will not pretend otherwise. If "
        "that bothers you, it is still for sale."),
    "stw_caravan_agent": (
        "Agent Rullo Tack", "goblin", "male", 7,
        ["meal_trailbread", "drink_waterskin", "elixir_of_swiftness", "healing_potion_superior"], False,
        "Freight west, freight south, and a price for each that assumes you have looked at the "
        "alternatives.\n\nThere is a pan north of here with a town on it that has wanted a regular "
        "cart for three years. I could run one. I have not, and the reason is not the hives, it is "
        "that there is nothing coming back the other way worth the axle."),
}

STEAMWHEEDLE_AMBIENT = {
    # ================= THE QUAY =================
    "stw_harbourmaster": (
        "Harbourmaster Senna Coil", "goblin", "female", 14,
        "Four berths, and I have been turning ships away since the second winter.\n\nThey want me to "
        "cut two more out of the rock. I have told them what that costs and they have told me what "
        "the waiting costs and we are both right, which is the most annoying way for an argument to "
        "be stuck."),
    "stw_flight_master": (
        "Wind-Rider Kezzik", "goblin", "male", 6,
        "Only bird for a very long way, and I price like it.\n\nFolk come off that pan on foot with "
        "a face on them and ask why there is no post out there. There IS a post out there. There is "
        "no BIRD on it, because a bird needs feeding and a feeding needs somebody paying, and six "
        "customers do not pay for a wyvern.\n\nI would love to be wrong. Bring me the town that "
        "makes me wrong."),
    "stw_barkeep": (
        "Barkeep Oll", "goblin", "male", 18,
        "Quay side of the room is quiet and the yard side is not, and I have stopped trying to seat "
        "anybody anywhere.\n\nThey drink together. That is the thing nobody says out loud when they "
        "are telling you how divided this town is. They argue in here and then they go to work in "
        "the morning on the same dock."),

    # ================= THE UPPER YARD =================
    "stw_yard_boss": (
        "Yard-Boss Grizzel Hack", "goblin", "female", 15,
        "Everything that is not on a ship or in a shop is on my yard, and most of what IS on a ship "
        "came off it.\n\nThree years ago this was a goat field and I was somebody's third-best "
        "foreman in a town with a wall round it. Now I am this. I think about that most mornings "
        "for about as long as it takes to get my boots on."),
    "stw_old_gadgetzan": (
        "Old Mazzic", "goblin", "male", 21,
        "I did not leave Gadgetzan. Everybody says left. I was carried out on a door by two people "
        "whose names I never got.\n\nSo when the quay crowd say we ARRIVED, like it was a thing we "
        "decided on a Tuesday - no. Some of us arrived. The rest of us were brought."),

    # ================= BETWEEN THE TWO =================
    "stw_tally_clerk": (
        "Tally-Clerk Hesper Dunn", "goblin", "female", 24,
        "Every crate in, every crate out, which side of town it came from and which side it went "
        "to.\n\nPeople assume I keep the last two columns to be unpleasant. I keep them because in "
        "four years somebody is going to claim this town was always like this, and I would like to "
        "be able to put a book on the table."),
    "stw_doctor": (
        "Surgeon Wick Ambrose", "goblin", "male", 12,
        "Crush injuries, mostly. A dock does that to people - a rope goes, or a load swings, or "
        "somebody puts a hand where a hand has no business being.\n\nI have treated more of the "
        "yard crowd than the quay crowd and it is not because they are careless. It is because they "
        "are the ones doing the lifting, and if anybody tells you different send them to me."),
}
