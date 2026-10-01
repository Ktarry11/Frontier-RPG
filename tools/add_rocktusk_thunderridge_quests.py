"""
Rocktusk Farm + Thunder Ridge quest chains (Kyle: "start building quests,
the more the better" + "not every quest needs flavor text items, but the
rewards should be hand-crafted").

IMPORTANT ENGINE FINDING that shaped this file: Durotar's subzones
(Thunder Ridge, Rocktusk Farm, Kolkar Crag, Scuttle Coast, Skull Rock
Approach) are regions painted onto the SAME "Durotar" Tilemap via
add_subzone() (world/zone_generator.py) - they are NOT separate zone
objects. combat_screen.py's CombatEngine always receives
zone_manager.current_zone.name as the zone key, which stays "durotar"
regardless of which subzone the player is standing in. A KILL objective
with zone="Thunder Ridge" would therefore NEVER match and the quest
could never complete - this is exactly the "looks done but never
executes" trap. KILL objectives have no position-gate the way EXPLORE
does, so the fix is to drop the zone restriction entirely and rely on
each target creature name being globally unique (verified against
creatures.json before writing this file) - Thunder Lizard, Stormhide
Patriarch etc. don't exist anywhere else, so an unrestricted KILL
objective is exactly as correct as a zone-gated one would have been,
without the false zone check that would silently break it. Real cave
tilemaps (Tiragarde Keep, Skull Rock, etc) ARE separate Tilemap objects
with their own .name, so zone-gating on THOSE (as done for
durotar_tiragarde_approach/captain) is correct and unaffected.

Rewards are all hand-crafted unique items (real names/stats, not
procedural "of the X" rolls) per Kyle's explicit rule, but do NOT all
carry Earth-arrival flavor text - only where it adds real weight, per
his "not every quest needs flavor text items" correction.

Both chains given by Weapons Trainer Grokk (razorhill_trainer) - the
same NPC who welcomes the player to Razor Hill in razorhill_welcome,
continuing that conversation into actual send-off quests instead of a
different NPC for every subzone.

Run once. Appends to data/quests/razor_hill.json's quest list.
"""
import json

