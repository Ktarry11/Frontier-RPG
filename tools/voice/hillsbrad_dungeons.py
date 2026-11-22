"""Azurelode Mine, Dun Garok and Durnholde Keep in the plain voice (17 Nov 2026). Already close to the bar: the
fixes are dashes, uncontracted narration and a few short closing lines. Same stories, same directions."""

VOICE = {
    "az_kobolds": (
        "Azurelode was the richest silver seam in the valley until the pumps stopped and the lower galleries went under in a night. The kobolds were in it inside the week. Grint Halloway has never been able to explain how a creature that can't read a pump roster knew the pumps had failed.",
        "Go to Azurelode Mine, south of Southpoint, in through the adit in the rock face, and mind the standing water. It's deeper than the light makes it look, and it doesn't drain anywhere.\n\nThat should clear the upper galleries. They'll be back, they're always back. I'd settle for walking my own mine without a torch in one hand and an axe in the other.",
        None,
    ),
    "az_survey": (
        None,
        "Go to the Silver Face, at the top of the workings. You'll know it, because the rock goes blue-violet the moment a lamp touches it.\n\nWhat I need is whether the causeway still stands. My chart says there's a spine of dry rock running to the Face. If the chart's right, the seam is reachable and this is a mine again. If it's wrong, it's a lake with a door.",
        "So it's still standing. Then the chart holds, and the Face can be worked.\n\nDon't tell the Overseer yet. He'll put men down there tomorrow, and I'd like to know what else is down there first.",
    ),
    "az_prospectors": (
        "There are Syndicate men in the flooded galleries, and they're measuring, not digging. They sound the depth, chalk the walls, and run chain along the sump. There's exactly one reason to measure a drowned mine that carefully, and it's to work out what draining it would cost.",
        "They're below the causeway in Azurelode Mine, south of Southpoint. You'll hear the chain before you see the lamps, because they sound the depth every ten paces and log it.\n\nAlterac sold the pass to the Horde in the Second War, and the Alliance dissolved the kingdom for it. The lords scattered into these hills with nothing. This is what nothing looks like when it finds a silver seam it used to own.",
        "They were chalking depths on the wall in a hand I recognise from estate maps. Bandits don't work like that. Somebody up there still thinks of this valley as property.",
    ),
    "az_silver": (
        "There's no sense hauling ore to Tarren Mill when the mine's own furnace sits a full six feet above the waterline and has done all along. Halloway wants bars, not baskets, and he'd like to know the person bringing them can tell silver from tin.",
        "Cut it off the Face and smelt it, at my furnace or any forge in the valley, I don't care whose.\n\nI want silver bars, mind. I've had three men bring me tin this season with a straight face, and tin out of a mine called Azurelode is a special sort of insult.",
        None,
    ),
    "az_grimewick": (
        "The pump house has a kobold foreman in it. He had a hammer he used to beat the pumps back into working whenever they seized, and he was still beating them when the water came over the sill. He hasn't stopped since, and the pumps haven't started.",
        None,
        None,
    ),
    "az_ashlan": (
        "Halloway has a predecessor. Ashlan Silvervein ran Azurelode the night the pumps failed, ordered the lower galleries worked through it, and went down with the shift he refused to call back. He's at the Silver Face, and he's still overseeing. Even the kobolds won't go near him.",
        "He's at the Face itself, deep in Azurelode Mine, south of Southpoint. He carries a mattock with silver worked into the head. It was a waste of good silver, and he knew it, and he had it made anyway.\n\nI've had his job two years. I'd rather not have it this literally, and I'd rather the men stopped asking me whether he'd have called them back.",
        None,
    ),
    "dg_mountaineers": (
        "Niall Crag has his measuring chain on the road and has finally got close enough to look at the fort itself. His professional opinion, delivered with some bitterness, is that there's no weak point. The dwarves cut every room in that hold square and put a gate at every narrowing.",
        "Go after their mountaineers, inside the outer gate of Dun Garok, south of the mill. I need that muster yard quiet long enough to measure it.\n\nAnd look at the walls while you're in there. There's no chamfer anywhere, no rubble fill, and every corner is a true corner. They didn't tidy up a cave. They cut a hold out of a mountain, square, on purpose, and I'd admire it more if I weren't trying to get into it.",
        "I've measured it. It's twenty-two paces by sixty, and the gates line up to the inch.\n\nI've surveyed six keeps. This is the only one where I could find no mistake to work with.",
    ),
    "dg_brannic": (
        None,
        "He's at the outer gate of Dun Garok, south of the mill, with a bearded axe and a shield scarred in a band at exactly shoulder height. In fifteen years that axe has only ever swung in one doorway.\n\nHe won't come out to you. He's never once come out. You'll have to go to him, in the one place he's had fifteen years to practise standing.",
        None,
    ),
    "dg_dunmar": (
        None,
        "He's in the barracks, east off the muster yard. There's a sally port up the east wall that reaches it without going through the inner gate.\n\nHe sights for the length of that yard and no further, same as his men, because he taught them. Inside that distance he's a man with an empty rifle and a sergeant's temper.",
        None,
    ),
    "dg_morgrin": (
        "There's a door at the back of the Great Hall that the Stormpike keep shut, and a shrine-keeper standing in front of it who has made it his life's work. Nobody in the garrison will say what's behind it, and Pell has decided their silence is the answer.",
        None,
        "So it's open, then.\n\nAnd now we have to decide whether we want to know. Wanting it open was the easy part.",
    ),
    "dg_korrin": (
        "Behind the vault door is a crypt, and in the crypt is a thane. He was buried in Dun Garok in an iron circlet by dwarves who swore to hold the ridge, and he didn't stay buried, and the garrison above has spent a great many years not discussing the noise.",
        "He's in the Crypt of Dun Garok, past the vault.\n\nHe has the Stonewatch Greataxe, and a circlet of iron he was buried in. The oath was to hold the ridge. He's technically still holding it, and I've never had cause to write a more dwarven sentence in a dispatch.",
        "The Stormpike won't thank us, and they won't admit it happened.\n\nThey'll bury him again, deeper, and the next garrison will be told the noise is the wind. That's how a hold keeps a secret: badly, and for centuries.",
    ),
    "dh_revenants": (
        "The Syndicate hold Durnholde's walls and courtyard. They don't go into the undercroft, and Emeline Vask finds that more interesting than anything else about the keep. A garrison with a cellar it won't use has a reason, and reasons are what she's for.",
        "Find whatever is down there in Durnholde Keep, south-east of the mill. The stair is behind the Lord's Hall.\n\nThese were the keep's own garrison, Lordaeron's men, the ones who were here when it fell. They didn't leave. The Syndicate have simply built their camp on top of them and agreed not to go downstairs, which is the most honest thing I know about the Syndicate.",
        None,
    ),
    "dh_varth": (
        None,
        "He's in Durnholde Keep's gatehouse, south-east of the mill, first thing through the archway.\n\nHe'll sound the alarm before he fights. That's his whole function, and he's good at it. If you want to get further into that keep than the bailey, the bell has to stop before the shouting starts.",
        "It's quiet, then, for the first time in two years, quiet at the gate.\n\nGo further in while it lasts.",
    ),
    "dh_sable": (
        None,
        "She's at the kennels, in the east bailey, through the breach.\n\nShe sets the pack on first and fights second. Kill the handler, and the pack is a dozen dogs with nobody shouting at them, and they'll scatter inside a minute. Try it the other way round, and you'll be fighting dogs until there are no more dogs.",
        "The pack went over the wall and didn't come back. Dogs are sensible.\n\nThat's the bailey crossable now, which is two years of my reports made obsolete in an afternoon, and I'm delighted about it.",
    ),
    "dh_perenolde": (
        None,
        "He's in the Lord's Hall, at the heart of the ring. You've done the work that makes this possible, and I'd rather you knew it. Without the fence's ledger and the magister's postings, I'd have sent you in to kill a squatter.\n\nAlterac sold the Alliance to the Horde, and his father signed it. The Alliance dissolved the kingdom and left the family their titles, because titles cost nothing. This is what fifteen years of carrying a title and no country does to a man.\n\nDurnholde Keep is south-east of Tarren Mill, off the east road. You know the archway.",
        "It's finished now.\n\nThe Syndicate won't end. There's always another cousin with a sash. But the man who could pay wizards and buy a valley's thieves is on the floor of a hall his family had no claim to, and the ledger, the postings and the name all go north together.\n\nYou walked three roads for this. I'll see every one of them is in the dispatch.",
    ),
}


# Kyle, 21 Nov 2026: no quests handed out in third person (tools/voice/third_person_late.py)
from voice.third_person_late import merge as _merge
_merge("hillsbrad_dungeons", VOICE)


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/hillsbrad_dungeons_story.py.
from voice.hillsbrad_dungeons_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
