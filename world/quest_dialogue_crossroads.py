"""Dialogue topics for the Crossroads quests. Written by tools/build_crossroads_quests.py.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_shimmering_flats.py.
"""

QUEST_TOPICS = {
    "cr_what_it_costs": {
        "cr_thokk_eye": {
            "label": "Ask how he lost the eye.",
            "response": "A night elf arrow did it, from a tree I'd walked under an hour before and looked straight up into.\n\nThat's what nobody tells the recruits. You don't see them, and you're not meant to. The first you know of a sentinel is somebody next to you sitting down, and they don't get up again.\n\nI was lucky, because it went in at an angle. The orc beside me took the one that was aimed properly."
        },
        "cr_thokk_line": {
            "label": "Ask what's on the other side of the Rampart.",
            "response": "Trees, and you'll think I'm being short with you, but I'm not.\n\nThey're trees older than Orgrimmar, older than the Horde, and every one of them belongs to somebody who's been defending it since before your grandmother's grandmother. We go in to cut them because the city needs timber, and we call it the Warsong line as if it were a line, and it isn't one at all. It's wherever the last orc is standing.\n\nI'm not saying don't go, because the city does need the timber. I'm saying the captain up there should know what he's spending. Take him the tag. Nine notches is nine seasons, and I'm the only one from my camp who cut all nine."
        }
    },
    "cr_crossroads_holds": {
        "cr_hold_east": {
            "label": "Tell her about the Kolkar war camp.",
            "response": "There was a drum? Dorn wrote that there was a drum, and I thought he was being poetic, which isn't like him.\n\nSo the taskmasters kept the warriors in line and the warbringer kept the taskmasters, and when he went down, the whole camp stopped being an army and went back to being a clan with a grudge. I can live next to a grudge. I've lived next to that one for years.\n\nNow tell me about the south."
        },
        "cr_hold_south": {
            "label": "Tell her about the wardchief of Bramblescar.",
            "response": "Kishi's report was short, and it said Thulg was dead and asked for arrows. I take it that means the road to Taurajo is open and she'd like more arrows, and I'll send both.\n\nDo you understand what that road is? It's the only way the tauren have to reach us that doesn't go through somebody's spears. With Bramblescar leaderless, a calf could walk it. That matters more than the war camp did.\n\nNow tell me about the water."
        },
        "cr_hold_water": {
            "label": "Tell her about the queen under Lushwater.",
            "response": "There was a silithid queen under the oasis? I've been watering my kodo there since I took this post.\n\nSanu says the springs are clean. She also says the thing that soured them didn't start at Lushwater. It comes up out of the Wailing Caverns, and the queen was only feeding on it, so that isn't finished, and I know it isn't.\n\nBut the water's clean today, and a week ago it wasn't, and I know who to thank."
        }
    }
}
