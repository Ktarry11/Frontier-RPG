"""
Topic content for the Abyssal Sands' DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. QuestObjective.topics is only the completion condition;
the dialogue screen renders a button per AUTHORED topic, so a topic named in an objective and
missing here is a quest that cannot be finished and does not look broken.

THE VOICE (Kyle, 13 Nov 2026: "Don't use weird AI tics"). Eight working people in tents, talking
the way people talk: contractions, the place and the animal named, a reason given, and no line
written to sound clever. Rewritten on 13 Nov with tools/rewrite_abyssal_voice.py, which holds the
quest text these go with.

THE FACTS THESE AGREE ON. The pits began with the Integration, three years ago. The camp has been
out two years. The Throats are in the southwest, Underlight in the southeast, and the water under
the field drains east toward the Glittervein.
"""

QUEST_TOPICS = {
    # ================= THE LINE =================
    "ab_fourth_peg": {
        "ab_the_pegs": {
            "label": "Ask why the camp is called Fourth Peg.",
            "response": (
                "The camp's pitched round the fourth survey peg. The first three are gone or "
                "useless.\n\nFirst Peg fell in with the ground under it in our second season. "
                "Nobody was standing there.\n\nSecond Peg's still on the lip of the Wide Sink, "
                "marking ground that fell away. I haven't had it moved and I couldn't tell you "
                "why.\n\nWe moved Third Peg ourselves, because Hask didn't like the sound of the "
                "hardpan. That spot fell in four days later. He still can't explain how he knew "
                "in words I can put in the book.\n\nFourth Peg's held seven months. We try not to "
                "say that too loudly."),
        },
        "ab_the_job": {
            "label": "Ask what the camp is for.",
            "response": (
                "The port wants a road south. Rullo Tack at Steamwheedle has wanted one for three "
                "years. He'll tell you there's no trade down there worth an axle, and he's right "
                "about that. The trade was never what stopped it, though. The ground keeps "
                "falling in.\n\nSo the port paid for a survey, and they think they're paying me "
                "to find a route. I'm finding out if any route can last, and they haven't asked "
                "for that.\n\nI knew that when I signed. If they don't like the answer, I'll live "
                "with it."),
        },
    },
    "ab_is_it_possible": {
        "ab_the_answer": {
            "label": "Ask Peska for her answer.",
            "response": (
                "A road can be built across the Abyssal Sands. Nobody will lend money for it."
                "\n\nLenders want twenty years of safe ground. Four of my eleven pits are still "
                "moving. The Wide Sink is three years old and its rim moved eleven inches in four "
                "days last week.\n\nSo my answer to the port is to ask me again in ten years. I "
                "expect to lose the contract over it, and I've had two years to get used to that."
                "\n\nWhat bothers me more is that I don't know why it's happening. I can show you "
                "the ground's going. I can't tell you what's taking it, and a survey that can't "
                "say why is only half finished."),
        },
    },

    # ================= WHAT FELL IN =================
    "ab_on_the_box": {
        "ab_nineteen_mile": {
            "label": "Let Odd tell it.",
            "response": (
                "It was an ordinary afternoon. People expect me to say there was a warning, and "
                "there wasn't.\n\nWe were nineteen miles out of Gadgetzan on the old south road, "
                "four carts, and I was driving the second. The road was good. Twenty years of "
                "traffic had packed it hard.\n\nI heard a noise like a door shutting a long way "
                "off. Then the road in front of us was gone. The lead pair went in, the cart went "
                "after them, and I fell off the back.\n\nThe ground I landed on held. Four other "
                "people landed on ground that didn't, and that's all that separates us.\n\nI "
                "could hear the lead pair down there for a day and a half. Nobody asks about that "
                "part.\n\nThe camp talks about the ground the way you'd talk about weather. They "
                "have to, to do this work. When they start, I go for a walk."),
        },
    },

    # ================= WHAT CAME UP =================
    "ab_nine_have_floors": {
        "ab_the_rope": {
            "label": "Ask Vizzi about going down on a line.",
            "response": (
                "I've got a hundred and twenty feet of line and a harness Gorra made from kodo "
                "tack. Two people hold the top, and they have to keep their minds on it.\n\n"
                "People think the bottom's the dangerous end. I worry more about the top. If "
                "something comes up the rise at Hask, he has to choose between the rope and his "
                "own neck.\n\nI go down about forty feet. From there I can see if there's a floor "
                "and if it's sound. Peska's never asked for more than that."),
        },
        "ab_no_bottom": {
            "label": "Ask about the two without floors.",
            "response": (
                "I've let out the whole line in two pits and it's touched nothing. That's the "
                "Throats in the southwest and Underlight in the southeast.\n\nPeska writes that "
                "up as 'no bottom observed'. She's being careful, and it's true. I didn't see a "
                "bottom.\n\nI'd write 'don't go down'. She thinks a survey's there to record "
                "things. I think somebody's going to read it and then walk out to those pits, and "
                "they need a warning.\n\nIt's her book, so her wording stays."),
        },
    },

    # ================= THE GLASSWALL =================
    "ab_the_south_facing": {
        "ab_the_glass": {
            "label": "Ask the camp about the Glasswall.",
            "response": (
                "Twice a year the sun hits that face at the right angle and throws the afternoon "
                "back at us. It lasts forty minutes, and for that long this is the brightest "
                "place in Tanaris.\n\nTobbit calls it a hazard. He wrote a memo about it that "
                "nobody's read, and I doubt he's read it himself.\n\nHask thinks it's beautiful "
                "and stands out in it until somebody fetches him.\n\nOdd won't look at it. He's "
                "never said why and we've never asked.\n\nI like it because it comes on time. "
                "Nothing else out here does, and the ground won't even stay where you left it."),
        },
    },
    "ab_nothing_is_hot_enough": {
        "ab_the_glass": {
            "label": "Ask Peska how she is going to write up the Glasswall.",
            "response": (
                "It'll be the worst entry in the book, and I'll write it carefully anyway.\n\n"
                "Sand only melts in a furnace's heat. There's no volcanic rock within a hundred "
                "miles, and lightning doesn't melt sixty feet in a straight line. The face hasn't "
                "weathered, so it melted after the pit opened three years ago.\n\nSomething stood "
                "in that pit and made a furnace's heat, and I don't know what. The entry will say "
                "'cause unknown'.\n\nI've never written that under my name. With samples and a "
                "date it counts as a finding, so I'll have those."),
        },
    },

    # ================= UNDERLIGHT AND OUT =================
    "ab_everything_points_east": {
        "ab_the_east": {
            "label": "Have Peska list what points east.",
            "response": (
                "Everything I've got points east.\n\nSepp's revenants are cured in brine. The "
                "nearest brine is the Shimmering Flats, four days northwest, and the people there "
                "say their water went underground and headed east.\n\nHask found water animals in "
                "shrike crops, in a desert with no standing water.\n\nVizzi can't find the bottom "
                "of the Throats or of Underlight, and what climbs out of both is wet.\n\n"
                "Underlight's on our eastern edge, and the light in it gets a little brighter "
                "every season.\n\nI'm a surveyor, so I won't say what's causing it. I'll say "
                "those are separate findings and they all lead toward the Glittervein, east of "
                "here. It's a very large pit with water in it, and the goblins have had a camp at "
                "the bottom for two years."),
        },
    },
    "ab_carry_the_book": {
        "ab_the_east": {
            "label": "Ask why she will not carry the book herself.",
            "response": (
                "If I leave Fourth Peg for a fortnight, there'll be a fortnight missing from the "
                "readings. A record with a gap is worth a lot less.\n\nThat's the reason "
                "I'd give the port, and it's true.\n\nI've also spent two years not knowing why "
                "this is happening, and she knows. I'd like to find out if she's better at this than me, and I'd sooner not be in the room for it.\n\nI know how that sounds. I'm forty-one "
                "and I'd still sooner hear it secondhand.\n\nTake her the book. The dates in it "
                "are good work, whatever she makes of them."),
        },
    },
    "ab_the_answer_comes_back": {
        "ab_the_reply": {
            "label": "Ask Ulla what she put in the reply.",
            "response": (
                "The first three pages are sums. I did that on purpose. She'll want to check my "
                "working before she believes a word.\n\nThe fourth page says what it means, and "
                "she won't like it.\n\nThere's nothing wrong with her rock. That limestone sat on "
                "water for ten thousand years and held. The water's gone now, so the rock's "
                "falling in.\n\nEvery reading she's taken is right. She's been looking for the "
                "cause in the ground, and the cause is four days east of her and still drinking. "
                "Her pits will keep opening until it stops.\n\nI've put it as kindly as I can, "
                "and I'm no good at kind. She'd want it told straight anyway."),
        },
    },

    # ================= STANDALONE =================
    "ab_three_month_contract": {
        "ab_the_contract": {
            "label": "Ask Sepp why he stayed.",
            "response": (
                "It was a three-month contract. That was two years and two camps ago, and "
                "nobody's brought it up since.\n\nI could've left any time. It's a week's walk to "
                "the port and I'd have had a good story to tell.\n\nIt took me eight months to "
                "work out why I didn't. I want to be here when somebody finds out what's draining "
                "this desert.\n\nPeska might get recalled or sacked before then. Hask will follow "
                "the work wherever it goes. Vizzi's going to go down one pit too many. I can brew "
                "anywhere, so I can afford to wait, and I've never regretted staying."),
        },
    },
}
