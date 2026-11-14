"""
One-time content-addition script (Kyle's ask, 2026-09-05): adds the
Tiragarde Keep quest chain to Durotar - an approach quest (clearing the
stranded Kul Tiras garrison) followed by the Captain Thalenvorde boss
quest.

Per Kyle's explicit framing: Captain Thalenvorde is the first HUMAN a
Player character kills in this world, not a beast or a demon. The
approach quest still reads as "these are hostile soldiers, a fight" -
the weight lands specifically on the boss quest's accept/turn-in text
and its unique glove reward set, using Kyle's exact flavor text per
armor class. This matches frontier_rpg_vision.md's core premise: Players
are ordinary people from Earth, mundane lives, for whom real permanent
violence against another human is fundamentally new - "nobody dies
anymore" is true for creatures and (as far as anyone's told them) for
Players, but nothing in the vision doc says Natives get better odds than
a normal death when a Player is the one swinging the blade. The gloves
exist so that weight has somewhere to live in the player's own
inventory, not just in a line of dialogue that scrolls past once.

Also adds durotar_tiragarde_scout, the quest-giver NPC - an orc posted
to watch the ruins, placed at (90,170), a clean sand tile near the
Tiragarde Keep cave portal at Durotar (95,178) (see
world/portal_manager.py's PORTAL_DESTINATIONS). Chosen specifically to
be someone who's watched the stranded garrison for a while and has
complicated things to say about it, not a flat "kill the humans" NPC.

Run once. Appends the new NPC to ambient_npcs.json's "npcs" list and
writes a new data/quests/durotar.json (Durotar didn't have its own
quest file yet - only Valley of Trials did).
"""
import json

NEW_NPC = {
    "npc_id": "durotar_tiragarde_scout", "name": "Watchwarden Kelgrim", "zone": "durotar",
    "x": 90, "y": 170, "race": "orc", "gender": "male", "appearance_variant": 7, "facing": "down",
    "greeting": "The ruins are quiet today. Doesn't mean they're safe. It never does."
}

