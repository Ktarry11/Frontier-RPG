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
                "Nine hulls, lashed together, four miles north. You can see the masts from the Upper Yard "
                "on a clear day, and most of this town has stopped noticing them the way you stop noticing "
                "a hill.\n\nThey came in one at a time over about twenty years. A hull that's too far gone "
                "to sail and too good to burn gets rafted alongside and stripped slowly. Then somebody "
                "moves onto it because it's dry, and after that it's an address.\n\nI've got the soundings "
                "for that cove in this office. It's deep enough to lie a galleon in, and it has one way in. "
                "Twenty-two years and nobody has ever gone up there with a serious intention, because four "
                "berths can't be spared for a war, and because they take cargo rather than people, mostly. "
                "Mostly is a word this port has been living behind for a very long time."),
        },
        "lsh_the_arithmetic": {
            "label": "Ask why it has become a problem now.",
            "response": (
                "Because it hasn't, and that's the part I can't get the yard to hear.\n\nThey take about one "
                "sailing in six. They took about one in six twenty years ago. Ardessa Rake hasn't got "
                "greedier or bolder, and as far as I can tell she hasn't had a new idea since before I had "
                "this post.\n\nWhat changed is us. This town doubled in three years when Gadgetzan emptied "
                "into it. That's twice the people and twice the freight going out, with the same four berths "
                "and no slack in anything. A sixth was an annoyance when we had room. Now that we don't, a "
                "sixth turns a sailing schedule into a queue.\n\nSo the honest version is that the pirates "
                "are exactly where they were and we walked into them. I've said that at two meetings, and it "
                "hasn't gone well either time."),
        },
    },
    "lsh_the_masts_are_gone": {
        "lsh_after": {
            "label": "Ask Rullo what happens to the prices now.",
            "response": (
                "A sixth for the cove. That's what we called it, and nobody ever wrote it down. It was just "
                "in the number, the way weather is in a number.\n\nI've spent this morning taking it out of "
                "forty years of pricing, and I'll tell you something I didn't expect. It didn't make me glad, "
                "it made me feel strange.\n\nHere's what I worked out while I was doing it. I've been telling "
                "people for three years that there's nothing coming back west worth the axle, and that's "
                "true. It's also a thing I've been saying instead of the real reason, which is that I didn't "
                "want to argue about insurance on a road nobody was robbing and a coast where everybody "
                "was.\n\nI'll run a cart west now, out to that pan, to the town with six customers that's "
                "wanted one for three years. The arithmetic hasn't changed. I've just run out of sentences "
                "to put in front of it."),
        },
    },
    "lsh_the_last_column": {
        "lsh_two_columns": {
            "label": "Ask Hesper what she is going to write.",
            "response": (
                "It'll be one line. There's the date, then the vessel, and there's no vessel, so I'll rule "
                "it through. Then the cargo, ruled through as well, and then the two columns: which side of "
                "town it came from and which side it went to.\n\nFor this one both of those are the same "
                "word. That's never happened in my book before, and I've had to think about how to rule "
                "it.\n\nYou'll want to know why that's worth doing at all, so here it is.\n\nIn four years "
                "somebody is going to say there was never a cove. Or that it was nothing much. Or that it "
                "came apart on its own and this port had very little to do with it, which will be popular "
                "because it's comfortable, and because the yard will by then be handling a third more "
                "freight and won't want to examine where the room came from.\n\nAnd I'll have a line, with "
                "two names on it, written on the day.\n\nThat's the whole of my profession. Something "
                "enormous happens, and the only part of it still standing in forty years is a book two "
                "people signed while everybody else was busy being relieved."),
        },
    },
}
