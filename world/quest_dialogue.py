"""
Topic content for DIALOGUE-type quest objectives (see world/quest.py's
ObjectiveType.DIALOGUE and QuestObjective.topics/ask_topic).

Kyle's ask (2026-09-10): turn "A Real Town" (razorhill_welcome) - a
STORY-type quest that just handed the player a wall of text on accept -
into a real dialogue tree: ask about Durotar, then Razor Hill, then
Orgrimmar, and the quest completes once all three are covered.

Separation of concerns matches KILL's own split between "which monster"
(QuestObjective.target) and "what that monster's kit does"
(data/creatures/creatures.json + ability_kits.json, owned elsewhere):
QuestObjective.topics is just the completion condition (a list of
topic_id strings), the actual topic label + response TEXT lives here,
keyed by (quest_id, topic_id) so two different quests can each define
their own "durotar" topic with different phrasing for different givers
without colliding.
"""

#: (quest_id, topic_id) -> {"label": button text, "response": what the
#: NPC says}. Order within QUEST_TOPICS's value dict is the suggested/
#: natural ask order (matches the quest's topics list) but NOT enforced -
#: see QuestObjective.topics_asked's docstring for why coverage, not
#: sequence, gates completion.
QUEST_TOPICS = {
    "razorhill_welcome": {
        "durotar": {
            "label": "What is Durotar?",
            "response": (
                "The whole stretch of red dirt and dead grass between here and "
                "the coast - that's Durotar, not just this one town. Orcs hold "
                "it, but holding isn't the same as owning it outright. Quilboar "
                "dug into Rocktusk Farm before we could stop them, centaur ride "
                "the crags like they've got somewhere better to be, and there's "
                "still Burning Blade rot festering at Skull Rock. It's ours. "
                "That doesn't mean it's settled."
            ),
        },
        "razor_hill": {
            "label": "What is Razor Hill?",
            "response": (
                "Where you're standing. First real town past the valley - "
                "walls, a trainer, a way station for anyone headed further "
                "into Durotar or up toward Orgrimmar. It's not big and it's "
                "not soft, and that's on purpose. Recruits who can't hold "
                "Razor Hill for a season have no business heading anywhere "
                "harder than this."
            ),
        },
        "orgrimmar": {
            "label": "What is Orgrimmar?",
            "response": (
                "Capital. North of here, built into the rock, the closest "
                "thing the Horde's got to a heart that beats in one place. "
                "You'll end up there eventually - everyone does - but that's "
                "a city's problems, not a recruit's. Learn Durotar first. "
                "Orgrimmar will still be standing when you're ready for it."
            ),
        },
    },
    "taurajo_old_grudges": {
        "the_kolkar": {
            "label": "Tell me about the Kolkar.",
            "response": (
                "Centaur, same as ever. They were here before the Cataclysm "
                "scattered their old territories, before the Horde came east "
                "at all. Kolkar's just one tribe of many, but they're the "
                "tribe pressing closest to Camp Taurajo, and they remember "
                "every acre of ground we've claimed as ground they lost."
            ),
        },
        "the_old_barrens": {
            "label": "What was this land before?",
            "response": (
                "Open, further than the eye could carry, and contested long "
                "before any of us arrived. The Kolkar hunted it, the Grimtotem "
                "hunted it, kodo herds moved through it like weather. We built "
                "Camp Taurajo on land that never belonged to anyone cleanly - "
                "not us, not them. That's the part most warriors forget."
            ),
        },
        "why_it_matters": {
            "label": "Why does it matter now?",
            "response": (
                "Because every young warrior who rides out to kill Kolkar "
                "thinks it's a simple thing - us or them. It's never simple. "
                "They raid because they believe the land is owed to them. We "
                "defend because we've made a home here and won't be moved "
                "twice. Both things can be true. Neither makes the fighting "
                "stop."
            ),
        },
    },
    "ratchet_loose_lips": {
        "the_freebooters": {
            "label": "What do you know about the Freebooters?",
            "response": (
                "Southsea crew, goblin-flagged but they'll take anyone who "
                "can hold a cutlass. They've raided this coast before and "
                "moved on when it got too hot. This time feels different - "
                "they're digging in, not just raiding and running."
            ),
        },
        "the_maidens_dagger": {
            "label": "What's The Maiden's Dagger?",
            "response": (
                "Their fort, up the coast. Small, but well-stocked - I've "
                "seen the supply runs myself, more crates going in than any "
                "raiding camp needs. Someone's planning to stay a while, and "
                "Captain Saltspray's the one holding it together."
            ),
        },
        "what_happens_next": {
            "label": "What happens if no one stops them?",
            "response": (
                "Ratchet's trade dries up, is what happens. Every ship that "
                "doesn't make port because of pirate sails is money Gazlowe "
                "doesn't see, and money Gazlowe doesn't see becomes everyone's "
                "problem eventually. I'd rather it get handled quietly, before "
                "it becomes the kind of problem that needs an army."
            ),
        },
    },
    "taurajo_earthsongs_warning": {
        "what_she_senses": {
            "label": "What do you sense?",
            "response": (
                "A wrongness, faint but real, carried on the wind from the "
                "north. Not quilboar - they're loud, honest violence, the "
                "land doesn't flinch from that. This is quieter. Older. "
                "Something the fighting stirred up rather than caused."
            ),
        },
        "the_quilboar_war": {
            "label": "Could the quilboar war be the cause?",
            "response": (
                "Maybe. War disturbs more than the ground it's fought on - "
                "old wards weaken, old things wake up when the land around "
                "them stops being quiet. I don't know if the Bristleback and "
                "Razormane know what they're shaking loose. I don't think "
                "they'd care if they did."
            ),
        },
        "should_we_intervene": {
            "label": "Should we intervene?",
            "response": (
                "Not yet. Not until I understand what I'm feeling well "
                "enough to name it. Rushing north to fight a feeling gets "
                "warriors killed for nothing. But keep your eyes open out "
                "there. If it's what I fear, we'll need warning, not just "
                "warriors."
            ),
        },
    },
    "org_kranals_thanks": {
        "the_farms_history": {
            "label": "What's the history of the farm?",
            "response": (
                "Kranal's held that ground since before Orgrimmar had proper "
                "walls. Started with just him and his children, a handful of "
                "pigs, and more stubbornness than sense. It's grown since - "
                "real stopping point now, not just one orc's homestead."
            ),
        },
        "the_road_between": {
            "label": "Why does the road matter so much?",
            "response": (
                "Orgrimmar to Crossroads is a long stretch with not much "
                "shelter on it. Grol'dom Farm breaks that stretch in half. "
                "Lose the farm and every caravan running that road takes "
                "twice the risk. Small places hold up big roads more than "
                "people realize, until they're gone."
            ),
        },
        "what_kranal_needs": {
            "label": "What does Kranal actually need?",
            "response": (
                "Less flattery, more supplies, is what he'd say if he were "
                "here. Tools, feed for the pigs, someone to keep the "
                "quilboar off his fences. Go ask him yourself next time "
                "you're near Lushwater - he'll tell you straight, no "
                "diplomacy wasted on it."
            ),
        },
    },
    "taurajo_spiritcarvers_balance": {
        "the_three_wars": {
            "label": "What three wars do you mean?",
            "response": (
                "Bristleback against Razormane, first - quilboar spilling "
                "quilboar blood over ground neither truly owns. Dwarves "
                "digging into land that was never offered to them, second. "
                "And beneath it all, something old waking in the earth "
                "south of here - the silithid don't fight for territory the "
                "way the others do. They fight because they're hungry, and "
                "hunger doesn't negotiate."
            ),
        },
        "what_it_means": {
            "label": "What does it mean for the land?",
            "response": (
                "Land remembers violence longer than people do. Every war "
                "leaves a scar, and three wars at once, close together, "
                "leaves scars that overlap. I don't know yet if the land "
                "can heal from that or if it just... changes. Becomes "
                "something else. That's what troubles me most - not the "
                "fighting itself, but what's left after."
            ),
        },
        "the_path_forward": {
            "label": "What should we do about it?",
            "response": (
                "Watch. Listen. Don't assume every war is ours to end just "
                "because we have the strength to end one side of it. Camp "
                "Taurajo can't fight three wars at once, and trying would "
                "just make us the fourth scar. Better to choose carefully "
                "where our strength actually helps, and let the rest run "
                "its course. That's not easy counsel to give. It's the "
                "honest one, though."
            ),
        },
    },
}


