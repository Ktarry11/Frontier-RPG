"""Arathi in the plain voice (17 Nov 2026). Already near the bar: a few uncontracted lines, dashes, short closing
lines, and one accept text where a direction line had been pasted twice. The troll dialect stays. Same stories, same
directions."""

VOICE = {
    "arw_the_gap": (
        None,
        None,
        "I've got the slips, and all of them agree with my book.\n\nEighteen months I've been doing this, and it turns out I've been doing it correctly. I didn't expect that to feel like anything, and it does.",
    ),
    "arw_adder_season": (
        None,
        "Bring me adder glands, and whatever bruiseweed you can pull on the way. The weed grows along the road cuts, and you'll walk past it whether you're looking or not.\n\nAnd keep the bruiseweed. I need to see it, not take it off you. I don't rob people who do me favours. That's the Syndicate's business model.",
        None,
    ),
    "arw_the_overseer": (
        None,
        None,
        "You got the leaves, and the house is in uproar, which is what I wanted.\n\nThe farmers get to keep farming either way, which was never going to change and was never the point. The point is that somebody in Alterac now has to explain a gap in the accounts, and they're welcome to try.",
    ),
    "arw_what_veska_hears": (
        None,
        "Bring me the charms, and I want them lifted where they lie, so I can see which way each one faced. Don't go for the harbinger. She isn't the question.\n\nThe question is why a village would spend a year listening to itself.\n\nThe charms hang in Witherbark Hollow, north-east across the moor, and the shadowcasters carry the rest.",
        None,
    ),
    "arc_the_refuge_road": (
        None,
        None,
        "You've dealt with the maulers and the stone ones, and the road is a road again for about a fortnight.\n\nI'm not going to say I told them so. I'm going to carry this report myself and put it in the Overlord's hand and stand there while he reads it.",
    ),
    "arc_the_bound": (
        None,
        "Bring me their cores. They have a stone at the centre, and it isn't the same stone as the rest of them. It's ring stone, off the circles, and that's a fact I'd like several of rather than one.\n\nAnd go back to the fourth ring afterwards, the one east of here, below Hammerfall. Three of those circles are quiet. The fourth isn't, and I want you to have the cores in your hand when you stand in it.",
        None,
    ),
    "arc_the_mere": (
        None,
        "Bring me their bladders intact, and intact is the word that matters. They rupture if you're careless, and what's inside them is the entire sample.\n\nI'm not asking you to be brave. I'm asking you to be slow. Bravery has cost me two couriers and no data.",
        None,
    ),
    "arc_the_silt_mother": (
        None,
        "I want pearls off the bed, and a good look at what's in the middle.\n\nThese are freshwater pearls, in a mere. Something on the bed is making them, and making them in rows, and I'd very much like to know whether the rows mean anything, or whether I'm a man who's been alone with a pond for too long.",
        None,
    ),
    "arc_dry_the_brood": (
        None,
        "I want some of their shells and a look at the sump. I want the shells because a shell tells you the temperature it was laid at, and I want the sump because the sump is where the heat is coming from.\n\nThe Pick-Mother will be between you and both. I'm sorry about that, and I'm going to ask you to do it anyway.\n\nIt's Drywhisker Deeps, in the gorge south-east of Hammerfall. The warm gallery is past the diggings.",
        None,
    ),
    "arc_dry_below": (
        None,
        None,
        "They're offerings, and they were arranged, and arranged is a word I've been avoiding since the Envoy first used it about the pearls in the mere.\n\nThat's Drywhisker finished, and it isn't Arathi finished. Rest, and eat something. Then go east, and when you get to the coast, find a bosun called Tidewright and tell him Hammerfall sent you.",
    ),
    "are_they_are_holding": (
        None,
        "Bring me their watch orders, off different islands. I want to see whether the same hand wrote them.\n\nIf it's separate captains improvising, they're squatters and we can wait them out. If it's one hand, there's a plan, and a plan has an object.\n\nStart with Gallowmast Isle, east across the flats from the Landing. The other two crews will find you. The Wrackline bosuns carry the orders, and their gunners will be between you and the bosuns.",
        None,
    ),
    "are_wrack_drowned": (
        None,
        None,
        "Dese keepsakes, an' t'ree of dem I can name.\n\nDey went out to look for people. Dat is all dey did wrong. Go an' rest, an' den come back, because dere is one more watch on dis coast dat nobody relieved, an' it be older dan dis one by a long way.",
    ),
    "are_the_hermit": (
        None,
        "I was on a ferry out of Oban. Then the sea was a different sea, the ferry was on this rock, and that was three years ago. This is my rock now.\n\nI haven't asked anyone for anything in three years, so bear with me. The Storm Petrel Swarms have taken the lee side, which was my side. I held it for two years, and then there were more of them than me.\n\nBring me their down, in bundles. It's for a mattress. I'm nearly sixty and I've slept on a folded sail since before any of you arrived. There's a Reefmaw in the shallows under the rock, too. I'd sleep better without it.",
        None,
    ),
    "hf_by_the_measure": (
        None,
        None,
        "Half a dozen kinds of toxin, if my scales are right, and they are. The trolls blend it, which is clever of them.\n\nI'll have an antidote on the shelf by the end of the week, labelled, dated and measured. You'll find the first one costs you nothing.",
    ),
}


# THE STORY PASS (22 Nov 2026): the giver's speech becomes the description; see tools/voice/arathi_story.py.
from voice.arathi_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
