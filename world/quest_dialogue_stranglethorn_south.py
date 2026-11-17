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
    # -----------------------------------------------------------------------------------------------
    # Pilot Zan'rek, Booty Bay. Troll, proud, has carried this alone a long time.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'bb_kundaraz_means': {
        'the_name': {
            "label": 'What does Kundaraz mean?',
            "response": (
                "Da water comin' up. Not da sea, because da sea has its own word and it ain't a nice one. "
                "Kundaraz is water risin' to where you put it, because you put it dere. Everyone in dat port "
                'calls it da ruin, and when dey want to be polite dey call it da drowned place, which is da same '
                "insult in a nicer hat. A drowned place is somewhere somethin' happened to. Zul'Kundaraz is named"
                " for da thing happenin'. Da masons signed dere work in da name, and den da water rose over da "
                "signature. I think dey'd have found dat funny."
            ),
        },
        'three_cities': {
            "label": 'Three cities, one way of building. What does that mean?',
            "response": (
                "It means all three were cut by people taught da same way, who didn't argue with it. Da courts in"
                " da north nobody can read, da arena in da middle still full of shoutin', and ours. Three sets of"
                ' hands, hundreds of years apart, and one measure through all of dem. Da rule you carried north '
                "would fit any of da three. Da newest is da biggest, and it's da one under salt water, and "
                "everybody gets dat backwards. Dey didn't get worse at buildin'. Dey got bolder, and den dey were"
                ' done.'
            ),
        },
        'what_the_sluice_got': {
            "label": 'What has Pate actually got, then?',
            "response": (
                "A set of decisions. Dat's all a weir pin is. Long ago somebody stood in a junction, worked out "
                "how fast da hall should fill, and cut da answer in stone so da next crew wouldn't have to guess."
                " Your sluice-keeper has been guessin' for nine years with a wooden wedge and a bad temper, and "
                "now he doesn't have to. Dat's a big gift. And here's what I didn't say in front of him. I've "
                'carried dis my whole life and offered it to dat port whenever anyone would listen, and nobody '
                'ever did. Da first person who wanted it runs a mill in Hillsbrad and has never seen da place. '
                "I've decided to be pleased about dat. It took me a week."
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # The Quiet Man, Booty Bay. The fence. Careful, exact, not kind and says so.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'bb_quiet_mans_ledger': {
        'the_book': {
            "label": "What's actually in the book?",
            "response": (
                'Boats and years, nothing else, and I want you to understand how little that is. Which ship came '
                "in, on what tide, who walked off it, and when. I started it because a man in my trade who can't "
                'say where a thing came from is handling stolen goods, and one who can is handling goods with a '
                "history, and that's worth money. Then the world changed and the boats stopped being boats I "
                'knew, and I kept writing, because stopping would have been a decision and writing was a habit. '
                "So yes, you're in it. Ship, tide and year, three lines, the same as everybody."
            ),
        },
        'who_comes_asking': {
            "label": 'Who comes asking after it?',
            "response": (
                'Three kinds, and I can tell which before they finish their first sentence. Insurers, who want a '
                'ship. Families, who want a name, usually get one, and almost never thank me. And then the third '
                'kind, who ask very politely for everybody who arrived in a particular season. Not a name, a '
                "season. I've been asked that four times, and every one of them had a good reason ready before I "
                "opened my mouth. That's how I knew. A man with a good reason to want a list of strangers has "
                "already thought about what he'll do with it."
            ),
        },
        'what_it_is_worth': {
            "label": "What's it worth, and why do you still have it?",
            "response": (
                "More than this shop, and the offers go up every year, and that's why. Nizzik won't keep a "
                "list like that. She says it's something somebody uses later, and she's right. I started mine "
                'years before any of it mattered, and the only honest thing left to me is to be the one holding '
                "it. That isn't kindness. If I sell it, it gets used, and I'll be the man who sold it. I've been "
                "a lot of things in this cove, but never that, and at my age a man is mostly the things he's "
                'refused to be.'
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # Keeper Marla, Booty Bay tavern. From Lakeshire, warm, blunt.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'bb_marlas_question': {
        'lakeshire': {
            "label": 'Why did you leave Lakeshire?',
            "response": (
                "Because a cook in Lakeshire feeds people who are going home afterwards, and I found I didn't "
                "like that as much as I'd thought. Eleven years ago a goblin came up the lake buying salt pork "
                'and told me about a harbour in the south where nobody ever sat down to eat. He meant it as a '
                "complaint, and I heard it as a job opening. My sister still writes to ask when I'm coming back. "
                "I've stopped telling her it's warm, because she thinks that's the reason. The reason is that "
                'down here, when someone sits down to eat, it means something.'
            ),
        },
        'the_boards': {
            "label": "What's it like, cooking for this town?",
            "response": (
                'Nobody here eats. They refuel standing up, with one eye on their crates, and go back out, and a '
                "quarter of them won't be in the cove next week. So I make one pot properly and make them sit for"
                " it. That's my whole trade, and it took me three years to stop apologising for it. And since "
                "you've been in and out all season and heard them all talk: half this town is carrying something "
                "it won't put down, and the other half is charging it rent. Nizzik is kinder than she sounds, the"
                ' Baron is exactly what he sounds like, and the pilot is the only one who ever asks me a question'
                ' back.'
            ),
        },
        'the_hot_water': {
            "label": 'Your question about the hot water. What did you decide?',
            "response": (
                "That it's true, and worse than I thought, and I was right to keep chewing on it. It's not the "
                "water. Anyone can carry water, and I've carried plenty. What I couldn't get past is that nobody "
                'thinks about it. A whole world of people were given something so good they stopped noticing they'
                ' had it, then had it taken away all at once, and came ashore here and started paying a landing '
                "fee. So you've all come a long way down in the world. I've been saying that to the stew pot for "
                'a month, and somebody on these boards should have said it to you long ago. Sit down and finish '
                "that. It isn't hot water, but it's hot."
            ),
        },
    },
}
