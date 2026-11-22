"""Steamwheedle Port's people: the cartel's harbour town on the Tanaris coast (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." The port is the cartel's, so it's goblins first and last: dockers, tinkers, salvagers and the families
of all of them, with the sailors, caravan guards and drifters of every race the desert and the sea wash in. None of
them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Quay
    ("swp_tf_crane_hand", "Crane-Hand Bolt", "goblin", M, "The Quay",
     "The dock cranes swing a ton of cargo over people's heads all day, and the cartel's never once paid for a hat. Mine's got three dents in it, and I'm still here."),
    ("swp_tf_fish_gutter", "Gutter Mag", "goblin", F, "The Quay",
     "Oda's fish come in at dawn, and by noon they're gutted, salted and sold to the desert caravans. The sand eats everything, but salted fish lasts forever."),
    ("swp_tf_sailor_orc", "Bosun Krugga", "orc", F, "The Quay",
     "My ship runs cargo from Ratchet to here and back, and the cartel pays in gold, not promises. The sea's rough, but the sand's worse, so I stay on the water."),
    ("swp_tf_sailor_human", "Old Tamsin Reed", "human", F, "The Quay",
     "Forty years at sea, and this is the only port where nobody cares who you sailed for. The goblins care what you're carrying, and that's a simpler question."),
    ("swp_tf_quay_kid", "Spanner", "goblin", M, "The Quay",
     "Every ship that docks gets counted, every sail gets named, and every captain owes me a copper for the information. Most of them pay just to make me go away."),
    ("swp_tf_inn_regular", "Rumhand Fezzik", "goblin", M, "The Quay",
     "The harbour inn has the best view in Tanaris, if you like watching other people work. The barkeep says I've been watching for eleven years."),
    # ---- the Upper Yard
    ("swp_tf_forge_apprentice", "Apprentice Clinker", "goblin", F, "The Upper Yard",
     "Dorga's forge burns hot enough to melt sand into glass, and that's not a figure of speech. Half the windows in the port came out of our fire."),
    ("swp_tf_workshop_tinker", "Tinker Quillsprocket", "goblin", M, "The Upper Yard",
     "The engineering workshop's been building a shredder that walks on sand for six years. It's walked twice, and both times it walked into the sea."),
    ("swp_tf_water_keeper", "Water-Warden Drizzle", "goblin", F, "The Upper Yard",
     "The water tower's the only reason anybody lives in this port. Every drop is metered, every bucket is logged, and the cartel's still losing money on it."),
    ("swp_tf_auction_watcher", "Bidder Nix", "goblin", M, "The Upper Yard",
     "The auction house opens at noon, and the best deals go in the first minute. Speed is everything, and so is pretending you don't want it."),
    ("swp_tf_house_mother", "Ma Rivetta", "goblin", F, "The Upper Yard",
     "Five kids in the stacked houses, and every one of them can count change faster than the bank clerks. That's not bragging, that's an investment."),
    ("swp_tf_tauren_caravan", "Caravan Guard Kanuna", "tauren", M, "The Upper Yard",
     "The desert caravans hire tauren because the sand doesn't slow us down. The heat does, and the goblins pay extra for the water I drink."),
    ("swp_tf_earth_engineer", "Priya Nair", "human", F, "The Upper Yard",
     "Desalination plants in Chennai were my whole career, and the cartel can't believe somebody knows how to make sea water drinkable. Neither can I, with these parts."),
    # ---- the Scrap End
    ("swp_tf_scrap_picker", "Picker Junka", "goblin", F, "The Scrap End",
     "The salvage yard is where machines go to die, and I'm the one who checks they're really dead. Most of them still twitch, and a couple of them still bite."),
    ("swp_tf_scrap_old", "Old Grumbolt", "goblin", M, "The Scrap End",
     "Built half the machines in that yard back when the cartel had money to burn. Now they burn my machines for scrap, and I sit here and watch."),
    ("swp_tf_scrap_troll", "Zaba", "troll", F, "The Scrap End",
     "De goblins t'row away more metal in a week dan my village saw in a year, mon. I pick de good bits and send dem home on de boat."),
    ("swp_tf_shredder_pilot", "Pilot Gearlock", "goblin", M, "The Scrap End",
     "A shredder pilot without a shredder is just a goblin with a funny hat. Mine's in the hangar waiting on parts, and it's been waiting since spring."),
    ("swp_tf_scrap_kid", "Little Wrench", "goblin", F, "The Scrap End",
     "Every bolt in the yard is worth a copper to the right buyer, and I know every buyer. By the time I'm grown, I'll own the whole yard."),
    ("swp_tf_earth_scavenger", "Joe Brennan", "human", M, "The Scrap End",
     "Ran a scrapyard in Glasgow, and the goblins think it's hilarious that we used to pay people to take metal away. Here they pay you to bring it in, and they're right."),
    # ---- the Lighthouse Pier
    ("swp_tf_lighthouse_keeper", "Lamp-Tender Wick", "goblin", M, "The Lighthouse Pier",
     "The lighthouse runs on a gas mixture of my own invention, and it's only exploded once. The ships see it from three leagues out, and the explosion was seen from five."),
    ("swp_tf_customs_aide", "Aide Fennimore", "goblin", F, "The Lighthouse Pier",
     "Every crate off the ships gets searched at the customs house, and every search finds something. Mostly it's sand, which isn't illegal, but it's very annoying."),
    ("swp_tf_boarding_lodger", "Lodger Pezz", "goblin", M, "The Lighthouse Pier",
     "The boarding house rents by the night, and I've been renting by the night for six years. The landlady keeps offering me a weekly rate, and that feels like a trap."),
    ("swp_tf_firework_maker", "Sparky Dazzlefuse", "goblin", F, "The Lighthouse Pier",
     "The fireworks shop lights up the harbour every new moon, and the ships come in just to watch. Some of them come in faster than they meant to."),
    ("swp_tf_fisher_orc", "Grukk Netmaw", "orc", M, "The Lighthouse Pier",
     "The best fishing in Tanaris is off the end of this pier, where the lighthouse throws its shadow. The goblins buy everything I catch, and they never ask how."),
    ("swp_tf_pier_wanderer", "Marisol Vega", "human", F, "The Lighthouse Pier",
     "Watching the ships come in reminds me of the harbour in Valparaiso, where I grew up. The ships here have rockets on them, which ours never did."),
]
