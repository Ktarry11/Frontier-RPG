"""Undercity's people: the Forsaken's capital under the ruins of Lordaeron (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", "capitals can be 50+", and "Generally cities lean towards one or two
races but not exclusive." Undercity had its trainers, traders and twenty people of its own; these thirty-one make it a
capital. Forsaken above all, the dead who kept their minds, then a few living allies who come down the stairs on
business: an orc, a troll, blood elves, and an Earthborn or two who found the dead easier company than they expected.
None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Royal Quarter
    ("ucf_tf_court_petitioner", "Petitioner Agnes Wold", "forsaken", F, "The Royal Quarter",
     "I've come to ask the Dark Lady for the deed to my old farm in Tirisfal. I was buried in its orchard, so I think "
     "I've got a fair claim, and the clerk says she'll consider it."),
    ("ucf_tf_royal_clerk", "Clerk Barnaby Shroud", "forsaken", M, "The Royal Quarter",
     "I keep the Royal Quarter's records, and there are a great many of them, because the dead have a lot of time to "
     "file complaints. I read every one, and I answer about half."),
    ("ucf_tf_old_noble", "Lord Edric Varne", "forsaken", M, "The Royal Quarter",
     "I was a lord in Lordaeron when there was a Lordaeron, and I had a house in the city above. Now I've got a bench in "
     "the Royal Quarter, and I've found it suits me rather better."),
    ("ucf_tf_bloodelf_envoy_aide", "Aide Selenne Brightwater", "blood_elf", F, "The Royal Quarter",
     "I came down with Silvermoon's envoy, and I've been told not to stare. It's very hard not to stare, and the "
     "Forsaken are kind enough to pretend they don't notice."),
    # ---- the Magic Quarter
    ("ucf_tf_apprentice_mage", "Apprentice Corvus Pell", "forsaken", M, "The Magic Quarter",
     "I studied magic in Dalaran before I died, and I'm studying it again now, with fewer distractions. Sleep was "
     "always the thing that slowed me down, and I don't need it any more."),
    ("ucf_tf_tower_sweeper", "Hettie Ashgrove", "forsaken", F, "The Magic Quarter",
     "I sweep the mage tower's floors, and the dust down here's half bone and half arcane powder. It glows when I sweep "
     "it into a pile, which makes the job more interesting than you'd think."),
    ("ucf_tf_warlock_student", "Morwen Blackmoor", "forsaken", F, "The Magic Quarter",
     "I'm learning to bind imps, and the imps are learning to bite. The dreadmaster says I'll get the hang of it, and "
     "I've stopped counting how many fingers I've had sewn back on."),
    ("ucf_tf_bloodelf_scholar", "Theron Dawnquill", "blood_elf", M, "The Magic Quarter",
     "The Forsaken keep libraries the living forgot about, and I've been reading in one for a month. Nobody's asked me "
     "to leave yet, and I've stopped noticing the smell."),
    # ---- the War Quarter
    ("ucf_tf_deathguard_recruit", "Recruit Tobias Hull", "forsaken", M, "The War Quarter",
     "I joined the Deathguard the week I woke up, because I needed something to do with my hands. The drillmaster says "
     "I'm too slow, and I've told him I've got all the time in the world."),
    ("ucf_tf_forge_bellows", "Bellows Martha Crane", "forsaken", F, "The War Quarter",
     "I work the bellows at the grand forge, and the heat doesn't bother me at all now. That's the one good thing about "
     "being dead, and I make the most of it."),
    ("ucf_tf_orc_trainer_aide", "Grunt Mukla", "orc", F, "The War Quarter",
     "I came down with the battlemaster to help train the Deathguard. They don't bleed and they don't tire, and they "
     "still can't hold a shield properly, so I've got plenty of work."),
    ("ucf_tf_veteran", "Old Sergeant Lowe", "forsaken", M, "The War Quarter",
     "I fought the Scourge alive, and I fought them dead, and I'll fight them again if they come back. I sit by the "
     "barracks and tell the recruits what it was like, and they listen better than the living did."),
    # ---- the Apothecarium
    ("ucf_tf_apoth_runner", "Runner Silas Quill", "forsaken", M, "The Apothecarium",
     "I carry samples between the apothecaries, and I've learned never to ask what's in the jars. One of them knocked "
     "from the inside last week, and I ran the rest of the way."),
    ("ucf_tf_apoth_washer", "Greta Mould", "forsaken", F, "The Apothecarium",
     "I wash the beakers and the vats, and I've lost the feeling in my hands from the acids. It doesn't matter much, "
     "because I'd lost most of the feeling in them already."),
    ("ucf_tf_plague_patient", "Patient Number Nine", "forsaken", M, "The Apothecarium",
     "I volunteered for one of the apothecaries' tests, and now I glow a little green in the dark. They say it'll wear "
     "off, and they've been saying that for three weeks."),
    ("ucf_tf_troll_herbalist", "Zhen'gai", "troll", F, "The Apothecarium",
     "I bring herbs from de jungle for de apothecaries, mon, and dey pay very well. Dey don't tell me what de herbs are "
     "for, and I don't ask, and dat's why dey keep payin'."),
    # ---- the Trade Ring
    ("ucf_tf_canal_boatman", "Boatman Jory Fen", "forsaken", M, "The Trade Ring",
     "I pole a little boat along the canals and carry goods round the ring. The green water's no good for drinking, "
     "but it's no good for anything else either, so nobody minds my boat."),
    ("ucf_tf_market_gossip", "Widow Plume", "forsaken", F, "The Trade Ring",
     "I come to the market every day to hear who's died and come back this week. It's the same news as when I was "
     "alive, only now it has a happier ending."),
    ("ucf_tf_bank_waiter", "Cuthbert Lane", "forsaken", M, "The Trade Ring",
     "I've been waiting for MerchantTusk to open my account for an hour. He's very polite about it, and he's very slow, "
     "and I'm certain both are on purpose."),
    ("ucf_tf_goblin_buyer", "Grinny Twistlock", "goblin", M, "The Trade Ring",
     "The auction hall down here has the best prices in the Horde, because the Forsaken don't haggle. They just stare, "
     "and I've learned to name my lowest price first."),
    ("ucf_tf_earth_florist", "Charlotte Webb", "human", F, "The Trade Ring",
     "I ran a flower shop in Bristol, and now I sell dried flowers to the Forsaken for their graves. They're the most "
     "sentimental customers I've ever had, and I didn't expect that at all."),
    ("ucf_tf_earth_mortician", "Darius Okafor", "human", M, "The Trade Ring",
     "I was an undertaker in Atlanta, and the Forsaken think that's the funniest thing they've ever heard. They've "
     "made me an honorary citizen, and I'm still deciding whether that's a compliment."),
    ("ucf_tf_child_ghoul_keeper", "Little Mags", "forsaken", F, "The Trade Ring",
     "I was nine when I died, and I'm still nine, and I'll always be nine. I keep a pet ghoul on a lead, and it's the "
     "best dog I've ever had, even if it's not really a dog."),
    # ---- the stairs
    ("ucf_tf_stair_guard", "Deathguard Ellis", "forsaken", M, "The North Stair",
     "I stand at the top of the stair and watch the ruins above for anybody who doesn't belong. Most of the living who "
     "come down turn round when they see me, and I've decided that's their loss."),
    ("ucf_tf_ruins_wanderer", "Annabel Grey", "forsaken", F, "The North Stair",
     "I climb up to the ruins every evening and sit where my house used to be. The city's gone, but the view of the "
     "sky's the same, and I like to look at it before I come back down."),
    ("ucf_tf_bat_feeder", "Feeder Hob", "forsaken", M, "The South Stair",
     "I feed the bats for the bat handler, and they eat better than I ever did alive. They're good company, and they "
     "don't mind that I'm missing most of my nose."),
    ("ucf_tf_deeps_lurker", "Sexton Pym", "forsaken", M, "The South Stair",
     "I dig the new graves down here for the ones who don't wake up. There aren't many, and I give each of them a proper "
     "stone, because somebody should."),
    ("ucf_tf_stable_hand", "Stablehand Tilly", "forsaken", F, "The War Quarter",
     "I care for the skeletal horses, and they're the gentlest creatures in Undercity. They don't eat, they don't "
     "sleep, and they nuzzle me when I brush their ribs."),
    ("ucf_tf_poet", "Nathaniel Ashe", "forsaken", M, "The Royal Quarter",
     "I was a poet in life, and nobody read me, and now I'm a poet in death, and the Forsaken read everything. They say "
     "my verses are too cheerful, which nobody ever said when I was alive."),
    ("ucf_tf_orc_trader_aide", "Durza", "orc", F, "The Trade Ring",
     "I help Grukthar run his stall, and the Forsaken buy everything we bring down from Orgrimmar. They pay in coins so "
     "old I've got to ask a scholar what they're worth."),
    ("ucf_tf_tailor_apprentice", "Prudence Hemlock", "forsaken", F, "The Magic Quarter",
     "I stitch robes for the mages, and I stitch the mages back together too when their spells go wrong. The robes are "
     "harder, because the mages complain about the colour."),
]
