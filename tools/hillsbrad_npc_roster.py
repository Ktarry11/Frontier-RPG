"""
The people of Hillsbrad: Western Hillsbrad (16), Eastern Hillsbrad (16) and Tarren Mill (18).

Data only - tools/sync_hillsbrad_npcs.py writes these into data/npcs/*.json and takes every coordinate from the
zone modules' NPC_POSITIONS, so the layout stays the only place a position is decided.

WHO IS ALIVE AND WHO IS NOT IS THE GEOGRAPHY.  Hillsbrad is contested ground, not Forsaken heartland, and the
roster says so without a word of exposition:

  WEST  the farms are still worked by living people. The Forsaken hold one tower, Southpoint, and watch the rest
        from the treeline. Humans outnumber the dead on this side.
  EAST  the Forsaken hold it outright from Tarren Mill, and the living here are either working for them or hiding
        from them.
  TOWN  the race splits it: every west-bank NPC is human, every east-bank one is Forsaken (see the town module).

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

# =====================================================================================================
# WESTERN HILLSBRAD - the player's first step into green country, and still mostly alive
# =====================================================================================================
WEST_VENDORS = {
    "hbw_southpoint_quartermaster": (
        "Quartermaster Dreng", "forsaken", "male", 3,
        ["healing_potion_standard", "mana_potion_standard", "bread_and_cheese", "roasted_meat",
         "guardian_elixir_standard", "whetstone", "vial_empty"], True,
        "Tower stores. Signed for, counted twice, and I will know if it is not."),
    "hbw_fields_quartermaster": (
        "Quartermaster Ivek", "forsaken", "male", 12,
        ["healing_potion_minor", "mana_potion_minor", "bread_and_cheese", "thread_coarse",
         "flux_weak", "parchment"], False,
        "A forward post gets forward-post stock. Do not ask for anything polished."),
}

WEST_AMBIENT = {
    "hbw_southpoint_commander": (
        "Commander Hale Rethven", "forsaken", "female", 7,
        "One tower, and every farm in the valley watching it. We hold what we can see from the top."),
    "hbw_southpoint_apothecary": (
        "Apothecary Jessel Vane", "forsaken", "male", 9,
        "Green country. Do you know how long it has been since I had anything LIVING to work with?"),
    "hbw_southpoint_deathguard": (
        "Deathguard Orlin", "forsaken", "male", 15,
        "Militia come up the road twice a week to look at us. We look back. Nobody has swung yet."),
    "hbw_pass_scout": (
        "Scout Aelin Frost", "forsaken", "female", 5,
        "You came down out of Silverpine. Take a breath - the air here does not have the blight in it."),
    "hbw_road_outrider": (
        "Outrider Kess", "forsaken", "female", 18,
        "East road runs to Tarren Mill. Stay on it. What is off it is not friendly and not slow."),
    "hbw_fields_agent": (
        "Agent Sarra Dunwick", "forsaken", "female", 11,
        "The farmhands out here still think this is their valley. I am not in a hurry to correct them."),
    "hbw_fields_poacher": (
        "Poacher Tam Hollis", "human", "male", 2,
        "I take a ram now and then. The Marshal calls it theft. The rams have no opinion."),
    "hbw_fields_scout": (
        "Scout Bren Ashby", "forsaken", "male", 20,
        "Count the militia, count the marines, report, repeat. Riveting work."),
    "hbw_pasture_herder": (
        "Herder Maud Kellen", "human", "female", 6,
        "Yetis come down off the snowline when it turns cold. My rams know it before I do."),
    "hbw_mine_overseer": (
        "Overseer Grint Halloway", "forsaken", "male", 14,
        "Azurelode was the richest silver seam in the valley. Now it is the wettest."),
    "hbw_mine_surveyor": (
        "Surveyor Pell Iversen", "human", "male", 17,
        "I mapped those workings before they flooded. The map is worth more than the mine now."),
    "hbw_strand_tidewatcher": (
        "Tidewatcher Nols", "forsaken", "male", 4,
        "Murlocs on the strand, and something further out that the murlocs are frightened of."),
    "hbw_southshore_spy": (
        "Spy Lia Marrow", "forsaken", "female", 13,
        "Southshore is awake, armed, and three hundred strong. Walk in and you will not walk out."),
    "hbw_orchard_forager": (
        "Forager Ned Quill", "human", "male", 22,
        "Apples the size of your fist, and wasps the size of your hand guarding every one of them."),
    "hbw_purgation_castaway": (
        "Castaway Ilsa Roane", "human", "female", 23,
        "My ship went down off that shore. Everyone else who came up out of the water came up wrong."),
    "hbw_southshore_saboteur": (
        "Saboteur Henk", "orc", "male", 8,
        "Dey build a dock, I burn a dock. Simple arrangement. Works fine."),
}

# =====================================================================================================
# EASTERN HILLSBRAD - held outright, and the living here either work for the dead or hide from them
# =====================================================================================================
EAST_VENDORS = {
    "hbe_mill_quartermaster": (
        "Quartermaster Sule", "forsaken", "female", 10,
        ["healing_potion_standard", "mana_potion_standard", "roasted_meat", "spiced_stew",
         "battle_elixir_standard", "whetstone", "flux_medium"], True,
        "Gate stores. The town has its own shops across the bridges; this is for people who are leaving."),
}

EAST_AMBIENT = {
    "hbe_mill_magistrate": (
        "Magistrate Orrin Pell", "forsaken", "male", 1,
        "Everything east of the mill is my problem: gnolls, Syndicate, ogres, and a wall nobody can open."),
    "hbe_mill_apothecary": (
        "Field Apothecary Wren", "forsaken", "female", 16,
        "I sample the ditches so the ones inside the town do not have to. It is a career."),
    "hbe_mill_deathguard": (
        "Deathguard Kolt", "forsaken", "male", 19,
        "Gate's behind me, road's in front of you. Mind which one you are facing when you draw."),
    "hbe_mill_caravan_master": (
        "Caravan Master Ovid Thane", "forsaken", "male", 6,
        "Flour out, reagents in, twice a month. The Syndicate has started taking an interest in my wheels."),
    "hbe_mill_hunter": (
        "Huntsman Dell Varrow", "human", "male", 21,
        "Worgs in the hedgerows, gnolls in the hollow. I was a gamekeeper. Now I am a different sort."),
    "hbe_west_gate_scout": (
        "Scout Pria Halm", "forsaken", "female", 3,
        "West road to the Foothills, east road to everything that wants you dead. Choose carefully."),
    "hbe_hollow_trapper": (
        "Trapper Gus Mirren", "human", "male", 12,
        "Mudsnout gnolls took my whole line of snares and left me the stakes. Insulting, that."),
    "hbe_west_outrider": (
        "Outrider Jace", "forsaken", "male", 8,
        "I ride the west road all day and most of the night. It has never once been quiet."),
    "hbe_naze_infiltrator": (
        "Infiltrator Vess", "forsaken", "female", 14,
        "Gavin's Naze is a fence's camp with delusions. Everything stolen in this valley passes through it."),
    "hbe_durnholde_watcher": (
        "Watcher Odrin Falk", "forsaken", "male", 5,
        "The keep has been held by the Syndicate longer than it was ever held by Lordaeron. Think on that."),
    "hbe_durnholde_scholar": (
        "Scholar Emeline Vask", "forsaken", "female", 17,
        "Thrall was kept in that keep as a boy. Half the Horde's history started behind those walls."),
    "hbe_stead_outrider": (
        "Outrider Brann Odgar", "orc", "male", 11,
        "Nethander ogres took da stead. Dey took da barn too, and dey are living in it."),
    "hbe_garok_sapper": (
        "Sapper Niall Crag", "forsaken", "male", 20,
        "Dwarves cut that fort square into the ridge. I have been told to find a way in that is not the door."),
    "hbe_strand_tidewatcher": (
        "Tidewatcher Ferris", "forsaken", "male", 9,
        "Daggerspine murlocs on this strand too. They are spreading, and nobody will say from where."),
    "hbe_wall_sentry": (
        "Sentry Ada Rook", "forsaken", "female", 2,
        "Thoradin's Wall. Built by an empire that is dust, and it still closes the road."),
}


# =====================================================================================================
# TARREN MILL - the race splits the roster: west bank human, east bank Forsaken, guards on the seam
# =====================================================================================================
TOWN_VENDORS = {
    "tarren_mill_innkeeper": (
        "Innkeeper Mallory Dunn", "human", "female", 4,
        ["healing_potion_standard", "mana_potion_standard", "bread_and_cheese", "roasted_meat",
         "spiced_stew", "spiced_wine", "guardian_elixir_standard"], False,
        "Room's yours if you want it. I'll not ask which bank you came off."),
    "tarren_mill_trader": (
        "Goodwife Serrin Holt", "human", "female", 11,
        ["healing_potion_minor", "mana_potion_minor", "bread_and_cheese", "parchment", "glue",
         "salt", "thread_coarse", "vial_empty"], False,
        "Flour, thread, lamp oil. Whatever the mill does not eat, I sell."),
    "tarren_mill_smith": (
        "Smith Odrin Vance", "human", "male", 7,
        ["whetstone", "flux_medium", "flux_strong", "coal", "resin"], True,
        "I shoe their horses and mend their cart axles. A trade is a trade."),
    "tarren_mill_bowyer": (
        "Bowyer Tess Aldren", "human", "female", 16,
        ["fletching", "sinew", "component_string", "resin", "glue"], True,
        "Yew from the river stand, strung the way my father strung them."),
    "tarren_mill_reagent_seller": (
        "Factor Vell", "forsaken", "male", 9,
        ["vial_empty", "vial_leaded", "vial_crystal", "dye_mild", "bleach", "parchment"], False,
        "The Society requisitions. I merely keep the ledger, and the ledger keeps everyone honest."),
    "tarren_mill_apothecary": (
        "Apothecary Lysbet Crane", "forsaken", "female", 14,
        ["elixir_of_toughness", "elixir_of_warding", "elixir_of_agility", "arcane_elixir",
         "healing_potion_standard", "mana_potion_standard"], False,
        "Mind the vats. What is in them is not finished, and it does not like being looked at."),
    "tarren_mill_vat_tender": (
        "Vat-Tender Grusk", "forsaken", "male", 18,
        ["battle_elixir_standard", "guardian_elixir_standard", "elixir_of_firepower",
         "mushroom_broth", "tanning_reagent"], False,
        "Stir it, skim it, log it. Twelve years dead and I have a trade again."),
}

TOWN_AMBIENT = {
    # --- the seam: the two who stand where the banks meet
    "tarren_mill_gate_guard": (
        "Gate Guard Hollis", "forsaken", "male", 8,
        "South gate. State your business, keep to the road, and do not swim the race."),
    "tarren_mill_watchman": (
        "Watchman Grell", "forsaken", "male", 20,
        "Three bridges, three of us. You would be amazed how many try the water anyway."),
    # --- west bank: the village still working
    "tarren_mill_miller": (
        "Miller Aldous Reed", "human", "male", 2,
        "The wheel has turned every day for sixty years. Who holds the town has never once stopped it."),
    "tarren_mill_stablemaster": (
        "Stablemaster Brann Teague", "human", "male", 13,
        "Horses will not cross the bridges at night. Clever animals, horses."),
    "tarren_mill_farrier": (
        "Farrier Nell Marsh", "human", "female", 6,
        "Hooves and hinges. Half this town runs on things I hammered flat."),
    "tarren_mill_chaplain": (
        "Chaplain Ewen Blackwood", "human", "male", 17,
        "I keep the chapel on this side. They have never asked me to stop. I have never asked why."),
    "tarren_mill_sluice_keeper": (
        "Sluice-Keeper Pate", "human", "male", 10,
        "Crank's mine. Drop the gate and the wheel stops, the vats go cold, and everyone remembers my name."),
    "tarren_mill_farmhand": (
        "Farmhand Dorrin", "human", "male", 19,
        "Barley in the north plots, oats in the south. Same as my mother sowed, same rows."),
    # --- east bank: the Society
    "tarren_mill_apprentice": (
        "Apprentice Nilla Stitch", "forsaken", "female", 5,
        "I label everything. If a jar has no label, do not open it, and do not tell me you opened it."),
    "tarren_mill_commander": (
        "Commander Vellis Thorne", "forsaken", "female", 12,
        "Alterac to the north, Southshore to the south, and the Syndicate in between. We hold the middle."),
    "tarren_mill_scout": (
        "Scout Mirren Vask", "forsaken", "male", 15,
        "Durnholde is thick with Syndicate and the hills are thick with gnolls. Walk the road."),
}
