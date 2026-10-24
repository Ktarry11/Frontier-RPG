"""
Per-class school-to-tree mapping for the Spellbook screen's tab placement.

Real WoW convention (per Kyle): every combat spell belongs to its real
tree identity regardless of whether it's talent-gated - Frostbolt is a
Frost spell even though every Mage starts with it; Chain Lightning is
Elemental even though it's just a level-32 baseline unlock, not a talent
purchase. damage_school (built earlier this session) gives the real
school for most spells, but school alone isn't enough where multiple
trees in the same class touch the same school (Shaman: Elemental AND
Enhancement both have Nature-flavored kit) - that needs real per-class
knowledge this table encodes by hand.

Scope: classic 9 use the tables below; the implemented CoA classes use
data/spellbook_tabs_coa.json (generated from the CoA handoff's per-spec ability lists).

Structure: CLASS_SCHOOL_TREE_MAP[class_name][damage_school] -> tree_id.
A school not listed for a class means "no tree owns this school for this
class" - the ability falls back to whichever tree's unlock_ability
explicitly claims it (the requires_talent path), or Core if neither
applies.

PHYSICAL_TREE_OVERRIDES handles the handful of physical-school abilities
(bleeds, mostly) where a flat damage_school lookup can't disambiguate
which tree owns them, keyed directly by ability_id since these are
individually confirmed via real talent/description text (see comments on
each), not inferred from a school.
"""

CLASS_SCHOOL_TREE_MAP = {
    "Warrior": {
        # Warriors have no real elemental/spell-school split - all 3
        # trees are physical/utility flavored differently (Arms=two-hand/
        # bleeds, Fury=dual-wield/rage, Protection=shields/threat). No
        # school-based mapping applies; PHYSICAL_TREE_OVERRIDES handles
        # Rend specifically.
    },
    "Rogue": {
        # Same as Warrior - no school split, all physical. Rupture/
        # Hemorrhage handled via PHYSICAL_TREE_OVERRIDES.
    },
    "Hunter": {
        # Hunter's DoTs (Serpent Sting/Explosive Trap/Explosive Shot/
        # Black Arrow) are all Survival-flavored regardless of their
        # individual school (Nature/Fire/Shadow) - traps and sustained
        # damage-over-time are Survival's real identity, confirmed
        # directly for Explosive Shot/Black Arrow via their own
        # descriptions ("granted by the ... talent in the Survival
        # tree"). Serpent Sting/Explosive Trap are baseline but
        # thematically the same tree.
        "nature": "hunter_survival",
        "fire": "hunter_survival",
        "shadow": "hunter_survival",
    },
    "Mage": {
        # Clean 1:1 - Mage's three trees ARE their three schools.
        "fire": "mage_fire",
        "frost": "mage_frost",
        "arcane": "mage_arcane",
    },
    "Warlock": {
        # Deliberately EMPTY - Warlock's Shadow-schooled kit splits across
        # two real trees (Shadow Bolt/Shadowburn = Destruction's real
        # signature spell, confirmed via "Improved Shadow Bolt" living in
        # warlock_destruction's talent data; Curse of Agony/Drain Life =
        # Affliction's real DoT identity, confirmed via "Amplify Curse"
        # in warlock_affliction), so a flat school->tree map would put
        # them all in the wrong place for half of them. Handled instead
        # via WARLOCK_ABILITY_OVERRIDES below, same pattern as
        # PHYSICAL_TREE_OVERRIDES.
    },
    "Priest": {
        "holy": "priest_holy",
        "shadow": "priest_shadow",
    },
    "Druid": {
        # Nature -> Balance (Wrath is a core Balance nuke); Arcane ->
        # Balance too (Starfire is Balance's other real nuke, real WoW
        # Balance is Nature+Arcane split, not a whole separate tree).
        "nature": "druid_balance",
        "arcane": "druid_balance",
    },
    "Shaman": {
        # The real disambiguation case Kyle flagged: Elemental owns the
        # Nature/Fire direct-damage kit (Lightning Bolt, Earth Shock,
        # Chain Lightning, Lava Burst) - Enhancement's real kit is melee/
        # imbue-flavored with no direct-damage Nature spells of its own
        # in this class's current data, so Nature/Fire both map to
        # Elemental here, not split.
        "nature": "shaman_elemental",
        "fire": "shaman_elemental",
    },
    "Paladin": {
        # Judgement/Hammer of Wrath are both Holy and both real
        # Retribution-identity abilities (Ret's whole kit is Judgement-
        # centric) even though Paladin also has a dedicated Holy tree for
        # healing - Holy tree's real spells are heals (no damage_school
        # tag), so Holy-schooled DAMAGE abilities map to Retribution.
        "holy": "paladin_retribution",
    },
}

