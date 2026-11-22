"""Lenswatch's people: the House of the Patient Lens's survey town, anchored off the Sunward Crown (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated". The survey towed an island down to the tree and lives on it: scholars,
their clerks and apprentices, the crew of the survey ship, the guesthouse's staff, and the survey's guests from Earth on
the Annex's rock. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Landing
    ("lw_tf_cargo_hand", "Cargo Hand Tobias Venn", "aetherian", M, "The Landing",
     "I unload whatever comes over the gangway from the crown, and lately it's mostly trolls with questions. They're "
     "polite enough once they've decided you're not going to shoot them. I've decided the same about them."),

    # ---- the Guesthouse
    ("lw_tf_guest_maid", "Calla Wren", "aetherian", F, "The Guesthouse",
     "The House built the guesthouse for visitors from the ground, and for two years nobody came. Now every bed's full, "
     "and half the guests sleep on the floor because they don't trust a bed that soft."),
    ("lw_tf_guest_cook", "Cook Hollis Brand", "aetherian", M, "The Guesthouse",
     "I cook for the guests, and the guests eat things I'd never have put in a pot. A troll asked me for roasted beetles "
     "yesterday, and I made them, and he said they were the best he'd had. I'm not sure how I feel about that."),

    # ---- the Survey Court
    ("lw_tf_apprentice", "Apprentice Lira Dell", "aetherian", F, "The Survey Court",
     "I polish the great lens every morning, which sounds grander than it is. It takes four hours and a ladder. The "
     "Lensmaster says I'll get to look through it when I've polished it a thousand times."),
    ("lw_tf_court_clerk", "Clerk Anton Pell", "aetherian", M, "The Survey Court",
     "I write down everything the survey sees through the lens, and since the seal cracked it's been a lot. Yesterday I "
     "filled forty pages about the trolls' cooking fires. The House will want every one of them."),

    # ---- the Skiff Roost
    ("lw_tf_roost_hand", "Roost Hand Maren Oss", "aetherian", F, "The Skiff Roost",
     "I hood the skiffs before they fly down to the troll city, so the old stones don't see them. Every pilot who comes "
     "back thanks me, and every pilot who doesn't, I think about."),

    # ---- the Mooring
    ("lw_tf_ship_boy", "Deckhand Teo Marsh", "aetherian", M, "The Mooring",
     "I scrub the survey ship's deck, and the shipmaster says that's how every captain started. He also says I scrub "
     "like a scholar, which I think was meant as an insult."),
    ("lw_tf_rigger", "Rigger Sela Cord", "aetherian", F, "The Mooring",
     "We towed this whole island down behind the ship, and I tied every line that did the towing. If the island ever "
     "drifts, it'll be my knots they blame, so I check them twice a day."),

    # ---- the Lens Hall
    ("lw_tf_hall_scribe", "Scribe Orrin Vale", "aetherian", M, "The Lens Hall",
     "I copy Archivist Sarre's rubbings of the seal into the House's books. I can't read the Kharad marks, so I copy "
     "them like drawings. My hand shakes on the ones he says mean danger."),

    # ---- the Annex
    ("lw_tf_annex_painter", "Mei Lin Chou", "human", F, "The Annex",
     "I painted murals in Taipei, and the scholars have given me a whole wall of the Annex to paint. I'm painting the "
     "view from my old apartment. They keep asking me which of the buildings could fly."),
    ("lw_tf_annex_mechanic", "Joao Batista", "human", M, "The Annex",
     "I fixed buses in Salvador, and now I fix the survey's carts. They float, which makes the wheels easy. Everything "
     "else is exactly as broken as a bus."),
    ("lw_tf_annex_kid", "Little Aiyana Redcloud", "human", F, "The Annex",
     "My dad says we live on a rock tied to a bigger rock. I've counted the ropes and there are nine. Pavel says nine is "
     "plenty, and Pavel builds bridges, so I believe him."),
    # ---- 22 Nov 2026, Kyle: "Small towns can be 15-20 ... cities lean towards one or two races but not exclusive"
    ("lw_tf_landing_porter", "Porter Edvin Sall", "aetherian", M, "The Landing",
     "I carry the survey's crates up from the gangway, and every one of them is full of instruments that hum. The "
     "scholars say they're delicate, so I carry them slowly and complain loudly."),
    ("lw_tf_court_gardener", "Gardener Ilka Rowe", "aetherian", F, "The Survey Court",
     "I keep the court's pools clear, and the trolls who come to the parley like to sit by them. They don't talk to me "
     "much, but one of them left me a carved bead yesterday, and I've put it by the water."),
    ("lw_tf_annex_geologist", "Hamid Karimi", "human", M, "The Annex",
     "I studied rocks in Tabriz, and now the survey has me looking at a rock that floats. The scholars ask me what I "
     "think, and I tell them, and then we both stare at it for an hour."),
    ("lw_tf_troll_visitor", "Spear Ulaka", "troll", F, "The Mooring",
     "The war-leader sent me down from Spearhold to watch the sky people, and they gave me tea. I'm still watching, "
     "mon, but the tea's good, so I'm watching from a chair."),
    ("lw_tf_orc_attendant", "Grosh Ironmane", "orc", M, "The Guesthouse",
     "I came up with the Warchief's envoy, and my job is to stand behind him and look patient. I'm better at it than "
     "the envoy is, and he knows it, so he lets me sit down when nobody's looking."),
]
