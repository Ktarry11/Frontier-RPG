"""
Topic content for Tanaris's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. QuestObjective.topics is only the completion condition;
the dialogue screen renders a button per AUTHORED topic, so a topic named in an objective and
missing here is a quest that cannot be finished and does not look broken.

THE FOUR HERE ARE ALL THINGS SOMEBODY HAS BEEN WAITING YEARS TO BE ASKED, which is the only test
that earns a dialogue objective: the content IS the conversation, and the having-asked is the event.

  tan_berth_signed      Hesper keeps two columns nobody has ever asked her about, and the town has
                        just, for the first time, needed a document from her.
  tan_gad_mazzic        Old Mazzic insists he did not LEAVE Gadgetzan. Three years and nobody in
                        Steamwheedle has asked him to explain the distinction.
  tan_zf_the_offer      A surgeon wants one person in town to have an opinion about the Sandfury
                        that they arrived at by looking rather than by drinking.

VOICE: goblin, mercantile, and fast - but Mazzic is old and slow and says the hard sentence plainly,
and Hesper is a clerk who has had three years to get the wording right and has.
"""

QUEST_TOPICS = {
    "tan_berth_signed": {
        "tan_topic_columns": {
            "label": "Ask Hesper what the last two columns are for.",
            "response": (
                "Which half of town a thing came from, and which half it went to.\n\nPeople assume "
                "I keep them to be unpleasant. Grizzel thinks it. She has never said so and she "
                "thinks it.\n\nI keep them because in four years somebody is going to stand in this "
                "room and say this town was always like this - that there was never a quay and a "
                "yard, that it was all just Steamwheedle, that nobody was ever treated as having "
                "arrived.\n\nAnd I would like to be able to put a book on the table. Not to win the "
                "argument. So that whoever is right can be right with something in front of them."),
        },
        "tan_topic_both_sides": {
            "label": "Ask whether the two halves have ever signed anything together before.",
            "response": (
                "Not once. I went back through my mother's books as well and not once there "
                "either, though that is a shorter span than people think.\n\nContracts, yes. The "
                "quay buys from the yard every day of the week and there is paper for all of it. "
                "But a contract is two people who want different things agreeing on a price.\n\n"
                "This is a works order. Two signatures, one job, one outcome, and neither of them "
                "gets a thing the other one does not.\n\nI have been a clerk for thirty years and "
                "I did not expect to be moved by a works order."),
        },
    },

    "tan_gad_mazzic": {
        "tan_topic_carried": {
            "label": "Ask Old Mazzic about leaving Gadgetzan.",
            "response": (
                "I did not leave.\n\nI know how that sounds. Everybody in this port says we left - "
                "the Gadgetzan crowd, the ones who came over, like it was a Tuesday and a "
                "decision and we all talked it through.\n\nSome of us decided. Bix decided. He "
                "closed his shop properly and put the key somewhere and loaded three carts. Good "
                "for him, honestly.\n\nI was carried out on a door by two people whose names I "
                "never got, because by then I had not had water in two days and I was not making "
                "decisions about anything.\n\nSo when the quay crowd say we arrived - I did not "
                "arrive. I was BROUGHT. It is a different sentence and I would like it used."),
        },
        "tan_topic_the_wells": {
            "label": "Ask about the wells.",
            "response": (
                "Nine of them. I can name all nine and I drank from four.\n\nThe shallow ones went "
                "first, in one season, and everybody said drought and everybody was wrong, because "
                "a drought takes the river and we did not have a river, we had a water TABLE and "
                "nobody in that town knew the difference including me.\n\nThe deep well held "
                "another year. That year is the one nobody talks about. Four hundred people and "
                "one well and a wall round it, and a queue, and a number stamped on a token.\n\n"
                "Three years I have been here and not one person on that quay has asked me about "
                "the wells. They have asked me about the wall. Everybody asks about the wall."),
        },
    },

    "tan_zf_the_offer": {
        "tan_topic_ask_them": {
            "label": "Tell the surgeon what you made of the Sandfury.",
            "response": (
                "[Wick Ambrose listens to the whole of it without writing anything down, which for "
                "him is unusual.]\n\nEleven marks. Four hundred years. And the last one is a foot "
                "and a half below the one before it.\n\nI am not going to tell you they are "
                "friendly. You had to go through a great many of them to stand on that step and I "
                "sent you knowing it.\n\nWhat I will say is this. For three years this town has "
                "explained the Sandfury to itself at the bar, by people who have never been within "
                "a mile of them, and the explanation has always been that they are what is left "
                "over. Leftovers of a thing that happened to them.\n\nThey have a four-hundred-year "
                "water record cut into a stone. We had a rates ledger and nine wells and we lost "
                "the lot in two seasons.\n\nI would not say that too loudly on the quay. But it is "
                "what you came back with, and somebody in this town should have it."),
        },
    },
}
