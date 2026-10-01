"""
One-time content-fix script (Kyle's correction, 2026-09-05): replaces the
generic procedural weapon-reward pattern on 5 Valley of Trials quests with
real, hand-authored, uniquely-named green weapons.

THE BUG THIS FIXES: vot_first_blood, vot_scorpid_trouble,
vot_nest_guardian, vot_vile_familiars, and vot_felstalkers all used
gear_reward_slot="weapon" with NO unique_item_defs, which routes through
build_reward_gear_set()'s DEFAULT_WEAPON_PLAN - a FIXED, SHARED plan of
exactly 4 weapon types (sword_1h/dagger/staff/mace_1h). Every one of
those 5 quests therefore offered the SAME 4 weapon types with the SAME
Earth-arrival flavor lines every time, just re-rolled through the
procedural "of the X" suffix system at slightly different item levels.

THE FIX: each quest gets its OWN unique_item_defs - real named items, no
name repeated across any quest. Rarity is "uncommon" (green,
(30,200,30) per rarity.json) per Kyle's explicit instruction - NOT
"rare"/blue, which is reserved for the Tiragarde Keep boss-kill
milestone built earlier this session.

FLAVOR TEXT RULE (Kyle's second correction): his 9 canonical
Earth-arrival lines (1H/2H Sword, Dagger, 1H/2H Mace, 1H/2H Axe, Wand,
Staff) are a ONE-TIME-USE POOL, not a per-weapon-type default to stamp
on every matching item forever - "these flavor texts are only for
specific quests that have weight behind them." Split 3/3/3 across
vot_first_blood / vot_scorpid_trouble / vot_nest_guardian per Kyle's
explicit split, each line used EXACTLY ONCE across the whole file.
vot_vile_familiars and vot_felstalkers get fresh bespoke text instead of
any canonical line, since the pool was already spent by the time they're
reached. Bow and Gun/Rifle's lines were left unused entirely - both real
WoW concepts, but data/items/weapon_types.json has no bow/gun weapon_type
(only thrown covers ranged-physical), so forcing either line onto
`thrown` would just be a different kind of arbitrary reuse; better to
hold them for whenever those weapon types get built for real.

Run once. Overwrites gear_reward_slot/gear_reward_rarity (cleared -
unique_item_defs takes priority per Quest.get_gear_choices) and sets
unique_item_defs on each of the 5 target quests.
"""
import json

