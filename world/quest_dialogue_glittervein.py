"""
Topic content for Glittervein's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. QuestObjective.topics is only the completion condition;
the dialogue screen renders a button per AUTHORED topic, so a topic named in an objective and
missing here is a quest that cannot be finished and does not look broken.

THE TEST A DIALOGUE OBJECTIVE HAS TO PASS is that the conversation IS the content - that somebody
has been waiting to be asked, and the having-asked is the event. Lastwater is ten people who have
been stuck on a rock together for eleven months, so it passes that test more easily than anywhere
else in the game: every one of them has a speech ready and none of them has a new audience.

Two of these do most of the work:

  gv_the_chain    Ulla Stormhollow laying out five zones in order. This is the payoff of the
                  longest thread in the game and the player has walked four sixths of it already.
  gv_the_end      What she says when it is over, which is NOT triumph. She has been right for four
                  years and being right has cost a city.

VOICE: goblin, fast and mercantile, except that these goblins have been underground for a year and
talk more quietly than goblins should. Ulla is the exception in every way - slow, exact, and the
only person in the camp who is not arguing.
"""

QUEST_TOPICS = {
    # ================= THE RIM AND THE WAY DOWN =================
    "gv_the_lip": {
        "gv_the_hole": {
            "label": "Ask Dez what you are actually looking at.",
            "response": (
                "A cenote. That is the word for it, and I had to be told it too.\n\nLimestone "
                "sits on water for a few thousand years and the water eats it hollow from "
                "underneath, and then one day the roof is thinner than the roof needs to be and "
                "the whole lot drops. You came through the Sands - that is the same thing, all "
                "eleven times, with the water already gone when the floor went.\n\nThis one still "
                "has its water. That is the entire difference between a hole full of sand and the "
                "only pool in Tanaris, and it is nothing but luck about which bit of rock gave "
                "way first."),
        },
        "gv_lastwater": {
            "label": "Ask who is down there.",
            "response": (
                "Ten of us. It was ninety.\n\nSteamwheedle put the money up because the crystal in "
                "that wall does not care about magic and there is no other seam like it this side "
                "of the world. Eighteen months of cutting road, four months of actual digging, "
                "and then the water came up the shaft and that was the end of the digging.\n\nWe "
                "are not stranded. I want to be clear about that, people arrive thinking we are "
                "stranded. We could walk out tomorrow. It is just that walking out means somebody "
                "has decided it is over, and nobody down there is willing to be that person."),
        },
    },
    "gv_the_long_way_down": {
        "gv_the_road": {
            "label": "Ask Brodd about the road.",
            "response": (
                "One lap. That is the whole design and it took them a year and a half.\n\nThe "
                "first survey wanted three laps on a tighter pitch - shorter cut, less rock to "
                "shift, cheaper by a third. Marn threw it out. He said a road you take four times "
                "a day has to be a road you do not resent, and three laps of this hole is twelve "
                "hundred feet of walking to come up for a tool you forgot.\n\nIt is the only "
                "decision that man has ever made that nobody has argued with since. Everybody who "
                "has walked it knows."),
        },
        "gv_the_water": {
            "label": "Ask what the pool is like.",
            "response": (
                "Cold. Colder than it has any business being, and I have been cooking next to it "
                "for two years so I notice.\n\nIt is clean, mind. Nix brews off it and I boil off "
                "it and neither of us has ever had a bad barrel. There is just something about "
                "standing in a desert four days from anywhere, forty-six feet down, with your "
                "hands in water that is colder than the night air.\n\nUlla says that is the most "
                "important thing about this place. She says it like it is good news and it has "
                "never once sounded like good news."),
        },
    },

    # ================= THE DEADLOCK =================
    "gv_eleven_months": {
        "gv_the_company": {
            "label": "Let Marn make the Company's case.",
            "response": (
                "Here it is, and it is not complicated.\n\nThere is one seam of magic-proof "
                "crystal in the world. It is four hundred feet below us. Every day it stays "
                "flooded is a day that stone is in the ground instead of on somebody's back, and "
                "a day somebody else gets closer to finding their own.\n\nI am not greedy. I have "
                "ninety people's wages in a ledger with my name at the bottom and forty of those "
                "people are still down there, and the only version of this where that was worth "
                "anything is the one where we go back.\n\nShe wants to understand it first. I "
                "have never in my life been in the room where understanding it first was the "
                "thing that paid for the funerals."),
        },
        "gv_the_flood": {
            "label": "Ask what actually happened on the day.",
            "response": (
                "Nothing. That is what nobody believes.\n\nNo crack, no roar, no face coming in. "
                "The night shift came up and said the floor was wet and the day shift went down "
                "and the floor was wetter, and by the end of that shift there was an inch of "
                "standing water in a gallery that had been dry for four months.\n\nThree days "
                "later it was over your boots. Nine days later it was at the ceiling of the lower "
                "drift and we had the pumps on it and the pumps did not touch it.\n\nWater does "
                "not come UP. Not in a desert, not at four hundred feet, not for nine days "
                "straight without a storm within two hundred miles. I have been in holes my whole "
                "life. I have never seen that and nor has anybody I have ever asked."),
        },
    },
    "gv_the_book": {
        "gv_the_book_topic": {
            "label": "Ask Oss what the book is for.",
            "response": (
                "A number, taken at the same time, in the same place, every day, whether anybody "
                "wants it or not.\n\nThat is the whole thing. People hear nine hundred and "
                "forty-one days and they think it must be complicated. It is a stick with marks "
                "on it and a woman who gets up early.\n\nThe Boss reads it as a season. Ulla "
                "reads it as a trend. They are reading the same column and I have watched them "
                "both do it and neither of them is lying to me.\n\nSo one of two things is true. "
                "Either a number can mean two things, or I have been getting up at dawn for three "
                "years to produce something useless. I would quite like it to be the first one."),
        },
    },
    "gv_same_book": {
        "gv_the_company": {
            "label": "Hear the Company's reading of the column.",
            "response": (
                "Seasonal. Look at it - it goes up, it comes down a little, it goes up.\n\nWater "
                "tables do that. Every hole I have ever worked has done that. You pump through the "
                "high season, you cut through the low, and if you are patient you get the whole "
                "seam in four years instead of two.\n\nEleven months is not a long time to a "
                "mountain. It is a very long time to a wage bill, which is the actual difference "
                "between me and her and always has been."),
        },
        "gv_the_survey": {
            "label": "Hear the Survey's reading of the column.",
            "response": (
                "It does go up and down. He is right about that and I have never said otherwise.\n\n"
                "Put a straight edge on it.\n\nEvery high is higher than the last high. Every low "
                "is higher than the last low. The season is real and it is riding on something "
                "that is not a season, and the something is winning by about four inches a "
                "year.\n\nI did not bring that from anywhere. I read it in his clerk's book, in "
                "his camp, on his paper. It is the only argument I have ever made that is built "
                "entirely out of the other side's evidence, and it is the reason he has not been "
                "able to end it."),
        },
        "gv_the_book_topic": {
            "label": "Ask Oss what she thinks now you have heard both.",
            "response": (
                "I think I am going to keep getting up at dawn.\n\nYou want me to pick. Everyone "
                "wants me to pick, and the moment I pick I stop being the person who writes the "
                "number down and start being the person who writes down the number that proves "
                "her point.\n\nThere is a clerk out in the port, Hesper Dunn, keeps her books the "
                "same way and for the same reason. We have never met. We have written to each "
                "other twice. Both letters were about ruling paper.\n\nShe would understand "
                "exactly what I am saying and she is four days away and that is the loneliest "
                "sentence in this camp."),
        },
    },
    "gv_works_order": {
        "gv_the_works_order": {
            "label": "Get Marn to say the terms out loud.",
            "response": (
                "Nine days of pumping on the first gallery. Her two housings and my four. A man "
                "of hers on the face the whole time, writing down whatever comes out of it, and "
                "that man's book is HERS and not mine.\n\nThat last part is the part that took "
                "eleven months. I could have had the pumps running last autumn if I had been "
                "willing to own what they found.\n\nI was not. I am now. That is not a change of "
                "heart, it is arithmetic: a seam I cannot sell is worth the same as a seam I "
                "cannot reach, and I have had a year to work out which of those I was holding."),
        },
    },

    # ================= THE WATER CHAIN =================
    "gv_five_places": {
        "gv_the_chain": {
            "label": "Let Ulla lay out all five, in order.",
            "response": (
                "Sit down. This takes longer than people expect and it is worth the time.\n\n"
                "The Aspen Wilderness. The melt comes earlier every spring and runs harder, and "
                "there is a woman up there who has measured it for six years and cannot get "
                "anybody to care because an early thaw is good news in a cold place.\n\nSouthern "
                "Thousand Needles. All of that water goes down into the Needles and the Needles "
                "are drying. Both of those are true at once and nobody there can tell you how.\n\n"
                "The Shimmering Flats. The water arrives. It has always arrived. It goes under "
                "the pan and it goes EAST, and the people on the salt have known that for "
                "generations and treat it as weather.\n\nNorthern Tanaris. East of the pan is "
                "Gadgetzan, and Gadgetzan's wells went dry over two seasons and a walled city "
                "with a wall and no water is a siege it is holding against itself.\n\nThe Abyssal "
                "Sands. Take the water out from under limestone and the limestone comes down. "
                "Eleven holes, in four years, in ground that had not moved in ten thousand.\n\n"
                "And then here. Where all of it is.\n\nFive places. Five sets of careful people. "
                "Every one of them right about their own valley and not one of them able to see "
                "the next one along."),
        },
        "gv_the_melt": {
            "label": "Ask why she started.",
            "response": (
                "Because the thaw was four days early and then it was nine days early and then it "
                "was a fortnight, and I could not find one person who thought that was strange.\n\n"
                "I am not a scholar. I want that understood. I kept a herd on the Needles and the "
                "spring flood is what fills the washes and the washes are what the herd drinks "
                "from, and one year the flood came and went in a week and did not fill anything.\n\n"
                "So I walked up the water to find out why. And then I kept walking, because every "
                "time I got to the top of one problem it turned out to be the bottom of the next "
                "one.\n\nFour years. I have been told I am obsessed, by people who were being "
                "kind, and by people who were not. I did not set out to be right about a region. "
                "I set out to find out what happened to a wash."),
        },
    },
    "gv_a_well_in_the_middle": {
        "gv_gadgetzan": {
            "label": "Ask about Gadgetzan.",
            "response": (
                "I was there in the second season. They were still arguing about whether to deepen "
                "the well.\n\nThere is nothing cruel about what happened to that city and that is "
                "the part people cannot hold on to. Nobody poisoned it. Nobody besieged it. The "
                "water under it went somewhere else, gradually, over about twenty months, and "
                "every month it was reasonable to wait one more month before doing anything "
                "drastic.\n\nI have met four people since who were there at the end and all four "
                "of them tell it as a decision they should have made sooner. It was not. There "
                "was never a day when leaving was obviously right until there was a day when "
                "staying was obviously fatal, and those are not the same day, and nobody gets to "
                "live in between them.\n\nThere is a man in Steamwheedle who was carried out on a "
                "door. He will tell you he did not leave. He is correct and it matters to him "
                "enormously and I have never once heard anybody let him finish the sentence."),
        },
    },
    "gv_it_is_being_pulled": {
        "gv_the_argument": {
            "label": "Have her state it plainly, once.",
            "response": (
                "Plainly. All right.\n\nWater moves downhill. That is not a rule of thumb, it is "
                "the only thing water does. Everything I have been doing for four years is an "
                "elaborate way of asking why the water under this region has been moving somewhere "
                "that is not downhill.\n\nThere are two answers. Either the ground tipped - which "
                "is what everybody says, and a range did come down three years ago, and a tipped "
                "table drains ONCE and then stops - or something is lifting it.\n\nIt has not "
                "stopped. It is four inches a year faster than it was. A tipped table does not "
                "accelerate.\n\nSo: something four hundred feet under this camp has been lifting "
                "the water out from under five regions since about the time the sky changed, and "
                "it is still doing it, and it is doing it harder.\n\nThat is the sentence. I have "
                "had the first half of it for three years and I have wanted very badly to be "
                "wrong about the second."),
        },
    },

    # ================= THE SEAMS =================
    "gv_what_shrugs_off_a_spell": {
        "gv_resistance": {
            "label": "Ask Vessa what the glass actually does.",
            "response": (
                "Right. Watch the plate, not me.\n\n[She holds a backed plate up and a wisp's "
                "light breaks across it and goes nowhere.]\n\nIt did not stop that. People say "
                "stop and it is the wrong word and the wrong word gets people killed.\n\nThe "
                "stone takes the shape of whatever hits it - properly takes it, all the way "
                "through, in about the time it takes you to blink - and then it cannot HOLD the "
                "shape, and the whole thing comes apart in the stone instead of in you.\n\nTwo "
                "things follow and both of them matter. One: it works best where you are actually "
                "being hit, which is your chest and your shield and your legs. Putting it in a "
                "ring is decoration.\n\nTwo: it does not care what KIND. Fire, frost, arcane, the "
                "thing the singers do down in the dig - all the same to it. That is why there is "
                "one seam in the world worth this much and why I have four months of it left."),
        },
    },

    # ================= THE CISTERN =================
    "gv_ci_the_thirst": {
        "gv_the_end": {
            "label": "Ask Ulla what happens now.",
            "response": (
                "Honestly? I do not know, and I have had four years to prepare an answer.\n\nThe "
                "water table will come back. Not quickly - it took three years to go and it will "
                "take longer than that to return, because going was being pulled and coming back "
                "is only gravity. The Needles will get their spring flood. The washes will fill. "
                "Somebody's grandchildren will keep a herd where I kept mine.\n\nGadgetzan is not "
                "coming back. A city is not a water table. Four hundred people left and most of "
                "them are in Steamwheedle now doing well, and the ones doing well are the reason "
                "nobody out there wants to hear that it was preventable.\n\nI was right. I want to "
                "tell you what that is like, because you were there for the end of it and nobody "
                "else will be.\n\nIt is not good. Being right about this means every single person "
                "who told me it was a local problem was wrong at the worst possible moment, and "
                "most of them were kind to me, and two of them are dead.\n\nI am going to write it "
                "up properly. Then I am going to go and look at the pool for a while, and I would "
                "rather do that part alone."),
        },
    },

    # ================= OUT OF THE ZONE =================
    "gv_tell_them_why": {
        "gv_the_road_east": {
            "label": "Ask Mazzic what he will do with it.",
            "response": (
                "Nothing. I am going to do nothing with it, and I would like you to not be "
                "disappointed about that.\n\nI am seventy-one. I am not going to walk back across "
                "that pan and point at a hole in the ground. There is no court. There is nobody to "
                "hand it to. The goblin who would have wanted it most ran the Gadgetzan water "
                "office and he did not come out.\n\nWhat I am going to do is put it in the box "
                "with the deed, and when I die somebody is going to open that box and find a deed "
                "to a house in a dead city and a sheet of paper that says why the city died.\n\n"
                "Those two things belong together. They have not been together for three years. "
                "Now they are, and that is worth more to me than you probably think it is."),
        },
    },
    "gv_the_book_goes_east": {
        "gv_two_clerks": {
            "label": "Hear what Hesper says about the column.",
            "response": (
                "[Hesper Dunn reads the first page without sitting down, and then sits down.]\n\n"
                "She rules her paper the same way. Look at that - same gutter, same hand in the "
                "margin, and we have never met.\n\nNine hundred and forty-two days. I have four "
                "thousand and change, but mine is crates and hers is the water table under a "
                "region, and hers is going to matter more.\n\nTell her I will keep it in the same "
                "box, and tell her I have dated the box.\n\nAnd tell her - no. I will write it. "
                "Some things should not be carried by somebody else, and a clerk writing to a "
                "clerk is one of them."),
        },
    },
}
