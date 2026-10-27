"""
Ability system. Defines abilities with costs, cooldowns, and effects.

RANK SYSTEM (added post-Phase-6):
Abilities now rank up like classic WoW - Rank 1/2/3/etc, learned at fixed
even-numbered levels (see combat/rank_generator.py for the spacing rules),
rather than continuously auto-scaling with character level. Each rank has
its own cost and effect_value. Mana-costing abilities have cost increase
per rank (matching WoW); Rage/Energy/other non-Mana resources keep a FLAT
cost across all ranks (also matching WoW - Rage/Energy abilities never got
more expensive as they ranked up, only their damage grew).

Ability.cost / Ability.effect_value / Ability.name / Ability.description
remain simple properties for backward compatibility with UI code
(combat_screen.py, character_sheet_screen.py) - they now read from
whichever rank is currently unlocked for the owning character, rather than
being fixed at construction time.
"""
from enum import Enum
from combat.rank_generator import generate_ranks
from combat.status_effects import StatusEffect, EffectType, _UNSET, DamageSchool


# ----------------------------------------------------------------------
# LEVEL-DIFFERENCE DAMAGE SCALING
# ----------------------------------------------------------------------
# Without this, a party could out-level content by 10+ levels and still
# trade damage roughly evenly with it (armor/resist alone doesn't scale
# fast enough to matter) - Kyle's level-3 full party was taking down
# level-16 bosses. WoW handles this with to-hit/crit/avoidance tables tied
# to level delta; for this game a single symmetric multiplier on the
# ATTACKER's side of take_damage is simpler to reason about and tune, and
# it works identically whether the player is over- or under-leveled.
#
# +8% damage dealt per level the attacker is ABOVE the defender, and the
# same curve going the other way (an under-leveled attacker deals less),
# clamped so it never fully trivializes or wipes a fight in one hit.
LEVEL_DIFF_PER_LEVEL = 0.08
LEVEL_DIFF_MIN_MULT = 0.15
LEVEL_DIFF_MAX_MULT = 4.0


def level_diff_multiplier(attacker_level, defender_level):
    """Symmetric damage multiplier from attacker/defender level gap.

    Positive level_diff (attacker higher) -> multiplier > 1 (more damage).
    Negative level_diff (attacker lower)   -> multiplier < 1 (less damage).
    Applies identically to player-attacks-monster and monster-attacks-player,
    so a level 25 player one-shots a level 5 boar AND a level 25 mob
    steamrolls a level 5 player - the same rule both directions.
    """
    if attacker_level is None or defender_level is None:
        return 1.0
    diff = attacker_level - defender_level
    mult = 1.0 + diff * LEVEL_DIFF_PER_LEVEL
    return max(LEVEL_DIFF_MIN_MULT, min(LEVEL_DIFF_MAX_MULT, mult))


class ResourceType(Enum):
    RAGE = "rage"
    ENERGY = "energy"
    MANA = "mana"
    HEALTH = "health"
    STATIC = "static"              # Stormbringer: stacks 0-100, risk of Discharge at max
    INSANITY = "insanity"           # Cultist: 0-100, more dmg at high stacks, risk at max
    COMBO = "combo"                 # Templar: Opener -> Followup -> Combo Breaker chain
    LIFE_FORCE = "life_force"       # Necromancer: pool for summoning/maintaining undead
    ROUNDS = "rounds"               # Unused - Tinker actually uses Mana; "Rounds"
                                     # are ammo-loadout self-buffs (see
                                     # data/abilities/tinker.json), not a
                                     # spendable resource. Kept in the enum in
                                     # case a future class wants a real
                                     # ammo-count resource.
    RUNES = "runes"                 # Runemaster: up to 4 stored, cycles Frost/Fire/Arcane
    SOULS = "souls"                 # Reaper: harvested from kills, spent on burst
    FOCUS = "focus"                 # Witch Hunter
    DEATHFIRE = "deathfire"         # Knight of Xoroth: combo-point-style finisher currency
    FELFURY = "felfury"             # Felsworn: passive charges + toggleable Demon Form
    ARCHERY_POINTS = "archery_points"  # Ranger: banks toward a payoff
    SOLAR_POWER = "solar_power"     # Sun Cleric: builds from spells, unleashed at threshold
    VITALITY = "vitality"           # Bloodmage: HP spent as a resource alongside Rage


# Single source of truth for "what resource(s) does this class use".
# UI screens (combat_screen.py, character_sheet_screen.py) and Character's
# stat recalculation both read this instead of hardcoding per-class name
# checks in three different places - that duplication is exactly what let
# Warrior/Rogue/Hunter end up with a computed-but-unused Mana pool, and let
# Hunter/Mage/Warlock/Druid/Paladin's real Mana bars silently fail to render
# after the roster expanded past the original 4 launch classes.
#
# Each entry is (primary_resource, secondary_resource_or_None). The primary
# is what drives the main resource bar and what abilities are assumed to
# cost by default (matches the single-resource model the original 9 classes
# use). The secondary is a class-defining mechanic layered on top (Insanity,
# Deathfire, Solar Power, etc.) - these are DATA ONLY for now, matching
# Kyle's direction that skills/abilities for the CoA roster come in a later
# pass. No combat logic consumes secondary resources yet; Character just
# tracks a pool for each so the UI and future ability system have something
# real to read from instead of needing another rework.
CLASS_RESOURCE_MAP = {
    # Original 9
    "Warrior": (ResourceType.RAGE, None),
    "Rogue": (ResourceType.ENERGY, None),
    "Hunter": (ResourceType.MANA, None),
    "Mage": (ResourceType.MANA, None),
    "Warlock": (ResourceType.MANA, None),
    "Priest": (ResourceType.MANA, None),
    "Druid": (ResourceType.MANA, None),
    "Shaman": (ResourceType.MANA, None),
    "Paladin": (ResourceType.MANA, None),

    # 21 CoA classes (resources only - no abilities yet, see class docstring above)
    "Necromancer": (ResourceType.LIFE_FORCE, None),
    "Pyromancer": (ResourceType.MANA, None),
    "Cultist": (ResourceType.MANA, ResourceType.INSANITY),
    "Starcaller": (ResourceType.MANA, ResourceType.ENERGY),  # confirmed via screenshots (Celestial Strike costs Energy) - was wrongly Mana-only
    "Sun Cleric": (ResourceType.MANA, ResourceType.SOLAR_POWER),  # confirmed via handoff doc: pure Mana + Solar Power sub-resource, no Rage in any spec (was wrongly noted "also uses Rage")
    "Tinker": (ResourceType.MANA, None),  # "Rounds" are NOT a resource - they're
    # a swappable ammo-loadout buff (Armor-Piercing/Overcharged/Medic Rounds,
    # ~1hr duration, one active at a time via exclusive_group) implemented as
    # ordinary self-buff abilities. See data/abilities/tinker.json.
    "Runemaster": (ResourceType.MANA, ResourceType.RUNES),
    "Primalist": (ResourceType.MANA, ResourceType.RAGE),  # dual-resource builder/
    # spender, same shape as Stormbringer's Mana->Static: Mana-cost spells
    # (Geode Barrage) generate Rage, Rage-cost abilities (Wildclaw, Hand of
    # the Earthmother) spend it on payoffs. Confirmed via CoA screenshot
    # tooltips - NOT pure Rage-from-melee like a Warrior.
    "Reaper": (ResourceType.MANA, ResourceType.SOULS),
    "Venomancer": (ResourceType.MANA, None),  # spec-dependent (Mana OR Rage) - defaulted to Mana, see reference doc
    "Chronomancer": (ResourceType.MANA, None),
    "Bloodmage": (ResourceType.RAGE, ResourceType.VITALITY),  # spends own HP (Vitality) alongside Rage
    "Guardian": (ResourceType.ENERGY, None),
    # Mana is the primary pool; Static is BANKED by spending Mana on builders
    # and then spent on payoff abilities. Static is the class-defining
    # mechanic but Mana is what actually gates the rotation, which is why
    # Mana is primary here.
    "Stormbringer": (ResourceType.MANA, ResourceType.STATIC),
    "Felsworn": (ResourceType.FELFURY, None),
    "Barbarian": (ResourceType.ENERGY, None),
    "Witch Doctor": (ResourceType.MANA, None),
    "Witch Hunter": (ResourceType.FOCUS, None),
    "Knight of Xoroth": (ResourceType.RAGE, ResourceType.DEATHFIRE),
    "Templar": (ResourceType.COMBO, None),
    "Ranger": (ResourceType.ARCHERY_POINTS, None),
}


def get_class_resource(char_class, character=None):
    """Return the PRIMARY ResourceType this class uses, defaulting to Mana
    for any unrecognized class rather than raising. This is what the main
    resource bar (combat_screen.py, character_sheet_screen.py) displays.

    character (optional): when given and currently shapeshifted (see
    combat/forms.py), the form's resource type overrides the class
    default - real WOTLK Bear/Dire Bear Form use Rage and Cat Form uses
    Energy regardless of the Druid's normal Mana pool. Callers that only
    have a bare char_class string (not a live Character) keep working
    exactly as before; this parameter is additive, not a breaking change
    to the 13 existing call sites that don't pass it.
    """
    if character is not None:
        form_id = getattr(character, "current_form", None)
        if form_id:
            from combat.forms import resource_for_form
            form_resource = resource_for_form(form_id)
            if form_resource is not None:
                return form_resource
    primary, _ = _lookup_class_resource(char_class)
    return primary


def _lookup_class_resource(char_class):
    """Case-insensitive lookup into CLASS_RESOURCE_MAP.

    Real bug found: the map's keys are title-cased ("Rogue", "Warrior")
    and the old direct .get() silently fell back to (Mana, None) for ANY
    casing mismatch or typo, with no warning. Every real data file uses
    correct title-case so this hasn't bitten actual gameplay yet, but a
    resource lookup that fails silently instead of loudly is exactly the
    kind of landmine that shows up later as "why is this class's bar
    wrong" with no error to point at. Now case-insensitive, and warns
    once per unrecognized class instead of pretending Mana is correct.
    """
    if char_class in CLASS_RESOURCE_MAP:
        return CLASS_RESOURCE_MAP[char_class]
    lowered = char_class.lower() if isinstance(char_class, str) else char_class
    for key, value in CLASS_RESOURCE_MAP.items():
        if key.lower() == lowered:
            return value
    if char_class not in _WARNED_UNKNOWN_CLASSES:
        _WARNED_UNKNOWN_CLASSES.add(char_class)
        print(f"[get_class_resource] WARNING: unrecognized char_class {char_class!r}, defaulting to Mana")
    return (ResourceType.MANA, None)


_WARNED_UNKNOWN_CLASSES = set()


def get_class_secondary_resource(char_class):
    """Return the SECONDARY ResourceType this class uses, or None if it only
    has one resource. Data-only for now (see CLASS_RESOURCE_MAP docstring) -
    no combat logic spends from this yet."""
    _, secondary = _lookup_class_resource(char_class)
    return secondary


# Resource types whose ability cost is allowed to increase per rank, matching
# WoW: only Mana-costing abilities got more expensive as they ranked up.
_SCALES_COST_WITH_RANK = {ResourceType.MANA}


