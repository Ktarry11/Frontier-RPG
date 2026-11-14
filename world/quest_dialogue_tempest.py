"""
Topic content for Tempest Isle's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_abyssal.py for why.

Two people who stand at doors. Bron watches the gate of Khaz Varun and has never been through it;
Kettil watches the door of the Emberdeep and wishes nobody would go through it. Each tells you
what he knows before he asks for his book to be carried.

Whole sentences, as a person would say them (Kyle, 13 Nov 2026).
"""

QUEST_TOPICS = {
    "tmp_nine_generations": {
        "tmp_bron_the_gate": {
            "label": "Ask about the gate.",
            "response": (
                "My family kept that arch for nine generations. We oiled the hinges, we "
                "counted the carts and we knew every face that went under it.\n\nThen the "
                "city went dark. My great-great-grandmother was on the gate that night. She "
                "said the lamps in the Ember Road went out one after another, from the far "
                "end toward her, and that nobody came running. She shut the gate and walked "
                "away, and the Emberholds have been ashamed of it ever since.\n\nIt was "
                "shut for a hundred years. It opened by itself three years ago, on the day "
                "the world changed. The Thane took that as a sign, and I took it as a "
                "warning."),
        },
        "tmp_bron_the_count": {
            "label": "Ask why he's never gone in.",
            "response": (
                "I've been asked that by every hero who's walked past me, and I'll give you "
                "the same answer I gave them.\n\nSomebody has to stand here and count. If "
                "I go in and I don't come out, nobody knows how many are still down "
                "there, and the Thane sends the next party in blind.\n\nThat's the answer "
                "I give. The other one is that I've watched what comes back. Some of them "
                "walk out and sit down in the forecourt and never go home. They aren't "
                "hurt. They just can't seem to leave. I'd sooner face anything in that "
                "city than end up sitting out there with them."),
        },
    },
    "tmp_the_door_was_sealed": {
        "tmp_kettil_the_seal": {
            "label": "Ask about the seal.",
            "response": (
                "The dwarves of Khaz Varun mined this mountain from the top down, and a "
                "long time ago they broke through into the lake.\n\nThey lost a whole "
                "shift in an afternoon. The Thane of the day had the opening closed with "
                "a door of black iron, and the Keepers set a seal on it. It was words and "
                "fire, the old way. Every year an Ashhold came down and said the words "
                "again.\n\nThat went on for longer than anyone wrote down. Then the city "
                "went dark and there was nobody left to say them, and the seal held "
                "anyway for another hundred years. I think that's the part that should "
                "worry us. It held with nobody tending it, right up until it didn't."),
        },
        "tmp_kettil_the_day": {
            "label": "Ask about the day it broke.",
            "response": (
                "I wasn't here, because nobody was. But I've seen the door, and I can "
                "tell you what it looks like.\n\nIt wasn't forced from our side. The "
                "iron's bent outward, like a lid on a pot that's boiled over. Something "
                "under the mountain pushed, once, hard enough to fold a door as thick as "
                "my arm.\n\nThe goblins' records say the first fire elementals were seen "
                "on the Flats three years ago, the same week the sea route opened. Dr. "
                "Arakawa at the Works says that's the week the mountain's heartbeat "
                "started. I don't know what he means by that. I do know that I write "
                "'it breathed' in my book several times a day, and that I didn't choose "
                "the word to be clever."),
        },
    },
}
