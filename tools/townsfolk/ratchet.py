"""Ratchet's people: the goblins' neutral port on the Barrens coast (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." Gazlowe's port is a mid-size town: goblins first and last, then the sailors of every race who come in on
the boats, orcs and trolls working the docks, and a few humans who found the only harbour on the coast that doesn't ask
whose side you're on. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("rt_tf_office_clerk", "Clerk Ledgerwick", "goblin", M, "The Office Row",
     "There are more of Gazlowe's contracts in this office than there are people in Ratchet. Half of them "
     "contradict the other half, and he likes it that way."),
    ("rt_tf_scrap_picker", "Scrappy Nell", "goblin", F, "The Office Row",
     "Half a shredder and a whole teapot, that's today's haul from the scrapyard. Still deciding which one's "
     "more exciting."),
    ("rt_tf_house_mother", "Granny Gizzle", "goblin", F, "The Office Row",
     "Ratchet was three shacks and a pier when I moved in, and I've seen every boss come and go. Gazlowe's the"
     " best of them, and I'll deny saying so if he asks."),
    ("rt_tf_runner_kid", "Zippy", "goblin", M, "The Office Row",
     "A copper a trip, up and down the docks, and nobody in Ratchet runs faster. Rocket boots, that's what the"
     " coppers are for."),
    ("rt_tf_harbor_watch", "Lookout Spiv", "goblin", M, "The Harbor",
     "Booty Bay's boat comes in on the tide, and somebody has to ring the bell before it hits the pier. From "
     "up in the harbour tower, that somebody's me."),
    ("rt_tf_orc_dockhand", "Dockhand Gruul", "orc", M, "The Harbor",
     "The goblins pay in coin, not promises, so the boats get unloaded. The work's hard, but the sea air beats"
     " the dust of the Barrens."),
    ("rt_tf_az_sailor", "Bosun Maggie Hart", "human", F, "The Harbor",
     "Ratchet's the only port on this coast where nobody cares that a sailor's human. They care whether the "
     "bar tab's paid, and mine always is."),
    ("rt_tf_az_net_mender", "Old Barnaby", "human", M, "The Harbor",
     "From Kul Tiras to here, every pier had nets that needed mending. A sailor in from Tanaris swore a whole "
     "goblin caravan went under the dunes out east and never came up, but he owes me money, so I don't believe"
     " a word."),
    ("rt_tf_customs_aide", "Aide Fennick", "goblin", M, "The Customs Gate",
     "Prynn and I search the wagons, and we find something every single day. Most of it's cheese, which isn't "
     "illegal, but the smugglers hide it like it is."),
    ("rt_tf_road_guard", "Bruiser Kronk", "orc", M, "The Customs Gate",
     "The cartel hires me to stand at the gate and look scary. I'm very good at it, and I've only had to "
     "actually hit somebody twice this year."),
    ("rt_tf_bazaar_hawker", "Hawker Squee", "goblin", F, "The Bazaar",
     "Genuine pearls, genuine silks, genuine dragon scales, everything genuine! The pearls are real, anyway, "
     "and I'll let you guess about the rest."),
    ("rt_tf_troll_charm_seller", "Mama Jinju", "troll", F, "The Bazaar",
     "Every sailor in Ratchet wears one of my sea charms. Dey don't all work, mon, but de ones dat don't, "
     "nobody comes back to complain."),
    ("rt_tf_tauren_traveler", "Ohanzee Windwalker", "tauren", M, "The Bazaar",
     "Three days now I've been staring at the sea. It's bigger than the Barrens and louder than a stampede, "
     "and nobody in Mulgore will believe me."),
    ("rt_tf_fish_gutter", "Gutter Brine", "goblin", M, "The Wharf",
     "A thousand fish a day for Gribble in the good season. My hands smell like fish, my clothes smell like "
     "fish, and my wife married me anyway."),
    ("rt_tf_troll_fisher", "Kwame'ji", "troll", M, "The Wharf",
     "De goblins sell my fish for twice what dey pay me, mon. Dat's fine, because I sell dem to de goblins for"
     " twice what dey're worth."),
    ("rt_tf_warehouse_keeper", "Keeper Rattlebolt", "goblin", F, "The Wharf",
     "Every crate in my warehouse has a number, and every number has a ledger, and every ledger has a lock. "
     "Nothing's gone missing in five years, and the smugglers hate me for it."),
    ("rt_tf_earth_sailor", "Ricardo Alves", "human", M, "The Wharf",
     "Container ships out of Santos were nothing like goblin boats, which are louder and much more dangerous. "
     "The pay's worse, but the stories are better."),
    ("rt_tf_az_keel_drunk", "Sozzled Pete", "human", M, "The Broken Keel",
     "One drink ashore, a missed ship, and that was eleven years ago. Molka keeps my stool warm, and I keep "
     "her in business."),
    ("rt_tf_keel_card_player", "Cards Quigley", "goblin", M, "The Broken Keel",
     "More wins than losses in the Broken Keel, every night. That's not cheating, it's very good luck, and you"
     " can stop looking at my sleeves."),
    ("rt_tf_boarding_landlady", "Landlady Fuzzwhit", "goblin", F, "The Low Quarter",
     "I rent rooms in the boarding house by the night, the week or the hour, and I don't ask which. The rooms "
     "are clean, the walls are thin, and the rent's due before you sleep."),
    ("rt_tf_orc_family", "Moka Ironfang", "orc", F, "The Low Quarter",
     "My husband works the docks and I work the laundry, and our children run wild with the goblin kids. "
     "They've learned to count money before they've learned to fight, which worries my husband."),
    ("rt_tf_earth_barber", "Yusuf Demir", "human", M, "The Low Quarter",
     "I cut hair in Istanbul, and now I shave goblins, which is much harder than it sounds. They have very "
     "strong opinions about their ear hair, and I've learned to respect every one of them."),
]
