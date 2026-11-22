"""Halcyon Rest's people: the waystation on the Great Sky River and Tethertown tied on below it (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and of the sky natives, "These people have lived here 1000s of years".
The Rest has fed travellers on the river for three hundred years, and since the Eighth Ring fell its pavilions are full
of the ring's people. Its gardeners, cooks and bell-keepers are Aetherians who've always lived here; the refugees are
Aetherians who never meant to; Tethertown's people are the Earthborn who woke on the islands. None of them gives a
quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Rest Gate
    ("hr_tf_bell_keeper", "Bell-Keeper Anwen Sorrel", "aetherian", F, "The Rest Gate",
     "I ring the gate bell when a traveller comes off the gangway, the way my mother did and hers before her. I rang it "
     "four times this morning, which is more than I rang it all last season."),

    # ---- the Guest Hall
    ("hr_tf_hall_cook", "Cook Merrin Ashvale", "aetherian", M, "The Guest Hall",
     "I cook for the Guest Hall and the pavilions both now, so the pot's three times the size it used to be. The "
     "refugees eat everything I put in front of them, and they thank me for it, which the old guests never did."),
    ("hr_tf_hall_scribe", "Lissa Vane", "aetherian", F, "The Guest Hall",
     "I keep the Rest's guest book, and it goes back to the first keeper's hand. Most of the names in it are travellers "
     "who stayed a night. This season they're mostly people who've got nowhere else to go."),

    # ---- the Pool Garden
    ("hr_tf_gardener", "Gardener Tamsin Holl", "aetherian", F, "The Pool Garden",
     "The silver trees round the pool were planted by the third keeper, and I've tended them since I was a girl. They "
     "drink from the wellstone like everything else here, and they've never once dropped a leaf out of season."),
    ("hr_tf_pool_elder", "Old Corwin Lake", "aetherian", M, "The Pool Garden",
     "I come and sit by the pool every afternoon because it's the only place on the river that's quiet. My knees "
     "ache, the young people talk too fast, and the water's the same as it was when I was born."),

    # ---- the Pavilions: the Eighth Ring's people
    ("hr_tf_ring_weaver", "Maela Ostrin", "aetherian", F, "The Pavilions",
     "I had a loom on the Eighth Ring, and a shop with a blue door. I got out with the shuttle in my apron pocket and "
     "nothing else. Keeper Ithren found me thread, so I'm weaving blankets for the pavilions."),
    ("hr_tf_ring_father", "Davor Kell", "aetherian", M, "The Pavilions",
     "My daughter asks me every night when we're going home, and I tell her the ring's resting. I haven't found a "
     "better answer yet. She's started helping the cook, so at least she's busy."),
    ("hr_tf_ring_girl", "Little Ysolde Kell", "aetherian", F, "The Pavilions",
     "Papa says our street's resting. I help the cook stir the soup, and he lets me ring the little bell when it's "
     "ready, and then everybody comes running like birds."),

    # ---- the Market Steps
    ("hr_tf_steps_porter", "Porter Gavin Thale", "aetherian", M, "The Market Steps",
     "I carry crates up from the skiff dock to the kiosks, and I've done it so long my feet know every step. The crates "
     "are lighter this year because there's less in them, and I don't like what that says about the river."),
    ("hr_tf_steps_haggler", "Ama Boateng", "human", F, "The Market Steps",
     "I sold fabric in Makola Market in Accra, and the haggling here is exactly the same, only slower and more polite. "
     "The Aetherians think I'm rude, and I think they're overpaying, so we get on very well."),

    # ---- the Skiff Dock
    ("hr_tf_dock_hand", "Dockhand Rennic Faye", "aetherian", M, "The Skiff Dock",
     "I hood the skiffs' crystals before they fly and unhood them when they land. It's a small job, but if I forget one, "
     "the old stones see it from three islands away, and then it's a short flight."),

    # ---- Tethertown: the Earthborn
    ("hr_tf_tether_student", "Tomasz Wrobel", "human", M, "Tethertown",
     "I was studying engineering in Krakow, and now I study rope, because that's what's holding my house to the sky. "
     "Gustavo says I'm getting good at knots. I'd rather be getting good at bridges."),
    ("hr_tf_tether_grandmother", "Nalani Kahale", "human", F, "Tethertown",
     "Ana and I are both from the islands back home, so we talk story by the fire in the evenings. I never thought I'd "
     "be living on an island again, and I certainly never thought it'd be floating."),
    # ---- 22 Nov 2026, Kyle: "Small towns can be 15-20" (the frontier feel)
    ("hr_tf_gate_lamplighter", "Lamplighter Odo Fenn", "aetherian", M, "The Rest Gate",
     "I light the crystal lamps along the gangway at dusk, all forty of them. The Eighth Ring's children follow me down "
     "the line every evening, and I've started letting them light the last one."),
    ("hr_tf_hall_sweeper", "Bettany Crane", "aetherian", F, "The Guest Hall",
     "I sweep the Guest Hall twice a day now, because twelve beds have turned into forty bedrolls. Nobody complains about "
     "the floor, and I've decided that's the nicest thing a guest has ever said to me."),
    ("hr_tf_ring_mason", "Halvard Ostrin", "aetherian", M, "The Pavilions",
     "I built walls on the Eighth Ring for thirty years, and now I'm building pavilion floors so the children don't "
     "sleep on the grass. Maela says I'm happier with a trowel than I ever was with a guild seal."),
    ("hr_tf_steps_fruit_seller", "Rhenna Lowe", "aetherian", F, "The Market Steps",
     "I bring fruit down from the Rest's orchards every morning and give half of it away by noon. The keeper says that's "
     "bad trade, and then he takes a pear without paying, so I don't listen to him."),
    ("hr_tf_tether_fisher", "Mateus Oliveira", "human", M, "Tethertown",
     "I fished off the coast of Bahia my whole life, and now I fish the sky river off the end of a rock. The fish up here "
     "have wings, and they're delicious, and I've stopped telling anyone back at the hearth how strange that is."),
]