#: Ability-id-keyed overrides for physical-school abilities where a flat
#: school lookup can't disambiguate the owning tree (no class in
#: CLASS_SCHOOL_TREE_MAP maps "physical" to anything, since physical is
#: almost always genuinely tree-agnostic - these are the real, individually
#: confirmed exceptions).
PHYSICAL_TREE_OVERRIDES = {
    # Confirmed via real talent data: "Improved Rend" lives in Arms.
    "warrior_rend": "warrior_arms",
    # Confirmed via Hemorrhage's own ability description ("granted by the
    # Hemorrhage talent in the Subtlety tree").
    "rogue_hemorrhage": "rogue_subtlety",
    # NOT individually confirmed - Rupture is real WoW's classic Combo
    # Point finisher, available to any Rogue spec, no single tree
    # authentically owns it. Left unmapped deliberately (falls through to
    # Core/unassigned) rather than guessing a tree for it - flag this one
    # to Kyle directly if a specific placement is wanted.
}

#: Real per-ability overrides for Warlock's Shadow-schooled kit, which
#: splits across two trees despite sharing one school (see the empty
#: "Warlock" entry in CLASS_SCHOOL_TREE_MAP above for why a flat map
#: Real per-ability overrides for physical/utility abilities AND same-
#: school-different-tree cases (e.g. Warlock's Shadow Bolt vs Curse of
#: Agony), whose real WoW tree identity is well-established public
#: class-design knowledge, covering baseline (non-requires_talent)
#: abilities. requires_talent abilities don't need an entry here - their
#: real tree is already derived live from each character's own
#: talent_trees via unlock_ability (see skills_screen.py's _build_tabs).
CLASS_ABILITY_TREE_OVERRIDES = {
    # --- Warrior: Arms (bleeds/two-hand), Fury (dual-wield/rage),
    # Protection (shields/threat) ---
    "warrior_heroic_strike": "warrior_arms",
    "warrior_overpower": "warrior_arms",
    "warrior_thunder_clap": "warrior_arms",
    "warrior_demoralizing_shout": "warrior_fury",
    "warrior_bloodrage": "warrior_fury",
    "warrior_cleave": "warrior_fury",
    "warrior_whirlwind": "warrior_fury",
    "warrior_berserker_rage": "warrior_fury",
    "warrior_intercept": "warrior_fury",
    "warrior_recklessness": "warrior_fury",
    "warrior_sunder_armor": "warrior_protection",
    "warrior_disarm": "warrior_protection",
    "warrior_shield_wall": "warrior_protection",
    "warrior_charge": "warrior_protection",
    "warrior_intimidating_shout": "warrior_protection",
    "warrior_retaliation": "warrior_protection",
    "warrior_battle_shout": "warrior_fury",
    "warrior_execute": "warrior_fury",
    "warrior_pummel": "warrior_fury",
    # Battle Shout, Pummel, Rend: all-spec baseline, no single tree
    # authentically owns them - correctly fall through to Core.

    # --- Rogue: Assassination (poison/daggers), Combat (weapons/Energy),
    # Subtlety (stealth/burst) ---
    "rogue_sinister_strike": "rogue_combat",
    "rogue_slice_and_dice": "rogue_combat",
    "rogue_sprint": "rogue_combat",
    "rogue_backstab": "rogue_assassination",
    "rogue_eviscerate": "rogue_assassination",
    "rogue_expose_armor": "rogue_assassination",
    "rogue_kick": "rogue_subtlety",
    "rogue_gouge": "rogue_subtlety",
    "rogue_sap": "rogue_subtlety",
    "rogue_vanish": "rogue_subtlety",
    "rogue_feint": "rogue_subtlety",
    "rogue_rupture": "rogue_assassination",
    "rogue_garrote": "rogue_assassination",
    "rogue_deadly_poison": "rogue_assassination",
    "rogue_crippling_poison": "rogue_assassination",
    "rogue_envenom": "rogue_assassination",
    "rogue_shiv": "rogue_assassination",
    "rogue_ambush": "rogue_subtlety",
    "rogue_cheap_shot": "rogue_subtlety",
    "rogue_kidney_shot": "rogue_subtlety",
    "rogue_blind": "rogue_subtlety",
    "rogue_preparation": "rogue_subtlety",
    "rogue_blade_flurry": "rogue_combat",
    "rogue_killing_spree": "rogue_combat",
    "rogue_fan_of_knives": "rogue_combat",

    # --- Hunter: Beast Mastery (pet), Marksmanship (ranged precision),
    # Survival (traps/DoTs, already covered by CLASS_SCHOOL_TREE_MAP for
    # the schooled ones) ---
    "hunter_steady_shot": "hunter_marksmanship",
    "hunter_multi_shot": "hunter_marksmanship",
    "hunter_aimed_shot": "hunter_marksmanship",
    "hunter_hunters_mark": "hunter_marksmanship",
    "hunter_aspect_of_the_hawk": "hunter_beast_mastery",
    "hunter_aspect_of_the_wild": "hunter_beast_mastery",
    "hunter_mend_pet": "hunter_beast_mastery",
    "hunter_revive_pet": "hunter_beast_mastery",
    "hunter_concussive_shot": "hunter_survival",
    "hunter_disengage": "hunter_survival",
    "hunter_freezing_trap": "hunter_survival",
    "hunter_feign_death": "hunter_survival",
    "hunter_scare_beast": "hunter_survival",
    # Arcane Shot is Marksmanship's baseline instant; Tame Beast is the Beast Mastery pet unlock.
    "hunter_arcane_shot": "hunter_marksmanship",
    "hunter_tame_beast": "hunter_beast_mastery",

    # --- Warlock: Affliction (DoTs/curses), Demonology (pet/self-buff),
    # Destruction (direct Fire/Shadow burst) ---
    "warlock_shadow_bolt": "warlock_destruction",
    "warlock_shadowburn": "warlock_destruction",
    "warlock_curse_of_agony": "warlock_affliction",
    "warlock_drain_life": "warlock_affliction",
    "warlock_corruption": "warlock_affliction",
    "warlock_curse_of_weakness": "warlock_affliction",
    "warlock_curse_of_recklessness": "warlock_affliction",
    "warlock_fear": "warlock_affliction",
    "warlock_life_tap": "warlock_affliction",
    "warlock_banish": "warlock_affliction",
    "warlock_summon_imp": "warlock_demonology",
    "warlock_summon_voidwalker": "warlock_demonology",
    "warlock_summon_succubus": "warlock_demonology",
    "warlock_summon_felhunter": "warlock_demonology",
    "warlock_demon_armor": "warlock_demonology",
    "warlock_health_funnel": "warlock_demonology",
    "warlock_immolate": "warlock_destruction",
    "warlock_searing_pain": "warlock_destruction",
    # Warlock Attack has no school (a basic melee swing) - Core is correct.

    # --- Priest: Discipline (shields/mana), Holy (heals/party),
    # Shadow (already covered by CLASS_SCHOOL_TREE_MAP for the schooled
    # DoTs) ---
    "priest_power_word_shield": "priest_discipline",
    "priest_inner_fire": "priest_discipline",
    "priest_dispel_magic": "priest_discipline",
    "priest_abolish_disease": "priest_holy",
    "priest_heal": "priest_holy",
    "priest_renew": "priest_holy",
    "priest_power_word_fortitude": "priest_holy",
    "priest_prayer_of_healing": "priest_holy",
    "priest_shadow_word_pain": "priest_shadow",
    "priest_fade": "priest_shadow",
    "priest_psychic_scream": "priest_shadow",

    # --- Druid: Balance (caster nuke, already covered for schooled ones),
    # Feral (cat/bear physical), Restoration (heals) ---
    "druid_mangle": "druid_feral",
    "druid_claw": "druid_feral",
    "druid_shred": "druid_feral",
    "druid_ferocious_bite": "druid_feral",
    "druid_ravage": "druid_feral",
    "druid_swipe_cat": "druid_feral",
    "druid_maul": "druid_feral",
    "druid_bash": "druid_feral",
    "druid_enrage": "druid_feral",
    "druid_rake": "druid_feral",
    "druid_rejuvenation": "druid_restoration",
    "druid_healing_touch": "druid_restoration",
    "druid_regrowth": "druid_restoration",
    "druid_innervate": "druid_restoration",
    "druid_moonfire": "druid_balance",
    "druid_entangling_roots": "druid_balance",
    "druid_hibernate": "druid_balance",
    "druid_thorns": "druid_balance",
    "druid_mark_of_the_wild": "druid_restoration",
    "druid_barkskin": "druid_feral",
    "druid_bear_form": "druid_feral",
    "druid_cat_form": "druid_feral",
    "druid_dire_bear_form": "druid_feral",
    "druid_moonkin_form": "druid_balance",
    "druid_tree_of_life": "druid_restoration",
    # Mark of the Wild, Thorns, Barkskin: real all-spec party/self utility,
    # no single tree owns them - correctly Core.

    # --- Shaman: Elemental (already covered for schooled nukes),
    # Enhancement (melee/weapon imbues), Restoration (heals/water totems)
    # ---
    "shaman_flame_shock": "shaman_elemental",
    "shaman_lightning_shield": "shaman_elemental",
    "shaman_thunderstorm": "shaman_elemental",
    "shaman_searing_totem": "shaman_elemental",
    "shaman_magma_totem": "shaman_elemental",
    "shaman_fire_resistance_totem": "shaman_elemental",
    "shaman_frost_shock": "shaman_enhancement",
    "shaman_stormstrike": "shaman_enhancement",
    "shaman_rockbiter_weapon": "shaman_enhancement",
    "shaman_flametongue_weapon": "shaman_enhancement",
    "shaman_frostbrand_weapon": "shaman_enhancement",
    "shaman_windfury_weapon": "shaman_enhancement",
    "shaman_windfury_totem": "shaman_enhancement",
    "shaman_shamanistic_rage": "shaman_enhancement",
    "shaman_feral_spirit": "shaman_enhancement",
    "shaman_stoneclaw_totem": "shaman_enhancement",
    "shaman_earthbind_totem": "shaman_enhancement",
    "shaman_strength_of_earth_totem": "shaman_enhancement",
    "shaman_stoneskin_totem": "shaman_enhancement",
    "shaman_hex": "shaman_enhancement",
    "shaman_purge": "shaman_elemental",
    "shaman_grounding_totem": "shaman_elemental",
    "shaman_healing_wave": "shaman_restoration",
    "shaman_water_shield": "shaman_restoration",
    "shaman_mana_spring_totem": "shaman_restoration",
    "shaman_earth_shield": "shaman_restoration",
    "shaman_riptide": "shaman_restoration",
    "shaman_mana_tide_totem": "shaman_restoration",
    "shaman_nature_resistance_totem": "shaman_restoration",
    "shaman_frost_resistance_totem": "shaman_restoration",
    "shaman_reincarnation": "shaman_restoration",
    # Strength of Earth/Stoneskin/Grounding Totem, Hex, Reincarnation:
    # real all-spec utility, no single tree owns them - correctly Core.

    # --- Paladin: Holy (heals), Protection (tank/shields),
    # Retribution (Judgement/melee) ---
    "paladin_holy_light": "paladin_holy",
    "paladin_flash_of_light": "paladin_holy",
    "paladin_blessing_of_wisdom": "paladin_holy",
    "paladin_lay_on_hands": "paladin_holy",
    "paladin_redemption": "paladin_holy",
    "paladin_divine_shield": "paladin_protection",
    "paladin_hammer_of_justice": "paladin_protection",
    "paladin_consecration": "paladin_protection",
    "paladin_cleanse": "paladin_holy",
    "paladin_crusader_strike": "paladin_retribution",
    "paladin_blessing_of_might": "paladin_retribution",
    "paladin_blessing_of_kings": "paladin_retribution",
    "paladin_exorcism": "paladin_retribution",
    "paladin_turn_evil": "paladin_retribution",
    "paladin_seal_of_righteousness": "paladin_retribution",
}


