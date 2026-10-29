"""
Pet template data. Each entry defines a summonable/tameable pet family's
base stats and starting Ability set (see entities/pet.py for how these get
turned into a live Pet instance).

The roster started small on purpose - Wolf (Hunter's best-in-class Ferocity
pet per real WOTLK guides, chosen for its actually-unique family ability
rather than an arbitrary pick) and Imp (every Warlock's first, signature
demon) - on the reasoning that more families were a straightforward
copy-paste of this same shape once the acquisition flows (taming UI,
demon-summon UI) existed to offer a real choice.

That reasoning held for the two classes with a taming/summon SCREEN and
broke badly for everyone else. Abilities that summon a pet by being CAST do
not wait for an acquisition flow, and by Oct 2026 there were 28 of them
across 13 classes still pointing at a 14-template roster, so 14 summons
handed the player something with the wrong name, the wrong school and the
wrong kit: Raise: Ghoul produced a pet named "Wolf", Raise: Banshee
produced "Succubus", and once multi-pet support landed a Necromancer stood
four of those borrowed pets on the field at once. The roster is now one
template per summon (see SUMMON_THEME_SOURCE below for the fix and for the
four engine limits every template is authored around).

TWO SEPARATE THINGS CALLED "A PET TEMPLATE" LIVE HERE, and the difference
matters when adding one:
  - Templates reachable through ui/screens/pet_screen.py, which maps only
    the classes Hunter -> "hunter", Warlock -> "warlock" and Primalist ->
    "primalist". Only a template whose pet_type is one of those three is
    ever offered as a choice on that screen.
  - Templates that exist only so get_pet_template can find them, summoned
    by casting an ability (every Tinker construct, Stormbringer's Air
    Elemental, the Cultist, Necromancer, Reaper, Felsworn, Knight of
    Xoroth, Witch Hunter, Barbarian and Ranger summons). These carry their
    own class's slug as pet_type precisely so they do NOT surface on that
    screen for the wrong class.
A template's level_req is checked by Character.summon_pet separately from
its summon ability's own level_req, so the two always have to move
together.
"""

SENTRY_SOURCE = (
    'Tinker construct, authored 2026-10-28 to fix a real bug: tinker_build_sentry_turret, _clockwork_assistant, _mechano_bear and _rusthound all shipped with effect_type="summon", which the ability engine does not handle - it only branches on "summon_pet", and only with a summon_pet_template. All four had no template either, so four abilities on a shipped class spent their resource and summoned nothing. Found by tools/validate_class.py\'s effect_type check. Like ZIGGI-6K and Stormbringer\'s Air Elemental these are never passed to pets_for_class - the Tinker builds them by casting the ability, not through a taming screen - so the template only has to exist for get_pet_template to find. level_req matches each ability\'s own level_req, because Character.summon_pet gates on THIS field separately and the two have to move together.'
)

