"""
VoT -> Razor Hill bridge quest chain (Kyle's original ask this session).

Two quests:
1. vot_graduation (given by Farseer Nakhtar in Valley of Trials) - a
   position-gated EXPLORE objective targeting Weapons Trainer Grokk's
   exact tile in Razor Hill (35,20), so simply entering Durotar or
   wandering near Razor Hill doesn't complete it - the player has to
   actually walk up to Grokk, matching Razor Hill's real
   design-doc-confirmed geography (its only exit leads to Durotar;
   Valley of Trials and Razor Hill are connected by walking Durotar's
   own roads, not a direct portal - see world/zone_generator.py's
   generate_razor_hill docstring).
2. razorhill_welcome (given by Weapons Trainer Grokk in Razor Hill) - a
   short welcome/orientation quest that turns in immediately (STORY-style,
   no real objective beyond accepting) and points the player at the
   wider Durotar subzones for what's next.

Chained off vot_scorpid_trouble (a currently-dead-end quest, level 2-5,
appropriate level for "you're ready to leave the valley").

Run once. Appends to valley_of_trials.json's next_quest_id chain and adds
a new razor_hill.json quest file (Razor Hill didn't have one yet).
"""
import json

VOT_GRADUATION = {
    "quest_id": "vot_graduation",
    "title": "Beyond the Valley",
    "description": (
        "Farseer Nakhtar has watched you long enough to know the valley "
        "doesn't have much left to teach you. The boars, the scorpid, "
        "even the coven's demons - you've handled what this place can "
        "throw at a green recruit, and there's a wider world waiting "
        "past the ridge that won't wait forever. Razor Hill sits at the "
        "heart of Durotar, the real town where real orcs make their real "
        "lives, and Nakhtar says it's time you saw it. Weapons Trainer "
        "Grokk holds court there and takes in every recruit who graduates "
        "out of this valley - find him, and your training truly begins."
    ),
    "giver_npc_id": "vot_greeter",
    "zone": "valley_of_trials",
    "objectives": [
        {
            "type": "explore",
            "target": "razor_hill",
            "target_x": 35,
            "target_y": 20,
            "radius": 5
        }
    ],
    "reward_exp": 300,
    "reward_gold": 1000,
    "accept_text": (
        "Follow the road north out of the valley and keep it under your "
        "feet the whole way - Durotar doesn't forgive wandering off it, "
        "not yet, not for someone as green as you still are underneath "
        "everything you've survived here. Razor Hill sits at the heart "
        "of it. Find Grokk. Tell him Nakhtar sent you, though I suspect "
        "he'll know the second he sees you carry yourself."
    ),
    "turn_in_text": (
        "You made it. Of course you made it - I wouldn't have sent you "
        "otherwise. This is farther than most of you get, in either "
        "direction of what that means. Go find Grokk properly now. What "
        "happens from here isn't mine to teach you anymore."
    ),
    "next_quest_id": None,
    "level_min": 3,
    "level_max": 6
}

RAZORHILL_WELCOME = {
    "quest_id": "razorhill_welcome",
    "title": "A Real Town",
    "description": (
        "Weapons Trainer Grokk has seen a hundred valley recruits walk up "
        "this same road, dust-covered and a little too pleased with "
        "themselves over five dead boars. He doesn't hold that against "
        "you - everyone starts somewhere, and the valley is exactly as "
        "gentle as it needs to be. Razor Hill is not the valley. Real "
        "orcs live here, real quilboar raid the farms south of town, real "
        "centaur ride the crags to the west, and something washed-up and "
        "wrong still holds the old ruins at Tiragarde Keep on the coast. "
        "Grokk wants you to understand the shape of the place before he "
        "sends you off to bleed in it."
    ),
    "giver_npc_id": "razorhill_trainer",
    "zone": "razor_hill",
    "objectives": [
        {
            "type": "story"
        }
    ],
    "reward_exp": 150,
    "reward_gold": 500,
    "accept_text": (
        "Nakhtar's recruits always have that look - like the valley was "
        "the whole world until about an hour ago. It wasn't. Durotar goes "
        "on a long way past that ridge, and it wants you dead in about "
        "six different directions at once. Rocktusk Farm to the south, "
        "quilboar raiders. Thunder Ridge to the northeast, if you want to "
        "learn what 'hits like a truck' actually means. Kolkar Crag out "
        "west, centaur that'll put an arrow in you before you see them. "
        "Scuttle Coast has murlocs if the water doesn't scare you off "
        "first. And Skull Rock - that's the Burning Blade again, same "
        "rot you already cut out of the valley, just older and meaner "
        "here. Pick a direction. I'll be here when you're ready for the "
        "next one."
    ),
    "turn_in_text": (
        "Good. Now you actually know where you're standing, instead of "
        "just knowing you're not in the valley anymore. That's worth "
        "more than it sounds like. Go pick a fight with Durotar. It's "
        "been waiting."
    ),
    "next_quest_id": None,
    "level_min": 3,
    "level_max": 6
}


def main():
    # Chain vot_scorpid_trouble -> vot_graduation
    vot_path = "data/quests/valley_of_trials.json"
    vot_data = json.load(open(vot_path))
    linked = False
    for q in vot_data["quests"]:
        if q["quest_id"] == "vot_scorpid_trouble":
            q["next_quest_id"] = "vot_graduation"
            linked = True
    if not any(q["quest_id"] == "vot_graduation" for q in vot_data["quests"]):
        vot_data["quests"].append(VOT_GRADUATION)
    json.dump(vot_data, open(vot_path, "w"), indent=2)
    print(f"Linked vot_scorpid_trouble -> vot_graduation: {linked}")
    print("Added vot_graduation to valley_of_trials.json")

    # New razor_hill.json quest file
    rh_path = "data/quests/razor_hill.json"
    rh_data = {"quests": [RAZORHILL_WELCOME]}
    json.dump(rh_data, open(rh_path, "w"), indent=2)
    print("Wrote razorhill_welcome to data/quests/razor_hill.json")


if __name__ == "__main__":
    main()
