"""Razor Hill's people: the orcs' first town in Durotar, under the barracks hill (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "Small towns can be 15-20 ... cities lean towards one or two races
but not exclusive." Razor Hill already had its children, elders, refugees and travellers; these nine make it a town.
Mostly orcs, a troll or two from the Echo Isles, a goblin. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    ("rzh_tf_drill_sergeant", "Sergeant Gharr", "orc", M, "The Barracks Yard",
     "I drill the new grunts in the yard at dawn, and every one of them thinks he's the next Grom Hellscream. By noon "
     "they think they're going to die, and by supper they're soldiers."),
    ("rzh_tf_brewer", "Brewer Ozga", "orc", F, "The Barracks Yard",
     "The brew house makes the strongest ale in Durotar, and the grunts drink it like water. I water it down for the "
     "young ones, and they've never once noticed."),
    ("rzh_tf_smokehouse", "Old Kurgh", "orc", M, "The Barracks Yard",
     "I smoke boar and scorpid tail in the smokehouse, and the smell carries all the way to the coast. The trolls on "
     "the Echo Isles say they can smell my supper from their beach."),
    ("rzh_tf_spirit_tender", "Tender Mazra", "orc", F, "The Lodge Side",
     "I keep the spirit lodge's fire lit and its floor swept, and I listen when the shaman isn't looking. The spirits "
     "don't mind, and they've started speaking a little louder when I'm there."),
    ("rzh_tf_troll_mother", "Kwasi'ra", "troll", F, "The Lodge Side",
     "We came over from de Echo Isles when de sea witch's naga got too bold. Razor Hill took us in, and my boys are "
     "learnin' to fight like orcs, which I'm still decidin' how I feel about."),
    ("rzh_tf_market_haggler", "Ruga", "orc", F, "The Market Corner",
     "I come to the market every day to argue with the goblin about his prices. I never buy anything from him, but "
     "it's the best entertainment in Razor Hill."),
    ("rzh_tf_goblin_errand", "Pip Sparkfuse", "goblin", M, "The Market Corner",
     "I run errands for Prizzle at the engineer's shop, and half of them are just to keep me out of the way when "
     "something's about to explode. I know because I can hear it from the well."),
    ("rzh_tf_well_old", "Grandfather Durn", "orc", M, "The Well Square",
     "I dug this well with my own hands when we first came to Durotar, and the water's never once run dry. I sit here "
     "every day to make sure nobody spits in it."),
    ("rzh_tf_gate_watcher", "Watcher Bru", "orc", M, "The South Gate",
     "I count the travellers coming up the road from the Valley of Trials. Every one of them looks lost, and every one "
     "of them looks a bit less lost by the time they leave."),
]