SUMMON_THEME_SOURCE = (
    'Authored 2026-10-29 to fix the summon/template mismatch: 28 summon_pet '
    'abilities across the game pointed at only 14 templates, so 14 of them '
    'summoned something with the wrong name and the wrong kit. A Necromancer '
    'casting Raise: Ghoul fielded a pet literally named "Wolf"; with multi-pet '
    'support (Character.EXTRA_PET_CAP) the same Necromancer fielded Wolf, Imp, '
    'Succubus and Faceless Destroyer side by side. Every template below is the '
    'thing its own ability says it summons, built from the CoA sidekick '
    'tooltip quoted in its own _source.\n'
    '\n'
    'FOUR ENGINE LIMITS EVERY TEMPLATE HERE IS AUTHORED AROUND. All four were '
    'read out of the engine before authoring, not guessed, and none of them is '
    'fixable from this file:\n'
    '\n'
    '1. PET AI ONLY EVER SELECTS A DAMAGE ABILITY OR A SELF-HEAL. '
    'Pet.choose_action (entities/pet.py) picks, in order: a "heal" when the pet '
    'is under 40% health, then the highest-effect_value ability whose '
    'effect_type is in ("damage", "spell_damage", "ranged_damage", '
    '"damage_and_heal"), then hotbar slot 0 as the guaranteed fallback. A '
    '"dot", "debuff" or "buff" on a pet is therefore NEVER cast in combat. Four '
    'shipped templates carry one anyway (Wolf\'s Furious Howl, Air Elemental\'s '
    'Updraft, Clockwork Assistant\'s Calibrate, Mechano-Bear\'s Iron Hide, plus '
    'Raptor\'s and Rusthound\'s dots) and none of them has ever fired. Rather '
    'than add fourteen more buttons that do nothing, every pet below gets TWO '
    'abilities the AI genuinely reaches: a cheap slot-0 basic and a costlier, '
    'cooldown-gated signature with a higher effect_value. Where a CoA tooltip '
    'describes a debuff or an aura instead, that half is named in the '
    'template\'s own _source and deliberately NOT authored.\n'
    '\n'
    '2. THE AI RANKS DAMAGE OPTIONS BY effect_value, NOT BY REAL DAMAGE. '
    'choose_action does max(damage_options, key=lambda a: a.effect_value), but '
    'actual damage is effect_value + attack_power*0.5 for "damage" and '
    'effect_value + spell_power*1.5 for "spell_damage"/"damage_and_heal"/'
    '"damage_and_restore_mana". A high-effect_value ability that scales off the '
    'stat its pet does not have would be PREFERRED while hitting for less. '
    'Every pair below is checked so the signature wins on both counts at the '
    'summon level AND at 60 - see each template\'s own _source for the two '
    'numbers.\n'
    '\n'
    '3. PET AoE IS NOT EXPRESSIBLE RIGHT NOW, EITHER WAY. CombatEngine\'s '
    'execute_pet_action does read is_aoe - but _ability_from_data '
    '(combat/abilities.py) never passes is_aoe to Ability(), and Ability.'
    '__init__ does not accept it, so getattr(ability, "is_aoe", False) is '
    'False on every pet ability no matter what the template says. The other '
    'route is worse: target_type "enemy_aoe" makes execute_pet_action take its '
    'single-target branch anyway (it only passes the full enemy list when '
    'is_aoe is true), so _hostile_recipients gets ONE enemy while '
    'AOE_DAMAGE_MULTIPLIER is still applied - strictly worse than plain '
    '"enemy". So no template here is authored with either, and the CoA '
    'tooltips that describe a cleave (Ghoul\'s leeching plague, Skeletal Mage\'s '
    'ice, Abomination\'s cloud, Spectral Scythe\'s 5-target strike, Rampaging '
    'Hounds) are implemented single-target with the right damage school.\n'
    '\n'
    '4. A PET HEAL AND A PET PARTY BUFF BOTH GO NOWHERE. Heal amount is '
    'effect_value + healing_power*1.2, and Pet._apply_template_stats hardcodes '
    'healing_power = 0, so a pet heal is a flat number forever - negligible '
    'against a level-60 pet\'s own level-scaled health pool. Worse, '
    'target_type "party" on a pet resolves through _recipients(caster, target) '
    'where target is the pet\'s ENEMY, so a non-list target falls through to '
    '[caster]: a party-wide pet heal or buff lands on the pet alone. The ONE '
    'ally-reaching pet effect that does work is "damage_and_heal", which '
    'routes through _apply_smart_heal(caster, party, heal_value) and does get a '
    'real party list from execute_pet_action - which is exactly why the Ghoul\'s '
    'CoA leech ("its auto attacks restore SP health to you") is authored that '
    'way and nothing else below carries a heal at all.\n'
    '\n'
    'VALUE CONVENTIONS, for any future edit here: damage_taken_pct and '
    'max_health_pct are FRACTIONS (0.10 = 10%); armor_pct, stamina_pct, block, '
    'parry, dodge and haste are PERCENT POINTS (10 = 10%). A buff/debuff rank '
    'needs effect_value 100 to mean "apply stat_mods as written" - '
    'Ability._stat_mod_scalar multiplies the mods by effect_value/100, and 113 '
    'shipped abilities authored effect_value 0 and applied nothing. There is '
    'now a guard that reads a zero scalar with mods present as "as written", '
    'but author the 100 anyway.\n'
    '\n'
    'pet_type is the owning class\'s slug for all fourteen. It is deliberately '
    'NOT "hunter", "warlock" or "primalist": those three are the only values '
    'ui/screens/pet_screen.py maps a class to, so anything carrying one would '
    'appear as a tameable choice on that screen for the wrong class. These are '
    'all cast-summoned directly, same as the Tinker constructs and '
    'Stormbringer\'s Air Elemental, so the template only has to exist for '
    'get_pet_template to find. level_req on each matches its own summon '
    'ability\'s level_req, because Character.summon_pet gates on THIS field '
    'separately and the two have to move together.'
)

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
        "_source": "Stormbringer Wind's Tempest's Call summon, built during the pet-system push (Oct 2026, Kyle: 'We need the pet system up and running... since we have hunters, warlocks, primalist, and wind spec stormbringer'). Unlike Hunter/Warlock/Primalist (all acquired through the real taming/summon SCREEN via pets_for_class), this pet_type is never passed to pets_for_class - Stormbringer summons it directly by casting stormbringer_summon_air_elemental, same as any other ability, so this template only needs to exist for get_pet_template to find, not for the screen's roster listing. level_req 20 matches the real ability's own level_req. A caster-style ranged pet (base_attack 0, real base_spell_power) rather than a melee beast, matching real WoW air elementals and this spec's own lightning/wind theme. NOTE: a tier-5 Wind talent, Lexicon of Servitude ('Increases your Air Elemental's damage by 6% per rank'), reads a pet_damage key. That key WAS unread when this note was written; entities/pet.py now reads pet_damage and pet_health off the owner's talents, so the talent works. Separately, the real CoA Lexicon of Servitude does something else entirely - 'causing your next Summon: Air Elemental to be instant cast and cost no mana' - which matters because the spec page calls the slow re-summon its biggest weakness",
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
    "sentry_turret": {
        "display_name": "Sentry Turret",
        "pet_type": "tinker",
        "base_hp": 70,
        "base_armor": 24,
        "base_magic_resist": 0,
        "base_attack": 18,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 5.0,
        "speed": 1.0,
        "level_req": 1,
        "_source": SENTRY_SOURCE,
        "abilities": [
            {
                "ability_id": "pet_sentry_turret_bullet_spray",
                "name": "Bullet Spray",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "ranged_damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The turret's only job: put rounds downrange.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 20, "effect_value": 30}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },
    "clockwork_assistant": {
        "display_name": "Clockwork Assistant",
        "pet_type": "tinker",
        "base_hp": 105,
        "base_armor": 14,
        "base_magic_resist": 6,
        "base_attack": 20,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 6.0,
        "speed": 1.1,
        "level_req": 8,
        "_source": SENTRY_SOURCE,
        "abilities": [
            {
                "ability_id": "pet_clockwork_assistant_spanner_strike",
                "name": "Spanner Strike",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It swings the heaviest tool it is holding.",
                "ranks": [
                    {"rank": 1, "level_req": 8, "cost": 22, "effect_value": 38}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_clockwork_assistant_calibrate",
                "name": "Calibrate",
                "resource_type": "energy",
                "cooldown": 5,
                "effect_type": "buff",
                "duration": 3,
                "stat_mods": {"haste": 6.0},
                "description": "A few quick adjustments and it runs faster.",
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": None,
            },
        ],
    },
    "mechano_bear": {
        "display_name": "Mechano-Bear",
        "pet_type": "tinker",
        "base_hp": 260,
        "base_armor": 42,
        "base_magic_resist": 10,
        "base_attack": 30,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 5.0,
        "speed": 0.9,
        "level_req": 14,
        "_source": SENTRY_SOURCE + " The Mechano-Bear is the durable one of "
                   "the four - highest health and armour, slowest speed - so "
                   "a Tinker has something that can hold a hit.",
        "abilities": [
            {
                "ability_id": "pet_mechano_bear_piston_maul",
                "name": "Piston Maul",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "Hydraulics do the work a shoulder used to.",
                "ranks": [
                    {"rank": 1, "level_req": 14, "cost": 25, "effect_value": 52}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_mechano_bear_iron_hide",
                "name": "Iron Hide",
                "resource_type": "energy",
                "cooldown": 6,
                "effect_type": "buff",
                "duration": 2,
                "stat_mods": {"damage_taken_pct": -0.2},
                "description": "Plating locks down over the joints.",
                "ranks": [
                    {"rank": 1, "level_req": 26, "cost": 0, "effect_value": 100}
                ],
                "target_type": "self",
                "is_instant": True,
                "icon_id": None,
            },
        ],
    },
    "rusthound": {
        "display_name": "Rusthound",
        "pet_type": "tinker",
        "base_hp": 180,
        "base_armor": 20,
        "base_magic_resist": 8,
        "base_attack": 44,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 10.0,
        "speed": 1.4,
        "level_req": 30,
        "_source": SENTRY_SOURCE + " The Rusthound is the aggressive one - "
                   "fastest, highest attack and crit, thin armour - and the "
                   "latest of the four at level 30.",
        "abilities": [
            {
                "ability_id": "pet_rusthound_scrap_bite",
                "name": "Scrap Bite",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "Teeth that were never meant to be teeth.",
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 22, "effect_value": 70}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_rusthound_corroding_wound",
                "name": "Corroding Wound",
                "resource_type": "energy",
                "cooldown": 4,
                "effect_type": "dot",
                "duration": 3,
                "stat_mods": {},
                "description": "The bite keeps working after it lets go.",
                "ranks": [
                    {"rank": 1, "level_req": 38, "cost": 25, "effect_value": 26}
                ],
                "is_instant": True,
                "icon_id": None,
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

    # ------------------------------------------------------------------
    # NECROMANCER - the four Animation raises. These are the only pets in
    # the game fielded SIMULTANEOUSLY (Character.EXTRA_PET_CAP gives
    # Necromancer 3 beyond active_pet, and all four abilities carry
    # additional_pet), so they are the one set that has to be balanced as a
    # BOARD rather than as four separate pets. See SUMMON_THEME_SOURCE.
    #
    # POWER TARGET, and why. Each minion is sized well under the weakest
    # Warlock demon so no single raise ever reads as a better button than a
    # Warlock summon, and they are spread by CoA's own Life Force cost
    # (Ghoul 1, Skeletal Mage 2, Banshee 2, Abomination 3) so the expensive
    # one is the strong one. Per-turn damage at level 60, averaged across
    # each pet's basic and signature: Ghoul ~48, Skeletal Mage ~67, Banshee
    # ~66, Abomination ~68. The Warlock demons at the same level are
    # Felhunter 178, Voidwalker 183, Succubus 208, Imp 267 - so every
    # individual minion sits at 27-38% of the WEAKEST demon.
    #
    # Aggregate, stated plainly rather than buried: all four together come
    # to ~249, which is 0.93x the strongest demon (Imp) and 1.40x the
    # weakest (Felhunter). It is NOT under 1x of every demon, and tuning it
    # there would have put each minion near 11% of a demon - a button not
    # worth pressing. The four-body board costs four separate casts and
    # four separate resource payments to assemble, each body is frail
    # (95-200 base health against the Voidwalker's 220), and the upside
    # over one demon is ~20% on the damage mean. Flagged here so it can be
    # cut deliberately if that trade is judged too generous.
    "ghoul": {
        "display_name": "Ghoul",
        "pet_type": "necromancer",
        "base_hp": 95,
        "base_armor": 8,
        "base_magic_resist": 4,
        "base_attack": 6,
        "base_spell_power": 2,
        "base_resource": 120,
        "resource_type": "mana",
        "crit_chance": 7.0,
        "speed": 1.15,
        "level_req": 8,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: necromancer_raise_ghoul pointed at "wolf" and '
            'summoned a pet named Wolf. CoA class tree, Raise: Ghoul - "Raise '
            'a Ghoul to aid you in combat occupying 1 Life Force. Its auto '
            'attacks restore SP health to you. Command: Expels leeching plague '
            'that strikes up to 5 nearby enemies, dealing Intellect Plague '
            'damage, and healing you for Intellect for each Ghoul." The leech '
            'is the whole identity, so Leeching Bite is effect_type '
            'damage_and_heal - the ONE pet effect that actually reaches a real '
            'ally (limit 4 in SUMMON_THEME_SOURCE), smart-healing the owner\'s '
            'lowest-health party member. It scales off spell power rather than '
            'attack power, which is not an accident: CoA writes the leech as '
            '"SP health", i.e. off the Necromancer\'s spell power, so a Ghoul '
            'carrying a little spell power of its own is the faithful reading '
            'and not a stat bolted on to make the numbers work. The Command\'s '
            '5-target plague is the AoE half and is not authored (limit 3). '
            'Cheapest raise in CoA at 1 Life Force, so the weakest of the '
            'four here. Damage ordering holds at both ends: at the summon '
            'level Claw 22 vs Leeching Bite 28, at 60 Claw 45 vs Leeching '
            'Bite 51, so the signature is both the higher effect_value the AI '
            'sorts on and the harder hit. Fast (speed 1.15) for CoA\'s own '
            'Ghoul Mastery haste theme - "transformed into a Frenzied Ghoul, '
            'increasing haste by 40%" - which is a proc on the owner\'s talent '
            'tree, not a pet ability, so nothing is authored for it here.'
        ),
        "abilities": [
            {
                "ability_id": "pet_ghoul_claw",
                "name": "Claw",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It does not aim. It just keeps reaching.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 16}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_ghoul_leeching_bite",
                "name": "Leeching Bite",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "damage_and_heal",
                "duration": 0,
                "damage_school": "shadow",
                "stat_mods": {},
                "description": (
                    "What it tears loose goes back down the line to whoever "
                    "needs it most."
                ),
                "ranks": [
                    {"rank": 1, "level_req": 8, "cost": 30,
                     "effect_value": 22, "heal_value": 20}
                ],
                "is_instant": True,
                "icon_id": "ability_shadow",
            },
        ],
    },
    "skeletal_mage": {
        "display_name": "Skeletal Mage",
        "pet_type": "necromancer",
        "base_hp": 100,
        "base_armor": 6,
        "base_magic_resist": 12,
        "base_attack": 0,
        "base_spell_power": 3,
        "base_resource": 150,
        "resource_type": "mana",
        "crit_chance": 6.0,
        "speed": 0.95,
        "level_req": 14,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: necromancer_raise_skeletal_mage pointed at "imp" '
            'and summoned a pet named Imp. CoA class tree, Raise: Skeletal '
            'Mage - "Raise a Skeletal Mage to aid you in combat, occupying 2 '
            'Life Force. Command: Unleashes ice at your target and enemies '
            'within 6 yds, dealing frost SP Frost damage." So: a Frost caster, '
            'base_attack 0 and real base_spell_power, same caster shape as '
            'Stormbringer\'s Air Elemental rather than a melee beast. Both '
            'abilities are damage_school "frost" spell_damage, which is also '
            'what keeps the AI\'s effect_value ranking honest (limit 2) - two '
            'abilities off the same scaling stat cannot invert. The Command\'s '
            '6-yard splash is the AoE half and is not authored (limit 3). Per '
            'turn at 60: Frostbolt 60, Rime Lance 74.'
        ),
        "abilities": [
            {
                "ability_id": "pet_skeletal_mage_frostbolt",
                "name": "Frostbolt",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "frost",
                "stat_mods": {},
                "description": "The staff still works. The hands barely do.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 18, "effect_value": 16}
                ],
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_skeletal_mage_rime_lance",
                "name": "Rime Lance",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "frost",
                "stat_mods": {},
                "description": "A spike of old ice, thrown hard.",
                "ranks": [
                    {"rank": 1, "level_req": 14, "cost": 40, "effect_value": 30}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },
    "banshee": {
        "display_name": "Banshee",
        "pet_type": "necromancer",
        "base_hp": 115,
        "base_armor": 8,
        "base_magic_resist": 16,
        "base_attack": 0,
        "base_spell_power": 3,
        "base_resource": 160,
        "resource_type": "mana",
        "crit_chance": 7.0,
        "speed": 1.0,
        "level_req": 20,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: necromancer_raise_banshee pointed at "succubus" '
            'and summoned a pet named Succubus. CoA class tree, Raise: Banshee '
            '- "Raise a Banshee to aid you in combat, occupying 2 Life Force. '
            'It will channel on your target, dealing damage and draining their '
            'mana over time. Command: Drains 20% of your target\'s mana (up to '
            'a maximum of 40% of their own maximum mana) and deals Frost '
            'damage equal to the mana drained." Mana Siphon is effect_type '
            'damage_and_restore_mana - Stormbringer\'s Discharge mechanic, '
            'which restores the CASTER\'s pool as a side effect of hitting an '
            'enemy. BE CLEAR ABOUT WHAT THAT IS AND IS NOT: the Frost damage '
            'is faithful, and the resource gain is the Banshee refilling '
            'herself, NOT the target-side mana drain CoA describes. Draining a '
            'target\'s mana has no mechanic in this engine at all (no effect '
            'type reduces an enemy\'s pool), and handing the drained mana to '
            'the pet\'s OWNER is the same unsupported pet-reaches-its-owner '
            'pattern the Wolf\'s Furious Howl and the Voidwalker\'s Sacrifice '
            'are both already approximated around. High magic resistance, low '
            'armour - she is not solid. Per turn at 60: Wail 60, Mana Siphon '
            '72.'
        ),
        "abilities": [
            {
                "ability_id": "pet_banshee_wail",
                "name": "Wail",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "shadow",
                "stat_mods": {},
                "description": "The sound arrives before she does.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 20, "effect_value": 16}
                ],
                "icon_id": "ability_shadow",
            },
            {
                "ability_id": "pet_banshee_mana_siphon",
                "name": "Mana Siphon",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "damage_and_restore_mana",
                "duration": 0,
                "damage_school": "frost",
                "stat_mods": {},
                "description": "She drinks whatever is keeping them upright.",
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 38,
                     "effect_value": 28, "mana_restore_pct": 12}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },
    "abomination": {
        "display_name": "Abomination",
        "pet_type": "necromancer",
        "base_hp": 200,
        "base_armor": 26,
        "base_magic_resist": 10,
        "base_attack": 8,
        "base_spell_power": 3,
        "base_resource": 130,
        "resource_type": "mana",
        "crit_chance": 4.0,
        "speed": 0.75,
        "level_req": 30,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: necromancer_raise_abomination pointed at '
            '"faceless_destroyer" and summoned the Cultist\'s pet. CoA class '
            'tree, Raise: Abomination - "Raise an Abomination to aid you in '
            'combat, occupying 3 Life Force. It is surrounded by a disease '
            'cloud, dealing SP Nature damage to enemies when they deal damage '
            'and reducing their attack speed by 20% for 15 seconds. Command: '
            'Instantly unleashes an empowered disease cloud around it." The '
            'most expensive raise at 3 Life Force, so the strongest and by far '
            'the most durable of the four - though its 200 base health is '
            'still under the Warlock Voidwalker\'s 220, and its damage is well '
            'under the Cultist Faceless Destroyer (62 basic, 34 attack) it '
            'used to borrow. Disease Cloud is spell_damage/nature, matching '
            'CoA\'s "SP Nature damage", and it scales off a small '
            'base_spell_power so it stays the harder hit of the two at every '
            'level (summon level 41 vs 58; at 60, 59 vs 78) rather than just '
            'the higher effect_value the AI sorts on. TWO HALVES '
            'DELIBERATELY NOT AUTHORED: the -20% attack speed is a debuff, '
            'which a pet never casts (limit 1 - the live key would be '
            '"haste", percent points, so -20), and the cloud\'s area effect is '
            'the AoE half (limit 3). What is here is the Abomination as a slow '
            'soak that also carries plague, which is the part of the tooltip '
            'this engine can actually run.'
        ),
        "abilities": [
            {
                "ability_id": "pet_abomination_hook_and_drag",
                "name": "Hook and Drag",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "The hook goes out. Something comes back.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 20}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_abomination_disease_cloud",
                "name": "Disease Cloud",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "nature",
                "stat_mods": {},
                "description": "It opens up and the air goes bad.",
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 34, "effect_value": 34}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },

    # ------------------------------------------------------------------
    # REAPER - two Soulreaper summons, one pet slot (no EXTRA_PET_CAP entry
    # for Reaper), so these replace each other and each can sit in the
    # ordinary single-pet power band rather than the Necromancer's board
    # budget.
    "spectral_scythe": {
        "display_name": "Spectral Scythe",
        "pet_type": "reaper",
        "base_hp": 90,
        "base_armor": 6,
        "base_magic_resist": 6,
        "base_attack": 20,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 15.0,
        "speed": 1.5,
        "level_req": 34,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: reaper_spectral_scythe pointed at '
            '"faceless_destroyer" and summoned the Cultist\'s pet. CoA Reaper '
            'tree, Spectral Scythe - "Summons 1 Spectral Scythe for each '
            'Reaped Soul active which attack a nearby enemy for 20 seconds. '
            'Striking enemies with Soul Strike causes the Spectral Scythe to '
            'attack that enemy and 5 nearby enemies. Consumes Reaped Souls and '
            'Soul Infusion." A floating animated weapon, not a body: lowest '
            'health in this batch, almost no armour, fastest turn speed of the '
            'melee pets, and the highest crit chance of any pet in the game '
            'because a scythe is the crit fantasy. THREE THINGS CoA DESCRIBES '
            'THAT ARE NOT AUTHORED. (a) One scythe per Reaped Soul: '
            'Character.EXTRA_PET_CAP has no Reaper entry, so a second summon '
            'replaces the first; a resource-counted number of pets is an '
            'engine feature, not a template one. (b) The 5-target Soul Strike '
            'cleave is the AoE half (limit 3). (c) "ignoring resistances, '
            'absorption, and invulnerability effects" (from the sibling '
            'Wraithblade tooltip) has no flag - both abilities are plain '
            'physical "damage", which is also why damage_school is omitted '
            'rather than set to "shadow": the "damage" branch in '
            'combat/abilities.py hardcodes take_damage(..., "physical"), so a '
            'damage_school on a physical ability is read by nothing. Per turn '
            'at 60: Reaping Arc 127, Soulcleave 149.'
        ),
        "abilities": [
            {
                "ability_id": "pet_spectral_scythe_reaping_arc",
                "name": "Reaping Arc",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "No hand on the handle and it still swings true.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 28}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_spectral_scythe_soulcleave",
                "name": "Soulcleave",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It picks a seam and opens it.",
                "ranks": [
                    {"rank": 1, "level_req": 34, "cost": 30, "effect_value": 50}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },
    "spectral_warden": {
        "display_name": "Spectral Warden",
        "pet_type": "reaper",
        "base_hp": 230,
        "base_armor": 30,
        "base_magic_resist": 20,
        "base_attack": 18,
        "base_spell_power": 0,
        "base_resource": 140,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.8,
        "level_req": 44,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: reaper_spectral_warden pointed at "voidwalker" '
            'and summoned a pet named Voidwalker. CoA Reaper tree, Spectral '
            'Warden - "Summon a spectral guardian to fight along side you for '
            '20 seconds and apply an absorption shield to up to 8 allies '
            'within 20 yds, absorbing Stamina damage." Built as the protective '
            'counterpart to the Spectral Scythe: most health and armour of the '
            'two, and deliberately the LOWER damage of the two (130 per turn '
            'at 60 against the Scythe\'s 138) so the choice between them is '
            'durability against output rather than a strict upgrade. THE '
            'PARTY ABSORPTION SHIELD IS NOT AUTHORED, and that is the main '
            'thing to know about this template. The buff branch in '
            'combat/abilities.py does support a real shield via absorb / '
            'absorb_pct_max_health, so it looks authorable - but on a pet it '
            'fails twice over (limits 1 and 4): a "buff" is never selected by '
            'Pet.choose_action, and target_type "party" on a pet resolves to '
            '[the pet] because _recipients is handed the pet\'s enemy as '
            'target. Authoring it would have produced exactly the kind of '
            'correct-looking dead data this codebase keeps catching, so the '
            'Warden gets a second real strike instead and the shield is '
            'recorded here as owed. A self-heal was considered and rejected '
            'for the same reason: heal amount is effect_value + '
            'healing_power*1.2 and a Pet\'s healing_power is hardcoded 0, so a '
            'flat 90 heal against this pet\'s ~2,265 health at level 60 is '
            'noise.'
        ),
        "abilities": [
            {
                "ability_id": "pet_spectral_warden_warding_strike",
                "name": "Warding Strike",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It steps in front of you first, then it hits back.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 14, "effect_value": 30}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_spectral_warden_sunder_guard",
                "name": "Sunder Guard",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "A slow swing with the whole weight of it behind.",
                "ranks": [
                    {"rank": 1, "level_req": 44, "cost": 38, "effect_value": 52}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },

    # ------------------------------------------------------------------
    # FELSWORN
    "infernal": {
        "display_name": "Infernal",
        "pet_type": "felsworn",
        "base_hp": 210,
        "base_armor": 24,
        "base_magic_resist": 14,
        "base_attack": 24,
        "base_spell_power": 8,
        "base_resource": 120,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.85,
        "level_req": 28,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: felsworn_infernal pointed at "voidwalker" and '
            'summoned a pet named Voidwalker. CoA Felsworn tree, Infernal - '
            '"Drop an infernal from the sky with grotesque magic, dealing fire '
            'SP Fire damage to enemies in the radius, horrifying them for 4 '
            'seconds, and spawning an Infernal to fight by your side for 15 '
            'seconds. Inner Demon: Lasts 1 additional sec." The on-landing '
            'burst and the horrify belong to the ABILITY, not the pet, so this '
            'template is only the Infernal that stands up afterwards: a heavy, '
            'slow fire bruiser. Immolation is spell_damage/fire for CoA\'s own '
            '"SP Fire damage" and carries the higher real damage at every '
            'level (summon level 91 vs 117; at 60, 148 vs 174) off a real '
            'base_spell_power, so the AI\'s effect_value sort and actual '
            'output agree (limit 2). ~160 per turn at 60 puts it just under '
            'the weakest Warlock demon (Felhunter 178), which is the right '
            'side of the line for a class whose Infernal spec also has '
            'Infernal Summoner ("5% chance to reset the cooldown of '
            'Infernal") and Infernal Ruin ("every 3rd Ruin or Felwrath now '
            'spawns an Infernal") - the spec expects to have one up often, so '
            'the pet itself should not be a demon-grade body.'
        ),
        "abilities": [
            {
                "ability_id": "pet_infernal_fel_smash",
                "name": "Fel Smash",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It brings both arms down and the ground gives.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 14, "effect_value": 30}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_infernal_immolation",
                "name": "Immolation",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "Standing near it is already a mistake.",
                "ranks": [
                    {"rank": 1, "level_req": 28, "cost": 38, "effect_value": 56}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },

    # ------------------------------------------------------------------
    # KNIGHT OF XOROTH - three called demons, one pet slot, so they form a
    # ladder that replaces itself: Hellfire Imp at 12, Greater Imp at 18,
    # Hellfire Abyssal at 40.
    "hellfire_imp": {
        "display_name": "Hellfire Imp",
        "pet_type": "knight_of_xoroth",
        "base_hp": 100,
        "base_armor": 6,
        "base_magic_resist": 12,
        "base_attack": 4,
        "base_spell_power": 7,
        "base_resource": 160,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.95,
        "level_req": 12,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE IS THE ONE ADDITION NOT ON THE ORIGINAL FIX LIST, '
            'so the reasoning is on the record: knight_of_xoroth_call_hellfire'
            '_imp pointed at "warlock" template "imp", which is thematically '
            'defensible - an imp summoning an Imp is not a Ghoul summoning a '
            'Wolf. It was split out anyway for two reasons. First, CoA names '
            'the creature itself: Call: Hellfire Abyssal\'s tooltip reads '
            '"Costs 15 less Rage for each active Hellfire Imp", so "Hellfire '
            'Imp" is the real name, not a Frontier embellishment. Second, this '
            'class\'s sibling summon (Greater Imp) now has its own template, '
            'and leaving the lesser one borrowing the Warlock\'s Imp would have '
            'given one class an "Imp" and a "Greater Imp" from two different '
            'rosters with the Warlock\'s own fire numbers underneath. Reverting '
            'this one entry to "imp" is a one-line change if that trade is '
            'judged not worth a template. Built as a fire caster, markedly '
            'weaker than the Warlock Imp it replaced (123-141 per turn at 60 '
            'against the Warlock Imp\'s 267) because Knight of Xoroth is a '
            'plate melee class whose called demons are a side channel, not its '
            'damage identity. Both abilities are spell_damage/fire off the same '
            'stat, so the AI\'s effect_value ranking cannot invert (limit 2).'
        ),
        "abilities": [
            {
                "ability_id": "pet_hellfire_imp_cinder_bolt",
                "name": "Cinder Bolt",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "Small, and it throws harder than it looks.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 18, "effect_value": 20}
                ],
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_hellfire_imp_scorch",
                "name": "Scorch",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "It holds the fire a moment longer before letting go.",
                "ranks": [
                    {"rank": 1, "level_req": 12, "cost": 36, "effect_value": 38}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },
    "greater_imp": {
        "display_name": "Greater Imp",
        "pet_type": "knight_of_xoroth",
        "base_hp": 130,
        "base_armor": 8,
        "base_magic_resist": 14,
        "base_attack": 6,
        "base_spell_power": 8,
        "base_resource": 180,
        "resource_type": "mana",
        "crit_chance": 8.0,
        "speed": 1.0,
        "level_req": 18,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: knight_of_xoroth_summon_greater_imp pointed at '
            '"felhunter" and summoned a pet named Felhunter. CoA Knight of '
            'Xoroth tree, Greater Imp - "Level 10 Passive. Teaches you Summon: '
            'Greater Imp and increases your expertise by 10. Summon: Greater '
            'Imp - Summon a Greater Imp to aid you in combat. Greater Imp has '
            'various combat abilities that provide excellent single target '
            'damage and control." "Excellent single target damage" is the '
            'brief, so this is the strongest of the two imps and tuned up '
            'against the Hellfire Imp rather than down from the Warlock\'s '
            'Felhunter: 142-164 per turn at 60, which stays under the Felhunter '
            '(178) it was borrowing. "Control" is the part NOT authored - every '
            'control shape in this engine is a debuff or the ability-level '
            'is_stun flag, and a pet never casts a debuff (limit 1). '
            '"Excellent single target" also reads as permission to leave the '
            'AoE half alone, which suits limit 3.'
        ),
        "abilities": [
            {
                "ability_id": "pet_greater_imp_felbolt",
                "name": "Felbolt",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "Bigger, meaner, and it knows the difference.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 20, "effect_value": 24}
                ],
                "icon_id": "ability_spell",
            },
            {
                "ability_id": "pet_greater_imp_immolating_grasp",
                "name": "Immolating Grasp",
                "resource_type": "mana",
                "cooldown": 3,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "It takes hold and does not let the fire out.",
                "ranks": [
                    {"rank": 1, "level_req": 18, "cost": 40, "effect_value": 46}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },
    "hellfire_abyssal": {
        "display_name": "Hellfire Abyssal",
        "pet_type": "knight_of_xoroth",
        "base_hp": 255,
        "base_armor": 32,
        "base_magic_resist": 18,
        "base_attack": 24,
        "base_spell_power": 9,
        "base_resource": 130,
        "resource_type": "mana",
        "crit_chance": 5.0,
        "speed": 0.75,
        "level_req": 40,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: knight_of_xoroth_call_hellfire_abyssal pointed at '
            '"voidwalker" and summoned a pet named Voidwalker. CoA Knight of '
            'Xoroth tree, Call: Hellfire Abyssal - "Call down a Hellfire '
            'Abyssal from the sky to crash down upon the targeted 8 yd area, '
            'dealing AP Fire damage. The abyssal remains to aid you in battle '
            'for 15 seconds and emits an aura that reduces the damage taken by '
            'party and raid members within 40 yds by 5%. Costs 15 less Rage '
            'for each active Hellfire Imp." The landing burst belongs to the '
            'ability; this is the body that stays. Biggest and slowest of the '
            'three Xoroth demons - most health and armour in this batch after '
            'the Faceless Destroyer, and the slowest turn speed of any pet in '
            'the game. THE PARTY DAMAGE-REDUCTION AURA IS NOT AUTHORED. It '
            'would be a buff with stat_mods {"damage_taken_pct": -0.05} - a '
            'FRACTION, per this file\'s value conventions, and the live key is '
            'real - but on a pet it is dead twice over (limits 1 and 4): '
            'Pet.choose_action never selects a buff, and target_type "party" '
            'from a pet resolves to the pet alone. A permanent aura is also '
            'not a thing this engine has at all - every buff here is a cast '
            'with a duration. Recorded as owed rather than shipped as a button '
            'that does nothing. Per turn at 60: Abyssal Slam 148, Hellfire '
            'Crash 189; ordering holds at the summon level too (112 vs 148).'
        ),
        "abilities": [
            {
                "ability_id": "pet_hellfire_abyssal_slam",
                "name": "Abyssal Slam",
                "resource_type": "mana",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "Everything in reach stops being upright.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 14, "effect_value": 30}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_hellfire_abyssal_hellfire_crash",
                "name": "Hellfire Crash",
                "resource_type": "mana",
                "cooldown": 4,
                "effect_type": "spell_damage",
                "duration": 0,
                "damage_school": "fire",
                "stat_mods": {},
                "description": "It drops its shoulders and the fire comes up through the stone.",
                "ranks": [
                    {"rank": 1, "level_req": 40, "cost": 40, "effect_value": 56}
                ],
                "icon_id": "ability_spell",
            },
        ],
    },

    # ------------------------------------------------------------------
    # WITCH HUNTER - the Houndmaster's two hounds. KNOWN CONTENT PROBLEM,
    # not fixable from this file: Witch Hunter has no Character.
    # EXTRA_PET_CAP entry, so Unleash the Hounds (level 20) REPLACES the
    # permanent Shadowhound from Houndmaster's Whistle (level 1) with the
    # deliberately weaker Lesser Shadowhound - a level-20 button that
    # downgrades you. Setting additional_pet on the ability would be dead
    # data without a cap entry (Character.summon_pet ignores additional when
    # max_extra_pets is 0), so it is left alone and reported instead. CoA
    # itself reads as a board - Houndmaster's Call and Rampaging Hounds both
    # say "Hounds", plural.
    "shadowhound": {
        "display_name": "Shadowhound",
        "pet_type": "witch_hunter",
        "base_hp": 130,
        "base_armor": 9,
        "base_magic_resist": 7,
        "base_attack": 20,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 9.0,
        "speed": 1.25,
        "level_req": 1,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: witch_hunter_houndmasters_whistle pointed at '
            '"wolf" and summoned a pet named Wolf. That was the most '
            'defensible of the fourteen mismatches - a houndmaster\'s hound '
            'really is wolf-shaped - but CoA names the creature and gives it '
            'its own mechanic, so it gets its own template. CoA Witch Hunter '
            'tree, Houndmaster - "Level 10 Passive. Your ranged auto attacks '
            'now generate Rage. In addition, teaches you Houndmaster\'s '
            'Whistle. Houndmaster\'s Whistle - Summons a permanent Shadowhound '
            'companion to aid you in combat. Your Shadowhound receives 25% of '
            'healing done to you." Deliberately built close to the Wolf it '
            'replaced (139-159 per turn at 60 against the Wolf\'s 153, 130 '
            'health against 140) because that mapping was never a power '
            'problem, only a naming one - a Witch Hunter who had this pet '
            'before should not notice a balance change, only the right name. '
            'THE HEALING SPLIT IS NOT AUTHORED: "receives 25% of healing done '
            'to you" is an owner-to-pet redirect, which is the same '
            'pet-cannot-reach-its-owner gap the Wolf\'s Furious Howl and the '
            'Imp\'s Blood Pact are both already approximated around, just in '
            'the other direction. Also note the energy pool: 100 flat at every '
            'level (Pet._apply_template_stats does not scale energy) with no '
            'between-turn regeneration for pets at all, so costs here are 12 '
            'and 30 rather than the shipped beasts\' 20-25 - see the report\'s '
            'engine-findings section.'
        ),
        "abilities": [
            {
                "ability_id": "pet_shadowhound_shadow_bite",
                "name": "Shadow Bite",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It takes the first thing it can reach and keeps it.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 40}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_shadowhound_throat_hold",
                "name": "Throat Hold",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It goes for the throat and sits down on the problem.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 30, "effect_value": 60}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },
    "lesser_shadowhound": {
        "display_name": "Lesser Shadowhound",
        "pet_type": "witch_hunter",
        "base_hp": 95,
        "base_armor": 6,
        "base_magic_resist": 5,
        "base_attack": 14,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 7.0,
        "speed": 1.3,
        "level_req": 20,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: witch_hunter_unleash_the_hounds pointed at '
            '"raptor" and summoned a pet named Raptor - the Primalist\'s '
            'tameable beast, on a Witch Hunter. CoA Witch Hunter tree, Unleash '
            'the Hounds - "Summon 1 Lesser Shadow Hound to aid you in combat '
            'for 20 seconds." CoA says Lesser, so this is authored as plainly '
            'weaker than the Shadowhound in every stat: 97-115 per turn at 60 '
            'against the Shadowhound\'s 139-159, 95 health against 130. That '
            'is correct against the tooltip and WRONG as a player experience, '
            'for the reason recorded in the section comment above - with no '
            'EXTRA_PET_CAP entry for Witch Hunter this level-20 ability '
            'replaces the level-1 permanent hound with the lesser one. The '
            'weaker numbers are kept rather than inflated to paper over it, '
            'because inflating them would hide the real bug behind a template '
            'that lies about what CoA says.'
        ),
        "abilities": [
            {
                "ability_id": "pet_lesser_shadowhound_bite",
                "name": "Lesser Bite",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "Half the size and twice as eager.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 28}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_lesser_shadowhound_pack_rush",
                "name": "Pack Rush",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It comes in low and fast because it has to.",
                "ranks": [
                    {"rank": 1, "level_req": 20, "cost": 30, "effect_value": 46}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },

    # ------------------------------------------------------------------
    # BARBARIAN
    "honored_ancestor": {
        "display_name": "Honored Ancestor",
        "pet_type": "barbarian",
        "base_hp": 185,
        "base_armor": 18,
        "base_magic_resist": 12,
        "base_attack": 24,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 10.0,
        "speed": 1.1,
        "level_req": 30,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: barbarian_ancestors_call pointed at "wolf" and '
            'summoned a pet named Wolf. CoA Barbarian Ancestry tree, '
            'Ancestor\'s Call - "Teaches you Ancestor\'s Call. Ancestor\'s Call '
            '(Troll) - Call an Honored Ancestor to aid you in battle until '
            'dismissed that scales with your Agility and attack power. '
            'Whenever you use Barbaric Whirl or Whirling Advance, your Honored '
            'Ancestor mimics it." A permanent spirit warrior: solid but not '
            'tanky, fast enough to keep up, high crit to match the Ancestry '
            'tree\'s own One With The Ancestors ("increases your critical '
            'strike chance by 2%"). TWO HALVES NOT AUTHORED, both engine '
            'limits rather than choices. (a) "Scales with your Agility and '
            'attack power": Pet._apply_template_stats reads exactly three '
            'owner talent keys - pet_damage, pet_health, pet_armor - and '
            'nothing else off the owner, deliberately (its own comment: '
            'inheriting the owner\'s whole bonus pool "would hand the pet the '
            'owner\'s gear stats too"). A pet that scales off an owner STAT '
            'rather than an owner TALENT has no mechanism at all. (b) The '
            'mimicry - the Ancestor copying Barbaric Whirl and Whirling '
            'Advance - would need a pet to react to its owner\'s casts, which '
            'nothing in the pet system does. Spirit Whirl is the flavour of '
            'that kept as a real ability the pet casts itself, which is '
            'honest about being an approximation rather than the mechanic. Per '
            'turn at 60: Ancestral Strike 150, Spirit Whirl 174.'
        ),
        "abilities": [
            {
                "ability_id": "pet_honored_ancestor_strike",
                "name": "Ancestral Strike",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "An old grip on an old weapon.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 32}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_honored_ancestor_spirit_whirl",
                "name": "Spirit Whirl",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "He turns once, the way he was taught.",
                "ranks": [
                    {"rank": 1, "level_req": 30, "cost": 30, "effect_value": 56}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },

    # ------------------------------------------------------------------
    # RANGER
    "war_falcon": {
        "display_name": "War Falcon",
        "pet_type": "ranger",
        "base_hp": 85,
        "base_armor": 5,
        "base_magic_resist": 5,
        "base_attack": 18,
        "base_spell_power": 0,
        "base_resource": 100,
        "resource_type": "energy",
        "crit_chance": 16.0,
        "speed": 1.5,
        "level_req": 16,
        "_source": SUMMON_THEME_SOURCE + (
            ' THIS TEMPLATE: ranger_summon_war_falcon pointed at "raptor" and '
            'summoned a pet named Raptor - the Primalist\'s tameable beast, on '
            'a Ranger. CoA Ranger tree, Falcon\'s Call - "Call down war falcons '
            'upon a targeted area, slowing up to 8 enemies within the area by '
            '-60% for 5 seconds. A Falcon is summoned for each enemy affected '
            'for 12 seconds." Supporting nodes confirm the shape: Falcon '
            'Charmer "increases the duration of War Falcons by 3 sec", '
            'Falcon\'s Aid "10% chance to summon a War Falcon", Falcon Diving '
            'summons one on a killing blow. So CoA\'s falcons are many, brief '
            'and disposable, and none of that is expressible - '
            'Character.EXTRA_PET_CAP has no Ranger entry, and pets here are '
            'permanent with no duration field. What IS authored is a single '
            'falcon built like one of that flock: lowest health in this entire '
            'batch, almost no armour, the joint-fastest turn speed of any pet, '
            'and the second-highest crit chance in the game. 115-133 per turn '
            'at 60 is deliberately under the Raptor it replaced (164) - a '
            'harass bird on a full-damage class, not a bruiser. The area slow '
            'belongs to the ability and the -60% would be a debuff, which a '
            'pet never casts (limit 1).'
        ),
        "abilities": [
            {
                "ability_id": "pet_war_falcon_talon_rake",
                "name": "Talon Rake",
                "resource_type": "energy",
                "cooldown": 0,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It is past you before you look up.",
                "ranks": [
                    {"rank": 1, "level_req": 1, "cost": 12, "effect_value": 26}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
            {
                "ability_id": "pet_war_falcon_diving_strike",
                "name": "Diving Strike",
                "resource_type": "energy",
                "cooldown": 3,
                "effect_type": "damage",
                "duration": 0,
                "stat_mods": {},
                "description": "It folds, drops, and opens at the last second.",
                "ranks": [
                    {"rank": 1, "level_req": 16, "cost": 30, "effect_value": 44}
                ],
                "is_instant": True,
                "icon_id": "ability_melee",
            },
        ],
    },
}


def get_pet_template(template_id):
    return PET_TEMPLATES.get(template_id)


def pets_for_class(pet_type, level):
    """Every pet template this pet_type can currently acquire at this
    level, in level order. Used by the summon/tame selection UI so it only
    ever offers real, reachable choices.

    In practice pet_type is only ever "hunter", "warlock" or "primalist"
    here, because ui/screens/pet_screen.py is the sole caller and those are
    the only three values its _pet_type_for_class maps a class to. Every
    other pet_type in PET_TEMPLATES belongs to a cast-summoned pet that
    never goes through a selection screen at all - see this module's
    docstring."""
    matches = [
        (tid, t) for tid, t in PET_TEMPLATES.items()
        if t["pet_type"] == pet_type and level >= t.get("level_req", 1)
    ]
    return sorted(matches, key=lambda pair: pair[1].get("level_req", 1))
