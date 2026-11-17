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
    # -----------------------------------------------------------------------------------------------
    # Gatehouse Broker Zul'tamo, Gurbashi Arena. Old, formal, light troll speech.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stvc_zultamo_courses': {
        'the_one_way': {
            "label": 'Why does the ring only run one way?',
            "response": (
                "You're standin' where every visitor stands, and seein' what every visitor sees, which looks like"
                ' a choice. Look at da sand at your feet. Da ring opens left and right, but one of dose ways ends'
                " forty paces along at a rock face nobody ever cut. People say walkin' it anticlockwise is "
                "tradition, but it's really just masonry. You can't go da other way because it was never built, "
                'and somebody decided dat with a chisel before my grandfather was born.'
            ),
        },
        'the_uncut_faces': {
            "label": 'Who left the two faces uncut?',
            "response": (
                'A mason, not a priest or a chief. Da gatehouse keeps da old course records, and dey show a '
                "mason's mark with no name. Da ring was laid out with eight openings, and two were never cut. "
                "Think what dat cost. You've dug da ring, you've got da stone out and da men standin' dere, and "
                'you stop two openings short, so every fighter after you comes down da stair with no choice of '
                "direction. Why a man would work dat hard to take a choice away from strangers, I don't know, and"
                " I won't make somethin' up for you."
            ),
        },
        'the_word_for_sand': {
            "label": 'Your word for the sand is their word for the river.',
            "response": (
                "Say dat again. You're right, and da attache is right, and I've been signin' dat word on paper "
                "since I was nine without ever hearin' it. It ain't a word for sand or for water. It's a word for"
                " what a thing gets poured into, a bed dat holds somethin' while it passes through. Their river "
                'has one, and my arena floor is one. Da same people cut a stair you can only climb one way, a '
                'terrace you can only enter from below, and a ring you can only walk one way round, and dey '
                "called da middle of all three by da same word. Dat's as far as I can take you. Da rest is south,"
                " under da water, in a hall my family stopped visitin'."
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # Sluice-Keeper Pate, Tarren Mill. Careful, plain, a man who checks.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stvc_sluice_book': {
        'the_board_and_the_book': {
            "label": "What's in the book?",
            "response": (
                "Water heights, one a day and more during a melt, with the date beside each. That's all of it, "
                "and it's taken three men's working lives. I've got twenty-two years in there, and the front "
                'pages are in the hand of the man who had the crank before me and taught me to read the boards. '
                'People think the skill is knowing when to drop the gate, but any fool can drop a gate. The skill'
                ' is writing down a number every day for twenty-two years when nothing happens, so that when '
                "something does, you can say how far off normal it's gone instead of just having an opinion."
            ),
        },
        'what_the_knots_say': {
            "label": "What do the jungle's cords say?",
            "response": (
                'They say a waterfall rose and stayed up, and I believe it for one reason. Whoever knotted these '
                "wasn't trying to prove anything. A man faking readings makes a clean line. These wander by a "
                'knot or so from day to day, the way real water does, and then in one month they all step up '
                'together and never come back down. A river rises with more rain and falls when the rain stops. '
                "If it rises and stays up, something new is feeding it. In twenty-two years I've never found a "
                'third answer.'
            ),
        },
        'the_other_book': {
            "label": 'Why do you keep a second book?',
            "response": (
                "Because the first one stopped working, and I'll be plain about when. Three years ago the sky "
                "changed. After that my old book couldn't predict the race any more. The melt came at the wrong "
                "time, the dry month came twice, and a man who'd been right about his own water for nineteen "
                'years was suddenly guessing. So I started a second book, dated from the change, and I keep the '
                "two apart. Here's the rest, because you'll hear it worse from someone else. I don't trust any "
                "measurement taken in the last three years, mine or the ones you brought, because I can't check "
                "them against anything. That's not an accusation. It bothers me as much as it should bother you."
            ),
        },
    },
    # -----------------------------------------------------------------------------------------------
    # Scrip, Booty Bay. Nine years old, quick, stubborn.
    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).
    # -----------------------------------------------------------------------------------------------
    'stvc_scrip_second': {
        'the_crocolisk_theory': {
            "label": "So you still think it's gorilla?",
            "response": (
                "I think it CAN'T be croc, which isn't the same thing. Bexx says it's not the same. Look, a croc "
                "is long and a drum is round. You can't get a round thing out of a long thing without wasting "
                "most of it, and nobody down here wastes anything. Have you MET the Bay? A gorilla's chest is "
                "round already. That's not me wanting to be right, that's just the shape it is."
            ),
        },
        'who_told_you_that': {
            "label": 'Who told you about the drums in the first place?',
            "response": (
                "It was Hobb. He's nine and a half and he says it like it's a rank. But I've been thinking, and "
                "Hobb's never been up the road either. Bruiser Kolk counts us at the gate, and it's the same four"
                ' of us every day, so none of us has ever been a mile out of this cove. So where did Hobb get it?'
                " Off a sailor, who got it off another sailor. That's just a story with extra sailors in it. And "
                "mine's the same, isn't it? Mine's just got one less sailor."
            ),
        },
        'what_he_would_do': {
            "label": 'What would you do if you could get up the road?',
            "response": (
                "I'd measure it properly, with a string, and bring the string back so I wasn't just saying a "
                "number. Then I'd ask the drum crew what they oil it with. Leather needs oil, like boots, so a "
                'drum that big must drink loads of it, and whoever sells them the oil has a book that says how '
                "much. A book doesn't care who's asking. That's the bit nobody does. Everyone argues about what "
                'the drums are made of, and the oil seller already knows and would tell you for nothing.'
            ),
        },
    },
}
