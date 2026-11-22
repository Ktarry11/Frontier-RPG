"""Ratchet's people: the goblins' neutral port on the Barrens coast (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Gazlowe's port is a mid-size town: goblins first and last, then the sailors of every race who come in on
the boats, orcs and trolls working the docks, and a few humans who found the only harbour on the coast that doesn't ask
whose side you're on. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Office Row
    ("rt_tf_office_clerk", "Clerk Ledgerwick", "goblin", M, "The Office Row",
     "I file Gazlowe's contracts, and there are more of them than there are people in Ratchet. Half of them contradict "
     "the other half, and he likes it that way."),
    ("rt_tf_scrap_picker", "Scrappy Nell", "goblin", F, "The Office Row",
     "I pick through the scrapyard for anything that still works. Today I found half a shredder and a whole teapot, and "
     "I'm not sure which one I'm more excited about."),
    ("rt_tf_house_mother", "Granny Gizzle", "goblin", F, "The Office Row",
     "I've lived in Ratchet since it was three shacks and a pier, and I've seen every boss come and go. Gazlowe's the "
     "best of them, and I'll deny I said so if he asks."),
    ("rt_tf_runner_kid", "Zippy", "goblin", M, "The Office Row",
     "I run messages up and down the docks for a copper a trip. I'm the fastest runner in Ratchet, and I'm saving up for "
     "a pair of rocket boots."),
    # ---- the Harbor
    ("rt_tf_harbor_watch", "Lookout Spiv", "goblin", M, "The Harbor",
     "I sit in the harbour tower and watch for sails. Booty Bay's boat comes in on the tide, and I ring the bell so the "
     "dock crews wake up before it hits the pier."),
    ("rt_tf_orc_dockhand", "Dockhand Gruul", "orc", M, "The Harbor",
     "I unload the boats for the goblins because they pay in coin, not promises. The work's hard, but the sea air's "
     "better than the dust of the Barrens."),
    ("rt_tf_az_sailor", "Bosun Maggie Hart", "human", F, "The Harbor",
     "I crew on the Booty Bay run, and Ratchet's the only port on this coast where nobody cares that I'm human. They "
     "care whether I pay my bar tab, and I always pay my bar tab."),
    ("rt_tf_az_net_mender", "Old Barnaby", "human", M, "The Harbor",
     "I mend nets on the pier, and I've mended nets on piers from Kul Tiras to here. The goblins pay better than the "
     "admirals ever did, and they don't make me salute anybody."),
    # ---- the Customs Gate
    ("rt_tf_customs_aide", "Aide Fennick", "goblin", M, "The Customs Gate",
     "I help Prynn search the wagons for contraband, and I find something every single day. Most of it's cheese, which "
     "isn't illegal, but the smugglers hide it like it is."),
    ("rt_tf_road_guard", "Bruiser Kronk", "orc", M, "The Customs Gate",
     "The cartel hires me to stand at the gate and look scary. I'm very good at it, and I've only had to actually hit "
     "somebody twice this year."),
    # ---- the Bazaar
    ("rt_tf_bazaar_hawker", "Hawker Squee", "goblin", F, "The Bazaar",
     "Genuine pearls, genuine silks, genuine dragon scales, everything genuine! The pearls are real, anyway, and I'll "
     "let you guess about the rest."),
    ("rt_tf_troll_charm_seller", "Mama Jinju", "troll", F, "The Bazaar",
     "I sell charms for luck at sea, and every sailor in Ratchet's got one of mine. Dey don't all work, mon, but de ones "
     "dat don't, de sailors never come back to complain."),
    ("rt_tf_tauren_traveler", "Ohanzee Windwalker", "tauren", M, "The Bazaar",
     "I came to Ratchet to see the sea for the first time. It's bigger than the Barrens and louder than a stampede, and "
     "I've been staring at it for three days."),
    # ---- the Wharf
    ("rt_tf_fish_gutter", "Gutter Brine", "goblin", M, "The Wharf",
     "I gut fish for Gribble, a thousand a day in the good season. My hands smell like fish, my clothes smell like "
     "fish, and my wife married me anyway."),
    ("rt_tf_troll_fisher", "Kwame'ji", "troll", M, "The Wharf",
     "I fish off de end of de wharf every morning before de boats come in. De goblins sell my fish for twice what dey "
     "pay me, and I sell my fish to de goblins for twice what dey're worth."),
    ("rt_tf_warehouse_keeper", "Keeper Rattlebolt", "goblin", F, "The Wharf",
     "Every crate in my warehouse has a number, and every number has a ledger, and every ledger has a lock. Nothing's "
     "gone missing in five years, and the smugglers hate me for it."),
    ("rt_tf_earth_sailor", "Ricardo Alves", "human", M, "The Wharf",
     "I worked on container ships out of Santos, and now I crew on goblin boats, which are louder and much more "
     "dangerous. The pay's worse, but the stories are better."),
    # ---- the Broken Keel
    ("rt_tf_az_keel_drunk", "Sozzled Pete", "human", M, "The Broken Keel",
     "I came ashore here for one drink and missed my ship, and that was eleven years ago. Molka keeps my stool warm, "
     "and I keep her in business."),
    ("rt_tf_keel_card_player", "Cards Quigley", "goblin", M, "The Broken Keel",
     "I play cards in the Broken Keel every night, and I win more than I lose. That's not cheating, it's just very good "
     "luck, and I'd thank you to stop looking at my sleeves."),
    # ---- the Low Quarter
    ("rt_tf_boarding_landlady", "Landlady Fuzzwhit", "goblin", F, "The Low Quarter",
     "I rent rooms in the boarding house by the night, the week or the hour, and I don't ask which. The rooms are "
     "clean, the walls are thin, and the rent's due before you sleep."),
    ("rt_tf_orc_family", "Moka Ironfang", "orc", F, "The Low Quarter",
     "My husband works the docks and I work the laundry, and our children run wild with the goblin kids. They've "
     "learned to count money before they've learned to fight, which worries my husband."),
    ("rt_tf_earth_barber", "Yusuf Demir", "human", M, "The Low Quarter",
     "I cut hair in Istanbul, and now I shave goblins, which is much harder than it sounds. They have very strong "
     "opinions about their ear hair, and I've learned to respect every one of them."),
]