class Ability:
    """An ability that a character can use. Supports multiple ranks."""

    #: Who an ability is aimed at when the data doesn't say. Buffs default
    #: to SELF (the conservative choice - a personal cooldown wrongly cast on
    #: someone else is worse than a raid buff you have to target manually),
    #: heals to a friendly target, everything else to the enemy.
    DEFAULT_TARGET_TYPE = {
        "heal": "ally",
        "hot": "ally",
        "buff": "self",
        "damage": "enemy",
        "spell_damage": "enemy",
        "dot": "enemy",
        "spell_dot": "enemy",
        "debuff": "enemy",
        "damage_and_heal": "enemy",
    }

    #: Valid target_type values.
    #:   self       - always the caster, ignores the passed target
    #:   ally       - one friendly target (falls back to the caster)
    #:   party      - every living party member at once
    #:   enemy      - a single hostile target
    #:   enemy_aoe  - every living enemy at once (Arcane Explosion, Chain
    #:                Lightning, Consecration, Multi-Shot, ...). Per-target
    #:                damage is reduced by AOE_DAMAGE_MULTIPLIER so an AoE
    #:                nuke doesn't out-damage a single-target one against a
    #:                lone target while still being clearly worth using
    #:                against a pack - matches the standard MMO convention
    #:                rather than dealing full single-target damage to
    #:                every enemy in the fight for the same resource cost.
    TARGET_TYPES = ("self", "ally", "party", "enemy", "enemy_aoe")

    #: Fraction of an ability's normal single-target damage/DoT tick each
    #: target takes when the ability is enemy_aoe. Tunable in one place
    #: rather than scattered through every AoE ability's data.
    AOE_DAMAGE_MULTIPLIER = 0.6

    def __init__(self, ability_id, name, resource_type, ranks,
                 cooldown=0, effect_type="damage", description="",
                 duration=0, stat_mods=None, generates=None,
                 target_type=None, buff_scope=None, requires_talent=False,
                 is_instant=False, consumes_hot=False, consumable_hot_ids=None,
                 dispel_type=None, requires_form=None, heal_scope="lowest_ally",
                 exclusive_group=None, heal_in_form=None, applies_dot_pct=None,
                 shapeshift_form_id=None, consumes_seal=False, proc=None,
                 execute_threshold_pct=None, damage_school=None,
                 requires_ranged_weapon=None, is_stun=False, icon_id=None,
                 dispel_count=1, consumes_stacks_of=None, duration_per_stack=0,
                 restore_resource_type=None, absorb=0, absorb_pct_max_health=0.0,
                 max_targets=None, force_proc_group=None, summon_pet_template=None):
        """
        ranks: list of dicts, each with at least "rank", "level_req", "cost",
            and "effect_value" keys (from combat/rank_generator.py's
            generate_ranks(), or hand-authored in the same shape).
        """
        self.ability_id = ability_id
        self.name = name
        # Real per-ability icon art is named after ability_id 1:1 by
        # convention (see icon_migration_and_ui.py's
        # get_ability_icon_surface) - icon_id only needs to be set
        # explicitly in JSON when an ability intentionally shares another
        # ability's art (e.g. every class's basic melee Attack sharing
        # one generic sword via "ability_melee", or universal Shoot/Wand
        # using their own dedicated weapon-type icons). This field was
        # accepted by _ability_from_data's JSON parsing and set in every
        # ability JSON file, but the Ability class itself never had a
        # place to put it - it was silently dropped at construction time,
        # so EVERY ability's icon_id was always None regardless of what
        # the JSON said, and every icon lookup fell through to whatever
        # ability_id-named file happened to exist (never anything for
        # "ability_melee"/"ability_ranged"/"ability_wand", which don't
        # match any real ability_id) - a real "looks done but never
        # executed" case: the icon pipeline, the JSON data, and the UI
        # lookup code all existed and were individually correct, but
        # nothing carried the value between them.
        self.icon_id = icon_id
        self.resource_type = resource_type  # ResourceType enum
        # Optional secondary-resource generation, e.g. a Stormbringer builder
        # that costs Mana but banks Static: {"resource": "static", "amount": 20}
        self.generates = generates or None
        # Tinker's Rounds (and any future ammo/loadout-style ability): the
        # exclusive_group tag passed straight through to the StatusEffect
        # this ability creates, so applying a new Round replaces whichever
        # other Round was active. None for every other ability, which keeps
        # the normal same-id-refresh/different-id-stack buff behavior.
        self.exclusive_group = exclusive_group
        # (form_id, target_type) pair, or None. When set and caster.current_form
        # matches form_id, _apply_effect reroutes this cast to the heal branch
        # instead of its normal effect_type - see Venomancer's Serpent's Fang.
        self.heal_in_form = heal_in_form
        # % of a spell_damage hit's damage also applied as a 1-turn DoT on
        # the same target(s) - e.g. Stormbringer's Shock (10%). None/0 for
        # every ability that doesn't do this (the vast majority).
        self.applies_dot_pct = applies_dot_pct or 0
        # Real form_id this ability shifts the caster into, for
        # effect_type="shapeshift" (e.g. "bear", "spider"). None for every
        # other ability.
        self.shapeshift_form_id = shapeshift_form_id
        # Pet template id (combat/pet_templates.py) this ability summons,
        # for effect_type="summon_pet" (e.g. "wolf", "imp", "ziggi_6k").
        # Same shapeshift_form_id-style pattern: the real mechanic
        # (Character.summon_pet) already existed before this field did -
        # Hunter taming, Warlock demon summons, and Primalist/Stormbringer/
        # Tinker's companion pets were ALL stubbed as plain self-buffs with
        # no way to actually call it from a cast (Kyle, Oct 2026: "We need
        # the pet system up and running"). None for every other ability.
        self.summon_pet_template = summon_pet_template
        self.ranks = ranks  # list of rank dicts, ascending by level_req
        self.cooldown = cooldown  # Turns between uses (NOT seconds!)
        self.turns_remaining = 0  # Turns remaining on cooldown
        # "damage", "spell_damage", "heal", "dot", "spell_dot", "hot",
        # "buff", "debuff", "damage_and_heal" (Cryotherapist: one cast
        # damages the enemy target AND smart-heals the caster's lowest-HP%
        # ally in the same action - see _apply_effect and _lowest_hp_ally)
        self.effect_type = effect_type
        self.description = description
        # Duration in turns for dot/hot/buff/debuff effect types (ignored by
        # instant types). stat_mods is the base buff/debuff magnitude, scaled
        # per rank by effect_value as a percentage.
        self.duration = duration
        self.stat_mods = stat_mods or {}

        # Reactive proc payload this ability's resulting BUFF/DEBUFF
        # carries (see combat/status_effects.py's ProcTrigger and
        # StatusEffectMixin.fire_proc_trigger for the full schema:
        # trigger/chance/icd + one of grant_resource/bonus_pct/
        # apply_effect/extra_attack). None (the default, and every
        # ability authored before this system existed) means the
        # resulting buff/debuff is purely passive stat_mods, exactly as
        # before. Only meaningful for effect_type="buff"/"debuff" - other
        # effect_types don't produce a StatusEffect for this to attach to.
        self.proc = proc or None

        # Real "execute-style" HP gate: this ability can only target an
        # enemy at or below this % of their max health (e.g. Warrior
        # Execute's real 20%, Stormbringer Electrocute's real 35% - the
        # exact field name/convention already existed as dead data on
        # Electrocute's JSON before this, documented but never actually
        # enforced anywhere in use()/_apply_effect - see the "bypass"
        # check below for how Sudden Death/an equivalent talent removes
        # this gate temporarily). None (the default) means no gate at
        # all - every ability that doesn't set this is completely
        # unaffected, including the many abilities that were silently
        # castable on any-HP targets before this existed (that's not a
        # new restriction on them, just this one flag staying opt-in).
        self.execute_threshold_pct = execute_threshold_pct

        # Real spell school this ability's damage belongs to (Fire/Frost/
        # Nature/Shadow/Arcane/Holy - see DamageSchool in combat/
        # status_effects.py), or a tuple of two for a combined/hybrid
        # school (e.g. ("shadow", "frost") for a Shadowfrost-style
        # ability). Read by _apply_effect's damage/spell_damage/dot
        # branches to pick WHICH string/tuple gets passed to take_damage,
        # replacing the old hardcoded "magic" literal every direct-damage
        # branch used unconditionally before this existed. None (the
        # default) means this ability still uses the legacy "magic"
        # damage_type - see DamageSchool.MAGIC's docstring for why that's
        # a deliberate compatibility fallback, not a bug: abilities not
        # yet migrated to a real school keep working exactly as before,
        # they just don't interact with any of the new per-school
        # resistance stats until deliberately assigned one.
        self.damage_school = damage_school

        # Gates this ability to a specific Ranged-slot weapon_type - the
        # universal Shoot ("thrown") and Wand ("wand") actions (data/
        # abilities/_universal.json) are the only abilities that set
        # this. None (the default, every other ability) means no ranged-
        # weapon requirement at all. Checked in is_ranged_weapon_ready /
        # is_usable_by so Shoot doesn't appear usable with a Wand
        # equipped (or nothing) in the Ranged slot, and vice versa.
        self.requires_ranged_weapon = requires_ranged_weapon

        # Turn-based translation of WoW's real-time "instant cast" concept.
        # A normal ability ends the caster's turn on use (see
        # CombatEngine.execute_ability -> _end_turn). is_instant=True skips
        # that turn-consumption specifically, so casting it lets the same
        # actor act again immediately - the correct analogue for spells
        # like Swiftmend (instant by its own nature) in a turn-based
        # engine. See CombatEngine.execute_ability for where this is
        # actually read.
        self.is_instant = bool(is_instant)

        # Swiftmend's real mechanic: it doesn't just heal, it CONSUMES an
        # active Rejuvenation/Regrowth-style HoT on the target and heals
        # for an amount based on that HoT (12 sec worth of Rejuv or 18 sec
        # of Regrowth, per real WOTLK tooltips) rather than having its own
        # independent heal amount. consumes_hot=True marks an ability as
        # this special case; Ability.use()'s heal branch checks for it and
        # requires + removes a qualifying HoT rather than just healing a
        # flat/ranked amount. False means "ordinary heal", unaffected.
        self.consumes_hot = bool(consumes_hot)

        # Judgement-style detonation: this ability finds the caster's
        # currently active Seal (a BUFF StatusEffect whose `proc` payload
        # includes an "on_judgement" sub-payload - see Seal of
        # Righteousness's data), consumes it (removes the Seal buff
        # entirely - matches real WoW, Judgement always consumes the
        # Seal, even Seals with no on-hit component), and detonates that
        # payload against the target as a single instant effect. If no
        # Seal is active, the cast fails and refunds, same all-or-nothing
        # pattern as consumes_hot above. This does NOT go through
        # fire_proc_trigger's chance/ICD gate - Judgement's detonation is
        # a deliberate, guaranteed consume-on-cast, not a reactive proc.
        self.consumes_seal = bool(consumes_seal)
        # Which HoT ability_ids this ability is allowed to consume, when
        # consumes_hot=True (e.g. ["druid_rejuvenation", "druid_regrowth"]
        # for Swiftmend). Ignored when consumes_hot=False. A list rather
        # than a hardcoded Druid-only check, since other classes could
        # reuse the same "consume a HoT for a burst heal" pattern later.
        self.consumable_hot_ids = consumable_hot_ids or []

        # For effect_type="dispel" abilities (Cleanse Spirit, Remove
        # Curse, Purify, etc): which DispelType (see status_effects.py)
        # this ability removes from the target. A real dispel targets one
        # specific school - Cleanse Spirit only removes Curse effects, not
        # Poison or Disease - matching WoW's actual dispel-school system
        # rather than a generic "remove all debuffs" button.
        self.dispel_type = dispel_type

        # How many matching effects one cast removes - almost always 1 (a
        # real single-target cleanse), but Venomancer's Blight Antidote is
        # authored as "Cull 2 curse effects from an ally" - a genuine
        # mechanical distinction (a double-dispel) from every other
        # single-removal cleanse in the game, not just a bigger number.
        self.dispel_count = max(1, int(dispel_count))

        # consumes_stacks_of / duration_per_stack: Venomancer's Expulsion
        # ("Clear your Exposed Flesh stacks to poison nearby enemies for
        # 5 sec plus 1 sec per cleared stack") - the ONLY ability in the
        # game whose DoT duration scales off a stacking buff/debuff the
        # CASTER is carrying, consumed on cast. consumes_stacks_of names
        # the effect_id to look for and remove from the caster (None, the
        # default, means this ability doesn't touch any stacks - every
        # other DoT-type ability is completely unaffected).
        # duration_per_stack is the EXTRA seconds/turns added per stack
        # consumed, on top of this ability's own base `duration` - see the
        # "dot"/"spell_dot" branch of _apply_effect, which reads the
        # caster's current stack count before building the DoT's duration.
        self.consumes_stacks_of = consumes_stacks_of
        #: Pool named by a restore_resource ability, overriding the
        #: caster's primary one. See the restore_resource branch.
        self.restore_resource_type = restore_resource_type
        #: Shield payloads for a buff ability - a flat absorb, or one
        #: sized as a fraction of the RECIPIENT's max health so a
        #: party shield scales per ally. See the buff branch.
        self.absorb = absorb
        self.absorb_pct_max_health = absorb_pct_max_health
        self.duration_per_stack = duration_per_stack

        # True marks this ability's DEBUFF as a real stun/incapacitate -
        # threaded straight to StatusEffect.is_stun when the debuff is
        # applied (see the "debuff" branch of _apply_effect below).
        # False (default) for every ordinary debuff. Kyle, 2026-09-06:
        # "we will need stuns built" - replaces the flat Haste-debuff
        # placeholder pattern several talents used to stand in for a
        # missing stun mechanic (Concussion Blow, Shockwave, Shadowfury,
        # Wyvern Sting, Repentance, Silence, and others).
        self.is_stun = is_stun

        # Which persistent shapeshift form(s) (see combat/forms.py) this
        # ability requires to be cast, or None if it's usable in any form
        # (which covers most abilities). A list rather than a single form
        # since some real WoW abilities work in more than one shape (e.g.
        # a Feral ability usable in both Cat and Bear). Real WOTLK: Mangle
        # literally cannot be cast outside Bear/Cat Form at all - it's not
        # that it costs a different resource depending on form, the
        # ability itself doesn't exist to you otherwise (per Kyle: "Mangle
        # should cost rage or energy as a regular druid can't mangle").
        # Checked by is_form_ready(), NOT folded into is_learned - level/
        # talent gating happens once at refresh_rank_for_level() time, but
        # a character's form changes live during play far more often than
        # their level does, so this needs to be evaluated fresh on every
        # check rather than cached.
        #
        # Normalized to always be a list: JSON data (see _ability_from_data)
        # naturally writes a single form_id as a plain string ("spider"),
        # not a 1-element list - passing that straight through left
        # is_form_ready() doing `current in "spider"` (substring/character
        # membership on a string) instead of `current in ["spider"]` (list
        # membership), which crashed outright when current was None and
        # would have silently mismatched for any other value too.
        if isinstance(requires_form, str):
            requires_form = [requires_form]
        self.requires_form = requires_form or []

        # Some abilities aren't known from level alone - WOTLK-style
        # talent-granted spells (Wild Growth, Nourish, Chimera Shot) don't
        # exist in a character's book until the specific talent that
        # grants them has at least 1 point spent. requires_talent is a
        # simple boolean flag marking "this ability is talent-gated, do
        # not auto-learn it from level_req alone" - the actual matching
        # against which talent grants it happens by ability_id: the
        # granting talent's data declares {"unlock_ability": "<this
        # ability's ability_id>"} in its effects (see TalentNode), and
        # Character.get_talent_unlocked_abilities() aggregates those into
        # a flat list of ability_ids. Character._sync_talent_unlocked_
        # abilities() is what actually checks self.ability_id against
        # that list and sets talent_unlocked below - this class doesn't
        # reach back into Character itself.
        # False (the default) means "no talent gate" - level_req alone
        # decides is_learned, same as every ability before this existed.
        self.requires_talent = bool(requires_talent)

        # buff_scope distinguishes WoW's two buff archetypes, per Kyle:
        # a raid buff (Power Word: Fortitude, Mark of the Wild, Blessing of
        # Might/Kings, Battle Shout, Arcane Intellect, Demon Armor) is cast
        # once and just sits there for 30 real minutes, castable in or out
        # of combat, surviving between fights - vs a short combat cooldown
        # (Icy Veins, Divine Shield, Ice Barrier, Power Word: Shield,
        # Evasion, Adrenaline Rush, Lightning Shield, Aspect of the Hawk)
        # that's turn-based and expires within the same fight it was cast
        # in. Same is true for enemy debuffs, and for monster self-buffs
        # like Frenzy - those always default to "combat" (see below), since
        # a monster's cooldown has no business outliving the pull.
        #   "raid"    -> real_time_seconds = BUFF_DURATION_SECONDS (30 min)
        #   "combat"  -> real_time_seconds = None (turn-based via `duration`)
        # Defaults to "raid" for buffs (matches most player buffs authored
        # so far) and "combat" for debuffs (a weakening effect outlasting
        # the fight it was cast in has never been the intent here).
        if buff_scope not in ("raid", "combat"):
            buff_scope = "raid" if effect_type == "buff" else "combat"
        self.buff_scope = buff_scope

        # Who this ability is aimed at. Previously there was no such concept:
        # `buff` and `hot` were hardcoded to apply to the CASTER and silently
        # discarded whatever target they were handed. That made every buff in
        # the game self-only (a Priest could not put Fortitude or a shield on
        # anyone) and quietly broke the "smart heal" targeting for HoTs -
        # combat carefully picked the most wounded ally, then Renew landed on
        # the healer regardless.
        if target_type not in self.TARGET_TYPES:
            target_type = self.DEFAULT_TARGET_TYPE.get(effect_type, "enemy")
        self.target_type = target_type

        # max_targets: caps an "enemy_aoe" hit to N targets instead of
        # every living enemy in the fight - a real, distinct mechanic from
        # the flat AOE_DAMAGE_MULTIPLIER penalty. Several abilities are
        # tooltip-explicit about a SPECIFIC target count rather than true
        # unlimited AoE (Runemaster's Fist of the Ancients: "your target
        # and A nearby enemy" = 2; Stormbringer's Forked Lightning: "arcs
        # to strike up to 3 enemies"), which target_type="enemy_aoe" alone
        # can't express - before this field existed, authoring one of
        # these as enemy_aoe silently over-hit every enemy in the fight,
        # the exact bug this fixes for Fist of the Ancients. None (the
        # default) means genuinely unlimited, matching every enemy_aoe
        # ability authored before this field existed. Only meaningful
        # when target_type == "enemy_aoe"; ignored otherwise.
        self.max_targets = max_targets
        # force_proc_group: Venomancer's Barbed Stinger - a taunt that
        # "forces" whichever single Venom buff (Debilitating/Rejuvenating/
        # Nullifying/Blight, all sharing exclusive_group=
        # "venomancer_venom_slot_a") is currently active to fire its proc
        # immediately on this cast, bypassing that Venom's normal ~20-30%
        # chance roll entirely (Kyle, Oct 2026: "the venom barb forces
        # both venoms to proc... usually in the form of a dot on the
        # enemy when used by tank" - "both" referred to real WoW's 2-slot
        # Venom system; Kyle separately decided to keep this engine at
        # 1-Venom-at-a-time, so here it forces the one active Venom).
        # None (the default) means no forcing - every ability authored
        # before this field existed is unaffected. See the debuff branch
        # of use() for where this actually looks up and fires the active
        # Venom's proc; a value is only acted on when effect_type ==
        # "debuff", since Barbed Stinger's own effect is the taunt itself.
        self.force_proc_group = force_proc_group

        self.current_rank_index = 0  # index into self.ranks; refreshed by refresh_rank_for_level()
        # Set properly by refresh_rank_for_level(); defaults True so any
        # ability constructed and used without a level refresh still works.
        self.is_learned = True
        # Class trainers (Oct 2026): a trainable ability is only KNOWN, and only at the rank bought, once the player has
        # paid a class trainer (Character.trained_ranks).  Talent abilities, the universal Shoot/Wand and every companion's
        # book are not trainable - they keep the old "known from level" behaviour.
        self.trainable = False

        # Only meaningful when requires_talent is set. Character sets this
        # directly (see _sync_talent_unlocked_abilities) rather than
        # Ability reaching back into Character - defaults True so an
        # ability with no talent gate is never accidentally blocked here.
        self.talent_unlocked = True

        # Cryotherapist (Mage/Frost): once the Cryobolt/Cryolance talent is
        # spent, Frostbolt/Ice Lance THEMSELVES start also smart-healing the
        # lowest-HP% ally on every cast - no new hotbar button, per Kyle
        # ("the actual Frostbolt/Ice Lance just also heals"). Character sets
        # this directly, mirroring talent_unlocked above, rather than
        # mutating effect_type in place - effect_type also drives
        # DEFAULT_TARGET_TYPE and other lookups at construction time, so
        # flipping it live would be one more hidden state transition to
        # reason about. _apply_effect's spell_damage branch checks this flag
        # and runs the damage_and_heal path instead when it's set. False for
        # every ability by default - only Character ever sets it True, only
        # ever on mage_frostbolt/mage_ice_lance.
        self.cryo_converted = False

        # Only meaningful for effect_type="damage_and_heal". Controls how
        # many allies get smart-healed (lowest HP% first) and whether it's
        # "everyone" vs "the N neediest":
        #   "lowest_ally" (default) - smart-heals exactly 1 ally.
        #     Cryobolt/Cryolance's per-cast proc.
        #   "party" - heals every living ally for the same amount each.
        #     Frostfall's capstone - its damage is already AoE, so the heal
        #     matches that scope instead of singling anyone out.
        #   int N - smart-heals the N neediest living allies (lowest HP%
        #     first), same targeting priority as "lowest_ally" just widened.
        #     Icy Penance heals 3 allies this way per Kyle.
        self.heal_scope = heal_scope if heal_scope in ("lowest_ally", "party") or isinstance(heal_scope, int) else "lowest_ally"

    def refresh_rank_for_level(self, level, trained_rank=None):
        """Update current_rank_index to the highest rank this level qualifies
        for. Called by Character whenever level changes (level-up, load from
        save, prestige reset).

        trained_rank: None = ordinary level-based learning.  An int (0 = never trained, n = rank n bought from a class
        trainer) only matters for `trainable` abilities: the ability is unknown at 0, and the rank in use is capped at
        the trained one even when the level would allow more.  Training a higher rank later raises the cap."""
        best = 0
        for i, r in enumerate(self.ranks):
            if level >= r["level_req"]:
                best = i
            else:
                break
        trained_gate = True
        if trained_rank is not None and self.trainable:
            if trained_rank < 1:
                trained_gate = False
            else:
                best = min(best, trained_rank - 1)
        self.current_rank_index = best

        # An ability is only KNOWN once the character reaches rank 1's level
        # requirement. Previously this method clamped to rank 0 regardless,
        # so every ability in a class's book was castable from level 1 - a
        # level 1 Warrior could open with Mortal Strike (learned at 30) at
        # full rank-1 power. Now unlearned abilities report is_learned()
        # False, and the UI/hotbar filter on it.
        #
        # A talent-granted ability (requires_talent=True) also needs its
        # talent_unlocked flag True - level alone isn't enough for Wild
        # Growth-style spells that only exist once their talent point is
        # spent. talent_unlocked defaults True for ordinary abilities
        # (requires_talent=False), so this AND has no effect on them.
        level_met = level >= self.ranks[0]["level_req"]
        if self.requires_talent:
            # A talent-granted ability is known the moment its talent has a point in it: the talent IS the lesson.  (It
            # used to also demand rank 1's level, so a level-12 Warrior who took Mortal Strike - rank 1 at level 30 -
            # never actually got it.)  Higher ranks still come from level via current_rank_index.
            self.is_learned = bool(self.talent_unlocked)
        else:
            self.is_learned = level_met and self.talent_unlocked and trained_gate

    def is_form_ready(self, character):
        """True if this ability's form/stance requirement (if any) is
        currently satisfied. Abilities with no requires_form are always
        ready (returns True regardless of character).

        requires_form values can be either shapeshift form_ids (combat/
        forms.py - "bear", "cat", ...) or Warrior stance_ids (combat/
        stances.py - "battle", "berserker", ...). One list rather than
        two separate mechanisms since both are the same underlying
        concept for gating purposes: "character must currently be in
        state X". Checked against BOTH current_form and current_stance so
        a single requires_form list works regardless of which system the
        character actually has active - a Warrior's current_form is
        always None (Warriors don't shapeshift) so the form check simply
        never matches for them, and vice versa for Druids/Priests and
        current_stance.
        """
        if not self.requires_form:
            return True
        current = getattr(character, "current_form", None) or getattr(character, "current_stance", None)
        if current in self.requires_form:
            return True
        # Real Tinker Mechsuit check - current_mechsuit is a bool, not a
        # form_id string, so it can't be compared against requires_form's
        # list of real ids the way current_form/current_stance are. The
        # real "form id" this checks against is the literal string
        # "mechsuit" - an ability that should only be usable while
        # Mechsuit is active sets requires_form=["mechsuit"] in its JSON.
        if getattr(character, "current_mechsuit", False) and "mechsuit" in self.requires_form:
            return True
        return False

    def is_ranged_weapon_ready(self, character):
        """True if this ability's requires_ranged_weapon (if any) matches
        the character's currently-equipped Ranged-slot weapon_type.
        Abilities with no requirement are always ready. A missing/None
        Ranged item, or one of the wrong weapon_type (e.g. Wand equipped
        while checking Shoot's requirement), returns False - this is what
        keeps Shoot and Wand mutually exclusive based on what's actually
        equipped, rather than both always showing up.

        requires_ranged_weapon accepts EITHER a single weapon_type string
        (backward compatible with the original "wand"-only Wand gate) OR
        a list/tuple/set of weapon_types - Shoot needs this because real
        ranged-physical weapons now span 4 distinct types (thrown/bow/
        gun/crossbow, added this session per Kyle's ask to keep them
        genuinely separate rather than one generic "ranged" catch-all),
        any of which should make Shoot usable."""
        if not self.requires_ranged_weapon:
            return True
        ranged_item = character.equipment.get_ranged_weapon() if hasattr(character, "equipment") else None
        if not ranged_item:
            return False
        equipped_type = getattr(ranged_item, "weapon_type", None)
        if isinstance(self.requires_ranged_weapon, (list, tuple, set)):
            return equipped_type in self.requires_ranged_weapon
        return equipped_type == self.requires_ranged_weapon

    def is_usable_by(self, character):
        """True if the character has learned this ability, it's off
        cooldown, they can currently AFFORD its resource cost, AND (for
        form-gated abilities like Mangle) they're currently in a form
        that allows it. Cheaper for callers than checking all these
        separately.

        The resource-affordability check was missing here until now -
        is_usable_by only ever checked learned/cooldown/form/ranged-
        weapon, never whether the caster could actually PAY for the
        ability. That made the hotbar button render bright green
        ("ready") for an ability the caster had 0 chance of successfully
        casting - worst case, a Static/Insanity/Runes-style secondary-
        resource spender (Stormbringer's Torrential Wrath, Cultist's
        Wrath of the Black Empire, ...) that's NEVER affordable until a
        separate builder ability has been cast first. A player sees a
        green "ready" button, clicks it, gets a text-log failure message
        with no visual warning beforehand - exactly the "my skills don't
        work" confusion this exists to fix. Uses the real
        talented_cost()/_has_resource() pair use() itself calls, so this
        can never disagree with what an actual cast would do.
        """
        return (getattr(self, "is_learned", True)
                and self.is_available()
                and self.is_form_ready(character)
                and self.is_ranged_weapon_ready(character)
                and self._has_resource(character, self.talented_cost(character)))

    @property
    def current_rank(self):
        return self.ranks[self.current_rank_index]

    @property
    def active_proc(self):
        """The proc payload this ability's buff/debuff carries at its CURRENT rank.

        A rank dict may hold a partial "proc" override (e.g. {"bonus_pct": 0.18} or {"chance": 24}) that is merged
        over the ability's base proc, so weapon imbues, seals and shields grow with rank instead of staying flat.
        Nested payloads (grant_resource, on_judgement, apply_effect) are replaced whole, so give the full dict.
        """
        if not self.proc:
            return None
        override = self.current_rank.get("proc")
        if not override:
            return self.proc
        merged = dict(self.proc)
        merged.update(override)
        return merged

    @property
    def rank_number(self):
        return self.current_rank["rank"]

    @property
    def max_rank_number(self):
        return self.ranks[-1]["rank"]

    @property
    def cost(self):
        return self.current_rank["cost"]

    @property
    def effect_value(self):
        return self.current_rank["effect_value"]

    @property
    def heal_value(self):
        """Secondary heal magnitude for effect_type="damage_and_heal"
        (Cryotherapist). A separate key from effect_value (which carries the
        damage side for this effect_type) so damage and healing can be
        ranked/balanced independently, same as how a real Cryotherapist
        rank might buff one without the other. Defaults to 0 so every
        existing ability's rank data - none of which has this key - keeps
        working unchanged.
        """
        return self.current_rank.get("heal_value", 0)

    @property
    def mana_restore_pct(self):
        """% of max Mana restored for effect_type="damage_and_restore_mana"
        (Stormbringer's Discharge). Same pattern as heal_value - a separate
        rank key so the mana-return and damage sides can be tuned
        independently. Defaults to 0 so every other ability's rank data
        keeps working unchanged.
        """
        return self.current_rank.get("mana_restore_pct", 0)

    @property
    def next_rank_level_req(self):
        """Level at which the next rank unlocks, or None if already max rank."""
        if self.current_rank_index + 1 < len(self.ranks):
            return self.ranks[self.current_rank_index + 1]["level_req"]
        return None

    def get_tooltip_lines(self, caster=None):
        """Real hover-tooltip content for this ability, at its CURRENT rank.

        EFFECT VALUES stay RAW - straight off current_rank, before Spell
        Power/talents/crit - matching Kyle's real WoW reference screenshots:
        Lightning Bolt's tooltip shows "429 to 478 Nature damage" as a flat
        rank-defined number, not the caster's computed damage.

        COST AND COOLDOWN are different, and used to be wrong. WoW shows the
        TALENTED cost: a Paladin with Benediction sees Crusader Strike's
        reduced mana cost in the tooltip, not the base. Showing the base here
        made every cost-reduction talent in the game look broken - Kyle,
        2026-10-26: "crusader strike mana reduction with ret paladin doesnt
        reduce mana cost". The reduction was real and the spend path was
        already correct (use() passes talented_cost to both _has_resource and
        _consume_resource); only the number on screen lied about it.

        caster is optional. Without one this behaves exactly as before, so
        any caller that has no character in hand still works - it just shows
        the untalented cost, which is the best that can be said without
        knowing whose tooltip it is.

        Returns a list of plain strings, one per line, in a fixed real
        order: name+rank, cost+cast time, base value line(s) by
        effect_type, then the description. Callers (cast_screen.py,
        combat_screen.py, skills_screen.py, talent_tree_screen.py) render
        these into whatever tooltip box each screen already draws -
        this method only builds the TEXT, not any pygame Rect/positioning,
        so one real implementation serves every screen rather than
        duplicating the wording logic four times.
        """
        lines = []
        rank_suffix = f" (Rank {self.rank_number})" if len(self.ranks) > 1 else ""
        lines.append(f"{self.name}{rank_suffix}")

        cost_bits = []
        if self.cost:
            # Real resource name (Mana/Rage/Energy/Static/Insanity/...)
            # instead of a bare "Cost: N" - the old generic wording made
            # a secondary-resource spender (Stormbringer's Torrential
            # Wrath costing Static, Cultist's Wrath of the Black Empire
            # costing Insanity, ...) look exactly like an ordinary Mana
            # ability in its own tooltip, with nothing telling the player
            # WHICH pool to watch or that it's a different pool from the
            # class's main bar. self.resource_type is always a real
            # ResourceType on every ability (set at construction), so
            # this never needs a caster in hand the way the old comment
            # claimed - "Cost: 40 Static" reads the same whether or not
            # the player has 40 Static banked right now.
            resource_label = self.resource_type.value.replace("_", " ").title()
            shown_cost = self.talented_cost(caster) if caster is not None else int(self.cost)
            cost_bits.append(f"Cost: {shown_cost} {resource_label}")
        if self.is_instant:
            cost_bits.append("Instant")
        if self.cooldown:
            shown_cd = self.talented_cooldown(caster) if caster is not None else self.cooldown
            if shown_cd:
                cost_bits.append(f"{shown_cd} turn cooldown")
        if cost_bits:
            lines.append("  |  ".join(cost_bits))

        # Builder/spender callout (Stormbringer Shock->Static,
        # Cultist's Insanity builders, ...): without this line, nothing
        # in the ability's OWN tooltip tells a player it's quietly
        # banking a second resource their payoff ability needs - the
        # secondary resource bar (combat_screen._draw_secondary_resource)
        # shows the pool exists, but not which button fills it. This is
        # the single biggest real fix for "my best ability is never
        # castable" confusion on every builder/spender CoA class.
        if self.generates:
            gen_resource = self.generates.get("resource")
            gen_amount = self.generates.get("amount", 0)
            if gen_resource and gen_amount:
                gen_label = str(gen_resource).replace("_", " ").title()
                lines.append(f"Generates {int(gen_amount)} {gen_label}")

        # Real base-value line(s), phrased per effect_type - the actual
        # "before modifiers" numbers Kyle asked for.
        if self.effect_type in ("damage", "spell_damage"):
            lines.append(f"Base damage: {self.effect_value}")
        elif self.effect_type in ("dot", "spell_dot"):
            lines.append(f"Base damage: {self.effect_value} over {self.duration} turns")
        elif self.effect_type == "heal":
            lines.append(f"Base healing: {self.effect_value}")
        elif self.effect_type == "hot":
            lines.append(f"Base healing: {self.effect_value} over {self.duration} turns")
        elif self.effect_type == "damage_and_heal":
            lines.append(f"Base damage: {self.effect_value}  |  Base healing: {self.heal_value}")
        elif self.effect_type == "damage_and_restore_mana":
            lines.append(f"Base damage: {self.effect_value}  |  Restores {self.mana_restore_pct}% mana")
        elif self.effect_type in ("buff", "debuff") and self.stat_mods:
            mod_bits = [f"{k.replace('_', ' ').title()} {'+' if v >= 0 else ''}{v}"
                        for k, v in self.stat_mods.items()]
            lines.append(", ".join(mod_bits))

        if self.description:
            lines.append(self.description)

        return lines

    # ------------------------------------------------------------------
    # TALENT INTEGRATION (Phase 4.5b)
    # ------------------------------------------------------------------
    # Talents modify abilities through three effect keys, all resolved
    # against this ability's ability_id:
    #   ability_<id>_damage   -> multiplier on effect_value  (0.10 = +10%)
    #   ability_<id>_cost     -> flat resource cost reduction (5 = -5 cost)
    #   ability_<id>_cooldown -> flat cooldown turn reduction
    # Plus the global keys all_damage / physical_damage / spell_damage /
    # healing_done which stack multiplicatively on top per school.
    #
    # Monsters have no talent_trees attribute, so every lookup degrades to
    # the neutral value for them - no branching needed at the call sites.

    def _talent(self, caster, key, default=0.0):
        getter = getattr(caster, "get_talent_effect", None)
        if getter is None:
            return default
        try:
            return getter(key, default)
        except Exception:
            return default

    def talented_cost(self, caster):
        """Resource cost after talent reductions (never below 0).

        Two kinds stack, flat first then percentage:
          ability_<id>_cost      flat reduction, e.g. 8 -> 8 less Mana
          ability_<id>_cost_pct  fractional reduction, e.g. 0.05 -> 5% cheaper
          all_ability_cost_pct   the same, applied to everything
          heal_cost_pct          the same, healing abilities only
          healing_spell_cost_pct alias of heal_cost_pct

        Only the flat form was ever read. Twenty-nine talents across every
        homebrew class were authored as a percentage ("Reduces the Mana cost
        of your Shock spells by 3%") and did nothing at all, because a
        percentage cost reduction is the natural way to word this and nothing
        implemented it.
        """
        reduction = self._talent(caster, f"ability_{self.ability_id}_cost")
        cost = max(0, int(round(self.cost - reduction)))
        if cost <= 0:
            return 0
        pct = self._talent(caster, f"ability_{self.ability_id}_cost_pct")
        pct += self._talent(caster, "all_ability_cost_pct")
        if self.effect_type in ("heal", "hot"):
            pct += self._talent(caster, "heal_cost_pct")
            pct += self._talent(caster, "healing_spell_cost_pct")
        # Clamped so a stack of reductions discounts rather than inverts.
        pct = min(0.90, max(-0.90, pct))
        return max(0, int(round(cost * (1.0 - pct))))

    def talented_duration(self, caster):
        """Effect duration in turns after talent extensions.

        Completes the talented_cost/talented_cooldown pair. Authored as
        ability_<id>_duration and never read until now, so a talent extending
        a buff - Tinker's Fuel Injection on Mechsuit Form - did nothing.
        Positive values EXTEND, matching how those talents are worded
        ("increases the duration of X by N").

        An ability with NO duration stays at 0. The floor used to be an
        unconditional max(1, ...), which handed a phantom 1-turn duration to
        every instant ability in the game - Wrath, Shred and Swiftmend all
        reported "1 turn" where they have no duration at all. Only an
        ability that genuinely has a duration keeps a minimum of 1.
        """
        if not self.duration:
            return 0
        bonus = self._talent(caster, f"ability_{self.ability_id}_duration")
        return max(1, int(round(self.duration + bonus)))

    def talented_cooldown(self, caster):
        """Cooldown in turns after talent reductions.

        An ability that HAS a cooldown keeps at least 1 turn of it. The old
        floor was 0, which let stacked talents delete a cooldown outright and
        turn the ability into a spammable one - tools/check_talent_balance.py
        found eight abilities doing exactly that at max talents (Warrior's
        Rend via Intensify Rage, Paladin's Judgement, Hunter's Arcane Shot and
        Multi-Shot, Rogue's Backstab and Eviscerate, Priest's Heal, Shaman's
        Earth Shock). Several were -1/rank over 3 ranks against a 2-turn base,
        so they went negative before the clamp.

        Flooring here rather than in each talent's data keeps the guarantee
        global: no future talent can reduce a cooldown past this, and the
        reduction stays worth taking (2 -> 1 is still a doubled cast rate).
        Abilities with no cooldown to begin with stay at 0.
        """
        if not self.cooldown:
            return 0
        reduction = self._talent(caster, f"ability_{self.ability_id}_cooldown")
        cd = self.cooldown - reduction
        # ability_<id>_cooldown_pct is the percentage companion to the flat
        # key, and was authored by seven talents without ever being read.
        # Applied after the flat reduction, same order as talented_cost.
        pct = min(0.90, max(-0.90, self._talent(
            caster, f"ability_{self.ability_id}_cooldown_pct")))
        cd *= (1.0 - pct)
        return max(1, int(round(cd)))

    #: Real WoW-classic-style: a critical strike deals double damage.
    CRIT_DAMAGE_MULTIPLIER = 2.0

    def _roll_crit(self, caster, target, school):
        """Roll whether this hit crits. Returns (is_crit, multiplier) -
        multiplier is CRIT_DAMAGE_MULTIPLIER on a crit, 1.0 otherwise, so
        callers can just do `base_damage * multiplier` without an if/else.

        school is "physical" or "spell" - selects crit_chance_physical vs
        crit_chance_spell on the attacker. Casters/monsters without a crit
        stat (e.g. Monster) are treated as having 0% crit chance, same
        convention as hit_chance_physical's fallback elsewhere in this
        file - existing monster damage doesn't suddenly start critting
        just because this system now exists.

        Defender-side crit avoidance (Shield Specialization: "reduces the
        chance you'll be critically hit by melee attacks by 6%") is read
        from target.get_talent_effect("crit_taken_reduction") if present,
        and subtracted from the attacker's roll chance before rolling -
        mirrors how Character.take_damage's block roll already lets
        defender-side talents subtract from an attacker-favorable stat.
        Characters/Pets have get_talent_effect; Monsters don't, so
        getattr(...) defaults to 0 reduction for them same as everywhere
        else defender-side talent lookups happen in this file.
        """
        import random

        # Guaranteed-crit consumption (Fingers of Frost-style: "your next
        # spell is a guaranteed critical strike"). Checked BEFORE the
        # normal chance roll and consumes the granting effect on use,
        # same one-shot pattern as execute_threshold_pct's bypass check
        # in use() above - a guaranteed-crit proc is a single spent
        # charge, not a permanent 100% crit chance. Only consumed on a
        # REAL roll (this method being called at all means a real
        # hit/heal is resolving), so a guaranteed-crit buff sitting
        # unused when combat ends simply expires normally via its own
        # duration instead of being silently eaten by an unrelated roll.
        if hasattr(caster, "_effects"):
            guaranteed_effect = next(
                (e for e in caster._effects()
                 if getattr(e, "proc", None) and e.proc.get("guarantee_next_crit")),
                None,
            )
            if guaranteed_effect is not None:
                caster.active_effects = [e for e in caster._effects() if e is not guaranteed_effect]
                return True, self.CRIT_DAMAGE_MULTIPLIER

        key = "crit_chance_physical" if school == "physical" else "crit_chance_spell"
        crit_chance = getattr(caster, key, 0.0) or 0.0

        # Per-ability crit bonus from talents ("Increases the critical strike
        # chance of X by N%"). Authored as ability_<id>_crit but never read,
        # so any talent using it did nothing. Stored as percentage points, the
        # same unit as crit_chance_physical/_spell above.
        crit_chance += self._talent(caster, f"ability_{self.ability_id}_crit")

        crit_taken_reduction = 0.0
        if hasattr(target, "get_talent_effect"):
            crit_taken_reduction = target.get_talent_effect("crit_taken_reduction", 0.0) or 0.0
        crit_chance = max(0.0, crit_chance - crit_taken_reduction)

        is_crit = random.uniform(0, 100) < crit_chance
        if not is_crit:
            return False, 1.0
        return True, self.CRIT_DAMAGE_MULTIPLIER + self._crit_damage_bonus(caster, school)

    def _school_damage_bonus(self, caster):
        """School-specific spell damage, e.g. nature_spell_damage.

        Seven talents word their bonus by school rather than globally
        ("increases your Nature spell damage by 4%") and the keys were read by
        nothing. Both <school>_spell_damage and <school>_damage_pct are
        accepted, and so are COMBINED keys like nature_fire_spell_damage,
        which match if the ability's real school is any named component.
        Resolved against the school the ability actually deals this cast, so
        Runemaster's live attunement cycle is respected.
        """
        # An ability's damage_school may be a LIST of schools - Sun Cleric's
        # Radiant Flame and Hammer of Kings are ["holy", "fire"]. Bailing out
        # on those meant a combined-school ability could never receive ANY
        # school damage bonus, not even a combined key naming both of its own
        # schools. Each component is considered instead, which is the same
        # any-component rule the combined KEYS already use below.
        real = self._resolve_damage_school(caster)
        schools = ([real] if isinstance(real, str)
                   else [s for s in (real or []) if isinstance(s, str)])
        if not schools:
            return 0.0
        bonus = 0.0
        for real in schools:
            bonus += (self._talent(caster, f"{real}_spell_damage")
                      + self._talent(caster, f"{real}_damage_pct"))
        effects = (caster.get_talent_effects()
                   if hasattr(caster, "get_talent_effects") else {}) or {}
        for key, val in effects.items():
            if not isinstance(key, str) or not isinstance(val, (int, float)):
                continue
            for suffix in ("_spell_damage", "_damage_pct"):
                if key.endswith(suffix):
                    parts = key[:-len(suffix)].split("_")
                    # Only COMBINED keys here; the single-school case is
                    # already counted above and must not be double-added.
                    # Matched against any of the ability's own schools, so a
                    # combined-school ability is covered too.
                    if len(parts) > 1 and any(s in parts for s in schools):
                        bonus += val
                    break
        return bonus

    def _conditional_healing_bonus(self, caster):
        """Healing bonuses conditional on the caster's own mana.

        low_mana_healing_pct and high_mana_healing_pct are the "desperate" and
        "well-supplied" halves of a real healer mechanic, authored by eight
        homebrew talents and read by nothing. The threshold reuses
        low_health_threshold_pct's default of 35% so it matches every other
        conditional in this engine rather than inventing a second number.

        low_health_healing_pct is deliberately NOT handled here: it keys off
        the RECIPIENT's health, and _damage_multiplier has no recipient. It
        stays dead until the heal path threads a target through, and the audit
        keeps flagging it rather than it being quietly dropped.
        """
        # NOTE the naming trap: on Character, `mana` is the MAXIMUM and
        # `current_mana` is the live pool - exactly like `health` vs
        # `current_health`. Reading "max_mana" (which does not exist) or
        # treating `mana` as current both silently yield a wrong fraction;
        # the first attempt at this used getattr(caster, "max_mana", 0) and
        # the whole feature was dead because that default is 0.
        max_mana = getattr(caster, "mana", 0) or 0
        if not max_mana:
            return 0.0
        frac = (getattr(caster, "current_mana", 0) or 0) / max_mana
        threshold = 0.35
        if hasattr(caster, "get_talent_effect"):
            threshold = caster.get_talent_effect("low_health_threshold_pct", 0.35) or 0.35
        if frac <= threshold:
            return self._talent(caster, "low_mana_healing_pct")
        if frac >= 1.0 - threshold:
            return self._talent(caster, "high_mana_healing_pct")
        return 0.0

    def _crit_damage_bonus(self, caster, school):
        """Extra crit multiplier from talents, added to CRIT_DAMAGE_MULTIPLIER.

        "Increases the critical strike DAMAGE of your spells by 30%" is a
        different mechanic from increasing crit chance, and eleven talents
        across Cultist, Runemaster, Starcaller and Mage were authored for it
        under crit_damage_spell, crit_damage_physical, crit_damage_pct,
        <school>_crit_damage_pct and ability_<id>_crit_damage. None of those
        keys were read by anything, so every one of those talents did nothing.

        All are FRACTIONS of the base hit (0.30 = crits hit for 2.3x instead
        of 2.0x), which is how the data already authors them, and they stack
        additively with each other the same way every other talent bonus in
        this engine does.
        """
        bonus = self._talent(caster, "crit_damage_pct")
        bonus += self._talent(
            caster, "crit_damage_physical" if school == "physical" else "crit_damage_spell")
        bonus += self._talent(caster, f"ability_{self.ability_id}_crit_damage")
        # Per-school flavour (fire_crit_damage_pct and friends), resolved
        # against the school this ability actually deals this cast.
        real_school = self._resolve_damage_school(caster)
        if isinstance(real_school, str):
            bonus += self._talent(caster, f"{real_school}_crit_damage_pct")
        return bonus

    def _resolve_damage_school(self, caster):
        """Real school this ability deals THIS cast, resolving
        DamageSchool.ATTUNEMENT (Runemaster's live Frost/Fire/Arcane
        cycle - see StatusEffectMixin._tick_attunement) to whatever the
        caster is actually attuned to right now. Every other
        self.damage_school value (a fixed school, a combined-school
        list/tuple, or None) passes through unchanged - this is purely
        the attunement substitution point, not a general damage_school
        accessor, which is why every take_damage call site still reads
        `self.damage_school` directly for everything except going through
        here first when attunement matters.

        Falls back to "arcane" if the caster has no live
        current_attunement yet (matches DamageSchool.ATTUNEMENT's
        documented fallback - see its docstring).
        """
        if self.damage_school != DamageSchool.ATTUNEMENT:
            return self.damage_school
        return getattr(caster, "current_attunement", None) or DamageSchool.ARCANE

    def _damage_multiplier(self, caster, school, recipient=None):
        """Combined talent multiplier for this ability in a given school.

        school is "physical", "spell" or "healing" - selects which global
        key stacks alongside the per-ability one.
        """
        per_ability = self._talent(caster, f"ability_{self.ability_id}_damage")
        if school == "healing":
            # A heal's per-ability talent key reads more naturally as
            # ability_<id>_healing, and 18 talents across Cultist,
            # Venomancer, Starcaller and Stormbringer were authored that way
            # - but only _damage was ever looked up, so every one of them
            # silently did nothing. Both are accepted now: _healing is the
            # name that belongs on a heal, _damage keeps working for anything
            # already using it.
            per_ability += self._talent(caster, f"ability_{self.ability_id}_healing")
            global_key = self._talent(caster, "healing_done")
            global_key += self._conditional_healing_bonus(caster)
            # low_health_healing_pct: "your heals are N% stronger on targets
            # below X% health" - four homebrew talents, previously dead
            # because this method had no idea who was being healed. The heal
            # call sites now pass the recipient. Falls back to no bonus when
            # the recipient is unknown (a smart heal has not picked one yet).
            if recipient is not None:
                bonus = self._talent(caster, "low_health_healing_pct")
                if bonus:
                    max_hp = getattr(recipient, "health", 0) or 0
                    cur_hp = getattr(recipient, "current_health", None)
                    if max_hp and cur_hp is not None:
                        threshold = 0.35
                        if hasattr(caster, "get_talent_effect"):
                            threshold = caster.get_talent_effect(
                                "low_health_threshold_pct", 0.35) or 0.35
                        if cur_hp / max_hp <= threshold:
                            global_key += bonus
        elif school == "spell":
            global_key = (self._talent(caster, "spell_damage")
                          + self._talent(caster, "all_damage")
                          + self._school_damage_bonus(caster))
        else:
            global_key = (self._talent(caster, "physical_damage")
                          + self._talent(caster, "all_damage"))

        # Damage-type multipliers, independent of school: an AoE bonus and the
        # per-type DoT bonuses (bleed_dot_damage, poison_dot_damage,
        # nature_dot_damage, aoe_damage). Five talents were authored on these
        # and none were read.
        if school != "healing":
            if self.target_type == "enemy_aoe":
                global_key += self._talent(caster, "aoe_damage")
            if self.effect_type in ("dot", "spell_dot"):
                global_key += self._talent(caster, "dot_damage")
                real = self._resolve_damage_school(caster)
                if isinstance(real, str):
                    global_key += self._talent(caster, f"{real}_dot_damage")
                # bleed_dot_damage / poison_dot_damage name a flavour rather
                # than a school, so they key off the ability id instead.
                for flavour in ("bleed", "poison"):
                    if flavour in self.ability_id:
                        global_key += self._talent(caster, f"{flavour}_dot_damage")

        # Temporary BUFF-granted damage/healing-done cooldowns (CoA's
        # damage_dealt_pct / healing_done_pct - Voidborne, Blessing of
        # Triumph, March of the Valkyr, Runic Power, Champion of the Sun,
        # Visions, ...) stack on top of the talent-based multiplier the
        # same way the threat_generation_pct buff fix stacks on top of
        # Earthen Guardian's talent - sourced from an active status effect
        # instead of a spent talent point, same +N% MORE convention.
        # damage_dealt_pct is school-agnostic here (one generic "your
        # outgoing damage" buff, not separate physical/spell pools) -
        # several CoA abilities originally used school-specific names
        # (magic_damage_pct, spell_damage_pct, shadow_damage_pct,
        # holy_damage_bonus_pct) that got folded into this single key
        # during the stat-vocabulary cleanup, since this engine has no
        # separate physical-dealt-% buff distinct from the generic one.
        buff_key = "healing_done_pct" if school == "healing" else "damage_dealt_pct"
        buff_pct = 0.0
        if hasattr(caster, "get_status_stat_mod"):
            buff_pct = caster.get_status_stat_mod(buff_key) or 0.0

        return (1.0 + per_ability) * (1.0 + global_key) * (1.0 + buff_pct / 100.0)

    def is_available(self):
        """Check if ability is off cooldown."""
        return self.turns_remaining <= 0
    
    def use(self, caster, target=None, party=None, in_combat=True, free=False):
        """Use the ability. Returns success and message.

        `party` is an optional list of the caster's living allies, supplied
        by the call site (cast_panel/cast_screen/combat_engine already have
        this on hand). It's only consulted by effect_type="damage_and_heal"
        abilities (Cryotherapist) to find the lowest-HP ally to heal; every
        other effect_type ignores it, so passing None is always safe for
        abilities that don't need it.

        `in_combat` gates whether this cast sets/consumes cooldowns. Real
        WoW/CoA cooldowns are meant to throttle repeated fight-power (burst
        heals, nukes) turn-to-turn, not punish someone for topping the party
        off between fights - so out-of-combat casts (cast_panel.py, the only
        caller that ever passes False) still check is_available() to respect
        a cooldown already running FROM a fight, but never SET one of their
        own. Defaults True so every combat/monster call site (combat_engine,
        totem summon-through-use, etc) is untouched by this change.

        `free` (new): True skips the resource check/consume AND cooldown-
        check/set entirely - a genuine "no Mana cost" proc-triggered cast
        (Tinker's Build: Scrapmaw: "...your basic attacks have a 10%
        chance to fire an additional Scrap Shot at no Mana cost"), not a
        player action. Defaults False so every existing caller (which all
        want real resource/cooldown rules enforced) is completely
        unaffected. Still respects is_learned and the stun/execute-
        threshold gates just above - "free" means the resource is waived,
        not that every other cast requirement is skipped too.
        """
        # Refuse unlearned abilities outright - a hotbar left over from a
        # prestige reset (level 60 -> 1) would otherwise still fire them.
        if not getattr(self, "is_learned", True):
            return False, f"{self.name} has not been learned yet."

        # Check cooldown - still respected out of combat (a heal cast mid-
        # fight and still ticking down shouldn't be free to spam the second
        # you step out of combat), just never SET by an out-of-combat cast.
        # A free=True proc cast skips this check entirely (Scrap Shot has
        # its own cooldown of 0 anyway, but a future free-proc ability
        # with a real cooldown shouldn't be blocked by its own cooldown
        # clock just because this specific cast didn't start it).
        if not free and not self.is_available():
            return False, f"{self.name} is on cooldown ({self.turns_remaining} turns remaining)"

        # Execute-style HP gate (Warrior Execute's real 20%, Stormbringer
        # Electrocute's real 35%, ...). Checked BEFORE resource consumption
        # - a failed "target isn't low enough" cast shouldn't cost Rage/
        # Mana, matching how the resource check itself already fails
        # before spending anything. Bypassed if the caster carries a
        # status effect with proc["bypass_execute_threshold"] set (e.g.
        # Sudden Death/Fingers of Frost-style "your next X ignores its
        # normal restriction" talents) - checked via the same _effects()
        # a real proc reads, not a special-cased talent lookup, so any
        # future ability/talent can grant this bypass the same way.
        if self.execute_threshold_pct is not None and target is not None:
            bypassed = any(
                getattr(e, "proc", None) and e.proc.get("bypass_execute_threshold")
                for e in caster._effects()
            ) if hasattr(caster, "_effects") else False
            if not bypassed:
                target_pct = (target.current_health / target.health * 100.0) if getattr(target, "health", 0) else 100.0
                if target_pct > self.execute_threshold_pct:
                    return False, f"{target.name} is above {self.execute_threshold_pct}% health - {self.name} requires a wounded target."
            elif hasattr(caster, "_effects"):
                # Consume the bypass - Sudden Death-style procs are a
                # single guaranteed-usable window, not a permanent
                # "ignore HP requirement forever" state. Removes every
                # effect that granted a bypass (normally just one) so the
                # next Execute/Electrocute goes back to needing a real
                # wounded target.
                caster.active_effects = [
                    e for e in caster._effects()
                    if not (getattr(e, "proc", None) and e.proc.get("bypass_execute_threshold"))
                ]

        # Check resource (talent-reduced cost) - entirely skipped for a
        # free=True proc cast ("at no Mana cost" is the literal tooltip
        # wording, not "at a discounted cost"), cost reported as 0 to
        # _apply_effect/the return message rather than this ability's
        # real cost, since nothing was actually spent.
        # Shapeshifting while already shapeshifted is free (and shifting back to
        # Normal by recasting your current form costs nothing): shifting wipes the
        # mana pool, so a charge here would trap a Bear-form Druid in Bear Form.
        if self.effect_type == "shapeshift" and getattr(caster, "current_form", None):
            free = True
        if free:
            cost = 0
        else:
            cost = self.talented_cost(caster)
            if not self._has_resource(caster, cost):
                return False, f"Not enough {self.resource_type.value} (need {cost})"

            # Consume resource
            self._consume_resource(caster, cost)

        # Apply cooldown (in turns, not seconds; talent-reduced) - only
        # for in-combat casts. Buffs/heals used to prep before a pull
        # shouldn't lock the button for the fight that's about to start.
        # Also skipped for free=True (a proc firing this ability isn't
        # the player choosing to use their own cooldown-gated action).
        if in_combat and not free:
            self.turns_remaining = self.talented_cooldown(caster)
        
        # Apply effect
        result_msg = self._apply_effect(caster, target, cost=cost, party=party)

        # "taunt" in stat_mods (CoA tank cooldowns: Dreadfall Tank, Test of
        # Pride, Command, Injunction, Nature's Call, Vile Sting, Locust
        # Swarm, ...) is a flag, not a real stat - no engine code ever read
        # it as a stat_mod, so these abilities cast, applied a cosmetic
        # effect, and never actually pulled threat (confirmed:
        # CombatEngine.default_target_for only ever redirects off real
        # threat-table entries). Handled here rather than inside
        # _apply_effect's individual effect_type branches since "taunt" can
        # appear on a damage-type ability (Dreadfall Tank) just as easily as
        # a debuff (Test of Pride) - one place covers every effect_type.
        # Appends to the SAME self._last_threat_events list _apply_effect
        # just populated (see CombatEngine._generate_threat_from_ability,
        # which consumes it right after use() returns), so a taunt stacks
        # on top of whatever real damage/heal threat this same cast already
        # generated rather than replacing it.
        #
        # Deliberately NOT scaled by effect_value - several of these (Test
        # of Pride, Injunction) author effect_value=0 since they had no
        # real numeric payload before this fix, and a taunt's whole job is
        # "unconditionally top the threat table", not "deal a rank-scaled
        # amount of threat". Scaled off the target's own level instead, so
        # a taunt reliably overrides whatever threat a high-level pull has
        # already built up rather than going stale as content level rises.
        if (self.stat_mods or {}).get("taunt") and hasattr(self, "_hostile_recipients"):
            TAUNT_THREAT_PER_LEVEL = 500
            taunt_targets = self._hostile_recipients(target)
            for t in taunt_targets:
                taunt_amount = max(500, getattr(t, "level", 1) * TAUNT_THREAT_PER_LEVEL)
                self._last_threat_events.append((t, taunt_amount, True))

        # Proc triggers - fired off the SAME _last_threat_events data
        # _apply_effect just populated (real damage/heal amounts per
        # recipient, already distinguishing damage from healing), so a
        # proc reacts to what actually happened this cast, not a guess.
        # ON_CAST always fires (any successful use, buff/heal/nuke alike);
        # ON_DAMAGE_CAST/ON_HEAL_CAST/ON_CRIT only fire when this cast
        # genuinely dealt damage or landed a heal. See
        # StatusEffectMixin.fire_proc_trigger and ProcTrigger for the
        # full trigger contract.
        if hasattr(caster, "fire_proc_trigger"):
            from combat.status_effects import ProcTrigger
            # Every trigger fired from this cast carries ability_id, not just
            # ON_DAMAGE_CAST/ON_HEAL_CAST. A proc's ability_filter is matched
            # against it (see fire_proc_trigger), and because only those two
            # triggers used to supply it, a filter on ON_CAST, ON_CRIT,
            # ON_WEAPON_SWING or ON_KILL silently never matched - the proc
            # could never fire at all. The ability is right here in scope, so
            # there was never a reason for it to be missing; four Druid
            # talents (Mangle, Infected Wounds, King of the Jungle, Eclipse)
            # were dead on exactly this.
            # ON_CAST also carries the TARGET of the cast. Without it, a proc
            # whose apply_effect sets on_target: true fell back to the carrier,
            # so an enemy debuff authored on ON_CAST silently landed on the
            # PLAYER - and when that debuff is a damage-taken increase, the
            # talent actively hurt its owner. Druid's Mangle demonstrated it
            # exactly: "Mangle triggers Mangle on D", giving the Druid +10%
            # physical damage taken. Ten talents were authored this way.
            #
            # Fired before damage resolves, so this is the intended target of
            # the cast rather than a confirmed hit; for a self-buff or a heal
            # it is the caster or the ally, which is the correct recipient
            # there too.
            proc_msgs = caster.fire_proc_trigger(
                ProcTrigger.ON_CAST,
                {"amount": 0, "target": target, "ability_id": self.ability_id})

            events = getattr(self, "_last_threat_events", None) or []
            for recipient, evt_amount, is_damage in events:
                if evt_amount <= 0:
                    continue
                trigger = ProcTrigger.ON_DAMAGE_CAST if is_damage else ProcTrigger.ON_HEAL_CAST
                evt_target = recipient if is_damage else caster
                proc_msgs += caster.fire_proc_trigger(
                    trigger, {"amount": evt_amount, "target": evt_target, "ability_id": self.ability_id})

                # ON_WEAPON_SWING: fired ONLY when this specific cast was
                # the caster's own basic attack ("<class_prefix>_attack",
                # same real convention extra_attack already relies on -
                # see fire_proc_trigger's docstring). Real WoW weapon
                # imbues (Windfury/Flametongue/Rockbiter/Frostbrand) only
                # ever proc off a genuine weapon swing, never off spells -
                # this is the fix for a real bug where Rockbiter (built
                # listening for the broader ON_DAMAGE_CAST) was proccing
                # off Healing Wave and every other spell cast, since
                # ON_DAMAGE_CAST doesn't distinguish "basic attack" from
                # "any damage source." Fired as its own separate trigger
                # (not folded into ON_DAMAGE_CAST's matching) so imbue
                # procs can listen for exactly this and nothing broader.
                if is_damage and self.ability_id == f"{_class_file_prefix(caster.char_class)}_attack":
                    proc_msgs += caster.fire_proc_trigger(
                        ProcTrigger.ON_WEAPON_SWING,
                        {"amount": evt_amount, "target": evt_target,
                         "ability_id": self.ability_id})

                if self._last_crit:
                    proc_msgs += caster.fire_proc_trigger(
                        ProcTrigger.ON_CRIT,
                        {"amount": evt_amount, "target": evt_target,
                         "is_crit": True, "ability_id": self.ability_id})

                # ON_KILL: this specific damage event's recipient is a real
                # enemy (not None - heals route evt_target=caster above,
                # which is never "killed" by its own heal) and is no longer
                # alive AFTER take_damage() already ran inside _apply_effect.
                # Checked per-recipient rather than once for the whole cast,
                # so an AoE that kills 2 of 3 enemies fires ON_KILL exactly
                # twice, off the actual kills, not a guess based on whether
                # ANY target in the group died.
                if is_damage and recipient is not None and hasattr(recipient, "is_alive") and not recipient.is_alive():
                    proc_msgs += caster.fire_proc_trigger(
                        ProcTrigger.ON_KILL,
                        {"amount": evt_amount, "target": recipient,
                         "ability_id": self.ability_id})

            # Drain any ON_DAMAGE_TAKEN proc messages the recipient(s)
            # queued during take_damage() above (Character has no direct
            # combat_log access - see Character.take_damage's comment on
            # _pending_proc_messages). One caster action can hit multiple
            # recipients (AoE), so drain every recipient that was actually
            # hit this cast, not just the first.
            for recipient, _amt, is_damage in events:
                if is_damage and hasattr(recipient, "_pending_proc_messages") and recipient._pending_proc_messages:
                    proc_msgs += recipient._pending_proc_messages
                    recipient._pending_proc_messages = []

            for msg in proc_msgs:
                result_msg += f" {msg}"

        # force_proc_group restore (Barbed Stinger): the debuff branch of
        # _apply_effect above left the active Venom's proc dict mutated
        # to guaranteed-fire values so the taunt-threat-driven
        # ON_DAMAGE_CAST firing just above would hit it for real exactly
        # once. Restore the Venom's actual stored proc (its real chance/
        # icd) now that firing is done, so the Venomancer's normal
        # passive chance-based proccing on every future cast is
        # completely unaffected by this one forced cast.
        forced_effect = getattr(self, "_forced_proc_effect", None)
        if forced_effect is not None:
            forced_effect.proc = self._forced_proc_original
            self._forced_proc_effect = None
            self._forced_proc_original = None

        return True, result_msg
    
    def _effective_resource_type(self, caster):
        """The resource_type this cast should actually spend/check,
        resolving dynamically when the ability is gated to multiple
        forms with DIFFERENT resource pools (e.g. druid_swipe_cat -
        requires_form=["cat","bear","dire_bear"], but Cat draws Energy
        while Bear/Dire Bear draw Rage). Real bug found and fixed here
        (Kyle, 2026-09-06): swipe_cat's resource_type was hardcoded to
        "energy" in JSON, so a Bear-form Druid (current_energy=0 since
        shifting resets the pool they left) could never cast it at all -
        always "not enough energy" despite being in a form the ability
        explicitly allows.

        Falls back to self.resource_type unchanged for the overwhelming
        majority of abilities (single-form-gated or not form-gated at
        all), where the static JSON value is already correct and this
        is a no-op lookup."""
        if (isinstance(self.requires_form, list) and len(self.requires_form) > 1
                and hasattr(caster, "current_form") and caster.current_form):
            from combat.forms import resource_for_form
            form_resource = resource_for_form(caster.current_form)
            if form_resource is not None:
                return form_resource
        return self.resource_type

    def _has_resource(self, caster, cost=None):
        """Check if caster has enough of this ability's resource.

        Fully generic: routes through Character.get_resource(), which covers
        both the dedicated attributes (Rage/Energy/Mana/Health) and the
        dict-backed CoA resources (Static, Insanity, Deathfire, ...). Monsters
        and anything else without the generic API are treated as always able
        to pay, so enemy ability use never crashes on a missing pool.
        """
        if cost is None:
            cost = self.cost
        if not hasattr(caster, "get_resource"):
            return True
        resource_type = self._effective_resource_type(caster)
        # Health is special: spending it must never be lethal.
        if resource_type == ResourceType.HEALTH:
            return caster.current_health > cost
        return caster.get_resource(resource_type) >= cost

    def _consume_resource(self, caster, cost=None):
        """Consume this ability's resource, then apply any generation."""
        if cost is None:
            cost = self.cost
        if hasattr(caster, "spend_resource"):
            resource_type = self._effective_resource_type(caster)
            if resource_type == ResourceType.HEALTH:
                caster.current_health -= cost
            else:
                caster.spend_resource(resource_type, cost)

        self._generate_resource(caster)

    def _refund_failed_cast(self, caster, cost=None):
        """Undo use()'s resource-spend and cooldown-set for a cast that
        ultimately did nothing (currently only Swiftmend-style
        consumes_hot abilities with no qualifying HoT present).

        use() deducts the cost and sets turns_remaining BEFORE calling
        _apply_effect() - by design, so a partially-resolved cast (e.g.
        one that hits some but not all AoE targets) still pays its cost.
        But a consumes_hot ability with nothing to consume affects
        nobody and nothing, so charging for it and starting its cooldown
        would punish the player for a button press that had zero effect.
        Not a general-purpose "cancel any ability" - only meant for this
        specific all-or-nothing failure case.
        """
        if cost is None:
            cost = self.cost
        if hasattr(caster, "gain_resource") and self.resource_type != ResourceType.HEALTH:
            caster.gain_resource(self.resource_type, cost)
        elif self.resource_type == ResourceType.HEALTH:
            caster.current_health += cost
        self.turns_remaining = 0

    def _generate_resource(self, caster):
        """
        Award this ability's `generates` resource, if any.

        This is what makes CoA's builder/spender classes work. A Stormbringer
        spends Mana on a builder to bank Static, then spends Static on a
        payoff - so an ability needs to be able to pay in one currency and
        produce another. `generates` is {"resource": "static", "amount": 20}.
        """
        if not self.generates or not hasattr(caster, "gain_resource"):
            return 0
        resource = self.generates.get("resource")
        amount = self.generates.get("amount", 0)
        if not resource or amount <= 0:
            return 0
        return caster.gain_resource(resource, amount)

    def _recipients(self, caster, target):
        """
        Resolve who a friendly effect actually lands on.

        Always returns a non-empty list, so callers never have to special-case
        a missing target. `target` may be a single combatant or a list (the
        combat screen passes a list for party-wide abilities).
        """
        if self.target_type == "self":
            return [caster]

        if self.target_type == "party":
            if isinstance(target, (list, tuple)) and target:
                return [t for t in target if t is not None] or [caster]
            # No party context supplied (e.g. a 1v1 engine or a direct unit
            # test) - degrade to the caster rather than silently no-op.
            return [caster]

        # "ally": a single friendly target, defaulting to the caster.
        if isinstance(target, (list, tuple)):
            return [target[0]] if target else [caster]
        return [target if target is not None else caster]

    def _hostile_recipients(self, target):
        """
        Resolve who a HOSTILE effect (damage/dot/debuff) actually lands on.

        Mirrors _recipients() but for the enemy side: "enemy" hits exactly
        the single target passed in (or the first of a list, for callers
        that always pass a list); "enemy_aoe" hits every living enemy
        passed in. Previously there was no AoE concept at all here, so an
        ability like Arcane Explosion or Chain Lightning - unambiguously
        AoE by name and flavor - could only ever hit the one enemy handed
        to use(), identical to a single-target nuke.

        Always returns a list (possibly empty, if target is None/empty),
        so callers can loop over the result uniformly instead of branching
        on single-vs-list.
        """
        if self.target_type == "enemy_aoe":
            if isinstance(target, (list, tuple)):
                living = [t for t in target if t is not None and t.is_alive()]
            else:
                living = [target] if target is not None else []
            # max_targets (see Ability.__init__) caps a limited-cleave
            # ability to its real target count instead of hitting every
            # living enemy - the explicitly-targeted unit (whichever
            # element the caller put first, by convention "your target")
            # is always included, with the cap applied to the whole list
            # afterward so a 2-target cleave against a single remaining
            # enemy still just hits that one enemy rather than erroring.
            if self.max_targets and len(living) > self.max_targets:
                living = living[:self.max_targets]
            return living

        if isinstance(target, (list, tuple)):
            return [target[0]] if target else []
        return [target] if target is not None else []

    def _lowest_hp_allies(self, caster, party, count=1):
        """Pick the `count` neediest living allies, ranked by HP percentage
        (current/max) ascending - same priority _lowest_hp_ally uses for a
        single target, just returning a list of the N worst-off instead of
        just the worst. Backing implementation for both _lowest_hp_ally
        (count=1) and Icy Penance's 3-target smart-heal.
        """
        candidates = [caster]
        if party:
            candidates = [p for p in party if p is not None and getattr(p, "is_alive", lambda: True)()] or [caster]
        ranked = sorted(candidates, key=lambda c: getattr(c, "current_health", 0) / max(1, getattr(c, "health", 1)))
        return ranked[:max(1, count)]

    def _lowest_hp_ally(self, caster, party):
        """Pick the single neediest living ally. Thin wrapper around
        _lowest_hp_allies(count=1) kept as its own method since it's the
        common case and reads cleaner at call sites than indexing a list.
        """
        return self._lowest_hp_allies(caster, party, count=1)[0]

    def _apply_smart_heal(self, caster, party, heal_value):
        """Apply Cryotherapist's healing side effect and return a short
        " healing X for N!" clause to append to a combat log line.

        Scope depends on self.heal_scope:
          "lowest_ally" (default) - smart-heals the single neediest ally
              (by HP%), matching Cryobolt/Cryolance's per-cast proc.
          "party" - heals every living ally for the same amount each,
              matching Frostfall's capstone (its damage is already AoE, so
              the heal follows suit rather than singling one person out).

        Shared by effect_type="damage_and_heal" (Frostfall) and
        cryo_converted spell_damage abilities (Frostbolt/Ice Lance once the
        Cryobolt/Cryolance talent is spent) so every path computes healing
        power scaling identically instead of copies drifting apart.
        """
        heal_amt = int(heal_value + caster.healing_power * 1.2)
        # recipient stays None here: _apply_smart_heal has not chosen its
        # target yet (it picks the most wounded ally below), so a
        # recipient-conditional healing talent cannot apply to a smart heal.
        heal_amt = int(heal_amt * self._damage_multiplier(caster, "healing"))

        if self.heal_scope == "party":
            recipients = party if party else [caster]
            recipients = [p for p in recipients if p is not None and getattr(p, "is_alive", lambda: True)()] or [caster]
            for r in recipients:
                r.heal(heal_amt)
                self._last_threat_events.append((None, heal_amt, False))
            names = ", ".join(r.name for r in recipients)
            return names, heal_amt, len(recipients)

        if isinstance(self.heal_scope, int):
            recipients = self._lowest_hp_allies(caster, party, count=self.heal_scope)
            for r in recipients:
                r.heal(heal_amt)
                self._last_threat_events.append((None, heal_amt, False))
            names = ", ".join(r.name for r in recipients)
            return names, heal_amt, len(recipients)

        heal_target = self._lowest_hp_ally(caster, party)
        heal_target.heal(heal_amt)
        self._last_threat_events.append((None, heal_amt, False))
        return heal_target.name, heal_amt, 1

    def _apply_earthen_attunement_shred(self, caster, target):
        """Earthen Attunement (Shaman Tank talent): while Earthen Guardian
        is active, dealing physical damage reduces the target's Attack
        Power. Only fires for casters that actually have ranks in it AND
        currently have the stance active - get_talent_effect naturally
        returns 0 for anyone without both (see Character.get_talent_effects'
        guardian_stance_active-gated fold of earthen_attunement_ap_shred),
        so this is a safe no-op call for every other class/caster in the
        game, not just Shaman.

        Applied as a genuine DEBUFF StatusEffect on the target (stacks by
        refreshing duration each hit like most debuffs here, doesn't stack
        multiple copies) rather than mutating target.attack_power directly -
        attack_power is a derived stat recomputed from the bonus pool on
        every _recalculate_derived_stats() call, so a direct mutation would
        just get silently overwritten the next time anything recalculates.
        """
        shred = 0.0
        if hasattr(caster, "get_talent_effect"):
            shred = caster.get_talent_effect("earthen_attunement_ap_shred", 0.0) or 0.0
        if shred <= 0 or not hasattr(target, "apply_status_effect"):
            return
        effect = StatusEffect(
            effect_id="earthen_attunement_shred", name="Earthen Attunement",
            effect_type=EffectType.DEBUFF, duration=3,
            stat_mods={"attack_power": -int(shred)}, source_name=caster.name,
            real_time_seconds=None,
        )
        target.apply_status_effect(effect)

    def _apply_heal_effect(self, caster, target, cost=None, party=None):
        """The actual heal logic, factored out of effect_type="heal" so a
        form-reactive ability (Venomancer's Serpent's Fang: damage
        unshifted, heal while Vizier-shifted - see the heal_in_form
        dispatch at the top of _apply_effect) can reuse it without
        duplicating the Swiftmend-consume/party-recipients logic.
        """
        if not target:
            return f"{caster.name} casts {self.name}!"

        if self.consumes_hot:
            # Swiftmend: find the first active HoT on the target whose
            # effect_id matches one of consumable_hot_ids, heal for
            # that HoT's remaining total (potency * duration - i.e.
            # "the rest of what it would have healed"), then remove
            # it. If no qualifying HoT is present, the cast fails
            # outright - Swiftmend has nothing to consume, matching
            # the real spell's requirement.
            consumable = None
            for effect in target._effects():
                if effect.effect_id in self.consumable_hot_ids:
                    consumable = effect
                    break
            if consumable is None:
                # Refund - use() already deducted the cost and set the
                # cooldown before calling _apply_effect, so a failed
                # consume must give both back rather than punishing
                # the player for a cast that did nothing.
                self._refund_failed_cast(caster, cost=cost)
                return (f"{self.name} requires an active Rejuvenation or "
                        f"Regrowth on {target.name} - nothing to consume!")

            # tick_potency(), not bare potency: "the rest of what it would
            # have healed" has to agree with what the HoT actually heals per
            # tick, and potency is stored per-stack. Consuming a 3-stack HoT
            # off a bare potency would pay out a third of what the player
            # watched it ticking for.
            remaining_total = max(1, consumable.tick_potency() * max(0, consumable.duration))
            heal_amt = int(remaining_total * self._damage_multiplier(caster, "healing", recipient=target))
            target.heal(heal_amt)
            self._last_threat_events.append((None, heal_amt, False))
            target._effects().remove(consumable)
            return (f"{caster.name} consumes {consumable.name} on {target.name}, "
                    f"instantly healing for {heal_amt}!")

        # Healing now scales with Healing Power (derived stat) instead
        # of raw Spirit directly - same principle as spell_damage
        # above. Healing Power = Spirit*2 + INT*0.2 (base) + gear rolls.
        heal_amt = int(self.effect_value + caster.healing_power * 1.2)
        heal_amt = int(heal_amt * self._damage_multiplier(caster, "healing", recipient=target))

        # target_type="party" (Circle of Healing, etc) passes a LIST of
        # combatants rather than one - the single-target path below
        # crashed on list.heal() not existing until this branch was
        # added. _recipients() already handles list-vs-single
        # normalization correctly for hot/buff; reuse it here instead
        # of hand-rolling a second copy of that logic.
        recipients = self._recipients(caster, target)

        # THE ACTUAL BUG THIS FIXES: every party-wide heal applied its
        # FULL effect_value to every recipient with zero reduction, unlike
        # AoE damage which has always had a real per-target penalty
        # (AOE_DAMAGE_MULTIPLIER, 0.6x) - so an AoE heal on a 5-person
        # party delivered 5x the total HP of a single-target heal for
        # roughly the same mana, a straight exploit confirmed by directly
        # comparing cost-per-point-healed across ST vs AoE heals of the
        # same class (Circle of Healing/Wild Growth/Mending Mist etc were
        # all at parity with their own class's ST heals, not a real
        # throughput tradeoff). Reuses the EXACT SAME multiplier AoE
        # damage already uses, applied only when this cast actually has
        # more than one recipient - a heal authored as "party" but cast
        # with a 1-person party (solo play, or only one person needs it)
        # still heals for full value, matching how enemy_aoe damage
        # against a single remaining enemy isn't penalized either.
        is_aoe_heal = len(recipients) > 1
        if is_aoe_heal:
            heal_amt = int(heal_amt * self.AOE_DAMAGE_MULTIPLIER)

        for r in recipients:
            r.heal(heal_amt)
            self._last_threat_events.append((None, heal_amt, False))

        # Real Stim Rounds splash (Kyle: confirmed from real playtime as
        # a Tinker healer - "augment the tinkerer to allow Repair shot
        # to heal the main target AND two of the lowest HP allies for
        # 30% of the heal shot spell"). Only fires for Repair Shot
        # itself while the caster has the real "tinker_stim_rounds"
        # buff active (loaded via the Stim Rounds ability, exclusive
        # with the other real Rounds) - every other heal ability
        # (Sanctify, Illumination, etc across other classes) also
        # routes through this same _apply_heal_effect method, so the
        # ability_id check keeps this Tinker-specific splash from
        # leaking onto every heal in the game.
        splash_names = []
        if (self.ability_id == "tinker_repair_shot"
                and hasattr(caster, "has_status_effect")
                and caster.has_status_effect("tinker_stim_rounds")):
            already_healed = set(recipients)
            splash_targets = [
                a for a in self._lowest_hp_allies(caster, party, count=3)
                if a not in already_healed
            ][:2]
            splash_amt = max(1, int(heal_amt * 0.30))
            for a in splash_targets:
                a.heal(splash_amt)
                self._last_threat_events.append((None, splash_amt, False))
                splash_names.append(a.name)

        if splash_names:
            names = ", ".join(r.name for r in recipients)
            splash_str = ", ".join(splash_names)
            return (f"{caster.name} casts {self.name} on {names} for {heal_amt} "
                    f"healing! Stim Rounds also heals {splash_str} for {splash_amt}!")
        if len(recipients) > 1:
            names = ", ".join(r.name for r in recipients)
            return f"{caster.name} casts {self.name}, healing {names} for {heal_amt} each!"
        return f"{caster.name} casts {self.name} on {recipients[0].name} for {heal_amt} healing!"

    def _apply_judgement_effect(self, caster, target, cost=None):
        """Judgement's real mechanic: consume the caster's active Seal
        (a BUFF StatusEffect on the caster whose `proc` dict includes an
        "on_judgement" sub-payload) and detonate that payload against the
        target as one guaranteed instant effect, then remove the Seal.

        A Seal with no on_judgement payload (or no active Seal at all)
        means nothing to detonate - the cast fails and refunds via
        _refund_failed_cast, same all-or-nothing pattern as Swiftmend
        with no qualifying HoT (see _apply_heal_effect's consumes_hot
        branch). This matches real WoW: Judgement without an active Seal
        simply cannot be cast.

        The on_judgement payload supports "damage" (flat bonus magic
        damage on top of Judgement's own effect_value, scaled by spell
        power the same way spell_damage already does) and "grant_resource"
        (e.g. a Seal that also banks a resource on Judgement) - deliberately
        a small, explicit set rather than routing through the full proc
        payload vocabulary (bonus_pct/extra_attack/apply_effect), since a
        Judgement detonation is a one-shot guaranteed effect, not a
        reactive trigger, and doesn't need chance/ICD semantics at all.
        """
        seal = None
        for effect in caster._effects():
            if effect.proc and effect.proc.get("on_judgement"):
                seal = effect
                break

        if seal is None:
            self._refund_failed_cast(caster, cost=cost)
            return f"{caster.name} has no Seal active to Judge!"

        recipients = self._hostile_recipients(target)
        if not recipients:
            self._refund_failed_cast(caster, cost=cost)
            return f"{caster.name} has no target to Judge!"
        t = recipients[0]

        on_judgement = seal.proc["on_judgement"]
        judge_school = self._resolve_damage_school(caster) or "magic"
        base_damage = int(self.effect_value + caster.get_effective_spell_power(judge_school) * 1.0)
        seal_bonus = on_judgement.get("damage", 0)
        total_damage = int((base_damage + seal_bonus) * self._damage_multiplier(caster, "spell"))

        actual = t.take_damage(total_damage, judge_school, attacker_level=getattr(caster, "level", None), attacker=caster)
        self._last_threat_events.append((t, actual, True))

        grant = on_judgement.get("grant_resource")
        grant_msg = ""
        if grant and hasattr(caster, "gain_resource"):
            resource = grant.get("resource")
            grant_amt = grant.get("amount", 0)
            if resource and grant_amt > 0:
                gained = caster.gain_resource(resource, grant_amt)
                if gained:
                    grant_msg = f" {caster.name} gains {gained} {resource.replace('_', ' ').title()}!"

        caster._effects().remove(seal)
        return (f"{caster.name} judges {t.name} with {seal.name} for {actual} damage!"
                f"{grant_msg} {seal.name} is consumed.")

    def _apply_effect(self, caster, target, cost=None, party=None):
        """Apply ability effect to target(s).

        `target` may be a single enemy (existing callers) or a list of all
        living enemies (new AoE-aware callers) - _hostile_recipients()
        normalizes either shape based on self.target_type, so single-target
        abilities keep working exactly as before even when a caller starts
        passing the full enemy list for every ability.

        Populates self._last_threat_events as a side effect: a list of
        (enemy_or_None, amount, is_damage) tuples for every point this call
        actually dealt damage or landed a heal, so use()/execute_ability can
        turn real numbers into threat afterward (see CombatEngine.
        gain_threat) without every effect_type branch needing to change its
        return signature. Reset at the top of every call - callers must
        read it immediately after use() returns, before the next cast
        overwrites it.
        """
        self._last_threat_events = []
        # Set True the moment ANY _roll_crit() call in this _apply_effect
        # invocation lands a crit (see the 4 call sites below) - read by
        # use()'s proc-firing block right after this method returns, to
        # decide whether to also fire ProcTrigger.ON_CRIT for this cast.
        # Reset here per-call for the same reason _last_threat_events is:
        # a stale True from a previous cast must never leak into this one.
        self._last_crit = False
        is_aoe = self.target_type == "enemy_aoe"
        aoe_mult = self.AOE_DAMAGE_MULTIPLIER if is_aoe else 1.0

        # Form-reactive dispatch (Venomancer's Serpent's Fang): a small set
        # of abilities behave as their normal effect_type unshifted, but
        # become a heal while the caster is in a specific form - confirmed
        # by Kyle as the SAME ability, not two separate spells (mirrors how
        # a real Druid's identity shifts by spec without needing two
        # different spell books). heal_in_form is a (form_id, target_type)
        # pair; when the caster's current_form matches, this call is
        # redirected to the "heal" branch below using the ability's own
        # effect_value/ranks for the heal amount, with `target` and
        # `target_type` swapped to the ally-facing shape for that one call.
        if self.heal_in_form and getattr(caster, "current_form", None) == self.heal_in_form[0]:
            original_target_type = self.target_type
            self.target_type = self.heal_in_form[1]
            try:
                return self._apply_heal_effect(caster, target, party=party)
            finally:
                self.target_type = original_target_type

        if self.consumes_seal:
            return self._apply_judgement_effect(caster, target, cost=cost)

        if self.effect_type in ("damage", "ranged_damage"):
            recipients = self._hostile_recipients(target)
            if recipients:
                import random
                hit_chance = getattr(caster, "hit_chance_physical", 100.0)
                # ranged_damage (the universal "Shoot" action - see
                # data/abilities/_universal.json) pulls its weapon roll
                # from the Ranged slot (bow/gun/thrown, weapon_type
                # "thrown") via get_weapon_damage_roll(use_ranged=True)
                # and scales off ranged_attack_power instead of the
                # main-hand attack_power - a real separate stat that
                # existed on Character since Phase 5c but had no
                # consumer anywhere until this action. Ordinary "damage"
                # abilities (every class's melee Attack, and everything
                # else that was already using this branch) are completely
                # unaffected - same main-hand roll + attack_power as
                # before.
                if self.effect_type == "ranged_damage":
                    weapon_dmg = caster.get_weapon_damage_roll(use_ranged=True) if hasattr(caster, "get_weapon_damage_roll") else 0
                    ap = getattr(caster, "ranged_attack_power", 0)
                else:
                    weapon_dmg = caster.get_weapon_damage_roll() if hasattr(caster, "get_weapon_damage_roll") else 0
                    ap = caster.attack_power
                base_damage = int(self.effect_value + ap * 0.5) + weapon_dmg
                base_damage = int(base_damage * self._damage_multiplier(caster, "physical") * aoe_mult)

                hit_lines = []
                any_hit = False
                first_hit_amount = None
                first_hit_crit = False
                for t in recipients:
                    # Hit Rating (Phase 5c): roll for a miss before computing damage.
                    # Casters/monsters without hit_chance_physical (e.g. Monster
                    # class) are treated as always hitting - only Character has
                    # a hit chance stat for now.
                    if random.uniform(0, 100) > hit_chance:
                        hit_lines.append(f"misses {t.name}")
                    else:
                        is_crit, crit_mult = self._roll_crit(caster, t, "physical")
                        if is_crit:
                            self._last_crit = True
                        hit_damage = int(base_damage * crit_mult)
                        actual_damage = t.take_damage(hit_damage, "physical", attacker_level=getattr(caster, "level", None), attacker=caster)
                        if actual_damage == 0:
                            # Dodge/Parry (see Character.take_damage's
                            # avoidance roll) - the attack landed (passed
                            # the attacker's hit check above) but the
                            # defender fully avoided it. Every other damage
                            # path here floors at 1 via max(1, ...), so 0 is
                            # an unambiguous "avoided" signal, not a real
                            # zero-damage hit - must NOT count as any_hit or
                            # generate threat for a hit that didn't land.
                            hit_lines.append(f"is dodged/parried by {t.name}")
                        else:
                            hit_lines.append(f"{actual_damage} to {t.name}" + (" (CRIT!)" if is_crit else ""))
                            any_hit = True
                            if first_hit_amount is None:
                                first_hit_amount = actual_damage
                                first_hit_crit = is_crit
                            self._last_threat_events.append((t, actual_damage, True))
                            self._apply_earthen_attunement_shred(caster, t)

                if is_aoe and len(recipients) > 1:
                    return f"{caster.name} uses {self.name} on all enemies ({', '.join(hit_lines)})!"
                if not any_hit:
                    return f"{caster.name}'s {self.name} misses {recipients[0].name}!"
                return f"{caster.name} uses {self.name} on {recipients[0].name} for {first_hit_amount} damage!" + (" (CRIT!)" if first_hit_crit else "")
            return f"{caster.name} uses {self.name}!"
        
        elif self.effect_type == "spell_damage":
            recipients = self._hostile_recipients(target)
            if recipients:
                import random
                hit_chance = getattr(caster, "hit_chance_spell", 100.0)

                # Spell damage now scales with Spell Power (derived stat), the
                # same way physical damage scales with Attack Power. Spell
                # Power itself comes from a small base-INT contribution
                # (0.2/point) plus gear's spell_power rolls - so a caster's
                # real damage growth is meant to come from gear at higher
                # levels, not from stacking INT alone. Wand damage (Phase 5b)
                # adds a small ranged-weapon component for casters with a
                # Wand equipped in the Ranged slot.
                wand_dmg = caster.get_weapon_damage_roll(use_ranged=True) if hasattr(caster, "get_weapon_damage_roll") else 0
                spell_damage_school = self._resolve_damage_school(caster) or "magic"
                base_damage = int(self.effect_value + caster.get_effective_spell_power(spell_damage_school) * 1.5) + wand_dmg
                base_damage = int(base_damage * self._damage_multiplier(caster, "spell") * aoe_mult)

                hit_lines = []
                any_hit = False
                first_hit_amount = None
                first_hit_crit = False
                for t in recipients:
                    if random.uniform(0, 100) > hit_chance:
                        hit_lines.append(f"misses {t.name}")
                    else:
                        is_crit, crit_mult = self._roll_crit(caster, t, "spell")
                        if is_crit:
                            self._last_crit = True
                        hit_damage = int(base_damage * crit_mult)
                        actual_damage = t.take_damage(hit_damage, spell_damage_school, attacker_level=getattr(caster, "level", None), attacker=caster)
                        hit_lines.append(f"{actual_damage} to {t.name}" + (" (CRIT!)" if is_crit else ""))
                        any_hit = True
                        if first_hit_amount is None:
                            first_hit_amount = actual_damage
                            first_hit_crit = is_crit
                        self._last_threat_events.append((t, actual_damage, True))

                if is_aoe and len(recipients) > 1:
                    summary = f"{caster.name} casts {self.name} on all enemies ({', '.join(hit_lines)})!"
                elif not any_hit:
                    summary = f"{caster.name}'s {self.name} misses {recipients[0].name}!"
                else:
                    # Real school name in the log (Fire/Frost/Nature/...)
                    # when this ability has been migrated to one, instead
                    # of the old generic "magic damage" wording that gave
                    # no hint why a Fireball got resisted differently than
                    # a Frostbolt would. Falls back to "magic" for
                    # abilities not yet assigned a real school - identical
                    # wording to before this existed.
                    resolved_school = self._resolve_damage_school(caster)
                    school_label = resolved_school if isinstance(resolved_school, str) else "magic"
                    summary = f"{caster.name} casts {self.name} on {recipients[0].name} for {first_hit_amount} {school_label} damage!" + (" (CRIT!)" if first_hit_crit else "")

                # Cryotherapist (Cryobolt/Cryolance talent): once converted,
                # Frostbolt/Ice Lance smart-heal the lowest-HP% ally on every
                # cast that connects, on top of their normal damage - see
                # Ability.cryo_converted and _apply_smart_heal. Guarded on
                # any_hit so a miss doesn't also grant a free heal.
                if self.cryo_converted and any_hit:
                    heal_names, heal_amt, heal_count = self._apply_smart_heal(caster, party, self.heal_value)
                    if heal_count > 1:
                        summary += f" Cryotherapist heals {heal_names} for {heal_amt} each!"
                    else:
                        summary += f" Cryotherapist heals {heal_names} for {heal_amt}!"

                # Stormbringer's Shock: also applies a 1-turn DoT worth a %
                # of the hit's damage (applies_dot_pct, e.g. 0.10 for 10%).
                # Bolted onto the base cast the same way cryo_converted
                # bolts a heal onto Frostbolt/Ice Lance above - Shock stays
                # ONE hotbar button, not two, matching Kyle's direction
                # (the earlier "Shock (Lingering Current)" as a separate
                # selectable ability was wrong and has been removed).
                if self.applies_dot_pct and any_hit and first_hit_amount:
                    dot_amount = max(1, int(first_hit_amount * self.applies_dot_pct))
                    dot_target = recipients[0] if not (is_aoe and len(recipients) > 1) else None
                    dot_recipients = recipients if (is_aoe and len(recipients) > 1) else ([dot_target] if dot_target else [])
                    for t in dot_recipients:
                        if hasattr(t, "apply_status_effect"):
                            dot_effect = StatusEffect(
                                effect_id=f"{self.ability_id}_dot", name=f"{self.name} (Lingering)",
                                effect_type=EffectType.DOT, duration=1, potency=dot_amount,
                                damage_school="magic", source_name=caster.name,
                                real_time_seconds=None,
                            )
                            t.apply_status_effect(dot_effect)
                    summary += f" ({dot_amount} lingering damage over 1 turn)"

                return summary
            return f"{caster.name} casts {self.name}!"

        elif self.effect_type == "damage_and_heal":
            # Cryotherapist (Mage/Frost 4th tree): a single cast both damages
            # an enemy AND smart-heals the caster's lowest-HP ally, in one
            # action. Damage resolves exactly like spell_damage (same crit/
            # hit-chance/spell-power math); the heal is a flat effect_value
            # applied via Ability.heal_value so damage and healing scale off
            # separate numbers, mirroring how Cryotherapist's real design
            # (frost damage triggers a smaller, separate heal) works rather
            # than converting a fraction of the damage dealt.
            recipients = self._hostile_recipients(target)
            if recipients:
                import random
                hit_chance = getattr(caster, "hit_chance_spell", 100.0)
                wand_dmg = caster.get_weapon_damage_roll(use_ranged=True) if hasattr(caster, "get_weapon_damage_roll") else 0
                cryo_school = self._resolve_damage_school(caster) or "magic"
                base_damage = int(self.effect_value + caster.get_effective_spell_power(cryo_school) * 1.5) + wand_dmg
                base_damage = int(base_damage * self._damage_multiplier(caster, "spell") * aoe_mult)

                hit_lines = []
                any_hit = False
                first_hit_amount = None
                first_hit_crit = False
                for t in recipients:
                    if random.uniform(0, 100) > hit_chance:
                        hit_lines.append(f"misses {t.name}")
                    else:
                        is_crit, crit_mult = self._roll_crit(caster, t, "spell")
                        if is_crit:
                            self._last_crit = True
                        hit_damage = int(base_damage * crit_mult)
                        actual_damage = t.take_damage(hit_damage, cryo_school, attacker_level=getattr(caster, "level", None), attacker=caster)
                        hit_lines.append(f"{actual_damage} to {t.name}" + (" (CRIT!)" if is_crit else ""))
                        any_hit = True
                        if first_hit_amount is None:
                            first_hit_amount = actual_damage
                            first_hit_crit = is_crit
                        self._last_threat_events.append((t, actual_damage, True))

                heal_names, heal_amt, heal_count = self._apply_smart_heal(caster, party, self.heal_value)

                dmg_summary = ', '.join(hit_lines) if (is_aoe and len(recipients) > 1) else (
                    f"{first_hit_amount} damage to {recipients[0].name}" + (" (CRIT!)" if first_hit_crit else "") if any_hit else f"misses {recipients[0].name}"
                )
                heal_clause = f"healing {heal_names} for {heal_amt} each" if heal_count > 1 else f"healing {heal_names} for {heal_amt}"
                return f"{caster.name} casts {self.name}: {dmg_summary}, {heal_clause}!"
            return f"{caster.name} casts {self.name}!"

        elif self.effect_type == "damage_and_restore_mana":
            # Stormbringer's Discharge: spends Static (via normal cost/
            # resource_type, already deducted by use() before this runs) to
            # hit nearby enemies for Nature damage AND restore a % of the
            # caster's max Mana in one action. Distinct from damage_and_heal
            # (which heals an ALLY off a smart-heal pool) - this restores the
            # CASTER's own primary resource instead, which is Discharge's
            # whole identity as Stormbringer's "spend Static to keep casting"
            # relief valve. mana_restore_pct on the rank (0-100) drives the
            # restore amount; effect_value drives the damage as normal.
            recipients = self._hostile_recipients(target)
            mana_restored = 0
            if hasattr(caster, "gain_resource") and hasattr(caster, "get_resource_max"):
                max_mana = caster.get_resource_max(ResourceType.MANA)
                restore_amt = int(max_mana * (self.mana_restore_pct / 100.0))
                mana_restored = caster.gain_resource(ResourceType.MANA, restore_amt)

            if recipients:
                import random
                hit_chance = getattr(caster, "hit_chance_spell", 100.0)
                discharge_school = self._resolve_damage_school(caster) or "magic"
                base_damage = int(self.effect_value + caster.get_effective_spell_power(discharge_school) * 1.5)
                base_damage = int(base_damage * self._damage_multiplier(caster, "spell") * aoe_mult)

                hit_lines = []
                for t in recipients:
                    if random.uniform(0, 100) > hit_chance:
                        hit_lines.append(f"misses {t.name}")
                    else:
                        is_crit, crit_mult = self._roll_crit(caster, t, "spell")
                        if is_crit:
                            self._last_crit = True
                        hit_damage = int(base_damage * crit_mult)
                        actual_damage = t.take_damage(hit_damage, discharge_school, attacker_level=getattr(caster, "level", None), attacker=caster)
                        hit_lines.append(f"{actual_damage} to {t.name}" + (" (CRIT!)" if is_crit else ""))
                        self._last_threat_events.append((t, actual_damage, True))

                dmg_summary = ', '.join(hit_lines)
                return f"{caster.name} unleashes {self.name}: {dmg_summary}, restoring {mana_restored} mana!"
            return f"{caster.name} uses {self.name}, restoring {mana_restored} mana!"

        elif self.effect_type == "heal":
            return self._apply_heal_effect(caster, target, cost=cost, party=party)

        elif self.effect_type in ("dot", "spell_dot"):
            # Damage over time. The rank's effect_value is the TOTAL damage
            # across the whole duration; per-turn potency is that divided by
            # duration, so ranking up a DoT increases its damage without
            # silently also changing how long it lasts.
            recipients = self._hostile_recipients(target)
            if recipients:
                import random
                # Real school precedence: self.damage_school (a real
                # DamageSchool value, e.g. "shadow" for Curse of Agony)
                # wins when the ability was migrated to one; otherwise
                # fall back to the OLD "spell_dot"->magic / "dot"->physical
                # convention, so every DoT ability not yet given a real
                # school keeps behaving exactly as before this system
                # existed. school_for_stats controls which power stat
                # (spell power vs attack power) and hit-chance stat feeds
                # this DoT - a real school still counts as "magic-like"
                # for that purpose (Curse of Agony scales off Spell Power
                # like any other DoT, real school or not).
                #
                # ATTUNEMENT resolves ONCE here, at cast time - the
                # resulting DoT's school is then locked in for its whole
                # duration (see StatusEffect(damage_school=school) below),
                # matching real WoW: a DoT doesn't retroactively change
                # school if the caster's attunement cycles again mid-DoT.
                school = self._resolve_damage_school(caster) if self.damage_school is not None else (
                    "magic" if self.effect_type == "spell_dot" else "physical")
                school_for_stats = "physical" if school == "physical" else "magic"
                hit_stat = ("hit_chance_spell" if school_for_stats == "magic"
                            else "hit_chance_physical")
                hit_chance = getattr(caster, hit_stat, 100.0)

                power = (caster.get_effective_spell_power(school) if school_for_stats == "magic"
                         else caster.attack_power * 0.3)
                total = (self.effect_value + power) * self._damage_multiplier(
                    caster, "spell" if school_for_stats == "magic" else "physical") * aoe_mult

                # consumes_stacks_of (Venomancer's Expulsion: "...for 5 sec
                # PLUS 1 sec per cleared stack" - the ONLY DoT in the game
                # whose duration scales off a stacking effect the CASTER is
                # carrying, consumed on cast). Reads the current stack
                # count BEFORE removing the effect (there's nothing to read
                # once it's gone), extends this cast's duration by
                # duration_per_stack per stack, then clears the stacks -
                # "clear your Exposed Flesh stacks," not "lose one stack."
                # Every other dot/spell_dot ability has consumes_stacks_of
                # None and is completely unaffected by this block.
                consumed_stacks = 0
                if self.consumes_stacks_of:
                    consumed_effect = next(
                        (e for e in caster._effects() if e.effect_id == self.consumes_stacks_of),
                        None)
                    if consumed_effect is not None:
                        consumed_stacks = getattr(consumed_effect, "stacks", 1)
                        caster._effects().remove(consumed_effect)
                        caster._on_status_effects_changed()

                # talented_duration, not self.duration: the HoT branch below
                # already honoured talents here and this one did not, so
                # ability_<id>_duration was silently dead on every DoT in the
                # game while working fine on HoTs, buffs and debuffs. A
                # talent extending Rend, Corruption, Serpent Sting or Moonfire
                # did nothing at all, and nothing distinguished it from one
                # that worked.
                duration = max(1, self.talented_duration(caster)
                               + int(consumed_stacks * self.duration_per_stack))
                # dot_duration_pct lengthens every DoT this caster applies,
                # the global companion to the per-ability _duration key.
                # Authored by Venomancer's Patient Rot and read by nothing.
                # A fraction (0.20 = +20% duration). Applied after the flat
                # extensions so it scales the real final length.
                dot_pct = self._talent(caster, "dot_duration_pct")
                if dot_pct:
                    duration = max(1, int(round(duration * (1.0 + dot_pct))))

                # per_turn is derived from the ability's OWN base duration, not
                # the talented one, so extending a DoT adds TICKS rather than
                # thinning the same total across more turns.
                #
                # This was the bug that made duration talents pointless the
                # moment the dot branch started honouring them: total damage
                # was fixed, so `total / duration` meant a +2-turn talent
                # simply reduced each tick. The player paid points to make
                # their DoT slower. Now a 3-turn DoT extended to 5 deals its
                # normal per-turn damage for 5 turns, which is what every one
                # of those tooltips promises.
                base_duration = max(1, (self.duration or 1)
                                    + int(consumed_stacks * self.duration_per_stack))
                per_turn = max(1, int(total / base_duration))

                hit_names = []
                miss_names = []
                for t in recipients:
                    if random.uniform(0, 100) > hit_chance:
                        miss_names.append(t.name)
                        continue
                    effect = StatusEffect(
                        effect_id=self.ability_id, name=self.name,
                        effect_type=EffectType.DOT, duration=duration,
                        potency=per_turn, damage_school=school,
                        source_name=caster.name,
                        dispel_type=self.dispel_type,
                    )
                    t.apply_status_effect(effect)
                    hit_names.append(t.name)

                if is_aoe and len(recipients) > 1:
                    parts = []
                    if hit_names:
                        parts.append(f"{', '.join(hit_names)} afflicted")
                    if miss_names:
                        parts.append(f"missed {', '.join(miss_names)}")
                    return (f"{caster.name} afflicts all enemies with {self.name} "
                            f"({per_turn} damage for {duration} turns) - {'; '.join(parts)}!")
                if not hit_names:
                    return f"{caster.name}'s {self.name} misses {recipients[0].name}!"
                return (f"{caster.name} afflicts {recipients[0].name} with {self.name} "
                        f"({per_turn} damage for {duration} turns)!")
            return f"{caster.name} uses {self.name}!"

        elif self.effect_type == "hot":
            # Heal over time. Same total-across-duration model as DoTs above.
            # Lands on the chosen friendly target, NOT unconditionally on the
            # caster - that bug made every HoT in the game a self-heal.
            total = (self.effect_value + caster.healing_power * 0.8) * \
                self._damage_multiplier(caster, "healing", recipient=target)
            duration = self.talented_duration(caster)
            per_turn = max(1, int(total / duration))

            recipients = self._recipients(caster, target)
            # Same per-target AoE reduction as the "heal" branch above and
            # as AoE damage has always had (AOE_DAMAGE_MULTIPLIER, 0.6x) -
            # a party-wide HoT (Wild Growth, Mending Mist, etc) was applying
            # its FULL per-turn potency to every recipient with zero
            # reduction, the same exploit just for heal-over-time instead of
            # direct heals. Only kicks in when this cast actually lands on
            # more than one recipient, so a "party" HoT cast while solo (or
            # with only one person needing it) still ticks for full value.
            if len(recipients) > 1:
                per_turn = max(1, int(per_turn * self.AOE_DAMAGE_MULTIPLIER))
            for recipient in recipients:
                effect = StatusEffect(
                    effect_id=self.ability_id, name=self.name,
                    effect_type=EffectType.HOT, duration=duration,
                    potency=per_turn, source_name=caster.name,
                )
                recipient.apply_status_effect(effect)

            if len(recipients) > 1:
                who = "the party"
            else:
                who = "themselves" if recipients[0] is caster else recipients[0].name
            return (f"{caster.name} casts {self.name} on {who} "
                    f"(healing {per_turn} per turn for {duration} turns)!")

        elif self.effect_type == "buff":
            # stat_mods scale with rank via effect_value acting as a
            # multiplier on the ability's declared base mods. Recipients come
            # from target_type: a personal cooldown lands on the caster, a
            # blessing lands on the chosen ally, a shout hits the whole party.
            #
            # ability_<id>_potency (Guardian Totems: "+10% Stoneskin Totem
            # Armor per rank") scales the whole mods dict multiplicatively on
            # top of the rank scaling above - same ability_<id>_* naming
            # convention as talented_cost/talented_cooldown, just for buff
            # MAGNITUDE rather than resource cost or cooldown, since nothing
            # existed to scale a buff's stat_mods by talent before this.
            potency_bonus = self._talent(caster, f"ability_{self.ability_id}_potency")
            # Percentage-shaped stat keys (the "_pct" convention -
            # damage_taken_pct, max_health_pct, etc. - see
            # Character._recalculate_derived_stats/take_damage, which read
            # these as fractional multipliers like -0.30, not flat
            # amounts) must NOT be int()-truncated: int(-0.30) is 0 in
            # Python, which silently zeroed every percentage-based buff
            # stat_mod (caught via Shamanistic Rage's real -30% damage
            # reduction landing as a real 0% - confirmed via a direct
            # headless test before this fix). Flat stats (agility, armor,
            # attack_power, ...) keep their existing int() scaling exactly
            # as before - only the _pct suffix changes behavior here.
            mods = {}
            for k, v in (self.stat_mods or {}).items():
                scaled = v * (self.effect_value / 100.0) * (1.0 + potency_bonus)
                mods[k] = scaled if k.endswith("_pct") else int(scaled)
            recipients = self._recipients(caster, target)
            # "raid" buffs (Fortitude, Mark of the Wild, ...) run on the
            # 30-min real-time clock and survive between fights; "combat"
            # buffs (Icy Veins-style cooldowns) are turn-based via `duration`
            # and expire within the same fight. See buff_scope in __init__.
            real_time = None if self.buff_scope == "combat" else _UNSET
            # absorb_pct_max_health / absorb: a buff ability can raise a real
            # damage-absorbing shield. The proc path has had this for a while
            # via apply_effect, but a cast buff had NO way to express a shield
            # at all, which is why half a dozen abilities whose entire purpose
            # is shielding - Cultist's Void Shield, Eldritch Bastion and
            # Forbidden Ritual, Starcaller's Moonlit Bulwark - were buffs with
            # empty stat_mods that did nothing when cast.
            #
            # Sized per RECIPIENT inside the loop below, so a party-wide shield
            # scales to each ally's own health rather than the caster's.
            for recipient in recipients:
                shield_amt = int(self.absorb or 0)
                if self.absorb_pct_max_health:
                    shield_amt = max(1, int(getattr(recipient, "health", 0)
                                            * self.absorb_pct_max_health))
                effect = StatusEffect(
                    absorb=shield_amt,
                    effect_id=self.ability_id, name=self.name,
                    effect_type=EffectType.BUFF, duration=self.talented_duration(caster),
                    stat_mods=mods, source_name=caster.name,
                    real_time_seconds=real_time,
                    exclusive_group=self.exclusive_group,
                    proc=self.active_proc,
                    # a proc's bonus damage (weapon imbues) resolves through this school's resistance
                    damage_school=(self.damage_school if isinstance(self.damage_school, str)
                                   and self.damage_school in DamageSchool.ALL_SCHOOLS else "physical"),
                )
                recipient.apply_status_effect(effect)

            mod_text = ", ".join(f"{k.replace('_', ' ')} +{v}"
                                 for k, v in mods.items() if v)
            if len(recipients) > 1:
                return (f"{caster.name} uses {self.name} on the party "
                        f"({mod_text})!")
            who = recipients[0]
            if who is caster:
                return f"{caster.name} gains {self.name} ({mod_text})!"
            return f"{caster.name} grants {who.name} {self.name} ({mod_text})!"

        elif self.effect_type == "debuff":
            # Temporary enemy debuff. Values in stat_mods should be NEGATIVE.
            # AoE debuffs (e.g. a Frost Nova-style root/snare on the whole
            # pack) apply the same mods to every living enemy passed in.
            # Debuffs default to buff_scope="combat" (see __init__) - a
            # weakening effect has no business outlasting the fight it was
            # applied in unless explicitly authored as "raid" scope.
            recipients = self._hostile_recipients(target)
            if recipients:
                # Same _pct-suffix exemption as the buff branch above -
                # percentage-shaped debuff stat_mods must stay fractional,
                # not get int()-truncated to 0.
                mods = {}
                for k, v in (self.stat_mods or {}).items():
                    scaled = v * (self.effect_value / 100.0)
                    mods[k] = scaled if k.endswith("_pct") else int(scaled)
                real_time = None if self.buff_scope == "combat" else _UNSET
                for t in recipients:
                    effect = StatusEffect(
                        effect_id=self.ability_id, name=self.name,
                        effect_type=EffectType.DEBUFF,
                        duration=self.talented_duration(caster),
                        stat_mods=mods, source_name=caster.name,
                        real_time_seconds=real_time,
                        dispel_type=self.dispel_type,
                        exclusive_group=self.exclusive_group,
                        proc=self.active_proc,
                        is_stun=self.is_stun,
                    )
                    t.apply_status_effect(effect)
                    # force_proc_group (Barbed Stinger): find whichever
                    # active effect on the CASTER shares this
                    # exclusive_group - i.e. the one Venom currently
                    # loaded - and guarantee its proc fires THIS cast,
                    # bypassing the Venom's own chance roll.
                    #
                    # Does NOT call fire_proc_trigger directly here - a
                    # taunt debuff already generates a synthetic threat
                    # "damage" event (see the taunt-threat block a few
                    # hundred lines down in use(), which runs AFTER
                    # _apply_effect returns) that independently fires a
                    # real ON_DAMAGE_CAST proc check via the engine's own
                    # normal cast-completion path. Calling
                    # fire_proc_trigger a second time here would double-
                    # fire the SAME Venom off the SAME cast (caught via a
                    # direct test: Debilitating/Nullifying Venom's forced
                    # message appeared twice - this ability's own taunt-
                    # threat roll independently also matched). Instead,
                    # this only mutates the live effect's proc dict to
                    # guaranteed-fire values (chance=100, icd=0) and
                    # leaves it set - use()'s own taunt-driven
                    # ON_DAMAGE_CAST firing (which matches
                    # ON_DAMAGE_OR_HEAL_CAST-declared procs, see
                    # _fire_proc_trigger_inner) does the actual firing
                    # exactly once, using its real message. Restored back
                    # to the stored real proc dict in use() right after
                    # that firing happens (see the restore block below the
                    # taunt-threat/proc-trigger section), so the
                    # Venomancer's normal passive chance-based proccing on
                    # every OTHER cast is completely unaffected.
                    if self.force_proc_group and hasattr(caster, "_effects"):
                        active = next(
                            (e for e in caster._effects()
                             if getattr(e, "exclusive_group", None) == self.force_proc_group
                             and getattr(e, "proc", None)),
                            None)
                        if active is not None:
                            self._forced_proc_effect = active
                            self._forced_proc_original = dict(active.proc)
                            active.proc = dict(active.proc)
                            active.proc["chance"] = 100
                            active.proc["icd"] = 0
                mod_text = ", ".join(f"{k.replace('_', ' ')} {v}"
                                     for k, v in mods.items() if v and k != "taunt")
                # Stun/incapacitate/fear/sleep debuffs (is_stun=True) carry
                # no stat_mods at all - mod_text is empty for these, so the
                # old "(...)" suffix rendered as a bare, empty "()" in the
                # combat log. Use dedicated stun-flavored phrasing instead
                # of a generic "weakens" message with nothing to show.
                # force_proc_group abilities (Barbed Stinger) get dedicated
                # taunt-flavored phrasing instead of the generic "weakens"
                # line, same reasoning as the is_stun branch above: its
                # only stat_mods entry is taunt (filtered out of mod_text
                # on purpose), so the generic line would render as a bare,
                # contentless "weakens X with Barbed Stinger ()". The real
                # forced-proc message (e.g. "Debilitating Venom triggers
                # Debilitating Venom on Dummy!") is NOT appended here - it
                # arrives separately, appended to this whole return value
                # by use()'s own taunt-driven ON_DAMAGE_CAST proc firing
                # (see the proc_msgs loop and force_proc_group restore
                # block further down in use()), so it isn't duplicated.
                if self.is_stun:
                    if is_aoe and len(recipients) > 1:
                        return f"{caster.name} incapacitates all enemies with {self.name}!"
                    return f"{caster.name} incapacitates {recipients[0].name} with {self.name}!"
                if self.force_proc_group:
                    return f"{caster.name} taunts {recipients[0].name} with {self.name}!"
                if is_aoe and len(recipients) > 1:
                    return f"{caster.name} weakens all enemies with {self.name} ({mod_text})!"
                return f"{caster.name} weakens {recipients[0].name} with {self.name} ({mod_text})!"
            return f"{caster.name} uses {self.name}!"

        elif self.effect_type == "enable_instant_cast":
            # Nature's Swiftness: itself an instant self-buff (is_instant
            # should be True on abilities using this effect_type, so this
            # cast doesn't consume a turn either) that makes the caster's
            # VERY NEXT ability use instant too, regardless of what that
            # ability is. See CombatEngine.execute_ability for where
            # next_cast_instant is actually read and consumed - this
            # branch only sets the flag, since Ability has no reference to
            # the combat engine's turn-ending logic to skip a turn itself.
            caster.next_cast_instant = True
            return f"{caster.name}'s next spell will be instant!"

        elif self.effect_type == "dispel":
            # Cleanse Spirit / Remove Curse / Purify-style abilities:
            # removes up to self.dispel_count active debuffs/DoTs on the
            # target matching this ability's dispel_type (see
            # StatusEffect.dispel_type and StatusEffectMixin.dispel_effect -
            # dispel_type itself may be one DispelType or a tuple of them,
            # e.g. real Paladin Cleanse's "Poison, Disease, or Magic" in
            # one cast). If NOTHING was removed, the cast fails and
            # refunds - same all-or-nothing pattern as Swiftmend's
            # consumes_hot branch above, since a dispel that removes
            # nothing shouldn't cost a turn or mana. A multi-count dispel
            # that removes 1-of-2 still succeeds (partial credit, matching
            # how a real cast that finds fewer matching effects than its
            # max still goes off) - only a full zero refunds.
            if not target:
                return f"{caster.name} casts {self.name}!"
            removed_names = []
            for _ in range(self.dispel_count):
                removed = target.dispel_effect(self.dispel_type)
                if removed is None:
                    break
                removed_names.append(removed.name)
            if not removed_names:
                self._refund_failed_cast(caster, cost=cost)
                dispel_label = (self.dispel_type or "effect")
                if isinstance(dispel_label, (tuple, list)):
                    dispel_label = "/".join(d.capitalize() for d in dispel_label if d)
                else:
                    dispel_label = dispel_label.capitalize()
                return f"{target.name} has no {dispel_label} effect to remove!"
            return f"{caster.name} dispels {', '.join(removed_names)} from {target.name}!"

        elif self.effect_type == "revive":
            # Battle-resurrection-style ability: brings a DEAD ally back to
            # a percentage of their max HP. New effect_type - no engine
            # mechanism for reviving anyone existed before this (is_alive()
            # is purely current_health > 0, so "coming back" just means
            # setting current_health positive again; nothing else in the
            # engine caches a dead-list - turn_meter/combat_engine's
            # targeting/turn-order all re-check is_alive() live every time,
            # so a revived character is immediately eligible for turns and
            # targeting with no other state to untangle). Built specifically
            # so Venomancer's Unyielding Will ("reduces threat lost on
            # death by 5%/rank") has something real to apply to - see the
            # death_threat_retention_pct read below.
            #
            # target must be a SPECIFIC dead ally, not auto-picked - the
            # normal heal-target helpers (_lowest_hp_ally, etc) all filter
            # to LIVING allies by design and would never select a corpse,
            # so this intentionally bypasses them and requires the caller
            # (UI/AI) to have chosen a specific dead party member.
            if not target or not hasattr(target, "is_alive"):
                self._refund_failed_cast(caster, cost=cost)
                return f"{self.name} requires a fallen ally to target!"
            if target.is_alive():
                self._refund_failed_cast(caster, cost=cost)
                return f"{target.name} is not dead!"

            revive_pct = max(0.0, min(1.0, self.effect_value / 100.0))
            revive_hp = max(1, int(target.health * revive_pct))

            # death_threat_retention_pct (Venomancer's Unyielding Will) is
            # applied by CombatEngine right after this use() call returns,
            # not here - threat_tables live on the engine, not on Ability/
            # Character, and _apply_effect has no engine reference to read
            # them through (unlike fire_proc_trigger's proc payloads, which
            # DO thread one in from a different call site). See
            # CombatEngine's post-use revive handling for the actual
            # threat-table mutation; this branch only resolves the HP
            # change, which is all it has the context to do correctly.
            target.current_health = revive_hp
            target._reviving_this_cast = True  # one-shot flag CombatEngine reads and clears right after use()
            return f"{caster.name} revives {target.name}, restoring {revive_hp} health!"

        elif self.effect_type == "reset_cooldowns":
            # Cold Snap: instantly resets cooldowns. Real WOTLK only resets
            # Frost-school abilities specifically - this engine has no
            # per-ability school/damage-type tag to filter by (abilities
            # aren't categorized as Frost/Fire/Arcane etc, only by
            # effect_type), so this resets ALL of the caster's ability
            # cooldowns instead. Broader than the real spell, but still a
            # genuinely powerful and correctly-documented simplification
            # rather than an unbuilt no-op.
            if hasattr(caster, "ability_book"):
                for ability in caster.ability_book.get_all_abilities():
                    ability.turns_remaining = 0
            return f"{caster.name}'s ability cooldowns are reset!"

        elif self.effect_type == "shapeshift":
            # Real castable shapeshift ability (Bear/Cat/Moonkin/Tree of Life
            # for Druid, Spider/Beetle/Weaver/Vizier Form for Venomancer,
            # etc.) - calls the same Character.shift_form() the standalone
            # form_screen.py menu used to call directly. Kyle's direction:
            # shifting should be a real spell you cast from the hotbar/
            # spellbook like anything else, not a separate out-of-band menu
            # bound to its own keypress - form_screen.py and the H-keybind
            # are being retired in favor of this. self.shapeshift_form_id is
            # set from the JSON's "shapeshift_form" key at load time.
            if not self.shapeshift_form_id:
                return f"{caster.name} tries to shapeshift, but has no form to become!"
            if not hasattr(caster, "shift_form"):
                return f"{caster.name} cannot shapeshift."
            # Recasting the form you are already in drops it (WoW behaviour) -
            # this is the way back to Normal Form now the form screen is retired.
            if getattr(caster, "current_form", None) == self.shapeshift_form_id and hasattr(caster, "revert_form"):
                success, msg = caster.revert_form()
                return msg
            success, msg = caster.shift_form(self.shapeshift_form_id)
            if not success:
                self._refund_failed_cast(caster, cost=cost)
            return msg

        elif self.effect_type == "summon_pet":
            # Real castable pet summon (Hunter taming, Warlock demon
            # summons, Primalist's Spirit Beast Master companion,
            # Stormbringer Wind's Air Elemental, Tinker Invention's
            # ZIGGI-6K) - calls the same Character.summon_pet() the
            # standalone pet_screen.py menu already calls directly for
            # Hunter/Warlock. Kyle, Oct 2026: "We need the pet system up
            # and running" - the Pet engine itself (entities/pet.py,
            # combat turn integration, AI) already existed, and so did
            # real templates for Warlock's 4 demons and Hunter's Wolf, but
            # NOTHING anywhere actually called summon_pet() from a cast -
            # every pet-flavored ability for Primalist/Stormbringer/Tinker
            # was explicitly stubbed as a plain self-buff for exactly this
            # reason (see each one's own _implementation_note), and
            # Warlock had templates with no summon spell to use them.
            # self.summon_pet_template is set from the JSON's
            # "summon_pet_template" key at load time.
            #
            # Unlike shapeshift (which only ever fails on a missing
            # form_id/method), summon_pet's real Character.summon_pet()
            # can ALSO fail on a legitimate game-rule check (e.g. level
            # requirement) - its own (success, message_or_pet) return
            # already distinguishes this, so failure here refunds the
            # cast and surfaces that specific reason rather than a generic
            # "cannot summon" the way shapeshift's branch does, since
            # shapeshift has no equivalent rejection reason to show.
            if not self.summon_pet_template:
                return f"{caster.name} tries to summon a pet, but has nothing to summon!"
            if not hasattr(caster, "summon_pet"):
                return f"{caster.name} cannot summon pets."
            success, result = caster.summon_pet(self.summon_pet_template)
            if not success:
                self._refund_failed_cast(caster, cost=cost)
                return result
            return f"{caster.name} summons {result.name}!"

        elif self.effect_type == "restore_resource":
            # Evocation-like self-only resource restore (Tinker Invention's
            # ZIGGI-6K, lvl 30: Kyle - "evocation like skill at 30"). Unlike
            # damage_and_restore_mana (Stormbringer's Discharge - restores
            # the CASTER's mana as a side effect of hitting an ENEMY), this
            # has no target at all: it's a pure self-buff that instantly
            # refills a % of whichever resource pool the caster actually
            # uses (mana/rage/energy - reads caster.resource_type generically
            # rather than hardcoding Mana, so this isn't ZIGGI-6K-specific
            # plumbing). Reuses mana_restore_pct's existing rank key rather
            # than inventing a second "restore percent" field - the name is
            # slightly stale for a non-mana resource, but the field already
            # exists, already means "% of max resource restored", and
            # adding a near-duplicate field just to rename it isn't worth
            # the churn for one ability.
            if not hasattr(caster, "gain_resource") or not hasattr(caster, "get_resource_max"):
                return f"{caster.name} has no resource pool to restore."
            # restore_resource_type lets an ability name the pool explicitly
            # instead of always using the caster's PRIMARY one. Needed for
            # secondary pools: Cultist's Sanity Tap restores Insanity, not
            # Mana, and reading caster.resource_type would have silently
            # refilled the wrong bar. Absent (the default, and every use
            # before this) keeps the primary-pool behaviour exactly.
            resource_type = (self.restore_resource_type
                             or getattr(caster, "resource_type", "mana"))
            max_resource = caster.get_resource_max(resource_type)
            restore_amt = int(max_resource * (self.mana_restore_pct / 100.0))
            restored = caster.gain_resource(resource_type, restore_amt)
            return f"{caster.name} channels {self.name}, restoring {restored} {resource_type}!"

        elif self.effect_type == "totem_loadout":
            # Call of the Elements/Ancestors/Spirits: casts every totem
            # currently slotted in the caster's totem_loadout (see
            # Character.set_totem / combat/totems.py) as ONE action -
            # Kyle's original ask, confirmed real WOTLK mechanic. Each
            # slotted totem is cast through the exact same Ability.use()
            # path it would use standalone, so a party buff totem still
            # heals/buffs the party and a damage totem like Searing Totem
            # still needs an enemy target - this ability itself never
            # duplicates that logic, it just triggers each real ability
            # in sequence.
            loadout = getattr(caster, "totem_loadout", {})
            if not loadout:
                self._refund_failed_cast(caster, cost=cost)
                return f"{caster.name} has no totems slotted!"

            party = self._recipients(caster, target) if target else [caster]
            enemy_target = None
            # A damage-type totem (Searing Totem) needs an enemy, not the
            # party target this ability itself was cast with (Call of the
            # Ancestors is target_type="party") - the caller's `target`
            # kwarg IS the party in that case, so hostile totems fall back
            # to whatever the combat engine's default enemy target is via
            # the ability_book lookup below rather than mistakenly firing
            # at an ally.
            cast_names = []
            book = caster.ability_book if hasattr(caster, "ability_book") else None
            for element, totem_id in loadout.items():
                totem_ability = book.get_ability(totem_id) if book else None
                if totem_ability is None:
                    continue
                totem_target = party if totem_ability.target_type in ("party", "ally", "self") else target
                success_inner, _ = totem_ability.use(caster, totem_target)
                if success_inner:
                    cast_names.append(totem_ability.name)
            if not cast_names:
                return f"{caster.name}'s totems failed to activate!"
            return f"{caster.name} calls forth: {', '.join(cast_names)}!"

        return f"{caster.name} uses {self.name}!"
    
    def decrement_cooldown(self):
        """Decrement cooldown by 1 turn (called after turn ends)."""
        if self.turns_remaining > 0:
            self.turns_remaining -= 1


