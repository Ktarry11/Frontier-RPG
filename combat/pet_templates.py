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
    "raptor": {
        "display_name": "Raptor",
        "pet_type": "primalist",
        "base_hp": 150,
        "base_armor": 8,
        "base_magic_resist": 5,
        "base_attack": 24,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 10.0,
        "speed": 1.3,
        "level_req": 10,
        "_source": "Primalist Wildwalker's first beast companion, built during the pet-system push (Oct 2026, Kyle: 'Primalist tames beasts like hunter, not elementals' - correcting an earlier assumption that it should be one fixed signature pet). Kept as its own pet_type ('primalist', not 'hunter') and its own first template (Raptor, distinct bleed-flavored kit from Hunter's Wolf) rather than literally sharing Wolf, since a real Primalist Hunter-style taming system should be able to grow its own beast roster the same low-effort way Hunter's did (one template at a time, added once there's a real acquisition flow to offer them through - see this file's own module docstring). Level_req 10 matches Spirit Beast Master's own unlock level.",
        "abilities": [
            {
                "ability_id": "pet_raptor_claw",
                "name": "Claw",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The raptor's basic attack.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 25, "effect_value": 46}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_raptor_rend",
                "name": "Rend",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "dot",
                "duration": 3,
                "damage_school": "physical",
                "stat_mods": {},
                "description": "Tears at the target, causing it to bleed over time.",
                "ranks": [
                    {"rank": 1, "level_req": 10, "cost": 20, "effect_value": 18}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },
    "air_elemental": {
        "display_name": "Air Elemental",
        "pet_type": "stormbringer",
        "base_hp": 130,
        "base_armor": 6,
        "base_magic_resist": 15,
        "base_attack": 0,
        "base_spell_power": 18,
        "base_resource": 160,
        "resource_type": "mana",
        "crit_chance": 6.0,
        "speed": 1.1,
        "level_req": 20,
        "_source": "Stormbringer Wind's Tempest's Call summon, built during the pet-system push (Oct 2026, Kyle: 'We need the pet system up and running... since we have hunters, warlocks, primalist, and wind spec stormbringer'). Unlike Hunter/Warlock/Primalist (all acquired through the real taming/summon SCREEN via pets_for_class), this pet_type is never passed to pets_for_class - Stormbringer summons it directly by casting stormbringer_summon_air_elemental, same as any other ability, so this template only needs to exist for get_pet_template to find, not for the screen's roster listing. level_req 20 matches the real ability's own level_req. A caster-style ranged pet (base_attack 0, real base_spell_power) rather than a melee beast, matching real WoW air elementals and this spec's own lightning/wind theme. NOTE: a tier-5 Wind talent, Lexicon of Servitude ('Increases your Air Elemental's damage by 6% per rank'), reads a pet_damage stat_mod key that is NOT currently read anywhere in the engine (same unsupported-suffix category as several other talent keys flagged this session) - flagging here rather than silently leaving it un-flagged, since this is the talent's only real payload and it does nothing right now.",
        "abilities": [
            {
                "ability_id": "pet_air_elemental_lightning_bolt",
                "name": "Lightning Bolt",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "nature",
                "stat_mods": {},
                "description": "The Air Elemental's only attack - a bolt of Nature damage.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 25, "effect_value": 58}
                ],
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_air_elemental_updraft",
                "name": "Updraft",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "buff",
                "duration": 3,
                "stat_mods": {"dodge": 15},
                "description": "Rides the winds, increasing its own Dodge chance.",
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": "ability_buff",
            },
        ],
    },
    "ziggi_6k": {
        "display_name": "ZIGGI-6K",
        "pet_type": "tinker",
        "base_hp": 110,
        "base_armor": 10,
        "base_magic_resist": 8,
        "base_attack": 0,
        "base_spell_power": 16,
        "base_resource": 160,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 1.0,
        "level_req": 10,
        "_source": "Tinker Invention's capstone, built during the pet-system push (Oct 2026, Kyle: 'ZIGGI-6K is a pet (like an imp) that helps heal with wrench toss (deals small damage and smart heals ally)'). Same pattern as Stormbringer's Air Elemental: never passed to pets_for_class (Tinker summons it directly by casting tinker_build_ziggi_6k, not through a taming/summon screen). Wrench Toss itself uses effect_type=damage_and_heal (same real mechanic Mage's Cryotherapist talents already use) so one cast both hits the enemy AND smart-heals the owner's lowest-HP party member - fixed a real bug alongside this (combat/combat_engine.py's execute_pet_action wasn't passing `party` to a pet's ability.use() at all, so this would have silently healed only the pet itself, never a real ally, before this fix). Two more abilities added at pet levels 20/30 (Kyle: 'ziggi gets an expensive aoe heal at lvl 20 and evocation like skill at 30') - these level_req values are the PET's own level (synced 1:1 to the owner's character level via Character.summon_pet/sync_to_owner_level), not a separate pet-rank system, same as every other pet template's abilities. Learning a new ability at a LATER level than the pet's own tame-time level is a first for this template set, and surfaced a real bug in entities/pet.py's sync_to_owner_level/_autofill_hotbar (fixed alongside this - see that file's own comments): newly-learned abilities were never added to the hotbar after construction. This template's own level_req LOWERED from 50 to 10 to match tinker_build_ziggi_6k's own ability-level_req drop and the talent's move to tier 1 - Character.summon_pet checks THIS field separately from the ability's own level_req, so both had to move together or the ability would have been castable at 10 while still failing the pet's own gate underneath it.",
        "abilities": [
            {
                "ability_id": "pet_ziggi_6k_wrench_toss",
                "name": "Wrench Toss",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage_and_heal",
                "duration": 0,
                "damage_school": "physical",
                "stat_mods": {},
                "description": "ZIGGI-6K's basic action - tosses a wrench at an enemy for small damage while smart-healing the lowest-HP ally.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 25, "effect_value": 18, "heal_value": 45}
                ],
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_ziggi_6k_regenerative_field",
                "name": "Regenerative Field",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "heal",
                "target_type": "party",
                "duration": 0,
                "damage_school": "physical",
                "stat_mods": {},
                "description": "An expensive but powerful heal to the whole party, learned once ZIGGI-6K reaches level 20.",
                "_source": "Kyle: 'ziggi gets an expensive aoe heal at lvl 20'. Real target_type=party heal (same mechanic as Asher's Resignation/Circle of Healing) - the engine's real AOE_DAMAGE_MULTIPLIER heal-parity penalty already applies automatically to any multi-recipient heal (see Ability._apply_heal_effect), so this doesn't need its own AoE discount logic. Costly (90 of ZIGGI-6K's 160 max mana at this level) and on a real cooldown to match 'expensive' rather than being a spammable party heal.",
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 90, "effect_value": 70}
                ],
                "icon_id": "ability_heal",
            },
            {
                "ability_id": "pet_ziggi_6k_overcharge",
                "name": "Overcharge",
                "resource_type": "mana",
                "cooldown": 6,
                "effect_type": "restore_resource",
                "target_type": "self",
                "is_instant": True,
                "duration": 0,
                "stat_mods": {},
                "description": "Channels raw power into ZIGGI-6K's own battery, instantly restoring a large chunk of its Mana. Learned at level 30.",
                "_source": "Kyle: 'evocation like skill at 30' - an Evocation-like self-only resource-restore, new effect_type=restore_resource built for this (combat/abilities.py), since no existing effect_type was a pure self-buff resource refill with no attached damage/heal (damage_and_restore_mana - Stormbringer's Discharge - always also hits an enemy). Reuses the existing mana_restore_pct rank key (already used by Discharge) rather than adding a near-duplicate field.",
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 0, "mana_restore_pct": 60}
                ],
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
    # Cultist's two summons were effect_type "buff" with empty stat_mods, so
    # casting them summoned nothing at all. They are real summon_pet abilities
    # now, which needed templates: a melee bruiser and a healer minion,
    # matching their own descriptions ("an ally-fighting Faceless Destroyer",
    # "a minion that periodically heals nearby allies").
    "faceless_destroyer": {
        "display_name": "Faceless Destroyer",
        "pet_type": "cultist",
        "base_hp": 260,
        "base_armor": 28,
        "base_magic_resist": 14,
        "base_attack": 34,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.85,
        "level_req": 30,
        "abilities": [
            {
                "ability_id": "pet_faceless_rend",
                "name": "Rend",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The Faceless Destroyer's basic melee attack.",
                "ranks": [{"rank": 1, "level_req": 1, "cost": 10, "effect_value": 62}],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_faceless_dread_howl",
                "name": "Dread Howl",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "debuff",
                "duration": 3,
                "stat_mods": {"attack_power": -30},
                "description": "Cows the target, weakening its attacks.",
                "ranks": [{"rank": 1, "level_req": 30, "cost": 20, "effect_value": 100}],
                "is_instant": True,
                "icon_id": "ability_debuff",
            },
        ],
    },
    "mindbender": {
        "display_name": "Mindbender",
        "pet_type": "cultist",
        "base_hp": 170,
        "base_armor": 14,
        "base_magic_resist": 20,
        "base_attack": 14,
        "base_spell_power": 30,
        "base_resource": 160,
        "resource_type": "mana",
        "crit_chance": 4.0,
        "speed": 0.9,
        "level_req": 30,
        "abilities": [
            {
                "ability_id": "pet_mindbender_lash",
                "name": "Mind Lash",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "stat_mods": {},
                "damage_school": "shadow",
                "description": "The Mindbender's basic shadow attack.",
                "ranks": [{"rank": 1, "level_req": 1, "cost": 14, "effect_value": 48}],
                "is_instant": True,
                "icon_id": "ability_shadow",
            },
            {
                "ability_id": "pet_mindbender_mend",
                "name": "Whispered Mending",
                "resource_type": "mana",
                "cooldown": 2,
                "effect_type": "heal",
                "duration": 0,
                "stat_mods": {},
                "description": "Heals the most wounded nearby ally.",
                "ranks": [{"rank": 1, "level_req": 30, "cost": 25, "effect_value": 85}],
                "target_type": "ally",
                "is_instant": True,
                "icon_id": "ability_heal",
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
