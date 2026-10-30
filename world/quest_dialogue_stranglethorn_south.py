"""
Topic content for the DIALOGUE objectives in Booty Bay / Southern Stranglethorn.

Owned outright by this zone's pass (see world/quest_dialogue.py's PER-ZONE TOPIC MODULES note, which
exists because three Stranglethorn passes all skipped dialogue rather than append to one shared dict).
Same shape as that file: {quest_id: {topic_id: {"label", "response"}}}.  world/quest_dialogue.py
imports and merges this by name and raises on a quest_id collision, so nothing here needs guarding
and nothing here edits that file.

HARD CONSTRAINT, and the reason tools/build_stranglethorn_south_quests.py's audit() imports this
module and calls get_topic on all nine ids: a topic named in a quest's objective with no authored
text renders NO BUTTON, which makes the quest impossible to complete and reports as nothing at all.
The objective's topics list and the keys below are the same nine strings or the build fails.

THREE QUESTS, AND WHY EACH ONE IS A CONVERSATION RATHER THAN A JOB:

  bb_kundaraz_means       Pilot Zan'rek, on the pier head.  The end of the millrace chain and the end
                          of the jungle's three-city thread: Northern raises Zul'Marosh, Central
                          answers part of it at the arena, and here a troll pilot who has corrected
                          the player's word for the ruin twice finally says the whole thing out loud -
                          to a courier, because there is nobody else left to say it to.  The content
                          could not be a kill count.  It is an etymology and a grievance about who
                          listened.
  bb_quiet_mans_ledger    The fence, who said he knows which boat and which year and then said he had
                          not seen you.  This is where the Earth-transplant undercurrent gets a whole
                          quest instead of an aside, and it does real work: the book is the same
                          object Tollkeeper Nizzik refuses to start, seen from the other side by
                          somebody who did start one and will not sell out of it.
  bb_marlas_question      Keeper Marla, inside, at a table.  She asked about the hot water over a
                          bowl of crab and let the player walk out without answering.  The warm
                          exception that makes the rest of the zone's coldness read as deliberate -
                          and the one person on the boards who says out loud that somebody should
                          have said something.

VOICE.  Zan'rek is written the way his greeting is written - flat, short, no dialect spelling, which
is how the twenty shipped quests already have him and the one place consistency beats colour.  The
Quiet Man is quiet: short sentences, nothing hedged.  Marla is a Lakeshire cook who has been down
here eleven years and is not sad about it.  ASCII only - the game font has nothing else.
"""

