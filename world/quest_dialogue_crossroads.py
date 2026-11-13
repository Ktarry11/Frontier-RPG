"""Dialogue topics for the Crossroads quests. Written by tools/build_crossroads_quests.py.

EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_shimmering_flats.py.
"""

QUEST_TOPICS = {
    "cr_what_it_costs": {
        "cr_thokk_eye": {
            "label": "Ask how he lost the eye.",
            "response": "Arrow. Night elf arrow, from a tree I'd walked under an hour before and looked straight up into.\n\nThat's the thing nobody tells the recruits. You don't see them. You're not meant to. The first you know of a sentinel is somebody next to you sitting down, and they don't get up.\n\nI was lucky. It went in at an angle. The orc beside me took the one that was aimed properly."
        },
        "cr_thokk_line": {
            "label": "Ask what's on the other side of the Rampart.",
            "response": "Trees. You'll think I'm being short with you. I'm not.\n\nTrees older than Orgrimmar, older than the Horde, and every one of them belongs to somebody who has been defending it since before your grandmother's grandmother. We go in to cut them because the city needs timber, and we call it the Warsong line as if it were a line. It isn't. It's wherever the last orc is standing.\n\nI'm not saying don't go. The city does need the timber. I'm saying the captain up there should know what he's spending. Take him the tag. Nine notches is nine seasons, and I'm the only one from my camp who cut all nine."
        }
    },
    "cr_crossroads_holds": {
        "cr_hold_east": {
            "label": "Tell her about the Kolkar war camp.",
            "response": "A drum. Dorn wrote that there was a drum, and I thought he was being poetic, which isn't like him.\n\nSo the taskmasters kept the warriors in line and the warbringer kept the taskmasters, and when he went down the whole camp stopped being an army and went back to being a clan with a grudge. Good. A grudge I can live next to. I've lived next to that one for years.\n\nThe south, now."
        },
        "cr_hold_south": {
            "label": "Tell her about the wardchief of Bramblescar.",
            "response": "Kishi's report was four words long. 'Thulg is dead. Arrows.'\n\nI take it that means the road to Taurajo is open and she'd like more arrows. I'll send both.\n\nYou understand what that road is? It's the only way the tauren have to reach us that doesn't go through somebody's spears. With Bramblescar leaderless, a calf could walk it. That matters more than the war camp did.\n\nAnd the water."
        },
        "cr_hold_water": {
            "label": "Tell her about the queen under Lushwater.",
            "response": "Under it. Silithid, under the oasis, and I've been watering my kodo there since I took this post.\n\nSanu says the springs are clean. She also says the thing that soured them didn't start at Lushwater - that it comes up out of the Wailing Caverns and the queen was only feeding on it. So that isn't finished. I'm aware it isn't finished.\n\nBut the water's clean today, and a week ago it wasn't, and I know who to thank."
        }
    }
}
