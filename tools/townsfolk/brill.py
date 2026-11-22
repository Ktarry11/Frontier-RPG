"""Brill's people: the Forsaken village on the hill, and the few living who stay (21 Nov 2026).

Kyle: "a lot of towns you make have like.... only quest givers or like 3NPCs in a town...they dont feel a live". Brill
had 20 people and 18 of them gave quests. Now the street has its residents: the drinkers and the barmaid at the
Gallows' End, the square's idlers, the clerks at the Town Hall, the gravediggers, the farm plots' tenders, the market
lane and both gates. Mostly Forsaken, dry and tired, with a few others the way Undercity's country is. None of them
gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the West Road
    ("br_tf_west_sentry", "Deathguard Halloway", "forsaken", M, "The West Road",
     "I watch the road from Deathknell, and I've watched it for three years. Every new one who comes up it looks lost, "
     "and I point them to the inn. It's the only kind thing I'm allowed to do on duty."),
    ("br_tf_west_walker", "Edith Crane", "forsaken", F, "The West Road",
     "I walk this road every morning because my legs remember doing it when I was alive. I don't remember where I "
     "was going, but my legs seem very sure about it."),
    ("br_tf_west_cart", "Old Tobias Wren", "forsaken", M, "The West Road",
     "My cart's lost a wheel again, and I've been sitting here waiting for it to fix itself. It hasn't yet, but I'm "
     "patient. I've got nowhere to be and forever to get there."),

    # ---- the Gallows' End Tavern
    ("br_tf_tavern_drinker", "Mortimer Hale", "forsaken", M, "Gallows' End Tavern",
     "I can't taste the ale any more, but I still order one every night. Holding the cup feels like being someone. "
     "The innkeeper doesn't charge me, which is decent of her."),
    ("br_tf_tavern_barmaid", "Lottie Graves", "forsaken", F, "Gallows' End Tavern",
     "I wipe the tables, sweep the floor and listen to the same six stories every evening. The stories don't get "
     "better, but the people telling them seem to need it, so I listen."),
    ("br_tf_tavern_card_player", "Silas Blackwood", "forsaken", M, "Gallows' End Tavern",
     "I've played cards with the same three fellows for two years. None of us remembers the rules the same way, so "
     "every game is a new argument. It passes the time."),
    ("br_tf_tavern_orc", "Grunt Nazgra", "orc", F, "Gallows' End Tavern",
     "The Warchief sent me to Brill to keep an eye on things, and the things have been very quiet. The Forsaken don't "
     "talk much, but they're good company once you stop staring."),

    # ---- Brill Square
    ("br_tf_square_crier", "Crier Beatrice Moss", "forsaken", F, "Brill Square",
     "I read the Dark Lady's notices from the square every noon. Most days nobody stops to listen, but I read them "
     "anyway. Somebody might need to hear them, and it gives me a reason to get up."),
    ("br_tf_square_bench", "Ambrose Finch", "forsaken", M, "Brill Square",
     "I sit on this bench because I sat on it when I was alive, with my wife. She didn't come back the way I did. I "
     "keep her side of the bench clear, just in case."),
    ("br_tf_square_child", "Pip Holloway", "forsaken", M, "Brill Square",
     "I was eleven when I died, and I'm still eleven, which isn't fair. The grown-ups won't let me do anything. At "
     "least nobody makes me eat vegetables any more."),
    ("br_tf_square_well", "Agnes Thorne", "forsaken", F, "Brill Square",
     "Don't drink from the square well, love. Nobody's quite sure what's at the bottom of it since the plague. I just "
     "come here to sit, because it's the middle of town."),
    ("br_tf_square_transplant", "Kenji Arakawa", "human", M, "Brill Square",
     "I was a schoolteacher in Sapporo, and I ended up in a town full of the walking dead. They've been kinder to me "
     "than I expected, and the apothecary has started teaching me chemistry."),

    # ---- Brill Town Hall
    ("br_tf_hall_clerk", "Clerk Josiah Pell", "forsaken", M, "Brill Town Hall",
     "I keep the town's records, which mostly means writing down who's died twice. It's a short list, but it's "
     "growing, and the ink runs out faster than it used to."),
    ("br_tf_hall_petitioner", "Martha Dunning", "forsaken", F, "Brill Town Hall",
     "I've come to ask for my old house back. The magistrate says I'm legally dead, which is true, but I still have "
     "the key. I think that ought to count for something."),
    ("br_tf_hall_guard", "Deathguard Ferris", "forsaken", M, "Brill Town Hall",
     "I guard the Town Hall door, and nobody's tried to get past me in two years. I think the smell keeps most people "
     "away, mine and the building's both."),

    # ---- the Graveyard
    ("br_tf_gravedigger", "Gravedigger Amos", "forsaken", M, "Brill Graveyard",
     "I dig graves for the ones who don't get up again. It's odd work for a dead man, and I've gotten very good at it. "
     "Mind where you step, some of the plots are fresh."),
    ("br_tf_grave_visitor", "Widow Rowena Ash", "forsaken", F, "Brill Graveyard",
     "My husband's buried over there, the proper way, with a stone and everything. I come and sit with him every "
     "evening. He was a terrible listener in life, and he's much better at it now."),
    ("br_tf_grave_tender", "Brother Caspar", "forsaken", M, "Brill Graveyard",
     "I tend the graves and pull the weeds. I used to be a priest of the Light, before. I don't pray any more, but I "
     "find I still like keeping things tidy for the dead."),

    # ---- the South Lane: the last farm plots
    ("br_tf_farmer", "Farmer Hiram Doyle", "forsaken", M, "The South Lane",
     "I grow pumpkins in what's left of the south field. They come up grey and they taste of nothing, but they grow, "
     "and that's more than most things do round here."),
    ("br_tf_farm_wife", "Clara Doyle", "forsaken", F, "The South Lane",
     "Hiram and I both came back, which the apothecaries say is rare for a married couple. We still argue about the "
     "pumpkins every morning. Some things death doesn't fix."),
    ("br_tf_scarecrow_mender", "Jem Haskett", "forsaken", M, "The South Lane",
     "I mend the scarecrows on the south plots. The crows aren't scared of them, and they aren't scared of me "
     "either. I think they know we're all made of the same old cloth."),

    # ---- the East Lane and the Market Lane
    ("br_tf_apothecary_runner", "Wick Sallow", "forsaken", M, "The East Lane",
     "I fetch for the apothecaries, bottles, herbs and things I'd rather not name. They pay well and ask nothing, "
     "and I've learned not to ask anything back."),
    ("br_tf_chapel_keeper", "Mother Prudence Vale", "forsaken", F, "The East Lane",
     "The old chapel's empty now, but I still sweep it every morning. Somebody built it with a lot of love, and I "
     "don't think it should fall down just because nobody prays in it."),
    ("br_tf_market_haggler", "Gideon Marsh", "forsaken", M, "The Market Lane",
     "I sell nothing and buy nothing, but I haggle with every merchant on the lane anyway. It's the only thing that "
     "makes me feel properly alive, and they've all learned to play along."),
    ("br_tf_market_goblin", "Snitch Bramblecog", "goblin", M, "The Market Lane",
     "I came to Brill thinking the dead would be easy customers. They aren't, because they've got nothing to spend "
     "and all the time in the world to decide. I've learned a lot about patience."),

    # ---- the East Gate
    ("br_tf_east_sentry", "Deathguard Morrow", "forsaken", M, "The East Gate",
     "This gate looks east toward the Undercity and the zeppelin tower. Everybody coming home goes through here, and "
     "everybody leaving for good does too. I try to nod at both."),
    ("br_tf_east_waiter", "Lydia Hartwell", "forsaken", F, "The East Gate",
     "I'm waiting for my son to come up from the Undercity. He said he'd visit this week, and he said that last week "
     "too. I'll keep waiting, because I've got the time now."),
]