QUESTS = [
    # ================= ROCKTUSK FARM =================
    # Level 4-8, no cave/boss - single approach-style quest, kill-clear only
    {
        "quest_id": "razorhill_rocktusk_farm",
        "title": "The Rocktusk Problem",
        "description": (
            "Rocktusk Farm sits south of Razor Hill, and it used to be "
            "farmland before the Razormane quilboar dug in and made it "
            "theirs. Grokk doesn't dress this up as anything more than it "
            "is: territory, contested, and currently losing ground to "
            "tusked raiders who've gotten bold enough to hit supply wagons "
            "on the open road. He wants their numbers thinned - "
            "battleguards, scouts, the shaman-geomancers who keep patching "
            "the others back up mid-fight. Kill enough of them and the "
            "farm quiets down for a season, maybe two."
        ),
        "giver_npc_id": "razorhill_trainer",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "kill",
                "target": "Razormane Battleguard",
                "alt_targets": ["Razormane Scout", "Razormane Geomancer"],
                "count": 10
            }
        ],
        "reward_exp": 480,
        "reward_gold": 1600,
        "accept_text": (
            "Ten of them, whichever kind - battleguard, scout, geomancer, "
            "doesn't matter which order you find them in. Kill the "
            "geomancer first if you can reach it. It'll keep healing the "
            "others just to spite you otherwise."
        ),
        "turn_in_text": (
            "Ten down. The farm won't stay quiet forever - it never does "
            "- but that buys the road some breathing room, and the "
            "wagons stop getting hit for a while. Good work."
        ),
        "next_quest_id": None,
        "level_min": 5,
        "level_max": 8,
        "unique_item_defs": [
            {
                "name": "Rocktusk Farmer's Pick", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "mace_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 3},
                "weapon_damage_min": 14, "weapon_damage_max": 19, "attack_speed": 2.5,
                "label": "Mace (Str)"
            },
            {
                "name": "Quilboar-Tusk Skinning Knife", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "dagger", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 1},
                "weapon_damage_min": 11, "weapon_damage_max": 14, "attack_speed": 1.7,
                "label": "Dagger (Agi)"
            },
            {
                "name": "Geomancer's Broken Totem-Rod", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "wand", "stat_template": "int_caster",
                "primary_stats": {"intellect": 5},
                "weapon_damage_min": 9, "weapon_damage_max": 12, "attack_speed": 1.9,
                "label": "Wand (Int)"
            }
        ]
    },

    # ================= THUNDER RIDGE =================
    # Level 7-11, real roaming boss (Stormhide Patriarch, open-world,
    # no cave needed per bestiary doc) - two-quest chain
    {
        "quest_id": "razorhill_thunder_ridge_approach",
        "title": "Thunder on the Ridge",
        "description": (
            "Thunder Ridge rises northeast of Razor Hill, a plateau where "
            "the thunder lizards nest and the air itself seems to crackle "
            "before a storm that never quite arrives. Grokk has sent "
            "recruits up there before - the ones who come back talk about "
            "how slow the lizards are right up until the moment their tail "
            "connects with something. Thin the herd. It's good practice "
            "for a fight where speed doesn't save you, only positioning "
            "does."
        ),
        "giver_npc_id": "razorhill_trainer",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "kill",
                "target": "Thunder Lizard",
                "alt_targets": ["Crackling Thunderhide"],
                "count": 8
            }
        ],
        "reward_exp": 520,
        "reward_gold": 1800,
        "accept_text": (
            "They're slow. That's the trap. Everyone who's died up there "
            "died because they got comfortable with slow and forgot to "
            "respect what happens when the hit actually lands. Watch the "
            "windup, not the lizard."
        ),
        "turn_in_text": (
            "Eight down and you're still walking without a limp. That's "
            "more than I can say for half the recruits I've sent up "
            "there. There's something bigger on that ridge, if you're "
            "not done yet - a patriarch, old and mean, the kind that's "
            "outlived every hunting party that's gone after it so far."
        ),
        "next_quest_id": "razorhill_stormhide_patriarch",
        "level_min": 7,
        "level_max": 10,
        "unique_item_defs": [
            {
                "name": "Ridgewalker's Warhammer", "slot": "main_hand", "item_level": 9,
                "rarity": "uncommon", "weapon_type": "mace_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 6, "stamina": 4},
                "weapon_damage_min": 24, "weapon_damage_max": 31, "attack_speed": 3.3,
                "label": "2H Mace (Str)"
            },
            {
                "name": "Thunderhide Bow-Grip Gloves", "slot": "hands", "item_level": 9,
                "rarity": "uncommon", "armor_type": "leather", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 3},
                "armor_value": 22,
                "label": "Leather (Agi)"
            },
            {
                "name": "Storm-Charged Focus", "slot": "off_hand", "item_level": 9,
                "rarity": "uncommon", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 6, "spirit": 2},
                "label": "Off-Hand (Int)"
            }
        ]
    },
    {
        "quest_id": "razorhill_stormhide_patriarch",
        "title": "The Old Thunder",
        "description": (
            "The Stormhide Patriarch has ruled Thunder Ridge longer than "
            "anyone in Razor Hill has been alive to remember it arriving. "
            "Grokk's own trainer sent a hunting party after it once, back "
            "when he was young enough to go himself. Three came back. He "
            "doesn't say what happened to the rest, and you get the sense "
            "he'd rather not be asked. It roams the ridge rather than "
            "guarding a den, so there's no cave to corner it in - just "
            "open ground, its size, and whatever nerve you can hold onto "
            "when something that big decides to charge."
        ),
        "giver_npc_id": "razorhill_trainer",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Stormhide Patriarch",
                "count": 1
            }
        ],
        "reward_exp": 950,
        "reward_gold": 3400,
        "accept_text": (
            "It's not clever. It doesn't need to be. It's old and it's "
            "huge and it hits like the ridge itself decided to fall on "
            "you. Don't get greedy with your own hits - patience beats "
            "size, eventually. I believe that. I have to."
        ),
        "turn_in_text": (
            "You actually did it. I'm going to be honest with you - I "
            "wasn't sure I'd be having this conversation. That thing has "
            "outlasted better fighters than either of us. Thunder Ridge "
            "is just a ridge now, not a graveyard with good scenery. "
            "Take what it was carrying. You earned every piece of it."
        ),
        "next_quest_id": None,
        "level_min": 9,
        "level_max": 11,
        "unique_item_defs": [
            {
                "name": "Patriarch's Last Roar", "slot": "main_hand", "item_level": 11,
                "rarity": "uncommon", "weapon_type": "axe_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 7, "stamina": 5},
                "weapon_damage_min": 29, "weapon_damage_max": 37, "attack_speed": 3.4,
                "flavor_text": "It still smells faintly of ozone, like the storm that never quite broke over the ridge finally did, once, all at once.",
                "label": "2H Axe (Str)"
            },
            {
                "name": "Stormhide Mantle", "slot": "shoulder", "item_level": 11,
                "rarity": "uncommon", "armor_type": "mail", "stat_template": "agi_physical",
                "primary_stats": {"agility": 6, "stamina": 4},
                "armor_value": 30,
                "label": "Mail (Agi)"
            },
            {
                "name": "Thunder-Cracked Grimoire", "slot": "off_hand", "item_level": 11,
                "rarity": "uncommon", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 7, "spirit": 3},
                "label": "Off-Hand (Int)"
            }
        ]
    }
]


def main():
    path = "data/quests/razor_hill.json"
    d = json.load(open(path))
    existing_ids = {q["quest_id"] for q in d["quests"]}
    added = []
    for q in QUESTS:
        if q["quest_id"] in existing_ids:
            continue
        d["quests"].append(q)
        added.append(q["quest_id"])
    json.dump(d, open(path, "w"), indent=2)
    print(f"Added {len(added)} quests to {path}:")
    for qid in added:
        print(f"  {qid}")


if __name__ == "__main__":
    main()
