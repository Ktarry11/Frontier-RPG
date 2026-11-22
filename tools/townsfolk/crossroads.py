"""The Crossroads' people: the Horde's walled fort where the Barrens' roads meet (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." The Crossroads is the Barrens' hub, so it's a mid-size town: orcs mostly, tauren from Mulgore and
Taurajo, trolls, goblins on the caravans, and Earthborn who walked in off the plains. None of them gives a quest, sells
or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the War Hall
    ("xr_tf_hall_scribe", "Scribe Hollek", "orc", M, "The War Hall",
     "I write down every report the scouts bring in, and Sergra reads every word. The centaur raids are up this month, "
     "and so is my ink bill."),
    ("xr_tf_tower_watch", "Watcher Grusha", "orc", F, "The War Hall",
     "I stand the north tower and watch the plains for dust. Dust means riders, and riders mean centaur, and centaur "
     "mean I shout very loudly."),
    ("xr_tf_barracks_cook", "Cook Morg", "orc", M, "The War Hall",
     "I feed the whole garrison out of one pot, and nobody's ever complained to my face. Behind my back they call it "
     "Morg's Mystery, and I take that as a compliment."),
    # ---- the Stable Yard
    ("xr_tf_wolf_groom", "Groom Rakka", "orc", F, "The Stable Yard",
     "I brush down the riders' wolves when they come in off the plains, and they come in caked in red dust. The dust "
     "gets in my teeth, and I've stopped caring."),
    ("xr_tf_tauren_drover", "Drover Kele Plainstrider", "tauren", M, "The Stable Yard",
     "I drive kodo between the Crossroads and Taurajo, and the road's longer than it looks on any map. The kodos know "
     "it better than I do, so mostly I just walk beside them."),
    ("xr_tf_stable_child", "Little Brekka", "orc", F, "The Stable Yard",
     "I'm allowed to feed the wolves if I keep my fingers flat. My brother didn't keep his flat, and now he has nine, "
     "so I'm very careful."),
    # ---- the Trading Post
    ("xr_tf_caravan_master", "Caravan Master Nozz", "goblin", M, "The Trading Post",
     "My caravans run from Ratchet to Orgrimmar, and the Crossroads is where they rest. The orcs charge me a toll at the "
     "gate, and I charge them double for the goods, so we're all happy."),
    ("xr_tf_caravan_guard", "Guard Hulga", "orc", F, "The Trading Post",
     "I guard Nozz's caravans for coin, and I've fought off quilboar, centaur and one very angry kodo. The kodo was the "
     "hardest, and it wasn't even the kodo's fault."),
    ("xr_tf_troll_trader", "Juma", "troll", M, "The Trading Post",
     "I trade fish and voodoo charms from de coast for hides from de plains. De orcs buy de fish, and de tauren buy de "
     "charms, and nobody buys both, which I find very funny."),
    ("xr_tf_tauren_weaver", "Weaver Ayita", "tauren", F, "The Trading Post",
     "I sell blankets to the caravans for the cold nights on the plains. The goblins always try to bargain, and I always "
     "let them think they've won."),
    # ---- the Well
    ("xr_tf_water_carrier", "Gakka", "orc", F, "The Well",
     "I carry water from the well to the barracks forty times a day. The well's the only sweet water for a day's ride in "
     "any direction, and the whole fort lives or dies by it."),
    ("xr_tf_earth_engineer", "Femi Adeyemi", "human", M, "The Well",
     "I was a water engineer in Lagos, and now I'm helping the orcs dig a second well. They didn't believe the ground "
     "would give water there, and then it did, and now they listen to me."),
    ("xr_tf_bounty_reader", "Old Sharga", "orc", F, "The Well",
     "I read the bounty board out loud for the grunts who never learned their letters. I add a little to the stories, "
     "so the bounties sound more exciting than they are."),
    # ---- the Inn Yard
    ("xr_tf_inn_regular", "Grizzled Torvak", "orc", M, "The Inn Yard",
     "I've drunk at Boorka's every night for twenty years, and I've got a groove worn in the bench to prove it. Nobody "
     "else sits there, and I'd like to see them try."),
    ("xr_tf_bard", "Lutegrip Dorn", "orc", M, "The Inn Yard",
     "I sing the old songs of the clans in the inn yard every evening. The young grunts don't know the words, but they "
     "stamp along, and that's how songs live on."),
    ("xr_tf_earth_traveler", "Emma Fischer", "human", F, "The Inn Yard",
     "I was a hiking guide in Bavaria, and the Barrens are the biggest open country I've ever seen. I've walked most of "
     "it now, and I keep coming back here because Boorka's stew is worth the walk."),
    # ---- the Forge Corner
    ("xr_tf_forge_striker", "Striker Dugg", "orc", M, "The Forge Corner",
     "I hammer the arrowheads and spear points for the garrison, a hundred a day. My arm's bigger than my leg now, and "
     "my wife says I walk lopsided."),
    ("xr_tf_armourer_wife", "Hesha", "orc", F, "The Forge Corner",
     "I stitch the leather under the grunts' armour so it doesn't rub them raw. Nobody thanks me, but nobody comes back "
     "with blisters either, and that's thanks enough."),
    # ---- the Healers' Tents
    ("xr_tf_healer_aide", "Aide Morrowhoof", "tauren", F, "The Healers' Tents",
     "I help the healer bind wounds from the centaur raids. The orcs never cry out, not once, and I've decided that's "
     "the bravest and most foolish thing about them."),
    ("xr_tf_recovering_grunt", "Grunt Lokar", "orc", M, "The Healers' Tents",
     "A centaur arrow went through my leg, and the healer says I'll walk again in a week. I've told her I'll walk in "
     "three days, and she's told me to sit down."),
    ("xr_tf_goblin_patient", "Fizzy Brightwick", "goblin", F, "The Healers' Tents",
     "I burned my eyebrows off testing a new kind of lamp oil, and I'm here for the ointment. The lamp works great, and "
     "the eyebrows will grow back eventually."),
    # ---- the South Gate
    ("xr_tf_gate_grunt", "Grunt Vosh", "orc", M, "The South Gate",
     "I check every caravan coming in from the south road for stowaways. Last week I found a quilboar piglet in a crate "
     "of apples, and we kept it, and now it's the fort's mascot."),
    ("xr_tf_troll_wanderer", "Jin'zo", "troll", M, "The South Gate",
     "I sailed from Grom'gol and walked de whole plains to see de famous Crossroads. It's smaller "
     "dan I thought, mon, but de people are bigger."),
]
