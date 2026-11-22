"""The Valley of Trials: the starter voice is kept simple on purpose; only the short fragments are joined up."""

VOICE = {
    "vot_den_scout": (
        None,
        "I'm Kuraw, and I look after the new ones here. Have you been in a cave yet? The Den's a small one in the ridge west of camp, and it's a good one to start with.\n\nGo in and have a look around. Be careful in the small rooms, because you can end up with three of them on you at once. Come back and tell me what's in there.",
        "Alright, that's useful. Now I know what we're dealing with in there.",
    ),
    "vot_nest_guardian": (
        None,
        None,
        "You got it? That's nice work, and one less thing for the camp to lose sleep over.",
    ),
    "vot_yarrog_baneshadow": (
        None,
        None,
        "Is Baneshadow dead? That's a big help, and the whole valley will breathe easier tonight.",
    ),
    "vot_gulpjaw": (
        None,
        None,
        "Old Gulpjaw's gone? Oh, thank goodness. I can fish that pool again.",
    ),
    "vot_cinderjaw": (
        None,
        None,
        "You actually killed Smolderhide? That's amazing, and I'll tell everyone it was you.",
    ),
    "vot_fel_shards": (
        None,
        "Oh, hello there! Are you going into the Coven? The crystals in there give off this weird heat, and I'd love to know why.\n\nThe cultists carry little shards of it on their belts. Could you bring me some? Don't grab them with your bare hands, though.",
        None,
    ),
    "vot_mother_of_nest": (
        None,
        None,
        "Sarrix is dead? That's huge news, and the nest will fall apart without her.",
    ),
    "vot_ritual_disruption": (
        None,
        "I've got bad news. They're drawing a summoning circle deeper in the Coven, and if they finish it we're going to have something a lot worse than Baneshadow on our hands.\n\nCan you kill some of the initiates and the ritual guards? Get the guards first if you can, because they're the ones doing the summoning.",
        "The circle's broken? Good, now it's just Baneshadow left in there.",
    ),
    "vot_first_blood": (
        None,
        None,
        "Good, you can still fight. Get some food in you before you head back out.",
    ),
    "vot_scorpid_trouble": (
        None,
        None,
        "That'll push them back for a bit. Have a look through the camp stores and take something you can use.",
    ),
    "vot_vile_familiars": (
        None,
        None,
        "It's gone quiet in there for now, but whoever's in charge of them is still around.",
    ),
    "vot_sagewood_petals": (
        None,
        None,
        "These are perfect. That'll keep a few of them on their feet.",
    ),
    "vot_felstalkers": (
        None,
        None,
        "That's a lot less of them to worry about. The path to the den will be safer for the next lot through.",
    ),
    "vot_carrion_circle": (
        None,
        None,
        "Ah, that's so much better. I'm not supposed to give out coin, but here, have some of my old gear.",
    ),
    "vot_troubled_waters": (
        None,
        None,
        "It's clearing up already. I'll be able to fill the troughs by tomorrow.",
    ),
    "vot_heartwood": (
        None,
        None,
        "It's so much quieter in there now. Take whatever you like from the pile.",
    ),
    "vot_brood_below": (
        None,
        None,
        "Good, that'll make the next bit a lot easier.",
    ),
    "vot_windrift_omens": (
        None,
        None,
        "That's much calmer out there, and my leg feels better for hearing it. Elder Kuraw wants to see you when you're ready.",
    ),
    "vot_grosks_trophy": (
        None,
        None,
        "No way, you got it! Thanks so much. My mum's going to kill me. Here, this is yours.",
    ),
}


# THE STORY PASS (22 Nov 2026), to docs/quest_writing_standard.md; see tools/voice/valley_of_trials_story.py.
from voice.valley_of_trials_story import STORY as _STORY
for _qid, (_d, _a) in _STORY.items():
    _old = VOICE.get(_qid, (None, None, None))
    VOICE[_qid] = (_d, _a, _old[2])
