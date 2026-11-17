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
    # Plain voice, 17 Nov 2026.
    # ================= THE RIM AND THE WAY DOWN =================
    "gv_the_lip": {
        "gv_the_hole": {
            "label": "Ask Dez what you are actually looking at.",
            "response": (
                "It's a cenote. That's the word for it, and I had to be told it too.\n\nLimestone sits on "
                "water for a few thousand years and the water eats it hollow from underneath. Then one day "
                "the roof is thinner than the roof needs to be, and the whole lot drops. You came through "
                "the Sands, and that's the same thing eleven times over, with the water already gone when "
                "the floor went.\n\nThis one still has its water. That's all that separates a hole full of "
                "sand from the only pool in Tanaris, and it came down to luck about which bit of rock gave "
                "way first."),
        },
        "gv_lastwater": {
            "label": "Ask who is down there.",
            "response": (
                "There are ten of us. There were ninety.\n\nSteamwheedle put the money up because the "
                "crystal in that wall doesn't care about magic, and there's no other seam like it this side "
                "of the world. Eighteen months of cutting road, four months of actual digging, and then the "
                "water came up the shaft and that was the end of the digging.\n\nWe aren't stranded. I want "
                "to be clear about that, because people arrive thinking we're stranded. We could walk out tomorrow. "
                "Walking out just means somebody has decided it's over, and nobody down in the camp is willing to "
                "be that person."),
        },
    },
    "gv_the_long_way_down": {
        "gv_the_road": {
            "label": "Ask Brodd about the road.",
            "response": (
                "It's one lap. That's the whole design, and it took them a year and a half.\n\nThe first "
                "survey wanted three laps on a tighter pitch, with a shorter cut and less rock to shift, "
                "cheaper by a third. Marn threw it out. He said a road you take four times a day has to be "
                "a road you don't resent, and three laps of this hole is twelve hundred feet of walking to "
                "come up for a tool you forgot.\n\nIt's the only decision that man has ever made that nobody "
                "has argued with since. Everybody who's walked it knows."),
        },
        "gv_the_water": {
            "label": "Ask what the pool is like.",
            "response": (
                "It's cold, colder than it has any business being, and I've been cooking next to it for two "
                "years so I notice.\n\nIt's clean, mind. Nix brews off it and I boil off it, and neither of "
                "us has ever had a bad barrel. There's just something about standing in a desert four days "
                "from anywhere, forty-six feet down, with your hands in water that's colder than the night "
                "air.\n\nUlla says that's the most important thing about this place. She says it like it's "
                "good news, and it's never once sounded like good news."),
        },
    },

    # ================= THE DEADLOCK =================
    "gv_eleven_months": {
        "gv_the_company": {
            "label": "Let Marn make the Company's case.",
            "response": (
                "Here it is, and it isn't complicated.\n\nThere's one seam of magic-proof crystal in the "
                "world, and it's four hundred feet below us. Every day it stays flooded is a day that stone "
                "is in the ground instead of on somebody's back, and a day somebody else gets closer to "
                "finding their own.\n\nI'm not greedy. I've got ninety people's wages in a ledger with my "
                "name at the bottom, and forty of those people are still down there. The only version of "
                "this where that was worth anything is the one where we go back.\n\nShe wants to understand "
                "it first. I've never in my life been in a room where understanding it first paid for the "
                "funerals."),
        },
        "gv_the_flood": {
            "label": "Ask what actually happened on the day.",
            "response": (
                "Nothing happened, and that's what nobody believes.\n\nThere was no crack, no roar, no face "
                "coming in. The night shift came up and said the floor was wet, the day shift went down and "
                "the floor was wetter, and by the end of that shift there was an inch of standing water in a "
                "gallery that had been dry for four months.\n\nThree days later it was over your boots. Nine "
                "days later it was at the ceiling of the lower drift, and we had the pumps on it and the "
                "pumps didn't touch it.\n\nWater doesn't come up. It doesn't do it in a desert, or at four "
                "hundred feet, or for nine days straight without a storm within two hundred miles. I've been "
                "in holes my whole life. I've never seen that, and nor has anybody I've ever asked."),
        },
    },
    "gv_the_book": {
        "gv_the_book_topic": {
            "label": "Ask Oss what the book is for.",
            "response": (
                "It's a number, taken at the same time, in the same place, every day, whether anybody wants "
                "it or not.\n\nThat's all it is. People hear nine hundred and forty-one days and they "
                "think it must be complicated. It's a stick with marks on it and a woman who gets up "
                "early.\n\nThe Boss reads it as a season. Ulla reads it as a trend. They're reading the same "
                "column, I've watched them both do it, and neither of them is lying to me.\n\nSo one of two "
                "things is true. Either a number can mean two things, or I've been getting up at dawn for "
                "three years to produce something useless. I'd quite like it to be the first one."),
        },
    },
    "gv_same_book": {
        "gv_the_company": {
            "label": "Hear the Company's reading of the column.",
            "response": (
                "It's a seasonal pattern. Look at it. It goes up, it comes down a little, it goes up.\n\nWater tables "
                "do that. Every hole I've ever worked has done that. You pump through the high season, you "
                "cut through the low, and if you're patient you get the whole seam in four years instead of "
                "two.\n\nEleven months isn't a long time to a mountain. It's a very long time to a wage "
                "bill, and that's what's always stood between me and her."),
        },
        "gv_the_survey": {
            "label": "Hear the Survey's reading of the column.",
            "response": (
                "It does go up and down. He's right about that, and I've never said otherwise.\n\nNow put a "
                "straight edge on it.\n\nEvery high is higher than the last high. Every low is higher than "
                "the last low. The season is real, and it's riding on something that isn't a season, and the "
                "something is winning by about four inches a year.\n\nI didn't bring that from anywhere. I "
                "read it in his clerk's book, in his camp, on his paper. It's the only argument I've ever "
                "made that's built entirely out of the other side's evidence, and it's the reason he hasn't "
                "been able to end it."),
        },
        "gv_the_book_topic": {
            "label": "Ask Oss what she thinks now you have heard both.",
            "response": (
                "I think I'm going to keep getting up at dawn.\n\nYou want me to pick. Everyone wants me to "
                "pick, and the moment I pick I stop being the person who writes the number down and start "
                "being the person who writes down the number that proves her point.\n\nThere's a clerk out "
                "in the port, Hesper Dunn, who keeps her books the same way and for the same reason. We've "
                "never met. We've written to each other twice, and both letters were about ruling "
                "paper.\n\nShe'd understand exactly what I'm saying, and she's four days away, and that's "
                "the loneliest sentence in this camp."),
        },
    },
    "gv_works_order": {
        "gv_the_works_order": {
            "label": "Get Marn to say the terms out loud.",
            "response": (
                "It's nine days of pumping on the first gallery, her two housings and my four. She gets a "
                "man on the face the whole time, writing down whatever comes out of it, and that man's book "
                "is hers and not mine.\n\nThat last part is what took eleven months. I could have had the "
                "pumps running last autumn if I'd been willing to own what they found.\n\nI wasn't willing then, and I'm willing "
                "now. My heart hasn't changed, the arithmetic has. A seam I can't sell is worth the same as "
                "a seam I can't reach, and I've had a year to work out which of those I was holding."),
        },
    },

    # ================= THE WATER CHAIN =================
    "gv_five_places": {
        "gv_the_chain": {
            "label": "Let Ulla lay out all five, in order.",
            "response": (
                "Sit down with me. This takes longer than people expect, and it's worth the time.\n\nFirst "
                "the Aspen Wilderness. The melt comes earlier every spring and runs harder, and there's a "
                "woman up there who's measured it for six years and can't get anybody to care, because an "
                "early thaw is good news in a cold place.\n\nThen Southern Thousand Needles. All of that "
                "water goes down into the Needles, and the Needles are drying. Both of those are true at "
                "once, and nobody there can tell you how.\n\nThen the Shimmering Flats. The water arrives, "
                "and it's always arrived. It goes under the pan and it goes east, and the people on the salt "
                "have known that for generations and treat it as weather.\n\nThen northern Tanaris. East of "
                "the pan is Gadgetzan, and Gadgetzan's wells went dry over two seasons, and a walled city "
                "with no water is a siege it's holding against itself.\n\nThen the Abyssal Sands. Take the "
                "water out from under limestone and the limestone comes down. That's eleven holes, in four "
                "years, in ground that hadn't moved in ten thousand.\n\nAnd then here, where all of it "
                "is.\n\nThat's five places and five sets of careful people. Every one of them was right about "
                "their own valley, and not one of them could see the next one along."),
        },
        "gv_the_melt": {
            "label": "Ask why she started.",
            "response": (
                "Because the thaw was four days early, and then it was nine days early, and then it was a "
                "fortnight, and I couldn't find one person who thought that was strange.\n\nI'm not a "
                "scholar, and I want that understood. I kept a herd on the Needles. The spring flood is what "
                "fills the washes and the washes are what the herd drinks from, and one year the flood came "
                "and went in a week and didn't fill anything.\n\nSo I walked up the water to find out why. "
                "Then I kept walking, because every time I got to the top of one problem it turned out to be "
                "the bottom of the next one.\n\nThat was four years ago. I've been told I'm obsessed, by "
                "people who were being kind and by people who weren't. I didn't set out to be right about a "
                "region. I set out to find out what happened to a wash."),
        },
    },
    "gv_a_well_in_the_middle": {
        "gv_gadgetzan": {
            "label": "Ask about Gadgetzan.",
            "response": (
                "I was there in the second season. They were still arguing about whether to deepen the "
                "well.\n\nThere's nothing cruel about what happened to that city, and people can't hold on "
                "to that. Nobody poisoned it and nobody besieged it. The water under it went somewhere else, "
                "gradually, over about twenty months, and every month it was reasonable to wait one more "
                "month before doing anything drastic.\n\nI've met four people since who were there at the "
                "end, and all four of them tell it as a decision they should have made sooner, and it wasn't one. "
                "There was never a day when leaving was obviously right, until there was a day when staying "
                "was obviously fatal. Those aren't the same day, and nobody gets to live in between "
                "them.\n\nThere's a man in Steamwheedle who was carried out on a door. He'll tell you he "
                "didn't leave. He's correct, it matters to him enormously, and I've never once heard anybody "
                "let him finish the sentence."),
        },
    },
    "gv_it_is_being_pulled": {
        "gv_the_argument": {
            "label": "Have her state it plainly, once.",
            "response": (
                "All right, plainly.\n\nWater moves downhill. That's the only thing water does. Everything "
                "I've been doing for four years is an elaborate way of asking why the water under this region "
                "has been moving somewhere that isn't downhill.\n\nThere are two answers. Either the ground "
                "tipped, or something is lifting it. Everybody says the ground tipped, and a range did come "
                "down three years ago. But a tipped table drains once and then stops.\n\nThis hasn't "
                "stopped. It's four inches a year faster than it was, and a tipped table doesn't "
                "accelerate.\n\nSo something four hundred feet under this camp has been lifting the water "
                "out from under five regions since about the time the sky changed. It's still doing it, and "
                "it's doing it harder.\n\nThat's the sentence. I've had the first half of it for three "
                "years, and I've wanted very badly to be wrong about the second."),
        },
    },

    # ================= THE SEAMS =================
    "gv_what_shrugs_off_a_spell": {
        "gv_resistance": {
            "label": "Ask Vessa what the glass actually does.",
            "response": (
                "Right, watch the plate, not me.\n\nShe holds a backed plate up, and a wisp's light breaks "
                "across it and goes nowhere.\n\nIt didn't stop that. People say stop, and it's the wrong "
                "word, and the wrong word gets people killed.\n\nThe stone takes the shape of whatever hits "
                "it. It properly takes it, all the way through, in about the time it takes you to blink, and "
                "then it can't hold the shape, so the whole thing comes apart in the stone instead of in "
                "you.\n\nTwo things follow, and both of them matter. First, it works best where you're "
                "actually being hit, which is your chest and your shield and your legs. Putting it in a ring "
                "is decoration.\n\nSecond, it doesn't care what kind. Fire, frost, arcane, the thing the "
                "singers do down in the dig, it's all the same to it. That's why there's one seam in the "
                "world worth this much, and why I've got four months of it left."),
        },
    },

    # ================= THE CISTERN =================
    "gv_ci_the_thirst": {
        "gv_the_end": {
            "label": "Ask Ulla what happens now.",
            "response": (
                "Honestly, I don't know, and I've had four years to prepare an answer.\n\nThe water table "
                "will come back, though not quickly. It took three years to go and it'll take longer than "
                "that to return, because going was being pulled and coming back is only gravity. The Needles "
                "will get their spring flood. The washes will fill. Somebody's grandchildren will keep a herd "
                "where I kept mine.\n\nGadgetzan isn't coming back. A city doesn't refill like a water "
                "table. Four hundred people left, and most of them are in Steamwheedle now doing well, and "
                "the ones doing well are the reason nobody out there wants to hear that it was "
                "preventable.\n\nI was right. I want to tell you what that's like, because you were there "
                "for the end of it and nobody else will be.\n\nIt isn't good. Being right about this means "
                "every single person who told me it was a local problem was wrong at the worst possible "
                "moment, and most of them were kind to me, and two of them are dead.\n\nI'm going to write "
                "it up properly. Then I'm going to go and look at the pool for a while, and I'd rather do "
                "that part alone."),
        },
    },

    # ================= OUT OF THE ZONE =================
    "gv_tell_them_why": {
        "gv_the_road_east": {
            "label": "Ask Mazzic what he will do with it.",
            "response": (
                "I'm going to do nothing with it, and I'd like you not to be disappointed about that.\n\nI'm seventy-one years old, and I'm "
                "not going to walk back across that pan and point at a hole in the ground. "
                "There's no court, and there's nobody to hand it to. The goblin who'd have wanted it most ran "
                "the Gadgetzan water office, and he didn't come out.\n\nWhat I'm going to do is put it in the "
                "box with the deed. When I die somebody is going to open that box and find a deed to a house "
                "in a dead city and a sheet of paper that says why the city died.\n\nThose two things belong "
                "together, and they haven't been together for three years. Now they are, and that's worth "
                "more to me than you probably think it is."),
        },
    },
    "gv_the_book_goes_east": {
        "gv_two_clerks": {
            "label": "Hear what Hesper says about the column.",
            "response": (
                "Hesper Dunn reads the first page without sitting down, and then sits down.\n\nShe rules her "
                "paper the same way. Look at that, the same gutter and the same hand in the margin, and "
                "we've never met.\n\nNine hundred and forty-two days. I've got four thousand and change, but "
                "mine is crates and hers is the water table under a region, and hers is going to matter "
                "more.\n\nTell her I'll keep it in the same box, and tell her I've dated the box.\n\nAnd tell "
                "her, no, I'll write it myself. A clerk writing to a clerk shouldn't be carried by somebody "
                "else."),
        },
    },
}
