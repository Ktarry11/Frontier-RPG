"""The Celestial Expanse's quests in the giver's own voice (22 Nov 2026), to docs/quest_writing_standard.md, written once
Halcyon Rest was built and its people had moved in. The speeches and accept lines are in celestial_expanse_story; the
turn-ins below are the ones that still spoke from the wreck or the Golem Fields before their givers came up to the Rest."""

VOICE = {
    "ceq_the_wards_were_kharad": (None, None,
        "Ilaren Vey sent this, and Ilaren Vey said sorry? I'll have that written down.\n\nIt's Kharad, and it's a ward "
        "letter, the one that means strike, and it's cut on every golem lying out on the Golem Fields. They're the same "
        "makers, and they woke up on the same day."),
    "ceq_the_councils_courtesy": (None, None,
        "The gifts are glass now, but the seal's whole. That's the first thing that's gone right today.\n\nI'll keep it "
        "in my coat until the road to the bridge is open. When it is, it's yours to carry."),
    "ceq_something_to_eat": (None, None,
        "Three years up here, and I've learned to cook a sky sheep. My mother would be proud and a little confused.\n\n"
        "Eat something while it's hot. The Rest's bread is very good, but it isn't meat."),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/celestial_expanse_story.py.
from voice.celestial_expanse_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
