"""
Kolkar Crag + Scuttle Coast + Skull Rock quest chains (Kyle: "keep
building... quests given by goblins, forsaken, even elves in the
region... quest flavors should be their style").

QUESTGIVER RACE CASTING:
- Kolkar Crag -> Kravel Coinsnatch (goblin, razorhill_goblin_trader,
  already placed). Centaur raiders hit caravans on the roads - that's a
  goblin trader's actual business interest. Voice: transactional,
  profit-first, treats violence as a business expense.
- Scuttle Coast -> Sylthressa Windmourne (blood elf, durotar_beltelf_
  merchant, already placed). She travels "between Razor Hill and the
  coast" per her existing greeting - murlocs disrupting coastal routes
  is literally her problem. Voice: clipped, a little superior, treats
  orc-run Durotar as beneath her but useful.
- Skull Rock -> new NPC, Bloodwarden Ashgrym (orc). No forsaken/undead
  playable-race NPC asset exists yet (only bare "skeleton", a different
  and much more limited asset than a real Forsaken character - flagging
  this rather than faking a Forsaken with the wrong asset). Given the
  demon-cult continuity from Valley of Trials' Burning Blade Coven
  quests, an orc who's fought this specific cult before carries the
  right weight - mirrors Elder Kuraw's "I remember when..." voice.

ENGINE NOTE: Skull Rock Approach (open Durotar subzone, trash only) vs
Skull Rock (a REAL separate cave Tilemap, confirmed via
world/portal_manager.py's registered portal Durotar (118,60) -> "Skull
Rock" (54,85), same pattern as Tiragarde Keep) are two different
locations despite the name overlap - confirmed against data/creatures/
encounters.json's zones.Durotar.subzones["Skull Rock Approach"] vs
zones.Durotar.caves["Skull Rock"] before writing anything. The approach
quest is an unrestricted kill objective (open subzones share the parent
"Durotar" zone key, so a zone restriction would silently never match).
The two boss quests correctly use zone="Skull Rock" since that cave IS a
real separate Tilemap, exactly like Tiragarde Keep.

Skull Rock has TWO real bosses (Neru Fireblade AND Gazz'uz, both
count:0 boss-only spawns per encounters.json) - built as a genuine
3-quest chain rather than picking one, since both have real stat data.

Run once. Appends to razor_hill.json (Kolkar Crag, Scuttle Coast) and
durotar.json (Skull Rock). Adds durotar_burning_blade_warden NPC.
"""
import json

NEW_NPC = {
    "npc_id": "durotar_burning_blade_warden", "name": "Bloodwarden Ashgrym", "zone": "durotar",
    "x": 100, "y": 55, "race": "orc", "gender": "male", "appearance_variant": 9, "facing": "left",
    "greeting": "The Burning Blade doesn't die easy. I've been trying for longer than I care to say."
}