# --------------------------------------------------------------------------------------------------
# PER-ZONE TOPIC MODULES
#
# Everything above is authored directly in this file, which was fine while six quests used dialogue.
# It does not survive several content passes running at once: three authors appending to one dict in
# one file is a merge conflict at best and a silently dropped zone at worst, and the Stranglethorn
# passes all skipped dialogue objectives entirely rather than touch this file - which is why 56
# quests across three zones use four objective types out of seven.
#
# So a zone can own its own module instead. Drop a world/quest_dialogue_<zone>.py exporting a
# QUEST_TOPICS dict in exactly the shape above, add its name below, and it merges in at import.
# Nobody edits anybody else's file and the races are gone.
#
# A later module silently overwriting an earlier module's quest would be the same class of invisible
# bug this codebase keeps producing, so a collision raises instead.
# --------------------------------------------------------------------------------------------------
_ZONE_TOPIC_MODULES = (
    "stranglethorn_north",
    "stranglethorn_central",
    "stranglethorn_south",
    "shimmering_flats",
    "tanaris",
    "abyssal",
    "glittervein",
    "lashings",
    "crossroads",
    "black_strand",
    "tempest",
)

for _mod_name in _ZONE_TOPIC_MODULES:
    try:
        _mod = __import__(f"world.quest_dialogue_{_mod_name}", fromlist=["QUEST_TOPICS"])
    except ImportError:
        # A zone listed before its content lands is normal, not an error. get_topic returns None
        # for unauthored topics by design, and the dialogue screen renders no button for them.
        continue
    for _qid, _topics in getattr(_mod, "QUEST_TOPICS", {}).items():
        if _qid in QUEST_TOPICS:
            raise RuntimeError(
                f"quest_dialogue: {_qid} is defined in both quest_dialogue_{_mod_name} and an "
                f"earlier source. Topic content is keyed by quest_id, so one would silently "
                f"replace the other."
            )
        QUEST_TOPICS[_qid] = _topics
del _mod_name


def get_topic(quest_id, topic_id):
    """The {"label", "response"} dict for one topic, or None if this
    quest/topic_id combination has no authored content - callers should
    treat None as "don't show this topic" rather than crash, in case a
    quest's objective.topics list and this module's content ever drift
    out of sync (e.g. a topic added to the JSON before its text is
    written)."""
    return QUEST_TOPICS.get(quest_id, {}).get(topic_id)


def get_all_topics(quest_id):
    """Ordered list of (topic_id, label) for every topic authored for
    this quest - what the dialogue screen actually renders as buttons.
    Order follows QUEST_TOPICS's own dict insertion order (Python 3.7+
    guarantees this), which is the natural/intended ask order even
    though it isn't enforced - see QuestObjective.topics_asked."""
    topics = QUEST_TOPICS.get(quest_id, {})
    return [(tid, data["label"]) for tid, data in topics.items()]
