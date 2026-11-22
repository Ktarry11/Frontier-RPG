"""ashen_reach: closing lines varied so the zone stops ending every hand-in on thanks (17 Nov 2026)."""

VOICE = {
    "tmp_the_wreck_captain": (
        None,
        None,
        "That's its helm. It was wearing one of my berth tags.\n\nI'll post the news on the wharf tonight and the pilots will sign on again. This is from the harbour office.",
    ),
    "tmp_a_harbour_chart": (
        None,
        None,
        "Every reef and wreck is marked on this.\n\nNobody has had a chart of this coast since the sea route opened three years ago. I'll send the surveyor a bottle. Take something from the harbour office.",
    ),
    "tmp_pitch_for_two_boats": (
        None,
        None,
        "That's good tar, and it's still soft.\n\nI'll have both hulls sealed by tomorrow. Take this, it washed up last week.",
    ),
    "tmp_old_scoria": (
        None,
        None,
        "The whole yard felt it go. The ground jumped and then went quiet.\n\nVarga came in an hour ago and said she hadn't seen a single elemental on her round. Choose whichever of these suits you.",
    ),
    "tmp_brass_in_a_month": (
        None,
        None,
        "These are just right.\n\nI'll cut new gaskets for the whole pump engine tonight. Have this, I made it and never got round to using it.",
    ),
    "tmp_drive_belts": (
        None,
        None,
        "That's a good thick hide with no scorch marks.\n\nI'll have it on the drum by the end of the shift. This is from the mine head stores.",
    ),
    "tmp_walking_into_the_face": (
        None,
        None,
        "I fired three faces this afternoon and there was nothing in them but rock.\n\nPulling a live charge is the most dangerous part of this job. You did it carefully, and that's why you've still got your hands. Take this with you.",
    ),
    "tmp_where_the_vents_moved": (
        None,
        None,
        "So the north-west rope has burned through and the other two are fine.\n\nThe western vent has moved toward the cart road. I'll move the road markers east in the morning. Take this, I won't need it until my ankle heals.",
    ),
    "tmp_the_ventlord": (
        None,
        None,
        "I watched the steam stop all along the Approach at once.\n\nThe Foreman told me to give you this when you came back.",
    ),
    "tmp_whatever_came_off_the_boat": (
        None,
        None,
        "It does smell smoked.\n\nThe dwarves had three bowls each and the goblins asked for the recipe. Your name's on the board, and this is for you.",
    ),
    "tmp_the_landing_shelf": (
        None,
        None,
        "The shelf is clear, so I can put surveyors on it this week.\n\nHere's what the Ashclaim owes you.",
    ),
    "tmp_four_barges": (
        None,
        "A whole run of my barges never arrived, and I think the naga have them.\n\nThe current off the landing runs north along the west shore. Anything that sinks in the bay washes up on the Scoured Coast, and the Stormscale Naga Raiders have been there since the sea route opened three years ago. They keep trophies, so they'll have the nameboards.\n\nLeave by the town gate and cross the Ashen Reach to its far west shore, past the Cinder Flats. Kill the Raiders and bring back any nameboards you find.",
        "That's every one of them.\n\nSo the naga had them. What I don't know is whether they found them wrecked or wrecked them. Take these boards to Adjuster Raman at the Merchant House. Working that out is her job.",
    ),
    "tmp_the_mountains_heart": (
        None,
        None,
        "All three needles stopped at the same moment.\n\nThe vents are still smoking, but it's an ordinary volcano now, and I know how to watch one of those. When the bay at Kagoshima vanished three years ago I didn't think I'd be doing this work again.",
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/ashen_reach_story.py.
from voice.ashen_reach_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
