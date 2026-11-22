"""Timbermaw Hold's people: a furbolg city that's been here longer than anyone's records (21 Nov 2026).

Kyle: "Also timbermaw hold is dead...for a capital city". Every quarter gets the furbolgs who live and work there:
elders and their keepers, the long hall's families, beekeepers, carvers and their apprentices, the market's traders
and gossips, the workshops' hands, the tunnel's watchers and the basin's crowd round the totem and the spring. A few
outsiders who've climbed the pass since the Integration are here too. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    ("th_tf_elder_attendant", "Bramblefur", "furbolg", M, "The Elders' Terrace",
     "Thirty winters the Great Lodge's fire has burned for the Elders under my care. Never once out, not even "
     "the night the deep gate shook."),
    ("th_tf_old_storyteller", "Grandmother Mossheart", "furbolg", F, "The Elders' Terrace",
     "Sit down, little one. My grandmother's grandmother told me how the Hold was dug, and I'll tell you if "
     "you've got the afternoon. It takes about that long, and the best part is at the end."),
    ("th_tf_shrine_tender", "Ashbrook", "furbolg", M, "The Elders' Terrace",
     "Every family in the Hold has a carving at the ancestor shrine, and honey gets set out for the ones who "
     "came before. Every name on every one is known to me."),
    ("th_tf_young_elder", "Thistlecoat", "furbolg", F, "The Elders' Terrace",
     "The Elders asked me to sit with them this season and listen, which is how you start learning to be one. "
     "Mostly I'm learning how long a furbolg can go without saying anything."),
    ("th_tf_hall_cook", "Mother Honeypaw", "furbolg", F, "The Long Hall",
     "The long hall feeds anyone who's hungry, and that's been true since before the tunnel was dug. Sit, eat,"
     " and don't tell me you're full, because I've heard that one before."),
    ("th_tf_hall_cubs", "Pip Brownfoot", "furbolg", M, "The Long Hall",
     "My big sister says outsiders don't have fur because they're always cold. Is that true? You can borrow my"
     " blanket if you like, it's the one with the bees on it."),
    ("th_tf_hall_stores", "Stout Burlbark", "furbolg", M, "The Long Hall",
     "Honey, dried fish, roots and grain, counted every evening. Two hard winters' worth, and three would let "
     "me sleep better."),
    ("th_tf_hall_weaver", "Fernwhisker", "furbolg", F, "The Long Hall",
     "A furbolg doesn't feel the cold much, but the outsiders who come up the pass do. The long hall's "
     "blankets are coming off my loom twice as fast now."),
    ("th_tf_hall_grandfather", "Old Rootclaw", "furbolg", M, "The Long Hall",
     "Too old for the walls now, so the hall door is where I sit and watch the young ones go up and down. "
     "Somebody ought to know who's coming and going."),
    ("th_tf_beekeeper", "Beekeeper Goldmane", "furbolg", F, "The Honey Terraces",
     "The hive-tree's bees have lived here as long as the Timbermaw have. Speak softly near the skeps, because"
     " they know every voice in the Hold and they'll want to know yours."),
    ("th_tf_honey_presser", "Waxpaw", "furbolg", M, "The Honey Terraces",
     "Everything in the Hold tastes a little of honey, and the press is why. Dawn to dusk all summer, and "
     "you're very welcome."),
    ("th_tf_bee_apprentice", "Little Clover", "furbolg", F, "The Honey Terraces",
     "Four stings this morning, and Beekeeper Goldmane says that means the bees like me. The nose has stopped "
     "swelling, at least."),
    ("th_tf_honey_trader", "Cask Hollowtree", "furbolg", M, "The Honey Terraces",
     "We send honey down the pass to the orcs now, and they send back salt and iron. My grandfather would "
     "never have believed it. He thought orcs only ate meat and trouble."),
    ("th_tf_carver_apprentice", "Shavings", "furbolg", M, "The Carvers' Quarter",
     "The carvers let me practise on their offcuts if I sweep their shavings. This one's meant to be a bear, "
     "and everyone says it's a lovely duck."),
    ("th_tf_totem_painter", "Ochrefur", "furbolg", F, "The Carvers' Quarter",
     "Clay, berries and ash, and recipes older than the Hold itself. The totems get their colour once the "
     "carvers are done."),
    ("th_tf_old_carver", "Old Knotwood", "furbolg", M, "The Carvers' Quarter",
     "Sixty years of totems, and the one in the square has waited twelve of them for its top. It'll be "
     "finished when I know what face it wants."),
    ("th_tf_carver_rival", "Splinterclaw", "furbolg", F, "The Carvers' Quarter",
     "Bennik thinks he's the best carver in the Hold, and he might be right, but don't tell him I said so. I "
     "carved the bears on the south gate, and nobody's complained about those."),
    ("th_tf_market_gossip", "Burdock Bristleback", "furbolg", M, "The Market",
     "Everything that comes up the pass passes this bench by the inn. Yesterday a goblin sold a shovel that "
     "digs by itself, and it didn't, and he left in a hurry."),
    ("th_tf_market_fisher", "Reedtail", "furbolg", F, "The Market",
     "Every third day, fish up from the streams below the pass. They're small and bony, and the long hall "
     "turns them into the best stew you've ever had."),
    ("th_tf_market_goblin", "Nix Sparkwhistle", "goblin", F, "The Market",
     "Came up to sell to the furbolgs and ended up buying everything instead. Have you tried the honey cakes? "
     "The trip down needs a bigger pack."),
    ("th_tf_market_orc", "Grunt Mordak", "orc", M, "The Market",
     "The envoy brought me up as his guard, and I spend most days carrying honey jars for the furbolg "
     "grandmothers. I'm not complaining. They feed me better than the barracks ever did."),
    ("th_tf_market_volunteer", "Sarah Lindqvist", "human", F, "The Market",
     "Outsiders climb the pass sick, and the Hold's healers needed another pair of hands. Gothenburg trained "
     "me as a nurse, and the furbolgs are the gentlest patients."),
    ("th_tf_market_cub", "Bumble", "furbolg", M, "The Market",
     "You're the first outsider through the gate today, so the bet with my cousin is mine. Mother thinks I've "
     "been helping at her stall all morning."),
    ("th_tf_tanner", "Hidewright Thornback", "furbolg", M, "The Workshops",
     "I tan the hides the hunters bring up, and I use every bit of the animal. It's an old promise between the"
     " Timbermaw and the forest, and we've kept it for a very long time."),
    ("th_tf_smith_helper", "Emberpaw", "furbolg", F, "The Workshops",
     "I work the bellows for the smith, and my arms are twice the size they were last spring. The Hold never "
     "used to need much iron. These days we can't make enough."),
    ("th_tf_herb_drier", "Sagecoat", "furbolg", F, "The Workshops",
     "I hang the herbs on the racks to dry and turn them every morning. Since the spring went green, the "
     "healers want golden sansam faster than it'll grow, and I can't dry it any quicker."),
    ("th_tf_rope_maker", "Twinefur", "furbolg", M, "The Workshops",
     "I make the rope for the walls and the climbing lines. Every lodge on the caldera hangs from something "
     "I've twisted, so I check my work twice. Then I check it again."),
    ("th_tf_tunnel_watcher", "Watcher Mossjaw", "furbolg", M, "The Tunnel Mouth",
     "I watch the tunnel mouth at night, the way my father did and his father before him. The tunnel used to "
     "go to four places. Now it goes to one, and I still watch all of it."),
    ("th_tf_tunnel_lamp", "Lampwick", "furbolg", F, "The Tunnel Mouth",
     "Dark in the first stretch of the tunnel even at noon, so the lamps get trimmed every day. The travellers"
     " from Felwood come out blinking like owls."),
    ("th_tf_tunnel_refugee", "Ashpelt", "furbolg", M, "The Tunnel Mouth",
     "My family came through the tunnel from the Felwood side when the Deadwood turned. We were lucky to get "
     "out. The Hold took us in without a single question, and I won't forget it."),
    ("th_tf_tunnel_runner", "Quickfoot", "furbolg", F, "The Tunnel Mouth",
     "I run messages through the tunnel to the galleries above Felwood. I've done it so many times I could run"
     " it with my eyes shut, and some nights I nearly do."),
    ("th_tf_bonfire_keeper", "Cinderhide", "furbolg", M, "The Basin",
     "The bonfire by the great totem burns every night, and the whole Hold comes down to sit by it when the "
     "work's done. Stay for it tonight. Someone always starts singing eventually."),
    ("th_tf_spring_washer", "Brightwater", "furbolg", F, "The Basin",
     "Since the spring went green, nobody touches it, and the Hold's linen gets washed with water carried up "
     "from the streams. My back hates every trip."),
    ("th_tf_totem_dancer", "Fawnfoot", "furbolg", F, "The Basin",
     "We dance round the great totem at every new moon, the whole Hold together. The steps are older than any "
     "song we know. My feet learned them before I could talk."),
    ("th_tf_deep_gate_worrier", "Old Grumblefur", "furbolg", M, "The Basin",
     "We sealed the deep gate in my grandfather's day, and I've lived my whole life walking past it. I don't "
     "like it open. I don't like any of this, and I've told the Elders so."),
    ("th_tf_basin_couple", "Hazelpaw", "furbolg", F, "The Basin",
     "My mate and I met at the bonfire forty summers ago. We still sit in the same spot every night, by the "
     "totem's left side. The young ones know to leave it for us."),
    ("th_tf_basin_tauren", "Tahna Swiftbrook", "tauren", F, "The Basin",
     "Mulgore sent me up the pass to learn how the furbolgs tend their spring. Their ways and ours are closer "
     "than either of us expected, and the Elders have been kind."),
    # ---- topped up to a capital's numbers (Kyle, 22 Nov 2026: "capitals can be 50+")
    ("th_tf_market_basketmaker", "Basketweave", "furbolg", F, "The Market",
     "Every basket in the Market was woven by my paws or my mother's, and some of hers are older than me. They hold honey, roots and gossip equally well."),
    ("th_tf_parcel_cub", "Little Acorn", "furbolg", M, "The Market",
     "The traders give me a honey drop if I carry their parcels across the Market. My teeth are very sticky, and my mother's very cross about it."),
    ("th_tf_basin_drummer", "Drummer Oakthump", "furbolg", M, "The Basin",
     "The drums by the totem sound at dawn and dusk, and the whole Hold hears them through the stone. My paws know the rhythm better than my head does."),
    ("th_tf_basin_spring_keeper", "Keeper Clearbrook", "furbolg", F, "The Basin",
     "The spring in the Basin gives the Hold its water, and it's been clean since the first furbolg drank from it. Keeping it clean is the oldest job we've got."),
    ("th_tf_hall_stewpot", "Cook Barleyclaw", "furbolg", F, "The Long Hall",
     "Supper in the Long Hall feeds every family that wants a bench, and most of them do. Mushroom stew, roasted roots and honey cakes, every night."),
    ("th_tf_hall_storyteller", "Old Tanglewhisker", "furbolg", M, "The Long Hall",
     "After supper, the cubs gather round my bench for a story, and they've heard them all. They still gasp at the right parts, which is very kind of them."),
    ("th_tf_elder_scribe", "Scribe Inkpaw", "furbolg", F, "The Elders' Terrace",
     "The Elders' words get carved into the terrace stone, never written on anything that rots. Some of the oldest carvings are worn smooth by paws."),
    ("th_tf_honey_smoker", "Smoker Hazelbee", "furbolg", M, "The Honey Terraces",
     "A little smoke calms the hives, and a lot of smoke angers them, and the difference is everything. Twenty years of stings taught me exactly where that line is."),
    ("th_tf_honey_cub", "Little Buzz", "furbolg", F, "The Honey Terraces",
     "The bees know me now, and they don't sting me any more, or not very often. Goldmane says that's the first step to becoming a beekeeper."),
    ("th_tf_acorn_carver", "Apprentice Chipclaw", "furbolg", M, "The Carvers' Quarter",
     "Old Knotwood makes me carve the same acorn a hundred times before I'm allowed a bear. Ninety-four acorns done, and my paws are very tired."),
    ("th_tf_workshop_tanner", "Tanner Thicket", "furbolg", F, "The Workshops",
     "Hides from the pass get cured in the workshops, slow and careful with oak bark. Rush it, and the leather cracks in the first winter, and everybody knows who did it."),
    ("th_tf_tunnel_trimmer", "Lamplighter Glowpaw", "furbolg", M, "The Tunnel Mouth",
     "The tunnel lamps get lit at dusk and trimmed at midnight, every one of them. Travellers who come in from the pass always thank the light first, then me."),
    ("th_tf_tunnel_earth_hiker", "Ingrid Solberg", "human", F, "The Tunnel Mouth",
     "A mountain guide from Tromso, and the furbolgs let me walk their pass with the watchers. They're the quietest climbers I've ever met, and the strongest."),
]
