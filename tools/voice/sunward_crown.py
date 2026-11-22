"""The Sunward Crown's quests in the giver's own voice (22 Nov 2026), to docs/quest_writing_standard.md, written once
Lenswatch took in the Annex and Spearhold became its own camp. The speeches and accept lines are in sunward_crown_story."""

VOICE = {}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/sunward_crown_story.py.
from voice.sunward_crown_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