RAZOR_HILL_QUESTS = [
    {
        "quest_id": "razorhill_kolkar_approach",
        "title": "Centaur Toll",
        "description": (
            "Kravel Coinsnatch runs numbers on everything, and lately the "
            "numbers on the western caravan route are bad. Kolkar "
            "centaur have turned Kolkar Crag into a toll booth nobody "
            "agreed to, and every wagon that doesn't make it through "
            "comes straight out of Kravel's margins. He's not "
            "sentimental about it. He wants the centaur numbers down and "
            "the road profitable again, in roughly that order of "
            "priority, and he's honest enough to admit it."
        ),
        "giver_npc_id": "razorhill_goblin_trader",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "kill",
                "target": "Kolkar Raider",
                "alt_targets": ["Kolkar Outrunner", "Kolkar Wrangler", "Kolkar Pack Runner", "Kolkar Windchaser"],
                "count": 10
            }
        ],
        "reward_exp": 470,
        "reward_gold": 2200,
        "accept_text": (
            "Ten centaur, any flavor - I'm not paying by the subspecies, "
            "just the body count. Every wagon that gets through instead "
            "of getting looted is money I don't have to explain to my "
            "cousin Gazlowe, and trust me, you do not want to be the "
            "reason I have to explain anything to Gazlowe."
        ),
        "turn_in_text": (
            "Ten fewer problems on the road. This is good work, the kind "
            "I'd pay for twice if the first payment weren't already "
            "covering it. There's still a warlord out there running the "
            "whole operation, if you want the real bonus."
        ),
        "next_quest_id": "razorhill_warlord_krellian",
        "level_min": 5,
        "level_max": 8,
        "unique_item_defs": [
            {
                "name": "Tollbooth Cleaver", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "axe_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 5, "stamina": 2},
                "weapon_damage_min": 15, "weapon_damage_max": 20, "attack_speed": 2.5,
                "label": "Axe (Str)"
            },
            {
                "name": "Outrunner's Own Bowstring Knife", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "dagger", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 1},
                "weapon_damage_min": 11, "weapon_damage_max": 15, "attack_speed": 1.7,
                "label": "Dagger (Agi)"
            }
        ]
    },
    {
        "quest_id": "razorhill_warlord_krellian",
        "title": "The Krellian Contract",
        "description": (
            "Warlord Krellian holds Kolkar Crag together through sheer "
            "reputation, and Kravel has done the math on this one "
            "carefully. Kill the warlord, the centaur operation "
            "fragments into raiding bands too disorganized to hit a "
            "moving wagon - or it doesn't, and a new warlord takes over "
            "in a week. Kravel thinks the odds favor fragmentation. He's "
            "willing to bet quite a lot of gold on that math being right."
        ),
        "giver_npc_id": "razorhill_goblin_trader",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Warlord Krellian",
                "count": 1
            }
        ],
        "reward_exp": 920,
        "reward_gold": 4000,
        "accept_text": (
            "Krellian is exactly what a decade of successfully robbing "
            "caravans buys a centaur - confidence, mostly, and the gear "
            "to back it up. Kill him fast if you can. Every second you "
            "spend fighting fair is a second his lieutenants have to "
            "regroup."
        ),
        "turn_in_text": (
            "Done. Beautiful. I already have three caravans queued up for "
            "the western route that were sitting idle waiting for exactly "
            "this news. You want to know the secret to profit? It's "
            "paying the right person exactly once for a problem that "
            "would've cost you ten times as much left alone. Here. You "
            "earned every coin of this."
        ),
        "next_quest_id": None,
        "level_min": 7,
        "level_max": 9,
        "unique_item_defs": [
            {
                "name": "Krellian's Broken Lance", "slot": "main_hand", "item_level": 9,
                "rarity": "uncommon", "weapon_type": "sword_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 6, "stamina": 4},
                "weapon_damage_min": 25, "weapon_damage_max": 32, "attack_speed": 3.3,
                "flavor_text": "Snapped clean at the haft when he fell. The head's still good, and it's worth more broken than most weapons are whole.",
                "label": "2H Sword (Str)"
            },
            {
                "name": "Warlord's Coinpurse Wrap", "slot": "waist", "item_level": 9,
                "rarity": "uncommon", "armor_type": "leather", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 3},
                "armor_value": 18,
                "label": "Leather (Agi)"
            }
        ]
    },
    {
        "quest_id": "razorhill_scuttle_coast",
        "title": "The Drowned Road",
        "description": (
            "Sylthressa Windmourne makes her living moving goods between "
            "Razor Hill and the coast, and Scuttle Coast has become "
            "something between an inconvenience and a genuine liability. "
            "Murlocs have claimed the shallows, and something worse "
            "washed up with them: drowned deckhands, walking wrong, that "
            "she refuses to look at directly for longer than necessary. "
            "She's not asking out of civic duty. Her supply chain runs "
            "directly through that water."
        ),
        "giver_npc_id": "durotar_beltelf_merchant",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill",
                "target": "Murloc Tidehunter",
                "alt_targets": ["Coastal Murloc", "Murloc Oracle", "Drowned Deckhand"],
                "count": 10
            }
        ],
        "reward_exp": 460,
        "reward_gold": 2000,
        "accept_text": (
            "Ten of them - I genuinely do not care which combination. "
            "The murlocs are merely unpleasant. The deckhands are "
            "something else entirely, and I would prefer not to describe "
            "what happens to a person who drowns wrong in Durotar's "
            "coastal water. Just handle it."
        ),
        "turn_in_text": (
            "The shallows are passable again, which is worth more to me "
            "than you likely realize - every day that coast stays "
            "blocked is a day my margins suffer for it. You have my "
            "gratitude, such as it is, and considerably more usefully, "
            "my gold."
        ),
        "next_quest_id": None,
        "level_min": 5,
        "level_max": 8,
        "unique_item_defs": [
            {
                "name": "Tideworn Harpoon", "slot": "main_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": "fist_weapon", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 2},
                "weapon_damage_min": 12, "weapon_damage_max": 16, "attack_speed": 1.8,
                "label": "Fist Weapon (Agi)"
            },
            {
                "name": "Oracle-Bone Focus", "slot": "off_hand", "item_level": 7,
                "rarity": "uncommon", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 5, "spirit": 2},
                "label": "Off-Hand (Int)"
            }
        ]
    }
]

