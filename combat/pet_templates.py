"""
Pet template data. Each entry defines a summonable/tameable pet family's
base stats and starting Ability set (see entities/pet.py for how these get
turned into a live Pet instance).

Starting roster kept small on purpose - Wolf (Hunter's best-in-class
Ferocity pet per real WOTLK guides, chosen for its actually-unique family
ability rather than an arbitrary pick) and Imp (every Warlock's first,
signature demon). More families are a straightforward copy-paste of this
same shape once the acquisition flows (taming UI, demon-summon UI) exist
to actually offer a choice - no point authoring a dozen pets nobody can
reach yet.
"""

PET_TEMPLATES = {
    "wolf": {
        "display_name": "Wolf",
        "pet_type": "hunter",
        "base_hp": 140,
        "base_armor": 10,
        "base_magic_resist": 5,
        "base_attack": 22,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 8.0,
        "speed": 1.2,
        "level_req": 1,
        "abilities": [
            {
                "ability_id": "pet_wolf_bite",
                "name": "Bite",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The wolf's basic attack.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 25, "effect_value": 45}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_wolf_furious_howl",
                "name": "Furious Howl",
                "resource_type": "energy",
                "cooldown": 4,
                "effect_type": "buff",
                "duration": 2,
                "stat_mods": {"attack_power": 60},
                "description": (
                    "Real WOTLK Furious Howl buffs both the wolf AND its "
                    "Hunter's Attack Power - the wolf-only half is what's "
                    "implemented here, since a pet ability reaching out to "
                    "buff its owner as a side effect isn't a pattern "
                    "Ability.use() supports yet (every buff branch only "
                    "ever targets the caster or the caster's own "
                    "target_type='party', and a pet's owner is neither)."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": "ability_buff",
            },
        ],
    },
    "imp": {
        "display_name": "Imp",
        "pet_type": "warlock",
        "base_hp": 90,
        "base_armor": 4,
        "base_magic_resist": 10,
        "base_attack": 8,
        "base_spell_power": 14,
        "base_resource": 180,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.9,
        "level_req": 1,
        "abilities": [
            {
                "ability_id": "pet_imp_firebolt",
                "name": "Firebolt",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The Imp's only attack - a bolt of Fire damage.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 25, "effect_value": 60}
                ],
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_imp_blood_pact",
                "name": "Blood Pact",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "buff",
                "duration": 3,
                "stat_mods": {"stamina": 20},
                "description": (
                    "Real WOTLK Blood Pact also buffs the Warlock and "
                    "nearby party members - only the Imp's own Stamina "
                    "gain is implemented here, same reach-the-owner "
                    "limitation as the wolf's Furious Howl above."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 10, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": "ability_buff",
            },
        ],
    },
    "voidwalker": {
        "display_name": "Voidwalker",
        "pet_type": "warlock",
        "base_hp": 220,
        "base_armor": 22,
        "base_magic_resist": 8,
        "base_attack": 26,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "mana",
        "crit_chance": 4.0,
        "speed": 0.8,
        "level_req": 10,
        "abilities": [
            {
                "ability_id": "pet_voidwalker_smash",
                "name": "Smash",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The Voidwalker's basic melee attack.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 15, "effect_value": 55}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_voidwalker_sacrifice",
                "name": "Sacrifice",
                "resource_type": "mana",
                "cooldown": 6,
                "effect_type": "buff",
                "duration": 3,
                "stat_mods": {"armor": 80},
                "description": (
                    "Real WOTLK Sacrifice consumes the Voidwalker entirely "
                    "to shield the Warlock from damage - since a pet "
                    "consuming itself to buff its owner isn't a supported "
                    "cross-combatant effect yet, this is approximated as a "
                    "temporary Armor buff on the Voidwalker itself instead."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": "ability_buff",
            },
        ],
    },
    "succubus": {
        "display_name": "Succubus",
        "pet_type": "warlock",
        "base_hp": 150,
        "base_armor": 10,
        "base_magic_resist": 10,
        "base_attack": 24,
        "base_spell_power": 8,
        "base_resource": 120,
        "resource_type": "mana",
        "crit_chance": 8.0,
        "speed": 1.0,
        "level_req": 20,
        "abilities": [
            {
                "ability_id": "pet_succubus_lash_of_pain",
                "name": "Lash of Pain",
                "resource_type": "mana",
                "cooldown": 2,
                "effect_type": "spell_damage",
                "duration": 0,
                "stat_mods": {},
                "description": "A vicious lash dealing Shadow damage.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 30, "effect_value": 90}
                ],
                "is_instant": True,
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_succubus_seduction",
                "name": "Seduction",
                "resource_type": "mana",
                "cooldown": 6,
                "effect_type": "debuff",
                "duration": 2,
                "stat_mods": {"haste": -70},
                "description": (
                    "PLACEHOLDER (no incapacitate mechanic exists): real "
                    "WOTLK Seduction incapacitates a Humanoid/Demon target "
                    "for 15 sec - here it heavily reduces the target's "
                    "Haste for 2 turns instead."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 40, "effect_value": 100}
                ],
                "is_instant": True,
                "icon_id": "ability_debuff",
            },
        ],
    },
    "felhunter": {
        "display_name": "Felhunter",
        "pet_type": "warlock",
        "base_hp": 170,
        "base_armor": 14,
        "base_magic_resist": 16,
        "base_attack": 25,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "mana",
        "crit_chance": 6.0,
        "speed": 1.0,
        "level_req": 30,
        "abilities": [
            {
                "ability_id": "pet_felhunter_bite",
                "name": "Bite",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The Felhunter's basic melee attack.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 15, "effect_value": 55}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_felhunter_spell_lock",
                "name": "Spell Lock",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "debuff",
                "duration": 1,
                "stat_mods": {"hit_chance_spell": -70},
                "description": (
                    "PLACEHOLDER (no cast-interrupt mechanic exists): real "
                    "WOTLK Spell Lock silences for 3 sec, or interrupts and "
                    "locks out the school for 8 sec - here it heavily "
                    "reduces the target's spell hit chance for 1 turn "
                    "instead."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 40, "effect_value": 100}
                ],
                "is_instant": True,
                "icon_id": "ability_debuff",
            },
            {
                "ability_id": "pet_felhunter_devour_magic",
                "name": "Devour Magic",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "dispel",
                "duration": 0,
                "stat_mods": {},
                "description": "Purges one Magic effect from the target.",
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 35, "effect_value": 0}
                ],
                "dispel_type": "magic",
                "is_instant": True,
                "icon_id": "ability_buff",
            },
        ],
    },
}


def get_pet_template(template_id):
    return PET_TEMPLATES.get(template_id)


def pets_for_class(pet_type, level):
    """Every pet template this pet_type ("hunter" or "warlock") can
    currently acquire at this level, in level order. Used by the summon/
    tame selection UI so it only ever offers real, reachable choices."""
    matches = [
        (tid, t) for tid, t in PET_TEMPLATES.items()
        if t["pet_type"] == pet_type and level >= t.get("level_req", 1)
    ]
    return sorted(matches, key=lambda pair: pair[1].get("level_req", 1))
