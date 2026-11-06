"""
Character class with full stat system, abilities, resources, leveling, and prestige.
"""
from combat.abilities import get_class_abilities
from entities.equipment import Equipment, BASE_INVENTORY_CAPACITY


from combat.status_effects import StatusEffectMixin, DamageSchool


#: Target names accepted by the <target>_from_<source>_pct stat-conversion
#: keys, mapped to the Character attribute each one adds to. Read by
#: _recalculate_derived_stats, and imported by tools/audit_talents.py so the
#: dead-key check knows which of these dynamically-named keys are real.
#: Module-level, and shared, specifically so the audit cannot drift from the
#: engine - a second hand-maintained copy of this list is how a key ends up
#: "live" in the audit and dead at runtime.
STAT_CONVERSION_TARGETS = {
    "attack_power": "attack_power", "ap": "attack_power",
    "ranged_ap": "ranged_attack_power",
    "spell_power": "spell_power", "spell_damage": "spell_power",
    "healing_power": "healing_power",
    # block_value/block both target block_value, NOT "block". There was no
    # attribute named "block" after block was split into block_chance (a %,
    # shield-gated) and block_value (flat absorbed) on 2026-10-28, so these
    # two targets wrote a phantom attribute that nothing read and
    # Sun Cleric Seraphim's Clarity of the Heavens ("+3%/rank block value
    # from Intellect", 5 ranks) silently did nothing. A conversion target
    # has to name a real attribute: getattr returns 0 for a missing one and
    # setattr happily invents it, so the whole pairing fails silently.
    "armor": "armor", "block_value": "block_value", "block": "block_value",
    "parry": "parry", "dodge": "dodge", "haste": "haste",
    "crit_chance": "crit_chance_physical", "crit": "crit_chance_physical",
    "crit_chance_spell": "crit_chance_spell",
}

#: Source names accepted by those same keys. Values are computed per
#: character in _recalculate_derived_stats; only the NAMES matter here.
STAT_CONVERSION_SOURCES = frozenset({
    "strength", "agility", "intellect", "spirit", "stamina",
    "ap", "attack_power", "spell_power", "weapon", "str_int",
})


def _main_hand_average_damage(equipment):
    """Average damage of the equipped main hand, or 0 while unarmed.

    The "weapon" stat-conversion source. Deliberately the AVERAGE rather
    than a roll: a conversion feeds a persistent derived stat recomputed on
    every equip and talent change, so rolling here would make healing power
    jitter between recalculations.
    """
    try:
        weapon = equipment.get_main_hand_weapon()
    except Exception:
        return 0
    if not weapon:
        return 0
    low = getattr(weapon, "weapon_damage_min", 0) or 0
    high = getattr(weapon, "weapon_damage_max", 0) or 0
    return (low + high) / 2.0


