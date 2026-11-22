"""royal_hive: closing lines varied so the zone stops ending every hand-in on thanks (17 Nov 2026)."""

VOICE = {
    "rh_under_the_cell": (
        None,
        None,
        "Then the hive has nobody left to lead it.\n\nThe digging stopped this morning. I had Rurik sit by the wall all night to be sure. Take what Aldis has put aside for you.",
    ),
    "rh_the_warden": (
        None,
        None,
        "That means my scouts can get further in now.\n\nThis is from the gate stores.",
    ),
    "rh_eating_the_pillars": (
        None,
        None,
        "The pillars have stopped ringing hollow.\n\nThat's the first good news I've had about the roof since the ground shook three years ago.",
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/royal_hive_story.py.
from voice.royal_hive_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