class AbilityBook:
    """Collection of abilities for a character."""
    
    def __init__(self):
        self.abilities = {}  # Dict of ability_id -> Ability
    
    def add_ability(self, ability):
        """Add an ability to the book."""
        self.abilities[ability.ability_id] = ability
    
    def get_ability(self, ability_id):
        """Get ability by ID."""
        return self.abilities.get(ability_id)
    
    def get_all_abilities(self):
        """Get all abilities."""
        return list(self.abilities.values())
    
    def decrement_all_cooldowns(self):
        """Decrement all ability cooldowns by 1 turn (called at end of turn)."""
        for ability in self.abilities.values():
            ability.decrement_cooldown()


# ============================================================
# ABILITY LOADING (data-driven)
# ============================================================
# Ability kits used to be nine hardcoded create_<class>_abilities() factory
# functions right here. That made abilities the only major game system NOT
# data-driven - items, creatures, consumables and talents all load from JSON.
#
# They now load from data/abilities/<class>.json, regenerated by
# tools/generate_abilities.py. The get_class_abilities() signature is
# unchanged, so every existing caller (Character, combat_screen,
# character_sheet_screen) keeps working untouched.

# Every ResourceType, keyed by its JSON string. Built from the enum rather
# than hand-listed: the hand-listed version only covered rage/energy/mana/
# health, so a CoA ability declaring "static" silently fell back to MANA and
# charged the wrong pool - Aeroblast was castable at 0 Static and billed 50
# Mana instead. Deriving this from the enum means a new ResourceType can
# never be forgotten here again.
_RESOURCE_BY_NAME = {rt.value: rt for rt in ResourceType}

