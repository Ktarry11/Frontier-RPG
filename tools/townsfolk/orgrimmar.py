"""Orgrimmar's people: the Horde's capital in the canyon (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", "capitals can be 50+", and "Generally cities lean towards one or two
races but not exclusive." Orgrimmar already had its trainers, traders, leaders and twenty-odd people of its own; these
thirty more make it a capital. Mostly orcs, then the Darkspear trolls who came with them, tauren, goblins, a few blood
elves and Forsaken, and the odd Earthborn who walked in off the Barrens road and stayed. None of them gives a quest,
sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Valley of Wisdom
    ("org_tf_hall_petitioner", "Petitioner Durga", "orc", F, "The Valley of Wisdom",
     "I've waited outside the Warchief's hall three days to ask for a plot of land by the river. The guards say he'll "
     "see me tomorrow, and they said that yesterday too, but I've got nowhere else to be."),
    ("org_tf_old_shaman", "Grandfather Morok", "orc", M, "The Valley of Wisdom",
     "I remember when we couldn't hear the spirits at all, before Thrall brought the old ways back. I come and sit by the "
     "lodge every morning just to listen, and they're never quiet now."),
    ("org_tf_tauren_pilgrim", "Ahiga Tallhorn", "tauren", M, "The Valley of Wisdom",
     "I walked from Mulgore to hear the orcs' shamans speak to the elements. They do it louder than we do, and the "
     "elements answer them anyway, which I'm still trying to understand."),
    ("org_tf_troll_storyteller", "Auntie Zhara", "troll", F, "The Valley of Wisdom",
     "I tell de children how de Darkspear came to dis land on de orcs' ships. Dey've heard it a hundred times, and dey "
     "still ask for de part wit' de sea witch."),
    # ---- the Wyvern Terrace
    ("org_tf_wyvern_feeder", "Gruzh", "orc", M, "The Wyvern Terrace",
     "I feed the wyverns raw kodo twice a day, and they still look at me like I'm dessert. Kar says that's respect, but "
     "I've noticed he stands well behind me when I do it."),
    ("org_tf_inn_regular", "Old Tusk Barga", "orc", M, "The Wyvern Terrace",
     "I fought at the internment camps' gates when we broke them open, and now I fight Gryshka for the seat by the fire. "
     "She wins more often than the humans did."),
    ("org_tf_bloodelf_student", "Lirien Dawncaller", "blood_elf", F, "The Wyvern Terrace",
     "I came to study under the mage trainer, and the orcs keep asking me why I'm so thin. I've stopped explaining and "
     "started eating their bread, which is very heavy and surprisingly good."),
    ("org_tf_goblin_tinker", "Spindle Gearsnap", "goblin", M, "The Wyvern Terrace",
     "The engineer's shop lets me sweep up the spare parts, and I build little wind-up wolves out of them. The orc "
     "children love them, and the grunts pretend they don't."),
    # ---- the Valley of Honor
    ("org_tf_young_grunt", "Grunt Kazka", "orc", F, "The Valley of Honor",
     "I joined the army last spring, and I've been on guard duty every day since. My sergeant says the Horde's real "
     "battles are fought standing still, and I'm starting to think he means it."),
    ("org_tf_kennel_keeper", "Kennel-Keeper Rugg", "orc", M, "The Valley of Honor",
     "I raise the wolf pups for the riders, and every one of them has a name and an opinion. The grey one bit a general "
     "last week, and I've never been prouder of an animal in my life."),
    ("org_tf_veteran", "One-Arm Throg", "orc", M, "The Valley of Honor",
     "I left the arm at the Dark Portal, and I don't miss it as much as you'd think. I teach the recruits to fight "
     "one-handed, so they're ready for the day it happens to them."),
    ("org_tf_troll_sparring", "Zen'ko", "troll", M, "The Valley of Honor",
     "De orcs fight like a falling rock, all at once and straight down. I fight like de river, and I've won more "
     "sparring matches dis month dan anybody in de barracks."),
    # ---- the Forge Row
    ("org_tf_forge_apprentice", "Apprentice Brakk", "orc", M, "The Forge Row",
     "I pump the bellows at the war forge from dawn till dusk, and I can't hear a thing by supper. Krunk says that's how "
     "you know you've done a good day's work."),
    ("org_tf_bank_queue", "Morra Ironvein", "orc", F, "The Forge Row",
     "I'm waiting on MerchantTusk to count out my savings, and he's been counting for an hour. He does it slowly on "
     "purpose, I'm sure of it, and he smiles the whole time."),
    ("org_tf_goblin_bidder", "Nettle Quickcoin", "goblin", F, "The Forge Row",
     "I buy things at the auction hall in the morning and sell them back in the afternoon. Nobody's caught on yet, and "
     "if you tell them, I'll know it was you."),
    ("org_tf_forsaken_smith", "Halden Crowe", "forsaken", M, "The Forge Row",
     "I was a blacksmith in Lordaeron before I died, and the orcs let me work their forge after I proved I wasn't "
     "contagious. They still stand upwind of me, but they buy my nails."),
    # ---- the Valley of Strength
    ("org_tf_market_porter", "Porter Ugra", "orc", F, "The Valley of Strength",
     "I carry crates between the stalls for anyone who pays, and I've carried everything from fish to a goblin who was "
     "too drunk to walk. The goblin tipped the best."),
    ("org_tf_well_gossip", "Mother Gasha", "orc", F, "The Valley of Strength",
     "I come to the well every morning for water and every afternoon for news. The water's always the same, but the "
     "news is never boring in a city this size."),
    ("org_tf_tauren_weaver", "Kanti Morningdew", "tauren", F, "The Valley of Strength",
     "I weave blankets from kodo wool, and the orcs buy them faster than I can make them. They say the canyon gets cold "
     "at night, which surprised me, because it never seems to cool down by day."),
    ("org_tf_troll_fisher", "Bwemba", "troll", M, "The Valley of Strength",
     "I bring de fish up from Echo Isles every morning and sell dem by noon. De orcs never learned to fish, mon, so "
     "I've got de whole city to myself."),
    ("org_tf_earth_cook", "Marcus Bell", "human", M, "The Valley of Strength",
     "I ran a barbecue joint in Memphis, and kodo ribs turn out to be about the best thing I've ever smoked. The orcs "
     "were suspicious of a human at first, but nobody stays suspicious of good ribs."),
    ("org_tf_earth_child", "Lucia Moreno", "human", F, "The Valley of Strength",
     "My mum and I woke up in the desert outside, and an orc patrol brought us in. Now I help at the bakery stall, and "
     "the orc kids taught me how to throw a spear, badly."),
    # ---- the Cleft of Shadow
    ("org_tf_shadow_lurker", "Vashka the Quiet", "orc", F, "The Cleft of Shadow",
     "People come down to the Cleft when they don't want to be seen, and I make sure nobody sees them. It pays better "
     "than you'd expect, and it's mostly very boring."),
    ("org_tf_forsaken_alchemist", "Mirabel Hask", "forsaken", F, "The Cleft of Shadow",
     "The Cleft's the only place in Orgrimmar the orcs don't mind my smell, because everything down here smells worse. "
     "I brew in peace, and nobody asks what's in the bottles."),
    ("org_tf_bloodelf_warlock", "Saelith Emberveil", "blood_elf", M, "The Cleft of Shadow",
     "I came to the Cleft because Silvermoon thought my studies were too dark. The orcs think they're dark too, but "
     "they've seen worse, and they let me get on with it."),
    # ---- the Low Homes
    ("org_tf_homemaker", "Rokka Stonefist", "orc", F, "The Low Homes",
     "My husband guards the gate, my son guards the wall, and I guard the house, which is the hardest job of the three. "
     "Nobody tries to raid the gate at supper time."),
    ("org_tf_child", "Little Zug", "orc", M, "The Low Homes",
     "When I'm big I'm going to ride a wolf and fly a wyvern and be the Warchief. My mother says I've got to finish my "
     "chores first, so I'm doing those now, mostly."),
    # ---- the Gate Ward
    ("org_tf_gate_trader", "Trader Hruk", "orc", M, "The Gate Ward",
     "I meet the caravans at the gate and buy whatever they couldn't sell on the road. Half of it's junk, and the other "
     "half's worth a fortune, and I've learned to tell which is which."),
    ("org_tf_tanner_hand", "Durba", "orc", F, "The Gate Ward",
     "I scrape hides at the tannery, and I've stopped noticing the smell. My friends noticed it for me, though, and "
     "they've stopped visiting."),
    # ---- the Wolf Pens
    ("org_tf_stable_boy", "Gorkul", "orc", M, "The Wolf Pens",
     "I muck out the wolf pens and brush the kodos, and the kodos are much friendlier about it. One of them follows me "
     "home some nights, and my mother's run out of patience."),
]
