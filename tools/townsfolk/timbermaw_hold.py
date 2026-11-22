"""Timbermaw Hold's people: a furbolg city that's been here longer than anyone's records (21 Nov 2026).

Kyle: "Also timbermaw hold is dead...for a capital city". Every quarter gets the furbolgs who live and work there:
elders and their keepers, the long hall's families, beekeepers, carvers and their apprentices, the market's traders
and gossips, the workshops' hands, the tunnel's watchers and the basin's crowd round the totem and the spring. A few
outsiders who've climbed the pass since the Integration are here too. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Elders' Terrace
    ("th_tf_elder_attendant", "Bramblefur", "furbolg", M, "The Elders' Terrace",
     "I keep the Great Lodge's fire for the Elders, and I've kept it lit for thirty winters. It's never gone out, not "
     "once, not even the night the deep gate shook."),
    ("th_tf_old_storyteller", "Grandmother Mossheart", "furbolg", F, "The Elders' Terrace",
     "Sit down, little one. My grandmother's grandmother told me how the Hold was dug, and I'll tell you if you've got "
     "the afternoon. It takes about that long, and the best part is at the end."),
    ("th_tf_shrine_tender", "Ashbrook", "furbolg", M, "The Elders' Terrace",
     "I sweep the ancestor shrine and set out honey for the ones who came before. Every family in the Hold has a "
     "carving here, and I know the name on every one of them."),
    ("th_tf_young_elder", "Thistlecoat", "furbolg", F, "The Elders' Terrace",
     "The Elders asked me to sit with them this season and listen, which is how you start learning to be one. Mostly "
     "I'm learning how long a furbolg can go without saying anything."),

    # ---- the Long Hall
    ("th_tf_hall_cook", "Mother Honeypaw", "furbolg", F, "The Long Hall",
     "The long hall feeds anyone who's hungry, and that's been true since before the tunnel was dug. Sit, eat, and "
     "don't tell me you're full, because I've heard that one before."),
    ("th_tf_hall_cubs", "Pip Brownfoot", "furbolg", M, "The Long Hall",
     "My big sister says outsiders don't have fur because they're always cold. Is that true? You can borrow my "
     "blanket if you like, it's the one with the bees on it."),
    ("th_tf_hall_stores", "Stout Burlbark", "furbolg", M, "The Long Hall",
     "I count the Hold's stores every evening: honey, dried fish, roots and grain. We've got enough for two hard "
     "winters, and I'd sleep better if it were three."),
    ("th_tf_hall_weaver", "Fernwhisker", "furbolg", F, "The Long Hall",
     "I weave the blankets for the long hall's sleepers. A furbolg doesn't feel the cold much, but the outsiders "
     "who've come up the pass do, so I've been weaving twice as many."),
    ("th_tf_hall_grandfather", "Old Rootclaw", "furbolg", M, "The Long Hall",
     "I'm too old to climb the walls now, so I sit by the hall door and watch the young ones go up and down. I like "
     "to know who's coming and going. Somebody ought to."),

    # ---- the Honey Terraces
    ("th_tf_beekeeper", "Beekeeper Goldmane", "furbolg", F, "The Honey Terraces",
     "The hive-tree's bees have lived here as long as the Timbermaw have. Speak softly near the skeps, because they "
     "know every voice in the Hold and they'll want to know yours."),
    ("th_tf_honey_presser", "Waxpaw", "furbolg", M, "The Honey Terraces",
     "I work the honey press from dawn to dusk in the summer. Everything in the Hold tastes a little of honey, and "
     "that's my doing, so you're very welcome."),
    ("th_tf_bee_apprentice", "Little Clover", "furbolg", F, "The Honey Terraces",
     "I got stung four times this morning, and Beekeeper Goldmane says that means the bees like me. I'm not sure I "
     "believe her, but my nose has stopped swelling."),
    ("th_tf_honey_trader", "Cask Hollowtree", "furbolg", M, "The Honey Terraces",
     "We send honey down the pass to the orcs now, and they send back salt and iron. My grandfather would never have "
     "believed it. He thought orcs only ate meat and trouble."),

    # ---- the Carvers' Quarter
    ("th_tf_carver_apprentice", "Shavings", "furbolg", M, "The Carvers' Quarter",
     "I sweep up the carvers' shavings and they let me practise on the offcuts. This one's meant to be a bear. "
     "Everyone keeps telling me it's a lovely duck."),
    ("th_tf_totem_painter", "Ochrefur", "furbolg", F, "The Carvers' Quarter",
     "I paint the totems once the carvers are done with them. The colours come from clay, berries and ash, and the "
     "recipes are older than the Hold itself."),
    ("th_tf_old_carver", "Old Knotwood", "furbolg", M, "The Carvers' Quarter",
     "I've carved totems for sixty years, and that unfinished one in the square has been waiting for its top for "
     "twelve of them. I'll finish it when I know what face it wants."),
    ("th_tf_carver_rival", "Splinterclaw", "furbolg", F, "The Carvers' Quarter",
     "Bennik thinks he's the best carver in the Hold, and he might be right, but don't tell him I said so. I carved "
     "the bears on the south gate, and nobody's complained about those."),

    # ---- the Market
    ("th_tf_market_gossip", "Burdock Bristleback", "furbolg", M, "The Market",
     "I sit by the inn and hear everything that comes up the pass. Yesterday it was a goblin selling a shovel that "
     "digs by itself. It didn't, and he left in a hurry."),
    ("th_tf_market_fisher", "Reedtail", "furbolg", F, "The Market",
     "I bring fish up from the streams below the pass every third day. They're small and bony, but the long hall "
     "turns them into the best stew you've ever had."),
    ("th_tf_market_goblin", "Nix Sparkwhistle", "goblin", F, "The Market",
     "I came up here to sell to the furbolgs and I ended up buying everything instead. Have you tried the honey "
     "cakes? I'm going to need a bigger pack for the trip down."),
    ("th_tf_market_orc", "Grunt Mordak", "orc", M, "The Market",
     "The envoy brought me up as his guard, and I spend most days carrying honey jars for the furbolg grandmothers. "
     "I'm not complaining. They feed me better than the barracks ever did."),
    ("th_tf_market_volunteer", "Sarah Lindqvist", "human", F, "The Market",
     "I was a nurse in Gothenburg, and now I help the Hold's healers with the outsiders who climb the pass sick. The "
     "furbolgs are the gentlest patients I've ever had."),
    ("th_tf_market_cub", "Bumble", "furbolg", M, "The Market",
     "I'm supposed to be helping my mother at her stall, but I've been watching the gate all morning. You're the "
     "first outsider today, so I win the bet with my cousin."),

    # ---- the Workshops
    ("th_tf_tanner", "Hidewright Thornback", "furbolg", M, "The Workshops",
     "I tan the hides the hunters bring up, and I use every bit of the animal. It's an old promise between the "
     "Timbermaw and the forest, and we've kept it for a very long time."),
    ("th_tf_smith_helper", "Emberpaw", "furbolg", F, "The Workshops",
     "I work the bellows for the smith, and my arms are twice the size they were last spring. The Hold never used to "
     "need much iron. These days we can't make enough."),
    ("th_tf_herb_drier", "Sagecoat", "furbolg", F, "The Workshops",
     "I hang the herbs on the racks to dry and turn them every morning. Since the spring went green, the healers want "
     "golden sansam faster than it'll grow, and I can't dry it any quicker."),
    ("th_tf_rope_maker", "Twinefur", "furbolg", M, "The Workshops",
     "I make the rope for the walls and the climbing lines. Every lodge on the caldera hangs from something I've "
     "twisted, so I check my work twice. Then I check it again."),

    # ---- the Tunnel Mouth
    ("th_tf_tunnel_watcher", "Watcher Mossjaw", "furbolg", M, "The Tunnel Mouth",
     "I watch the tunnel mouth at night, the way my father did and his father before him. The tunnel used to go to "
     "four places. Now it goes to one, and I still watch all of it."),
    ("th_tf_tunnel_lamp", "Lampwick", "furbolg", F, "The Tunnel Mouth",
     "I trim the lamps along the first stretch of the tunnel. It's dark in there even at noon, and the travellers "
     "from Felwood come out blinking like owls."),
    ("th_tf_tunnel_refugee", "Ashpelt", "furbolg", M, "The Tunnel Mouth",
     "My family came through the tunnel from the Felwood side when the Deadwood turned. We were lucky to get out. "
     "The Hold took us in without a single question, and I won't forget it."),
    ("th_tf_tunnel_runner", "Quickfoot", "furbolg", F, "The Tunnel Mouth",
     "I run messages through the tunnel to the galleries above Felwood. I've done it so many times I could run it "
     "with my eyes shut, and some nights I nearly do."),

    # ---- the Basin
    ("th_tf_bonfire_keeper", "Cinderhide", "furbolg", M, "The Basin",
     "The bonfire by the great totem burns every night, and the whole Hold comes down to sit by it when the work's "
     "done. Stay for it tonight. Someone always starts singing eventually."),
    ("th_tf_spring_washer", "Brightwater", "furbolg", F, "The Basin",
     "I used to wash the Hold's linen in the spring every morning. We don't touch it now, not since it went green. I "
     "carry water up from the streams instead, and my back hates me for it."),
    ("th_tf_totem_dancer", "Fawnfoot", "furbolg", F, "The Basin",
     "We dance round the great totem at every new moon, the whole Hold together. The steps are older than any song "
     "we know. My feet learned them before I could talk."),
    ("th_tf_deep_gate_worrier", "Old Grumblefur", "furbolg", M, "The Basin",
     "We sealed the deep gate in my grandfather's day, and I've lived my whole life walking past it. I don't like it "
     "open. I don't like any of this, and I've told the Elders so."),
    ("th_tf_basin_couple", "Hazelpaw", "furbolg", F, "The Basin",
     "My mate and I met at the bonfire forty summers ago. We still sit in the same spot every night, by the totem's "
     "left side. The young ones know to leave it for us."),
    ("th_tf_basin_tauren", "Tahna Swiftbrook", "tauren", F, "The Basin",
     "I came up the pass from Mulgore to learn how the furbolgs tend their spring. Their ways and ours are very "
     "close, closer than either of us expected, and the Elders have been kind."),
]
