"""Dawnspear Wreck's people: the deserters' town in the broken war-skiff (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated". The Dawnspear's crew came down with her when Captain Marrane refused to
fire on Tethertown, and the town grew round them: crew who stayed, deserters who followed, free-skiff hands, a few
families who got out of Aurelion's lower rings. Aetherians, nearly all of them, and one Earthborn who walked in off the
Ashwake. None of them gives a quest or sells anything.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Gangway
    ("dw_tf_gangway_kid", "Pip Halloran", "aetherian", M, "The Gangway",
     "I run messages from the gangway to the captain, because I'm fastest. I've counted every plank on the gangway, "
     "and there are forty-two, and three of them squeak if you step on the left side."),

    # ---- the Stern Mess
    ("dw_tf_mess_hand", "Tobin Weir", "aetherian", M, "The Stern Mess",
     "I peeled roots for the Dawnspear's mess when she was flying, and I peel them now she's lying down. The steward "
     "says the stew tastes better since we stopped saluting before supper. I think she's right."),
    ("dw_tf_mess_widow", "Ama Corriden", "aetherian", F, "The Stern Mess",
     "My husband was a gunner on the Dawnspear. He was on the deck when she came down, and he didn't get up. The captain "
     "found me a bunk here and never once asked me to forgive her, which is why I have."),

    # ---- the Sail Market
    ("dw_tf_sailmender", "Sailmender Ottilie Brae", "aetherian", F, "The Sail Market",
     "These awnings were the Dawnspear's mainsail. I cut it into eight pieces with the knife I used to mend it, and I "
     "cried the whole time. It keeps the rain off the market now, which is a better job than the one it had."),
    ("dw_tf_market_haggler", "Ferris Aldane", "aetherian", M, "The Sail Market",
     "Everything here was salvaged off the wreck or stolen off the slipways, and everybody knows which, so nobody asks. If "
     "you need a bronze rivet or a crystal hood, I've got one, and I won't tell you where it came from."),

    # ---- the Bow
    ("dw_tf_bow_watch", "Deckhand Sorrel Vey", "aetherian", F, "The Bow",
     "I stand the second watch on the bow with the lookout, and I count the warships on the slipways every evening. "
     "Last month there were four, and tonight there are five. I'd rather the number went the other way."),
    ("dw_tf_old_bosun", "Old Bosun Garrick", "aetherian", M, "The Bow",
     "I served on the Dawnspear for thirty years, longer than the captain. When she gave the order to bring her down, "
     "I was the first to say aye. I'd say it again tomorrow, and my knees would complain just the same."),

    # ---- the Sickbay
    ("dw_tf_orderly", "Orderly Mira Caskel", "aetherian", F, "The Sickbay",
     "I boil the bandages and I hold people still while the surgeon works. The worst ones come in from the pens with "
     "crystal burns, carried across the causeway at night. We don't sleep much when the hounds are out."),
    ("dw_tf_patient", "Hollan Drace", "aetherian", M, "The Sickbay",
     "I lost two fingers on the slipways before I ran. The surgeon says the rest of my hand will be fine, and I believe "
     "her, because she's the first person in years who's told me the truth about anything."),

    # ---- the Lance Yard
    ("dw_tf_lance_recruit", "Jory Tallis", "aetherian", M, "The Lance Yard",
     "Tavin's teaching me to use a lance on the dummies, and he says the first thing to learn is when to put it down. "
     "I thought he was joking, but he makes us practise laying it on the ground before anything else."),
    ("dw_tf_lance_veteran", "Lancer Brisa Ondal", "aetherian", F, "The Lance Yard",
     "I flew with Tavin's wing, and I put my lance down the day after he did. Most of the others didn't. I still dream "
     "about the ones who stayed, and I hope they're dreaming about us."),

    # ---- the Skiff Moorings
    ("dw_tf_skiff_hand", "Kesta Lune", "aetherian", F, "The Skiff Moorings",
     "My uncle keeps the docks in Aurelion, and he's the reason the free skiffs fly at all. I tie them off when they "
     "land and I check their hoods before they leave. One loose hood and the fort's guns find you."),
    ("dw_tf_earthborn_walker", "Kwame Asante", "human", M, "The Skiff Moorings",
     "I woke up in the Ashwake three years ago and walked through the smoke until I found the wreck. I drove a taxi in "
     "Kumasi for twelve years, so I know how to find my way through anything. Now I help the skiff hands load cargo."),
    # ---- 22 Nov 2026, Kyle: "Small towns can be 15-20" (the frontier feel)
    ("dw_tf_gangway_guard", "Deckhand Yorin Pell", "aetherian", M, "The Gangway",
     "I stand the gangway watch because the captain asked me to, and I'd stand it if she hadn't. She put this ship down "
     "on purpose to keep it off those people, and I'll keep it standing now."),
    ("dw_tf_mess_cook", "Cook Hanne Ostby", "aetherian", F, "The Stern Mess",
     "I cooked for the Ascendancy's officers, and now I cook for anybody who sits down. The stew's the same, but the "
     "company's better, and nobody salutes me for the second bowl."),
    ("dw_tf_market_tinker", "Tinker Rolf Ashby", "aetherian", M, "The Sail Market",
     "I take the broken fittings off the wreck and make them into something useful. A lance mount makes a fine lantern "
     "hook, and I've sold eleven of them to people who'd never have bought a lance."),
    ("dw_tf_sickbay_volunteer", "Marla Hale", "aetherian", F, "The Sickbay",
     "I wasn't a healer before the crash, I sold ribbons in the Bastions. Surgeon Nell needed hands, so now I roll "
     "bandages and hold people's hands while she works, and I'm better at it than I expected."),
    ("dw_tf_earthborn_carpenter", "Tomas Ibarra", "human", M, "The Bow",
     "I built fishing boats in Valparaiso, and this is the biggest boat I've ever worked on, even upside down in a "
     "field. The crew think I'm mad for whistling while I patch the hull, and they might be right."),
]
