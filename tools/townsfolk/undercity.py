"""Undercity's people: the Forsaken's capital under the ruins of Lordaeron (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", "capitals can be 50+", and "Generally cities lean towards one or two
races but not exclusive." Undercity had its trainers, traders and twenty people of its own; these thirty-one make it a
capital. Forsaken above all, the dead who kept their minds, then a few living allies who come down the stairs on
business: an orc, a troll, blood elves, and an Earthborn or two who found the dead easier company than they expected.
None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("ucf_tf_court_petitioner", "Petitioner Agnes Wold", "forsaken", F, "The Royal Quarter",
     "My old farm in Tirisfal is mine by rights, and the Dark Lady's clerk agrees I've got a fair claim. I was"
     " buried in its orchard, after all."),
    ("ucf_tf_royal_clerk", "Clerk Barnaby Shroud", "forsaken", M, "The Royal Quarter",
     "The dead have a great deal of time to file complaints, and every one of them lands on my desk. Half get "
     "answered, and the other half get filed again."),
    ("ucf_tf_old_noble", "Lord Edric Varne", "forsaken", M, "The Royal Quarter",
     "There was a Lordaeron once, and I was one of its lords, with a house in the city above. A bench in the "
     "Royal Quarter suits me rather better, as it turns out."),
    ("ucf_tf_bloodelf_envoy_aide", "Aide Selenne Brightwater", "blood_elf", F, "The Royal Quarter",
     "Silvermoon's envoy told me not to stare before we came down. It's very hard not to stare, and the "
     "Forsaken are kind enough to pretend they don't notice."),
    ("ucf_tf_apprentice_mage", "Apprentice Corvus Pell", "forsaken", M, "The Magic Quarter",
     "I studied magic in Dalaran before I died, and I'm studying it again now, with fewer distractions. Sleep "
     "was always the thing that slowed me down, and I don't need it any more."),
    ("ucf_tf_tower_sweeper", "Hettie Ashgrove", "forsaken", F, "The Magic Quarter",
     "Half the dust in this tower is bone and half is arcane powder. It glows when it's swept into a pile, "
     "which makes the job more interesting than you'd think."),
    ("ucf_tf_warlock_student", "Morwen Blackmoor", "forsaken", F, "The Magic Quarter",
     "Binding imps is harder than the dreadmaster makes it look, and the imps are learning to bite. Three "
     "fingers sewn back on this month, and counting."),
    ("ucf_tf_bloodelf_scholar", "Theron Dawnquill", "blood_elf", M, "The Magic Quarter",
     "The Forsaken keep libraries the living forgot about, and I've been reading in one for a month. Nobody's "
     "asked me to leave yet, and I've stopped noticing the smell."),
    ("ucf_tf_deathguard_recruit", "Recruit Tobias Hull", "forsaken", M, "The War Quarter",
     "The drillmaster says the Deathguard's slowest recruit is me. Fine by me, because I've got all the time "
     "in the world now."),
    ("ucf_tf_forge_bellows", "Bellows Martha Crane", "forsaken", F, "The War Quarter",
     "The grand forge's heat doesn't bother me at all now, and that's the one good thing about being dead. "
     "Might as well make the most of it at the bellows."),
    ("ucf_tf_orc_trainer_aide", "Grunt Mukla", "orc", F, "The War Quarter",
     "The Deathguard don't bleed and they don't tire, and they still can't hold a shield properly. The "
     "battlemaster brought me down to fix that, and it's slow going."),
    ("ucf_tf_veteran", "Old Sergeant Lowe", "forsaken", M, "The War Quarter",
     "I fought the Scourge alive, and I fought them dead, and I'll fight them again if they come back. I sit "
     "by the barracks and tell the recruits what it was like, and they listen better than the living did."),
    ("ucf_tf_apoth_runner", "Runner Silas Quill", "forsaken", M, "The Apothecarium",
     "Never ask what's in the jars, that's the first rule of running samples here. One of them knocked from "
     "the inside last week, and I ran the rest of the way."),
    ("ucf_tf_apoth_washer", "Greta Mould", "forsaken", F, "The Apothecarium",
     "The acids took the feeling out of my hands, washing these vats. Doesn't matter much, because most of it "
     "was gone already."),
    ("ucf_tf_plague_patient", "Patient Number Nine", "forsaken", M, "The Apothecarium",
     "Volunteering for an apothecary's test seemed like a good idea at the time. Now I glow a little green in "
     "the dark, and they keep saying it'll wear off."),
    ("ucf_tf_troll_herbalist", "Zhen'gai", "troll", F, "The Apothecarium",
     "De apothecaries pay very well for jungle herbs, mon, and dey never say what de herbs are for. Nobody "
     "asks, and dat's why de coin keeps comin'."),
    ("ucf_tf_canal_boatman", "Boatman Jory Fen", "forsaken", M, "The Trade Ring",
     "The green water in these canals is no good for drinking, and no good for anything else either. So nobody"
     " minds a little boat poling goods round the ring."),
    ("ucf_tf_market_gossip", "Widow Plume", "forsaken", F, "The Trade Ring",
     "Who died and came back this week, that's the news worth having in this market. It's the same news as "
     "when I was alive, only now it has a happier ending."),
    ("ucf_tf_bank_waiter", "Cuthbert Lane", "forsaken", M, "The Trade Ring",
     "An hour I've been waiting for MerchantTusk to open my account. He's very polite about it, and very slow,"
     " and I'm certain both are on purpose."),
    ("ucf_tf_goblin_buyer", "Grinny Twistlock", "goblin", M, "The Trade Ring",
     "The auction hall down here has the best prices in the Horde, because the Forsaken don't haggle. They "
     "just stare, and I've learned to name my lowest price first."),
    ("ucf_tf_earth_florist", "Charlotte Webb", "human", F, "The Trade Ring",
     "Back in Bristol it was a flower shop, and down here it's dried flowers for the Forsaken's graves. "
     "They're the most sentimental customers anyone could ask for."),
    ("ucf_tf_earth_mortician", "Darius Okafor", "human", M, "The Trade Ring",
     "An undertaker from Atlanta, living with the dead, and the Forsaken think it's the funniest thing they've"
     " ever heard. They made me an honorary citizen."),
    ("ucf_tf_child_ghoul_keeper", "Little Mags", "forsaken", F, "The Trade Ring",
     "I was nine when I died, and I'm still nine, and I'll always be nine. I keep a pet ghoul on a lead, and "
     "it's the best dog I've ever had, even if it's not really a dog."),
    ("ucf_tf_stair_guard", "Deathguard Ellis", "forsaken", M, "The North Stair",
     "Most of the living who come down this stair turn round when they see me. That's their loss, as far as "
     "the Deathguard's concerned."),
    ("ucf_tf_ruins_wanderer", "Annabel Grey", "forsaken", F, "The North Stair",
     "Where my house used to be, up in the ruins, the view of the sky's still the same. Every evening I climb "
     "up and look at it before coming back down."),
    ("ucf_tf_bat_feeder", "Feeder Hob", "forsaken", M, "The South Stair",
     "The bats eat better than I ever did alive, and they're good company besides. They don't mind that most "
     "of my nose is missing."),
    ("ucf_tf_deeps_lurker", "Sexton Pym", "forsaken", M, "The South Stair",
     "I dig the new graves down here for the ones who don't wake up. There aren't many, and I give each of "
     "them a proper stone, because somebody should."),
    ("ucf_tf_stable_hand", "Stablehand Tilly", "forsaken", F, "The War Quarter",
     "The skeletal horses are the gentlest creatures in Undercity. They don't eat, they don't sleep, and they "
     "nuzzle me when I brush their ribs."),
    ("ucf_tf_poet", "Nathaniel Ashe", "forsaken", M, "The Royal Quarter",
     "I was a poet in life, and nobody read me, and now I'm a poet in death, and the Forsaken read everything."
     " They say my verses are too cheerful, which nobody ever said when I was alive."),
    ("ucf_tf_orc_trader_aide", "Durza", "orc", F, "The Trade Ring",
     "Grukthar's stall sells out of everything we bring down from Orgrimmar. The Forsaken pay in coins so old "
     "a scholar has to tell us what they're worth."),
    ("ucf_tf_tailor_apprentice", "Prudence Hemlock", "forsaken", F, "The Magic Quarter",
     "Robes for the mages, and stitches for the mages when their spells go wrong. The robes are harder, "
     "because the mages complain about the colour."),
]
