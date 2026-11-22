"""Keelstone's people: the Anchor-Wardens' hold at the foot of the First Anchor (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and of the sky natives, "These people have lived here 1000s of years".
The wardens have kept the anchors for a thousand years, and their families have lived round the First Anchor's foot for
as long: chain-greasers, gauge-readers, cooks, apprentices, the old wardens who sit in the court and argue. The House of
Measures' clerks copy records in the annex, and Tiltside's Earthborn have a corner of their own below the market. None
of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Chain Yard
    ("kl_tf_chain_greaser", "Ostrel Brand", "aetherian", M, "The Chain Yard",
     "I grease the First Anchor's chains, a link a day, and it takes me four years to get round them all. My father did "
     "it before me, and he said the chains talk if you listen. Mostly they creak, if I'm honest."),
    ("kl_tf_apprentice", "Apprentice Wren Calloway", "aetherian", F, "The Chain Yard",
     "I'm learning to read the gauges, and Engineer Pell says I've got the hands for it. The First Anchor's needle "
     "hasn't moved since I started. I check it every hour anyway, because that's the job."),
    ("kl_tf_yard_elder", "Old Haskel Dunmere", "aetherian", M, "The Chain Yard",
     "I forged links for the Third Anchor when I was young, and now they're the ones slipping. I don't think it's my "
     "work that's failing. I think the anchor's just tired, the way I am."),

    # ---- the Wardens' Hall
    ("kl_tf_young_warden", "Warden Corra Feld", "aetherian", F, "The Wardens' Hall",
     "I took my oath in that hall last spring, and I've stood my first watch at the Slipping Anchor since. Everyone told "
     "me the anchors never fail. Nobody told me what to do when one does."),
    ("kl_tf_court_arguer", "Warden Emeric Sallow", "aetherian", M, "The Wardens' Hall",
     "I've argued with Ebbe about the Dropfield in this court every evening for thirty years. He says the island fell "
     "because the chains broke, and I say the chains broke because the island fell. We're both getting older, and "
     "neither of us is getting any less certain."),

    # ---- the Anchor Market
    ("kl_tf_baker", "Baker Lisane Holt", "aetherian", F, "The Anchor Market",
     "I bake the wardens' bread before the morning watch goes out, so I'm up before the chains are. The Earthborn "
     "taught me something they call a bagel. The wardens pretend they don't like it, and they eat every one."),
    ("kl_tf_market_child", "Little Teo Holt", "aetherian", M, "The Anchor Market",
     "Mama bakes and I carry the baskets. When I'm big I'm going to be a warden and grease the chains like Ostrel, "
     "because he gets to climb the highest of anybody."),
    ("kl_tf_well_keeper", "Mother Ilse Rann", "aetherian", F, "The Anchor Market",
     "This well's drawn from the same wellstone since before the hall was built, and it's never once run dry. When "
     "people worry about the anchors, I tell them to come and drink, and most of them feel better."),

    # ---- the Measures' Annex
    ("kl_tf_annex_clerk", "Clerk Pellan Rook", "aetherian", M, "The Measures' Annex",
     "I copy the House of Measures' readings for the wardens, every number twice, in case one of us is wrong. Lately "
     "the numbers from the Listing Isle make me want to copy them three times."),
    ("kl_tf_annex_student", "Selva Ardent", "aetherian", F, "The Measures' Annex",
     "I came down from the Observatory to study the wardens' gauges, and I've stayed a whole season. The house measures "
     "the shelf from the stars, and the wardens measure it from the chains. They don't always agree."),

    # ---- the Tilt Quarter
    ("kl_tf_tilt_carpenter", "Rafael Mendes", "human", M, "The Tilt Quarter",
     "I built houses in Recife, and on the Listing Isle I built them crooked on purpose so they'd stand level. Up here "
     "I'm learning to build them straight again. My hands keep wanting to lean everything."),
    ("kl_tf_tilt_teacher", "Ingrid Solberg", "human", F, "The Tilt Quarter",
     "I taught maths in Tromso, so Bartosz brings me his tilt numbers every morning and I check his sums. The wardens' "
     "children have started coming to my lessons too, and they're quicker than mine ever were."),

    # ---- the Gate Stair
    ("kl_tf_stair_porter", "Porter Dain Merrow", "aetherian", M, "The Gate Stair",
     "I carry the wardens' supplies up the gangway from the plaza, sixty steps, twelve times a day. My cousin keeps the "
     "skiff landing on Crashfall. He says I've got the easier job, and I say he's never carried a crate of chain grease."),
]
