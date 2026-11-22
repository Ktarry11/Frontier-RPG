"""scarlet_monastery: closing lines varied so the zone stops ending every hand-in on thanks (17 Nov 2026)."""

VOICE = {
    "sm_the_scout_in_the_cells": (
        None,
        None,
        "She was alive, then, and she's on her way here.\n\nI was a firefighter in Brno before all this. You learn to count who comes out. I'm still counting.",
    ),
    "sm_drilled_to_die": (
        None,
        None,
        "The newcomers brought a lot of things with them. Some of them brought this, apparently.\n\nI'd rather fight soldiers than children, and you've made that likelier.",
    ),
    "sm_the_sleepless": (
        None,
        None,
        "I felt something loosen, I think, a long way off.\n\nThe dead there aren't ours, but the dead are the dead.",
    ),
    "sm_a_book_of_names": (
        None,
        "Take the road east into Eastern Tirisfal for the Monastery. Mercer keeps to the Closed Stacks, off the long hall in the Library. She'll shut your casters down if she can, so bring someone who hits things. The ledger doesn't leave her desk.",
        None,
    ),
}


# Kyle, 21 Nov 2026: no quests handed out in third person (tools/voice/third_person_late.py)
from voice.third_person_late import merge as _merge
_merge("scarlet_monastery", VOICE)


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/scarlet_monastery_story.py.
from voice.scarlet_monastery_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