_ABILITY_CACHE = {}


def _abilities_dir():
    from pathlib import Path
    return Path(__file__).parent.parent / "data" / "abilities"


def _class_file_prefix(char_class):
    """Map a class display name to its JSON filename stem."""
    return char_class.lower().replace(" ", "_")


def _load_class_ability_data(char_class):
    """Read and cache the raw JSON for a class. Returns [] if absent, so a
    class with no authored kit yet (the 21 CoA classes) degrades to an empty
    ability book rather than crashing."""
    prefix = _class_file_prefix(char_class)
    if prefix in _ABILITY_CACHE:
        return _ABILITY_CACHE[prefix]

    import json
    path = _abilities_dir() / f"{prefix}.json"
    if not path.exists():
        _ABILITY_CACHE[prefix] = []
        return []

    try:
        with open(path, "r") as f:
            data = json.load(f)
        abilities = data.get("abilities", [])
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: failed to load abilities for {char_class}: {e}")
        abilities = []

    _ABILITY_CACHE[prefix] = abilities
    return abilities


def _normalize_requires_form(raw):
    """requires_form comes from JSON as either a bare string (e.g.
    Venomancer's "beetle", "spider") or a list (e.g. Druid's
    ["bear","dire_bear"]) - both authored correctly by different
    sessions, neither wrong on its own, but is_form_ready's `current in
    self.requires_form` check relies on Python's `in` operator, which
    means CONTAINMENT for a list but SUBSTRING match for a bare string.
    That's a real latent hazard even though no two current form ids
    happen to be substrings of each other today (verified) - a future
    form named e.g. "cat" would incorrectly satisfy a requires_form of
    "beetlecat" via substring match. Normalizing every requires_form to
    a real list at load time removes the hazard entirely rather than
    relying on lucky naming to keep working. None stays None (no
    requirement) rather than becoming an empty list, since is_form_ready
    checks truthiness first."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return [raw]
    return raw


def _ability_from_data(entry):
    """Build an Ability instance from one JSON entry."""
    resource = _RESOURCE_BY_NAME.get(
        entry.get("resource_type", "mana"), ResourceType.MANA)
    return Ability(
        entry["ability_id"],
        entry["name"],
        resource,
        ranks=entry["ranks"],
        cooldown=entry.get("cooldown", 0),
        effect_type=entry.get("effect_type", "damage"),
        description=entry.get("description", ""),
        duration=entry.get("duration", 0),
        stat_mods=entry.get("stat_mods", {}),
        generates=entry.get("generates"),
        target_type=entry.get("target_type"),
        buff_scope=entry.get("buff_scope"),
        requires_talent=entry.get("requires_talent"),
        restore_resource_type=entry.get("restore_resource_type"),
        absorb=entry.get("absorb", 0),
        absorb_pct_max_health=entry.get("absorb_pct_max_health", 0.0),
        is_instant=entry.get("is_instant", False),
        consumes_hot=entry.get("consumes_hot", False),
        consumable_hot_ids=entry.get("consumable_hot_ids"),
        dispel_type=entry.get("dispel_type"),
        dispel_count=entry.get("dispel_count", 1),
        consumes_stacks_of=entry.get("consumes_stacks_of"),
        duration_per_stack=entry.get("duration_per_stack", 0),
        max_targets=entry.get("max_targets"),
        force_proc_group=entry.get("force_proc_group"),
        summon_pet_template=entry.get("summon_pet_template"),
        requires_form=_normalize_requires_form(entry.get("requires_form")),
        heal_scope=entry.get("heal_scope", "lowest_ally"),
        exclusive_group=entry.get("exclusive_group"),
        heal_in_form=tuple(entry["heal_in_form"]) if entry.get("heal_in_form") else None,
        applies_dot_pct=entry.get("applies_dot_pct"),
        shapeshift_form_id=entry.get("shapeshift_form"),
        consumes_seal=entry.get("consumes_seal", False),
        proc=entry.get("proc"),
        execute_threshold_pct=entry.get("execute_threshold_pct"),
        damage_school=entry.get("damage_school"),
        requires_ranged_weapon=entry.get("requires_ranged_weapon"),
        is_stun=entry.get("is_stun", False),
        icon_id=entry.get("icon_id"),
    )


_UNIVERSAL_ABILITY_CACHE = None


def _load_universal_ability_data():
    """Read and cache data/abilities/_universal.json - the small set of
    abilities every class gets regardless of kit (currently just Shoot
    and Wand, gated by requires_ranged_weapon so only one is ever usable
    at a time based on what's actually equipped). Returns [] if the file
    is missing/corrupt rather than crashing character creation - same
    fail-soft convention as _load_class_ability_data."""
    global _UNIVERSAL_ABILITY_CACHE
    if _UNIVERSAL_ABILITY_CACHE is not None:
        return _UNIVERSAL_ABILITY_CACHE

    import json
    path = _abilities_dir() / "_universal.json"
    if not path.exists():
        _UNIVERSAL_ABILITY_CACHE = []
        return []

    try:
        with open(path, "r") as f:
            data = json.load(f)
        abilities = data.get("abilities", [])
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: failed to load universal abilities: {e}")
        abilities = []

    _UNIVERSAL_ABILITY_CACHE = abilities
    return abilities


def get_class_abilities(char_class):
    """Get the ability book for a class, loaded from data/abilities/.

    Returns an empty AbilityBook for any class without an authored kit
    (currently the 21 CoA classes), which is why every caller must tolerate
    an empty book rather than assuming at least one ability exists.

    Every class also gets the universal Shoot/Wand actions from
    _universal.json folded in - these aren't class-specific kit entries,
    so they're added on top rather than requiring every per-class JSON
    file to duplicate them.
    """
    book = AbilityBook()
    for entry in _load_class_ability_data(char_class):
        ability = _ability_from_data(entry)
        ability.trainable = not ability.requires_talent
        book.add_ability(ability)
    for entry in _load_universal_ability_data():
        book.add_ability(_ability_from_data(entry))
    return book