TARGET_QUESTS = {
    "vot_first_blood": {
        # Level 1-3, kill 5 Mottled Boars - the very first quest in the
        # game. 3 of Kyle's 9 canonical Earth-arrival lines spent here.
        "unique_item_defs": [
            {
                "name": "Sandworn Fang", "slot": "main_hand", "item_level": 2,
                "rarity": "uncommon", "weapon_type": "dagger", "stat_template": "agi_physical",
                "primary_stats": {"agility": 2, "stamina": 1},
                "weapon_damage_min": 3, "weapon_damage_max": 4, "attack_speed": 1.7,
                "flavor_text": "Smaller than a kitchen knife, yet infinitely more dangerous.",
                "label": "Dagger (Agi)"
            },
            {
                "name": "Novice's Kindling Rod", "slot": "main_hand", "item_level": 2,
                "rarity": "uncommon", "weapon_type": "staff", "stat_template": "int_caster",
                "primary_stats": {"intellect": 3, "spirit": 1},
                "weapon_damage_min": 6, "weapon_damage_max": 9, "attack_speed": 3.0,
                "flavor_text": "Back home magic didn't exist, but now you harness it freely.",
                "label": "Staff (Int)"
            },
            {
                "name": "First Light Shortblade", "slot": "main_hand", "item_level": 2,
                "rarity": "uncommon", "weapon_type": "sword_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 2, "stamina": 1},
                "weapon_damage_min": 4, "weapon_damage_max": 6, "attack_speed": 2.4,
                "flavor_text": "You've never swung a blade before, but in your hands, this feels right.",
                "label": "Sword (Str)"
            }
        ]
    },
    "vot_scorpid_trouble": {
        # Level 2-5, scorpid nest - venom/carapace theme. 3 more of
        # Kyle's 9 canonical lines spent here.
        "unique_item_defs": [
            {
                "name": "Carapace-Splitter", "slot": "main_hand", "item_level": 4,
                "rarity": "uncommon", "weapon_type": "mace_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 3, "stamina": 2},
                "weapon_damage_min": 8, "weapon_damage_max": 12, "attack_speed": 2.4,
                "flavor_text": "Back home this was a museum exhibit; here, it's a problem solver.",
                "label": "Mace (Str)"
            },
            {
                "name": "Chitin-Bound Wand", "slot": "ranged", "item_level": 4,
                "rarity": "uncommon", "weapon_type": "wand", "stat_template": "int_caster",
                "primary_stats": {"intellect": 3},
                "weapon_damage_min": 5, "weapon_damage_max": 7, "attack_speed": 1.9,
                "flavor_text": "You used to think these were just plastic toys at theme parks, until spark came out the tip.",
                "label": "Wand (Int)"
            },
            {
                "name": "Chitin-Cleaver", "slot": "main_hand", "item_level": 4,
                "rarity": "uncommon", "weapon_type": "axe_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 1},
                "weapon_damage_min": 12, "weapon_damage_max": 17, "attack_speed": 3.2,
                "flavor_text": "It lacks the clean balance of a golf club, but it certainly gets the message across.",
                "label": "2H Axe (Str)"
            }
        ]
    },
    "vot_nest_guardian": {
        # Level 2-4, Den cave boss - "guardian" theme. Final 3 of Kyle's
        # 9 canonical lines spent here.
        "unique_item_defs": [
            {
                "name": "Guardian's Broken Tusk", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "axe_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 1},
                "weapon_damage_min": 10, "weapon_damage_max": 14, "attack_speed": 2.6,
                "flavor_text": "You've only ever used one of these on firewood, but targets are targets.",
                "label": "Axe (Str)"
            },
            {
                "name": "Denwalker's Greatblade", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "sword_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 2},
                "weapon_damage_min": 17, "weapon_damage_max": 23, "attack_speed": 3.4,
                "flavor_text": "In movie props this would weigh forty pounds, but here you lift it like a feather.",
                "label": "2H Sword (Str)"
            },
            {
                "name": "Guardian-Cracked Maul", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "mace_2h", "stat_template": "str_physical",
                "primary_stats": {"strength": 4, "stamina": 3},
                "weapon_damage_min": 18, "weapon_damage_max": 24, "attack_speed": 3.3,
                "flavor_text": "You used to struggle with heavy groceries - now you're swinging a cinder block on a stick.",
                "label": "2H Mace (Str)"
            }
        ]
    },
    "vot_vile_familiars": {
        # Level 3-5, Burning Blade Coven demons - fel/corrupted theme.
        # Remaining 2 items here, no canonical Earth-arrival lines left
        # to spend - fresh bespoke text instead, per Kyle's "these
        # flavor texts are only for specific quests that have weight
        # behind them" ruling (the 9 lines are a one-time-use pool, not
        # a per-weapon-type default).
        "unique_item_defs": [
            {
                "name": "Coven-Forged Cleaver", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "sword_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 3, "stamina": 3},
                "weapon_damage_min": 9, "weapon_damage_max": 13, "attack_speed": 2.4,
                "flavor_text": "The fel-etched edge still hasn't cooled all the way down, even wrapped in the sheath.",
                "label": "Sword (Str)"
            },
            {
                "name": "Familiar-Hide Grips", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "fist_weapon", "stat_template": "agi_physical",
                "primary_stats": {"agility": 3, "stamina": 2},
                "weapon_damage_min": 8, "weapon_damage_max": 11, "attack_speed": 1.8,
                "flavor_text": "Still faintly warm. You try very hard not to think about why.",
                "label": "Fist Weapon (Agi)"
            }
        ]
    },
    "vot_felstalkers": {
        # Level 3-5, felstalker hounds - speed/hunting theme. No
        # canonical lines left; fresh bespoke text tied to this quest's
        # own theme instead.
        "unique_item_defs": [
            {
                "name": "Whelp-Fang Dirk", "slot": "main_hand", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "dagger", "stat_template": "agi_physical",
                "primary_stats": {"agility": 4, "stamina": 1},
                "weapon_damage_min": 7, "weapon_damage_max": 9, "attack_speed": 1.7,
                "flavor_text": "Filed down from something that used to have teeth of its own.",
                "label": "Dagger (Agi)"
            },
            {
                "name": "Coven-Hound Sling", "slot": "ranged", "item_level": 5,
                "rarity": "uncommon", "weapon_type": "thrown", "stat_template": "agi_physical",
                "primary_stats": {"agility": 3, "stamina": 1},
                "weapon_damage_min": 7, "weapon_damage_max": 10, "attack_speed": 2.0,
                "flavor_text": "Every pack has a runt that breaks off from the others. This is what you use to make sure it doesn't get back up.",
                "label": "Thrown (Agi)"
            }
        ]
    }
}


def main():
    path = "data/quests/valley_of_trials.json"
    d = json.load(open(path))
    changed = []
    for q in d["quests"]:
        qid = q["quest_id"]
        if qid not in TARGET_QUESTS:
            continue
        q.pop("gear_reward_slot", None)
        q.pop("gear_reward_rarity", None)
        q["unique_item_defs"] = TARGET_QUESTS[qid]["unique_item_defs"]
        changed.append(qid)
    json.dump(d, open(path, "w"), indent=2)
    print(f"Replaced procedural weapon rewards with unique hand-authored sets on {len(changed)} quests:")
    for qid in changed:
        names = [i["name"] for i in TARGET_QUESTS[qid]["unique_item_defs"]]
        print(f"  {qid}: {', '.join(names)}")


if __name__ == "__main__":
    main()