_COA_TABS = None


def _coa_tabs():
    """Lazy-load {class: {ability_id: tree_id|"core"}} for the CoA classes."""
    global _COA_TABS
    if _COA_TABS is None:
        import json, os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", "spellbook_tabs_coa.json")
        try:
            with open(path, encoding="utf-8") as fh:
                _COA_TABS = json.load(fh)
        except (OSError, ValueError):
            _COA_TABS = {}
    return _COA_TABS


def get_owning_tree(char_class, ability):
    """Real tree_id this ability belongs to for spellbook tab placement,
    or None if it belongs in Core (no tree owns it - a genuine passive/
    profession/racial, or a physical ability with no confirmed tree
    owner like Rupture).

    Resolution order, all using REAL data already on the ability/talent
    trees, never guessed:
      1. requires_talent abilities: use whichever tree's unlock_ability
         actually claims this ability_id (the real, authoritative link -
         checked by the caller via each TalentTree's node data, not here,
         since that needs the character's live talent_trees dict).
      2. PHYSICAL_TREE_OVERRIDES, for the individually-confirmed physical
         exceptions.
      3. CLASS_SCHOOL_TREE_MAP[char_class][damage_school], for baseline
         schooled spells (Frostbolt, Chain Lightning, ...).
      4. Mage-only: a school-LESS spell effect (buffs like Arcane
         Intellect/Mage Armor, crowd control like Polymorph/Counterspell)
         defaults to Arcane - real WoW convention (open-sourced client
         data confirms this: Arcane is historically the "no specific
         school" bucket for utility magic), and Mage is the only classic-9
         class with an actual Arcane-named tree for this to land in.
      5. None (Core) - no owning tree, matches Kyle's "professions/
         racials/general passives" definition of Core. This is the
         correct real fallback for every OTHER class's school-less
         utility spells (a Warrior's Shield Block, a Rogue's Stealth,
         ...) - they have no natural elemental-school home the way a
         caster's utility spells do, so Core is the honest answer, not
         a forced guess at a tree.

    This function only implements steps 2-4 (the parts that don't need
    live character talent state) - step 1 is real per-character data the
    caller (skills_screen.py) already has to walk anyway to build its
    unlock_ability reverse index, so it isn't duplicated here.
    """
    # CoA classes: spec placement comes from data/spellbook_tabs_coa.json (built from the CoA handoff's
    # per-spec ability lists by tools/build_coa_spellbook_tabs.py).  "core" = class kit / no single spec.
    coa = _coa_tabs().get(char_class)
    if coa is not None and ability.ability_id in coa:
        tab = coa[ability.ability_id]
        return None if tab == "core" else tab

    override = PHYSICAL_TREE_OVERRIDES.get(ability.ability_id)
    if override:
        return override

    class_override = CLASS_ABILITY_TREE_OVERRIDES.get(ability.ability_id)
    if class_override:
        return class_override

    school = getattr(ability, "damage_school", None)
    if isinstance(school, str):
        class_map = CLASS_SCHOOL_TREE_MAP.get(char_class, {})
        return class_map.get(school)

    # Mage-only Arcane fallback for school-less spell EFFECTS (not
    # physical abilities - a Mage's basic Attack has no school either,
    # but it's a weapon swing, not a spell, so it belongs in Core like
    # any other class's physical ability, not forced into Arcane).
    if char_class == "Mage" and school is None:
        real_spell_effect_types = ("buff", "debuff", "damage", "spell_damage",
                                    "dot", "spell_dot", "heal", "hot",
                                    "damage_and_heal", "damage_and_restore_mana")
        if getattr(ability, "effect_type", None) in real_spell_effect_types \
                and ability.ability_id != "mage_attack":
            return "mage_arcane"

    return None