DUROTAR_QUESTS = [
    {
        "quest_id": "durotar_skullrock_approach",
        "title": "Ashgrym's Old Enemy",
        "description": (
            "Bloodwarden Ashgrym has been watching Skull Rock for longer "
            "than he's willing to put a number on. The Burning Blade "
            "Coven cut into back in the valley wasn't the whole cult - "
            "just the part that wandered too far from its real nest. "
            "Skull Rock is the nest. Searing Blade scouts and raiders "
            "patrol the approach, and Ashgrym wants them cleared before "
            "anyone goes near the cave mouth. He's fought this cult "
            "before. He doesn't talk about how that went."
        ),
        "giver_npc_id": "durotar_burning_blade_warden",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill",
                "target": "Searing Blade Scout",
                "alt_targets": ["Searing Blade Raider", "Coastal Harpy"],
                "count": 10
            }
        ],
        "reward_exp": 500,
        "reward_gold": 2000,
        "accept_text": (
            "Clear the approach first. I mean that as an order, not a "
            "suggestion - the cave itself is worse, and I'd rather you "
            "walk in without half the patrol already alerted. Ten of "
            "them. Don't rush it."
        ),
        "turn_in_text": (
            "The approach is quiet. It won't stay that way once you go "
            "into the cave itself - nothing about Skull Rock stays quiet "
            "for long - but you've earned the right to try. Two names "
            "matter once you're inside: Neru Fireblade and Gazz'uz. "
            "Neither of them will make this easy."
        ),
        "next_quest_id": "durotar_skullrock_neru",
        "level_min": 7,
        "level_max": 10,
        "unique_item_defs": [
            {
                "name": "Approach-Warden's Blade", "slot": "main_hand", "item_level": 9,
                "rarity": "uncommon", "weapon_type": "sword_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 5, "stamina": 3},
                "weapon_damage_min": 17, "weapon_damage_max": 22, "attack_speed": 2.4,
                "label": "Sword (Str)"
            },
            {
                "name": "Cultwatch Grimoire", "slot": "off_hand", "item_level": 9,
                "rarity": "uncommon", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 6, "spirit": 2},
                "label": "Off-Hand (Int)"
            }
        ]
    },
    {
        "quest_id": "durotar_skullrock_neru",
        "title": "Fireblade",
        "description": (
            "Neru Fireblade holds rank inside Skull Rock through fire and "
            "force of will, in roughly that order. Ashgrym describes her "
            "the way you'd describe a wound that never fully closed - "
            "present tense, personal, unresolved. She commands the "
            "Searing Blade enforcers and warlocks who guard the cave's "
            "outer chambers, and she will not be reasoned with."
        ),
        "giver_npc_id": "durotar_burning_blade_warden",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Neru Fireblade",
                "count": 1,
                "zone": "Skull Rock"
            }
        ],
        "reward_exp": 850,
        "reward_gold": 3200,
        "accept_text": (
            "She fights with fire and she fights smart, which is a worse "
            "combination than either alone. Don't stand still. Whatever "
            "else you do in that fight, don't stand still."
        ),
        "turn_in_text": (
            "Neru's gone. I won't pretend that's simple for me to hear - "
            "old business, older than you'd guess to look at me. Gazz'uz "
            "is still down there, and he's the real reason this cave has "
            "never actually closed for good. He's not orc, or troll, or "
            "anything that bleeds the way we do. Be ready for that."
        ),
        "next_quest_id": "durotar_skullrock_gazzuz",
        "level_min": 9,
        "level_max": 11,
        "unique_item_defs": [
            {
                "name": "Fireblade's Cooling Ember", "slot": "off_hand", "item_level": 10,
                "rarity": "uncommon", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 6, "spirit": 3},
                "flavor_text": "Still warm to the touch, days later. You suspect it always will be.",
                "label": "Off-Hand (Int)"
            },
            {
                "name": "Searing Blade Warguard", "slot": "chest", "item_level": 10,
                "rarity": "uncommon", "armor_type": "mail", "stat_template": "str_physical",
                "primary_stats": {"strength": 6, "stamina": 5},
                "armor_value": 34,
                "label": "Mail (Str)"
            }
        ]
    },
    {
        "quest_id": "durotar_skullrock_gazzuz",
        "title": "What the Cave Was Guarding",
        "description": (
            "Gazz'uz is a demon, and Ashgrym is very deliberate about "
            "using that word instead of any softer one. Not a person who "
            "crossed a line, not a beast that got too big - something "
            "summoned, tearing at the world from somewhere that isn't "
            "supposed to touch it. This is the real reason Skull Rock has "
            "never fully closed. Kill it, and the cave is finally just a "
            "cave again."
        ),
        "giver_npc_id": "durotar_burning_blade_warden",
        "zone": "durotar",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Gazz'uz",
                "count": 1,
                "zone": "Skull Rock"
            }
        ],
        "reward_exp": 1000,
        "reward_gold": 4200,
        "accept_text": (
            "This one doesn't bleed the way Neru did, and it won't stop "
            "the way a person stops. Everything about it is wrong in a "
            "way I don't have good words for. Kill it anyway. That's the "
            "job, whether or not I can explain what it actually is."
        ),
        "turn_in_text": (
            "It's over. Skull Rock is just rock now, no cult, no demon, "
            "nothing left down there but the echo of what used to be. "
            "I've wanted this day for longer than you've been in this "
            "world, and I mean that far more literally than you probably "
            "assume. Whatever that thing was carrying is yours. Take it "
            "and don't look back at that cave mouth on your way out."
        ),
        "next_quest_id": None,
        "level_min": 10,
        "level_max": 11,
        "unique_item_defs": [
            {
                "name": "Gazz'uz's Unmaking", "slot": "main_hand", "item_level": 11,
                "rarity": "rare", "weapon_type": "staff", "stat_template": "int_caster",
                "primary_stats": {"intellect": 8, "spirit": 4},
                "weapon_damage_min": 30, "weapon_damage_max": 40, "attack_speed": 3.0,
                "flavor_text": "It doesn't feel like a weapon so much as a wound in the shape of one. You're not entirely sure the demon is done with it.",
                "label": "Staff (Int)"
            },
            {
                "name": "Warden's Closure", "slot": "neck", "item_level": 11,
                "rarity": "rare", "stat_template": "str_physical",
                "primary_stats": {"strength": 5, "stamina": 6},
                "flavor_text": "Ashgrym pressed this into your hand himself, and didn't say anything else. He didn't need to.",
                "label": "Neck (Str/Sta)"
            }
        ]
    }
]


