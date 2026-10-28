"""
The people of Freewind Post (11).

Data only - tools/sync_freewind_npcs.py writes these into data/npcs/*.json and takes every coordinate
from handbuilt_freewind_post.NPC_POSITIONS, so the layout stays the only place a position is decided.

THEY ARE NOT REFUGEES ANY MORE AND THEY ARE NOT HOME EITHER.

Camp Taurajo is where the tauren went when Thunder Bluff fell - guests in somebody else's town, and the
roster there sounds like it. This is different. Freewind is the first place since the city went down
that they BUILT, on ground nobody else wanted, out of timber from a mountain that is not even from this
world. There is pride in that and none of them quite trust it, because the last thing they built was
Thunder Bluff.

So the voice here is steadier than Longstand Camp's and warier than it sounds. They talk about the drop
the way people talk about weather. Nobody says "capital". Several of them will tell you, unprompted, that
this is temporary.

VOICE: tauren, patient, dry. They measure in winters. The elder is the only one who will discuss Cairne
and she will not do it twice.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

FREEWIND_AMBIENT = {
    # ---- THE LANDING: the gate
    "fw_gate_warden": (
        "Warden Hesk Stonefoot", "tauren", "male", 3,
        "Everything that reaches this town comes up that ramp and across this rock. Including you, so "
        "you will forgive me for looking."),
    "fw_bridge_keeper": (
        "Bridge-Keeper Oda", "tauren", "female", 7,
        "I check every rope on all three spans, every morning, before anyone crosses. It takes two "
        "hours. I have never once been asked to do it and I am never going to stop."),

    # ---- THE LONG MESA: the town
    "fw_elder": (
        "Elder Namka Windhollow", "tauren", "female", 2,
        "We built this. That is the part I cannot get used to - not the height, not the wind. We built "
        "something again, after the last thing we built went into the ground with everyone in it."),
    "fw_innkeeper": (
        "Innkeeper Tamu", "tauren", "male", 9,
        "First night up here nobody sleeps. The wind comes under the floor and you lie there doing "
        "arithmetic about rope. Second night you sleep fine. I do not know why and I have stopped asking."),
    "fw_skywatcher": (
        "Skywatcher Rell", "tauren", "male", 5,
        "From the lookout you can see the aspen on a clear day - a dark line along the north, where the "
        "mountain starts. Three years ago that was sky."),
    "fw_totem_keeper": (
        "Totem-Keeper Ashti", "tauren", "female", 11,
        "The great totem is aspen. Pale wood, wrong wood, carried down out of a range that is not from "
        "here. The spirits have not objected. I asked for a long time before I stopped."),
    "fw_flight_master": (
        "Wind-Rider Kalo", "tauren", "male", 6,
        "Only road in is the ramp, and the ramp is slow. Everything in a hurry comes to me."),
}

FREEWIND_VENDORS = {
    "fw_quartermaster": (
        "Quartermaster Bren Hollowhorn", "tauren", "female", 4,
        ["healing_potion_superior", "mana_potion_superior", "bread_and_cheese", "roasted_meat",
         "whetstone", "flux_medium"], True,
        "Everything on these shelves came up a ramp on somebody's back. The price reflects the back."),
    "fw_cook": (
        "Cook Dorn Steadyhand", "tauren", "male", 12,
        ["bread_and_cheese", "roasted_meat", "healing_potion_standard"], False,
        "Up here the fire wants watching. Wind takes the heat sideways and your supper with it."),
    "fw_tanner": (
        "Tanner Yula", "tauren", "female", 8,
        ["thread_coarse", "thread_fine", "whetstone", "vial_empty"], True,
        "Hide, leather and cloth, same bench. Bring me something that was recently an animal and we will "
        "get along."),
    "fw_timberwright": (
        "Timberwright Gohn", "tauren", "male", 10,
        ["flux_medium", "whetstone", "thread_coarse"], True,
        "Every plank in this town came off a mountain that was not here three years ago. I have stopped "
        "finding that strange, which I am told is the strange part."),
}
