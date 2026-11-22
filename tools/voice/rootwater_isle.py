"""Rootwater Isle and Rootwater Landing in the giver's own voice (22 Nov 2026), to docs/quest_writing_standard.md.
Narrated one- and two-liners rewritten as the giver talking, five or six sentences, facts and directions kept; accept
lines a short beat; turn-ins untouched. The climbing plan is an item starter and narrates to "you" on purpose.
"""

_S = {
    "rwq_off_the_boat": (
        "I row the crossing from Grom'gol, and everybody who comes off my boat goes up to the headwoman first. That way "
        "she knows who's on her island, and nobody gets lost between the pier and the trunk. I've written you down on the "
        "manifest, and I don't write much. Take it up to Headwoman Zula Rootcaller at the landing, under the trunk. You "
        "can't miss the trunk.",
        "She'll want to look at you before she looks at the paper. Stand up straight.",
    ),
    "rwq_crocs_at_the_pier": (
        "The Sap-Drunk Crocolisks have started coming up under the Grom'gol pier. One took my oar right out of my hands "
        "last week, and I'd rather it was the oar than the hands next time. They've lost their fear of the boat. I've "
        "rowed this crossing a long time, and I've never had to fight my way off a pier before. Thin them out round the "
        "lagoons for me.",
        "They lie still in the shallows by the pier. Look for the eyes, not the backs.",
    ),
    "rwq_from_the_other_coast": (
        "I row the long crossing to Zoram Strand on Ashenvale's coast. The night elves at Zoram keep asking my passengers "
        "what this tree is, and none of them can say. The headwoman's written them a proper answer, and it ought to go "
        "with somebody who's seen the place. Come across with me and give it to Boatwright Illyen on the pier. He's the "
        "one who's been asking hardest.",
        "Sit in the middle of the boat. The crossing gets rough past the reef.",
    ),
    "rwq_murlocs_under_the_oars": (
        "The Rootbound Murlocs follow my boat out of the lagoons and hang off the oars. They aren't strong, but there are a "
        "lot of them, and the roots growing through them make them heavy and hard to shake off. Last week I nearly lost "
        "an oar to three of them at once. Somebody's going to go over the side if this keeps up. Clear them out of the "
        "Root Lagoons, south of here, for me.",
        "Don't let them grab you. Those roots hold on like they're still growing.",
    ),
    "rwq_twice_their_size": (
        "The crocolisks in the lagoons have doubled in size since they started drinking the sap that seeps out of the "
        "roots. They've stopped running from us, too. A croc that isn't scared of you is a croc that's going to try "
        "something. I've hunted these lagoons my whole life, and they always used to run. Teach the Sap-Drunk Crocolisks "
        "to be scared again.",
        "Hit them hard the first time. They need to remember what it feels like.",
    ),
    "rwq_lizard_hides": (
        "Every hunter who goes up the tree needs a quiver that won't slip, and Bark Lizard hide grips like nothing else. "
        "Half the climbers these days are newcomers who'd never held a bow before they crossed over. Anything you drop up "
        "there, you never see again. The lizards live all over the island, and their hides look exactly like the bark "
        "they sleep on. Look hard, and bring me their hides.",
        "If a patch of bark blinks at you, that's a lizard.",
    ),
    "rwq_moths_round_the_lanterns": (
        "The Leafwing Moths come to the landing's lanterns every night, and they're the size of dogs now. Their wing dust "
        "gets into everything and makes people itch for days. I keep thinking I'll get used to this place, and then "
        "something else grows. I'd like a few nights without scratching. Knock them down wherever you find them on the "
        "island.",
        "They'll come to you if you carry a lantern, so use that.",
    ),
    "rwq_the_bloodscalp_climb": (
        "The Bloodscalp never forgave the tribes who climbed this tree without them, and now they're after it for "
        "themselves. They've made a war camp out on the north-west root. Their Headhunters and Axe-Throwers come down it "
        "at night to take trolls off the edge of the landing, and I've lost two hunters that way this month. Some of the Highbough were Bloodscalp once, which makes it a "
        "family fight, the worst kind. Go up the north-west root and break their hunting parties.",
        "The Axe-Throwers stay back and let the Headhunters close in. Go for the ones who hang back.",
    ),
    "rwq_measuring_the_sap": (
        "The sap's the tree's blood, and I measure it the way a healer measures a fever, because somebody has to. A little "
        "sap heals a cut, and a cup makes a man strong. The Sap-Drunk Crocolisks drink more of it than anything on this "
        "island. I want to see how much they're carrying. Bring me their blood in gourds, and I'll see how much gold's in "
        "it.",
        "Seal the gourds tight. I want to see it before it starts to set.",
    ),
    "rwq_rootbound": (
        "The murlocs in the lagoons have roots growing right through their fins now. I need to know whether the tree is "
        "feeding them or feeding on them, and that's not a small question. The only way to tell is to look at the roots "
        "themselves. Tazjin will want the answer as much as I do. Bring me some of the Rootbound Murlocs' fins.",
        "Cut them close to the body. I want the root where it goes in, not just the tip.",
    ),
    "rwq_whiskers_for_the_draught": (
        "I cut the tree's sap with Khadgar's Whisker, so it heals without doing anything else to you. Every troll going up "
        "the tree takes three draughts with them. Nobody's ever needed more than two, but they all want three, and I've "
        "run low. The herb grows all over the island, along the roots and under the jungle. Bring me what you can pick, "
        "and I'll keep the climbers supplied.",
        "Pick it with the leaves on. The leaves are where the good of it is.",
    ),
    "rwq_what_the_bloodsail_want": (
        "The Bloodsail aren't tapping the roots for their own use, and I want to know who's buying. Their Sap-Tappers write "
        "everything down, every barrel and every buyer. Somebody's buying the tree's blood by the barrel, and I want to "
        "know what they think it's going to do for them. A healer doesn't need sap by the barrel. Get me the Bloodsail "
        "Sap-Tappers' ledgers from their camp on Sapwash Beach, east of here.",
        "Bring every page you find. The buyers' names will be at the back.",
    ),
    "rwq_the_hungry_loa": (
        "The loa of this tree answered us when the world broke and nothing else did, and I listen for it every night. "
        "Lately it's hungry. The bark's begun to rot out on the north-east root, past the Root Stair, at the heart of the "
        "Saproot Thicket. A tree this size can lose a branch and never notice, but the root is where it drinks. Go and "
        "look at the rot for me, and tell me what you see.",
        "Don't touch the rot. Just look, and remember the smell.",
    ),
    "rwq_rot_on_the_root": (
        "Things live in the rot now, eating the bark from the inside where it's gone soft. The Rot Crawlers and the "
        "Bark-Borer Beetles spread it wherever they chew. They didn't start it, I think, they're just fat on it. I want "
        "them cleared before the rot climbs any higher. Clear them off the north-east root before it reaches the trunk.",
        "Kill them in the soft bark. If they get into the trunk, we'll never dig them out.",
    ),
    "rwq_living_sap": (
        "Out in the rot, the sap has started crawling about on its own. The Goldensap Oozes are what the tree bleeds when "
        "it's sick, and I need to know what's alive in them. I think something's feeding on the tree's sickness and "
        "growing on it. Bring me clots of the ooze from the Saproot Thicket, north-east of here, in a closed jar. Don't look at them too long.",
        "Keep the jar shut, whatever you hear from inside it.",
    ),
    "rwq_the_rot_mother": (
        "At the heart of the rot, something has grown big on the tree's sickness, and everything else in there's one of "
        "its children. I call it the Rot-Mother. I can feel the loa straining every time she feeds. She has to be cut out "
        "of the tree. Find her on the north-east root and kill her.",
        "Her children will come for you when she's hurt. Finish her quickly.",
    ),
    "rwq_the_bloodsail_tap": (
        "The Bloodsail have set up on the south-east root and hammered spigots into it. They're bleeding the tree for sap "
        "to sell, and every barrel they fill is the tree bleeding. I can see the stain on the bark from the landing. The tree gave itself to us, and none of us would ever "
        "put a price on it. Kill their Sap-Tappers, and the Bloodsail Cutthroats who guard them.",
        "Leave the spigots for now. I'll have the tribes pull them and seal the holes.",
    ),
    "rwq_tapmaster_grell": (
        "The Bloodsail's sap camp is run by a man called Grell, who taps the roots himself and knows exactly how deep to "
        "go. I've watched him work, and he's the one who knows how to bleed a root without killing it. Without him, they'd hit nothing but bark. As "
        "long as he's there, the camp will keep coming back. Find Tapmaster Grell on the south-east root and end him.",
        "He'll be at the deepest spigot. That's where the best sap runs.",
    ),
    "rwq_word_to_gromgol": (
        "The Highbough Tribes don't answer to the Horde, but Grom'gol is across the water, and its Darkspear attache, "
        "Zul'jana, is family to half the landing. She should hear about the Bloodsail tapping the tree and the Bloodscalp "
        "climbing it from us, not from rumours. I've written it down plainly. Take her this at Grom'gol. Take the boat, "
        "because it's quicker than you'd think.",
        "Give it to Zul'jana herself. Not the overseer, not anybody else.",
    ),
    "rwq_paid_in_sap": (
        "I built every lift on this tree, and the trolls paid me in sap. It was the best deal of my life, until the "
        "Bloodsail worked out what sap's worth. Last night their Powder Monkeys came up from Sapwash Beach, east of here, and blew my best winch to splinters. Somebody "
        "taught those monkeys to light fuses, and they're smarter than half the crews I've hired. Go and return the "
        "favour, and I'll owe you one.",
        "They keep the powder close. Don't stand next to a monkey with a lit match.",
    ),
    "rwq_cable_for_the_winch": (
        "Rope rots, and on a lift that climbs a tree this size, rotten rope means a long fall. I want mithril for a new "
        "winch cable. Nobody up there thinks about the cable until it's gone, and then it's all they think about, for "
        "about four seconds. There are veins of ore in the rock between the roots, if you've got a pick. Bring me some "
        "mithril, and I'll have the lift running again.",
        "Good clean ore, mind. A cable's only as strong as its worst link.",
    ),
    "rwq_the_wing_in_the_sand": (
        "Something came down out of the sky a few nights ago onto the north-west root, out past where the Zoram road bends "
        "north. The trolls say it's a bronze wing, with a blue crystal lying next to it. I say nobody makes wings out of "
        "bronze. I know every workshop between Undermine and Gadgetzan, and I'd like to see it for myself, but my legs "
        "aren't what they were. Go and look at it before the Bloodscalp do.",
        "Don't let anyone else touch it before you've had a good look.",
    ),
    "rwq_not_goblin_work": (
        "I can't place that bronze wing, and that bothers me more than I'd like. Marta Kowalczyk came over on the Zoram "
        "boat, and she built ships back where she comes from, real ones with engines. If anybody on this island's seen "
        "something like it, it's her. Show her this piece I broke off it. She's at the landing.",
        "Ask her straight. She doesn't like being flattered first.",
    ),
    "rwq_the_view_from_here": (
        "I came over on the Zoram boat to see the tree everybody was talking about, and I never got back on. I've been all "
        "over the landing, but I've never been out to the ends of the roots. I'd like to know how far the tree has reached. "
        "Walk out along the long south root and the north-east root for me. Tell me what you see at the end of each.",
        "Go slowly at the ends. The roots get narrow, and the sea's right there.",
    ),
    "rwq_cages_on_the_root": (
        "The Bloodscalp keep cages up at their camp on the north-west root, and last night I swear I heard someone calling "
        "for help in Polish. I know how that sounds. Their War-Climbers watch the camp from the branches above. Go up "
        "there, kill them, and look in the cages. I'll owe you, whatever you find.",
        "Look closely, even if the cages are empty. People leave things behind.",
    ),
    "rwq_censers_and_hexes": (
        "Up at the Bloodscalp Climb, north-west of here, the Bloodscalp Witch Doctors burn something in their censers that comes down the root on the night wind, and half "
        "the landing's been coughing for a week. Their Shamans keep the fires going. The trolls took me in when I didn't "
        "have anything, and I'd like to do something for them. Put the fires out, all of them. Kill the witch doctors and "
        "the shamans.",
        "Hold your breath near the censers. The smoke's worse up close.",
    ),
    "rwq_zulgash_the_climber": (
        "The Bloodscalp war camp on the north-west root answers to Zul'gash the Climber. He climbed that root first, and "
        "the trolls say he means to go up the trunk next. I've watched that camp from the landing, and it gets bigger every week. If he goes up, there won't be a landing to come back to. As long "
        "as he lives, the Bloodscalp will keep coming up. Find him at the war camp and stop him.",
        "He climbs better than he fights. Keep him on the ground.",
    ),
    "rwq_the_plan_to_climb": (
        "You unroll the strip of hide. A Bloodscalp war-climber was carrying it, painted with the tree's roots and a line "
        "of red handprints going up the north-west one. The handprints climb past the landing and on up the trunk. It's "
        "a raid plan, and a careful one. Headwoman Zula should see it before the Bloodscalp use it.",
        "Get it to the headwoman at the landing.",
    ),
    "rwq_what_drinks_the_sap": (
        "I watch the lagoons from the south-west road. The sap pools in the deep hole out in the lagoon, and everything "
        "that's thirsty comes to drink there. I can see the gold in the water from here at night. I want someone to wade "
        "out and look at it, and see what's living there. The Reef Shellcrushers will come at you in the shallows, so kill "
        "them as you go.",
        "The hole's further out than it looks. Keep wading until the water turns gold.",
    ),
    "rwq_shells_for_the_scouts": (
        "Every scout on the island eats out of a Reef Shellcrusher shell, and we're short of them. The shells out here have "
        "roots growing through them now. The old scouts say that's lucky, and the new ones say it's creepy. The crabs are "
        "all over the lagoon shallows. Bring me their shells, roots and all, and I'll scrape them clean.",
        "Unbroken ones, if you can. A cracked shell won't hold a meal.",
    ),
    "rwq_the_rootmaw": (
        "The Rootmaw is the oldest crocolisk on the island, and it was the first thing here to drink the sap. It's been "
        "drinking from the roots since the tree first split the reef, and it's covered in barnacles and roots now. Last "
        "month it took two of our fishers. It's still getting bigger. Find it in the Root Lagoons and kill it.",
        "It lies at the bottom and waits. Make it come up to you.",
    ),
    "rwq_the_root_stair": (
        "You've done more for this landing than most who come through, and I'd say you've earned the climb. The Root "
        "Stair runs up the trunk's east side, all the way to the Lower Boughs. Elder Tal'vani in Mossroof, the first "
        "village up the tree, should hear about you from me. Climb it, and take my word to him at the top. He'll have work "
        "for you.",
        "It's a long climb. Rest when you need to, and don't look down until you're used to it.",
    ),
}

VOICE = {qid: (d, a, None) for qid, (d, a) in _S.items()}
# the old turn-in closed on an aphorism the voice bar refuses ("the difference between a tribe and a crew")
VOICE["rwq_the_bloodsail_tap"] = VOICE["rwq_the_bloodsail_tap"][:2] + (
    "That'll cost them a few barrels. They'll be back, because sap pays, but they'll come back fewer.\n\nThe tree gave "
    "itself to us, and I'd sooner cut my own hand than sell what runs out of it.",)


from voice.rootwater_isle_beats import BEATS as _BEATS
for _qid, _a in _BEATS.items():
    _o = VOICE[_qid]
    VOICE[_qid] = (_o[0], _a, _o[2])
