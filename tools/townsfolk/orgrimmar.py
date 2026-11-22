"""Orgrimmar's people: the Horde's capital in the canyon (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", "capitals can be 50+", and "Generally cities lean towards one or two
races but not exclusive." Orgrimmar already had its trainers, traders, leaders and twenty-odd people of its own; these
thirty more make it a capital. Mostly orcs, then the Darkspear trolls who came with them, tauren, goblins, a few blood
elves and Forsaken, and the odd Earthborn who walked in off the Barrens road and stayed. None of them gives a quest,
sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("org_tf_hall_petitioner", "Petitioner Durga", "orc", F, "The Valley of Wisdom",
     "Three days outside the Warchief's hall, waiting to ask for a plot of land by the river. The guards say "
     "tomorrow, and they said that yesterday too."),
    ("org_tf_old_shaman", "Grandfather Morok", "orc", M, "The Valley of Wisdom",
     "I remember when we couldn't hear the spirits at all, before Thrall brought the old ways back. I come and"
     " sit by the lodge every morning just to listen, and they're never quiet now."),
    ("org_tf_tauren_pilgrim", "Ahiga Tallhorn", "tauren", M, "The Valley of Wisdom",
     "All the way from Mulgore to hear the orcs' shamans speak to the elements. They shout where we whisper, "
     "and the elements answer them anyway."),
    ("org_tf_troll_storyteller", "Auntie Zhara", "troll", F, "The Valley of Wisdom",
     "De children want de story of how de Darkspear came here on de orcs' ships, every single night. Dey "
     "always ask for de part wit' de sea witch."),
    ("org_tf_wyvern_feeder", "Gruzh", "orc", M, "The Wyvern Terrace",
     "Raw kodo twice a day, and the wyverns still look at me like I'm dessert. Kar calls that respect, and he "
     "stands well behind me while I do it."),
    ("org_tf_inn_regular", "Old Tusk Barga", "orc", M, "The Wyvern Terrace",
     "We broke the internment camps' gates open, and I was at the front. Now the only fight I've got left is "
     "with Gryshka for the seat by the fire."),
    ("org_tf_bloodelf_student", "Lirien Dawncaller", "blood_elf", F, "The Wyvern Terrace",
     "The orcs keep asking why I'm so thin, ever since I came to study under the mage trainer. Their bread is "
     "very heavy, and surprisingly good."),
    ("org_tf_goblin_tinker", "Spindle Gearsnap", "goblin", M, "The Wyvern Terrace",
     "The engineer's shop lets me sweep up the spare parts, and I build little wind-up wolves out of them. The"
     " orc children love them, and the grunts pretend they don't."),
    ("org_tf_young_grunt", "Grunt Kazka", "orc", F, "The Valley of Honor",
     "Guard duty every day since I joined up last spring. My sergeant says the Horde's real battles are fought"
     " standing still, and he might mean it."),
    ("org_tf_kennel_keeper", "Kennel-Keeper Rugg", "orc", M, "The Valley of Honor",
     "Every wolf pup in these kennels has a name and an opinion. The grey one bit a general last week, and "
     "I've never been prouder of an animal."),
    ("org_tf_veteran", "One-Arm Throg", "orc", M, "The Valley of Honor",
     "The arm stayed at the Dark Portal, and it's missed less than you'd think. The recruits learn to fight "
     "one-handed from me, for the day it happens to them."),
    ("org_tf_troll_sparring", "Zen'ko", "troll", M, "The Valley of Honor",
     "De orcs fight like a falling rock, all at once and straight down. I fight like de river, and I've won "
     "more sparring matches dis month dan anybody in de barracks."),
    ("org_tf_forge_apprentice", "Apprentice Brakk", "orc", M, "The Forge Row",
     "Dawn till dusk on the war forge's bellows, and nobody can hear a thing by supper. Krunk says that's how "
     "you know it was a good day's work."),
    ("org_tf_bank_queue", "Morra Ironvein", "orc", F, "The Forge Row",
     "MerchantTusk has been counting out my savings for an hour now. He does it slowly on purpose, and he "
     "smiles the whole time."),
    ("org_tf_goblin_bidder", "Nettle Quickcoin", "goblin", F, "The Forge Row",
     "Buy at the auction hall in the morning, sell it back in the afternoon. Nobody's caught on yet, and if "
     "they do, I'll know it was you."),
    ("org_tf_forsaken_smith", "Halden Crowe", "forsaken", M, "The Forge Row",
     "Lordaeron had me as a blacksmith before I died, and Orgrimmar has me now, once I'd proved I wasn't "
     "contagious. They stand upwind, but they buy my nails."),
    ("org_tf_market_porter", "Porter Ugra", "orc", F, "The Valley of Strength",
     "Fish, furniture, and once a goblin too drunk to walk, all carried between these stalls for a coin. The "
     "goblin tipped the best."),
    ("org_tf_well_gossip", "Mother Gasha", "orc", F, "The Valley of Strength",
     "Water in the morning and news in the afternoon, that's what the well's for. The water's always the same,"
     " and the news never is."),
    ("org_tf_tauren_weaver", "Kanti Morningdew", "tauren", F, "The Valley of Strength",
     "Kodo wool blankets sell faster here than anything else on my table. The canyon gets cold at night, the "
     "orcs say, though it never seems to cool by day."),
    ("org_tf_troll_fisher", "Bwemba", "troll", M, "The Valley of Strength",
     "De orcs never learned to fish, mon, so de whole city's mine. Up from Echo Isles every morning, and sold "
     "out by noon."),
    ("org_tf_earth_cook", "Marcus Bell", "human", M, "The Valley of Strength",
     "Kodo ribs turn out to be about the best thing I've ever smoked, and I ran a barbecue joint in Memphis. "
     "Nobody stays suspicious of good ribs for long."),
    ("org_tf_earth_child", "Lucia Moreno", "human", F, "The Valley of Strength",
     "My mum and I woke up in the desert outside, and an orc patrol brought us in. Now I help at the bakery "
     "stall, and the orc kids taught me how to throw a spear, badly."),
    ("org_tf_shadow_lurker", "Vashka the Quiet", "orc", F, "The Cleft of Shadow",
     "People come down to the Cleft when they don't want to be seen, and I make sure nobody sees them. It pays"
     " better than you'd expect, and it's mostly very boring."),
    ("org_tf_forsaken_alchemist", "Mirabel Hask", "forsaken", F, "The Cleft of Shadow",
     "The Cleft's the only place in Orgrimmar the orcs don't mind my smell, because everything down here "
     "smells worse. I brew in peace, and nobody asks what's in the bottles."),
    ("org_tf_bloodelf_warlock", "Saelith Emberveil", "blood_elf", M, "The Cleft of Shadow",
     "Silvermoon thought my studies were too dark, so the Cleft it is. The orcs think they're dark too, but "
     "they've seen worse, and they leave me be."),
    ("org_tf_homemaker", "Rokka Stonefist", "orc", F, "The Low Homes",
     "My husband guards the gate, my son guards the wall, and I guard the house, which is the hardest job of "
     "the three. Nobody tries to raid the gate at supper time."),
    ("org_tf_child", "Little Zug", "orc", M, "The Low Homes",
     "When I'm big I'm going to ride a wolf and fly a wyvern and be the Warchief. My mother says I've got to "
     "finish my chores first, so I'm doing those now, mostly."),
    ("org_tf_gate_trader", "Trader Hruk", "orc", M, "The Gate Ward",
     "Whatever the caravans couldn't sell on the road ends up with me at the gate. Half of it's junk, half of "
     "it's a fortune, and the trick is knowing which."),
    ("org_tf_tanner_hand", "Durba", "orc", F, "The Gate Ward",
     "The smell of the tannery stopped bothering me months ago. My friends still notice it, and they've "
     "stopped visiting."),
    ("org_tf_stable_boy", "Gorkul", "orc", M, "The Wolf Pens",
     "I muck out the wolf pens and brush the kodos, and the kodos are much friendlier about it. One of them "
     "follows me home some nights, and my mother's run out of patience."),
]
