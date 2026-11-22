"""timbermaw_tunnel quests in the giver's own voice; the story pass lives in timbermaw_tunnel_story.py."""

VOICE = {}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/timbermaw_tunnel_story.py.
from voice.timbermaw_tunnel_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