QUEST_TOPICS = {
    # ===================================================================== Pilot Zan'rek, pier head
    "bb_kundaraz_means": {
        "the_name": {
            "label": "What does Kundaraz mean?",
            "response": (
                "The water coming up. Not the sea - the sea has its own word and it is not a "
                "compliment. Kundaraz is the water rising to where you put it, because you put it "
                "there.\n\n"
                "Every mouth in that port calls it the ruin, and when they want to be careful they "
                "call it the drowned place, which is the same insult with a hat on. A drowned place "
                "is a place something happened to. Zul'Kundaraz is named for the thing happening. "
                "The masons signed their work in the title and then the water came up over the "
                "signature, which I think they would have found funny."
            ),
        },
        "three_cities": {
            "label": "Three cities, one grammar - what does that mean?",
            "response": (
                "It means they were all cut by people who had been taught the same thing and did not "
                "argue with it.\n\n"
                "The courts in the north nobody can read, the arena in the middle that is still full "
                "of shouting, and ours. Three hands, hundreds of years between the first and the "
                "last, and one measure running through all three of them. The rule you carried north "
                "would have fitted any of the three. The newest is the biggest and the newest is the "
                "one under salt water, and the order of those two facts is what everybody gets "
                "backwards.\n\n"
                "They did not get worse at it. They got bolder, and then they finished."
            ),
        },
        "what_the_sluice_got": {
            "label": "What has Pate actually got, then?",
            "response": (
                "A set of decisions. That is all a weir pin is - somebody stood in a junction a long "
                "time ago, worked out how fast the hall should fill, and cut the answer in stone so "
                "the next crew would not have to guess.\n\n"
                "Your sluice-keeper has been guessing for nine years with a hardwood wedge and a bad "
                "temper. Now he has not got to. That is the entire gift and it is a large one.\n\n"
                "And I will tell you the part I did not say in front of him. I have had that in my "
                "head for most of my life and I offered it to that port whenever anyone would hold "
                "still. Nobody ever did. The first person to want it keeps a mill in Hillsbrad and has "
                "never seen the place. I have decided to be pleased about it. It took me a week."
            ),
        },
    },
    # ======================================================================= The Quiet Man, back room
    "bb_quiet_mans_ledger": {
        "the_book": {
            "label": "What is actually in the book?",
            "response": (
                "Boats and years. Nothing else, and I want you to understand how little that is.\n\n"
                "Which hull came in, what tide, who walked off it, and when. I started keeping it "
                "because a man in my trade who cannot tell you where a thing came from is a man "
                "handling stolen goods, and a man who can is handling a provenance. That is the whole "
                "difference and it is worth money.\n\n"
                "Then the ground changed and the boats stopped being boats I knew, and I kept writing, "
                "because stopping would have been a decision and writing was a habit. So yes. You are "
                "in it. Hull, tide, year. Three lines, same as everybody."
            ),
        },
        "who_comes_asking": {
            "label": "Who comes asking after it?",
            "response": (
                "Three kinds, and I can sort them before they finish the first sentence.\n\n"
                "Insurers, who want a hull. Families, who want a name and usually get one and almost "
                "never thank me for it. And then the third kind, who come in asking very politely for "
                "everybody who arrived in a particular season.\n\n"
                "Not a name. A season. I have had that asked of me four times and every one of the "
                "four had a reason ready before I opened my mouth, and every reason was a good one, "
                "and that is how I knew. A man with a good reason to want a list of strangers has "
                "already thought about what he is going to do with it."
            ),
        },
        "what_it_is_worth": {
            "label": "What is it worth, and why have you still got it?",
            "response": (
                "More than the shop. Considerably more, and the offers go up every year, which tells "
                "you the thing is appreciating and tells you why.\n\n"
                "Nizzik will not start one. She says a list like that is a thing somebody uses later, "
                "and she says it as a fee schedule, which is the goblin way of saying it without "
                "having a feeling about it. She is right. I started one anyway, years before any of it "
                "mattered, and the only honest thing left to me is to be the one holding it.\n\n"
                "It is not kindness. If I sell it, it gets used, and I will have been the man who sold "
                "it. I have been a great many things in this cove and I have never been that, and at "
                "my age a man is mostly his list of things he has not been."
            ),
        },
    },
    # ========================================================= Keeper Marla, inside, away from the rail
    "bb_marlas_question": {
        "lakeshire": {
            "label": "Why did you leave Lakeshire?",
            "response": (
                "Because a cook in Lakeshire feeds people who are going home afterwards, and I found "
                "out I did not like that as much as I thought.\n\n"
                "Eleven years ago a goblin came up the lake buying a season of salt pork and told me "
                "there was a harbour in the south where nobody had ever once sat down to eat. He "
                "meant it as a complaint about the harbour. I heard it as a vacancy.\n\n"
                "My sister still writes to ask when I am coming back. I have stopped telling her it is "
                "warm, because she thinks that is the reason, and the reason is that down here when "
                "somebody sits down it means something."
            ),
        },
        "the_boards": {
            "label": "What is it like, cooking for this town?",
            "response": (
                "Nobody here eats. They refuel, standing up, with one eye on their own crates, and "
                "then they go back out, and a quarter of them will not be in the cove next week.\n\n"
                "So I do one pot properly and I make them sit for it. That is the whole of my trade "
                "and it took me three years to stop apologising for it.\n\n"
                "And I will say this, because you have been in and out of here all season and have "
                "heard every one of them talk. Half this town is carrying something it will not put "
                "down, and the other half is charging it rent. Nizzik is kinder than she sounds, the "
                "Baron is exactly what he sounds like, and the pilot is the only one of them who ever "
                "asks me a question back."
            ),
        },
        "the_hot_water": {
            "label": "Your question. The hot water. What did you decide?",
            "response": (
                "That it is true, and that it is worse than I thought, and that I was right to keep "
                "chewing on it.\n\n"
                "Not the water. Anybody can carry water and I have carried a great deal of it. What I "
                "could not get past is the part where nobody thinks about it. A whole world of people "
                "who had been given a thing so good they stopped noticing they had it, and then it was "
                "taken off them all at once, and they came ashore here and started paying a landing "
                "fee.\n\n"
                "So you have all come an extremely long way down in the world. I have been saying it "
                "to the pot for a month. Somebody on these boards ought to have said it to you years "
                "ago and nobody has, and I am not going to pretend that is because they were "
                "busy.\n\n"
                "Sit down. Have the rest of that. It is not hot water but it is hot."
            ),
        },
    },
}
