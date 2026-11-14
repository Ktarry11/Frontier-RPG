"""
Topic content for Tempest Isle's DIALOGUE-type quest objectives.

world/quest_dialogue.py imports this module by name and merges QUEST_TOPICS into its own.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_abyssal.py for why.

Two people who stand at doors. Bron watches the gate of Khaz Varun and has never been through it;
Kettil watches the door of the Emberdeep. Each tells you what he knows before he asks for his
book to be carried.

Plain speech (Kyle, 13 Nov 2026: "NO ONE talks like this"): what happened, in order, the way a
person would tell it.
"""

QUEST_TOPICS = {
    "tmp_nine_generations": {
        "tmp_bron_the_gate": {
            "label": "Ask about the gate.",
            "response": (
                "My family kept that gate for nine generations. We looked after the hinges, "
                "counted the carts and knew everyone who went through.\n\nThen the city went "
                "dark. My great-great-grandmother was on duty that night. She said the lamps "
                "along the Ember Road went out one after another, coming toward her, and nobody "
                "came out. She shut the gate and left. My family has been ashamed of that ever "
                "since.\n\nIt stayed shut for about a hundred years. Three years ago, on the day "
                "the world changed, it opened by itself. The Thane thinks that means the city "
                "wants him back. I'm not so sure."),
        },
        "tmp_bron_the_count": {
            "label": "Ask why he's never gone in.",
            "response": (
                "Somebody has to stand here and count. If I go in and don't come out, nobody "
                "knows how many are still down there, and the Thane sends the next group in "
                "without knowing.\n\nThat's part of it. The rest is that I've seen what comes "
                "back. Some of them sit down in the forecourt and never go home. They aren't "
                "hurt, they just can't seem to leave. I don't want to end up like that."),
        },
    },
    "tmp_the_door_was_sealed": {
        "tmp_kettil_the_seal": {
            "label": "Ask about the seal.",
            "response": (
                "The dwarves of Khaz Varun mined down into this mountain, and a long time ago "
                "they broke through into the lake.\n\nThey lost a whole shift that day. The "
                "Thane at the time had the opening closed with a door of black iron, and the "
                "Keepers put a seal on it. Every year one of the Ashholds came down and said the "
                "words again.\n\nWhen the city went dark there was nobody left to say them. "
                "The seal held anyway, for about a hundred years, until three years ago."),
        },
        "tmp_kettil_the_day": {
            "label": "Ask about the day it broke.",
            "response": (
                "Nobody was here to see it. I've looked at the door, though.\n\nIt wasn't "
                "forced from our side. The iron is bent outward, like something underneath "
                "pushed it once, hard enough to fold metal as thick as my arm.\n\nThe goblins' "
                "records say the first fire elementals turned up on the Flats the same week the "
                "sea route opened. Dr. Arakawa at the Works says that's when the mountain's "
                "pulse started too. I write it down in my book whenever the door breathes out "
                "hot air, and it does that several times a day."),
        },
    },
}
