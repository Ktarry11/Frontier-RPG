"""
Topic content for The Lashings' DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. A topic named in an objective and missing here is a
quest that cannot be finished and does not look broken.

FOUR TOPICS, AND THEY ARE THE ARGUMENT THE PORT HAS NOT BEEN HAVING. Steamwheedle has spent twenty
years deciding the Southsea are somebody else's problem, and what changed is not the pirates - the
town doubled in three years when Gadgetzan emptied into it, and a port that has doubled has twice
as much going out and the same four berths. Ardessa Rake did not get greedier. The town got
thinner.

THE LAST TWO ARE DELIBERATELY NOT TRIUMPHANT. Senna Coil gets what she asked for and says out loud
that the port will take the cove's trade within a month and call it recovery. Hesper Dunn files a
line in a book. That is what the end of a twenty-year problem actually looks like from inside a
harbour office, and anything louder would be a different town.
"""

QUEST_TOPICS = {
    "lsh_four_berths": {
        "lsh_the_cove": {
            "label": "Ask Senna what is actually up the coast.",
            "response": (
                "Nine hulls, lashed together, four miles north. You can see the masts from the "
                "Upper Yard on a clear day and most of this town has stopped noticing them the "
                "way you stop noticing a hill.\n\nThey came in one at a time over about twenty "
                "years. A hull that is too far gone to sail and too good to burn gets rafted "
                "alongside and stripped slowly, and then somebody moves onto it because it is "
                "dry, and then it is not a wreck any more, it is an address.\n\nI have the "
                "soundings for that cove in this office. It is deep enough to lie a galleon in "
                "and it has one way in. Twenty-two years and nobody has ever gone up there with a "
                "serious intention, because four berths cannot be spared for a war and because "
                "they take cargo rather than people, mostly, and mostly is a word this port has "
                "been living behind for a very long time."),
        },
        "lsh_the_arithmetic": {
            "label": "Ask why it has become a problem now.",
            "response": (
                "Because it has not. That is the part I cannot get the yard to hear.\n\nThey take "
                "about one sailing in six. They took about one in six twenty years ago. Ardessa "
                "Rake has not got greedier, she has not got bolder, and as far as I can tell she "
                "has not had a new idea since before I had this post.\n\nWhat changed is us. This "
                "town doubled in three years when Gadgetzan emptied into it. Twice the people, "
                "twice the freight going out, and the same four berths and no slack in anything. "
                "A sixth was an annoyance when we had room. A sixth is the difference between a "
                "sailing schedule and a queue when we do not.\n\nSo the honest version is that "
                "the pirates are exactly where they were and we walked into them. I have said "
                "that at two meetings and it has not gone well either time."),
        },
    },
    "lsh_the_masts_are_gone": {
        "lsh_after": {
            "label": "Ask Rullo what happens to the prices now.",
            "response": (
                "A sixth for the cove. That is what we called it and nobody ever wrote it down, "
                "it was just IN the number, the way weather is in a number.\n\nI have spent this "
                "morning taking it out of forty years of pricing and I will tell you something I "
                "did not expect: it made me feel strange. Not glad. Strange.\n\nBecause here is "
                "what I have worked out while I was doing it. I have been telling people for "
                "three years that there is nothing coming back west worth the axle, and that is "
                "TRUE, and it is also a thing I have been saying instead of the real reason, "
                "which is that I did not want to argue about insurance on a road nobody was "
                "robbing and a coast where everybody was.\n\nI will run a cart west now. Out to "
                "that pan, to the town with six customers that has wanted one for three years. "
                "Not because the arithmetic changed. Because I have run out of sentences to put "
                "in front of it."),
        },
    },
    "lsh_the_last_column": {
        "lsh_two_columns": {
            "label": "Ask Hesper what she is going to write.",
            "response": (
                "One line. Date, vessel - and there is no vessel, so a dash - cargo, and a "
                "dash, and then the two columns: which side of town it came from and which side "
                "it went to.\n\nFor this one both of those are the same word, which has never "
                "happened in my book before and I have had to think about how to rule it.\n\nYou "
                "will want to know why that is worth doing at all. Here it is.\n\nIn four years "
                "somebody is going to say there was never a cove. Or that it was nothing much. Or "
                "that it came apart on its own and this port had very little to do with it, which "
                "will be popular because it is comfortable and because the yard will by then be "
                "handling a third more freight and will not want to examine where the room came "
                "from.\n\nAnd I will have a line, with two names on it, written on the day.\n\n"
                "That is the whole of my profession. Something enormous happens, and the only "
                "part of it still standing in forty years is a book two people signed while "
                "everybody else was busy being relieved."),
        },
    },
}
