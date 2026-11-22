"""Brill's people: the Forsaken village on the hill, and the few living who stay (21 Nov 2026).

Kyle: "a lot of towns you make have like.... only quest givers or like 3NPCs in a town...they dont feel a live". Brill
had 20 people and 18 of them gave quests. Now the street has its residents: the drinkers and the barmaid at the
Gallows' End, the square's idlers, the clerks at the Town Hall, the gravediggers, the farm plots' tenders, the market
lane and both gates. Mostly Forsaken, dry and tired, with a few others the way Undercity's country is. None of them
gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    ("br_tf_west_sentry", "Deathguard Halloway", "forsaken", M, "The West Road",
     "Three years watching the road from Deathknell, and every new one up it looks lost. Pointing them to the "
     "inn is the only kind thing allowed on duty."),
    ("br_tf_west_walker", "Edith Crane", "forsaken", F, "The West Road",
     "My legs remember walking this road every morning when I was alive. Where they were going is gone, but "
     "they seem very sure about it."),
    ("br_tf_west_cart", "Old Tobias Wren", "forsaken", M, "The West Road",
     "My cart's lost a wheel again, and I've been sitting here waiting for it to fix itself. It hasn't yet, "
     "but I'm patient. I've got nowhere to be and forever to get there."),
    ("br_tf_tavern_drinker", "Mortimer Hale", "forsaken", M, "Gallows' End Tavern",
     "The ale has no taste now, and there's still one ordered every night. Holding the cup feels like being "
     "someone, and the innkeeper doesn't charge, which is decent."),
    ("br_tf_tavern_barmaid", "Lottie Graves", "forsaken", F, "Gallows' End Tavern",
     "Same six stories every evening while the tables get wiped. They don't get better, but the people telling"
     " them seem to need it."),
    ("br_tf_tavern_card_player", "Silas Blackwood", "forsaken", M, "Gallows' End Tavern",
     "One of the fellows at my table came over from Silverpine, and he swears some of the pines up there weep "
     "like mourners. A whole grove of them nobody walks into, he says, and he was buried under a pine, so he "
     "might be biased."),
    ("br_tf_tavern_orc", "Grunt Nazgra", "orc", F, "Gallows' End Tavern",
     "The Warchief sent me to Brill to keep an eye on things, and the things have been very quiet. The "
     "Forsaken don't talk much, but they're good company once you stop staring."),
    ("br_tf_square_crier", "Crier Beatrice Moss", "forsaken", F, "Brill Square",
     "The Dark Lady's notices get read from the square every noon, whether anyone stops or not. Somebody might"
     " need to hear them, and it's a reason to get up."),
    ("br_tf_square_bench", "Ambrose Finch", "forsaken", M, "Brill Square",
     "My wife and I sat on this bench when we were alive. She didn't come back the way I did, and her side of "
     "the bench stays clear, just in case."),
    ("br_tf_square_child", "Pip Holloway", "forsaken", M, "Brill Square",
     "Eleven when I died, and still eleven, which isn't fair. The grown-ups won't let me do anything, but at "
     "least nobody makes me eat vegetables any more."),
    ("br_tf_square_well", "Agnes Thorne", "forsaken", F, "Brill Square",
     "Don't drink from the square well, love. Nobody's quite sure what's at the bottom of it since the plague."
     " I just come here to sit, because it's the middle of town."),
    ("br_tf_square_transplant", "Kenji Arakawa", "human", M, "Brill Square",
     "A schoolteacher from Sapporo, in a town full of the walking dead. They've been kinder than expected, and"
     " the apothecary's teaching me chemistry."),
    ("br_tf_hall_clerk", "Clerk Josiah Pell", "forsaken", M, "Brill Town Hall",
     "The town's records are mostly a list of who's died twice. It's short but growing, and the ink runs out "
     "faster than it used to."),
    ("br_tf_hall_petitioner", "Martha Dunning", "forsaken", F, "Brill Town Hall",
     "Legally dead, the magistrate says, which is true, and the key to my old house is still in my pocket. "
     "That ought to count for something."),
    ("br_tf_hall_guard", "Deathguard Ferris", "forsaken", M, "Brill Town Hall",
     "Nobody's tried to get past the Town Hall door in two years. The smell keeps most people away, the "
     "building's and mine both."),
    ("br_tf_gravedigger", "Gravedigger Amos", "forsaken", M, "Brill Graveyard",
     "I dig graves for the ones who don't get up again. It's odd work for a dead man, and I've gotten very "
     "good at it. Mind where you step, some of the plots are fresh."),
    ("br_tf_grave_visitor", "Widow Rowena Ash", "forsaken", F, "Brill Graveyard",
     "My husband's buried over there, the proper way, with a stone and everything. I come and sit with him "
     "every evening. He was a terrible listener in life, and he's much better at it now."),
    ("br_tf_grave_tender", "Brother Caspar", "forsaken", M, "Brill Graveyard",
     "Weeds pulled, graves tended, the way a priest of the Light would, before. The praying stopped, but "
     "keeping things tidy for the dead never did."),
    ("br_tf_farmer", "Farmer Hiram Doyle", "forsaken", M, "The South Lane",
     "Grey pumpkins in what's left of the south field, tasting of nothing. They grow, though, and that's more "
     "than most things do round here."),
    ("br_tf_farm_wife", "Clara Doyle", "forsaken", F, "The South Lane",
     "Hiram and I both came back, which the apothecaries say is rare for a married couple. We still argue "
     "about the pumpkins every morning. Some things death doesn't fix."),
    ("br_tf_scarecrow_mender", "Jem Haskett", "forsaken", M, "The South Lane",
     "The crows aren't scared of the scarecrows on the south plots, or of me. They know we're all made of the "
     "same old cloth."),
    ("br_tf_apothecary_runner", "Wick Sallow", "forsaken", M, "The East Lane",
     "Bottles, herbs and things best left unnamed, fetched for the apothecaries. They pay well and ask "
     "nothing, and nothing gets asked back."),
    ("br_tf_chapel_keeper", "Mother Prudence Vale", "forsaken", F, "The East Lane",
     "The old chapel's empty now, but I still sweep it every morning. Somebody built it with a lot of love, "
     "and I don't think it should fall down just because nobody prays in it."),
    ("br_tf_market_haggler", "Gideon Marsh", "forsaken", M, "The Market Lane",
     "Nothing bought, nothing sold, and every merchant on the lane gets haggled with anyway. It's the only "
     "thing that feels properly alive, and they've learned to play along."),
    ("br_tf_market_goblin", "Snitch Bramblecog", "goblin", M, "The Market Lane",
     "The dead seemed like easy customers from Booty Bay. They've got nothing to spend and all the time in the"
     " world to decide, and patience has been a hard lesson."),
    ("br_tf_east_sentry", "Deathguard Morrow", "forsaken", M, "The East Gate",
     "This gate looks east toward the Undercity and the zeppelin tower. Everybody coming home goes through "
     "here, and everybody leaving for good does too. I try to nod at both."),
    ("br_tf_east_waiter", "Lydia Hartwell", "forsaken", F, "The East Gate",
     "I'm waiting for my son to come up from the Undercity. He said he'd visit this week, and he said that "
     "last week too. I'll keep waiting, because I've got the time now."),
]