QUESTS = [
    {
        "quest_id": "durotar_tiragarde_approach",
        "title": "The Stranded Garrison",
        "description": (
            "Watchwarden Kelgrim has held this post at the edge of Tiragarde Keep "
            "for longer than he likes to admit. The humans washed up here years back - "
            "Kul Tiras sailors, shipwrecked or marooned, nobody's ever gotten a straight "
            "answer out of the survivors before putting them down. They dug in. Built "
            "walls out of the ruin's old stones. Now they raid the coast road when they're "
            "hungry, which is often. Kelgrim doesn't call them monsters - he's careful about "
            "that word, more careful than you'd expect from an orc who's killed his share of "
            "them. He calls them 'the stranded' and he says it like it costs him something. "
            "Thin their numbers at the outer wall - marines, deckhands, whoever's standing "
            "watch. Leave their captain for later. Kelgrim wants to talk about him separately, "
            "and he made that very clear."
        ),
        "giver_npc_id": "durotar_tiragarde_scout",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill",
                "target": "Stranded Marine",
                "alt_targets": ["Stranded Deckhand", "Kul Tiras Sharpshooter"],
                "count": 8,
                "zone": "Tiragarde Keep"
            }
        ],
        "reward_exp": 420,
        "reward_gold": 1400,
        "accept_text": (
            "Eight of them, whichever kind you find first - marines, deckhands, the ones "
            "with the long rifles up on the wall. They'll fight like people who know they're "
            "already dead men walking, because in every way that matters to them, they are. "
            "Don't mistake desperate for weak. And don't go near the one who commands them. "
            "Not yet. We'll talk about him when you're done here."
        ),
        "turn_in_text": (
            "Eight down. Good. You didn't hesitate, which tells me something about you, "
            "though I couldn't say what yet. Sit a moment before you go back in. There's "
            "still the matter of their captain, and that conversation deserves more than "
            "me shouting it at you between sword-swings."
        ),
        "next_quest_id": "durotar_tiragarde_captain",
        "level_min": 6,
        "level_max": 9,
        "gear_reward_gear_level": 8,
        "gear_reward_slot": "chest",
        "gear_reward_rarity": "uncommon"
    },
    {
        "quest_id": "durotar_tiragarde_captain",
        "title": "The Line You Cross",
        "description": (
            "Captain Thalenvorde commands what's left of the Tiragarde garrison, and "
            "Kelgrim has been putting off this conversation since you first walked up to "
            "his post. Thalenvorde is a person. Not a boar, not a demon summoned out of "
            "some tear in the world's fabric that was never going to have a name if you "
            "hadn't asked - a person, with a rank and a crew and, however he ended up here, "
            "a life before this island that Kelgrim suspects looked ordinary once. Kelgrim "
            "has killed enough of the stranded to stop feeling the weight of it years ago. "
            "He watches you carefully as he says this next part, like he's trying to remember "
            "what it was like the first time, for him. Killing a beast doesn't ask anything "
            "of you. Killing a person does, whether or not you asked to fall into a world "
            "where the second one is suddenly on the table. He isn't going to talk you out "
            "of it. The garrison won't stop raiding while Thalenvorde commands it, and that's "
            "reason enough by the only math that matters out here. But he wanted you to walk "
            "in understanding exactly what you're about to do, instead of finding out after. "
            "That's the only kindness he has to offer you today."
        ),
        "giver_npc_id": "durotar_tiragarde_scout",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Captain Thalenvorde",
                "count": 1,
                "zone": "Tiragarde Keep"
            }
        ],
        "reward_exp": 900,
        "reward_gold": 3200,
        "accept_text": (
            "I won't pretend this is the same as the boars in the valley, or the demons in "
            "that cave you cleared out as a green recruit. Thalenvorde bleeds like you do. "
            "He probably has people somewhere who'd grieve him, the way people back on your "
            "blue planet would grieve you, if news like that could even reach them anymore. "
            "None of that changes what has to happen. It just means you should know what "
            "you're carrying afterward. Go. Finish it. And however it sits with you when it's "
            "done - that's not weakness. That's just what it costs, the first time. Every "
            "time after this one gets a little quieter. I'm not sure if that's supposed to "
            "be a comfort."
        ),
        "turn_in_text": (
            "It's done, then. I can see it on you, the particular quiet that comes after - "
            "I remember mine, if you can believe an orc admitting that. Thalenvorde won't be "
            "leading raids on the coast road anymore, and the valley's a little safer for it. "
            "That part's true, and it matters. Keep what you took off him. Wear it. Not as a "
            "trophy - as a reminder, if you need one, of exactly where you stand now. You "
            "crossed a line today that doesn't uncross. Most people out here crossed it a "
            "long time before you fell into this world. Now you know what it actually weighs. "
            "That's not nothing, and I won't pretend it is."
        ),
        "next_quest_id": None,
        "level_min": 8,
        "level_max": 11,
        "unique_item_defs": [
            {
                "name": "Blood-Soaked Wraps",
                "slot": "hands",
                "item_level": 10,
                "rarity": "rare",
                "armor_type": "cloth",
                "stat_template": "int_caster",
                "primary_stats": {"intellect": 4, "spirit": 3},
                "armor_value": 10,
                "flavor_text": (
                    "No amount of scrubbing will truly clean these threads, but you "
                    "tighten the wraps anyway\u2014there is no turning back now."
                ),
                "label": "Cloth (Int)"
            },
            {
                "name": "Blood-Soaked Grips",
                "slot": "hands",
                "item_level": 10,
                "rarity": "rare",
                "armor_type": "leather",
                "stat_template": "agi_physical",
                "primary_stats": {"agility": 4, "stamina": 3},
                "armor_value": 18,
                "flavor_text": (
                    "The warmth of their life faded against your palm, leaving behind "
                    "a cold grip and a steel-hardened resolve."
                ),
                "label": "Leather (Agi)"
            },
            {
                "name": "Blood-Soaked Handguards",
                "slot": "hands",
                "item_level": 10,
                "rarity": "rare",
                "armor_type": "mail",
                "stat_template": "agi_physical",
                "primary_stats": {"agility": 3, "strength": 3, "stamina": 2},
                "armor_value": 28,
                "flavor_text": (
                    "Iron rings absorb the crimson stain, a silent armor for hands that "
                    "have crossed a line they can never uncross."
                ),
                "label": "Mail (Agi/Str)"
            },
            {
                "name": "Blood-Soaked Gauntlets",
                "slot": "hands",
                "item_level": 10,
                "rarity": "rare",
                "armor_type": "plate",
                "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 4},
                "armor_value": 42,
                "flavor_text": (
                    "Steel conceals the blood on your fingers, armoring not just your "
                    "hands, but the quiet resolve growing within you."
                ),
                "label": "Plate (Str)"
            }
        ]
    }
]


def main():
    # Add the questgiver NPC to ambient_npcs.json
    npc_path = "data/npcs/ambient_npcs.json"
    npc_data = json.load(open(npc_path, encoding="utf-8"))
    if not any(n["npc_id"] == NEW_NPC["npc_id"] for n in npc_data["npcs"]):
        npc_data["npcs"].append(NEW_NPC)
        json.dump(npc_data, open(npc_path, "w", encoding="utf-8"), indent=2)
        print(f"Added questgiver NPC: {NEW_NPC['name']} ({NEW_NPC['npc_id']}) at Durotar ({NEW_NPC['x']},{NEW_NPC['y']})")
    else:
        print(f"NPC {NEW_NPC['npc_id']} already exists, skipped.")

    # Write the new Durotar quest file
    quest_path = "data/quests/durotar.json"
    quest_data = {"quests": QUESTS}
    json.dump(quest_data, open(quest_path, "w", encoding="utf-8"), indent=2)
    print(f"Wrote {len(QUESTS)} quests to {quest_path}:")
    for q in QUESTS:
        print(f"  {q['quest_id']} - \"{q['title']}\" (level {q['level_min']}-{q['level_max']})")


if __name__ == "__main__":
    main()
