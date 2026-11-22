"""Hammerfall's people: the Horde's fortress in the Arathi Highlands (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." A war town: orcs of the garrison and their families, the Forsaken of the quarter by the apothecary, the
tauren envoy's people, and the goblins who supply all of them. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the War Hall
    ("hmf_tf_hall_scribe", "Scribe Grisha", "orc", F, "The War Hall",
     "Every report from the Arathi front gets read aloud in the war hall before it's copied. The overlord likes to hear the bad news twice, so he believes it."),
    ("hmf_tf_hall_guard", "Grunt Thokk", "orc", M, "The War Hall",
     "Twelve hours at the war hall's door, and the hardest part is the tauren envoy. She keeps offering me tea, and the overlord says guards don't drink tea."),
    ("hmf_tf_envoy_aide", "Aide Wenona Stillwater", "tauren", F, "The War Hall",
     "The High Envoy came from Thunder Bluff to remind the orcs that the Horde is more than an army. They listen, mostly, between drills."),
    # ---- the Forsaken Quarter
    ("hmf_tf_apoth_runner", "Runner Eldon Grave", "forsaken", M, "The Forsaken Quarter",
     "The apothecary's samples go out to the front in sealed jars, and they come back empty. Nobody asks what was in them, and nobody asks what happened."),
    ("hmf_tf_deathguard_wife", "Martha Olen", "forsaken", F, "The Forsaken Quarter",
     "My husband stands the Deathguard post, and I keep our little house in the quarter. We were married in Stromgarde, a long time and a whole death ago."),
    ("hmf_tf_forsaken_child", "Little Edwin", "forsaken", M, "The Forsaken Quarter",
     "The orc children won't play with me since my arm came off in the tug of war. The apothecary sewed it back on, so I don't see why they're upset."),
    # ---- the Muster Yard
    ("hmf_tf_drill_recruit", "Recruit Gorza", "orc", F, "The Muster Yard",
     "The sergeant drills us in the muster yard from dawn till our arms fall off. Then he drills us one-armed, because the Alliance won't wait for us to heal."),
    ("hmf_tf_muster_veteran", "Old Grommash's Tusk", "orc", M, "The Muster Yard",
     "Fought at Hammerfall when it was taken back, and the scar's still here to prove it. The recruits listen to my stories, and then they go and make their own."),
    ("hmf_tf_muster_drummer", "Drummer Krug", "orc", M, "The Muster Yard",
     "The war drum calls the garrison to muster, three beats for drill and five for battle. It's been three beats for a month now, and I'm grateful."),
    # ---- the War Yard
    ("hmf_tf_forge_striker", "Striker Brakka", "orc", F, "Hammerfall War Yard",
     "The war forge never cools, and neither do the arms swinging hammers in front of it. A hundred spearheads a day, and the front wants two hundred."),
    ("hmf_tf_armoury_clerk", "Clerk Varn", "orc", M, "Hammerfall War Yard",
     "Every axe, shield and helm in the armoury is numbered and signed for. The grunts lose them anyway, and somehow it's always my fault."),
    ("hmf_tf_tanner_hand", "Tanner's Mate Ogra", "orc", F, "Hammerfall War Yard",
     "The tannery hall smells worse than the battlefield, the grunts say. They wear the leather anyway, and it's never once split on them."),
    ("hmf_tf_smokehouse", "Smoker Durk", "orc", M, "Hammerfall War Yard",
     "Raptor and boar smoked in the smokehouse, enough to feed a war band for a week. The scouts say they can smell Hammerfall from the Alliance lines."),
    # ---- the Market Row
    ("hmf_tf_goblin_supplier", "Supplier Grizzik", "goblin", M, "Hammerfall Market Row",
     "Nails, rope, lamp oil and arrowheads, all at war prices. The overlord complains about the cost, and then he orders more, because nobody else delivers."),
    ("hmf_tf_brew_hand", "Brewer's Girl Zuka", "orc", F, "Hammerfall Market Row",
     "The brew house makes the strongest grog in the highlands, and the garrison drinks it every night. On drill days, they drink it twice."),
    ("hmf_tf_market_haggler", "Old Mother Karsh", "orc", F, "Hammerfall Market Row",
     "Every merchant on the market row gets argued with, every day, about every price. They've learned to start high, and I've learned to start loud."),
    ("hmf_tf_supply_porter", "Porter Hrag", "orc", M, "Hammerfall Market Row",
     "Every crate that comes up from the supply store goes somewhere on my back. The goblins pack them, and the goblins never have to carry them."),
    ("hmf_tf_earth_medic", "Dr. Sam Okafor", "human", M, "Hammerfall Market Row",
     "An emergency doctor from Lagos, patching up orcs who think stitches are optional. They're the toughest patients alive, and the worst at sitting still."),
    # ---- the Wind Rider Roost
    ("hmf_tf_roost_feeder", "Feeder Gak", "orc", M, "The Wind Rider Roost",
     "The wind riders get fed before the soldiers, the stablemaster says, because the wind riders bite harder. He's right about that."),
    ("hmf_tf_kennel_keeper", "Kennel-Keeper Ruga", "orc", F, "The Wind Rider Roost",
     "The war wolves in the kennel block know every grunt by smell, and they like most of them. The ones they don't like learn quickly to walk round."),
    ("hmf_tf_totem_tender", "Tender Moshka", "orc", F, "The Wind Rider Roost",
     "The great totem by the roost carries the names of every orc who died retaking Hammerfall. A name gets carved for every one, and there's still room."),
    ("hmf_tf_officer_wife", "Lady Garra", "orc", F, "The Wind Rider Roost",
     "My husband's an officer, which means our house has a door that shuts. That's the whole of the privilege, and it's worth it."),
    ("hmf_tf_tauren_drover", "Drover Tahoma", "tauren", M, "The Wind Rider Roost",
     "Kodos haul supplies up from the Barrens road to Hammerfall, and somebody has to walk with them. The orcs don't understand kodos, and the kodos don't understand orcs."),
    ("hmf_tf_watch_grunt", "Watcher Barga", "orc", F, "The Muster Yard",
     "From the watchtowers by the gate, you can see the highland road for leagues. Nothing's come up it with a banner in a month, and the quiet makes everyone nervous."),
    ("hmf_tf_forsaken_scholar", "Scholar Adela Whitcombe", "forsaken", F, "The Forsaken Quarter",
     "Stromgarde's libraries were the finest in the highlands, and I read every book in them before I died. Now I read the orcs' battle reports, and the prose is worse."),
]
