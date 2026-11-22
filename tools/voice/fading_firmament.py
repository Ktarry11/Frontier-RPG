"""the Fading Firmament's quests in the giver's own voice (22 Nov 2026).

Kyle, 21 Nov 2026: no quests handed out in third person. The rewrites live in tools/voice/third_person_late.py with the
other stragglers; this module folds the Fading Firmament's block in so tools/build_zone_voice.py can compile it.
"""
from voice.third_person_late import merge

VOICE = merge("fading_firmament", {})
