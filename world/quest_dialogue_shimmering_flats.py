"""
Topic content for the Shimmering Flats' DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own. The shape is
exactly the shape there:

    {quest_id: {topic_id: {"label": button text, "response": what the NPC says}}}

EVERY TOPIC A QUEST NAMES MUST BE IN HERE. QuestObjective.topics is only the completion condition;
QuestDialogScreen renders a button per AUTHORED topic, so a topic named in an objective and missing
here is a quest that cannot be finished AND DOES NOT LOOK BROKEN. tools/audit_quests.py checks the
pair, and build_shimmering_flats_quests.talk() carries the other half of this note.

WHY THESE SIX QUESTS AND NOT OTHERS. A dialogue objective earns its place only when the CONTENT IS THE
CONVERSATION - when what the player is being handed is something a person knows, and the having-asked
is itself the event. Every one of these is a question somebody in Saltwheel has been waiting years to
be asked and will not raise themselves:

  swf_open_entries     Tozzik will not go round the town asking for entries, because asking would make
                       it a favour and a favour is not an entry. So somebody else asks, and the three
                       answers are the state of the sport in three sentences.
  swf_dust_cousins     Grizzik wants to be asked OUT LOUD what the town calls the Dustwheel, because
                       the answer is that it calls them nothing and she will not volunteer that.
  swf_dust_ledger      Winnow has been waiting three years for one specific question and nobody has
                       asked it. The quest is asking it.
  swf_salt_crossing    Eleven years of trade between two women who have never met. The deliverable of
                       a delivery quest is the message that could not go in a letter.
  swf_inn_two_years    Two people who have not spoken in two years. There is no errand in that.
  swf_solo_shrinking   The town asks itself a question at night and avoids the one person who can
                       answer it. She would like, once, to be asked rather than avoided.

VOICE. Goblins, so: fast, mercantile, and incapable of leaving a number out of a sentence. But the
register splits hard and on purpose - Mozz is openly bitter, Winnow is flat arithmetic with no feeling
attached at all, Grizzik is defensive about something she is ashamed of, Nazzik gets there before you
can, Ovi is tauren and measures in winters, and Snod has simply forgotten. A zone where every goblin
sounds resentful is as flat as one where none of them does.
"""

