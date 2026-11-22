"""plaguelands_epl_west quests in the giver's own voice; the story pass lives in plaguelands_epl_west_story.py."""

VOICE = {}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/plaguelands_epl_west_story.py.
from voice.plaguelands_epl_west_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])


from voice.plaguelands_epl_west_beats import BEATS as _BEATS
for _qid, _a in _BEATS.items():
    _o = VOICE[_qid]
    VOICE[_qid] = (_o[0], _a, _o[2])
