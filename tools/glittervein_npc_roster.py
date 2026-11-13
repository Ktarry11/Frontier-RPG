"""
The people of Lastwater (46-49). The outpost at the bottom of the Glittervein cenote.

Data only - tools/sync_glittervein_npcs.py writes these into data/npcs/*.json and takes every
coordinate from handbuilt_glittervein.NPC_POSITIONS.

Kyle: "I'd like an outpost with quest givers outside of the cenote dungeon too."

TEN PEOPLE ON AN ISLAND IN A LAKE AT THE BOTTOM OF A HOLE, AND ONE ARGUMENT BETWEEN THEM.

Steamwheedle funded a dig here because the crystal in these walls does not care about magic, and
there is no other seam like it this side of the world. The dig went down, hit the water table, and
stopped being a dig. What is left is a camp on the spit of rock in the middle of the pool, pressed
up against a doorway nobody wants to be the one to close.

  THE COMPANY want it reopened. Every day the workings stay flooded is a day the only magic-proof
  crystal in Kalimdor stays in the ground while somebody else looks for their own. They are not
  stupid and they are not villains - they have simply never once in their lives been the people who
  decide that a thing is not worth it.
  THE SURVEY want it understood first. Not closed. UNDERSTOOD. The water in this pool did not
  gather here, it was PULLED here, across five zones and three years, and until somebody can say
  what is doing the pulling, reopening the hole it came out of is a decision made by people who
  cannot read the figures.

NOBODY HERE IS WRONG AND NOBODY HERE IS WINNING. The company cannot restart without the survey's
numbers and the survey cannot get its numbers without the company's pumps, so the two of them have
been deadlocked for eleven months on a rock they cannot leave quickly.

THIS IS THE END OF THE WATER CHAIN AND THE PLAYER SHOULD FEEL IT. Someone who has crossed the Aspen
melt, the dry Needles, the salt pan, a walled city that died of thirst and a desert whose floor fell
in arrives at the bottom of this hole and meets a tauren who has walked the same five places in the
same order for a different reason, and got here first. She is the zone's single best moment and
everything she says should earn it.

VOICE: goblin, so fast and mercantile - but down here it is goblins who have been underground for
a year and talk more quietly than goblins should. Ulla Stormhollow is the exception in every way:
slow, exact, and the only person in the camp who is not arguing.

AN INN AND A FLIGHT POINT (13 Nov 2026). This used to say Lastwater got neither - a cook with
bedrolls and no bird. Kyle, finishing the zone: "It'll need an inn and a flight path." So Brodd's
cook tent is a building now and he keeps it, and Tazzi flies from a platform on the east side.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

GLITTERVEIN_VENDORS = {
    "gv_innkeeper": (
        "Cook Brodd Kettlewick", "goblin", "male", 16,
        ["bread_and_cheese", "roasted_meat", "meal_spiced_haunch", "meal_river_fish",
         "drink_barley_beer", "drink_waterskin", "healing_potion_superior"], False,
        "Welcome to the Kettle. It was my cook tent until the dig stopped. Then people kept "
        "sleeping in it, so the crew put up walls and now it's an inn.\n\nThere's stew on and "
        "there are real beds upstairs. If you want to bind your hearth here, say so. It saves "
        "you the walk down the ramp next time."),
    "gv_quartermaster": (
        "Quartermaster Dez Hobbin", "goblin", "female", 19,
        ["healing_potion_superior", "mana_potion_superior", "meal_trailbread", "drink_waterskin",
         "whetstone", "flux_strong", "component_string", "glue", "parchment", "coal"], True,
        "Everything the dig still owns, and the dig has not dug anything in eleven months.\n\nThis "
        "camp was provisioned for ninety people. There are ten of us. So I am generous with the "
        "rope and I am generous with the lamp oil and I will remain generous right up until "
        "somebody from the Survey asks me for a favour."),
    "gv_crystal_cutter": (
        "Cutter Vessa Quill", "goblin", "female", 21,
        ["vial_leaded", "vial_empty", "thread_fine", "whetstone", "resin"], True,
        "Vein glass. Cut, backed, and set into whatever you are already wearing.\n\nThere is one "
        "seam in the world that shrugs off a spell and you are standing in the hole it came out "
        "of. I have about four months of cut stock left. After that I am a very skilled woman "
        "sitting on a rock, so you will understand why I have a view about reopening the works."),
    "gv_reagents": (
        "Brewer Nix Pallow", "goblin", "male", 8,
        ["healing_potion_superior", "mana_potion_superior", "battle_elixir_superior",
         "guardian_elixir_superior", "elixir_of_greater_endurance", "vial_leaded"], False,
        "Brewed with the only clean water for a hundred miles, which is the single best thing "
        "about this posting.\n\nEverybody up top pays four silver a skin for water hauled from "
        "here. I stand in it. Do you know what that does to a man's sense of what things are "
        "worth? I have stopped being able to price anything."),
    "gv_smith": (
        "Smith Harla Benttooth", "goblin", "female", 10,
        ["whetstone", "flux_strong", "coal", "glue", "thread_fine", "resin"], True,
        "Bring it to me before it breaks, not after. Down here after is a long walk.\n\nI repaired "
        "pump housings for two years and I have repaired weapons for one, and I will tell you "
        "which of those I would rather be doing. A pump that fails floods a gallery. A sword that "
        "fails kills the person holding it, and lately the person holding it is somebody I know."),
}

GLITTERVEIN_AMBIENT = {
    # Kyle, 13 Nov 2026: "It'll need an inn and a flight path." Every town has both.
    "gv_flight_master": (
        "Wind-Rider Tazzi Updraft", "goblin", "female", 9,
        "Need a lift out? It's a long climb otherwise.\n\nI fly from the platform. The birds "
        "like it down here, there's water and it's out of the wind. Getting them to leave again "
        "is the hard part. I can take you to Steamwheedle Port or anywhere beyond it you've "
        "already been."),

    # ================= THE COMPANY =================
    "gv_dig_boss": (
        "Dig-Boss Marn Cobble", "goblin", "male", 4,
        "Eleven months. Eleven months of paying ninety people's wages out of a hole producing "
        "nothing, and do you know what the ledger in Steamwheedle calls that? It calls it MY "
        "FAULT.\n\nIt was not my fault. We were four hundred feet down a clean seam when the water "
        "came up to meet us, and water does not come UP. Not here. Not in a desert.\n\nAnd before "
        "you say it - yes, I have heard the theory that it started when the worlds got stitched "
        "together. Everyone's problem started when the worlds got stitched together. Mine came "
        "with a figure attached."),
    "gv_pump_chief": (
        "Pump-Chief Grizzik Thane", "goblin", "male", 22,
        "Six pumps. Four of them are mine and two of them are the Survey's, and the two that are "
        "the Survey's are the two that work, which I would like entered into a record "
        "somewhere.\n\nI can clear the first gallery in nine days. I have been able to clear the "
        "first gallery in nine days for eleven months. All I need is for two people who both think "
        "they are the adult here to say the same sentence out loud on the same afternoon."),
    "gv_tally_clerk": (
        "Tally-Clerk Oss Pinch", "goblin", "female", 13,
        "Nine hundred and forty-one days of water level, taken at dawn, written down whether "
        "anybody wanted it or not.\n\nThe Boss says my book proves the flood is seasonal. Ulla "
        "says my book proves the flood is not. It is the SAME BOOK. I have started to suspect that "
        "a number is only ever worth what the person reading it already believed, which is a "
        "terrible thing for a clerk to work out about herself."),

    # ================= THE SURVEY =================
    "gv_surveyor": (
        "Ulla Stormhollow", "tauren", "female", 3,
        "I started at the Aspen melt four years ago because the thaw was coming early and nobody "
        "could tell me why.\n\nThen the Needles went dry. Then the pan went to salt. Then a walled "
        "city out east died of thirst with a well in the middle of it, and then the floor of the "
        "desert fell in, and at every single one of those places somebody told me it was a local "
        "problem with a local cause.\n\nIt is one problem. You are standing in it. Every drop of "
        "water that left those five places is in this pool, and water does not CHOOSE to go "
        "somewhere. It goes where it is pulled.\n\nSo. Something down that shaft has been drinking "
        "a region for three years, and the goblins want to open the door and ask it for the "
        "crystal."),
    "gv_diver": (
        "Diver Sanna Creel", "goblin", "female", 24,
        "Forty feet in on a lungful, tie off, forty feet back. I have been into the first gallery "
        "nine times and I have come out nine times, which I am aware is not the same as being "
        "good at it.\n\nIt is not dark in there. That is the part nobody writes down. There is "
        "light coming off the seam and it is not the colour that crystal goes when you put a lamp "
        "on it. It is the colour crystal goes when something is USING it."),
}