#: (quest_id, topic_id) -> {"label", "response"}. Dict order is the natural ask order; coverage and
#: not sequence gates completion - see QuestObjective.topics_asked.
QUEST_TOPICS = {
    # =================================================================================================
    # THE OPEN - three people asked whether they will enter a race that cannot really happen.
    # Answers: no and proud of it, yes and desperate, and yes with a condition attached that Tozzik
    # will not put on a board.
    # =================================================================================================
    "swf_open_entries": {
        "swf_topic_nazzik": {
            "label": "Ask Old Nazzik whether he will enter the Open.",
            "response": (
                "No.\n\nAnd before you tell me what you were going to tell me - I know. I hold a "
                "record on a course nobody drives, which makes it a number on a rock, and I have had "
                "three years to work that out and I worked it out in the first fortnight.\n\nIf I "
                "drive it now I beat nobody and I lose to myself at twenty-two. There is no version "
                "of that afternoon I walk away from.\n\nTell Tozzik I said no. Tell him I said it "
                "fast, so he does not think I had to consider it."),
        },
        "swf_topic_grizzik": {
            "label": "Ask Pit-Boss Grizzik whether she would crew it.",
            "response": (
                "Tomorrow. This afternoon. Give me two hours and a wheel and I will give you a crew "
                "that can turn a machine round in the time it takes you to walk the straight.\n\nI "
                "have four hands on a payroll for a race that does not run and I have never once "
                "told them that is what it is. They think there is a reason. There is a reason, it "
                "is just not the one they think.\n\nYes. Write down yes and do not let him put a "
                "question mark after it."),
        },
        "swf_topic_mozz": {
            "label": "Ask Fuel-Trader Mozz about supplying the race.",
            "response": (
                "At cost. One condition.\n\nSomebody stands under that board on the day and says out "
                "loud that this pan had two hundred racers on it before the sky changed and has six "
                "customers now, and that the two things happened in the same season, and that I am "
                "not the one who has to explain the coincidence.\n\nI am not asking anybody to blame "
                "you personally. You walked in here off a road like everyone else. But I have done "
                "the sum every night for three years and the sum does not come out any other way, "
                "and I would like it said once, by somebody, in front of people.\n\nAt cost. That is "
                "the price. It is not really about the fuel."),
        },
    },

    # =================================================================================================
    # THE DUSTWHEEL - the word. Grizzik wants to be asked, which is not the same as wanting to answer.
    # =================================================================================================
    "swf_dust_cousins": {
        "swf_topic_word": {
            "label": "Ask what the town calls the Dustwheel.",
            "response": (
                "Nothing.\n\nThat is not me being clever. Go and listen. Three years and not one "
                "person in this town has put a word on them, and the words were all available - "
                "bandits, wreckers, thieves, any of them would have done and none of them is wrong.\n\n"
                "When the track died some of us walked into town and some of us walked out onto the "
                "pan, and I have thought very hard about which way I was facing that week and I "
                "cannot honestly tell you it was a decision.\n\nSo we call them nothing, and we send "
                "somebody out to put them off a road, and we do not write it down. You made me say "
                "it. I want you to know I noticed you making me say it."),
        },
    },

    "swf_dust_ledger": {
        "swf_topic_ledger": {
            "label": "Ask Winnow what column they go in.",
            "response": (
                "Customers.\n\nThat is the answer. It has been the answer since the second winter and "
                "it is in this book in my own hand and not one person has come to this bench and "
                "asked.\n\nThey buy fuel. Not from Mozz, which is why he thinks he has lost them, but "
                "they buy it. They buy parts. They have bought salt off Jixa under a name that is not "
                "a name since before the second wet and she knows exactly who she is selling to, and "
                "she writes it in, and so do I.\n\nThis town has spent three years deciding not to "
                "have a word for people it is already trading with. I am a clerk. I have a word. The "
                "word is customers and it goes in the customers column."),
        },
    },

    # =================================================================================================
    # THE SALT LINE - eleven years of trade and never a face. Ovi is tauren: patient, dry, measures in
    # winters. She is the far end of a thread the Freewind roster planted long before this quest pass.
    # =================================================================================================
    "swf_salt_crossing": {
        "swf_topic_ovi": {
            "label": "Ask Spice-Trader Ovi the question Jixa could not write down.",
            "response": (
                "She wants to know whether I still think it is boring.\n\nI said that to somebody "
                "once, at this table, about her salt. Three climates on one table and the only thing "
                "on it that has never cost me a night's sleep is the sacks that come up from the pan, "
                "and I called that boring, and I meant it kindly, and I have wondered since whether "
                "it reached her.\n\nIt reached her. Eleven years and that is the thing she sends a "
                "stranger across a dead pan to ask about.\n\nTell her yes. Tell her boring is what I "
                "have left and I am holding onto it with both hands. The mountain can do what it "
                "likes up there as long as her pan keeps drying."),
        },
    },

    # =================================================================================================
    # THE INN - a two-year silence, and the thing neither of them will do about it.
    # =================================================================================================
    "swf_inn_two_years": {
        "swf_topic_snod": {
            "label": "Ask Snod what he and Vozzi fell out about.",
            "response": (
                "I do not remember.\n\nI want to be clear that this is not a joke and it is not me "
                "protecting her. I have sat in this bar at four in the morning with the lamps down "
                "and gone looking for it properly, more than once, and it is gone.\n\nShe remembers. "
                "I am certain of that. She has the sort of memory that keeps a grievance in good "
                "order the way I keep glasses.\n\nWhich means one of us is carrying this and it is "
                "not me, and if I walk through that door and ask her what it was, she has to say it "
                "out loud to a man who put it down two years ago and did not notice.\n\nI am not "
                "doing that to her. So we do not speak, and the business has never been better, and "
                "that is the arrangement."),
        },
    },

    # =================================================================================================
    # THE SHRINKING - the question the town asks itself at night and asks of nobody.
    # =================================================================================================
    "swf_solo_shrinking": {
        "swf_topic_shrinking": {
            "label": "Ask Winnow how much the town has shrunk.",
            "response": (
                "By a quarter. Three years, in bodies, counted twice and written both times.\n\nIn "
                "trade it is worse and I am not going to give you that figure, because a figure like "
                "that in a stranger's mouth two towns over is how a place stops getting carts.\n\n"
                "People think I keep this book to be unpleasant. Tozzik thinks it. He has never said "
                "so and he thinks it.\n\nI keep it because when a place goes, it goes without anybody "
                "writing down what was in it. No list. Nothing to say who was here or what they did "
                "or how many carts a week it took to keep them. Just a name on a map that stops being "
                "a town and nobody can tell you what it was like.\n\nThat is not happening here. "
                "Whatever else happens here, that is not happening here.\n\nThat is all. You asked. "
                "Nobody asks."),
        },
    },
}
