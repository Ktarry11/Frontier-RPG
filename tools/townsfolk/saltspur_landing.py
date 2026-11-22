"""Saltspur Landing's people: the Horde's little harbour on the Arathi coast (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "Small towns can be 15-20". A landing: orcs of the bosun's crews,
Forsaken of the quartermaster's stores, the shipwright's goblins, and the sailors who come and go. None of them gives a
quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("ssl_tf_yard_sailor", "Sailor Groka", "orc", F, "The Landing Yard",
     "The landing yard's where the crews wait for the tide, and the tide's never in a hurry. Dice, grog and stories pass the time, mostly the grog."),
    ("ssl_tf_yard_loader", "Loader Thrag", "orc", M, "The Landing Yard",
     "Every crate off the boats goes up the yard on my shoulder. The mess hall's at the top, so at least the walk ends in supper."),
    ("ssl_tf_mess_cook", "Cook Hesk", "orc", M, "The Landing Yard",
     "Fish stew every night, because the sea gives us fish and nothing else. The crews complain, and they eat it, and they ask for seconds."),
    ("ssl_tf_mess_forsaken", "Barnaby Coldwater", "forsaken", M, "The Landing Yard",
     "The mess hall stays warm for the living ones, and I sit by the fire out of habit. Can't feel the warmth any more, but I remember liking it."),
    ("ssl_tf_yard_child", "Little Nakka", "orc", F, "The Landing Yard",
     "My father's on the boat that went out yesterday, and it'll be back tomorrow. I watch from the yard every morning, and one day it'll come early."),
    ("ssl_tf_store_clerk", "Clerk Edith Moor", "forsaken", F, "Saltspur Stores",
     "Every barrel in the stores gets counted twice and checked for rot once. The dead are good at spotting rot, as it happens."),
    ("ssl_tf_store_watch", "Grunt Vosh", "orc", M, "Saltspur Stores",
     "Guarding the stores means guarding them from the crews, mostly. The grog barrels go missing more than anything, and the crews never know who took them."),
    ("ssl_tf_tower_watch", "Watcher Kesh", "orc", F, "Saltspur Stores",
     "From the watchtower you can see sails coming round the point long before they land. Horde sails get a horn, Alliance sails get a bell, and the bell's rusty."),
    ("ssl_tf_store_goblin", "Nix Barrelwick", "goblin", M, "Saltspur Stores",
     "Cooperage for the whole landing, barrels made and barrels mended. A barrel's only a barrel until it leaks, and then it's a puddle with a lid."),
    ("ssl_tf_beach_caulker", "Caulker Fizzle", "goblin", F, "The Shipwright's Beach",
     "Oona's boats get their seams sealed by me, and the tar never comes off. My hands are black to the wrist, and the boats never leak."),
    ("ssl_tf_beach_apprentice", "Apprentice Grok", "orc", M, "The Shipwright's Beach",
     "Orcs don't build boats, everyone says, so the goblin's teaching me. The first one sank, and the second one floated, and the third one's going to sail."),
    ("ssl_tf_beach_net_mender", "Mender Ada Salt", "forsaken", F, "The Shipwright's Beach",
     "Nets mended on the beach in the sun, because the sun doesn't bother the dead. The crews bring me their torn ones, and they come back whole."),
    ("ssl_tf_smokehouse", "Smoker Gurka", "orc", F, "The Shipwright's Beach",
     "The smokehouse turns the catch into something that'll last a voyage. Smoked fish, smoked eel, and once, by accident, smoked goblin. He was fine."),
    ("ssl_tf_officer_house", "First Mate Drogan", "orc", M, "The Shipwright's Beach",
     "Shore leave at the officers' house means a bed that doesn't rock. Three nights on land, and I can't sleep without the sea moving under me."),
    ("ssl_tf_earth_sailor", "Erik Nilsson", "human", M, "The Landing Yard",
     "Fishing trawlers out of Gothenburg, and now orc longboats, which are heavier and slower and somehow more fun. The orcs sing when they row, and they sing badly."),
]
