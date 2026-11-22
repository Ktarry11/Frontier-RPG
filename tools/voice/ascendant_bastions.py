"""The Ascendant Bastions' quests in the giver's own voice (22 Nov 2026), to docs/quest_writing_standard.md, written once
Dawnspear Wreck was built and its people had moved in. The speeches and accept lines are in ascendant_bastions_story."""

VOICE = {}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/ascendant_bastions_story.py.
from voice.ascendant_bastions_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
