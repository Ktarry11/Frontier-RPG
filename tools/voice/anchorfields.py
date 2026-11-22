"""the Anchorfields's quests in the giver's own voice (22 Nov 2026).

Kyle, 21 Nov 2026: no quests handed out in third person. The rewrites live in tools/voice/third_person_late.py with the
other stragglers; this module folds the Anchorfields's block in so tools/build_zone_voice.py can compile it.
"""
from voice.third_person_late import merge

VOICE = merge("anchorfields", {})


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/anchorfields_story.py.
from voice.anchorfields_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
