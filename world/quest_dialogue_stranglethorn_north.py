"""
Topic content for the DIALOGUE objectives in data/quests/stranglethorn_north.json.

Merged into world/quest_dialogue.QUEST_TOPICS at import by that module's
_ZONE_TOPIC_MODULES loop - this file is owned by the Northern Stranglethorn
pass alone and nobody else appends to it, which is the whole reason it exists
(three content passes editing one shared dict is how a zone's dialogue goes
missing without anybody noticing).

Shape is exactly world/quest_dialogue.py's:
    QUEST_TOPICS[quest_id][topic_id] = {"label": ..., "response": ...}

Three quests use dialogue, and each one is here because the content IS the
conversation - there is nothing to fetch and nothing to kill that would say it:

  stn_nothing_they_have_fought_climbs   Drillmaster Ukko rewrote his syllabus
                                        once, three years ago, and the reason
                                        is the people the airship brings him.
  stn_what_the_pens_know                Beast-Handler Kozza has read something
                                        real off her raptors and has no way to
                                        put it in a report an overseer accepts.
  stn_two_roosts_one_ledger             Wind-Rider Ghulrak, at the far end of
                                        the cross-zone flight thread, on what
                                        Hillsbrad looks like from the air and
                                        who actually gets blamed for the fences.

Plain ASCII, same as the quest text source - the game font has no curly quotes.
"""

QUEST_TOPICS = {
    # -----------------------------------------------------------------------------------------------
    # Drillmaster Ukko, Grom'gol. Orc, gruff and fair; the camp isn't.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stn_nothing_they_have_fought_climbs': {
        'what_climbs': {
            "label": 'What out here climbs?',
            "response": (
                'Everything worth worrying about. Thornback apes come down a trunk faster than you can climb a '
                'ladder. Coilvine pythons live in the canopy and drop the last few feet. A greenpelt runs up a '
                "buttress root like it's a staircase. You were taught a fight has a front, two flanks and a back."
                ' This jungle has a roof as well, and nobody on that airship was given a word for it.'
            ),
        },
        'what_the_drill_is_for': {
            "label": "What's the drill actually for, then?",
            "response": (
                "Looking up, and that's all I added. I used to drill a battle line: shields even, spears level, "
                'hold your ground and let them break on you. A line is for open fields, and there are no fields '
                'in Stranglethorn. So now I drill the glance upward, twice a minute, every minute, until a '
                "recruit does it in his sleep and resents me for it. The ones who resent me live, and I've made "
                'peace with that.'
            ),
        },
        'who_you_get': {
            "label": 'Who does the airship give you?',
            "response": (
                "Whoever's standing on the berth stair when it leaves. I had a sergeant who said your sort "
                "couldn't be taught the canopy. He was wrong, but he wasn't stupid, and that's the uncomfortable "
                "part. You can be taught anything, but nobody can assume what you know. I don't ask a recruit "
                "where he's from. I ask what he's stood under, and most of you have stood under nothing but open "
                "sky, and sky doesn't drop on a man. Half this camp says that a lot less kindly than I just did. "
                'I used to correct them, but I got tired.'
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # Beast-Handler Kozza, Grom'gol. Troll, full dialect, unsentimental.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stn_what_the_pens_know': {
        'the_difference': {
            "label": "Tame and fed. What's the difference?",
            "response": (
                'Tame is a promise you made up and told yourself da animal agreed to. Fed is a trade, and da '
                "animal knows it. She knows what she gets and when, and as long as dat holds, she'll let you "
                "stand in da pen with her and won't open you up. Da day it stops holdin', she ain't betrayin' "
                "you, mon. She's just done tradin'. Every handler who ever got torn open thought he had a "
                'promise.'
            ),
        },
        'the_raptors_on_the_road': {
            "label": 'What do your birds hear out on the road?',
            "response": (
                "Dey go quiet, da same day every week, from mid-mornin', and dey all face da same way, up da road"
                " toward da crag. Quiet ain't fear. A predator makes dem loud and sends dem at da rail. Quiet is "
                "what dey do for somethin' dey've looked at and decided ain't theirs to fight. Somethin' with a "
                "lot of feet, movin' slow, goin' uphill at da same hour every week, like it has a man with a book"
                " countin' it out. Dat's all I've got."
            ),
        },
        'what_she_will_not_do': {
            "label": "What won't you do?",
            "response": (
                "Dere's three tings. I won't name one of dose birds. I won't put a bird's opinion in front of da "
                "overseer as fact, because she'll ask for a number and den I'm on paper bein' wrong. And I won't "
                "let dis camp use my pens as a watchtower. Da day dey do, da feed stops bein' feed and becomes a "
                "line in a ledger, and somebody upstairs can always cut a line. Den I've got hungry raptors and a"
                " camp dat's surprised about it."
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # Wind-Rider Ghulrak, Tarren Mill. Orc, dry, flown everything twice.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stn_two_roosts_one_ledger': {
        'fences_from_the_air': {
            "label": 'What does Hillsbrad look like from up there?',
            "response": (
                "Fences, all of it. You don't see how much of a country is fences until you're above it with "
                'nothing else to look at. Every one of them was argued over. Men have been buried over which side'
                " of a fence a cow was standing on, and the fence is still up and the men aren't. Your goblin's "
                'route crosses hundreds of them in the last hour of the flight, and not one will be moved for '
                'him.'
            ),
        },
        'why_not_bats': {
            "label": 'Why not fly bats the whole way?',
            "response": (
                "Because a bat doesn't need to see the tower and a wyvern does. A bat comes in by ear, through "
                "cloud and rain and dark, and doesn't care whether anyone lit anything. A wyvern won't land on a "
                "roost it can't see, and over that middle stretch there's nothing to see, so the bird keeps "
                "flying. A bird that keeps flying after it's spent ends up in the water. That's why I want the "
                'Forsaken tower lit. Not for the route, for the bird.'
            ),
        },
        'what_the_jungle_sends_north': {
            "label": 'Who comes north on your tower?',
            "response": (
                'Couriers, mostly, and lately you lot. You come up out of that jungle asking for places by names '
                "that aren't on any map I own, and I set you down at the mill, and you stand in the yard staring "
                "at a waterwheel like somebody's moved your house. Three years, and you still ask. Half the "
                "garrison here will tell you the fences came down the year the sky changed, but they didn't. They"
                ' came down the year the Syndicate worked out nobody was watching. But a man would rather blame '
                "the sky than a neighbour he has to keep living beside. I charge you all the same rate, if that's"
                ' any comfort.'
            ),
        },
    },
}
