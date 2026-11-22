"""The southern Plaguelands in the plain voice (17 Nov 2026). One aphorism left after the zone's own plain build."""

VOICE = {
    "pls_snapjaw_shell": (
        None,
        "I'm Surgeon Grey. Mind the bucket.\n\nWhen the fields take a leg off one of the Deathguard, I put it back, and I brace the break with turtle shell. It's hard as iron and it doesn't rot, which is more than I can say for anything else out here. The best shell in the Plaguelands is on the Darrowmere Snapjaws at the lake.\n\nThey sun themselves on the shore of Darrowmere Lake, a long walk east of the Bulwark. Go for the legs, because you won't cut through the shell, and that's exactly why I want it. Bring me plates, and the bigger the better.",
        None,
    ),
    "pls_the_broodlord": (
        None,
        None,
        "Then that's the brood finished, and the Haunt's lost its nursery.\n\nI've been in a cell and I've been in a web now. I'm not sure which I liked less. Here, this is yours.",
    ),
    "pls_what_we_kill": (
        "Kill Scarlet Outriders and Scarlet Field Chaplains in Andorhal, south-east of the Bulwark.",
        "I'm Rory Callahan. Before you wear our flame, you need to know the one rule, so here it is. We kill the mindless dead and the fanatics who burn people, and nobody else.\n\nI wore the red for a year. When the world ended the Crusade were the only ones killing what was killing us, and I joined them. Then I saw who else they were burning, people like me, for the crime of being born on Earth. I scraped the red off and walked out, and some good people walked out with me.\n\nThe Scarlet Outriders and the Scarlet Field Chaplains patrol Andorhal now, south-east of the Bulwark. That's who we kill. Don't touch the Forsaken. They're rude, and they're not mindless.",
        None,
    ),
    "pls_clear_skies": (
        "Kill Plaguewing Vultures over the fields east of the Bulwark, out toward Darrowmere Lake.",
        "I'm Anders, and these are the Order's hawks. They carry our letters now that we've given up flying people.\n\nThe Plaguewing Vultures have started going after them in the air. I've lost two birds this week, and one of them was carrying a letter I'd rather the Crusade didn't read.\n\nThe vultures circle over everything dead, which out here is most of the map. They're thickest east of here, out toward Darrowmere Lake. Shoot them down if you can. Don't let them settle anywhere near the wall.",
        None,
    ),
    "pls_the_survey_map": (
        None,
        "The Crusade's Scarlet Outriders carry a surveyor's map of Andorhal. One of the guards at the Monastery bragged about it while I was in the cell, so I know it's real. Every Scourge strong point is on it, and every Forsaken one too.\n\nIf the Crusade knows where everyone is, so should we.\n\nThe outriders patrol Andorhal, south-east of the Bulwark. One of them carries it rolled in a leather tube. Bring it back dry, and don't let them burn it. They burn things when they're losing.",
        None,
    ),
    "pls_the_fallen_of_andorhal": (
        "Take Andorhal Company Rings from the Andorhal Skeletons in Andorhal, south-east of the Bulwark.",
        "Ser Aldren Holt. I held Andorhal for the King, and then I held it for the Crusade, and I walked out of both.\n\nWhen the plague came, my company held the city. My men are the Andorhal Skeletons now. Some of them still wear the company's iron rings.\n\nI'd like the rings back. I can't bury the men, so I'll bury those by Uther's Tomb. Not all of them will still have one. Bring me what you find, and forgive me for asking. I don't ask lightly.",
        None,
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/plaguelands_south_story.py.
from voice.plaguelands_south_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])


from voice.plaguelands_south_beats import BEATS as _BEATS
for _qid, _a in _BEATS.items():
    _o = VOICE[_qid]
    VOICE[_qid] = (_o[0], _a, _o[2])