class Character(StatusEffectMixin):
    """Complete character with stats, abilities, and resources."""
    
    def __init__(self, name, char_class, level=1):
        self._init_status_effects()
        self.name = name
        self.char_class = char_class  # "Warrior", "Shaman", "Rogue", "Priest"
        self.level = level
        self.experience = 0
        self.prestige_level = 0
        self.prestige_points = 0

        # Cosmetic appearance only - see world/race_registry.py for how
        # these three resolve to an actual sprite folder. Purely visual:
        # no stat, ability, or resource effect anywhere in the game reads
        # these fields (unlike char_class). Defaults to a real, valid
        # combination (human male, first variant) so a Character created
        # anywhere in the codebase without explicitly setting these still
        # resolves to a real sprite rather than None.
        self.race = "human"
        self.gender = "male"
        self.appearance_variant = 0
        
        # Core Stats (5) - these are BASE stats only (no gear applied).
        # Equipment bonuses are layered on top in _recalculate_derived_stats()
        # and exposed separately so equip/unequip never has to touch these.
        self.strength = 0
        self.stamina = 0
        self.intellect = 0
        self.spirit = 0
        self.agility = 0

        # Effective stats (base + equipped gear bonuses). Populated by
        # _recalculate_derived_stats(); this is what UI should display.
        self.effective_strength = 0
        self.effective_stamina = 0
        self.effective_intellect = 0
        self.effective_spirit = 0
        self.effective_agility = 0
        
        # Derived Stats (10)
        self.attack_power = 0
        self.ranged_attack_power = 0
        self.spell_power = 0
        self.healing_power = 0
        self.crit_chance_physical = 0.0
        self.crit_chance_spell = 0.0
        self.dodge = 0.0
        # BLOCK IS TWO STATS, not one. block_chance is the percentage of physical hits stopped;
        # block_value is how much damage a stopped hit loses. They were a single `block` field
        # computed as a VALUE - Strength times 0.3 plus the shield's block_value, scaled by
        # block_value_pct - and then used as a CHANCE, compared against a 0-100 roll in
        # take_damage. A Sun Cleric Seraphim read 285, so it blocked every physical hit in the
        # game, and the value it had accumulated was then thrown away in favour of a flat 30%
        # reduction. Kyle, 2026-10-28: "we need block % AND block rating. parry and dodge is 100%
        # mitigation, block is a value."
        self.block_chance = 0.0
        self.block_value = 0.0
        self.parry = 0.0
        self.haste = 0.0

        # New real gear-suffix stats (Kyle's Gear.docx suffix system,
        # this session) that had no home on Character before now -
        # mp5 (mana per 5 sec, see combat/status_effects.py's
        # tick_out_of_combat_regen), spell_penetration (reduces a
        # target's effective resistance - see combat resolution),
        # and per-school spell power (on top of the existing generic
        # spell_power, for suffixes like "of Fiery Wrath").
        self.mp5 = 0
        self.spell_penetration = 0
        self.fire_spell_power = 0
        self.frost_spell_power = 0
        self.arcane_spell_power = 0
        self.shadow_spell_power = 0
        self.nature_spell_power = 0
        self.holy_spell_power = 0

        # Hit chance (Phase 5c): base miss chance that Hit Rating (a gear
        # secondary stat, same family as Crit/Haste) reduces. Attacks that
        # fail this roll deal 0 damage and log as a miss.
        self.base_miss_chance_physical = 8.0   # WoW-classic-style baseline vs a same-level target
        self.base_miss_chance_spell = 6.0       # Spells miss slightly less often than melee by convention
        self.hit_chance_physical = 100.0 - self.base_miss_chance_physical
        self.hit_chance_spell = 100.0 - self.base_miss_chance_spell
        
        # Defense Stats
        self.health = 0
        self.mana = 0
        self.armor = 0
        # MAGIC RESISTANCE IS DELIBERATELY ZERO UNTIL LEVEL 45 CONTENT EXISTS. It is not in
        # data/items/stat_templates.json's secondary_stat_pool, so no gear can roll it and every
        # class sits at 0% against spell damage for the whole game - which is why caster creatures
        # still do roughly twice what melee creatures do even after the armour curve was fixed.
        #
        # Kyle, 2026-10-28: "we can slowly start adding magic resistance gear after lvl 45." So the
        # gap is known and intended for now. When it is time, the lever is adding
        # "magic_resistance" to that secondary pool and gating it to item levels 45 and up - the
        # mitigation curve it feeds through (mitigation_from, below) already scales with attacker
        # level and needs no change, and Monster already carries base_magic_resist, so the
        # creature side is done. Nothing before 45, and phased in rather than switched on.
        self.magic_resistance = 0

        # Per-school resistances (real WotLK-style: Fire/Frost/Nature/
        # Shadow/Arcane/Holy, each independent from Armor and from each
        # other, mitigated through the same asymptotic mitigation_from()
        # curve Armor already uses - see get_resistance() below for the
        # single real lookup point, and DamageSchool in
        # combat/status_effects.py for the school constants). Separate
        # from magic_resistance (the old flat "all non-physical" stat,
        # kept only as a legacy fallback for abilities not yet migrated
        # to a real school - see DamageSchool.MAGIC's docstring). Default
        # 0 here, real values computed in _recalculate_derived_stats from
        # Spirit + gear/talent bonuses, same pattern as magic_resistance.
        self.fire_resistance = 0
        self.frost_resistance = 0
        self.nature_resistance = 0
        self.shadow_resistance = 0
        self.arcane_resistance = 0
        self.holy_resistance = 0

        # Resources
        self.max_rage = 100
        self.max_energy = 100
        
        # Current State
        self.current_health = 0
        self.current_mana = 0
        self.current_rage = 0
        self.current_energy = 100

        # One-shot flag set by Nature's Swiftness-style effects (see
        # Ability's "enable_instant_cast" effect_type): True means the
        # NEXT ability this character casts is treated as instant by
        # CombatEngine.execute_ability, regardless of that ability's own
        # is_instant flag, and is cleared the moment it's consumed. Not
        # persisted across combat (there's no real-world reason a buff
        # like this should survive a fight it wasn't used in).
        self.next_cast_instant = False

        # Warrior stance (see combat/stances.py). None for every other
        # class - stances are Warrior-specific in real WOTLK, and nothing
        # here assumes every character has one. Battle Stance is the
        # default the moment a Warrior can act, matching real WOTLK where
        # it's the stance you start in.
        self.current_stance = "battle" if char_class == "Warrior" else None

        # Persistent shapeshift form (see combat/forms.py) - Druid Bear/
        # Cat/Dire Bear/Moonkin/Tree of Life, Priest Shadowform. None means
        # "base Humanoid form" (Mana). Unlike current_stance, this is
        # PERSISTENT per Kyle's direction - nothing resets it between
        # fights or on zone transitions, it only changes via shift_form().
        self.current_form = None

        # Real Tinker Mechsuit state - see StatusEffectMixin.current_mechsuit
        # (a derived property, not a plain attribute - there's no
        # self.current_mechsuit assignment here on purpose, see that
        # property's docstring for why).

        # Scrap (Tinker's Makeshift Dynamite "Generates 10 Scrap" -
        # confirmed via real screenshot; a secondary spend-to-transform
        # currency gating entry into Mechsuit form, not a pool that fuels
        # every ability) does NOT get a dedicated attribute pair here. It
        # is a dict-backed secondary resource like Insanity, Static and
        # Deathfire, handled generically by _RESOURCE_ATTRS' fallthrough -
        # get_resource("scrap"), gain_resource and spend_resource all work
        # on it today, and SECONDARY_RESOURCE_MAX gives it the same 0-100
        # ceiling the old max_scrap hardcoded.
        #
        # There used to be a self.current_scrap/self.max_scrap pair right
        # here, read by NOTHING. Worse than dead: it silently diverged from
        # the pool that actually works - after gaining 30 and spending 10,
        # the dict read 20 while current_scrap still read 0 - so anyone
        # reading this file would reasonably wire new code to the wrong
        # one. Removed rather than kept in sync.
        #
        # Known gap, tracked separately: nothing in the game COSTS scrap,
        # so the pool fills and cannot be spent. The sink belongs on
        # Mechsuit form per the screenshot above.

        # Earthen Guardian toggle (Shaman Tank, see combat/guardian_stance.py).
        # PERSISTENT like current_form, not per-fight like current_stance -
        # a Shaman turns it on and stays a tank across multiple fights until
        # explicitly toggling off. False for every class by default; only
        # ever set True via toggle_guardian_stance() and only meaningful for
        # Shaman (mirrors current_form's "None for classes that don't use
        # it" pattern rather than restricting the attribute's existence).
        self.guardian_stance_active = False

        # The one active pet (Hunter tame / Warlock summon - see
        # entities/pet.py), or None. Only one pet can be active at a time
        # for either class, matching real WoW - summoning/taming a new one
        # replaces this reference rather than adding to a list.
        self.active_pet = None
        #: ADDITIONAL simultaneous pets, beyond active_pet. CoA is explicit
        #: that two specs field several at once: Tinker Mechanics runs "your
        #: permanent Scrapmaw, PLUS proc'd Clockwork Guardians", and
        #: "Clockwork Guardians AND the Sentry Turret add a Guldan-style
        #: board of extra summoned pressure"; Necromancer Animation's whole
        #: answer to having no hard CC is "several bodies soaking and dealing
        #: damage AT ONCE". With one slot, Tinker's five summons and
        #: Necromancer's four could only ever replace each other.
        #:
        #: Kept as a SEPARATE list rather than turning active_pet into one,
        #: so every existing reader - the combat engine, the pet screen, the
        #: overworld party row, saves - keeps working unchanged against the
        #: primary pet. Warlock and Hunter deliberately stay single-pet,
        #: which is correct for both: a Warlock's four demons are
        #: alternatives, not a board.
        self.extra_pets = []

        # Shaman totem loadout: element -> ability_id, up to 4 entries (one
        # per real WoW element: earth/fire/water/air). Player-configured
        # via the totem selection screen, then cast as a single action by
        # Call of the Elements/Ancestors/Spirits (see the totem_loadout
        # effect_type in combat/abilities.py). Empty dict for every
        # non-Shaman - nothing else reads this for other classes.
        self.totem_loadout = {}

        # Secondary / CoA class resources (Static, Insanity, Deathfire, ...).
        # Rage/Energy/Mana/Health have dedicated attributes for historical
        # reasons; everything else lives in this dict so adding a new CoA
        # resource never requires new Character attributes. Keyed by
        # ResourceType.value (a plain string) so it serializes directly.
        self.secondary_resources = {}
        self.status_effects = []
        
        # Equipment (Phase 5) - 16 gear slots + 4 bag slots (bags added per
        # Kyle's "WoW style with limited space" spec), stat bonuses summed
        # at recalc time. See inventory_capacity / add_to_inventory below
        # for how bag slots cap the backpack.
        self.equipment = Equipment()
        self.inventory = []  # List[Item] - unequipped items the player is carrying
        self.auto_sell_junk = False  # global: vendors auto-sell vendor trash when opened (Kyle's 'lazy' tick-box)
        
        # Consumables (Phase 6) - separate inventory from gear
        self.consumables = []  # List[Consumable] - potions, elixirs, food
        self.consumable_cooldown = 0.0  # Shared potion cooldown (WoW-style)

        # Gathering materials (Phase: Gathering/Crafting Phase 1) - separate
        # from both gear and consumables, same reasoning that split
        # Consumable off from Item: a raw material has no use() effect,
        # it's inert until a future crafting system consumes it. Stacks
        # by material_id via add_material(), same shape as add_consumable.
        self.materials = []  # List[Material] - ore, herbs, (future) wood/hides/essence

        # Gathering profession skill levels. Flat dict rather than one
        # attribute per profession so adding Woodcutting/Skinning/Essence
        # Harvesting later never touches this __init__ again - just a new
        # key. 0 means "not learned" (Kyle hasn't decided yet whether
        # professions are auto-known or must be learned from a trainer,
        # so this defaults to a state that works either way: a character
        # with 0 skill just can't gather anything above tier-0 nodes once
        # node skill-gating is wired).
        self.profession_skills = {
            "herbalism": 0,
            "mining": 0,
            "woodcutting": 0,
            "skinning": 0,
        }
        # Profession learning (Oct 2026): a profession must be learned from a profession trainer (3 primary slots).
        # Gathering without it still picks things up but never skills up; crafting needs it. profession_tiers maps a
        # profession to its trained tier (0 Apprentice, 1 Journeyman, ...), which sets the skill cap.
        self.known_professions = []
        self.profession_tiers = {}
        # Recipe discovery (Oct 2026): recipes must be explicitly learned — either taught by a trainer, found as
        # world drops, bought from a vendor, or rewarded from a quest. A recipe item in the inventory has a
        # recipe_id field; right-clicking it calls learn_recipe() which checks skill_required and adds the id here.
        # available_recipes() in every crafting manager filters against this set rather than auto-granting all
        # recipes at the current skill tier — players must actively discover and learn each one.
        self.known_recipes: set = set()
        
        # Buff slots (Phase 6) - 1 guardian, 1 battle, 1 food buff active at a time
        self.guardian_buff = None  # (consumable, remaining_duration)
        self.battle_buff = None    # (consumable, remaining_duration)
        self.food_buff = None      # (consumable, remaining_duration)
        self.ammo_buff = None      # (consumable, remaining_duration) - crafted arrows/bolts (Woodworking)
        
        # Currency moved to Party.copper (shared party purse) - see the
        # CURRENCY comment further down in this class for why.
        
        # Abilities
        self.ability_book = get_class_abilities(char_class)
        self.hotbar = [None] * 20  # 20 hotbar slots (2 rows of 10) - player fills these with abilities or consumables (Phase 6)
        # Every ability_id _autofill_hotbar has EVER placed on the bar,
        # regardless of whether it's still there now. Autofill checks
        # this instead of "is it currently slotted" - otherwise removing
        # an unwanted ability (Shoot/Wand with no matching weapon, say)
        # only lasted until the next level-up, since _refresh_ability_ranks
        # (called on every level-up) re-ran autofill, saw the slot was
        # empty and the ability wasn't CURRENTLY on the bar, and put it
        # right back (Kyle: "if I remove shoot and wand, level up, and
        # it's forced back into my skill bar"). Once an ability has been
        # auto-placed once, it's the player's call forever after whether
        # it stays on the bar.
        self.hotbar_autofilled_ids = set()
        self.extra_slots = [None] * 8  # Click-only ability slots beyond the 20 keybound ones -
        # no number-key binding (there's no key left to bind - 1-9,0 and
        # Shift+1-9,0 are already spoken for), just mouse-click. Lives in
        # the dead space next to the stance buttons on the combat screen.
        # Kept as a separate list rather than extending hotbar to 28 so
        # existing keybind math (_key_to_hotbar_slot, slot_ability's 0-19
        # bound) never has to think about "which slots have no key".
        # Class training (Oct 2026).  Only the PLAYER's character is trained at a class trainer (character creation turns
        # training_enabled on); companions, enemies and previews keep ability learning purely level-based.
        #   trained_ranks - ability_id -> highest rank number bought (or granted free, see FREE_TRAINING_LEVEL)
        self.training_enabled = False
        self.trained_ranks = {}
        self._refresh_ability_ranks()  # unlock whatever ranks self.level already qualifies for
        
        # Talent Trees (Phase 4.5) - will be populated by character creation screen
        self.talent_trees = {}  # tree_id -> TalentTree (loaded from talent_manager)
        self.talent_points_available = 0  # Points to spend (1 per level starting at level 5)
        
        # Combat
        self.turn_meter = 0.0
        self.turn_speed = 1.0

        # Party identity. These were previously never declared here - they
        # were bolted on ad-hoc by RecruitManager and read everywhere through
        # getattr() fallbacks, which meant they also never serialized. A
        # companion reloaded from a save came back spec-UNLOCKED and in the
        # front row regardless of what they were recruited as.
        #   row         - "front"/"back"; set properly when joining a Party
        #   locked_spec - tree_id a companion may spend talent points in;
        #                 None for the player, who keeps all three trees
        #   recruit_id  - links back to the RecruitNPC definition
        self.row = None
        self.locked_spec = None
        self.recruit_id = None
        self.backstory = ""

        # Real 4-part background (Before / Adjustment / Now / Looking
        # Forward - per Kyle's ask for fleshed-out companion lore). Keys
        # are fixed: "before", "adjustment", "now", "forward". Separate
        # from self.backstory (kept as-is, unchanged, for save/recruit-
        # manager compatibility - see BACKGROUND_SECTION_KEYS' docstring
        # for the real migration rule: "now" falls back to self.backstory
        # when not explicitly set, so every existing companion's current
        # single-paragraph backstory keeps showing up exactly where it
        # already does, just under the "Now" tab, with zero content
        # rewriting required for this to work day one). Empty string for
        # a key not yet written means "not written yet" - the UI shows a
        # real "Not yet written" placeholder rather than blank space, so
        # it doesn't look broken/missing.
        self.background_sections = {}

        # Initialize
        self._initialize_class_stats()
    
    def _initialize_class_stats(self):
        """Set base stats based on class."""
        class_stats = {
            "Warrior": {
                "strength": 15, "stamina": 14, "intellect": 8, "spirit": 8, "agility": 10
            },
            "Shaman": {
                "strength": 10, "stamina": 12, "intellect": 16, "spirit": 14, "agility": 10
            },
            "Rogue": {
                "strength": 12, "stamina": 10, "intellect": 10, "spirit": 8, "agility": 18
            },
            "Priest": {
                "strength": 8, "stamina": 11, "intellect": 16, "spirit": 16, "agility": 10
            },
            "Hunter": {
                "strength": 10, "stamina": 12, "intellect": 12, "spirit": 10, "agility": 17
            },
            "Mage": {
                "strength": 7, "stamina": 10, "intellect": 18, "spirit": 13, "agility": 9
            },
            "Warlock": {
                "strength": 7, "stamina": 11, "intellect": 17, "spirit": 14, "agility": 9
            },
            "Druid": {
                "strength": 10, "stamina": 11, "intellect": 14, "spirit": 13, "agility": 12
            },
            "Paladin": {
                "strength": 14, "stamina": 13, "intellect": 13, "spirit": 11, "agility": 9
            },

            # ================================================================
            # 21 CoA classes (resources/armor sourced - see
            # COA_21_CLASS_RESOURCE_REFERENCE.md; stat spreads below are
            # reasonable estimates following the same design logic as the
            # original 9 - armor type informs Stamina lean, confirmed
            # primary stat(s) get the highest allocation.
            #
            # All 21 are now fully playable: abilities with ranks across
            # levels 1-60, one talent tree per CoA spec, spellbook tabs,
            # starting gear and a character-creation entry. The primary
            # stat named in each comment below is the one the class's CoA
            # page states, and the talent trees convert from it - so a
            # comment reading "Agility" is load-bearing, not decoration.
            # tools/audit_class_completeness.py checks all of that.
            # ================================================================
            "Necromancer": {  # Cloth, Intellect, Life Force
                "strength": 7, "stamina": 10, "intellect": 18, "spirit": 12, "agility": 9
            },
            "Pyromancer": {  # Cloth, Intellect, Mana
                "strength": 7, "stamina": 10, "intellect": 18, "spirit": 12, "agility": 9
            },
            "Cultist": {  # Cloth/Plate hybrid, Str/Int hybrid, Mana+Insanity
                "strength": 12, "stamina": 13, "intellect": 15, "spirit": 9, "agility": 9
            },
            "Starcaller": {  # Leather, Agility (confirmed via handoff doc + screenshots), Mana+Energy
                "strength": 8, "stamina": 12, "intellect": 12, "spirit": 9, "agility": 17
            },
            "Sun Cleric": {  # Plate, hybrid Int(Piety/Blessings/Seraphim)/Str(Valkyrie), Mana+Solar Power
                "strength": 13, "stamina": 13, "intellect": 15, "spirit": 11, "agility": 8
            },
            "Tinker": {  # Mail, Agi/Int hybrid, Rounds
                "strength": 8, "stamina": 12, "intellect": 14, "spirit": 9, "agility": 15
            },
            "Runemaster": {  # Cloth, hybrid Int(Glyphic)/Agi(Engravement/Riftblade), Mana+Runes
                "strength": 8, "stamina": 11, "intellect": 15, "spirit": 10, "agility": 13
            },
            "Primalist": {  # Mail, Strength (melee) / Intellect (Geomancy) hybrid
                "strength": 13, "stamina": 13, "intellect": 13, "spirit": 11, "agility": 10
            },
            "Reaper": {  # Mail, Agility/Stamina lead, Mana+Souls
                "strength": 10, "stamina": 13, "intellect": 10, "spirit": 9, "agility": 16
            },
            "Venomancer": {  # Mail, Intellect/Stamina, Mana or Rage (spec-dependent)
                "strength": 9, "stamina": 14, "intellect": 15, "spirit": 10, "agility": 10
            },
            "Chronomancer": {  # Cloth, Intellect, Mana
                "strength": 7, "stamina": 10, "intellect": 18, "spirit": 12, "agility": 9
            },
            "Bloodmage": {  # Leather, Agility, Rage+Vitality
                "strength": 10, "stamina": 12, "intellect": 11, "spirit": 9, "agility": 16
            },
            "Guardian": {  # Plate, Strength, Energy
                "strength": 16, "stamina": 15, "intellect": 8, "spirit": 8, "agility": 9
            },
            "Stormbringer": {  # Cloth, Intellect, Static
                "strength": 7, "stamina": 10, "intellect": 18, "spirit": 12, "agility": 9
            },
            "Felsworn": {  # Leather, Agi/Int hybrid, Felfury+Demon Form
                "strength": 9, "stamina": 12, "intellect": 13, "spirit": 9, "agility": 15
            },
            "Barbarian": {  # Leather, Agility/Strength, Energy
                "strength": 14, "stamina": 12, "intellect": 8, "spirit": 8, "agility": 15
            },
            "Witch Doctor": {  # Leather, Intellect/Agility, Mana
                "strength": 8, "stamina": 11, "intellect": 15, "spirit": 11, "agility": 13
            },
            "Witch Hunter": {  # Mail, Agility, Focus
                "strength": 9, "stamina": 12, "intellect": 9, "spirit": 8, "agility": 17
            },
            "Knight of Xoroth": {  # Plate, Str/Int hybrid, Rage+Deathfire
                "strength": 15, "stamina": 14, "intellect": 12, "spirit": 8, "agility": 9
            },
            "Templar": {  # Leather, Agility, Combo chain
                "strength": 10, "stamina": 11, "intellect": 8, "spirit": 8, "agility": 18
            },
            "Ranger": {  # Leather, Agility, Archery Points
                "strength": 9, "stamina": 11, "intellect": 9, "spirit": 9, "agility": 18
            },
        }
        
        stats = class_stats.get(self.char_class, {})
        self.strength = stats.get("strength", 10)
        self.stamina = stats.get("stamina", 10)
        self.intellect = stats.get("intellect", 10)
        self.spirit = stats.get("spirit", 10)
        self.agility = stats.get("agility", 10)

        # Snapshot the level-1 class stats. _apply_level_scaling() recomputes
        # from THIS every time rather than adding onto whatever the stats
        # currently are, so it can safely be re-run on every level-up (and on
        # prestige, and after a save load) without compounding.
        self.class_base_stats = {
            "strength": self.strength,
            "stamina": self.stamina,
            "intellect": self.intellect,
            "spirit": self.spirit,
            "agility": self.agility,
        }

        self._apply_level_scaling()
        self._recalculate_derived_stats()
        self._load_talent_trees()
    
    def _load_talent_trees(self):
        """Load talent trees for this character's class from talent manager."""
        from entities.talent_manager import get_talent_manager
        from copy import deepcopy
        
        talent_manager = get_talent_manager()
        class_trees = talent_manager.get_trees_for_class(self.char_class)
        
        # Make deep copies so each character has their own talent tree state
        for tree_id, tree in class_trees.items():
            import json
            tree_dict = tree.to_dict()
            from entities.talent_tree import TalentTree
            copied_tree = TalentTree.from_dict(tree_dict)
            self.talent_trees[tree_id] = copied_tree
        
        # Single source of truth for point totals (see _grant_talent_points).
        self._grant_talent_points()
        # The trees now exist, so re-run the talent gate: abilities were first marked learned in __init__ before any
        # tree was loaded, which left every talent-granted spell known from its level (Golem Form at 8) without the talent.
        if hasattr(self, "ability_book"):
            self._refresh_ability_ranks()
    
    def apply_status_effect(self, effect):
        """Apply an effect, then recalculate derived stats so any stat_mods
        the effect carries take hold immediately rather than next level-up."""
        msg = super().apply_status_effect(effect)
        self._recalculate_derived_stats()
        return msg

    def tick_status_effects(self):
        """Tick effects, then recalculate - an expiring buff must actually
        remove its bonus, otherwise buffs would be permanent once applied."""
        messages = super().tick_status_effects()
        self._recalculate_derived_stats()
        return messages

    def clear_status_effects(self):
        super().clear_status_effects()
        self._recalculate_derived_stats()

    # ------------------------------------------------------------------
    # TALENT EFFECT AGGREGATION (Phase 4.5b)
    # ------------------------------------------------------------------
    # Talents used to spend points and do literally nothing in combat - the
    # engine tracked ranks and the JSON declared effects, but no consumer
    # ever read them. These three methods are the bridge: every talent
    # effect key from every tree this character owns is summed once and
    # cached, then read by _recalculate_derived_stats() (for stat keys) and
    # by combat/abilities.py (for per-ability damage/cost/cooldown keys).
    #
    # Effect key conventions:
    #   Stat keys        - match derived stat attribute names exactly
    #                      (crit_chance_physical, parry, dodge, block, haste,
    #                      attack_power, spell_power, healing_power, armor,
    #                      strength/stamina/intellect/spirit/agility, and the
    #                      percentage keys max_health_pct / max_mana_pct)
    #   Global combat    - all_damage, physical_damage, spell_damage,
    #                      healing_done (all multipliers, e.g. 0.02 = +2%)
    #   Per-ability      - ability_<ability_id>_damage   (multiplier)
    #                      ability_<ability_id>_cost     (flat reduction)
    #                      ability_<ability_id>_cooldown (flat turn reduction)
    #                      where <ability_id> is the Ability.ability_id, e.g.
    #                      "ability_warrior_mortal_strike_damage"
    #   Unlocks          - unlock_ability: "<ability_id>" (non-numeric,
    #                      passes through unscaled)

    def get_talent_effects(self):
        """Return the summed effects of every talent across all this
        character's trees, PLUS the current stance's bonuses (see
        combat/stances.py), as a dict of effect_key -> total value.

        Stances live here rather than in a separate aggregation step
        because every consumer of this method (_recalculate_derived_stats
        for stat keys, combat/abilities.py for per-ability keys) already
        trusts it as "every persistent bonus this character currently
        has" - a stance is exactly that, just keyed off current_stance
        instead of spent talent points.
        """
        totals = {}

        if getattr(self, "current_stance", None):
            from combat.stances import get_stance
            stance = get_stance(self.current_stance)
            if stance:
                for key, value in stance["stat_mods"].items():
                    totals[key] = totals.get(key, 0) + value

        if getattr(self, "current_form", None):
            from combat.forms import get_form
            form = get_form(self.current_form)
            if form:
                for key, value in form["stat_mods"].items():
                    totals[key] = totals.get(key, 0) + value

        if getattr(self, "guardian_stance_active", False):
            from combat.guardian_stance import get_guardian_stance
            guardian = get_guardian_stance()
            for key, value in guardian["stat_mods"].items():
                totals[key] = totals.get(key, 0) + value
            # threat_multiplier is multiplicative (3x), not additive like
            # every other key here - folding it with += would be wrong the
            # moment a second source of bonus threat existed. Set directly;
            # Earthen Guardian is the only source of this key right now so
            # there's nothing to stack against yet, but this stays correct
            # if that changes rather than silently summing multipliers.
            totals["threat_multiplier"] = guardian["threat_multiplier"]

            # Earthen Attunement (Shaman Tank talent) only does anything
            # while Earthen Guardian is active, per its own tooltip ("While
            # Earthen Guardian is active you take X% less..."). Its ranks
            # now live on the shaman_enhancement tree (Tank was merged into
            # Enhancement's own hex grid, shifted right - see the Shaman
            # Tank tree merge), same talent_id as always. Its bonus can't
            # just be a normal always-on effects entry - it needs to vanish
            # the instant the stance drops, which a plain
            # talent_tree.get_total_effects() entry has no way to express
            # (that path has no concept of "conditional on X"). Read
            # directly off the node's own points_spent here instead, gated
            # by the guardian_stance_active check this whole block is
            # already inside.
            # The magnitudes used to be hardcoded literals here (-0.02,
            # -0.03, 19.33) while the node's own `effects` carried three
            # invented keys - physical_damage_taken_pct_while_guardian and
            # friends - that NOTHING read. So the data was pure decoration,
            # the tooltip could drift from the real numbers with no way to
            # notice, and the dead-key audit flagged keys that were load
            #-bearing-looking but inert.
            #
            # The node now authors the real values under conditional_guardian_*
            # and this reads them off the node, so the data is authoritative
            # and the tooltip is checkable. get_effective_effects() is used
            # rather than node.effects because it already scales per-rank
            # values by points_spent - the rank curve comes free and cannot
            # drift from how every other talent scales.
            shaman_enhancement = self.talent_trees.get("shaman_enhancement") if hasattr(self, "talent_trees") else None
            if shaman_enhancement:
                node = shaman_enhancement.get_node("shaman_tank_earthen_attunement")
                if node and node.points_spent > 0:
                    scaled = node.get_effective_effects()
                    for src, dst in (
                        ("conditional_guardian_physical_damage_taken_pct",
                         "physical_damage_taken_pct"),
                        ("conditional_guardian_magic_damage_taken_pct",
                         "magic_damage_taken_pct"),
                    ):
                        if src in scaled:
                            totals[dst] = totals.get(dst, 0) + scaled[src]
                    if "conditional_guardian_ap_shred" in scaled:
                        totals["earthen_attunement_ap_shred"] = scaled[
                            "conditional_guardian_ap_shred"]

        # self.talent_trees doesn't exist yet during the early part of
        # __init__ (_refresh_ability_ranks() runs before the talent_trees
        # assignment further down __init__ - a pre-existing ordering gap
        # that stayed harmless until _sync_talent_unlocked_abilities()
        # started calling this during that same early window). Treating
        # "not set up yet" as "no talents spent yet" is correct either
        # way: a character with zero talent trees loaded has zero talent
        # effects, same as one whose trees are loaded but empty.
        # Pass the current form down so form-gated talents (TalentNode.
        # require_form) only contribute while that form is active - a Cat Form
        # mastery must do nothing in Bear Form.
        # A STANCE COUNTS AS A FORM FOR TALENT GATING, same as it already
        # does for ABILITY gating. abilities.py:812 resolves an ability's
        # requires_form against `current_form or current_stance`, but this
        # passed current_form ALONE - so an ability could be stance-gated
        # and a talent could not, and a talent authored "while in Berserker
        # Stance" silently did nothing for a Warrior, whose current_form is
        # always None.
        #
        # Found while building Fury's Improved Berserker Stance ("+20%
        # Strength and -10% threat while in Berserker Stance", a real
        # 3.3.5a talent) - the node loaded, the audit passed, and
        # strength_pct measured 0 in every stance including the right one.
        #
        # Purely additive: before this change exactly one talent in the
        # project gated on a stance id, and it is that new node. Every
        # other require_form value in use is a shapeshift (shadowform,
        # moonkin, cat, bear/dire_bear), which current_form still serves
        # first.
        active_form = (getattr(self, "current_form", None)
                       or getattr(self, "current_stance", None))
        for tree in getattr(self, "talent_trees", {}).values():
            for key, value in tree.get_total_effects(active_form).items():
                if isinstance(value, (int, float)):
                    totals[key] = totals.get(key, 0) + value
                else:
                    # Non-numeric (ability unlocks) - collect into a flat
                    # list. TalentTree.get_total_effects() already
                    # collects same-key values into a list WITHIN one
                    # tree, so `value` arriving here can itself be a list
                    # (multiple unlock_ability talents in the same tree)
                    # or a bare string (a tree with only one such talent).
                    # Treating both the same way - extend from an
                    # iterable, append a bare scalar - is what avoids
                    # nesting a list-inside-a-list, which used to make
                    # the final result unhashable (crashed set() in
                    # get_talent_unlocked_abilities the moment more than
                    # one tree, or one multi-value tree, contributed to
                    # the same key).
                    totals.setdefault(key, [])
                    incoming = value if isinstance(value, list) else [value]
                    for v in incoming:
                        if isinstance(totals[key], list) and v not in totals[key]:
                            totals[key].append(v)
        return totals

    #: Fixed real section keys for the 4-part background system - see
    #: self.background_sections' docstring in __init__.
    BACKGROUND_SECTION_KEYS = ("before", "adjustment", "now", "forward")
    BACKGROUND_SECTION_LABELS = {
        "before": "Before",
        "adjustment": "Adjustment",
        "now": "Now",
        "forward": "Looking Forward",
    }

    def get_background_section(self, key):
        """Real text for one background section, or "" if genuinely
        unwritten. "now" specifically falls back to self.backstory when
        background_sections doesn't have an explicit "now" entry yet -
        this is what lets every existing companion's current single-
        paragraph backstory keep showing up correctly under the "Now"
        tab without any data migration, the moment this system ships.
        Every other key ("before"/"adjustment"/"forward") has no such
        fallback - there's no prior data for those, so "" (rendered by
        the UI as "Not yet written") is the honest answer until real
        content is authored.
        """
        text = self.background_sections.get(key, "")
        if text:
            return text
        if key == "now":
            return self.backstory
        return ""

    def get_talent_effect(self, key, default=0.0):
        """Look up a single summed talent effect value by key."""
        return self.get_talent_effects().get(key, default)

    def _resist_pct_keys(self):
        """Yield (key, fraction) for every *_resist_pct talent effect held.

        Separated out so take_damage's school branch stays readable, and so
        the combined-school keys (fire_nature_resist_pct,
        poison_disease_resist_pct) need no hardcoded list - the key names its
        own schools and is split on underscores at the call site.
        """
        effects = self.get_talent_effects() if hasattr(self, "get_talent_effects") else {}
        for key, val in effects.items():
            if isinstance(key, str) and key.endswith("_resist_pct") and isinstance(val, (int, float)):
                yield key[:-len("_resist_pct")], val

    def get_talent_unlocked_abilities(self):
        """Return the list of ability_ids unlocked by spent talent points."""
        unlocked = self.get_talent_effects().get("unlock_ability", [])
        if isinstance(unlocked, str):
            return [unlocked]
        return list(unlocked)

    def can_use_stance(self, stance_id):
        """Whether this character currently qualifies for a given stance
        (right class, right level). Does not check Rage - that's checked
        separately by set_stance so the caller can distinguish "you don't
        know this stance" from "you can't afford to switch right now"."""
        if self.current_stance is None:
            return False  # not a Warrior (or any future stance-using class)
        from combat.stances import get_stance
        stance = get_stance(stance_id)
        return stance is not None and self.level >= stance["level_req"]

    def set_stance(self, stance_id, free=False):
        """Switch to a new stance. Returns (success, message).

        Charges STANCE_SWITCH_COST Rage (real WOTLK: 10 Rage per switch,
        see combat/stances.py) unless free=True - used for the initial
        stance assignment at character creation, which shouldn't cost
        anything since there's no "previous stance" to switch from.
        Recalculates derived stats immediately, same pattern as talent
        point spend/refund in talent_tree_screen.py, so the new stance's
        bonuses (or Berserker's damage-taken penalty) apply to the very
        next action rather than waiting for an unrelated recalc to notice.
        """
        if not self.can_use_stance(stance_id):
            return False, f"{self.name} cannot use that stance."
        if stance_id == self.current_stance:
            return False, f"{self.name} is already in that stance."

        from combat.stances import get_stance, STANCE_SWITCH_COST
        if not free:
            if self.current_rage < STANCE_SWITCH_COST:
                return False, f"Not enough Rage to switch stances (needs {STANCE_SWITCH_COST})."
            self.current_rage -= STANCE_SWITCH_COST

        self.current_stance = stance_id
        self._recalculate_derived_stats()
        stance = get_stance(stance_id)
        return True, f"{self.name} shifts into {stance['name']}."

    def summon_pet(self, template_id, name=None, additional=False):
        """Summon/tame a pet, replacing any currently active one. Returns
        (success, message_or_pet) - False and an error string if this
        character doesn't meet the template's level_req, otherwise True
        and the new Pet. Both Hunter taming and Warlock summoning funnel
        through this single method - the two classes differ only in WHICH
        template_ids their UI offers, not in how acquisition actually
        works mechanically (see entities/pet.py's module docstring).

        The level check lives HERE, not just in the UI that lists
        available pets - a UI-only check is advisory, not enforcement;
        anything that calls this method directly (a test, a future
        console command, a bug in the screen's own click handling) could
        otherwise hand a level 5 character a level-30-gated Felhunter.
        Confirmed this was a real gap, not a hypothetical one: calling
        summon_pet('felhunter') directly on a level 5 Warlock succeeded
        before this check existed.
        """
        from combat.pet_templates import get_pet_template
        template = get_pet_template(template_id)
        if template is None:
            return False, f"Unknown pet '{template_id}'."
        level_req = template.get("level_req", 1)
        if self.level < level_req:
            return False, f"Requires level {level_req} to summon a {template['display_name']}."

        from entities.pet import Pet
        display_name = name or template["display_name"]
        pet = Pet(name=display_name, template_id=template_id, owner=self)

        # additional=True parks this one alongside the primary instead of
        # replacing it, up to the class's cap. Re-summoning the same template
        # refreshes rather than stacking duplicates, so spamming a turret
        # button cannot build an army.
        # An additional summon with no primary yet BECOMES the primary, so a
        # Necromancer's first raise fills the main slot and the next three go
        # to extras - four bodies from four abilities, rather than three plus
        # an empty primary.
        if additional and self.max_extra_pets and self.active_pet is None:
            self.active_pet = pet
            return True, pet

        if additional and self.max_extra_pets:
            self.extra_pets = [p for p in self.extra_pets
                               if p.template_id != template_id]
            if len(self.extra_pets) >= self.max_extra_pets:
                self.extra_pets.pop(0)          # oldest construct expires
            self.extra_pets.append(pet)
            return True, pet

        self.active_pet = pet
        return True, self.active_pet

    #: How many pets a class may field BEYOND active_pet. Only the specs CoA
    #: describes as fielding a board get any; everyone else stays at 0, so
    #: nothing changes for the remaining 27 classes.
    #:
    #: Witch Hunter was added after the fact and it fixes a button that
    #: DOWNGRADED you: Unleash the Hounds at level 20 was replacing the
    #: level-1 permanent Shadowhound with a weaker Lesser Shadowhound, so
    #: pressing it made you worse. CoA reads as a pack either way -
    #: Houndmaster's Call and Rampaging Hounds both say "Hounds", plural.
    EXTRA_PET_CAP = {"Tinker": 2, "Necromancer": 3, "Witch Hunter": 2}

    @property
    def max_extra_pets(self):
        # Display-name keys against an id. Necromancer, Tinker and Witch Hunter all resolved
        # to 0, so the three classes built around commanding several minions could not summon a
        # single extra one. See core/class_names.py.
        from core.class_names import lookup
        return lookup(self.EXTRA_PET_CAP, self.char_class, 0)

    @property
    def all_pets(self):
        """Primary pet plus any additional ones, in summon order."""
        out = [self.active_pet] if self.active_pet else []
        return out + list(self.extra_pets)

    def dismiss_pet(self):
        """Release the active pet, if any. Real WoW: Hunters can only
        dismiss between fights (no in-combat dismiss), which this engine
        doesn't need to enforce itself since nothing currently calls this
        mid-turn - documented here rather than added as an unused guard."""
        self.active_pet = None
        self.extra_pets = []

    def set_totem(self, totem_ability_id):
        """Slot a totem into the loadout, replacing whatever was in that
        element's slot (matches real WoW: only one totem per element).
        Returns (success, message)."""
        from combat.totems import element_of
        element = element_of(totem_ability_id)
        if element is None:
            return False, f"'{totem_ability_id}' is not a known totem."
        self.totem_loadout[element] = totem_ability_id
        return True, f"{self.name}'s {element} totem slot set."

    def clear_totem(self, element):
        self.totem_loadout.pop(element, None)

    def generates_rage_from_combat(self):
        """True for Warriors and for anyone in a Rage shapeshift form (Druid Bear /
        Dire Bear, Venomancer Beetle) - they build Rage from hitting and being hit."""
        if self.char_class == "Warrior":
            return True
        form = getattr(self, "current_form", None)
        if form:
            from combat.forms import resource_for_form
            from combat.abilities import ResourceType
            return resource_for_form(form) == ResourceType.RAGE
        return False

    def can_use_form(self, form_id):
        """Whether this character currently qualifies for a given form
        (right class, right level)."""
        from combat.forms import get_form
        form = get_form(form_id)
        return form is not None and form["class"] == self.char_class and self.level >= form["level_req"]

    def shift_form(self, form_id):
        """Enter a persistent shapeshift form. Returns (success, message).

        PERSISTENT per Kyle's direction - nothing anywhere calls this
        automatically, the player shifts once and stays shifted across
        multiple fights until they explicitly revert_form() or shift
        again.

        Resets RAGE and ENERGY to 0 on shift. Mana is deliberately NOT
        reset, and that distinction is the whole fix for the 2 Nov hard
        lock (tools/qa_druid_form_lock.py).

        The rule this used to cite - "shifting resets your current
        resource unless talented otherwise" - is about the Rage and
        Energy pools. Mana persists across a shift in real WoW; that is
        exactly what makes shifting out to cast a heal possible. Zeroing
        all three meant a druid who shifted into Bear had 0 rage
        (correct) and 0 mana (wrong), leaving no resource anywhere in the
        character to spend on anything at all. The symptom got noticed
        once before and patched in the wrong place - combat/abilities.py
        still carries a comment reading "shifting wipes the mana pool, so
        a charge here would trap a Bear-form Druid in Bear Form", which
        made shifting free rather than asking why the pool was being
        wiped.
        """
        if not self.can_use_form(form_id):
            return False, f"{self.name} cannot use that form."
        if form_id == self.current_form:
            return False, f"{self.name} is already in that form."

        from combat.forms import get_form
        form = get_form(form_id)
        old_max_health, old_current_health = self.health, self.current_health
        self.current_form = form_id
        self.current_rage = 0
        self.current_energy = 0
        self._recalculate_derived_stats()
        self._carry_health_through_max_change(old_max_health, old_current_health)
        return True, f"{self.name} shifts into {form['name']}."

    def _carry_health_through_max_change(self, old_max_health, old_current_health):
        """Keep the health BAR where it was when a form changes max health.

        Bear Form's +25 Stamina takes a level 15 druid from 244 max health
        to 444. Leaving current_health alone meant a full-health druid
        shifted into bear and immediately read 244/444 - 55% - which is
        what Kyle's friend reported as "bear form has separate health from
        caster with no way to heal it". It was never a second pool; it
        just looked like one, because the bar dropped by half the moment
        he shifted and no heal he could reach would move it.

        Matching WoW: a Stamina gain hands you the health with it, and
        losing it takes the same amount back. Carrying the DELTA rather
        than the percentage is what makes shift -> revert -> shift a no-op
        instead of a slow drain or a free heal.

        The delta is applied to the current health from BEFORE the recalc,
        not to whatever is on the character now. _recalculate_derived_stats
        ends with `current_health = min(current_health, health)`, so on the
        way DOWN out of a form it has already taken the lost maximum off -
        adding the negative delta on top of that subtracted it twice. A
        full-health level 60 druid round-tripping bear went 420 -> 620 ->
        220, losing half its health for shifting and shifting back. The
        single shift looked perfect, which is why only the round trip
        caught it.
        """
        delta = self.health - old_max_health
        if delta and old_current_health > 0:
            self.current_health = max(1, min(self.health, old_current_health + delta))

    def revert_form(self):
        """Return to base Humanoid form. Returns (success, message).

        Mana survives the trip back for the same reason it survives the
        trip out (see shift_form) - a druid who shifts out of Bear to heal
        and finds an empty mana pool waiting is in the same trap by a
        different door. Rage and Energy reset, since the form that used
        them is gone.
        """
        if self.current_form is None:
            return False, f"{self.name} is not shapeshifted."
        old_max_health, old_current_health = self.health, self.current_health
        self.current_form = None
        self.current_rage = 0
        self.current_energy = 0
        self._recalculate_derived_stats()
        self._carry_health_through_max_change(old_max_health, old_current_health)
        return True, f"{self.name} reverts to normal form."

    def get_basic_attack_id(self):
        """This class's basic attack, by the "<class_prefix>_attack"
        convention every class's ability file already follows.

        Exists so combat can offer the basic attack as a permanent action
        rather than trusting it to be on the hotbar. Kyle's friend took it
        off his bar, which removed the only rage-generating action in the
        game from a class that needs rage to do anything - the hotbar is a
        convenience, and the game must not become unplayable because
        someone rearranged it.
        """
        from combat.abilities import _class_file_prefix
        if not getattr(self, "ability_book", None):
            return None
        ability_id = f"{_class_file_prefix(self.char_class)}_attack"
        return ability_id if self.ability_book.get_ability(ability_id) else None

    def toggle_guardian_stance(self):
        """Flip Earthen Guardian on/off (Shaman Tank). Returns (success,
        message). Costs guardian_stance.EARTHEN_GUARDIAN['activation_cost']
        Mana to turn ON; turning OFF is free, matching how the Warrior
        stance-switch cost only ever gates ENTERING a stance in spirit
        (real WOTLK doesn't charge Rage to stop tanking either). Does NOT
        reset current_mana - unlike shift_form, Earthen Guardian doesn't
        change resource pools, so there's nothing to reset (see
        combat/guardian_stance.py's module docstring for why this isn't
        just shift_form with a different table).
        """
        if self.char_class != "Shaman":
            return False, f"{self.name} cannot use Earthen Guardian."

        from combat.guardian_stance import get_guardian_stance
        stance = get_guardian_stance()

        if self.level < stance["level_req"]:
            return False, f"Earthen Guardian requires level {stance['level_req']}."

        if self.guardian_stance_active:
            self.guardian_stance_active = False
            self._recalculate_derived_stats()
            return True, f"{self.name} drops Earthen Guardian."

        cost = stance["activation_cost"]
        if self.current_mana < cost:
            return False, f"Not enough Mana to activate Earthen Guardian (needs {cost})."
        self.current_mana -= cost
        self.guardian_stance_active = True
        self._recalculate_derived_stats()
        return True, f"{self.name} becomes an Earthen Guardian!"

    def _apply_level_scaling(self):
        """Apply level-based stat scaling.

        Recomputed from `self.class_base_stats` (the level-1 snapshot) every
        call, NOT accumulated onto the current values. This is what makes it
        safe to call on every level-up. Previously it only ran once at
        character creation, which meant a character's core stats were frozen
        for their entire life - levelling from 1 to 60 granted literally zero
        Strength/Intellect/Stamina.
        """
        base = getattr(self, "class_base_stats", None)
        if not base:
            # Older save or a character built before the snapshot existed.
            base = {
                "strength": self.strength, "stamina": self.stamina,
                "intellect": self.intellect, "spirit": self.spirit,
                "agility": self.agility,
            }
            self.class_base_stats = dict(base)

        self.strength = base["strength"]
        self.stamina = base["stamina"]
        self.intellect = base["intellect"]
        self.spirit = base["spirit"]
        self.agility = base["agility"]

        level_bonus = self.level - 1
        
        if self.char_class == "Warrior":
            self.strength += level_bonus * 1.0
            self.stamina += level_bonus * 0.9
            self.agility += level_bonus * 0.4
        elif self.char_class == "Shaman":
            self.intellect += level_bonus * 1.0
            self.spirit += level_bonus * 0.9
            self.stamina += level_bonus * 0.5
        elif self.char_class == "Rogue":
            self.agility += level_bonus * 1.0
            self.strength += level_bonus * 0.8
            self.stamina += level_bonus * 0.4
        elif self.char_class == "Priest":
            self.intellect += level_bonus * 1.0
            self.spirit += level_bonus * 0.9
            self.stamina += level_bonus * 0.5
        elif self.char_class == "Hunter":
            self.agility += level_bonus * 1.0
            self.stamina += level_bonus * 0.6
            self.intellect += level_bonus * 0.3
        elif self.char_class == "Mage":
            self.intellect += level_bonus * 1.0
            self.spirit += level_bonus * 0.7
            self.stamina += level_bonus * 0.3
        elif self.char_class == "Warlock":
            self.intellect += level_bonus * 1.0
            self.stamina += level_bonus * 0.6
            self.spirit += level_bonus * 0.5
        elif self.char_class == "Druid":
            self.intellect += level_bonus * 0.8
            self.spirit += level_bonus * 0.7
            self.stamina += level_bonus * 0.5
            self.agility += level_bonus * 0.3
        elif self.char_class == "Paladin":
            self.strength += level_bonus * 0.9
            self.intellect += level_bonus * 0.6
            self.stamina += level_bonus * 0.8
            self.spirit += level_bonus * 0.4
        else:
            # Generic fallback for the 21 CoA classes (no abilities exist for
            # them yet per Kyle's direction, so hand-tuning 21 more bespoke
            # scaling curves isn't worth it right now). Derives scaling
            # proportionally from the class's own base stat ratios instead
            # of a flat/arbitrary split - a class with high base Intellect
            # naturally scales Intellect fastest, etc. Every base stat still
            # grows somewhat (matching how every original-9 class grows a
            # little in everything), just weighted toward what the class
            # actually leans on.
            base_total = self.strength + self.stamina + self.intellect + self.spirit + self.agility
            if base_total > 0:
                self.strength += level_bonus * 0.5 * (self.strength / base_total) * 5
                self.stamina += level_bonus * 0.5 * (self.stamina / base_total) * 5
                self.intellect += level_bonus * 0.5 * (self.intellect / base_total) * 5
                self.spirit += level_bonus * 0.5 * (self.spirit / base_total) * 5
                self.agility += level_bonus * 0.5 * (self.agility / base_total) * 5

        # Core stats are whole numbers everywhere they're displayed or used;
        # keeping fractional values here just leaks "15.6 Strength" into the
        # character sheet.
        self.strength = int(self.strength)
        self.stamina = int(self.stamina)
        self.intellect = int(self.intellect)
        self.spirit = int(self.spirit)
        self.agility = int(self.agility)
    
    def _recalculate_derived_stats(self):
        """Recalculate all derived stats from base stats + equipped gear bonuses."""
        bonuses = self.equipment.get_total_stat_bonuses()

        # Fold talent stat effects into the same bonus pool as gear, so any
        # talent granting a raw stat (+STR, +crit, +armor, ...) flows through
        # the identical derived-stat maths as an equipped item would. Only
        # keys the recalc below actually reads matter here; unrecognised keys
        # (per-ability multipliers etc.) are simply ignored at this layer and
        # get consumed by combat/abilities.py instead.
        talent_effects = self.get_talent_effects() if self.talent_trees else {}
        for _key, _value in talent_effects.items():
            if isinstance(_value, (int, float)):
                bonuses[_key] = bonuses.get(_key, 0) + _value

        # Temporary combat buffs/debuffs (Battle Shout, Demoralizing Shout,
        # Blessing of Kings, etc.) fold in through the exact same pool, so a
        # +30 Attack Power buff and a +30 Attack Power item are indistinguish-
        # able to every downstream formula. Recalc is re-triggered whenever an
        # effect is applied or expires (see _on_status_effects_changed).
        for _eff in self._effects():
            # Scaled by stacks, matching get_status_stat_mod, which has always
            # multiplied by them. This path did not, so the two readers of the
            # same stat_mods disagreed: a 5-stack buff granting spell_power or
            # armor delivered ONE stack's worth through the derived-stat pool
            # while a damage_taken_pct buff delivered all five. Every stacking
            # buff whose payload is a plain stat was therefore silently capped
            # at rank one, which is why authors kept reaching for the handful
            # of keys that happened to route through get_status_stat_mod.
            _stacks = max(1, getattr(_eff, "stacks", 1) or 1)
            for _key, _value in _eff.stat_mods.items():
                if isinstance(_value, (int, float)):
                    bonuses[_key] = bonuses.get(_key, 0) + _value * _stacks
                else:
                    bonuses[_key] = _value

        # Elixir/food consumable buffs (guardian/battle/food slots) - same
        # bonus pool as gear/talents/status effects, so "+8 Intellect, +4
        # Spell Power" from a food buff feeds every downstream formula
        # (spell_power calc below, crit, etc.) exactly like a ring with the
        # same stats would. Previously get_active_buff_stats() existed but
        # was never called from here, so consumable buffs did nothing to
        # actual character stats - this wires it in for real.
        for _key, _value in self.get_active_buff_stats().items():
            bonuses[_key] = bonuses.get(_key, 0) + _value

        # Effective core stats = base + gear (base stats themselves are never mutated).
        # Stored as persistent attributes (not just locals) so UI screens like the
        # character sheet can display "what you actually have" including gear,
        # rather than reading the frozen base-only self.strength/self.intellect/etc.
        eff_strength = self.strength + bonuses.get("strength", 0)
        eff_stamina = self.stamina + bonuses.get("stamina", 0)
        eff_intellect = self.intellect + bonuses.get("intellect", 0)
        eff_spirit = self.spirit + bonuses.get("spirit", 0)
        eff_agility = self.agility + bonuses.get("agility", 0)

        # all_stats_pct (CoA buffs like Whispers of N'Zoth, Devotion of
        # Emperors, Etching of the Leylines: "+10% all stats") - a flat %
        # multiplier on top of the additive strength/stamina/intellect/
        # spirit/agility bonuses just computed above, same two-layer shape
        # real WoW uses (flat stat items, then a multiplicative "all stats"
        # cooldown on top). Applied here, before every downstream formula
        # (attack_power, spell_power, armor, crit, ...) derives from these
        # eff_* values, so a +10% all-stats buff actually ripples through
        # every stat it should rather than only existing on paper.
        all_stats_mult = 1.0 + bonuses.get("all_stats_pct", 0) / 100.0
        eff_strength *= all_stats_mult
        eff_stamina *= all_stats_mult
        eff_intellect *= all_stats_mult
        eff_spirit *= all_stats_mult
        eff_agility *= all_stats_mult

        # Single-stat percentage companions to all_stats_pct above, for
        # talents/buffs that boost exactly ONE stat rather than all five
        # (Cultist's Thick Skin: "+2%/rank Armor AND Stamina" - the Stamina
        # half needs its own key since all_stats_pct would wrongly also
        # boost Strength/Agility/Intellect/Spirit for a talent that only
        # ever mentions Armor+Stamina). Applied multiplicatively on top of
        # all_stats_pct, same layering convention (flat bonus, then %
        # multiplier) used throughout this method. Added as a full set
        # (not just stamina_pct) so the same convention is available to
        # any future strength_pct/agility_pct/intellect_pct/spirit_pct
        # talent or buff without another one-off key needing to be invented.
        eff_strength *= 1.0 + bonuses.get("strength_pct", 0) / 100.0
        eff_stamina *= 1.0 + bonuses.get("stamina_pct", 0) / 100.0
        eff_intellect *= 1.0 + bonuses.get("intellect_pct", 0) / 100.0
        eff_spirit *= 1.0 + bonuses.get("spirit_pct", 0) / 100.0
        eff_agility *= 1.0 + bonuses.get("agility_pct", 0) / 100.0

        self.effective_strength = eff_strength
        self.effective_stamina = eff_stamina
        self.effective_intellect = eff_intellect
        self.effective_spirit = eff_spirit
        self.effective_agility = eff_agility

        # Attack Power
        # attack_power_pct (CoA's Boon of the Bear: "+10% Attack Power") is
        # a straight multiplier on the final value, same two-layer pattern
        # as all_stats_pct above (flat bonus first, then a % cooldown on
        # top) rather than feeding into the strength/agility formula itself.
        self.attack_power = int((int(eff_strength * 2 + eff_agility * 0.5) + int(bonuses.get("attack_power", 0)))
                                 * (1.0 + bonuses.get("attack_power_pct", 0) / 100.0))
        self.ranged_attack_power = int(eff_agility * 2 + eff_strength * 0.5)

        # Spell Power / Healing Power: small per-point contribution from base
        # stats (0.2 per INT for Spell Power; 0.2 per INT + 0.2 per Spirit for
        # Healing Power), same philosophy as WoW - a level 60 naked caster's
        # rank-1 spell hits almost the same as a level 1 naked caster's,
        # because the stat contribution is small enough that leveling alone
        # barely moves it. Real growth comes from gear (spell_power /
        # healing_power secondary stat rolls). Spirit is intentionally not
        # the ONLY path to Healing Power - not every healer build leans on it.
        self.spell_power = int(eff_intellect * 0.2) + int(bonuses.get("spell_power", 0))
        # healing_power_pct (Starcaller's Aspect of the Goddess: "+15%
        # Healing Power") - same final-multiplier shape as attack_power_pct.
        self.healing_power = int((int(eff_intellect * 0.2 + eff_spirit * 0.2) + int(bonuses.get("healing_power", 0)))
                                  * (1.0 + bonuses.get("healing_power_pct", 0) / 100.0))
        
        # Crits
        self.crit_chance_physical = eff_agility * 0.5 + bonuses.get("crit_chance_physical", 0)
        self.crit_chance_spell = eff_intellect * 0.5 + bonuses.get("crit_chance_spell", 0)

        # Hit Rating (Phase 5c): gear-only secondary stat, 1 rating = 1% less
        # miss chance, capped so it can't go negative (min 0% miss / 100% hit).
        # No base-stat contribution (unlike Crit/Haste) - this is purely a
        # gear stat, matching WoW's convention where Hit Rating has no
        # baseline from STR/AGI/INT.
        hit_rating = bonuses.get("hit_rating", 0)
        self.base_miss_chance_physical = max(0.0, 8.0 - hit_rating)
        self.base_miss_chance_spell = max(0.0, 6.0 - hit_rating)
        self.hit_chance_physical = 100.0 - self.base_miss_chance_physical
        self.hit_chance_spell = 100.0 - self.base_miss_chance_spell
        
        # Avoidance
        # dodge_rating/parry_rating/block_rating (real gear suffix stats,
        # see data/items/gear_suffixes.json) feed directly into these
        # same existing %-stats, same convention hit_rating already uses
        # for miss chance - Kyle's explicit call: no separate
        # diminishing-returns rating system, just a direct additive feed.
        # defense_rating is split evenly across dodge/parry as a broad
        # "harder to hit overall" stat, since the doc pairs it with
        # Dodge/Parry in suffixes like "of Eluding" rather than treating
        # it as its own distinct mechanic.
        defense_bonus = bonuses.get("defense_rating", 0) * 0.5
        # BASE_DODGE: everybody can get out of the way of something. Kyle, 2026-10-28: "its
        # impossible for no tanks to have no dodge. agility should give dodge and each class
        # should have baseline 5% dodge." Agility already fed dodge at a quarter point each; what
        # was missing was the floor, so a low-agility plate wearer with no dodge talent sat near
        # zero. Added before the agility term so it is a floor every class shares rather than
        # something only a talent or a gear suffix can buy.
        # Base-stat dodge is NOT diminished (see AVOIDANCE_DR_K); only what
        # talents, gear suffixes and defense rating add on top of it.
        self.dodge = (self.BASE_DODGE + eff_agility * 0.25
                      + self._diminish(bonuses.get("dodge", 0)
                                       + bonuses.get("dodge_rating", 0)
                                       + defense_bonus))
        # spirit_guard_block_from_agility (Spirit Guard, Shaman Tank: "gain
        # Block Rating equal to 33%/66%/100% of your Agility per rank") -
        # an ADDITIONAL block source layered on top of the existing
        # Strength-based formula below, not a replacement - real WoW block
        # rating stacks from every source (gear, Strength conversion,
        # talent conversions) rather than any one overriding another.
        agility_block_bonus = eff_agility * bonuses.get("spirit_guard_block_from_agility", 0.0)
        # BLOCK VALUE: how much a blocked hit loses. Strength, the shield itself, and the talent
        # conversions - block_rating and Spirit Guard's agility conversion are rating, i.e. value.
        self.block_value = (eff_strength * 0.3 + self.equipment.get_total_block_value()
                            + bonuses.get("block_rating", 0) + agility_block_bonus)
        # block_value_pct scales the VALUE, which is what its name always said and what the two
        # talents using it meant. Before the split it scaled the number being used as a chance.
        self.block_value *= (1.0 + bonuses.get("block_value_pct", 0))
        # BLOCK CHANCE: a percentage, and only if there is a shield to block with. The talent key
        # `block` is a chance in every tree that uses it - Shield Specialization 2 a point, Holy
        # Shield 10, Improved Holy Shield 4 - so it feeds here, not into the value. defense_rating
        # raises it the same way it raises dodge and parry.
        self.block_chance = 0.0
        if self.equipment.get_shield_armor() > 0 or self.equipment.get_total_block_value() > 0:
            self.block_chance = (self.BASE_BLOCK_CHANCE + bonuses.get("block", 0) + defense_bonus)
        self.block_chance = max(0.0, min(self.BLOCK_CHANCE_CAP, self.block_chance))
        avg_stat = (eff_agility + eff_strength) / 2
        # Parry previously ignored the bonus pool entirely, so gear and
        # talents rolling Parry did nothing. Now additive like Dodge.
        self.parry = avg_stat * 0.2 + self._diminish(
            bonuses.get("parry", 0) + bonuses.get("parry_rating", 0) + defense_bonus)

        # Joint ceiling on outright avoidance. Scaled proportionally rather
        # than clipped one stat at a time, so a build that leaned on parry
        # keeps leaning on parry instead of having whichever stat is checked
        # second silently zeroed. Block is excluded - it reduces a hit by
        # 30%, it does not erase it, and it has its own cap.
        total_avoid = self.dodge + self.parry
        if total_avoid > self.AVOIDANCE_COMBINED_CAP:
            scale = self.AVOIDANCE_COMBINED_CAP / total_avoid
            self.dodge *= scale
            self.parry *= scale

        self.haste = (eff_intellect + eff_agility) * 0.1 + bonuses.get("haste", 0)

        # New real gear-suffix stats - see Character.__init__ for what
        # each does. Pure pass-through from gear bonuses; none of these
        # have a base-stat-derived component the way dodge/parry/haste
        # do, since nothing in the doc's suffixes scales them off Str/
        # Agi/Int - they're gear-only stats.
        self.mp5 = bonuses.get("mp5", 0)
        self.spell_penetration = bonuses.get("spell_penetration", 0)
        self.fire_spell_power = bonuses.get("fire_spell_power", 0)
        self.frost_spell_power = bonuses.get("frost_spell_power", 0)
        self.arcane_spell_power = bonuses.get("arcane_spell_power", 0)
        self.shadow_spell_power = bonuses.get("shadow_spell_power", 0)
        self.nature_spell_power = bonuses.get("nature_spell_power", 0)
        self.holy_spell_power = bonuses.get("holy_spell_power", 0)
        
        # Resources (conservative scaling for long-term progression)
        old_health_max = self.health
        self.health = int((100 + eff_stamina * 8) * (1.0 + bonuses.get("max_health_pct", 0)))
        old_mana_max = self.mana

        # Only Mana-resource classes actually get a Mana pool. Rage/Energy
        # classes (Warrior/Rogue) have no use for Mana in their kit at all -
        # previously this ran unconditionally for every class, which meant a
        # Warrior silently carried around a nonzero, unused Mana pool
        # (computed from their small INT/Spirit stats) that never showed in
        # the UI but existed in memory/save data for no reason.
        # The gate is the class's BASE resource, deliberately not
        # get_class_resource(), which returns the FORM's resource while
        # shapeshifted. Asking the form meant a Druid in Bear Form was
        # judged a Rage class and had their Mana pool recomputed to zero -
        # the pool did not just stop being spendable, it ceased to exist,
        # and current_mana got clamped to 0 against it a line later.
        #
        # That is what made Bear Form a prison on 2 Nov 2026: 0 rage
        # (correct on a fresh shift) and 0 mana (because the pool was
        # gone), so nothing in the character could pay for anything,
        # including shifting back out. A form changes which pool you DRAW
        # FROM - see combat/forms.py - it does not delete the others. A
        # real bear still has its mana underneath, which is precisely what
        # it spends to shift out and heal.
        from combat.abilities import _lookup_class_resource, ResourceType
        base_resource, _ = _lookup_class_resource(self.char_class)
        if base_resource == ResourceType.MANA:
            self.mana = int((100 + eff_intellect * 15 + eff_spirit * 5)
                            * (1.0 + bonuses.get("max_mana_pct", 0)))
        else:
            self.mana = 0

        # Preserve current HP/mana proportionally when recalculating due to gear changes,
        # but full-heal on first init (old_health_max == 0) same as before Phase 5.
        if old_health_max <= 0:
            self.current_health = self.health
        else:
            self.current_health = min(self.current_health, self.health)

        if old_mana_max <= 0:
            self.current_mana = self.mana
        else:
            self.current_mana = min(self.current_mana, self.mana)
        
        # Defense (base armor from Stamina + gear armor value)
        # shield_armor_pct (Shield Specialization, Shaman Tank: "+10% Armor
        # from your equipped Shield per rank") scales ONLY the shield's own
        # armor contribution (get_shield_armor), not the whole armor total -
        # a rank of this talent shouldn't also boost armor from chest/legs.
        # Applied as a separate additive bonus on top of the shield's base
        # contribution (which is already counted once inside
        # get_total_armor() above), matching how every other _pct bonus in
        # this method adds a bonus rather than re-deriving the base value.
        shield_bonus = int(self.equipment.get_shield_armor() * bonuses.get("shield_armor_pct", 0))
        # armor_pct (Primalist's Golem Form: "+20% Armor"; Primalist's
        # Terrasurge debuff: "-50% Armor" via the same key, negative value)
        # is a final multiplier on the whole armor total, same shape as
        # every other _pct bonus in this method.
        #
        # conditional_avatar_armor_pct (Mountain King's Earthen Bulwark:
        # "+4% Armor per rank while Mountain Avatar is active") is a
        # DIFFERENT shape from every other _pct key above - those all come
        # from get_talent_effects()'s static per-rank sum, but this one is
        # genuinely conditional on live combat state (whether the carrier
        # currently has the Earthen Avatar buff up), which bonuses (a pure
        # numeric dict) has no way to express. Checked directly via
        # has_status_effect against Mountain Avatar's real synthetic
        # buff id (see primalist_mountain_king.json's mountain_avatar proc
        # - apply_effect's effect_id), not read from bonuses at all. Safe
        # to call unconditionally even on classes/mobs with no talent in
        # this tree: get_talent_effect defaults to 0 and has_status_effect
        # is always defined on StatusEffectMixin.
        avatar_armor_bonus = 0.0
        if hasattr(self, "has_status_effect") and self.has_status_effect("primalist_earthen_avatar"):
            avatar_armor_bonus = self.get_talent_effect("conditional_avatar_armor_pct", 0.0) if hasattr(self, "get_talent_effect") else 0.0
        self.armor = int((int(eff_stamina * 2) + self.equipment.get_total_armor()
                          + int(bonuses.get("armor", 0)) + shield_bonus)
                          * (1.0 + bonuses.get("armor_pct", 0) / 100.0 + avatar_armor_bonus))
        # armor_penetration / armor_penetration_pct (Tinker's Round Armor
        # Pen, Piercing Augmentation) - real derived stats, and now actually
        # CONSUMED: take_damage's physical branch subtracts them from the
        # defender's Armor before mitigation. For a long time they were
        # computed and read by nothing, on the grounds that threading the
        # attacker through take_damage would be too invasive - by the time
        # that was revisited, `attacker` was already a parameter and every
        # call site already passed it, so the blocker had quietly gone away.
        self.armor_penetration = int(bonuses.get("armor_penetration", 0))
        self.armor_penetration_pct = bonuses.get("armor_penetration_pct", 0) / 100.0
        # Magic Resistance is talent/gear/buff-granted ONLY, same pattern
        # as the per-school resistances just below (Kyle: "remove Spirit
        # adding magic resistance, these will be talents only") - the old
        # `eff_spirit * 2` term meant every caster carried a flat magic
        # resist floor from Spirit alone with zero real resistance talents
        # taken, which isn't the real WoW model and made the character
        # sheet show a nonzero value that didn't come from anything the
        # player actually did.
        self.magic_resistance = int(bonuses.get("magic_resistance", 0))

        # ── stat conversion: <target>_from_<source>_pct ────────────────────
        #
        # "Increases your Healing Power by 20% of your Intellect" is a real
        # and very common WoW talent shape, and twenty-four talents across
        # every homebrew class were authored for it - healing_power_from_
        # intellect_pct, spell_damage_from_strength_pct, ap_from_agility_pct,
        # parry_from_intellect_pct and so on. Not one of those keys was read
        # by anything, so all twenty-four did nothing.
        #
        # Handled generically rather than key by key: the key names its own
        # target and source, so one loop covers every combination the data
        # already uses and any future one, instead of twenty-four bespoke
        # branches that the next author would have to extend. Values are
        # FRACTIONS of the source stat (0.20 = +20% of Intellect), matching
        # how the data authors them.
        #
        # Deliberately runs AFTER every base derived stat above, so the
        # source values are the final post-gear, post-buff ones, and the
        # conversion cannot feed back into itself.
        _conv_sources = {
            "strength": eff_strength, "agility": eff_agility,
            "intellect": eff_intellect, "spirit": eff_spirit,
            "stamina": eff_stamina,
            "ap": self.attack_power, "attack_power": self.attack_power,
            "spell_power": self.spell_power,
            # "weapon": average main-hand weapon damage. Equipment has no
            # get_weapon_damage method - it never did - so the old hasattr
            # guard meant this source resolved to 0 for every character and
            # Cultist Heretic's Void Power ("+2%/rank healing power from
            # main-hand weapon damage", 5 ranks) converted nothing. Read off
            # the equipped item's own min/max instead, which is what the
            # talent's wording means, and stays 0 while unarmed.
            "weapon": _main_hand_average_damage(self.equipment),
            # str_int: the sum, for Cultist's "Strength and Intellect" nodes
            "str_int": eff_strength + eff_intellect,
        }
        _conv_targets = STAT_CONVERSION_TARGETS
        for key, pct in bonuses.items():
            if not isinstance(pct, (int, float)) or not pct:
                continue
            if not key.endswith("_pct") or "_from_" not in key:
                continue
            tgt_name, src_name = key[:-4].split("_from_", 1)
            attr = _conv_targets.get(tgt_name)
            src = _conv_sources.get(src_name)
            if attr is None or src is None:
                continue  # unknown pairing - left to the dead-key audit
            current = getattr(self, attr, 0) or 0
            gained = src * pct
            # Integer stats stay integers; the percentage ones (crit, haste,
            # parry, dodge) are floats and keep their precision.
            setattr(self, attr, int(current + gained)
                    if isinstance(current, int) else current + gained)

        # Per-school resistances: purely bonus-pool driven (talents, gear,
        # buffs via the same `bonuses` dict every other derived stat reads
        # here), NOT derived from a base stat like magic_resistance's
        # Spirit-scaling - real WoW resistances come from gear/buffs, not
        # a character attribute, and Kyle wants per-monster/per-class
        # control here (a fire elemental with real Fire resistance, a
        # frost elemental with real Frost resistance, distinct from each
        # other) rather than every character sharing one formula. Defaults
        # to 0 for anything that hasn't been given resistance via talents/
        # gear/status effects - existing content is completely unaffected
        # until something deliberately grants one of these.
        self.fire_resistance = int(bonuses.get("fire_resistance", 0))
        self.frost_resistance = int(bonuses.get("frost_resistance", 0))
        self.nature_resistance = int(bonuses.get("nature_resistance", 0))
        self.shadow_resistance = int(bonuses.get("shadow_resistance", 0))
        self.arcane_resistance = int(bonuses.get("arcane_resistance", 0))
        self.holy_resistance = int(bonuses.get("holy_resistance", 0))
        
        # Turn speed
        self.turn_speed = 1.0 + (eff_agility / 100.0)
    
    def get_weapon_damage_roll(self, use_ranged=False, include_offhand=True):
        """
        Roll a random damage value from equipped weapon(s). Main Hand rolls
        at full value; if include_offhand=True and an Off Hand weapon is
        equipped (dual wield), it rolls too but at a 50% penalty, matching
        WoW's dual-wield offhand damage convention. use_ranged=True checks
        the Ranged slot (wand) instead, for caster auto-attacks - offhand
        is irrelevant there.
        """
        import random

        if use_ranged:
            weapon = self.equipment.get_ranged_weapon()
            if not weapon or weapon.weapon_damage_max <= 0:
                return 0
            return random.randint(weapon.weapon_damage_min, weapon.weapon_damage_max)

        total = 0
        main_hand = self.equipment.get_main_hand_weapon()
        if main_hand and main_hand.weapon_damage_max > 0:
            total += random.randint(main_hand.weapon_damage_min, main_hand.weapon_damage_max)

        if include_offhand:
            off_hand = self.equipment.slots.get("off_hand")
            if off_hand and off_hand.weapon_damage_max > 0:
                offhand_roll = random.randint(off_hand.weapon_damage_min, off_hand.weapon_damage_max)
                total += int(offhand_roll * 0.5)  # Dual-wield offhand penalty (WoW convention)

        return total

    def get_weapon_dps(self, use_ranged=False):
        """Return the DPS of the equipped main-hand (or ranged) weapon. 0 if unarmed."""
        weapon = self.equipment.get_ranged_weapon() if use_ranged else self.equipment.get_main_hand_weapon()
        if not weapon:
            return 0.0
        return weapon.get_dps()

    def gain_experience(self, amount):
        """
        Gain XP and check level up. Uses a while loop (not a single if) so a
        large XP reward that crosses multiple level thresholds at once
        correctly cascades through each level, carrying the leftover XP
        forward each time - rather than the old behavior of leveling up once
        and discarding all overflow XP regardless of how much was earned
        (which caused "went from level 2 to level 4 in one fight" style bugs
        when a big reward landed).

        Uses config.get_exp_needed_for_level() as the single source of truth
        for the XP curve - character_sheet_screen.py must call the same
        function for its EXP bar display, never a separately hardcoded
        formula, to avoid the display/logic mismatch that caused confusing
        "random" level jumps in earlier testing.

        Returns the number of levels gained (0 if none), so callers (like
        the combat log) can announce level-ups explicitly. The per-level stat
        gains are aggregated into `self.last_level_gains` so the combat log
        can also report what the level(s) actually granted.
        """
        from config import get_exp_needed_for_level

        self.experience += amount
        levels_gained = 0

        totals = {}
        exp_needed = get_exp_needed_for_level(self.level)
        while self.experience >= exp_needed:
            self.experience -= exp_needed
            gains = self.level_up() or {}
            for key, value in gains.items():
                totals[key] = totals.get(key, 0) + value
            levels_gained += 1
            exp_needed = get_exp_needed_for_level(self.level)

        self.last_level_gains = totals
        return levels_gained
    
    def level_up(self):
        """Level up character. Does NOT reset experience - gain_experience()
        handles carrying over any leftover XP after subtracting the cost of
        this level, so overflow XP from a big reward isn't lost.

        Returns a dict of what was gained this level (core stat deltas, health/
        mana deltas, talent points) so the combat log can report it.
        """
        before = {
            "strength": self.strength, "stamina": self.stamina,
            "intellect": self.intellect, "spirit": self.spirit,
            "agility": self.agility,
            "health": self.health, "mana": self.mana,
        }

        self.level += 1

        # Core stats actually grow now. This never ran on level-up before, so
        # a level 60 character had the exact core stats of a level 1 one.
        self._apply_level_scaling()
        self._recalculate_derived_stats()
        self._refresh_ability_ranks()
        self._grant_talent_points()

        # PETS FROZE AT THEIR SUMMON LEVEL. sync_to_owner_level existed and
        # was called from exactly one place: the overworld screen's debug
        # "TEST: party +N levels" handler. Nothing in the real levelling path
        # touched it, so a Warlock who summoned an Imp at 20 and played to 60
        # still had a level-20 Imp with 346 health - stats, armour and
        # ability ranks all frozen at the moment of summoning. Every pet
        # class was affected, which is now eleven of them.
        #
        # Covers additional pets too (Tinker's turret, Necromancer's
        # minions), since all_pets includes them.
        for pet in self.all_pets:
            if hasattr(pet, "sync_to_owner_level"):
                pet.sync_to_owner_level()

        self.current_health = self.health
        self.current_mana = self.mana

        gains = {k: (getattr(self, k, None) if k not in ("health", "mana")
                     else getattr(self, k)) - v for k, v in before.items()}
        gains["talent_points"] = 1 if self.level >= 5 else 0
        return gains

    def spend_talent_point(self, tree_id, talent_id):
        """Put one point into a talent. Returns True if it went in.

        THE ONE PLACE A TALENT POINT IS SPENT. This rule used to live only inside
        ui/screens/talent_tree_screen.py's click handler, which meant the four things that have
        to happen together - the node gains a rank, the character loses a point, derived stats
        recalculate, and talent-granted abilities and procs re-sync - were only guaranteed to
        happen together when a human clicked. Anything else that wanted to spend a point (the
        recruit auto-spend below, a future preset build, a test) would have had to repeat all
        four, and the fifth caller to forget _sync_talent_unlocked_abilities would ship a
        companion whose talents were paid for but whose spells never appeared.

        Enforces the same three gates the screen enforced: the spec lock, the tier gate, and the
        node's own max rank.
        """
        if self.talent_points_available <= 0:
            return False
        if self.locked_spec and tree_id != self.locked_spec:
            return False
        tree = self.talent_trees.get(tree_id)
        if tree is None:
            return False
        node = tree.get_node(talent_id)
        if node is None or not node.can_spend_point():
            return False
        if not tree.can_spend_in_tier(node.tier, tree.total_points_spent()):
            return False

        node.spend_point()
        self.talent_points_available -= 1
        self._recalculate_derived_stats()
        self._sync_talent_unlocked_abilities()
        self._sync_talent_procs()
        return True

    def auto_spend_talents(self, tree_id=None):
        """Spend every available point down one tree. Returns how many went in.

        For companions who arrive already levelled. A recruit caught up from 20 to 46 gets 42
        points and an empty tree, and an empty tree on a level 46 healer is not a blank slate -
        it is a level 46 healer missing two thirds of their healing. Nobody is going to sit in
        the talent screen clicking forty-two times for a hireling, so they turn up built.

        Nothing is lost by doing this: Kyle's free talent reset refunds the lot, so a player who
        dislikes the build gets the points back and spends them by hand.

        Order is lowest tier first, and each node is filled to its max before moving on. That is
        not an aesthetic choice - tier gates are cumulative point counts, so spending depth-first
        from the bottom is what unlocks the tiers above. Spreading one point per node would stall
        against the first gate with points left over.
        """
        tree_id = tree_id or self.locked_spec
        if not tree_id:
            # No locked spec (a player character): pick the tree they have already invested in,
            # and the first one only if they have invested nowhere.
            trees = sorted(self.talent_trees.items(),
                           key=lambda kv: (-kv[1].total_points_spent(), kv[0]))
            if not trees:
                return 0
            tree_id = trees[0][0]
        tree = self.talent_trees.get(tree_id)
        if tree is None:
            return 0

        spent = 0
        # Bounded by the points themselves rather than by `while True`: a tier gate that can
        # never be met (an authoring error in a tree) would otherwise spin forever on a
        # background load screen with nothing to show for it.
        guard = self.talent_points_available + 1
        while self.talent_points_available > 0 and guard > 0:
            guard -= 1
            placed = False
            for tier in range(0, tree.get_max_tier() + 1):
                if not tree.can_spend_in_tier(tier, tree.total_points_spent()):
                    continue
                for node in tree.get_nodes_in_tier(tier):
                    if node.can_spend_point() and self.spend_talent_point(tree_id, node.talent_id):
                        spent += 1
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                # Every reachable node is maxed and no gate will open. Leftover points stay
                # available rather than being silently dropped.
                break
        return spent

    def _grant_talent_points(self):
        """Keep talent points in sync with level: 1 per level from level 5 on.

        Points available = (level - 4) minus whatever is already spent across
        every tree. Derived rather than incremented so it can never drift out
        of sync with the trees, and so it self-corrects on load.
        """
        if self.level < 5:
            self.talent_points_available = 0
            return
        spent = sum(tree.total_points_spent()
                    for tree in self.talent_trees.values())
        self.talent_points_available = max(0, (self.level - 4) - spent)

    def _sync_talent_procs(self):
        """Apply/remove a permanent synthetic StatusEffect for every talent
        node that carries a `proc` payload (see TalentNode.proc), based on
        whether it currently has points_spent > 0.

        Mirrors _sync_talent_unlocked_abilities' exact pattern (same call
        sites: creation/level-up/load, plus talent_tree_screen.py's
        spend/refund handlers) - talents that grant reactive behavior
        (Seal of Command, Earth Shield's real proc-heal, Blade Twisting,
        Shamanistic Rage's mana-return, Sudden Death, Fingers of Frost)
        need this because get_talent_effects()'s pure numeric-summing
        model has no way to express "do something when X happens," only
        "add Y to stat Z" - see TalentNode.proc's docstring.

        Uses a deterministic effect_id (talent_proc_<talent_id>) so
        apply_status_effect's existing refresh-in-place-by-id behavior
        naturally handles "already applied, still spent" as a no-op
        refresh rather than stacking duplicates, and so removal here only
        ever touches the ONE synthetic effect this exact talent node
        owns - never a real cast-sourced buff, even one with a similar
        name (e.g. Seal of Command's proc-buff is separate from Seal of
        Righteousness's if a Paladin somehow had both talented, since
        their talent_ids differ).

        Applied as effect_type=BUFF, duration effectively permanent
        (matches how raid-scope buffs already work - real_time_seconds=
        None means it doesn't decay on its own; only removed here when
        points_spent drops to 0), stat_mods={} (any REAL stat contribution
        from this same talent already flows through get_talent_effects()
        and _recalculate_derived_stats() as normal - this synthetic
        effect exists ONLY to carry the proc, not to double up on stats).
        """
        from combat.status_effects import StatusEffect, EffectType

        for tree in getattr(self, "talent_trees", {}).values():
            for node in tree.nodes.values() if hasattr(tree, "nodes") else []:
                proc = getattr(node, "proc", None)
                if not proc:
                    continue
                synthetic_id = f"talent_proc_{node.talent_id}"
                if node.points_spent > 0:
                    # Rank-scaled chance (new): every proc-carrying talent
                    # node before Venomancer's Venomous Retort was
                    # max_points=1 (Fingers of Frost, Blade Twisting,
                    # Sudden Death - a single on/off point, no rank curve
                    # to speak of), so this never previously mattered.
                    # Retort's real tooltip is "3% chance PER RANK" across
                    # 3 ranks (3/6/9%) - without this, _sync_talent_procs
                    # would apply the proc dict's authored chance verbatim
                    # regardless of rank, silently granting the FULL
                    # multi-rank value off a single spent point. Scales
                    # proc["chance"] by points_spent the same way
                    # TalentNode.get_effective_effects already scales
                    # ordinary numeric effects by rank (effects are
                    # authored PER RANK, not pre-summed) - a copy of the
                    # dict, not a mutation of the authored data, so
                    # unspending/respending ranks always recomputes from
                    # the same per-rank base rather than compounding.
                    effective_proc = proc
                    if "chance" in proc and node.max_points > 1:
                        effective_proc = dict(proc)
                        effective_proc["chance"] = min(100, proc["chance"] * node.points_spent)

                    # DROP ANY EXISTING COPY FIRST. Without this, the
                    # rank-scaled chance computed just above never actually
                    # reached the character: apply_status_effect() keeps the
                    # effect already carrying this effect_id, so the
                    # synthetic proc created when the FIRST point was spent
                    # survived every later point, frozen at its rank-1
                    # chance for the rest of the game.
                    #
                    # That made the scaling code above dead on arrival and
                    # silently broke EVERY multi-rank proc talent in the
                    # project. Measured on a level-60 Holy Paladin with 5/5
                    # Illumination: the node reported points_spent=5 while
                    # its synthetic effect still carried chance=20, and the
                    # talent fired on 3 of 20 guaranteed-crit heals instead
                    # of all 20.
                    #
                    # It went unnoticed because the bug is invisible from
                    # the data side - audit_talents, qa_proc_stat_mods and
                    # probe --audit-all all inspect authored values, and the
                    # authored value was correct. Only spending real points
                    # on a real character and reading the resulting effect
                    # shows it.
                    self.active_effects = [
                        e for e in self._effects() if e.effect_id != synthetic_id
                    ]
                    effect = StatusEffect(
                        effect_id=synthetic_id, name=node.name,
                        effect_type=EffectType.BUFF, duration=999999,
                        stat_mods={}, source_name=node.name,
                        real_time_seconds=None,
                        proc=effective_proc,
                    )
                    self.apply_status_effect(effect)
                else:
                    self.active_effects = [
                        e for e in self._effects() if e.effect_id != synthetic_id
                    ]

    def _refresh_ability_ranks(self):
        """Unlock the correct rank of every ability for self.level. Called on
        character creation, level-up, prestige reset, and after loading a
        save (so an old save doesn't stay stuck on a stale rank)."""
        self._sync_talent_unlocked_abilities()
        self._sync_talent_procs()
        self._sync_cryo_converted_abilities()
        self._grant_free_training()
        for ability in self.ability_book.get_all_abilities():
            trained = None
            if self.training_enabled and getattr(ability, "trainable", False):
                trained = self.trained_ranks.get(ability.ability_id, 0)
            ability.refresh_rank_for_level(self.level, trained)
        self._autofill_hotbar()

    #: Ranks whose level requirement is at or below this are taught for free the moment you qualify (the starter kit).
    FREE_TRAINING_LEVEL = 3

    def _grant_free_training(self):
        """Starter abilities need no trainer: every rank at level <= FREE_TRAINING_LEVEL is trained automatically once the
        character's level allows it.  No-op for characters that don't use trainers."""
        if not self.training_enabled:
            return
        for ability in self.ability_book.get_all_abilities():
            if not getattr(ability, "trainable", False):
                continue
            for number, rank in enumerate(ability.ranks, start=1):
                if rank["level_req"] <= self.FREE_TRAINING_LEVEL and self.level >= rank["level_req"]:
                    if self.trained_ranks.get(ability.ability_id, 0) < number:
                        self.trained_ranks[ability.ability_id] = number

    def enable_training(self, grandfather=False):
        """Turn class trainers on for this character.  grandfather=True (old saves) marks every rank the character already
        qualifies for as trained, so nobody loses a spell they could cast yesterday."""
        self.training_enabled = True
        if grandfather:
            for ability in self.ability_book.get_all_abilities():
                if not getattr(ability, "trainable", False):
                    continue
                best = 0
                for number, rank in enumerate(ability.ranks, start=1):
                    if self.level >= rank["level_req"]:
                        best = number
                if best:
                    self.trained_ranks[ability.ability_id] = max(self.trained_ranks.get(ability.ability_id, 0), best)
        self._refresh_ability_ranks()

    def train_ability(self, ability_id, rank_number):
        """Record that `rank_number` of an ability was bought, then re-resolve ranks (the new spell is auto-slotted)."""
        if rank_number > self.trained_ranks.get(ability_id, 0):
            self.trained_ranks[ability_id] = rank_number
        self._refresh_ability_ranks()

    def _sync_cryo_converted_abilities(self):
        """Set cryo_converted=True on Frostbolt/Ice Lance once the matching
        Cryobolt/Cryolance talent (Mage/Cryotherapist tree) has a point
        spent, per Kyle: "the actual Frostbolt/Ice Lance just also heals" -
        no new hotbar button, the existing spell's behavior changes.

        Mirrors _sync_talent_unlocked_abilities immediately above (same
        "flag read from get_talent_effects(), applied to a specific ability
        by id" shape) rather than reusing unlock_ability - unlock_ability
        means "this ability doesn't exist in the book until talented",
        which is wrong here since Frostbolt/Ice Lance are already learned
        from level alone. cryo_convert_frostbolt/cryo_convert_ice_lance are
        a separate, purpose-built effect key for exactly this "mutate an
        already-known ability's behavior" case, not read by anything else.

        Called from the same place and same reasoning as
        _sync_talent_unlocked_abilities: creation/level-up/load, plus
        talent_tree_screen.py's spend/refund handlers.
        """
        effects = self.get_talent_effects()
        frostbolt_on = bool(effects.get("cryo_convert_frostbolt"))
        ice_lance_on = bool(effects.get("cryo_convert_ice_lance"))
        for ability in self.ability_book.get_all_abilities():
            if ability.ability_id == "mage_frostbolt":
                ability.cryo_converted = frostbolt_on
            elif ability.ability_id == "mage_ice_lance":
                ability.cryo_converted = ice_lance_on

    def _sync_talent_unlocked_abilities(self):
        """Set talent_unlocked on every ability that has requires_talent=True,
        based on the character's currently-spent talent points.

        THE ACTUAL FEATURE THIS ADDS: WOTLK talent trees don't just buff
        existing abilities - some talents grant entirely new spells (Wild
        Growth, Nourish, Chimera Shot) that don't exist for the character
        until that talent has at least 1 point spent. The read side of
        this already existed (get_talent_unlocked_abilities() correctly
        aggregates every "unlock_ability" effect across all trees into a
        flat list of ability_ids) but nothing ever called it and applied
        the result to the ability book - so a talent could claim to grant
        an ability and nothing would happen. This is that missing write
        side: for every ability flagged requires_talent=True, check
        whether its own ability_id appears in that unlocked list.

        Must run BEFORE refresh_rank_for_level() in _refresh_ability_ranks
        (see above) since is_learned there is level_met AND
        talent_unlocked - if this ran after, a freshly-unlocked talent
        ability would still show as unlearned until the NEXT refresh.

        Called here (creation/level-up/load) and also directly from
        talent_tree_screen.py's spend/refund handlers, matching the
        existing pattern there of calling _recalculate_derived_stats()
        immediately after every point change rather than waiting for the
        next level-up to notice.
        """
        unlocked_ids = set(self.get_talent_unlocked_abilities())
        newly = False
        # Any ability that one of this character's talent nodes grants ("unlock_ability") is talent-gated, whether or not
        # its data row carries requires_talent (189 of 273 granted abilities were missing the flag, so Golem Form was
        # known from level 8 without the talent).  The talent tree is the source of truth.
        granted_ids = set()
        for tree in getattr(self, "talent_trees", {}).values():
            for node in (tree.nodes.values() if hasattr(tree, "nodes") else []):
                u = (getattr(node, "effects", None) or {}).get("unlock_ability")
                if isinstance(u, str):
                    granted_ids.add(u)
                elif isinstance(u, (list, tuple)):
                    granted_ids.update(u)
        for ability in self.ability_book.get_all_abilities():
            if ability.ability_id in granted_ids:
                ability.requires_talent = True
            if not ability.requires_talent:
                continue  # no talent gate on this ability - never touched here
            was = getattr(ability, "is_learned", True)
            ability.talent_unlocked = ability.ability_id in unlocked_ids
            # Re-derive is_learned right away.  Spending a point only flipped talent_unlocked, and is_learned was only
            # recomputed on the next level-up/load, so a freshly taken talent did not teach its spell until then.
            ability.refresh_rank_for_level(self.level)
            if ability.is_learned and not was:
                newly = True
        if newly:
            self._autofill_hotbar()
        else:
            # Refunding a talent point revokes its ability, and the bar has
            # to follow - otherwise the slot sits there failing to fire.
            # _autofill_hotbar() prunes too, but it only runs here when
            # something was newly LEARNED, so a pure revoke (or the
            # creation-time window described in _prune_unlearned_hotbar)
            # would otherwise leave the stale slot until the next level-up.
            self._prune_unlearned_hotbar()

    def _prune_unlearned_hotbar(self):
        """Clear any hotbar/extra slot holding an ability this character has
        not actually learned.

        THE BUG THIS FIXES (Kyle: "i played venomancer and started with
        abilities i shouldnt have? like wilt"): a talent-granted ability
        could end up permanently stuck on the action bar from character
        creation onward.

        `requires_talent` is derived from the talent trees at runtime, not
        read from the ability rows - 193 of the 279 granted abilities never
        carried the flag in their data, so the tree is the only source of
        truth (see _sync_talent_unlocked_abilities). But __init__ calls
        _refresh_ability_ranks() BEFORE it assigns self.talent_trees, so
        during that window every one of those 193 looked untalented:
        requires_talent stayed False, is_learned came out as plain
        level_met, and the _autofill_hotbar() at the end of that same
        refresh slotted them and recorded them in hotbar_autofilled_ids -
        which is deliberately permanent, so that a deliberate removal
        sticks. Once the trees loaded, requires_talent flipped to True and
        is_learned to False, but the bar entry and the memo both survived.
        A fresh level 1 Venomancer therefore started with Blight Antidote
        and Decay on the bar, and a level 20 one with six abilities it had
        spent no points on.

        Pruning is safe rather than destructive: nothing can legitimately
        put an unlearned ability on the bar, because the Skills screen
        lists only get_learned_abilities(). So an unlearned id in a slot is
        always this artifact. It is also self-healing for saves already
        carrying the ghosts, which is the only way to fix Kyle's existing
        character short of a migration.

        Only ids the ability book actually knows are touched - anything
        else in a slot belongs to a system this method should not be
        second-guessing.

        Dropping the id from hotbar_autofilled_ids too is the point: the
        memo exists to record "the player has had their say about this
        ability," and a slot the player never chose is not that. Clearing
        it means the ability gets autofilled properly on the day it is
        really learned - take the Wilt talent and Wilt appears then, which
        is what the memo should have been recording all along.
        """
        if not hasattr(self, "hotbar"):
            return
        known = {a.ability_id for a in self.ability_book.get_all_abilities()}
        learned = {a.ability_id for a in self.get_learned_abilities()}
        for slots in (self.hotbar, getattr(self, "extra_slots", None) or []):
            for i, aid in enumerate(slots):
                if aid and aid in known and aid not in learned:
                    slots[i] = None
                    if hasattr(self, "hotbar_autofilled_ids"):
                        self.hotbar_autofilled_ids.discard(aid)

    def get_learned_abilities(self):
        """Every ability this character has actually reached the level
        requirement for, in book order."""
        return [a for a in self.ability_book.get_all_abilities()
                if getattr(a, "is_learned", True)]

    def _autofill_hotbar(self):
        """Place newly-learned abilities into the first free hotbar slots,
        exactly once per ability ever.

        The hotbar previously started completely empty and had to be filled
        by hand before the character could do anything, which was tolerable
        with 3 abilities per class and tedious with 9. This only ever fills
        EMPTY slots and never reorders what the player has arranged.

        Gated on self.hotbar_autofilled_ids (has this ability EVER been
        auto-placed), not on "is it currently in self.hotbar" - the latter
        made a manual removal temporary, since _refresh_ability_ranks runs
        on every level-up and would see the now-empty slot plus the
        ability "not currently slotted" and put it right back next level.
        Checking the seen-set instead means a deliberate removal (Kyle's
        case: unslotting Shoot/Wand when no matching weapon is equipped)
        sticks permanently - a level-up still auto-slots any ability
        that's newly learned and has never been placed before, but never
        re-adds one the player already made a call on.
        """
        if not hasattr(self, "hotbar"):
            return
        if not hasattr(self, "hotbar_autofilled_ids"):
            # Loading an older save from before this field existed - seed
            # it from whatever's currently slotted so existing bars don't
            # get instantly re-flooded with everything already learned.
            self.hotbar_autofilled_ids = {a for a in self.hotbar if a}
        self._prune_unlearned_hotbar()
        for ability in self.get_learned_abilities():
            if ability.ability_id in self.hotbar_autofilled_ids:
                continue
            for i in range(len(self.hotbar)):
                if self.hotbar[i] is None:
                    self.hotbar[i] = ability.ability_id
                    # Memo only what actually got PLACED. This add used to
                    # sit outside this loop, so an ability that found no
                    # free slot was still recorded as "the player has had
                    # their say about this one" - and never auto-slotted
                    # again even once space opened up. Harmless while the
                    # bar had room; not harmless alongside the
                    # creation-window bug in _prune_unlearned_hotbar, which
                    # filled all 20 slots with abilities the character had
                    # not learned and so memoed the genuinely learned ones
                    # out of ever appearing. Taking the Wilt talent now
                    # puts Wilt on the bar.
                    self.hotbar_autofilled_ids.add(ability.ability_id)
                    break
    
    def prestige(self):
        """Prestige: reset level, gain prestige level."""
        from config import PRESTIGE_LEVEL
        if self.level >= PRESTIGE_LEVEL:
            self.prestige_level += 1
            self.prestige_points += 1
            self.level = 1
            self.experience = 0
            # Re-derive core stats for level 1. Without this the character
            # kept their level-60 Strength/Stamina/etc. after prestiging,
            # since level scaling used to only ever run at creation.
            self._apply_level_scaling()
            self._recalculate_derived_stats()
            self._refresh_ability_ranks()
            self._grant_talent_points()
            self.current_health = self.health
            self.current_mana = self.mana
            return True
        return False
    
    # ------------------------------------------------------------------
    # Generic resource access
    # ------------------------------------------------------------------
    #: Resources backed by dedicated attributes: type -> (current, maximum).
    #: Everything else lives in self.secondary_resources.
    _RESOURCE_ATTRS = {
        "rage": ("current_rage", "max_rage"),
        "energy": ("current_energy", "max_energy"),
        "mana": ("current_mana", "mana"),
        "health": ("current_health", "health"),
    }

    #: Default ceiling for dict-backed secondary resources. Most of CoA's
    #: stacking resources (Static, Insanity, Deathfire, ...) are 0-100
    #: scales - but NOT all of them. Per-resource overrides below take
    #: priority over this default for anything that isn't actually 0-100.
    SECONDARY_RESOURCE_MAX = 100

    #: Per-resource cap overrides for dict-backed secondary resources whose
    #: real max isn't the 0-100 default. Solar Power (Sun Cleric) is a real
    #: 0-20 scale per Kyle's correction - it was silently capping at 100
    #: before this existed, letting Solar Power-spending abilities be gated
    #: at 5x their intended threshold.
    SECONDARY_RESOURCE_MAX_OVERRIDE = {
        "solar_power": 20,
        # Runemaster's own documented design (see ResourceType.RUNES in
        # combat/abilities.py: "up to 4 stored, cycles Frost/Fire/Arcane")
        # was silently falling through to the generic 0-100 default before
        # this existed - Glyphic Ruin/Thaumaturgy only cost 1 Rune each, so
        # against an uncapped-in-practice 100 pool the class never felt
        # the tight "bank a few, spend carefully" resource tension it was
        # designed around. 4 matches the documented intent exactly.
        "runes": 4,
    }

    #: Secondary resources that bleed away outside combat, and how fast per
    #: overworld step. Static behaves like Rage: built in a fight, gone by
    #: the next one, so you can't walk around permanently charged.
    SECONDARY_DECAY_PER_STEP = {"static": 2}

    @staticmethod
    def _resource_key(resource_type):
        """Accept either a ResourceType enum or its plain string value."""
        return getattr(resource_type, "value", resource_type)

    def get_resource(self, resource_type):
        """Current amount of any resource, dedicated-attribute or dict-backed."""
        key = self._resource_key(resource_type)
        if key in self._RESOURCE_ATTRS:
            return getattr(self, self._RESOURCE_ATTRS[key][0], 0)
        return self.secondary_resources.get(key, 0)

    def get_resource_max(self, resource_type):
        """Maximum for any resource, including talent bonuses.

        `<resource>_max` lets a talent raise a secondary resource pool -
        static_max for Stormbringer, energy_max for Venomancer. Five talents
        were authored on these and none were read, so "Increases maximum
        Static by 10 per rank" did nothing. Handled generically off the
        resource key rather than per-resource, so any future pool gets it
        for free.

        Only applied to SECONDARY resources. The primary pools (health, mana,
        rage, energy as a class resource) have their own derived-stat paths
        with max_health_pct / max_mana_pct, and adding a second source here
        would double-count them.
        """
        key = self._resource_key(resource_type)
        if key in self._RESOURCE_ATTRS:
            return getattr(self, self._RESOURCE_ATTRS[key][1], 0)
        base = self.SECONDARY_RESOURCE_MAX_OVERRIDE.get(key, self.SECONDARY_RESOURCE_MAX)
        bonus = 0
        if hasattr(self, "get_talent_effect"):
            bonus = self.get_talent_effect(f"{key}_max", 0) or 0
        return max(1, int(base + bonus))

    def set_resource(self, resource_type, amount):
        """Set a resource, clamped to [0, max]."""
        key = self._resource_key(resource_type)
        amount = max(0, min(self.get_resource_max(resource_type), amount))
        if key in self._RESOURCE_ATTRS:
            setattr(self, self._RESOURCE_ATTRS[key][0], amount)
        else:
            self.secondary_resources[key] = amount
        return amount

    def gain_resource(self, resource_type, amount):
        """Add to a resource. Returns the amount actually gained (after cap)."""
        before = self.get_resource(resource_type)
        after = self.set_resource(resource_type, before + amount)
        return after - before

    def spend_resource(self, resource_type, amount):
        """Deduct from a resource. Returns False if there wasn't enough."""
        if self.get_resource(resource_type) < amount:
            return False
        self.set_resource(resource_type, self.get_resource(resource_type) - amount)
        return True

    def get_secondary_resource_type(self):
        """This class's secondary ResourceType, or None."""
        from combat.abilities import get_class_secondary_resource
        return get_class_secondary_resource(self.char_class)

    def get_stat_contributions(self, stat_name):
        """
        Human-readable list of what one core stat currently feeds into, for
        character-sheet hover tooltips.

        Derived from the SAME coefficients used in _recalculate_derived_stats.
        If you change a formula there, change it here - these are deliberately
        written as "per point" values so they stay readable, and the totals
        shown come from the live derived stats rather than being recomputed.
        """
        from combat.abilities import get_class_resource, ResourceType
        is_mana = get_class_resource(self.char_class, self) == ResourceType.MANA

        stat_name = stat_name.lower()
        if stat_name == "strength":
            return [
                "+2 Attack Power per point",
                "+0.3% Block per point",
                "+0.1% Parry per point",
            ]
        if stat_name == "stamina":
            return [
                "+8 Max Health per point",
                "+2 Armor per point",
                f"Armor {self.armor} = {self.get_physical_reduction_percent():.1f}% phys reduction",
            ]
        if stat_name == "intellect":
            lines = [
                "+0.2 Spell Power per point",
                "+0.2 Healing Power per point",
                "+0.5% Spell Crit per point",
                "+0.1% Haste per point",
            ]
            if is_mana:
                lines.insert(0, "+15 Max Mana per point")
            return lines
        if stat_name == "spirit":
            lines = [
                "+0.2 Healing Power per point",
                "+2 Magic Resistance per point",
                f"MR {self.magic_resistance} = {self.get_magic_reduction_percent():.1f}% magic reduction",
            ]
            if is_mana:
                lines.insert(0, "+0.5 Mana regen per turn/step")
                lines.insert(1, "+5 Max Mana per point")
            return lines
        if stat_name == "agility":
            return [
                "+0.5 Attack Power per point",
                "+2 Ranged Attack Power per point",
                "+0.5% Physical Crit per point",
                "+0.25% Dodge per point",
                "+0.1% Parry per point",
                "+0.1% Haste per point",
                "+1% Turn Speed per point",
            ]
        return []

    #: Dodge every class has before agility, talents or gear. See _recalculate_derived_stats.
    BASE_DODGE = 5.0

    #: Block chance a shield gives before any talent. Classic gave 5% for carrying one.
    BASE_BLOCK_CHANCE = 5.0

    #: Block chance cannot exceed this. Dodge and parry avoid the hit outright, so an uncapped
    #: block chance on top of them left three tanks with no physical hit ever landing unreduced.
    BLOCK_CHANCE_CAP = 50.0

    #: DIMINISHING RETURNS ON AVOIDANCE. Dodge and parry had none, which is a
    #: systemic hole rather than a tuning question: every point from a talent
    #: or a gear suffix was worth exactly as much as the first, so the way to
    #: build any tank was to stack one stat until nothing could touch it.
    #: Primalist Mountain King reached 28% dodge and 28% parry and survived
    #: 692 turns in the role sim where its eight peers survived 6 to 16.
    #:
    #: Applied to the BONUS portion only - talents, gear, defense rating -
    #: and never to the base-stat-derived part (BASE_DODGE plus the Agility
    #: and Str/Agi terms). That matters: a Rogue already carries 24% dodge
    #: and 14% parry naked at 60 from stats alone, so running the whole
    #: number through a curve would quietly restate every class's baseline,
    #: which is a balance pass Kyle has explicitly deferred ("we can fine
    #: tune later too based on end game gear too"). Curving only what gets
    #: ADDED leaves all 30 classes' unspecced avoidance exactly where it
    #: was and changes only the thing that was broken - stacking.
    #:
    #: The curve is hyperbolic: effective = bonus / (1 + bonus / K). It is
    #: near-linear while the bonus is small relative to K, so an early
    #: talent still feels like it did something, and it flattens hard after
    #: that. At K = 40: +5 gives 4.4, +15 gives 10.9, +30 gives 17.1,
    #: +60 gives 24.0. Nothing is ever lost outright, which keeps a talent
    #: from reading as literally worthless, but the tenth point in a row
    #: buys a fraction of what the first did.
    AVOIDANCE_DR_K = 40.0

    #: Dodge and parry together cannot exceed this. The DR curve alone still
    #: has an asymptote of K (40 each, 80 combined on top of base), and
    #: dodge and parry both negate a hit outright, so without a joint
    #: ceiling a stacked tank can still converge on never being hit. Block
    #: is excluded because it only reduces a hit by 30% rather than erasing
    #: it, and it already has its own cap above. 60% leaves two in five
    #: attacks landing on even the most avoidance-stacked build, which is
    #: roughly where a well-geared Classic tank sat.
    AVOIDANCE_COMBINED_CAP = 60.0

    @classmethod
    def _diminish(cls, bonus):
        """Hyperbolic DR for an avoidance bonus. See AVOIDANCE_DR_K.

        Negative bonuses (a debuff) pass through untouched - diminishing a
        penalty would turn a dodge-reduction debuff into a weaker debuff the
        more it was applied, which is backwards.
        """
        if bonus <= 0:
            return bonus
        return bonus / (1.0 + bonus / cls.AVOIDANCE_DR_K)

    #: Armor/resistance curve: reduction = rating / (rating + BASE + PER_LEVEL * attacker_level).
    #:
    #: THE DENOMINATOR HAS TO SCALE WITH THE ATTACKER OR ARMOUR RUNS AWAY. This was a flat 100,
    #: which meant reduction only ever climbed as gear improved: a plate wearer reached 88% by
    #: level 20, 94% by 40 and 96% by 60, so physical damage stopped existing. Measured against a
    #: geared level-40 character, every melee creature in the game did 3 to 10 damage a turn - 83
    #: to 265 turns to kill somebody - while caster creatures, whose damage armour does not touch,
    #: did 116 to 195. That is the whole reason caster mobs were unbeatable and melee mobs were
    #: harmless, and no amount of class tuning could have fixed it.
    #:
    #: THESE TWO NUMBERS ARE FITTED TO FRONTIER'S OWN ARMOUR VALUES, not copied from WoW. WoW uses
    #: 400 + 85 per level, but its plate wearers carry four to six thousand armour at 60 where
    #: Frontier's carry about 2300, so WoW's constants would leave Frontier plate at 29%. Fitted
    #: instead so the curve lands where it should at every level:
    #:
    #:     level 20   plate ~46%   cloth ~17%
    #:     level 40   plate ~49%   cloth ~18%
    #:     level 60   plate ~50%   cloth ~20%
    #:
    #: Flat across levels is the point. Armour class stays a real difference - a plate wearer takes
    #: a bit over half what a cloth wearer takes from a sword - without either becoming immune.
    MITIGATION_BASE = 200
    MITIGATION_PER_LEVEL = 35

    #: Kept because saves, tooltips and tests referenced it. Not used by the curve any more.
    MITIGATION_CONSTANT = 100

    #: RESISTANCE IS NOT ARMOUR AND MUST NOT SHARE ARMOUR'S CURVE.
    #:
    #: Every resistance in the game - magic_resistance and all six schools,
    #: on characters, monsters and pets - used to run through
    #: mitigation_from, whose denominator is 200 + 35*level = 2300 at 60.
    #: That made a resistance rating of 100 worth 4.2% reduction at level
    #: 60, so resistance was decorative: you would need a four-digit rating
    #: before a fire elemental noticeably shrugged off a Fireball, and no
    #: creature or item in the game carries one. tools/sim_class_balance
    #: has been reporting the symptom for a while - "armour climbs with
    #: gear forever while magic resistance stays at zero".
    #:
    #: Resistance is a SMALL, FLAT, LEGIBLE scale instead - Kyle's spec:
    #: "we don't really want resistances to be super high. I'm thinking
    #: the highest a caster will ever need is like 60 spell pen. Where
    #: 1 spell pen = 1 resistance removed. So highest an enemy can have
    #: is 60 resistance."
    #:
    #: So: 0-60 points, half a percent each, 30% at the cap.
    #:
    #:     resistance 15 ->  7.5%      resistance 45 -> 22.5%
    #:     resistance 30 -> 15.0%      resistance 60 -> 30.0%  (cap)
    #:
    #: and 60 spell penetration cancels the worst of it outright, which is
    #: the whole point of the stat having a reachable ceiling.
    #:
    #: DELIBERATELY NOT LEVEL-SCALED, unlike armour. A flame elemental
    #: should shrug off the same share of a Fireball at level 12 as at
    #: level 60 - its nature does not change - and a 0-60 scale that got
    #: multiplied by the monster level curve would mean nothing at the
    #: bottom and sit far past the cap at the top.
    RESIST_MAX = 60
    RESIST_PCT_PER_POINT = 0.005
    RESIST_CAP = RESIST_MAX * RESIST_PCT_PER_POINT   # 30%

    @classmethod
    def resist_mitigation_from(cls, rating, attacker_level=None):
        """Fraction of damage (0.0-RESIST_CAP) mitigated by a RESISTANCE
        rating - magic resistance or any of the six schools.

        Separate from mitigation_from, which is for armour. Both are the
        single source of truth for their own stat: Character, Monster and
        Pet all call these rather than carrying a second copy.

        attacker_level is accepted and ignored, for call-signature parity
        with mitigation_from - resistance does not scale with level, see
        the constants above.
        """
        rating = max(0, min(cls.RESIST_MAX, rating))
        return min(cls.RESIST_CAP, rating * cls.RESIST_PCT_PER_POINT)

    @classmethod
    def mitigation_from(cls, rating, attacker_level=None):
        """Fraction of damage (0.0-1.0) mitigated by an armor/resistance rating.

        Asymptotic: never reaches 100%, always diminishing returns. Single source of truth -
        take_damage(), Monster.take_damage(), Pet.take_damage() and the tooltips all call this.

        attacker_level scales the curve. A caller that genuinely does not know it (an item tooltip
        comparing two pieces of armour) may leave it out and gets the level-1 curve, which is the
        most generous reading - fine for "this piece is better than that piece", wrong for damage.
        Every damage path passes it.
        """
        rating = max(0, rating)
        denom = cls.MITIGATION_BASE + cls.MITIGATION_PER_LEVEL * max(1, int(attacker_level or 1))
        return rating / (rating + denom)

    def get_physical_reduction_percent(self):
        """Current physical damage reduction from Armor, as a percentage."""
        return self.mitigation_from(self.armor, self.level) * 100.0

    def get_magic_reduction_percent(self):
        """Current magic damage reduction from Magic Resistance, as a percentage."""
        return self.resist_mitigation_from(self.magic_resistance, self.level) * 100.0

    def get_resistance(self, school):
        """Real per-school resistance rating lookup - the single place
        take_damage (and any tooltip/UI wanting to show a resistance
        value) should go for a school's resistance, rather than reading
        the fire_resistance/frost_resistance/... attributes directly.

        school: a DamageSchool constant (combat/status_effects.py) - a
        single string ("fire", "frost", ...) or a tuple of two for a
        combined/hybrid school (e.g. ("shadow", "frost") for
        Shadowfrost). PHYSICAL and MAGIC are NOT handled here - those
        stay on the existing armor/magic_resistance stats and
        take_damage's existing physical/magic branches, unchanged from
        before this system existed.

        Combined schools resolve to whichever component resistance is
        LOWEST (Kyle's explicit call: a combined-school hit should be
        harder to resist than either component alone, since hybrid
        damage types are meant to be rare/exotic, not a defensive
        loophole where a defender picks their best resist).

        Returns 0 for PHYSICAL/MAGIC/an unrecognized school string,
        rather than raising - a typo'd or not-yet-modeled school
        gracefully falls back to "no resistance" instead of crashing
        mid-combat.
        """
        if isinstance(school, (tuple, list)):
            return min(self.get_resistance(s) for s in school) if school else 0

        return {
            "fire": self.fire_resistance,
            "frost": self.frost_resistance,
            "nature": self.nature_resistance,
            "shadow": self.shadow_resistance,
            "arcane": self.arcane_resistance,
            "holy": self.holy_resistance,
        }.get(school, 0)

    def get_effective_spell_power(self, school):
        """Real per-school spell power lookup - the single place every
        damage-calculation call site should go for "how much spell power
        applies to THIS cast" instead of reading self.spell_power
        directly. Previously every school (Fire, Frost, Arcane, ...)
        secretly used the exact same generic spell_power stat - gear
        suffixes like "of Fiery Wrath" (pure Fire Spell Power, see
        data/items/gear_suffixes.json) rolled a real stat that then did
        nothing in combat, since nothing read fire_spell_power at all.

        Returns generic spell_power PLUS whichever per-school bonus
        applies - additive, not either/or, so a caster who stacks both
        generic spell power (int_caster gear) and school-specific power
        (Fire Wrath suffixes) gets the benefit of both, matching how real
        WoW itemization layers "+Spell Power" and "+Fire Spell Power"
        together rather than one overriding the other.

        school: a DamageSchool constant - single string or a tuple for a
        combined school (e.g. ("shadow","frost") for Shadowfrost), same
        calling convention as get_resistance(). A combined school AVERAGES
        its two component per-school powers (not min(), unlike
        get_resistance's deliberate min() for defender-favors-nothing) -
        an attacker's own hybrid itemization should get real, proportional
        benefit from both schools they invested in, not be capped by
        whichever they invested in less. PHYSICAL/MAGIC/unrecognized
        schools return just the generic spell_power (no per-school
        component exists for either).
        """
        if isinstance(school, (tuple, list)):
            if not school:
                return self.spell_power
            per_school_avg = sum(self._per_school_spell_power(s) for s in school) / len(school)
            return self.spell_power + per_school_avg

        return self.spell_power + self._per_school_spell_power(school)

    def _per_school_spell_power(self, school):
        """Just the per-school COMPONENT (not including generic
        spell_power) - split out so get_effective_spell_power can average
        components for a combined school without double-counting the
        generic spell_power term in the average."""
        return {
            "fire": self.fire_spell_power,
            "frost": self.frost_spell_power,
            "nature": self.nature_spell_power,
            "shadow": self.shadow_spell_power,
            "arcane": self.arcane_spell_power,
            "holy": self.holy_spell_power,
        }.get(school, 0)

    def get_resistance_percent(self, school):
        """Resistance for `school`, expressed as a mitigation percentage
        (0-100) through the same asymptotic curve as
        get_physical_reduction_percent/get_magic_reduction_percent -
        for tooltips/character-sheet display."""
        return self.resist_mitigation_from(self.get_resistance(school), self.level) * 100.0

    def _fire_avoidance_procs(self, triggers, attacker=None):
        """Fire ON_DODGE / ON_PARRY / ON_AVOID / ON_BLOCK and queue the text.

        Separate from take_damage's own ON_DAMAGE_TAKEN block because a dodge
        and a parry RETURN 0 immediately - they never reach it - so the
        messages have to be queued here or they are lost. Queued onto
        _pending_proc_messages exactly like the damage-taken path, which
        CombatEngine._apply_effect drains after every take_damage call;
        Character owns no combat log of its own.

        `attacker` is passed through as the proc's "target" so a retaliation
        on avoidance has something to hit back - Moon Guard's Moonflares
        ("Avoiding melee attacks will call down a Moonflare at the attacker")
        and Guardian's Retaliation ("blocks strike back") both need it, and a
        caller that has no attacker simply gets no retaliation, same as the
        damage-taken path.
        """
        if not hasattr(self, "fire_proc_trigger"):
            return
        for trigger in triggers:
            msgs = self.fire_proc_trigger(trigger, {"amount": 0, "target": attacker})
            if not msgs:
                continue
            pending = getattr(self, "_pending_proc_messages", None)
            if pending is None:
                pending = []
                self._pending_proc_messages = pending
            pending.extend(msgs)

    def take_damage(self, amount, damage_type="physical", attacker_level=None, attacker=None):
        """Take damage with resistance.

        attacker_level (optional): the level of whatever dealt this damage.
        When provided, applies the symmetric level-difference multiplier so
        a big level gap either direction actually matters (see
        combat/abilities.py level_diff_multiplier) - a level 25 mob should
        flatten a level 5 player, not trade evenly with them.

        AVOIDANCE (Dodge/Parry/Block): rolled here, defender-side, as a
        second independent check AFTER the attacker's own hit/miss roll
        already passed (see combat/abilities.py's hit_chance_physical roll,
        which happens before take_damage is ever called) - matches real
        WoW's two-stage resolution (did it land at all, then did the
        defender avoid it) rather than folding avoidance into the
        attacker's hit chance. Only applies to damage_type="physical":
        Dodge/Parry/Block have never been magic-damage mechanics in WoW,
        and this engine has no equivalent caster-side avoidance stat to
        roll against spell damage. Order matches real WoW's own combat
        table priority (dodge/parry checked before block - a Dodge/Parry
        fully avoids the attack, so Block never gets a chance to apply on
        top of one): Dodge and Parry each independently roll to negate the
        hit entirely (return 0 damage, same shape as a miss); Block rolls
        only if neither of those procs, and reduces (not negates) the
        incoming amount by SUBTRACTING self.block_value - stacked with
        block_bonus_reduction, the "reduce damage taken by blocked
        attacks" pool Spirit Guard talents contribute to (see
        get_talent_effect("block_bonus_reduction")).

        That sentence used to say a block reduces the hit by a flat 30%
        via a BLOCK_DAMAGE_REDUCTION constant. It no longer does - the
        constant was left declared but read by nothing after the switch to
        subtracting block_value (which is the fix that made every
        block_value talent and every bigger shield matter at all). A
        comment describing behaviour the code has stopped having is how
        today's per-key unit convention got documented backwards, so it is
        corrected rather than left as a second plausible story.

        Consequence worth knowing, not a bug: block_value is FLAT and
        scales with Strength, shield and talents, so once it exceeds a
        post-mitigation hit the block absorbs the whole thing and `actual`
        floors at 1. Warrior Protection at 60 carries ~210 block value
        against ~90 post-mitigation trash hits, so it reads as physically
        immune to them. Real Classic behaves the same way against
        low-level mobs; whether this game's damage curve should outrun
        block value by 60 is a tuning question, deferred.

        Parry requires a
        melee weapon capable of parrying in real WoW (can't parry with a
        ranged/caster kit) - not modeled here since this engine has no
        such distinction on non-Warrior/Rogue/Paladin classes; every
        Character rolls the same three checks off its own dodge/parry/
        block stats regardless of class, same as every other avoidance
        stat already being class-agnostic here.
        """

        # Absorb shields (StatusEffect.absorb - see its docstring; Tinker's
        # Reactive Plating is the first real user) soak the RAW incoming
        # amount first, before dodge/parry/block/armor/resistance/%
        # reductions - a shield should block the full hit, not a hit
        # already discounted by every other defensive stat, and applies
        # to every damage_type (physical or any school), unlike avoidance
        # which is physical-only. Drains the oldest-applied shield(s)
        # first (list order = application order) until either the
        # incoming amount is fully absorbed or every shield is spent;
        # removes a shield outright once its pool hits 0 rather than
        # leaving a dead 0-absorb buff sitting active. A character with no
        # absorb shields active takes this whole block as a cheap no-op
        # loop over zero matching effects, identical to before this
        # existed.
        if hasattr(self, "_effects") and amount > 0:
            for effect in list(self._effects()):
                if amount <= 0:
                    break
                if getattr(effect, "absorb", 0) <= 0:
                    continue
                soaked = min(effect.absorb, amount)
                effect.absorb -= soaked
                amount -= soaked
                if effect.absorb <= 0:
                    self._effects().remove(effect)
            if amount <= 0:
                self._on_status_effects_changed()
                return 0

        if damage_type == "physical":
            import random
            roll = random.uniform(0, 100)
            if roll < self.dodge:
                self._fire_avoidance_procs(("on_dodge", "on_avoid"), attacker)
                return 0
            roll -= self.dodge
            if roll < self.parry:
                self._fire_avoidance_procs(("on_parry", "on_avoid"), attacker)
                return 0
            roll -= self.parry
            blocked = roll < self.block_chance
        else:
            blocked = False

        if damage_type == "physical":
            # Armor penetration, finally consumed. The attacker's
            # armor_penetration (flat) and armor_penetration_pct (fraction)
            # ignore part of this defender's Armor before mitigation is
            # computed, which is what both stats have always claimed to do.
            #
            # They were computed as real derived stats and read by NOTHING,
            # so Tinker's Piercing Augmentation and Round Armor Pen - the
            # spec's whole premise - did nothing, and so did every gear roll
            # of the stat. The old comment here said threading the attacker
            # through take_damage and every call site was too invasive to do
            # safely; that is no longer true, because `attacker` is already a
            # parameter and every damage call site in abilities.py already
            # passes attacker=caster.
            effective_armor = self.armor
            if attacker is not None:
                flat = getattr(attacker, "armor_penetration", 0) or 0
                pct = getattr(attacker, "armor_penetration_pct", 0.0) or 0.0
                # Percentage first, then flat, and never below zero: a
                # defender cannot be pushed into negative Armor and start
                # taking bonus damage from penetration alone.
                effective_armor = max(0, int(effective_armor * (1.0 - min(1.0, pct)) - flat))
            reduction = self.mitigation_from(effective_armor, attacker_level)
        elif damage_type == "magic":
            # spell_penetration is the magic-side counterpart, and was equally
            # inert. Same ordering and same floor.
            effective_resist = self.magic_resistance
            if attacker is not None:
                effective_resist = max(0, int(effective_resist
                                              - (getattr(attacker, "spell_penetration", 0) or 0)))
            reduction = self.resist_mitigation_from(effective_resist, attacker_level)
        elif damage_type in DamageSchool.ALL_SCHOOLS or isinstance(damage_type, (tuple, list)):
            # Real per-school resistance path (Fire/Frost/Nature/Shadow/
            # Arcane/Holy, or a combined-school tuple - see get_resistance's
            # docstring for the lowest-of-components rule on combined
            # schools). Distinct from the legacy "magic" branch above:
            # "magic" abilities haven't been migrated to a real school yet
            # and keep using the old flat magic_resistance stat untouched;
            # only abilities deliberately authored with a real
            # DamageSchool value reach this branch.
            eff_res = self.get_resistance(damage_type)
            if attacker is not None:
                eff_res = max(0, int(eff_res - (getattr(attacker, "spell_penetration", 0) or 0)))
            reduction = self.resist_mitigation_from(eff_res, attacker_level)
        else:
            reduction = 0
        
        # Party row positioning (soft rows): the front line absorbs more
        # physical damage, the back line is exposed to spells instead. Applied
        # AFTER armor so it modifies real incoming damage rather than being
        # swallowed by the mitigation curve.
        from entities.party import row_damage_multiplier
        row = getattr(self, "row", None)
        row_mult = row_damage_multiplier(row, damage_type) if row else 1.0

        from combat.abilities import level_diff_multiplier
        level_mult = level_diff_multiplier(attacker_level, self.level)

        # Flat percentage modifier on ALL incoming damage, regardless of
        # school - the general-purpose hook Defensive Stance's -10% (and
        # any future "reduce damage taken" effect: Shield Wall, Ice
        # Barrier-style cooldowns) needs. Distinct from armor/magic
        # resistance (which only apply to their own damage school) and
        # from row positioning (which is about WHERE the damage lands,
        # not a flat scalar). Summed across talents + stat_mods the same
        # way every other derived stat is, via the shared bonus pool.
        taken_mult = 1.0 + self.get_talent_effect("damage_taken_pct", 0.0)
        taken_mult += self.get_status_stat_mod("damage_taken_pct")

        # School-specific companion to damage_taken_pct above (Earthen
        # Attunement, Shaman Tank: "6% less physical / 9% less spell damage
        # while Earthen Guardian is active" - real WOTLK splits physical vs
        # spell reduction, which the flat damage_taken_pct key can't
        # represent on its own). physical_damage_taken_pct stacks with
        # damage_taken_pct on physical hits; magic_damage_taken_pct stacks
        # with it on magic hits. Both default to 0 via get_talent_effect's
        # own default, so every ability/talent that never sets them is
        # completely unaffected by this addition.
        if damage_type == "physical":
            taken_mult += self.get_talent_effect("physical_damage_taken_pct", 0.0)
            # Buff/debuff-sourced companion to the talent-sourced line above
            # (Runemaster's Granite Resolve: "-20% physical damage taken"
            # self-buff; Starcaller's Chosen of the Moon taunt-debuff carries
            # the same key on the enemy it's cast on). THE ACTUAL BUG THIS
            # FIXES: get_status_stat_mod("damage_taken_pct") (the flat,
            # school-agnostic key) was already being read a few lines above,
            # but nothing anywhere ever read the school-specific buff/debuff
            # version of this key - every ability authored with
            # physical_damage_taken_pct/magic_damage_taken_pct in a REAL
            # buff or debuff's stat_mods (as opposed to a talent's) was a
            # complete no-op cooldown, the exact "correctly authored,
            # silently inert" failure mode found elsewhere this session.
            # get_status_stat_mod returns a plain percentage number (e.g.
            # -20 for -20%), so it divides by 100 here to match taken_mult's
            # 0.0-1.0 scale.
            #
            # NOTE, and this is a trap: this is the OPPOSITE convention to the
            # talent-sourced line above, which is NOT divided. A TALENT writes
            # these keys as a fraction (-0.02 for -2%, as the Shaman Tank
            # Earthen Attunement block in _recalculate_derived_stats does
            # literally) while a BUFF OR DEBUFF writes them as points (-20).
            # An earlier version of this comment claimed both used the same
            # convention; they never have. Authoring a proc's apply_effect
            # stat_mods with the talent convention makes it 100x too weak -
            # the same class of bug that left fifteen talents at 1/100th
            # strength (see tools/audit_talents.py, pct-unit-mixup).
            taken_mult += self.get_status_stat_mod("physical_damage_taken_pct") / 100.0
        elif damage_type == "magic" or damage_type in DamageSchool.ALL_SCHOOLS or isinstance(damage_type, (tuple, list)):
            # Broadened (Kyle's talent-overpass session, 2026-09-06):
            # previously only fired on the LEGACY "magic" string, missing
            # every ability using a real DamageSchool value (fire/frost/
            # nature/shadow/arcane/holy - the majority of abilities now,
            # per this session's balance pass). A generalist "resist all
            # magic" talent (Elemental Warding, Iron Will, Stoicism,
            # Unbreakable Will, Guarded by the Light - real WoW tank/
            # defensive talents, not school-specific ones) needs to apply
            # regardless of which real school the incoming hit uses, not
            # just the old catch-all "magic" damage_type.
            taken_mult += self.get_talent_effect("magic_damage_taken_pct", 0.0)
            # spell_damage_taken_pct is how two talents name the identical
            # idea. Accepted as an alias rather than left dead, since there is
            # no distinction in this engine between "magic" and "spell" damage
            # taken - every school above routes through this same branch.
            taken_mult += self.get_talent_effect("spell_damage_taken_pct", 0.0)
            # Same buff/debuff-sourced companion as the physical branch
            # above (Cultist's Doomcloak, Sun Cleric's Scroll of Hope,
            # Tinker's Aether/Arcane Bionics self- or party-buffs; Cultist's
            # Whispers of Yog-Saron, Runemaster's Inscription: Leyline, and
            # Tinker's Strength Bionics debuffs that INCREASE magic damage
            # taken on an enemy, same key, positive value) - identical bug,
            # identical fix: get_status_stat_mod was never read for this
            # key, so every one of these real buffs/debuffs was a no-op.
            taken_mult += self.get_status_stat_mod("magic_damage_taken_pct") / 100.0

            # Per-school companion to the catch-all magic_damage_taken_pct
            # above (Primalist's Stone Ward: "reduces Nature damage taken by
            # 3% per rank" - a school-SPECIFIC defensive talent, not a
            # generalist "resist all magic" one, so it needs its own key
            # rather than piggybacking on magic_damage_taken_pct, which
            # would also wrongly reduce Fire/Frost/Shadow/Arcane/Holy hits).
            # Key convention: "<school>_damage_taken_pct", e.g.
            # "nature_damage_taken_pct", "fire_damage_taken_pct" - reads
            # ONLY the single real school a hit actually carries (not a
            # combined-school tuple average/min; a combined-school hit gets
            # no per-school-specific reduction here, same as it gets no
            # per-school-specific resistance stacking beyond get_resistance's
            # existing min-of-components rule - a hybrid hit is deliberately
            # the hard case to defend against). Checked via both
            # get_talent_effect (talent trees) and get_status_stat_mod
            # (buffs/debuffs), same dual-source pattern as every other
            # damage_taken_pct key in this method.
            school_key = f"{damage_type}_damage_taken_pct" if isinstance(damage_type, str) else None
            if school_key:
                taken_mult += self.get_talent_effect(school_key, 0.0)
                taken_mult += self.get_status_stat_mod(school_key) / 100.0

            # <school>_resist_pct is how seven homebrew talents word the same
            # idea ("increases your Fire resistance by 3%"), and the key was
            # read by nothing. Treated as a reduction in that school's damage
            # taken, which is what resistance means mechanically here, so it
            # folds into the same taken_mult as the keys above rather than
            # needing a parallel system.
            #
            # Several are COMBINED - fire_nature_resist_pct covers Fire and
            # Nature, poison_disease_resist_pct covers both of those - so the
            # key is split on underscores and matched if the real school is
            # any of its named components. A combined-school hit still gets
            # nothing, same rule as the per-school block above.
            if isinstance(damage_type, str):
                for key, val in self._resist_pct_keys():
                    if damage_type in key.split("_"):
                        taken_mult -= val

        # low_health_damage_reduction_pct (Venomancer's Unbreakable: "-2%/
        # rank all damage taken while below 35% health"; Tinker's
        # Emergency Coolant: same key, "-2%/rank... below 30% Health" -
        # the actual threshold travels alongside the reduction via the new
        # low_health_threshold_pct key on the SAME talent node, since the
        # two classes' real tooltips use different thresholds and this one
        # reduction key alone can't carry two different numbers). Applies
        # to ALL damage types (unlike physical_damage_taken_pct/magic_
        # damage_taken_pct above, which are school-specific) - checked
        # unconditionally here, outside the physical/magic/school if-elif
        # chain, matching the generic damage_taken_pct catch-all's own
        # unconditional placement earlier in this method. Gated on
        # CURRENT health (before this hit lands), matching the real WoW
        # convention for "while below X% health" tank cooldowns/passives -
        # a hit that would cross the threshold doesn't retroactively get
        # the discount, and a hit taken while already below it does.
        # Falls back to a 35% threshold if a future talent grants the
        # reduction without pairing a threshold (keeps this from silently
        # doing nothing rather than silently always-on).
        low_hp_reduction = self.get_talent_effect("low_health_damage_reduction_pct", 0.0)
        if low_hp_reduction > 0 and self.health > 0:
            threshold = self.get_talent_effect("low_health_threshold_pct", 0.35)
            if (self.current_health / self.health) < threshold:
                taken_mult -= low_hp_reduction

        taken_mult = max(0.0, taken_mult)

        actual = max(1, int(amount * (1.0 - reduction) * row_mult * level_mult * taken_mult))

        if blocked:
            # A BLOCK SUBTRACTS ITS VALUE. Dodge and parry already stop the hit outright above, so
            # block is the partial one: the shield eats a fixed amount and the rest lands. This
            # used to ignore block_value entirely and apply a flat 30% instead, which meant a
            # bigger shield and every block_value talent in the game changed nothing.
            absorbed = self.block_value
            bonus = self.get_talent_effect("block_bonus_reduction", 0.0)
            if bonus:
                absorbed += actual * bonus
            actual = max(1, int(actual - absorbed))
            # A block is a partial hit, so ON_BLOCK fires here AND
            # ON_DAMAGE_TAKEN fires below, off the reduced amount. A talent
            # that pays out on blocking ("Blocking an attack now generates 3
            # Insanity") wants the former; one that pays out on being hurt
            # wants the latter; several specs have both.
            self._fire_avoidance_procs(("on_block",), attacker)

        self.current_health -= actual
        
        # Warriors - and anyone shapeshifted into a Rage form (Bear, Dire Bear,
        # Beetle) - generate rage from taking damage (reduced from 0.5 to 0.2)
        if self.generates_rage_from_combat():
            self.current_rage = min(100, self.current_rage + (actual * 0.2))

        # ON_DAMAGE_TAKEN procs (e.g. a defensive buff that grants a
        # resource, or reflects damage, when hit). Fired here - after
        # mitigation/avoidance/blocking are all resolved, off the real
        # final `actual` amount, not the raw incoming `amount`, so a proc
        # reading "amount" sees what genuinely landed.
        #
        # take_damage() has no combat_log handle of its own (Character
        # doesn't own the engine's log), so any messages this produces are
        # appended to self._pending_proc_messages rather than silently
        # dropped - CombatEngine._apply_effect's threat/proc block (which
        # DOES have combat_log) drains and clears that list right after
        # every take_damage() call resolves. Starts as [] via getattr's
        # default so this never crashes on an object that hasn't had it
        # initialized yet.
        if hasattr(self, "fire_proc_trigger"):
            from combat.status_effects import ProcTrigger
            # attacker (optional, new): whoever dealt this hit, passed
            # through as the proc's "target" - a retaliation-style
            # ON_DAMAGE_TAKEN proc (Venomancer's Venomous Retort: "melee
            # attacks against you have a 3%/rank chance to poison the
            # attacker"; Reactive Plating doesn't need it, since its
            # shield lands on self) needs to know WHO to hit back, which
            # take_damage had no way to express until this parameter was
            # added - every existing call site that doesn't pass attacker
            # (most of them, still) simply has no retaliation target,
            # exactly like before this parameter existed.
            proc_msgs = self.fire_proc_trigger(
                ProcTrigger.ON_DAMAGE_TAKEN, {"amount": actual, "target": attacker})
            if proc_msgs:
                pending = getattr(self, "_pending_proc_messages", None)
                if pending is None:
                    pending = self._pending_proc_messages = []
                pending.extend(proc_msgs)

        return actual
    
    def heal(self, amount):
        """Heal character.

        healing_taken_pct (recipient-side; CoA's Drown, Widowmaker,
        Inscription of the Leyline, Tentacle of Yog-Saron/healing_received_pct
        - merged into this one key during the stat-vocabulary cleanup since
        both names meant the exact same thing) scales the amount actually
        received, same "defender-side modifier on an already-rolled number"
        shape take_damage's damage_taken_pct already uses - a positive value
        is a healing-received buff, negative is the much more common
        anti-heal debuff (most of this engine's uses are the latter).
        """
        mult = 1.0 + (self.get_status_stat_mod("healing_taken_pct") if hasattr(self, "get_status_stat_mod") else 0.0) / 100.0
        self.current_health = min(self.health, self.current_health + amount * max(0.0, mult))
    
    def restore_mana(self, amount):
        """Restore mana."""
        self.current_mana = min(self.mana, self.current_mana + amount)
    
    def is_alive(self):
        """Check if alive."""
        return self.current_health > 0
    
    def update_combat(self, dt):
        """Update resources and abilities in combat (TURN-BASED ONLY).
        Resources only regen between turns, not during wait time."""
        # Update ability cooldowns (NOW DONE AT END OF TURN VIA decrement_all_cooldowns)
        pass
    
    def restore_resources_between_turns(self):
        """Restore resources when turn ends (for next turn)."""
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(self.char_class, self)

        # Energy regen - only Energy-resource classes (Rogue) actually spend
        # from this pool, so only they regen it. Previously every other
        # class also got +20 Energy/turn despite having zero abilities that
        # could ever spend it - harmless in practice but pointless busywork
        # and confusing if surfaced in UI/debugging later.
        if resource == ResourceType.ENERGY:
            self.current_energy = min(self.max_energy, self.current_energy + 25)

        # Mana regen tied to Spirit (0.5 mana per point of effective Spirit,
        # so 10 Spirit = 5 mana/turn). Only Mana-resource classes have a
        # nonzero self.mana pool to regen into (see _recalculate_derived_stats).
        if resource == ResourceType.MANA:
            self.current_mana = min(self.mana, self.current_mana + (self.effective_spirit * 0.5))

    def restore_resources_out_of_combat_step(self):
        """
        Called once per overworld tile moved (not a time tick).
          - Energy (Rogue only): 15 per step
          - Rage: decays by 2 per step (Rage has no out-of-combat source,
            so a Warrior shouldn't be able to wander around perpetually
            primed for a fight - it bleeds off between fights, matching WoW).

        Mana regen moved OFF this step-based path and onto
        StatusEffectMixin.tick_out_of_combat_regen (a real per-second
        tick, not per-tile-stepped) - see that method's docstring for why:
        Kyle wanted regen that works while STANDING STILL too (at half
        rate), which a "only while moving" step-based system could never
        support no matter how the numbers were tuned.
        """
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(self.char_class, self)

        if resource == ResourceType.ENERGY:
            self.current_energy = min(self.max_energy, self.current_energy + 15)

        if self.current_rage > 0:
            self.current_rage = max(0, self.current_rage - 2)

        # Secondary resources that decay (currently Static). Same reasoning
        # as Rage: these are built during a fight and shouldn't carry over.
        for key, rate in self.SECONDARY_DECAY_PER_STEP.items():
            if self.secondary_resources.get(key, 0) > 0:
                self.set_resource(key, self.secondary_resources[key] - rate)
    
    def get_stat_sheet(self):
        """Return formatted stat sheet. core_stats shows EFFECTIVE values (base + gear),
        matching what the character actually has in combat. base_stats is included
        separately so UI can optionally show "12 (+4 from gear)" style breakdowns."""
        return {
            "name": self.name,
            "class": self.char_class,
            "level": self.level,
            "prestige": self.prestige_level,
            "experience": self.experience,
            "core_stats": {
                "strength": self.effective_strength,
                "stamina": self.effective_stamina,
                "intellect": self.effective_intellect,
                "spirit": self.effective_spirit,
                "agility": self.effective_agility,
            },
            "base_stats": {
                "strength": self.strength,
                "stamina": self.stamina,
                "intellect": self.intellect,
                "spirit": self.spirit,
                "agility": self.agility,
            },
            "derived_stats": {
                "attack_power": self.attack_power,
                "ranged_attack_power": self.ranged_attack_power,
                "spell_power": self.spell_power,
                "healing_power": self.healing_power,
                "crit_physical": f"{self.crit_chance_physical:.1f}%",
                "crit_spell": f"{self.crit_chance_spell:.1f}%",
                "dodge": f"{self.dodge:.1f}%",
                "block": f"{self.block_chance:.1f}% / {self.block_value:.0f}",
                "parry": f"{self.parry:.1f}%",
                "haste": f"{self.haste:.1f}%",
            },
            "defense": {
                # display_health rounds the real internal float (Kyle:
                # "keep HP whole numbers") - current_health itself stays
                # exact so out-of-combat regen's fractional per-frame
                # ticks aren't lossy, only the UI-facing dict rounds.
                "health": self.display_health,
                "health_max": round(self.health),
                "mana": int(self.current_mana),
                "mana_max": round(self.mana),
                "armor": self.armor,
                "magic_resistance": self.magic_resistance,
            }
        }
    
    def to_dict(self):
        """Serialize to dict."""
        return {
            "name": self.name,
            "class": self.char_class,
            "level": self.level,
            # PETS WERE NEVER SAVED. active_pet was absent from this dict
            # entirely, so every pet class lost its pet on save and reload -
            # a Warlock summoned an Imp, saved, loaded, and had no Imp. It
            # survived unnoticed because a pet is cheap to re-summon and the
            # bug looks like "I forgot to summon".
            #
            # Only the template_id, display name and current health are
            # stored; everything else about a Pet is derived from its
            # template and its owner's level, and from_dict re-summons and
            # re-syncs. Additional pets (Tinker, Necromancer) round-trip the
            # same way.
            "pets": [
                {"template_id": pet.template_id, "name": pet.name,
                 "current_health": getattr(pet, "current_health", None),
                 "additional": i > 0}
                for i, pet in enumerate(self.all_pets)
            ],
            # Talent spend (save v4). Stored sparsely - only nodes with at
            # least one point are written, so the save stays small and adding
            # new talents to a tree later doesn't invalidate old saves.
            "talents": {
                tree_id: {
                    tid: node.points_spent
                    for tid, node in tree.nodes.items()
                    if node.points_spent > 0
                }
                for tree_id, tree in self.talent_trees.items()
                if tree.total_points_spent() > 0
            },
            "talent_points_available": self.talent_points_available,
            "prestige_level": self.prestige_level,
            "prestige_points": self.prestige_points,
            "experience": self.experience,
            "strength": self.strength,
            "stamina": self.stamina,
            "intellect": self.intellect,
            "spirit": self.spirit,
            "agility": self.agility,
            "current_health": self.current_health,
            "current_mana": self.current_mana,
            "current_rage": self.current_rage,
            "current_energy": self.current_energy,
            "hotbar": self.hotbar,
            "hotbar_autofilled_ids": sorted(self.hotbar_autofilled_ids),
            "extra_slots": self.extra_slots,
            "race": self.race,
            "gender": self.gender,
            "appearance_variant": self.appearance_variant,
            "equipment": self.equipment.to_dict(),
            "inventory": [item.to_dict() for item in self.inventory],
            "auto_sell_junk": bool(getattr(self, "auto_sell_junk", False)),
            "consumables": [c.to_dict() for c in self.consumables],
            "materials": [m.to_dict() for m in self.materials],
            "profession_skills": dict(self.profession_skills),
            "known_professions": list(self.known_professions),
            "known_recipes": list(self.known_recipes),
            "profession_tiers": dict(self.profession_tiers),
            "training_enabled": bool(self.training_enabled),
            "trained_ranks": dict(self.trained_ranks),
            # SHAPESHIFT FORM AND THE GUARDIAN TOGGLE WERE NEVER SAVED.
            # Both are documented as PERSISTENT (see the comment on
            # guardian_stance_active in __init__: "PERSISTENT like
            # current_form, not per-fight like current_stance") and neither
            # was in this dict, so a Druid logged out in Bear Form and came
            # back human, and a Shaman tank logged out as a tank and came
            # back a DPS.
            #
            # It showed up as smoke_play_all_classes.py reporting Venomancer
            # "save round trip LOST health: 874 -> 616" - the form's own
            # stat_mods go through get_talent_effects (character.py:635), so
            # dropping the form silently drops its health, armour and the
            # rest. The health loss was the visible half of a bug that was
            # really losing the whole form.
            #
            # current_stance is deliberately NOT saved: a Warrior stance is
            # per-fight, which is the distinction the __init__ comment draws.
            "current_form": self.current_form,
            "guardian_stance_active": bool(self.guardian_stance_active),
            "consumable_cooldown": self.consumable_cooldown,
            "guardian_buff": self.guardian_buff,
            "battle_buff": self.battle_buff,
            "food_buff": self.food_buff,
            "ammo_buff": self.ammo_buff,
            "class_base_stats": self.class_base_stats,
            "secondary_resources": self.secondary_resources,
            # Party identity (save v6). Without these a loaded companion lost
            # their spec lock and their row assignment.
            "row": self.row,
            "locked_spec": self.locked_spec,
            "recruit_id": self.recruit_id,
            "backstory": self.backstory,
            "background_sections": self.background_sections,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize from dict."""
        from entities.item import Item
        from entities.consumable import Consumable
        char = cls(data["name"], data["class"], data["level"])
        # Pets. Older saves have no "pets" key at all and simply come back
        # petless, which is what they did before this existed.
        for entry in data.get("pets") or []:
            ok, pet = char.summon_pet(entry.get("template_id"),
                                      name=entry.get("name"),
                                      additional=entry.get("additional", False))
            if ok and entry.get("current_health") is not None:
                pet.current_health = min(pet.max_health,
                                         max(1, int(entry["current_health"])))
        char.prestige_level = data.get("prestige_level", 0)
        char.prestige_points = data.get("prestige_points", 0)
        char.experience = data.get("experience", 0)
        char.strength = data["strength"]
        char.stamina = data["stamina"]
        char.intellect = data["intellect"]
        char.spirit = data["spirit"]
        char.agility = data["agility"]
        # Level-1 class stat snapshot. Older saves predate this field; the
        # constructor already set a correct one for this class, so fall back
        # to that rather than deriving a wrong baseline from levelled stats.
        char.class_base_stats = data.get("class_base_stats", char.class_base_stats)
        # Party identity (save v6); absent in v5 and earlier, where the
        # defaults set by __init__ are the correct fallback.
        char.row = data.get("row") or None
        char.locked_spec = data.get("locked_spec")
        char.recruit_id = data.get("recruit_id")
        char.backstory = data.get("backstory", "")
        char.background_sections = dict(data.get("background_sections", {}))
        char.secondary_resources = dict(data.get("secondary_resources", {}))
        char.current_rage = data.get("current_rage", 0)
        char.current_energy = data.get("current_energy", 100)
        char.hotbar = data.get("hotbar", [None] * 20)
        # Asher Coleman's ability_book must be rebuilt from his fixed kit
        # right after his hotbar is restored above - bug fix
        # (AttributeError: 'NoneType' object has no attribute
        # 'is_usable_by', on his combat turn after a save/load). The `cls`
        # constructor call at the top of this method runs the NORMAL
        # Character.__init__, which hands him a generic Paladin
        # ability_book - his saved hotbar (just restored above) still
        # points at "asher_wrath"/"asher_resignation", ability_ids that
        # only exist in his real hand-built book, never the generic one.
        # See RecruitNPC.build_asher_ability_book's docstring for the full
        # chain. Calling it here both rebuilds the correct ability_book
        # AND re-stamps hotbar slots 0/1 to those same two ids (a no-op
        # if the save already had them there, a real fix if an older/
        # corrupted save didn't). Deliberately NOT calling the full
        # RecruitNPC._build_asher_kit here - that also regenerates his
        # permanent gear with fresh random item_ids on every call, which
        # would silently discard whatever gear state this save actually
        # has.
        if char.recruit_id == "asher_coleman":
            from world.recruit_manager import RecruitNPC
            RecruitNPC.build_asher_ability_book(char)
        # Missing key = pre-fix save; seed from whatever's currently
        # slotted (matches the same fallback _autofill_hotbar itself
        # does) so an old save doesn't get its whole spellbook re-dumped
        # onto the bar the first time it's loaded post-fix.
        char.hotbar_autofilled_ids = set(data.get(
            "hotbar_autofilled_ids", [a for a in char.hotbar if a]))
        char.extra_slots = data.get("extra_slots", [None] * 8)
        char.race = data.get("race", "human")
        char.gender = data.get("gender", "male")
        char.appearance_variant = data.get("appearance_variant", 0)

        # Restore equipment/inventory BEFORE recalculating derived stats,
        # so gear bonuses are correctly folded into health/mana/armor/etc.
        char.equipment = Equipment.from_dict(data.get("equipment"))
        # Bags hold gear (Item) AND stackable LootItems (quest items / materials / vendor trash) - LootItem dicts have
        # no "slot", so dispatch on that or Item.from_dict KeyErrors on any save that carries a LootItem.
        from entities.loot_item import LootItem
        char.inventory = [(Item.from_dict(i) if "slot" in i else LootItem.from_dict(i))
                          for i in data.get("inventory", [])]
        char.auto_sell_junk = bool(data.get("auto_sell_junk", False))
        
        # Restore consumables (Phase 6). Currency is no longer stored on
        # Character (see Party.copper) - but a legacy save's "copper" key
        # is kept readable via getattr(player, "copper", 0) in
        # Party.from_dict's one-time migration, so an old save's money
        # isn't lost on first load under the new shared-purse model. This
        # attribute is transient (not re-saved by to_dict above) and only
        # meaningful immediately after loading an old save, before the
        # migration reads it.
        char.copper = data.get("copper", 0)
        char.consumables = [Consumable.from_dict(c) for c in data.get("consumables", [])]
        from entities.material import Material
        char.materials = [Material.from_dict(m) for m in data.get("materials", [])]
        char.profession_skills = data.get("profession_skills", {"herbalism": 0, "mining": 0, "woodcutting": 0, "skinning": 0})
        # Skinning was added after this field shipped, so a save written before
        # it exists has the key missing rather than zero. setdefault rather than
        # a rewrite so a real skill value in a newer save is never clobbered.
        char.profession_skills.setdefault("skinning", 0)
        # Profession learning (save v8).  Older saves: every profession the character has any skill in counts as learned
        # (even past the 3-slot limit - they just can't learn more), and skill above 75 means Journeyman.
        if "known_professions" in data:
            char.known_professions = list(data["known_professions"])
            char.profession_tiers = {k: int(v) for k, v in data.get("profession_tiers", {}).items()}
        else:
            char.known_professions = [p for p, v in char.profession_skills.items() if v > 0]
            char.profession_tiers = {p: 1 for p in char.known_professions if char.profession_skills[p] > 75}
        # Recipe discovery (save v9). Older saves had no known_recipes — treat all trainer-source recipes at or
        # below the character's current skill as already known (graceful migration: existing characters keep access
        # to everything they could already craft).
        if "known_recipes" in data:
            char.known_recipes = set(data["known_recipes"])
        else:
            char._migrate_known_recipes()
        char.consumable_cooldown = data.get("consumable_cooldown", 0.0)
        char.guardian_buff = data.get("guardian_buff")
        char.battle_buff = data.get("battle_buff")
        char.food_buff = data.get("food_buff")
        char.ammo_buff = data.get("ammo_buff")

        # Restore talent point spend (save v4). The character was constructed
        # with fresh trees and a level-derived point pool by __init__; here we
        # overwrite the per-node ranks with what was actually saved, then
        # restore the leftover pool. Without this, every talent point a player
        # spent was silently refunded on load - the trees reset to empty and
        # talent_points_available went back to (level - 4).
        saved_talents = data.get("talents")
        if saved_talents:
            for tree_id, node_ranks in saved_talents.items():
                tree = char.talent_trees.get(tree_id)
                if not tree:
                    continue  # tree renamed/removed since this save was made
                for talent_id, points in node_ranks.items():
                    node = tree.get_node(talent_id)
                    if node:
                        node.points_spent = min(points, node.max_points)
            char.talent_points_available = data.get(
                "talent_points_available", char.talent_points_available)

        # Class training (save v8).  A save without the field predates trainers: the player's character is grandfathered
        # with every rank their level already allows; companions stay level-based.
        # Restore the persistent form/toggle before the final stat
        # recalculation, so the form's stat_mods are folded back in rather
        # than the character being rebuilt in its humanoid shape. Both are
        # read through getattr-with-default elsewhere, so an older save
        # without these keys loads exactly as it did before.
        saved_form = data.get("current_form")
        if saved_form:
            char.current_form = saved_form
        if data.get("guardian_stance_active"):
            char.guardian_stance_active = True
        if saved_form or data.get("guardian_stance_active"):
            char._recalculate_derived_stats()

        if "training_enabled" in data:
            char.training_enabled = bool(data["training_enabled"])
            char.trained_ranks = {k: int(v) for k, v in data.get("trained_ranks", {}).items()}
            char._refresh_ability_ranks()
        elif not char.recruit_id:
            char.enable_training(grandfather=True)

        char._recalculate_derived_stats()
        char.current_health = data.get("current_health", char.health)
        char.current_mana = data.get("current_mana", char.mana)
        char.sanitize_hotbar()

        # RE-SYNC PETS NOW THAT THE OWNER IS A REAL CHARACTER AGAIN.
        # The pets are restored at the top of this method - they have to
        # be, because summon_pet enforces level and class rules and those
        # read the constructor's values - but at that point this character
        # has base stats, no gear and no talents. A Pet's stats are now a
        # share of its owner's (see entities/pet._apply_template_stats), so
        # building one against that half-restored character gave a loaded
        # save a pet scaled off a naked level-1-ish owner. Harmless before
        # pets scaled off anything, wrong the moment they did.
        for pet in char.all_pets:
            kept = pet.current_health
            pet._apply_template_stats()
            pet.current_health = min(pet.max_health, max(1, int(kept)))
        if char.recruit_id == "asher_coleman":
            # Kyle (2026-10-22): Asher's surname stays hidden early in the game; migrate older saves.
            char.name = "Asher"
            for it in char.equipment.slots.values():
                if it is not None and getattr(it, "name", "").startswith("Coleman Family "):
                    it.name = it.name.replace("Coleman Family ", "Family ")
        return char

    def sanitize_hotbar(self):
        """Drop hotbar / extra-slot ability ids that are not in this character's ability_book (stale ids from old
        saves, respecs or fixed-kit recruits) - they render as blank "?" blocks and used to crash combat."""
        book = getattr(self, "ability_book", None)
        if book is None:
            return
        for bar in (getattr(self, "hotbar", None), getattr(self, "extra_slots", None)):
            if not bar:
                continue
            for i, c in enumerate(bar):
                if isinstance(c, str) and book.get_ability(c) is None:
                    bar[i] = None

    def equip_item(self, item):
        """
        Equip an item from inventory. Moves any displaced item(s) back to
        inventory. Returns True if equipped successfully.

        Refuses items the class isn't proficient with (see
        entities/proficiency.py) - a Priest can't wear plate. Wearing armor
        LIGHTER than your class's type is allowed but weaker, matching WoW.
        """
        if item not in self.inventory:
            return False

        # Asher Coleman's gear is fixed and permanent - see
        # world/recruit_manager.py's _build_asher_kit and Kyle's explicit
        # spec ("You won't be able to change his equipment or his skills").
        # Hard-blocked here rather than just hidden in the UI, matching the
        # same "the real enforcement point every path funnels through, not
        # just a cosmetic UI restriction" approach used for Shoot/Wand's
        # ranged-weapon gate in combat/combat_engine.py.
        if getattr(self, "recruit_id", None) == "asher_coleman":
            return False

        from entities.proficiency import can_equip
        allowed, _reason = can_equip(self, item)
        if not allowed:
            return False

        result = self.equipment.equip(item)
        previous, displaced_offhand = result if isinstance(result, tuple) else (result, None)

        self.inventory.remove(item)
        if previous:
            self.inventory.append(previous)
        if displaced_offhand:
            self.inventory.append(displaced_offhand)

        self._recalculate_derived_stats()
        return True

    def unequip_item(self, slot, into=None):
        """Unequip an item from a slot into a bag. Returns True on success.

        `into` is WHOSE bag it lands in, and defaults to this character's own.
        The inventory screen passes the player, because that is the bag it
        draws and the bag it equips out of.

        KYLE, 2 NOV 2026: "when i unequip party gear its lost in the void."
        Not destroyed - parked somewhere with no UI. Unequipping a companion's
        item appended it to the COMPANION's inventory, and that screen's
        _bag_source always shows the PLAYER's bag when gearing a companion, so
        the item existed and nothing could ever display it again.

        Both halves were deliberate and they contradicted each other: you equip
        a companion OUT of the player's bag, and unequipped it back INTO
        theirs. One-way. The round trip has to be symmetric or the item falls
        out of the world.

        CAPACITY IS CHECKED, and a failed unequip puts the item BACK rather
        than dropping it. The old code appended straight to the list, bypassing
        inventory_capacity - so unequipping into a full bag silently overflowed
        it, which is the same class of mistake in the other direction.
        """
        # Same lock as equip_item above - Asher's gear can't be removed
        # either, not just "can't be replaced".
        if getattr(self, "recruit_id", None) == "asher_coleman":
            return False
        bag = into if into is not None else self
        item = self.equipment.unequip(slot)
        if not item:
            return False
        if not bag.add_to_inventory(item):
            # Straight back into the slot it came out of. NOT equip(), which
            # takes an item rather than a slot and carries the two-handed /
            # off-hand displacement rules with it - putting a shield back
            # through that path could evict the main hand. This is the exact
            # inverse of the unequip above and nothing else has changed.
            self.equipment.slots[slot] = item
            return False
        self._recalculate_derived_stats()
        if bag is not self:
            bag._recalculate_derived_stats()
        return True

    @property
    def inventory_capacity(self):
        """Total backpack slots: BASE_INVENTORY_CAPACITY (24, Kyle's spec)
        plus whatever the 4 equipped bags add on top. Recomputed live off
        currently-equipped bags rather than cached, so unequipping a bag
        immediately shrinks capacity - same "live off equipment" pattern
        as armor/stat totals elsewhere in this class."""
        return BASE_INVENTORY_CAPACITY + self.equipment.get_bag_capacity()

    def add_to_inventory(self, item):
        """Add a looted/generated item to inventory. Returns True if it
        fit, False if the backpack is full (inventory_capacity reached) -
        callers (combat loot, vendor buy, recruit gear) MUST check this
        return value rather than assuming success, since a full bag is now
        a real possible outcome instead of an unlimited list."""
        if len(self.inventory) >= self.inventory_capacity:
            return False
        self.inventory.append(item)
        return True

    def slot_ability(self, hotbar_slot, ability_id):
        """Slot an ability into the hotbar (0-19). Returns True if successful."""
        if 0 <= hotbar_slot < 20:
            ability = self.ability_book.get_ability(ability_id)
            if ability:
                self.hotbar[hotbar_slot] = ability_id
                return True
        return False
    
    def unslot_ability(self, hotbar_slot):
        """Remove ability from hotbar slot."""
        if 0 <= hotbar_slot < 20:
            self.hotbar[hotbar_slot] = None

    def slot_extra_ability(self, extra_slot, ability_id):
        """Slot an ability into one of the click-only extra slots (0-7).
        Same validation as slot_ability, separate list - see __init__."""
        if 0 <= extra_slot < len(self.extra_slots):
            ability = self.ability_book.get_ability(ability_id)
            if ability:
                self.extra_slots[extra_slot] = ability_id
                return True
        return False

    def unslot_extra_ability(self, extra_slot):
        """Remove ability from an extra (click-only) slot."""
        if 0 <= extra_slot < len(self.extra_slots):
            self.extra_slots[extra_slot] = None
    
    # =========== CURRENCY - MOVED TO Party (Phase "real people" refactor) ===========
    # Currency used to live here per-Character, which worked by accident
    # since only the player ever spent/earned it. Now that gear/consumables
    # are per-character, money is the one thing that stays SHARED across
    # the party - see entities/party.py's add_currency/remove_currency/
    # get_currency_string/self.copper. Every call site now goes through
    # state_manager.get_party() instead of state_manager.player directly.
    
    # =========== CONSUMABLE METHODS (Phase 6) ===========
    
    def add_consumable(self, consumable):
        """
        Add a consumable to inventory. If a stack of the same consumable_id
        exists and has room, add to that stack. Otherwise add as new stack.
        """
        for existing in self.consumables:
            if existing.consumable_id == consumable.consumable_id:
                if existing.quantity < existing.stack_limit:
                    existing.quantity += consumable.quantity
                    return True
        # No existing stack or all stacks full, add new
        self.consumables.append(consumable)
        return True
    
    def remove_consumable(self, consumable):
        """Remove a consumable from inventory."""
        if consumable in self.consumables:
            self.consumables.remove(consumable)
            return True
        return False

    # =========== MATERIAL METHODS (Gathering Phase 1) ===========

    def add_material(self, material):
        """Add a gathered material to inventory. If a stack of the same
        material_id exists and has room, add to that stack. Otherwise add
        as a new stack. Identical shape to add_consumable - see that
        method's docstring for the stacking rationale."""
        for existing in self.materials:
            if existing.material_id == material.material_id:
                if existing.quantity < existing.stack_limit:
                    existing.quantity += material.quantity
                    return True
        self.materials.append(material)
        return True

    def remove_material(self, material):
        """Remove a material stack from inventory."""
        if material in self.materials:
            self.materials.remove(material)
            return True
        return False

    def get_material_quantity(self, material_id):
        """Total quantity of a material_id across all stacks (there
        should only ever be one stack per material_id per add_material's
        own stacking logic, but this sums defensively rather than assumes
        that invariant always holds)."""
        return sum(m.quantity for m in self.materials if m.material_id == material_id)

    def has_materials(self, requirements):
        """requirements: dict of material_id -> quantity needed. Returns
        True only if EVERY requirement is met at its full quantity -
        used by smelting/crafting to validate before attempting a craft,
        so a recipe never partially consumes materials on a craft that
        was always going to fail partway through."""
        return all(self.get_material_quantity(mid) >= qty for mid, qty in requirements.items())

    def consume_material(self, material_id, quantity):
        """Remove `quantity` of material_id from inventory, across one or
        more stacks if needed (draining a stack fully before moving to
        the next, order otherwise unspecified). Returns True if the full
        quantity was removed, False if there wasn't enough (in which case
        NOTHING is removed - this is all-or-nothing, not a partial drain,
        so a failed consume never leaves inventory in a half-consumed
        state). Callers that need to consume several different materials
        atomically (e.g. a smelting recipe with 2 inputs) should call
        has_materials() first to check ALL requirements before consuming
        ANY of them - this method only guarantees atomicity for a single
        material_id, not across multiple consume_material() calls."""
        if self.get_material_quantity(material_id) < quantity:
            return False

        remaining = quantity
        # Iterate over a copy since stacks may be removed from
        # self.materials mid-loop (emptied stacks are deleted, not left
        # behind at quantity 0 - matches how a real inventory slot would
        # free up rather than showing a ghost "x0" stack).
        for stack in list(self.materials):
            if remaining <= 0:
                break
            if stack.material_id != material_id:
                continue
            take = min(stack.quantity, remaining)
            stack.quantity -= take
            remaining -= take
            if stack.quantity <= 0:
                self.materials.remove(stack)
        return True

    #: Skill cap by trained tier: Apprentice 75, Journeyman 150, Expert 225, Artisan 300.
    PROFESSION_TIER_CAPS = (75, 150, 225, 300)
    MAX_PRIMARY_PROFESSIONS = 3

    def knows_profession(self, profession):
        return profession in self.known_professions

    # ------------------------------------------------------------------ recipe discovery
    def knows_recipe(self, recipe_id):
        """True if this recipe has been explicitly learned (trainer, drop, vendor, or quest)."""
        return recipe_id in self.known_recipes

    def learn_recipe(self, recipe_id, profession, skill_required=0):
        """Add recipe_id to known_recipes.

        Returns (True, msg) on success, (False, msg) on failure.
        Callers should check skill_required before calling — the check is
        duplicated here as a hard gate so a race condition or UI bug can
        never sneak an unlearnable recipe into known_recipes.
        """
        if recipe_id in self.known_recipes:
            return False, "You already know that recipe."
        current = self.profession_skills.get(profession, 0)
        if current < skill_required:
            return False, f"Requires {profession.title()} skill {skill_required} (you have {current})."
        if not self.knows_profession(profession):
            return False, f"You haven't learned {profession.title()}."
        self.known_recipes.add(recipe_id)
        return True, "Recipe learned."

    def learn_trainer_recipes(self, profession, recipes_dict):
        """Called when visiting a trainer. Automatically teaches every recipe whose
        source is 'trainer' and whose skill_required <= the character's current skill.
        Returns a list of newly-learned recipe IDs for the trainer UI to display."""
        learned = []
        current = self.profession_skills.get(profession, 0)
        for rid, recipe in recipes_dict.items():
            if recipe.get("source") == "trainer" and recipe.get("skill_required", 0) <= current:
                if rid not in self.known_recipes:
                    self.known_recipes.add(rid)
                    learned.append(rid)
        return learned

    def _migrate_known_recipes(self):
        """Graceful migration for saves that pre-date the recipe-discovery system.
        Auto-learn all trainer-source recipes at or below current skill so existing
        characters don't lose access to recipes they could already craft."""
        try:
            from world.crafting_manager import get_crafting_manager
            from world.blacksmithing_manager import get_blacksmithing_manager
            from world.leatherworking_manager import get_leatherworking_manager
            managers = [
                ("tailoring", get_crafting_manager().all_recipes("tailoring")),
                ("alchemy", get_crafting_manager().all_recipes("alchemy")),
                ("woodworking", get_crafting_manager().all_recipes("woodworking")),
                ("blacksmithing", get_blacksmithing_manager().recipes),
                ("leatherworking", get_leatherworking_manager().recipes),
            ]
            for prof, recipes in managers:
                skill = self.profession_skills.get(prof, 0)
                for rid, recipe in recipes.items():
                    if recipe.get("source", "trainer") == "trainer" and recipe.get("skill_required", 0) <= skill:
                        self.known_recipes.add(rid)
        except Exception:
            pass  # Migration is best-effort; newer recipes will be learned normally

    def profession_cap(self, profession):
        tier = min(self.profession_tiers.get(profession, 0), len(self.PROFESSION_TIER_CAPS) - 1)
        return self.PROFESSION_TIER_CAPS[tier]

    def learn_profession(self, profession):
        """Learn a profession. False if already known, or if all primary slots are used.

        SECONDARY TRADES DO NOT COST A SLOT (Kyle, 2026-10-31, on Cooking). The slot test asks
        profession_manager rather than counting known_professions, because this method and
        profession_manager.offers() are two places that both decide "can you learn this" - the
        trainer would have offered Cooking and this would have silently refused it. One rule,
        asked in both places. Falls back to the old count if the data cannot be read, so a
        broken professions.json degrades to the previous behaviour instead of handing out
        unlimited professions.
        """
        if profession in self.known_professions:
            return False
        try:
            from world import profession_manager as pm
            if not pm.is_secondary(profession) and pm.primary_count(self) >= self.MAX_PRIMARY_PROFESSIONS:
                return False
        except Exception:
            if len(self.known_professions) >= self.MAX_PRIMARY_PROFESSIONS:
                return False
        self.known_professions.append(profession)
        self.profession_tiers.setdefault(profession, 0)
        self.profession_skills.setdefault(profession, 0)
        return True

    def unlearn_profession(self, profession):
        """Forget a profession; its skill and tier reset (re-learning starts from zero)."""
        if profession not in self.known_professions:
            return False
        self.known_professions.remove(profession)
        self.profession_tiers.pop(profession, None)
        self.profession_skills[profession] = 0
        return True

    def gain_profession_skill(self, profession, amount=1, cap=None):
        """Increase a gathering profession's skill level, clamped to cap
        if given (see world.gathering_manager.TIER_SKILL_CAPS - 75 for
        early tier, the only tier that currently exists). No cap passed
        means uncapped, same as before this existed - callers that care
        about the real WoW-style tier cap should pass one explicitly
        rather than this method reaching into gathering_manager itself,
        which would put a world/ import inside entities/ and invert the
        codebase's existing dependency direction (entities are lower-
        level than world, not the other way around)."""
        if profession not in self.profession_skills:
            self.profession_skills[profession] = 0
        # Skill only grows for a LEARNED profession, and never past the trained tier's cap.
        if profession not in self.known_professions:
            return False
        tier_cap = self.profession_cap(profession)
        cap = tier_cap if cap is None else min(cap, tier_cap)
        new_value = self.profession_skills[profession] + amount
        new_value = min(new_value, max(cap, self.profession_skills[profession]))
        self.profession_skills[profession] = new_value
        return False
    
    def apply_consumable_buff(self, buff_category, consumable):
        """
        Apply a buff from a consumable (elixir or food).
        buff_category: "guardian", "battle", or "food"
        """
        buff_tuple = (consumable, consumable.effect_duration)
        
        if buff_category == "guardian":
            self.guardian_buff = buff_tuple
        elif buff_category == "battle":
            self.battle_buff = buff_tuple
        elif buff_category == "food":
            self.food_buff = buff_tuple
        elif buff_category == "ammo":
            self.ammo_buff = buff_tuple
    
    def get_active_buff_stats(self):
        """
        Return the total stat bonuses from active buffs.
        Returns a dict like {'intellect': 12, 'spell_power': 4, ...} - keys are
        whatever each active consumable's stat_bonuses dict specifies (see
        Consumable docstring), summed across all three buff slots. Not
        hardcoded to a fixed stat set, so a food that grants Intellect+Spirit
        and an elixir that grants Stamina compose naturally, and any future
        consumable can target any stat _recalculate_derived_stats() reads
        from its bonus pool without touching this method.
        """
        buff_stats = {}

        for buff in (self.guardian_buff, self.battle_buff, self.food_buff, self.ammo_buff):
            if buff is None:
                continue
            consumable, _ = buff
            for stat_name, amount in consumable.stat_bonuses.items():
                buff_stats[stat_name] = buff_stats.get(stat_name, 0) + amount

        return buff_stats
    
    def update_buff_timers(self, dt):
        """
        Update consumable buff timers (call once per frame/turn).
        dt: delta time in seconds
        """
        if self.guardian_buff is not None:
            consumable, duration = self.guardian_buff
            new_duration = duration - dt
            if new_duration <= 0:
                self.guardian_buff = None
            else:
                self.guardian_buff = (consumable, new_duration)
        
        if self.battle_buff is not None:
            consumable, duration = self.battle_buff
            new_duration = duration - dt
            if new_duration <= 0:
                self.battle_buff = None
            else:
                self.battle_buff = (consumable, new_duration)
        
        if self.food_buff is not None:
            consumable, duration = self.food_buff
            new_duration = duration - dt
            if new_duration <= 0:
                self.food_buff = None
            else:
                self.food_buff = (consumable, new_duration)

        if self.ammo_buff is not None:
            consumable, duration = self.ammo_buff
            new_duration = duration - dt
            if new_duration <= 0:
                self.ammo_buff = None
            else:
                self.ammo_buff = (consumable, new_duration)
