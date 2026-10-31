"""
Topic content for the Abyssal Sands' DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. QuestObjective.topics is only the completion condition;
the dialogue screen renders a button per AUTHORED topic, so a topic named in an objective and
missing here is a quest that cannot be finished and does not look broken.

FOURTH PEG IS NOT STUCK, WHICH IS THE WHOLE TONAL DIFFERENCE from Lastwater. Ten people on a rock
in the Glittervein are deadlocked against each other; eight people in tents here could strike camp
and be gone in a day, and have, three times. Their argument is with the GROUND, and none of them
expects to win it. So these conversations are dry, specific and unromantic - the voice of people
who ran out of ways to make a sinkhole sound like an event about three years ago.

Two topics carry the thread:

  ab_the_answer  Peska saying the sentence no surveyor is ever paid to say.
  ab_the_east    What it costs her to admit that the answer to her question is four days away and
                 belongs to somebody else.
"""

QUEST_TOPICS = {
    # ================= THE LINE =================
    "ab_fourth_peg": {
        "ab_the_pegs": {
            "label": "Ask why the camp is called Fourth Peg.",
            "response": (
                "Because it is pitched round the fourth stake, and the first three are all in "
                "holes.\n\nFirst Peg went in with the ground under it in the second season. "
                "Nobody was standing on it, which is the only reason that sentence is dull.\n\n"
                "Second Peg is sitting on the lip of the Wide Sink being perfectly accurate about "
                "a place that is no longer there. I have not had it moved. I have thought about "
                "why I have not had it moved and I do not have a good answer.\n\nThird Peg we "
                "moved ourselves, because Hask did not like the hardpan. Four days later he was "
                "right. That is the only one we are proud of and he still cannot tell me how he "
                "knew in a way I can write in a book.\n\nFourth Peg has held seven months. We do "
                "not say that out loud much."),
        },
        "ab_the_job": {
            "label": "Ask what the camp is actually for.",
            "response": (
                "The port wants a road south. Rullo Tack out in Steamwheedle has wanted one for "
                "three years and he will tell you at length that there is nothing coming back the "
                "other way worth the axle, which is true and is also not why there is no road."
                "\n\nThere is no road because the ground keeps going.\n\nSo they funded a survey, "
                "and the survey they think they funded is 'find me a line'. The survey I am "
                "actually running is 'find out whether a line is possible'. Those produce "
                "different books and only one of them has ever been paid for.\n\nI took the "
                "contract knowing that. I will take the consequences knowing it too."),
        },
    },
    "ab_is_it_possible": {
        "ab_the_answer": {
            "label": "Ask Peska for the sentence.",
            "response": (
                "A road is possible.\n\nA road is not possible on a twenty-year bond, which is "
                "the only kind anybody will finance, because this field is still opening. Four of "
                "my eleven holes are still moving - the Wide Sink took eleven inches in four days "
                "last week and it is four years old and everybody thinks of it as finished.\n\n"
                "So the honest answer to 'can you build a road across the Abyssal Sands' is: ask "
                "me again in ten years.\n\nNobody has ever paid a surveyor to say that. I expect "
                "it will cost me the contract and I have had two years to make my peace with it, "
                "and the thing that actually bothers me is much smaller than that.\n\nI do not "
                "know WHY. I can tell you that the ground is going. I cannot tell you what is "
                "taking it, and a surveyor who cannot say why is a surveyor with a very good book "
                "and no finding."),
        },
    },

    # ================= WHAT FELL IN =================
    "ab_on_the_box": {
        "ab_nineteen_mile": {
            "label": "Let Odd tell it.",
            "response": (
                "It was an ordinary afternoon. I want to start there because everybody expects a "
                "sign and there was not one.\n\nNineteen miles out of Gadgetzan on the old south "
                "road, four carts, me on the second box. Good ground. Road ground - packed by "
                "twenty years of traffic, the best ground there is.\n\nThere was a noise like a "
                "door closing somewhere else. Then the front of the road was not there, and the "
                "lead pair were six lengths ahead of me and they went into it, and the cart "
                "followed them, and I came off the back of it.\n\nThe ground I landed on held. "
                "That is it. That is the entire difference between me and four other people and "
                "it is nothing I did.\n\nThe part nobody asks about is that I could hear the lead "
                "pair for about a day and a half.\n\nSo when the camp talks about the ground like "
                "it is weather - and they do, and they are right to, you cannot do this work "
                "otherwise - I let them. And I go and stand somewhere else for a bit."),
        },
    },

    # ================= WHAT CAME UP =================
    "ab_nine_have_floors": {
        "ab_the_rope": {
            "label": "Ask Vizzi about going down on a line.",
            "response": (
                "A hundred and twenty feet of line, a harness Gorra made out of kodo tack, and "
                "two people on the top who have to actually be paying attention.\n\nThat last "
                "part is the job. Everybody thinks the dangerous end is the bottom. The dangerous "
                "end is whether Hask is still holding the line in four minutes or whether "
                "something has come up the rise at him.\n\nI go down about forty feet. Far enough "
                "to see whether there is a floor and whether the floor is going anywhere, which "
                "is all Peska has ever asked for and more than anybody else has ever offered."),
        },
        "ab_no_bottom": {
            "label": "Ask about the two without floors.",
            "response": (
                "A hundred and twenty feet of line and it does not reach anything. Twice. Both on "
                "the east side.\n\nPeska logs that as 'no bottom observed', and she is being "
                "careful and she is right to be - I did not observe a bottom, that is all I can "
                "honestly say.\n\nI would log it differently. I would log it as 'do not'.\n\nWe "
                "have agreed to disagree about which of those is the job. She thinks a survey "
                "records. I think a survey is read by somebody who then walks out there, and what "
                "they need is a sentence that stops them.\n\nWe are both right and I am going to "
                "keep losing because it is her book."),
        },
    },

    # ================= THE GLASSWALL =================
    "ab_the_south_facing": {
        "ab_the_glass": {
            "label": "Ask the camp about the Glasswall.",
            "response": (
                "[Marda, and then most of the camp, at length.]\n\nTwice a year the sun gets the "
                "angle right and that face throws the whole afternoon back at us. Forty minutes, "
                "and for forty minutes this is the brightest place in Tanaris.\n\nTobbit calls it "
                "a hazard and has written a memorandum about it, which nobody has read, including "
                "Tobbit.\n\nHask calls it beautiful and will stand out in it until somebody makes "
                "him come in.\n\nOdd will not look at it. He has never said why and nobody has "
                "ever asked.\n\nI say it is the only thing out here that does anything on a "
                "schedule, and in a place where the ground itself cannot be relied on to stay "
                "where you left it, that is worth more than any of them think it is."),
        },
    },
    "ab_nothing_is_hot_enough": {
        "ab_the_glass": {
            "label": "Ask Peska how she is going to write up the Glasswall.",
            "response": (
                "Badly. I am going to write it up badly, and carefully, and it will be the worst "
                "entry in the book.\n\nSand goes to glass at about three thousand degrees. There "
                "is no volcanic rock within a hundred miles. Lightning does not do sixty feet in "
                "a straight line. And the face is unweathered, which means it happened after the "
                "hole opened, not before - so whatever did it was standing in a four-year-old "
                "sinkhole in the Abyssal Sands doing something at three thousand degrees.\n\nThe "
                "entry is going to read 'cause unknown'.\n\nI have never written that in a book "
                "with my name on it. Six samples and a date makes it a finding instead of an "
                "admission, which is the only comfort available and it is a thin one."),
        },
    },

    # ================= UNDERLIGHT AND OUT =================
    "ab_everything_points_east": {
        "ab_the_east": {
            "label": "Have Peska list what points east.",
            "response": (
                "All of it. That is the problem.\n\nSepp's revenants are brine-cured and the "
                "nearest brine is the pan, four days northwest, and everybody on the pan will "
                "tell you the water goes under and goes EAST.\n\nHask has four shrike crops with "
                "water animals in them, in a desert with no standing water.\n\nVizzi has a "
                "hundred and twenty feet of line that does not reach anything, twice, both east.\n\n"
                "My two biggest holes are east and they are the two that are still moving.\n\nAnd "
                "there is light coming up out of the ground on the eastern boundary, getting "
                "brighter by about a measurable amount every season.\n\nI am a surveyor. I do not "
                "get to say what that MEANS. I do get to say that six independent lines of "
                "evidence point the same direction, and that the direction has a very large hole "
                "with water in it at the end of it, and that the goblins sitting on that hole "
                "have been there for two years."),
        },
    },
    "ab_carry_the_book": {
        "ab_the_east": {
            "label": "Ask why she will not carry the book herself.",
            "response": (
                "Because I am two years into a survey and if I walk away from Fourth Peg for a "
                "fortnight the readings have a fortnight-shaped hole in them, and a column with a "
                "hole in it is worth considerably less than half a column.\n\nThat is the "
                "professional answer and it is true.\n\nThe other answer is that I have spent two "
                "years being the person who does not know why, and she is the person who does, "
                "and I would like somebody else to be in the room when I find out whether she is "
                "better at this than me.\n\nI am aware of how that sounds. I am forty-one years "
                "old and I would still rather hear it secondhand.\n\nTake her the book. It is "
                "good work. Whatever else happens, the dates are good work."),
        },
    },
    "ab_the_answer_comes_back": {
        "ab_the_reply": {
            "label": "Ask Ulla what she put in the reply.",
            "response": (
                "Three pages of arithmetic she can check herself, and that is deliberate - the "
                "only letter worth sending to somebody like her is one she can take apart.\n\nThe "
                "fourth page is what it means, and she is not going to like it.\n\nHer ground is "
                "not failing. There is nothing wrong with her rock. Limestone floats on water and "
                "it has been doing that competently for ten thousand years, and the only thing "
                "that has changed is that the water left.\n\nSo every reading she has taken for "
                "two years is correct and every conclusion anybody has drawn from it is about the "
                "wrong thing. Her field will keep opening - not because of anything in the "
                "ground, but because something four days east of her is still drinking.\n\nI have "
                "put that as kindly as I know how, which is not very. She is a professional. She "
                "would rather have it straight and I would rather give it to her that way than "
                "have her find out from the ground."),
        },
    },

    # ================= STANDALONE =================
    "ab_three_month_contract": {
        "ab_the_contract": {
            "label": "Ask Sepp why he stayed.",
            "response": (
                "Three months. It was a three-month contract and that was two years and two camps "
                "ago, and nobody has ever mentioned it again including me.\n\nI could have gone. "
                "I want that understood - there was no moment where I was trapped out here. Four "
                "carts, a week's walk, and I would have been back in the port with a story.\n\nIt "
                "took me about eight months to work out why I did not, and about four seconds to "
                "say once I had.\n\nSomebody has to be the one who is still here when the answer "
                "turns up.\n\nThat is it. Peska will not be - she will have been reassigned or "
                "sacked. Hask will follow the work. Vizzi will go down one hole too many. Somebody "
                "has to still be standing at this peg on the day it makes sense, and I have "
                "decided that is my job, and it is the only decision I have ever made that I have "
                "not revisited once."),
        },
    },
}
