"""
Topic content for Central Stranglethorn's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own, so nobody
has to edit that file to add a zone - which is the only reason the three Stranglethorn passes can use
dialogue objectives at all while running at the same time. The shape here is exactly the shape there:

    {quest_id: {topic_id: {"label": button text, "response": what the NPC says}}}

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. world/quest.py's QuestObjective.topics is only the
completion condition; QuestDialogScreen renders a button per AUTHORED topic, so a topic listed in the
objective and missing here is a quest that cannot be finished and does not look broken.
tools/audit_quests.py checks the pair, and tools/build_stranglethorn_central_quests.py's talk() has
the other half of this note.

WHY THESE THREE AND NOT OTHERS. A dialogue objective is the right shape only when the CONTENT is the
conversation - when what the player is being handed is a thing somebody knows, and the having-asked is
the event. So:

  stvc_zultamo_courses    The zone's half of the three-generations-of-troll-stonework spine. Northern
                          Stranglethorn asks what Zul'Marosh was for and has nobody who can say;
                          Southern keeps the answer under the sea. The Gurbashi never lost theirs,
                          because they stopped being a war band and became a business, and the gatehouse
                          is where the knowledge is kept. There is no errand in that. There is a man
                          with a list and a floor plan and one question he will not answer.
  stvc_sluice_book        The far end of the knot-cord line. Pate's trade IS reading water, so the
                          deliverable of a quest about water being read is him reading it out loud.
  stvc_scrip_second       A nine-year-old was told he was wrong and has come back with questions written
                          on his hand. That is a conversation or it is nothing.

VOICE. Zul'tamo is a troll clerk: "da/dis/mon" is not his register - three generations of gatehouse
have taught him to talk like a man signing for a weight, and he is precise about what he does and does
not know. Pate is Hillsbrad, tired and practical, twenty-two years on one crank, and he would rather be
the man who asked (data/quests/hillsbrad.json, tm_sluice). Scrip is nine and from the Bay.
"""

