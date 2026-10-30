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
    # ---------------------------------------------------------------------------------------------
    # Drillmaster Ukko, Grom'gol. Orc, gruff, and the only man in the camp who has had to change how
    # he does his job because of who arrived. He is fair about it, which is what gives the third
    # topic its edge: the camp is not fair about it and he has stopped correcting them.
    # ---------------------------------------------------------------------------------------------
    "stn_nothing_they_have_fought_climbs": {
        "what_climbs": {
            "label": "What out here climbs?",
            "response": (
                "Everything worth worrying about. The thornbacks come down a "
                "trunk faster than you go up a ladder. The coilvines live in "
                "the canopy and drop the last of the distance. A greenpelt "
                "goes up a buttress root like it is a stair, because to a "
                "greenpelt it is a stair. You were taught that a fight has a "
                "front and two flanks and a back. This jungle has a roof, and "
                "the roof is a direction, and nobody on that airship was "
                "issued a word for it."
            ),
        },
        "what_the_drill_is_for": {
            "label": "What is the drill actually for, then?",
            "response": (
                "Looking up. That is it. That is the whole of what I added. I "
                "used to drill a line - shields even, spears level, hold the "
                "ground and let them break on you. A line is for a field. "
                "There is no field in Stranglethorn and there never will be. "
                "So now I drill the glance. Twice a minute, every minute, "
                "until a recruit does it in his sleep and resents me for it. "
                "The ones who resent me live. I have made peace with being "
                "resented."
            ),
        },
        "who_you_get": {
            "label": "Who does the airship give you?",
            "response": (
                "Whoever is standing on the berth stair when it leaves. I had "
                "a sergeant here who said your sort could not be taught the "
                "canopy. He was wrong and he was also not stupid, which is the "
                "uncomfortable part. You can be taught anything. You cannot be "
                "assumed. I do not ask a recruit where he is from. I ask what "
                "he has stood under, and most of you have stood under nothing "
                "but sky, and sky does not drop on a man. Half this camp puts "
                "that same thought a good deal less kindly than I just did. I "
                "used to correct them. I got tired."
            ),
        },
    },
    # ---------------------------------------------------------------------------------------------
    # Beast-Handler Kozza, Grom'gol. Troll, light dialect, and the one giver in the camp whose
    # evidence is an animal's opinion - which is why she needs a second person to have heard it.
    # The middle topic quietly corroborates the supply-line chain: regular traffic, uphill, slow.
    # ---------------------------------------------------------------------------------------------
    "stn_what_the_pens_know": {
        "the_difference": {
            "label": "Tame and fed. What is the difference?",
            "response": (
                "Tame is a promise and fed is a trade. A promise is a ting you "
                "made up and told yourself de animal agreed to. A trade, de "
                "animal knows. She knows what she gets and she knows when, and "
                "as long as dat holds she will let you stand inside de pen with "
                "her and she will not open you up. De day it stops holding, she "
                "is not betraying you, mon. She is just done trading. Every "
                "handler who ever got opened up thought he had a promise."
            ),
        },
        "the_raptors_on_the_road": {
            "label": "What do your birds hear out on the road?",
            "response": (
                "Dey go quiet. Same day of de week, from mid-morning, and dey "
                "all face de same way - up de cutline, north, toward de crag. "
                "Quiet is not fear. A predator makes dem loud, makes dem come "
                "at de rail. Quiet is what dey do for something dey have looked "
                "at and decided is not theirs to fight. Something with a lot of "
                "feet, going slow, going uphill, and going at de same hour every "
                "week like it has got a man with a book counting it out. Dat is "
                "what I have. Dat is all I have."
            ),
        },
        "what_she_will_not_do": {
            "label": "What will you not do?",
            "response": (
                "Three tings. I will not name one of dose birds. I will not put "
                "a bird's opinion in front of de overseer as a fact, because she "
                "will ask me for a number and den she will have me on paper being "
                "wrong. And I will not let dis camp start using my pens as a "
                "watchtower. De hour dey do dat, de feed stops being feed and "
                "becomes a line in a ledger, and a line in a ledger is a ting "
                "somebody upstairs can cut. Den I have hungry raptors and a camp "
                "that is surprised about it."
            ),
        },
    },
    # ---------------------------------------------------------------------------------------------
    # Wind-Rider Ghulrak, Tarren Mill - the far end of the cross-zone flight thread. An orc on a
    # tower in Hillsbrad who has been flying transplants north for three years and has worked out
    # who the fences really belong to. The third topic is this pass's most direct look at the
    # resentment, and it is a native refusing to join in with it rather than an aside about it.
    # ---------------------------------------------------------------------------------------------
    "stn_two_roosts_one_ledger": {
        "fences_from_the_air": {
            "label": "What does Hillsbrad look like from up there?",
            "response": (
                "Fences. All of it, fences. You do not see how much of a country "
                "is fences until you are over it with nothing else to look at. "
                "Every one of them was argued about. Men have gone in the ground "
                "over which side of a fence a cow was standing on, and the fence "
                "is still up and the men are not. Your goblin's route crosses "
                "about four hundred of them in the last hour of the flight and "
                "not one of them will be moved for him."
            ),
        },
        "why_not_bats": {
            "label": "Why not just fly bats the whole way?",
            "response": (
                "Because a bat does not need to see the tower and a wyvern does. "
                "A bat comes in on its ears, in cloud, in rain, in the dark, and "
                "it does not care whether anybody lit anything. A wyvern will not "
                "put down on a roost it cannot pick out, and over that middle "
                "stretch there is nothing to pick out, so the bird keeps flying, "
                "and a bird that keeps flying when it is finished comes down in "
                "the water. That is why I want the dead man's tower lit. Not for "
                "the route. For the bird."
            ),
        },
        "what_the_jungle_sends_north": {
            "label": "Who comes north on your tower?",
            "response": (
                "Couriers, mostly. Lately, your lot. They come up out of that "
                "jungle and they ask me for places by names that are not on any "
                "map I own, and I set them down at the mill, and they stand in "
                "the yard looking at a waterwheel like somebody has moved their "
                "house. Three years and they still ask. I have stopped asking "
                "them back. Half the garrison here will tell you the fences came "
                "down the year the sky changed. They did not. They came down the "
                "year the Syndicate worked out nobody was watching them. But a "
                "man would rather blame a sky he saw change than a neighbour he "
                "has to go on living beside. I charge you all the same rate, if "
                "that is any comfort."
            ),
        },
    },
}
