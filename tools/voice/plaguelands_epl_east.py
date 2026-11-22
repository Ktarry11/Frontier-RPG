"""Eastern Plaguelands east direction fixes (17 Nov 2026)."""

VOICE = {
    "ple_zulmashar_the_last": (
        None,
        "The Mossflayers follow a warlord who named himself after their city. Zul'Mashar the Last says he's the last of the old Amani blood, and he's sworn to drive everyone who isn't a troll out of these lands.\n\nThe raids won't stop while he's giving the orders.\n\nHe holds the top of the temple at Zul'Mashar, north of here. He's big, and he hits like a falling tree. Take friends, and bring bandages, because you'll need them.",
        None,
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/plaguelands_epl_east_story.py.
from voice.plaguelands_epl_east_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