#: (quest_id, topic_id) -> {"label", "response"}. Dict order is the natural ask order; coverage and
#: not sequence gates completion - see QuestObjective.topics_asked.
QUEST_TOPICS = {
    # =============================================================================================
    # THE GATEHOUSE. Asked standing at the foot of the stair, on the sand, which is where the first
    # answer can be pointed at. stvc_zuljana_names ends by sending the player here with the one
    # question nobody in three generations has thought to ask, so this is a payoff and not an
    # introduction.
    # =============================================================================================
    "stvc_zultamo_courses": {
        "the_one_way": {
            "label": "Why does the ring only run one way?",
            "response": (
                "You are standing where every visitor stands, and you are seeing what every "
                "visitor sees, which is a choice. Look again at the sand in front of your feet. "
                "The ring opens left and it opens right and one of those two ways closes forty "
                "paces along, against a face of rock that was never cut.\n\n"
                "Men tell you anticlockwise is tradition. It is masonry. You cannot walk the "
                "other way because the other way is not there, and it is not there because "
                "somebody decided it would not be, with a chisel, before my grandfather was born."
            ),
        },
        "the_uncut_faces": {
            "label": "Who left the two faces uncut?",
            "response": (
                "A mason. Not a priest and not a chief - the gatehouse has the course records and "
                "the course records have a mason's mark and no name, which in my family's hand "
                "means he was alive and working when the mark was cut.\n\n"
                "The eight faces were laid out. Two were never opened. Think about what that "
                "costs: you have cut a ring, you have the stone out and the men standing there, "
                "and you stop two faces short so that forever afterward a fighter comes down the "
                "stair and has no order to choose.\n\n"
                "Why a man would spend that much work on taking a choice away from somebody he "
                "would never meet, I do not know, and I will not make something up for you."
            ),
        },
        "the_word_for_sand": {
            "label": "Your word for the sand is their word for the river.",
            "response": (
                "Say it again.\n\nNo. You have it right, and the attache has it right, and I have "
                "signed that word onto paper since I was nine years old without once hearing it.\n\n"
                "It is not a word for sand and it is not a word for water. It is a word for what a "
                "thing is poured into. A bed. A shape something is put in that holds it while it "
                "goes past. Their river has one. My floor is one.\n\n"
                "So the people who cut a stair you can only climb one way, and a terrace you can "
                "only enter from below, also cut a ring you can only walk one way round - and all "
                "three of them call the thing in the middle by the same word.\n\n"
                "That is as far as I go. The rest is south, under the water, in a hall my family "
                "stopped visiting, and I have not been."
            ),
        },
    },

    # =============================================================================================
    # THE WEIR HEAD, TARREN MILL. The valley end of the knot-cord line, and the pass's fourth and
    # most deliberate Earth note: Pate does not distrust the player, he distrusts every number taken
    # since the sky changed, and he says so to their face while handing their own evidence back to
    # them. The integration is three years ago (claude/integration_timeline.md); his twenty-two years
    # on the crank is a career and is not constrained by it.
    # =============================================================================================
    "stvc_sluice_book": {
        "the_board_and_the_book": {
            "label": "What is in the book?",
            "response": (
                "Heights. One a day, more in a melt, and the date beside each one. That is the "
                "whole of it and it has taken three men's working lives.\n\n"
                "I have twenty-two years in there. The front of it is the hand of the man who had "
                "the crank before me and taught me to read the boards, and he had the first forty "
                "pages off somebody else.\n\n"
                "People think the skill is knowing when to drop the gate. It is not. Any fool can "
                "drop a gate. The skill is having written down, every day for twenty-two years, a "
                "number nothing happened about - so that on the day something does happen, you can "
                "say how far off normal it is instead of standing there with an opinion."
            ),
        },
        "what_the_knots_say": {
            "label": "What do the jungle's cords say?",
            "response": (
                "They say a waterfall came up and stayed up, and I will tell you why I believe "
                "that part. Whoever knotted these was not trying to prove anything. A man cooking "
                "a reading makes a clean line. These wander about by a knot either way, day to "
                "day, the way real water does, and then they step up all together in one month and "
                "they never come back down.\n\n"
                "A river rises when there is more rain, and then it falls, because the rain stops. "
                "It rises and stays when something new is feeding it. There is no third answer. "
                "Twenty-two years and there has never been a third answer."
            ),
        },
        "the_other_book": {
            "label": "Why do you keep a second book?",
            "response": (
                "Because the first one stopped working, and I want to be plain with you about when.\n\n"
                "Three years ago the sky changed over. After that my old book would not predict "
                "the race any more - the melt came wrong, the dry month came twice, and a man who "
                "had been right about his own water for nineteen years was suddenly guessing. So I "
                "started the second book, and I date it from the change, and I do not mix the two.\n\n"
                "Now hear the rest of it, because you will hear it worse from somebody else. I do "
                "not trust a measurement taken in the last three years. Not mine. Not the ones in "
                "your bundle. I cannot check them against anything, and I am a man who checks.\n\n"
                "That is not an accusation. You brought me the best water-writing I have seen out "
                "of a jungle and I am still going to say to your face that I cannot verify a word "
                "of it. If that sits badly, it should. It sits badly with me."
            ),
        },
    },

    # =============================================================================================
    # THE BOOTY BAY PIER. He is nine, he has been wrong in public, and the questions are on his hand.
    # No Earth note here on purpose - stvc_scrip_drums already has one, and the best thing this quest
    # can do with a child is let him be a child who runs an experiment.
    # =============================================================================================
    "stvc_scrip_second": {
        "the_crocolisk_theory": {
            "label": "So you still think it is gorilla.",
            "response": (
                "I think it CAN'T be croc, which isn't the same, Bexx says that's not the same.\n\n"
                "Look. A croc is long. A drum is round. You can't get a round thing out of a long "
                "thing without wasting most of it, and nobody down here wastes most of anything, "
                "have you MET the Bay?\n\n"
                "A gorilla's chest is round. It's right there. It's already the shape. That's not "
                "me wanting to be right, that's just - that's the shape it is."
            ),
        },
        "who_told_you_that": {
            "label": "Who told you about the drums in the first place?",
            "response": (
                "Hobb. He's nine and a half and he says that like it's a rank.\n\n"
                "Only now I've been thinking about it and Hobb's never been up the road either. "
                "He's never been past the gate. Bruiser counts us at the gate and he counts the "
                "same four of us every day and he knows all our names, so none of us has ever been "
                "a mile out of this cove.\n\n"
                "So where did Hobb get it? He got it off a sailor. And a sailor got it off a "
                "sailor. That's just a story with extra sailors in it.\n\n"
                "...that's what mine is too, isn't it. Mine's got one less sailor. That's all mine's got."
            ),
        },
        "what_he_would_do": {
            "label": "What would you do if you could get up the road?",
            "response": (
                "Measure it. Properly, with a string, and I'd cut the string and bring the string "
                "back so I wasn't just saying a number.\n\n"
                "Then I'd ask the drum crew what they feed it with - because leather wants oil, "
                "right, boots want oil, so a drum that big must drink oil, and whoever buys the "
                "oil has a book with how much in it, and a book doesn't care who's asking.\n\n"
                "That's the bit nobody does. Everyone argues about what it's MADE of. The man who "
                "sells them oil already knows and he'd tell you for nothing, because to him it's "
                "just Tuesday."
            ),
        },
    },
}
