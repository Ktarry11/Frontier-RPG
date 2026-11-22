"""The Great Settlement in the giver's own voice (22 Nov 2026), to docs/quest_writing_standard.md. Narrated lines
rewritten as the giver talking, five or six sentences, facts and directions kept; accept lines a short beat;
turn-ins untouched.
"""

_S = {
    "gsq_an_audience": (
        "I keep the top of the Great Lift, and Tal'vani sent word you were coming up. Everybody the elders below send up "
        "goes to the High Chieftain first. I've written you a pass for the guards on the Rise, because they won't let you "
        "past on a face alone. Take it along the ledge to the Heart Palace on the Chieftain's Rise. You'll know it, "
        "because it's the one wrapped round the trunk.",
        "Show the guards the pass before they ask. They like that.",
    ),
    "gsq_the_war_below": (
        "I hold this tree for the tribes who climbed it, and I don't hand out trust for a good story. The Bloodscalp come "
        "up the ropes at the Climbers' Cut, down on the Lower Boughs. Their Reavers lead every climb, and their "
        "Bough-Shamans call the storm down on anyone in their way. Go down and break them, and their war leaders with "
        "them. Then come back and tell me how it went.",
        "I like stories best when the ending's already done. Bring me one of those.",
    ),
    "gsq_horde_ground": (
        "I've sat on this terrace for a year waiting for Zan'kaji's answer to Orgrimmar, and he gives it to me the week "
        "you turn up. I'd carry it myself, but I've been told to wait for the next one. I'd rather it went to Thrall with "
        "someone who's earned the tribes' trust anyway. Take it to Thrall in Grommash Hold. Take the bats from the Roost, "
        "because they're faster than the boats.",
        "Give it to Thrall and nobody else. He'll want to hear it in the tribes' own words.",
    ),
    "gsq_the_wall_of_fallen_things": (
        "I keep the wall in the market where the scholars show what's fallen from the clouds. Every piece on it fell out of "
        "the sky and caught in the branches. The Silkwood Weavers down in the Silkwood on the Lower Boughs have been "
        "wrapping the crystal chips up like prey. I want them on my wall, not in a spider's larder. Get me some of them, "
        "silk and all.",
        "Don't cut the silk off. I want to see how they wrapped them.",
    ),
    "gsq_into_the_web_hall": (
        "I'm sure the biggest pieces are in the spiders' web-hall at the far end of the Silkwood, where they keep what "
        "they can't eat. I've never been brave enough to go and look myself. Go and look for me. The Silkwood Stalkers will "
        "drop on you from the webs, so watch above you. If there's anything big in there, bring it back.",
        "Look for anything wrapped like an egg. That's what they guard hardest.",
    ),
    "gsq_the_record": (
        "That crystal from the web-hall needs to go into the scholars' record before it goes on my wall. Tel'zan keeps "
        "the record of everything that's fallen from the sky. He'll want to see this before anyone else does. It's the "
        "biggest piece we've had. Take it across the bridge to Archivist Tel'zan in the scholars' hall at the Roost.",
        "Carry it in both hands. It's still warm, and it's heavier than it looks.",
    ),
    "gsq_the_wards_lanterns": (
        "Our lanterns burn with a pinch of glimmer dust in the oil, and that's why the ward glows gold at night. Little "
        "Jinto lights them, and he's run out. He says if a lantern goes out, the loa can't find its way home, and I told "
        "him that myself when he was small. The Glimmerwing Moths along the trunk ledge below Mossroof carry the dust on "
        "their wings. Bring some back for him.",
        "Knock them down gently. The dust comes off their wings if you hit them too hard.",
    ),
    "gsq_a_bat_in_the_webs": (
        "One of my bats went down into the Silkwood in last week's storm, and she hasn't come back. I can hear her calling "
        "at night from the Roost, caught somewhere in the webs. The Silkwood Weavers will have her wrapped by now, if they "
        "haven't eaten her. I'm not leaving her down there. Clear them out of the Silkwood, and I'll go down and cut her "
        "loose.",
        "Listen for her as you go. She'll be the one shouting.",
    ),
    "gsq_offerings_for_the_loa": (
        "The first trolls who climbed this tree carried Goldthorn up with them. I lay it at the loa's feet every new moon "
        "to remember them. Since the world broke, the loa have been quiet everywhere but here, and this one still answers. "
        "I mean to keep it answering. Goldthorn grows out on the boughs below, so bring me what you can pick.",
        "Pick it with the flowers open. The loa likes it fresh.",
    ),
    "gsq_soil_for_the_terrace": (
        "I grow the ward's food on the garden terrace, and every basket of soil on it came up the lift. It wears thin in a "
        "season. Bloodroot wood from the boughs, chipped and worked into the beds, brings it back. I've tried other woods, "
        "and nothing works as well. Bring me some Bloodroot, and the ward will eat well this winter.",
        "Dry wood chips better. Leave the sappy pieces where you find them.",
    ),
    "gsq_a_taste_of_home": (
        "I ran a market stall in Accra before the merge, and every market day I'd grill tilapia with pepper and onions, "
        "and the whole street would come. I want to cook something that tastes like home for the Settlement's market day. "
        "The Redgill in the river on the Great Bough, below Mossroof, is close enough. Catch me some. I'll show these "
        "trolls what a market day smells like.",
        "Fresh ones, mind. I'll know if they've been sitting in the sun.",
    ),
    "gsq_a_leaf_for_tea": (
        "My family kept a tea house in Kyoto for four generations. Up here, I've been brewing a leaf the trolls grow in "
        "the gardens, and now it's gone. Khadgar's Whisker might take its place, because it's bitter in the right way. It "
        "grows out on the boughs below. Bring me some, and I'll try a pot.",
        "Young leaves, if you can find them. The old ones taste like bark.",
    ),
    "gsq_up_the_high_lift": (
        "I work the bottom of the High Lift. The shadow hunters at Heartwatch, up in the Middle Boughs, have asked the city "
        "for anyone who can fight, and after the Bloodscalp business, your name's the one everybody says. Nobody's asked us "
        "for fighters since the merge. Take my token up the High Lift, so Dezza at the top knows I sent you. Then find "
        "Shadow Hunter Vokra at Heartwatch.",
        "Hold on tight on the way up. The lift sways in the wind.",
    ),
}

VOICE = {qid: (d, a, None) for qid, (d, a) in _S.items()}
