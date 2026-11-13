"""
Topic content for The Black Strand's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_abyssal.py for why.

Three topics, and they are the two sides of one thing. Vault-Keeper Aldis tells it the way the
town tells it; Brannoc, who sits at the gate's brazier, tells it the way the shift tells it. The
quests that follow (tools/build_black_strand_quests.py) are about finding out that both of them
are telling the truth.

Plain speech (Kyle, 13 Nov 2026: "Don't use weird AI tics"). These are people explaining something
painful to a stranger.
"""

QUEST_TOPICS = {
    "bst_names_in_the_book": {
        "bst_who_was_put_out": {
            "label": "Ask who was put out of the gate.",
            "response": (
                "A whole shift. Forty people, miners and their foreman.\n\nThree years ago they "
                "were working the low gallery, the deepest one we had. Vigdis had condemned it "
                "the month before. She said the roof was sound for a year at most and nobody "
                "should be under it.\n\nSomebody sent a crew in anyway. Then came the day the ground "
                "shook. You'll know the one, it was the day everything changed topside. The "
                "gallery came down on a full day shift and eleven people died.\n\nThe Thane asked who gave the order. Not "
                "one of the forty would say. So he put them all out."),
        },
        "bst_the_gallery": {
            "label": "Ask why nobody would say who gave the order.",
            "response": (
                "I've asked myself that for three years.\n\nThe Thane decided they were "
                "protecting each other, and that made them all guilty. He's not a cruel man. "
                "He'd just buried eleven people and he wanted someone to answer for it.\n\nI "
                "think they were frightened. Their foreman was a man called Durn, and he wasn't "
                "someone you spoke against. He docked pay. He had people moved to the worst "
                "headings. One lad who complained about him had an accident with a cart.\n\nI "
                "couldn't prove any of that, and the Thane doesn't act on what an old woman "
                "thinks. So the names are still in my book, and the people are in the old "
                "diggings."),
        },
    },
    "bst_brannocs_shift": {
        "bst_brannocs_side": {
            "label": "Ask Brannoc what happened.",
            "response": (
                "I was a carter on the day shift. Forty of us.\n\nThat morning Durn picked "
                "nine and took them down to the low gallery. Everyone knew it was condemned. "
                "He said there was a seam in there worth a year's wages and he'd have it out "
                "before the roof went. The rest of us he sent to the north drift, same as "
                "always.\n\nWe heard it come down. It's a sound you don't forget.\n\nDurn "
                "walked out of the dust without a mark on him. He stood us in a line and told "
                "us that if the Thane asked, nobody had given any order, the men had gone in "
                "on their own. He said anyone who told it differently would be next under a "
                "roof.\n\nWe believed him. So we said nothing, and the Thane took that to mean "
                "we were all in it.\n\nI should have spoken. I know that. I've had three years "
                "to know it."),
        },
    },
}