def main():
    npc_path = "data/npcs/ambient_npcs.json"
    npc_data = json.load(open(npc_path))
    if not any(n["npc_id"] == NEW_NPC["npc_id"] for n in npc_data["npcs"]):
        npc_data["npcs"].append(NEW_NPC)
        json.dump(npc_data, open(npc_path, "w"), indent=2)
        print(f"Added questgiver NPC: {NEW_NPC['name']} ({NEW_NPC['npc_id']})")

    rh_path = "data/quests/razor_hill.json"
    rh_data = json.load(open(rh_path))
    existing = {q["quest_id"] for q in rh_data["quests"]}
    added_rh = []
    for q in RAZOR_HILL_QUESTS:
        if q["quest_id"] in existing:
            continue
        rh_data["quests"].append(q)
        added_rh.append(q["quest_id"])
    json.dump(rh_data, open(rh_path, "w"), indent=2)
    print(f"Added {len(added_rh)} quests to razor_hill.json: {added_rh}")

    dur_path = "data/quests/durotar.json"
    dur_data = json.load(open(dur_path))
    existing2 = {q["quest_id"] for q in dur_data["quests"]}
    added_dur = []
    for q in DUROTAR_QUESTS:
        if q["quest_id"] in existing2:
            continue
        dur_data["quests"].append(q)
        added_dur.append(q["quest_id"])
    json.dump(dur_data, open(dur_path, "w"), indent=2)
    print(f"Added {len(added_dur)} quests to durotar.json: {added_dur}")


if __name__ == "__main__":
    main()
