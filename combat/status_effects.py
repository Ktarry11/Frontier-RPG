"""
Status effects: damage-over-time, heal-over-time, and temporary stat
buffs/debuffs.

WHY THIS EXISTS
---------------
Before this module, `effect_type` supported only "damage", "spell_damage",
"heal" and a stub "buff" that did literally nothing. That meant every
nominally-DoT ability in the game - Rend, Corruption, Immolate, Shadow Word:
Pain, Moonfire, Rejuvenation - resolved as a single instant hit. Roughly half
the class roster is built around damage over time, so those classes had no
actual identity in combat.

DESIGN
------
Effects are owned by the combatant they're applied TO, in an `active_effects`
list. `tick_effects()` is called once per turn from CombatEngine._end_turn(),
which is the same place cooldowns decrement - so "1 turn" means exactly the
same thing everywhere.

Ticking order is deliberate: the effect deals/heals first, THEN decrements
its remaining duration. A 3-turn DoT therefore ticks 3 times, which is what
a player reading "deals X damage over 3 turns" expects.

Both Character and Monster get this via `StatusEffectMixin`, so the engine
never has to branch on which class it's holding.

STACKING
--------
Re-applying an effect with the same `effect_id` REFRESHES it (duration resets
to full, potency updated to the new value) rather than adding a second copy.
This matches WoW and prevents the degenerate "spam Corruption 8 times" case.
Effects from different abilities have different ids and stack normally.
"""


class DamageSchool:
    """Real WotLK-style spell schools, plus PHYSICAL. Used by Ability.
    damage_school and Character.take_damage's damage_type parameter to
    select which resistance stat (see Character's *_resistance attributes
    and get_resistance()) mitigates a given hit.

    MAGIC is kept as a legacy alias for abilities that haven't been
    assigned a real school yet (every spell_damage/dot/hot ability
    predates this system) - it resolves through get_resistance() to the
    OLD flat magic_resistance stat, not a new school, so nothing that
    already worked changes behavior until an ability is deliberately
    migrated to a real school (FIRE, FROST, ...). Don't author NEW
    content against MAGIC; it exists only so 100+ pre-existing
    "magic"-typed abilities keep working unmodified.

    Combined/hybrid schools (Shadowfrost, Plague = Nature+Shadow, ...)
    aren't separate constants here - they're expressed as a tuple of two
    base schools wherever an ability's damage_school is set (e.g.
    ("shadow", "frost")), and get_resistance() resolves a tuple to
    whichever component resistance is LOWEST (Kyle's call: combined
    schools should be harder to resist, not easier, since they're
    intentionally rare/exotic damage types).
    """
    PHYSICAL = "physical"
    FIRE = "fire"
    FROST = "frost"
    NATURE = "nature"
    SHADOW = "shadow"
    ARCANE = "arcane"
    HOLY = "holy"
    MAGIC = "magic"  # legacy alias - see docstring

    #: Sentinel for Runemaster's real Frost/Fire/Arcane Attunement cycle
    #: (see StatusEffectMixin.RUNEMASTER_ATTUNEMENT_CYCLE/_tick_attunement).
    #: An ability with damage_school=ATTUNEMENT doesn't deal a fixed
    #: school - it resolves to whatever caster.current_attunement is at
    #: the moment it's cast (see Ability._apply_effect's real resolution:
    #: it substitutes the live attunement value before calling
    #: take_damage, so resistance mitigation, the combat log's school
    #: name, and everything else downstream sees a real concrete school
    #: like "fire", never this sentinel itself). Falls back to "arcane"
    #: if the caster has no current_attunement (e.g. a non-Runemaster
    #: somehow granted an attunement-schooled ability, or before the
    #: first _tick_attunement call has run) - matches this project's
    #: existing collapsed-simplification default from before the real
    #: cycle was built.
    ATTUNEMENT = "attunement"

    ALL_SCHOOLS = (FIRE, FROST, NATURE, SHADOW, ARCANE, HOLY)


class EffectType:
    DOT = "dot"          # damage each turn
    HOT = "hot"          # healing each turn
    BUFF = "buff"        # temporary stat modifier on self
    DEBUFF = "debuff"    # temporary stat modifier on enemy


class ProcTrigger:
    """Real event names a StatusEffect's `proc` dict can react to.

    Each is fired from an ACTUAL point in the engine where that event
    already resolves - not an imagined hook - so a proc always reacts to
    something that genuinely just happened:

      ON_CAST                 - any ability successfully used by the actor
                                 carrying this effect (Ability.use, after
                                 cost is paid). Fires regardless of
                                 effect_type - a buff, a heal, a nuke, all
                                 count as "a cast."
      ON_DAMAGE_CAST           - specifically a cast that dealt damage to at
                                 least one target (subset of ON_CAST).
                                 Covers ALL damage - spells included. Do
                                 NOT use this for weapon-imbue-style procs
                                 (Windfury/Flametongue/Rockbiter/Frostbrand)
                                 - use ON_WEAPON_SWING instead, or the proc
                                 fires off spell damage too (a real bug
                                 caught in Rockbiter: it was proccing off
                                 Healing Wave and every other spell cast,
                                 since ON_DAMAGE_CAST doesn't distinguish
                                 "your basic weapon attack" from "any
                                 damage source at all").
      ON_WEAPON_SWING           - specifically the caster's own basic
                                 attack ability (ability_id ending in
                                 "_attack", the same real "<class_prefix>_
                                 attack" convention extra_attack already
                                 relies on - see fire_proc_trigger). This
                                 is what real WoW weapon imbues actually
                                 proc off - never spells, never DoTs
                                 ticking, only your own melee/ranged swing
                                 landing. A subset of ON_DAMAGE_CAST, but
                                 fired as its OWN separate trigger name so
                                 imbue-style procs can listen for exactly
                                 this and nothing broader.
      ON_HEAL_CAST              - specifically a cast that landed a heal on
                                 at least one target (subset of ON_CAST).
      ON_DAMAGE_OR_HEAL_CAST     - either of the above two - the shape most
                                 CoA "Vow"/"Devotion"-style effects actually
                                 need (Vow of Radiance procs off ANY damage
                                 or healing cast, not just one or the other).
      ON_CRIT                  - the cast that triggered this event landed
                                 at least one crit (fired alongside
                                 ON_DAMAGE_CAST/ON_HEAL_CAST for the same
                                 cast, not instead of it).
      ON_DAMAGE_TAKEN            - the carrier took damage (fired from
                                 Character.take_damage, after mitigation).
      ON_KILL                   - the carrier's action killed a target
                                 (fired from CombatEngine's death check).

    context (passed to fire_proc_trigger) always includes at least
    {"amount": int}, the real damage/heal amount from the event that fired
    it - what makes bonus_pct procs (see StatusEffectMixin.fire_proc_trigger)
    able to add real extra damage to the SAME hit, WoW-style, rather than
    logging a description of an effect that never mechanically happens.
    """
    ON_CAST = "on_cast"
    ON_DAMAGE_CAST = "on_damage_cast"
    ON_WEAPON_SWING = "on_weapon_swing"
    ON_HEAL_CAST = "on_heal_cast"
    ON_DAMAGE_OR_HEAL_CAST = "on_damage_or_heal_cast"
    ON_CRIT = "on_crit"
    ON_DAMAGE_TAKEN = "on_damage_taken"
    ON_KILL = "on_kill"

    #: AVOIDANCE TRIGGERS. Until these existed the only defensive hook was
    #: ON_DAMAGE_TAKEN, which fires when a hit LANDS - the opposite of
    #: avoiding one - so every talent in the game written as "blocking an
    #: attack does X" or "avoiding an attack does X" had to be rewritten as
    #: "being hit does X". An audit against the real Conquest of Azeroth
    #: trees found that rewrite in a dozen places across three classes, and
    #: it quietly inverted their design:
    #:
    #:   Moon Guard   Nebula, Starlight Duelist and Dancing in the Moonlight
    #:                all pay out on block or parry in CoA. Rewritten onto
    #:                damage taken, the spec's #4-#6 stats (parry, dodge,
    #:                block) bought it nothing at all, which is the real
    #:                reason it measured last on survival - not a shortage
    #:                of mitigation.
    #:   Dreadnought  Inner Darkness generates its secondary resource FROM
    #:                BLOCKING. Ungated, it generated unconditionally.
    #:   Guardian     Retaliation is "blocks strike back".
    #:
    #: ON_AVOID fires for a dodge or a parry, which is how CoA words the
    #: ones that do not care which ("Avoiding melee attacks will call down a
    #: Moonflare"). ON_BLOCK is separate because a block is a partial hit,
    #: not an avoid, and several talents key off exactly that difference.
    ON_DODGE = "on_dodge"
    ON_PARRY = "on_parry"
    ON_AVOID = "on_avoid"
    ON_BLOCK = "on_block"

    ALL = (ON_CAST, ON_DAMAGE_CAST, ON_WEAPON_SWING, ON_HEAL_CAST,
           ON_DAMAGE_OR_HEAL_CAST, ON_CRIT, ON_DAMAGE_TAKEN, ON_KILL,
           ON_DODGE, ON_PARRY, ON_AVOID, ON_BLOCK)


class DispelType:
    """WoW's real dispel-school categories. A debuff/DoT tagged with one of
    these can be removed by a cleanse/dispel ability that targets that
    specific school - e.g. a Shaman's Cleanse Spirit only removes Curse,
    not Poison or Disease. NONE means "not dispellable by anything" (most
    plain combat debuffs, e.g. a rogue's Expose Armor).
    """
    NONE = None
    MAGIC = "magic"
    CURSE = "curse"
    POISON = "poison"
    DISEASE = "disease"

    ALL = (MAGIC, CURSE, POISON, DISEASE)


#: How long a buff/debuff lasts in the real world, in seconds - 30 minutes,
#: matching WoW's standard raid-buff duration (Fortitude, Might, Mark of the
#: Wild, etc all last 30 min there). DoTs/HoTs are unaffected; they keep
#: their turn-based duration since they only make sense inside a fight.
BUFF_DURATION_SECONDS = 30 * 60

#: Sentinel distinguishing "caller didn't pass real_time_seconds at all" (use
#: the 30-min default) from "caller explicitly passed None" (stay turn-based,
#: like a DoT/HoT). Before this existed both cases looked identical from
#: inside __init__, so monster.py's `real_time_seconds=None` - written
#: specifically to keep combat buffs like Frenzy turn-based - was silently
#: indistinguishable from omitting the argument and got the 30-minute clock
#: anyway. A monster's 3-turn self-buff was therefore active for the entire
#: fight (and would have bled into the next one too), never visibly ticking
#: down. See monster.py's buff/debuff branch for the actual opt-out.
_UNSET = object()


class StatusEffect:
    """A single active effect on a combatant."""

    def __init__(self, effect_id, name, effect_type, duration,
                 potency=0, damage_school="physical", stat_mods=None,
                 source_name="", real_time_seconds=_UNSET, dispel_type=None,
                 exclusive_group=None, proc=None, is_stun=False,
                 max_stacks=1, absorb=0):
        """
        effect_id: stable id used for refresh-vs-stack decisions
                   (e.g. "warrior_rend"). Same id = refresh.
        max_stacks: real WoW-style stacking debuff/buff support (Venomancer's
                   Exposed Flesh: "...stacking 10 times"). 1 (the default)
                   means ordinary refresh-in-place behavior, completely
                   unchanged from every effect authored before this existed.
                   >1 means re-applying the SAME effect_id increments
                   `stacks` (capped at max_stacks) instead of just resetting
                   duration - see apply_status_effect's stacking branch.
                   stat_mods on a stacking effect are PER-STACK (like a
                   talent's per-rank effects): the actual bonus pool
                   contribution is stat_mods multiplied by current `stacks`,
                   not the flat dict - see StatusEffectMixin.get_status_
                   stat_mod, which already needs to read this correctly for
                   stacking to mean anything mechanically rather than just
                   changing a number in the UI.
        absorb:    BUFF only. A flat HP pool that soaks incoming damage
                   before it touches current_health (Tinker's Reactive
                   Plating: "chance to grant a shield absorbing damage" -
                   a genuine WoW-style damage shield, distinct from every
                   existing defensive stat here: armor/resistance reduce
                   damage by a PERCENTAGE forever; absorb soaks a FIXED
                   amount once, then is gone). 0 (the default) means this
                   effect carries no shield - every effect authored before
                   this existed is completely unaffected. See
                   Character.take_damage's absorb-consumption step, which
                   runs BEFORE armor/resistance/pct reductions (a shield
                   should soak the full raw hit, not a discounted one) and
                   removes the effect outright once its pool hits 0,
                   matching how a real WoW shield "breaks" rather than
                   lingering at 0 HP as a dead buff.
        duration:  number of TURNS the effect lasts. Used as-is for DOT/HOT.
                   For BUFF/DEBUFF, this is what's used when
                   real_time_seconds is explicitly None (i.e. stays
                   turn-based) - e.g. a monster's Frenzy with duration=3.
        potency:   damage or healing applied per turn (DOT/HOT only).
        damage_school: "physical" or "magic" - routed to take_damage() so
                   Armor vs Magic Resistance is applied correctly.
        stat_mods: dict of stat_name -> delta, applied while active
                   (BUFF/DEBUFF only), e.g. {"attack_power": -20}.
        real_time_seconds: for BUFF/DEBUFF only. Three states:
                   - omitted entirely -> defaults to BUFF_DURATION_SECONDS
                     (30 min), correct for long-lasting player buffs like
                     Fortitude that should survive outside combat.
                   - explicit None -> stays turn-based using `duration`,
                     correct for short combat buffs like a monster's Frenzy
                     that should never outlast the fight it was cast in.
                   - explicit number -> counts down in real seconds via
                     tick_seconds(dt).
        dispel_type: one of DispelType's constants (or None). Tags this
                   effect with a real WoW dispel school so a cleanse/dispel
                   ability that specifically targets that school (e.g.
                   Cleanse Spirit -> Curse) can find and remove it. Most
                   ordinary combat debuffs (a rogue's Expose Armor, a
                   monster's Frenzy) should leave this as None - "not
                   dispellable."
        exclusive_group: optional string tag. Applying a new effect with the
                   same exclusive_group as an existing one on the target
                   REMOVES the old one first, even if effect_id differs -
                   e.g. Tinker's Rounds ("armor_pen_round", "mana_round",
                   "medic_round"...) all share exclusive_group="tinker_round"
                   so loading a new Round always replaces whichever one was
                   active, matching a single ammo-loadout slot rather than
                   the normal same-id-refreshes / different-id-stacks rule.
                   None (the default) keeps every existing effect's
                   behavior unchanged.
        proc:      optional dict describing a reactive trigger this
                   BUFF/DEBUFF carries, e.g. Vow of Radiance's real
                   mechanic:
                       {"trigger": "on_cast_damage_or_heal",
                        "chance": 100, "icd": 0,
                        "grant_resource": {"resource": "solar_power", "amount": 2},
                        "bonus_pct": 0.25}
                   See ProcTrigger/StatusEffectMixin.fire_proc_trigger for
                   the full field list and valid trigger names. None (the
                   default) means this effect is a plain passive stat_mods
                   buff/debuff with no reactive behavior - every effect
                   authored before this system existed keeps working
                   completely unchanged.
        is_stun:   DEBUFF only. True marks this as a real stun/incapacitate -
                   TurnMeter.update() (combat/turn_meter.py) checks
                   StatusEffectMixin.is_stunned (a derived property, same
                   pattern as current_mechsuit) and refuses to accumulate
                   turn meter for a stunned combatant, so they're
                   genuinely skipped rather than getting a turn that does
                   nothing. False (the default) for every ordinary DEBUFF
                   - ~8 talents (Concussion Blow, Shockwave, Shadowfury,
                   Wyvern Sting, Repentance, Silence, and others) that
                   were flat Haste-debuff placeholders standing in for a
                   missing stun mechanic now use this for real (Kyle,
                   2026-09-06: "we will need stuns built").
        """
        self.effect_id = effect_id
        self.name = name
        self.effect_type = effect_type
        self.duration = duration
        self.max_duration = duration
        self.potency = potency
        self.damage_school = damage_school
        self.stat_mods = stat_mods or {}
        self.source_name = source_name
        self.dispel_type = dispel_type
        self.exclusive_group = exclusive_group
        self.proc = proc or None
        self.is_stun = is_stun
        self.max_stacks = max(1, int(max_stacks))
        # Starts at 1 (a freshly-applied effect is already "one stack"),
        # not 0 - matches how a normal non-stacking effect (max_stacks=1)
        # is simply "active," never "active with zero copies of itself."
        self.stacks = 1
        self.absorb = max(0, int(absorb))
        # Internal-cooldown tracker for this specific effect instance, in
        # turns remaining before its proc can fire again. Lives on the
        # effect (not the ability) since the same ability's buff could in
        # theory be applied by two different sources with independent
        # timers - though in practice same-effect_id refresh (see
        # apply_status_effect) means there's only ever one copy active.
        # Decremented once per turn in tick_status_effects, alongside
        # duration - see fire_proc_trigger for the actual chance/ICD gate.
        self.proc_icd_remaining = 0

        if effect_type in (EffectType.BUFF, EffectType.DEBUFF):
            if real_time_seconds is _UNSET:
                self.real_time_seconds = BUFF_DURATION_SECONDS
            else:
                # Explicit None (or an explicit number) is respected as-is -
                # None means "turn-based", handled by is_expired() falling
                # through to the `duration` check below.
                self.real_time_seconds = real_time_seconds
        else:
            self.real_time_seconds = None

    def is_expired(self):
        if self.real_time_seconds is not None:
            return self.real_time_seconds <= 0
        return self.duration <= 0

    def tick_potency(self):
        """Damage (DOT) or healing (HOT) for ONE tick, scaled by stacks.

        `potency` is stored PER STACK, exactly like `stat_mods` - see the
        constructor docstring, which has always said stacking effects
        contribute their mods multiplied by `stacks`. The DoT/HoT tick path
        never learned that: it ticked for a bare `self.potency`, so a
        stacking DoT was purely cosmetic. Eight stacks of a 100-damage
        Firebrand ticked for 100, same as one, and the only thing that
        changed was the stack number in the UI - which is the same class of
        bug as stacking buffs delivering a single stack through the derived
        stat pool (fixed 2026-10-27), from the same root cause: stacking was
        implemented for stat_mods and nothing else was told about it.

        max_stacks=1 is the overwhelming majority of effects in this game and
        is bit-for-bit unaffected: `stacks` is 1 for its entire life, so this
        multiplies by one. Verified both ways - a non-stacking DoT ticks for
        the identical value it did before, and re-applying it three times
        still ticks once for that value rather than stacking silently.
        """
        return int(self.potency * max(1, self.stacks))

    def to_dict(self):
        return {
            "effect_id": self.effect_id,
            "name": self.name,
            "effect_type": self.effect_type,
            "duration": self.duration,
            "max_duration": self.max_duration,
            "potency": self.potency,
            "damage_school": self.damage_school,
            "stat_mods": self.stat_mods,
            "source_name": self.source_name,
            "real_time_seconds": self.real_time_seconds,
            "dispel_type": self.dispel_type,
            "exclusive_group": self.exclusive_group,
            "proc": self.proc,
            "max_stacks": self.max_stacks,
            "stacks": self.stacks,
            # is_stun was never serialized here despite from_dict being
            # ABLE to read it as an "is_stun" key once passed through -
            # a real pre-existing save/load gap, caught incidentally while
            # adding max_stacks/stacks support: saving mid-fight while
            # stunned and reloading would have silently dropped the stun
            # flag (the effect itself persisted, just not its incapacitate
            # behavior). Fixed alongside rather than left for later, since
            # it's the exact same two-line shape as the fields just added.
            "is_stun": self.is_stun,
            "absorb": self.absorb,
        }

    @staticmethod
    def from_dict(data):
        eff = StatusEffect(
            data["effect_id"], data["name"], data["effect_type"],
            data["duration"], data.get("potency", 0),
            data.get("damage_school", "physical"),
            data.get("stat_mods", {}), data.get("source_name", ""),
            data.get("real_time_seconds"),
            data.get("dispel_type"),
            data.get("exclusive_group"),
            data.get("proc"),
            data.get("is_stun", False),
            data.get("max_stacks", 1),
            data.get("absorb", 0),
        )
        eff.max_duration = data.get("max_duration", eff.duration)
        eff.stacks = data.get("stacks", 1)
        return eff

    def __repr__(self):
        return f"<StatusEffect {self.name} {self.duration}/{self.max_duration}>"


class StatusEffectMixin:
    """Mixed into Character and Monster so both handle effects identically.

    Anything using this must call `_init_status_effects()` in its __init__
    (or tolerate `active_effects` being created lazily by apply_effect).
    """

    def get_talent_effect(self, key, default=0.0):
        """Fallback for anything without talent trees (Monster, Pet): no talent
        bonuses.  Character overrides this with the real talent lookup.  Without
        it, stunning any monster crashed apply_status_effect (Bash crash)."""
        return default

    @property
    def display_health(self):
        """Whole-number HP for UI display (Kyle: "keep HP whole numbers").

        current_health itself stays a real float internally - out-of-combat
        regen (tick_out_of_combat_regen) adds fractional HP every frame
        (spirit * rate * dt), and rounding that raw value on every tick
        would either lose sub-1 gains entirely at low regen rates or cause
        visible stutter-stepping as the displayed number repeatedly rounds
        the same way. Rounding only at the display boundary keeps the real
        underlying math exact while every UI read gets a clean int. Uses
        round() rather than int() truncation so 205.9 displays as 206, not
        205 - matches how a player would expect an HP bar to read.
        """
        return round(self.current_health)

    @property
    def display_mana(self):
        """Whole-number Mana for UI display - same rationale and same
        underlying cause as display_health: tick_out_of_combat_regen adds
        a real float (spirit * OUT_OF_COMBAT_MANA_REGEN_PER_SPIRIT * mult
        * dt) to current_mana every frame, so current_mana itself is
        legitimately fractional between casts. Rounds only at the display
        boundary, same as display_health, for the same reason (exact
        internal math, clean UI number)."""
        return round(getattr(self, "current_mana", 0))

    @property
    def display_rage(self):
        """Whole-number Rage for UI display. Rage doesn't tick per-frame
        the way Mana/HP do, but combat's rage-on-damage-taken gain
        (Character.take_damage: `actual * 0.2`) multiplies real damage by
        a decimal, so current_rage can end up fractional too (e.g. 7
        damage taken -> +1.4 Rage). Same round()-at-display-boundary
        pattern as display_health/display_mana - kept for consistency
        even though the fractional drift here is smaller and rarer."""
        return round(getattr(self, "current_rage", 0))

    @property
    def display_energy(self):
        """Whole-number Energy for UI display. Energy currently only
        changes in fixed integer chunks (see Character's +25/+15/-2 Energy
        adjustments), so this is a no-op today, but it exists so every
        resource pool has the same real display_* accessor rather than
        Energy being the one pool UI code reads raw - if a per-tick or
        percentage-based Energy gain gets added later, display code
        already calling display_energy won't need to change."""
        return round(getattr(self, "current_energy", 0))

    #: Human-readable labels for stat_mods keys, so combat log messages can
    #: actually say what a buff/debuff does ("+8 Agility") instead of just
    #: naming the ability and leaving the mechanical effect invisible to the
    #: player. Falls back to a title-cased version of the raw key for any
    #: stat not listed here, so a new stat added later never prints as a
    #: silent no-op description.
    STAT_LABELS = {
        "attack_power": "Attack Power",
        "spell_power": "Spell Power",
        "healing_power": "Healing Power",
        "armor": "Armor",
        "magic_resistance": "Magic Resistance",
        "strength": "Strength",
        "stamina": "Stamina",
        "intellect": "Intellect",
        "spirit": "Spirit",
        "agility": "Agility",
        "crit_chance_physical": "Physical Crit",
        "crit_chance_spell": "Spell Crit",
        "hit_rating": "Hit Rating",
        "hit_chance_physical": "Physical Hit",
        "hit_chance_spell": "Spell Hit",
        "parry": "Parry",
        "dodge": "Dodge",
        "block": "Block",
        "haste": "Haste",
        "max_health_pct": "Max Health %",
        "max_mana_pct": "Max Mana %",
    }

    @classmethod
    def _describe_stat_mods(cls, stat_mods):
        """Turn {'agility': 8, 'armor': -10} into '+8 Agility, -10 Armor'."""
        if not stat_mods:
            return ""
        parts = []
        for stat, value in stat_mods.items():
            label = cls.STAT_LABELS.get(stat, stat.replace("_", " ").title())
            sign = "+" if value >= 0 else ""
            parts.append(f"{sign}{value} {label}")
        return ", ".join(parts)

    def _init_status_effects(self):
        self.active_effects = []
        # Drained by CombatEngine/Ability.use() right after take_damage()
        # calls - see Character.take_damage's ON_DAMAGE_TAKEN proc-firing
        # comment for why this exists instead of take_damage() logging
        # directly (it has no combat_log handle of its own).
        self._pending_proc_messages = []

    def _effects(self):
        """Lazily create the list so old saves / partially-constructed
        objects never blow up with AttributeError."""
        if not hasattr(self, "active_effects") or self.active_effects is None:
            self.active_effects = []
        return self.active_effects

    def apply_status_effect(self, effect):
        """Add an effect, refreshing in place if one with the same id exists.

        Returns a short log line describing what happened, including the
        actual mechanical effect (e.g. "+8 Agility") rather than just the
        ability name - previously a buff/debuff's stat_mods were applied
        correctly but never surfaced anywhere, so "Cave Skitterer uses
        Skitter" told the player nothing about what Skitter actually did.
        """
        effects = self._effects()

        # MARK IT AS LANDING THIS TURN, so the end-of-turn tick that
        # immediately follows a non-instant cast does not expire it before
        # anything can read it. See the BUFF/DEBUFF branch of
        # tick_status_effects for the eighteen abilities this was silently
        # killing. Set here rather than in StatusEffect.__init__ because
        # landing on a combatant is the moment that matters - an effect
        # built and held for later should not carry the grace turn.
        effect.applied_this_turn = True

        # BECOMING IMMUNE TO CONTROL BREAKS CURRENT CONTROL. cc_immune only
        # blocked INCOMING stuns (see the check below), so a buff granting it
        # left an already-stunned character stunned - immune to the next stun
        # while still sitting out the turns of the last one, which is not what
        # any of these abilities say. Cultist's Voidborne and Dark Veil both
        # read as breaking free, and three more - Guardian's Liberation,
        # Ranger's Freedom and Templar's Testament of Will - are literally
        # "whatever is holding your ally, it stops holding them" and
        # "break an ally free of whatever is holding them in place".
        #
        # Those three were authored as effect_type "dispel" with
        # dispel_type "movement", which is NOT a DispelType member (the real
        # ones are NONE/MAGIC/CURSE/POISON/DISEASE), and
        # remove_debuff_by_dispel_type treats an unmatched school as a
        # guaranteed no-match - so all three removed nothing, ever. This
        # engine has no movement to impair; its one incapacitate mechanic is
        # is_stun, so breaking free means clearing that.
        if (effect.effect_type == EffectType.BUFF
                and (effect.stat_mods or {}).get("cc_immune", 0) > 0):
            for existing in list(effects):
                if getattr(existing, "is_stun", False):
                    effects.remove(existing)

        # cc_immune (CoA's Voidborne "stun immune", Dark Veil "stun +
        # silence immune" - stun_immune/silence_immune were originally two
        # separate stat_mods keys, merged into this one during the stat-
        # vocabulary cleanup since this engine has exactly one incapacitate
        # mechanic, is_stun, with no separate silence/root category to be
        # immune to individually - see StatusEffect's is_stun docstring).
        # Blocks the incoming incapacitate outright rather than applying it
        # and relying on is_stunned to ignore it, so the immunity is visible
        # in the combat log as a real resisted effect instead of a silent
        # no-op stun that still occupies a status-effect slot.
        if effect.effect_type == EffectType.DEBUFF and effect.is_stun:
            if self.get_status_stat_mod("cc_immune") > 0:
                return f"{self.name} is immune to {effect.name}!"

            # stun_duration_reduction_pct (Primalist's Unmovable Object,
            # Venomancer's Stubborn Exoskeleton: "reduces the duration of
            # stun effects against you by 5%/rank") - a real, talent-tree-
            # granted tank defensive stat that had never been read anywhere
            # (dead key, same failure mode as the other CoA tank-tree keys
            # fixed earlier this session). Talent-sourced only (no known
            # buff/debuff currently grants this), so get_talent_effect alone
            # - not get_status_stat_mod, which this class's trees don't use
            # for this key. Applied as a straight percentage cut to the
            # incoming stun's own duration, floored at 1 turn so a reduction
            # can shorten a stun but never fully negate it outright (that's
            # what cc_immune, checked just above, is for) - rounds down via
            # int() rather than round() so e.g. a 2-turn stun at 5% (1.9)
            # reduces to 1, not stays at 2, matching "reduces duration" being
            # a real, if small, effect even on short stuns.
            reduction_pct = self.get_talent_effect("stun_duration_reduction_pct", 0.0)
            if reduction_pct > 0 and effect.duration > 1:
                reduced = max(1, int(effect.duration * (1.0 - reduction_pct)))
                if reduced < effect.duration:
                    effect.duration = reduced
                    effect.max_duration = reduced

        stat_desc = self._describe_stat_mods(effect.stat_mods)
        suffix = f" ({stat_desc})" if stat_desc else ""

        # Exclusive-group replacement (e.g. Tinker's Rounds): applying a new
        # effect in the same group removes any other member of that group
        # first, even if effect_id differs - a single ammo-loadout slot
        # rather than the normal same-id-refreshes/different-id-stacks rule.
        # Must run BEFORE the same-id refresh check below so re-loading the
        # SAME Round still refreshes normally instead of removing-then-
        # re-adding itself.
        replaced_name = None
        if effect.exclusive_group:
            for existing in list(effects):
                if (existing.exclusive_group == effect.exclusive_group
                        and existing.effect_id != effect.effect_id):
                    replaced_name = existing.name
                    effects.remove(existing)

        for existing in effects:
            if existing.effect_id == effect.effect_id:
                existing.duration = effect.duration
                existing.max_duration = effect.max_duration
                existing.potency = effect.potency
                existing.stat_mods = effect.stat_mods
                existing.real_time_seconds = effect.real_time_seconds
                # Stacking (max_stacks > 1): re-applying the SAME effect_id
                # adds a stack instead of just refreshing duration at the
                # same strength, matching real WoW stacking debuffs
                # (Venomancer's Exposed Flesh: "...stacking 10 times" -
                # each hostile attack that procs it should make the stack
                # count go UP, not just reset the 20-second timer back to
                # a single stack's worth). Capped at existing.max_stacks
                # (itself refreshed from the incoming effect in case a
                # talent changed it, though no current content does that).
                # max_stacks=1 (the default, every effect before this
                # existed) always takes this branch but stacks stays 1,
                # so behavior is identical to before stacking existed.
                existing.max_stacks = effect.max_stacks
                if existing.max_stacks > 1:
                    existing.stacks = min(existing.max_stacks, existing.stacks + 1)
                    self._on_status_effects_changed()
                    return (f"{effect.name} stacks on {self.name} "
                            f"({existing.stacks}/{existing.max_stacks}){suffix}.")
                self._on_status_effects_changed()
                return f"{effect.name} refreshed on {self.name}{suffix}."

        effects.append(effect)
        self._on_status_effects_changed()
        if replaced_name:
            return f"{effect.name} replaces {replaced_name} on {self.name}{suffix}."
        if effect.effect_type == EffectType.BUFF:
            return f"{self.name} gains {effect.name}{suffix}."
        elif effect.effect_type == EffectType.DEBUFF:
            return f"{self.name} is afflicted by {effect.name}{suffix}!"
        return f"{self.name} is afflicted by {effect.name}!"

    def _on_status_effects_changed(self):
        """Recompute derived stats (max HP/Mana/etc) after any effect is
        applied, refreshed, or removed.

        THE ACTUAL BUG THIS FIXES: a stamina buff like Power Word:
        Fortitude was supposed to raise max HP through the SAME bonus pool
        gear uses (see _recalculate_derived_stats's stat_mods loop) - and
        that plumbing was correct - but nothing ever actually CALLED
        _recalculate_derived_stats() when a buff was applied or expired.
        _recalculate_derived_stats already had a comment claiming this
        hook existed ("Recalc is re-triggered whenever an effect is
        applied or expires (see _on_status_effects_changed)") but the
        method itself was never written. Max HP only got recomputed on
        level-up/gear-change, so it silently went stale the moment a
        stamina buff landed or fell off mid-session - producing exactly
        the "current HP exceeds max HP" displays users found in the party
        screen and combat target picker (e.g. a Shaman showing 364/204
        after Fortitude wore off: current_health was legitimately raised
        while the buff was active, but max never followed it back down).

        Monster shares this mixin and has no _recalculate_derived_stats
        (its stats are template-driven, not gear/stamina-derived), so this
        is a no-op there rather than an error.
        """
        if hasattr(self, "_recalculate_derived_stats"):
            self._recalculate_derived_stats()

    def has_status_effect(self, effect_id):
        return any(e.effect_id == effect_id for e in self._effects())

    @property
    def is_stunned(self):
        """True while any active DEBUFF with is_stun=True is on this
        combatant - derived from live status effects (same pattern as
        current_mechsuit below), never a plain attribute set/cleared by
        hand, so it can't go stale if a stun expires or gets dispelled
        through a path that forgot to flip a separate bool.

        Checked by TurnMeter.update() to withhold turn-meter
        accumulation entirely while stunned, so a stunned combatant is
        genuinely skipped rather than getting a turn that does nothing -
        see combat/turn_meter.py."""
        return any(getattr(e, "is_stun", False) for e in self._effects())

    @property
    def current_mechsuit(self):
        """Real Tinker Mechsuit state - True while the real screenshot-
        confirmed timed transform buff ("tinker_mechsuit_form") is active.
        Kyle: "we can do it as a kind of like metamorphosis style" for
        Mechsuit: Laser Beam/Combustion (both real screenshots say "Shares
        a cooldown with other Mechsuit abilities"), gated by requires_form
        =["mechsuit"] in their JSON (see Ability.is_form_ready).

        A DERIVED property reading has_status_effect, not a plain bool
        attribute set/cleared by hand at apply/expire time - this is
        deliberate: current_form/current_stance are set imperatively
        because they're truly persistent state with no natural expiry to
        hook into, but Mechsuit already has a perfect real signal (the
        StatusEffect's own is_expired()/tick_status_effects lifecycle)
        that a plain attribute could only ever shadow and risk drifting
        out of sync with (e.g. if a future dispel or clear_status_effects
        call removed the buff through a path that forgot to also flip a
        separate bool). Deriving it means it is definitionally always
        correct - it can't be checked while stale.
        """
        return self.has_status_effect("tinker_mechsuit_form")

    def has_dispellable_effect(self, dispel_type):
        """True if this combatant has at least one active effect tagged
        with the given DispelType, regardless of whether it's a
        BUFF/HOT or a DEBUFF/DOT (see dispel_effect for why both
        directions matter - Devour Magic-style "purge a buff off an
        enemy" is just as real as Cleanse Spirit-style "remove a curse
        from an ally"). Used by cleanse/dispel abilities to check
        castability before spending resources on a target with nothing
        to remove."""
        return any(e.dispel_type == dispel_type for e in self._effects())

    def dispel_effect(self, dispel_type):
        """Remove the first active effect matching the given DispelType
        (e.g. DispelType.CURSE), regardless of whether it's harmful or
        beneficial. Real WoW dispels work both directions depending on
        who you target - Devour Magic purges a beneficial Magic buff off
        an ENEMY, while Cleanse Spirit removes a harmful Curse DEBUFF off
        an ALLY. Both are "remove one matching effect," just aimed at
        different targets - this method doesn't need to know which
        direction it's being used for, only find and remove a match.

        Originally restricted to EffectType.DEBUFF/DOT only, which meant
        an ability like Devour Magic (purge a beneficial buff from an
        enemy) could never find anything to remove even when the enemy
        genuinely had a dispellable buff active - confirmed by testing
        Felhunter's Devour Magic against a tagged enemy buff and getting
        "nothing to dispel" when there plainly was.

        Real WoW dispels remove one matching effect per cast, not all of
        them - matched here (only the first hit is removed).

        Returns the removed StatusEffect, or None if nothing matched (the
        caller should treat None as "nothing to dispel" and can refund the
        cast the same way Swiftmend's consumes_hot path does for a missing
        HoT - see Ability._apply_effect's heal branch).

        dispel_type may be a single DispelType value OR a tuple/list of
        them (real Paladin Cleanse: "Poison, Disease, or Magic" in one
        cast, not three separate spells) - matches the FIRST active effect
        whose dispel_type is any of the given ones, same single-removal-
        per-cast rule either way.

        dispel_type=None (DispelType.NONE, "an ability authored with no
        real dispel type configured") is a GUARANTEED no-match, never a
        wildcard - THE ACTUAL BUG THIS FIXES: the naive `in (dispel_type,)`
        version treated an ability's own missing dispel_type as "remove
        anything tagged None", and almost every ordinary combat debuff
        defaults to dispel_type=None too (see StatusEffect.__init__) -
        confirmed via a real cast: Elune's Purification (authored with no
        dispel_type) against a target carrying both an ordinary Haste
        debuff AND a real tagged Poison effect incorrectly stripped the
        ordinary Haste debuff and left the actual Poison untouched. A
        cleanse/dispel ability with no configured dispel_type now finds
        nothing, full stop, which is the correct "not wired up yet"
        failure mode instead of a silent wrong-target removal.
        """
        if dispel_type is None:
            return None
        wanted = dispel_type if isinstance(dispel_type, (tuple, list)) else (dispel_type,)
        effects = self._effects()
        for effect in effects:
            if effect.dispel_type is not None and effect.dispel_type in wanted:
                effects.remove(effect)
                self._on_status_effects_changed()
                return effect
        return None

    def get_status_stat_mod(self, stat_name):
        """Sum all active buff/debuff modifiers for a given stat.

        Multiplies by `stacks` for a stacking effect (max_stacks > 1) -
        stat_mods on a stacking effect are authored PER STACK (same
        per-rank convention a talent's effects dict already uses), so 4
        stacks of Exposed Flesh's "+3% physical damage taken" means +12%,
        not +3% regardless of stack count. Non-stacking effects always
        have stacks == 1, so this multiply is a no-op for every effect
        authored before stacking existed.
        """
        total = 0
        for e in self._effects():
            if e.effect_type in (EffectType.BUFF, EffectType.DEBUFF):
                stack_mult = getattr(e, "stacks", 1)
                total += e.stat_mods.get(stat_name, 0) * stack_mult
        return total

    def tick_status_effects(self):
        """Advance DOT/HOT/turn-based-BUFF/DEBUFF effects by one turn.
        Returns a list of log messages.

        Called from CombatEngine._end_turn() for the combatant whose turn
        just ended (NOT for both combatants every turn). Damage/healing is
        applied BEFORE the duration decrements, so an N-turn effect ticks
        exactly N times.

        BUFF/DEBUFF effects only decrement here when they're turn-based
        (real_time_seconds is None - a "combat" scope buff_scope, e.g. a
        monster's Frenzy or a short player cooldown like Ice Barrier).
        "raid" scope buffs (Fortitude, Mark of the Wild, ...) have a real
        real_time_seconds value and are left alone here - they only run
        down via tick_seconds(), so a 30-minute buff cast before a 3-turn
        fight doesn't lose 3 turns of its real-world duration just because
        combat happened.

        THREAT GAP (Shaman Tank / Earthen Guardian, Phase 6): DoT/HoT ticks
        here do NOT generate threat. This method runs on the TARGET
        (self.take_damage/self.heal) with no reference to who originally
        cast the effect or which CombatEngine/enemy to credit - status
        effects only store potency/duration/school, not a caster or engine
        handle. Every other damage/heal path (Ability._apply_effect,
        called with caster+engine both in scope) DOES generate threat - see
        CombatEngine.gain_threat and Ability._last_threat_events. None of
        the initial Shaman Tank talent kit depends on DoT/HoT threat, so
        this is a documented gap rather than a blocker; closing it would
        mean threading a (caster, combat_engine) reference through every
        StatusEffect, which is a bigger change than this pass needs.
        """
        messages = []
        for effect in list(self._effects()):
            if effect.proc_icd_remaining > 0:
                effect.proc_icd_remaining -= 1
            if effect.effect_type == EffectType.DOT:
                dealt = self.take_damage(effect.tick_potency(), effect.damage_school)
                messages.append(f"{self.name} suffers {dealt} damage from {effect.name}.")
                effect.duration -= 1
                if effect.is_expired():
                    self._effects().remove(effect)
                    messages.append(f"{effect.name} fades from {self.name}.")
            elif effect.effect_type == EffectType.HOT:
                healed = effect.tick_potency()
                self.heal(healed)
                messages.append(f"{self.name} is healed {healed} by {effect.name}.")
                effect.duration -= 1
                if effect.is_expired():
                    self._effects().remove(effect)
                    messages.append(f"{effect.name} fades from {self.name}.")
            elif effect.effect_type in (EffectType.BUFF, EffectType.DEBUFF):
                if effect.real_time_seconds is not None:
                    continue  # "raid" scope - only tick_seconds() touches this
                # DON'T TICK A BUFF ON THE TURN IT WAS CAST. Eighteen
                # abilities across six classes did nothing whatsoever
                # because of this, and all of them looked fine in the data.
                #
                # CombatEngine.execute_ability ends the actor's turn after
                # any non-instant cast, and _end_turn calls this method on
                # that same actor. So a duration-1 combat-scope self-buff
                # was applied and then decremented to 0 by the very turn
                # end that its own cast triggered - it was gone before the
                # player could take another action, and before anything
                # could read it. Cast directly through Ability.use the buff
                # is there with its stat_mods live; cast through the engine
                # the effect list is empty one line later.
                #
                # That hit every one of Runemaster's five Palm Sigils (its
                # whole school-choosing mechanic), Starcaller's Lunar
                # Eclipse, Sun Cleric's Dawn, Stormbringer's Charge and
                # Cultist's Satiate among others - and these are precisely
                # the abilities authored to empower the NEXT cast, so
                # expiring at the end of the casting turn makes them
                # literally inert. Their _source notes say so outright:
                # "the real mechanic empowers the next 'Lunar Phase' spell
                # cast ... modeled as a short self-buff window instead".
                # The window was one turn and the turn was already over.
                #
                # Scoped to BUFF and DEBUFF deliberately. DoT and HoT above
                # are SUPPOSED to resolve on the turn they land - this
                # method's own docstring says "damage/healing is applied
                # BEFORE the duration decrements, so an N-turn effect ticks
                # exactly N times" - so skipping their first tick would
                # quietly change every DoT in the game.
                if getattr(effect, "applied_this_turn", False):
                    effect.applied_this_turn = False
                    continue
                effect.duration -= 1
                if effect.is_expired():
                    self._effects().remove(effect)
                    messages.append(f"{effect.name} fades from {self.name}.")
                    # A buff/debuff carrying stat_mods (e.g. Frenzy's
                    # +attack_power) just left the bonus pool
                    # _recalculate_derived_stats() folds effects into -
                    # recompute now or derived stats (including max HP for
                    # anything with a stamina mod) stay stale until the
                    # next unrelated recalc. See _on_status_effects_changed.
                    self._on_status_effects_changed()
        return messages

    def fire_proc_trigger(self, trigger, context=None, engine=None):
        """React to a real combat event on behalf of every active effect
        carrying a matching `proc`. Called from the real points those
        events already resolve (Ability._apply_effect for casts/damage/
        heals, Character.take_damage for damage taken, CombatEngine for
        kills) - see ProcTrigger's docstring for the exact call sites.

        context: dict with event data. "amount" (the real damage/heal
        number just dealt) is what bonus_pct reads to add real extra
        damage to the SAME hit - WoW-style "instant" procs, not a phantom
        follow-up attack. "target" (optional) is who the triggering cast
        hit, used as the default target for apply_effect payloads that
        don't specify their own. "is_crit" (optional bool) gates ON_CRIT
        matching.

        engine: the live CombatEngine, only needed so grant_resource/
        apply_effect payloads that log or generate threat can do so
        correctly. None is safe for anything running outside combat
        (e.g. an out-of-combat cast_panel heal) - those payloads just
        skip threat generation, exactly like every other out-of-combat
        cast already does.

        Returns a list of log message strings for whatever fired, exactly
        like tick_status_effects() - callers append these to combat_log.

        Each effect's own proc_icd_remaining gates repeat-fires: a proc
        that just fired sets its ICD from proc["icd"] (turns) and won't
        re-check its chance roll again until that many of the CARRIER's
        own turns have ended (decremented in tick_status_effects, same
        place duration already ticks) - this is why an effect with icd=1
        can't proc twice in the same turn from two different triggers
        (e.g. ON_DAMAGE_CAST then ON_CRIT off the same hit), matching how
        real WoW proc ICDs work.
        """
        context = context or {}
        amount = context.get("amount", 0)
        target = context.get("target")
        is_crit = bool(context.get("is_crit", False))
        ability_id = context.get("ability_id")
        messages = []

        # Re-entrancy guard: extra_attack re-invokes Ability.use(), which
        # itself calls fire_proc_trigger() again on the SAME caster for
        # that swing. Without this, an extra_attack proc with icd=0 would
        # trigger its own extra attack, which triggers another, forever.
        # Real WoW doesn't let Windfury proc off its own bonus swing
        # either - the bonus attack is explicitly excluded from
        # re-triggering itself - so this isn't a simplification, it's
        # matching the real mechanic. Sets a flag for the duration of this
        # call only; the extra_attack branch below checks it before
        # invoking basic_attack.use() and the recursive call sees it set.
        if getattr(self, "_proc_reentry_guard", False):
            return messages
        self._proc_reentry_guard = True
        try:
            return self._fire_proc_trigger_inner(trigger, amount, target, is_crit, engine, ability_id)
        finally:
            self._proc_reentry_guard = False

    def _fire_proc_trigger_inner(self, trigger, amount, target, is_crit, engine, ability_id=None):
        messages = []

        # ON_CRIT only matters alongside a real hit; if this event wasn't
        # actually a crit, effects listening for ON_CRIT specifically have
        # nothing to do, and effects listening for the underlying damage/
        # heal trigger should still fire normally regardless of crit status
        # (crit is additive information about the SAME event, not a
        # separate one) - so ON_CRIT is only ever passed in as `trigger`
        # itself when the caller explicitly fires it as its own event
        # (see Ability._apply_effect), never inferred here.

        for effect in list(self._effects()):
            proc = getattr(effect, "proc", None)
            if not proc:
                continue

            proc_trigger = proc.get("trigger")
            matches = (
                proc_trigger == trigger
                or (proc_trigger == ProcTrigger.ON_DAMAGE_OR_HEAL_CAST
                    and trigger in (ProcTrigger.ON_DAMAGE_CAST, ProcTrigger.ON_HEAL_CAST))
            )
            if not matches:
                continue

            # ability_filter: optional list of ability_ids this proc is
            # restricted to (Primalist's Mountain Avatar: "Damage dealt by
            # Geode Barrage or Earthquake has a 5% chance..." - a real WoW
            # proc tied to two SPECIFIC abilities, not "any damage you
            # deal," unlike every other ON_DAMAGE_CAST proc in this engine
            # so far which fires off any qualifying cast). None/absent
            # (the default) means unrestricted, so every proc authored
            # before this field existed keeps matching exactly as before.
            ability_filter = proc.get("ability_filter")
            if ability_filter and ability_id not in ability_filter:
                continue

            # require_form: optional shapeshift-form id this proc only
            # works in (Venomancer's Spider Lord talent: "While in Beetle
            # Form, generate 2 additional Rage whenever you deal damage" -
            # a real WoW mechanic gated on the carrier's CURRENT form, not
            # always-on just because the talent point is spent). Checked
            # against self.current_form (set by Character.set_form, see
            # combat/forms.py) - None/absent on an effect means
            # unrestricted, same backward-compatible default as
            # ability_filter above.
            # form_matches also accepts a LIST of form ids, so a proc can be
            # gated on Bear OR Dire Bear - see entities/talent_node.py for
            # why a single-string gate is a trap for those two. Imported
            # locally, like the ResourceType import below, to keep this
            # module free of module-level engine imports.
            from entities.talent_node import form_matches
            if not form_matches(proc.get("require_form"),
                                getattr(self, "current_form", None)):
                continue

            # require_mechsuit: like require_form above, but gated on the
            # Tinker's Mechsuit instead of a shapeshift form (Build:
            # Scrapmaw: "While your Mechsuit is active, your basic
            # attacks have a 10% chance to..."). Mechsuit is deliberately
            # NOT tracked via current_form (see StatusEffectMixin.
            # current_mechsuit's docstring - it's a timed buff derived
            # from a real StatusEffect, not persistent imperative state
            # like a shapeshift), so it needs its own gate rather than
            # reusing require_form against the wrong field. None/absent
            # is unrestricted, same default as every other proc gate.
            if proc.get("require_mechsuit") and not getattr(self, "current_mechsuit", False):
                continue

            if effect.proc_icd_remaining > 0:
                continue

            chance = proc.get("chance", 100)
            if chance < 100:
                import random
                if random.uniform(0, 100) > chance:
                    continue

            fired_something = False

            # heal_flat: a fixed-amount heal on the CARRIER, independent
            # of the triggering event's amount - Earth Shield's real
            # mechanic (heals for a flat number whenever the target takes
            # damage, NOT a percentage of the hit taken - unlike bonus_pct
            # below, which scales off the triggering amount). Distinct
            # payload from bonus_pct because "flat regardless of hit size"
            # and "percentage of hit size" are genuinely different proc
            # shapes in real WoW (Earth Shield vs. e.g. a life-steal proc).
            heal_flat = proc.get("heal_flat")
            if heal_flat and hasattr(self, "heal"):
                self.heal(heal_flat)
                messages.append(f"{effect.name} heals {self.name} for {heal_flat}!")
                fired_something = True

            # damage_flat: the mirror of heal_flat - a fixed amount dealt back
            # to whoever triggered this, independent of the triggering hit's
            # size. Retaliation shapes: Guardian's Retaliation ("Successful
            # blocks now deal damage to the attacker"), Moon Guard's Moonflares
            # ("Avoiding melee attacks will call down a Moonflare at the
            # attacker"), Gladiator's Upper Hand.
            #
            # THIS KEY WAS AUTHORED ON SIX NODES AND READ BY NOTHING. Grepping
            # the engine for it returned no hits outside tools/ - so every
            # retaliation talent in the game dealt zero, including Guardian's,
            # which shipped today. The validator accepted it because its proc
            # payload check derives the valid set from the AUTHORED DATA, which
            # makes it circular: it approves any payload simply because someone
            # wrote it. That check now reads this file instead.
            #
            # Uses `target` - the attacker, threaded through take_damage and the
            # avoidance helper - rather than `engine`, so it works from
            # Character.take_damage, which owns no engine handle. No target (a
            # caller that did not pass the attacker) means no retaliation,
            # exactly like the other retaliation payloads.
            damage_flat = proc.get("damage_flat")
            if damage_flat and target is not None and hasattr(target, "take_damage"):
                school = proc.get("school", effect.damage_school or "physical")
                target.take_damage(int(damage_flat), school)
                messages.append(
                    f"{effect.name} deals {int(damage_flat)} {school} damage "
                    f"to {target.name}!")
                fired_something = True

            # ── payloads added for the unlock_mechanic pass ───────────────
            #
            # 38 talents across six classes were authored as
            # `unlock_mechanic: "<some_name>"`, a key no engine code ever
            # read, so all 38 did nothing. Read together they are not 38
            # bespoke systems - they are a handful of mechanics wearing
            # different names, and these four payloads cover most of them.
            # Kyle: "I'd rather build the unique things that make these
            # classes different."

            # reset_cooldown: knock turns off a named ability, or reset it
            # outright. The single most-requested mechanic in that set -
            # Cultist's Dark Revelation, Primalist's Aftershock and Mountain
            # Giant, Sun Cleric's Solar Concord, Pendant of the Sun and It's
            # Always Sunny all describe exactly this. `turns` omitted means a
            # full reset; a list of ability ids is accepted so one proc can
            # refresh a whole kit.
            reset = proc.get("reset_cooldown")
            if reset and hasattr(self, "ability_book"):
                spec = reset if isinstance(reset, dict) else {"ability": reset}
                ids = spec.get("ability") or spec.get("abilities") or []
                if isinstance(ids, str):
                    ids = [ids]
                turns = spec.get("turns")
                hit = []
                for _ab in self.ability_book.get_all_abilities():
                    if _ab.ability_id not in ids:
                        continue
                    if not getattr(_ab, "turns_remaining", 0):
                        continue
                    _ab.turns_remaining = (0 if turns is None
                                           else max(0, _ab.turns_remaining - turns))
                    hit.append(_ab.name)
                if hit:
                    messages.append(
                        f"{effect.name} refreshes {', '.join(hit)} for {self.name}!")
                    fired_something = True

            # leech_pct: heal for a fraction of the triggering amount, which
            # is what every "damage done also heals you" mechanic in that set
            # wants (Cultist's Blade of Yogg-Saron, Sun Cleric's Adjudicator).
            # With "smart": true it heals the worst-off ally instead of the
            # carrier, which is how Blade of Yogg-Saron is actually worded.
            leech = proc.get("leech_pct")
            if leech and amount:
                spec = leech if isinstance(leech, dict) else {"pct": leech}
                healed = max(1, int(amount * spec.get("pct", 0)))
                recipient = self
                if spec.get("smart"):
                    allies = getattr(engine, "allies", None) if engine is not None else None
                    pool = [a for a in (allies or [self])
                            if a is not None and getattr(a, "is_alive", lambda: True)()] or [self]
                    recipient = min(pool, key=lambda a: getattr(a, "current_health", 0)
                                    / max(1, getattr(a, "health", 1)))
                if hasattr(recipient, "heal"):
                    recipient.heal(healed)
                    messages.append(
                        f"{effect.name} drains {healed} health to {recipient.name}!")
                    fired_something = True

            # shield_pct: an absorb shield sized from the triggering amount,
            # rather than from max health as absorb_pct_max_health does. Sun
            # Cleric's The Chosen ("Illumination shields you for a percentage
            # of the amount healed") is the shape this exists for.
            shield = proc.get("shield_pct")
            if shield and amount and hasattr(self, "apply_status_effect"):
                spec = shield if isinstance(shield, dict) else {"pct": shield}
                size = max(1, int(amount * spec.get("pct", 0)))
                self.apply_status_effect(StatusEffect(
                    effect_id=spec.get("effect_id", f"{effect.effect_id}_shield"),
                    name=spec.get("name", effect.name),
                    effect_type=EffectType.BUFF,
                    duration=spec.get("duration", 3),
                    absorb=size, real_time_seconds=None,
                ))
                messages.append(f"{effect.name} shields {self.name} for {size}!")
                fired_something = True

            # splash_heal: spread a fraction of the triggering heal to the
            # OTHER living allies - Sun Cleric's Heat Wave and Sunlight, which
            # smart_heal cannot express because it only ever picks one target.
            splash = proc.get("splash_heal")
            if splash and amount and engine is not None:
                spec = splash if isinstance(splash, dict) else {"pct": splash}
                share = max(1, int(amount * spec.get("pct", 0)))
                pool = [a for a in (getattr(engine, "allies", None) or [])
                        if a is not None and a is not self
                        and getattr(a, "is_alive", lambda: True)()]
                pool = pool[:spec.get("max_targets", 3)]
                for ally in pool:
                    if hasattr(ally, "heal"):
                        ally.heal(share)
                if pool:
                    messages.append(
                        f"{effect.name} splashes {share} healing to "
                        f"{', '.join(a.name for a in pool)}!")
                    fired_something = True

            # splash_damage: the mirror of splash_heal - spread a fraction of
            # the triggering hit to the OTHER living enemies. Runemaster's
            # Weapon Engraving: Earth ("your direct damage has a chance to
            # deal Nature damage to enemies within 8 yds of your target") and
            # any other "damage splashes to nearby enemies" design.
            #
            # This engine has no AoE radius (see the palette doc), so "within
            # 8 yds" becomes "the other enemies in the fight", capped by
            # max_targets - the same translation splash_heal already makes for
            # allies. Excludes `target`, the enemy that took the original hit,
            # so the primary is never double-dipped.
            #
            # `school` defaults to the carrying effect's own damage_school
            # rather than physical, so an Engraving's splash lands as the
            # element it is named after and is reduced by the right
            # resistance - a Nature splash off a Nature rune.
            splash_dmg = proc.get("splash_damage")
            if splash_dmg and amount and engine is not None:
                spec = (splash_dmg if isinstance(splash_dmg, dict)
                        else {"pct": splash_dmg})
                share = max(1, int(amount * spec.get("pct", 0)))
                school = spec.get("school", effect.damage_school)
                pool = [e for e in (getattr(engine, "enemies", None) or [])
                        if e is not None and e is not target
                        and getattr(e, "is_alive", lambda: True)()]
                pool = pool[:spec.get("max_targets", 3)]
                for foe in pool:
                    if hasattr(foe, "take_damage"):
                        foe.take_damage(share, school)
                if pool:
                    messages.append(
                        f"{effect.name} splashes {share} {school} damage to "
                        f"{', '.join(f.name for f in pool)}!")
                    fired_something = True

            # grant_resource: e.g. Vow of Radiance's "+2 Solar Power".
            # Uses the same gain_resource() every builder/spender ability
            # already goes through, so caps (see Character.
            # SECONDARY_RESOURCE_MAX_OVERRIDE) are respected automatically.
            grant = proc.get("grant_resource")
            if grant and hasattr(self, "gain_resource"):
                resource = grant.get("resource")
                grant_amt = grant.get("amount", 0)
                # scale_talent_key (optional): a get_talent_effect key
                # whose value is a PERCENTAGE bonus multiplier on this
                # specific grant (Venomancer's Adrenal Carapace: "+10%/rank
                # Rage generated from Exposed Flesh" - a talent that boosts
                # a DIFFERENT talent's own resource grant, not a flat
                # amount increase, so it can't be folded into Exposed
                # Flesh's own `amount` field). Read live every time this
                # fires (not baked into the synthetic effect once), so
                # spending/unspending Adrenal Carapace ranks takes effect
                # on the very next proc with no re-sync needed. None/absent
                # (the default) leaves grant_amt untouched, exactly as
                # before this field existed.
                scale_key = grant.get("scale_talent_key")
                if scale_key and hasattr(self, "get_talent_effect"):
                    grant_amt = grant_amt * (1.0 + self.get_talent_effect(scale_key, 0.0))
                grant_amt = int(round(grant_amt))
                if resource and grant_amt > 0:
                    gained = self.gain_resource(resource, grant_amt)
                    if gained:
                        messages.append(
                            f"{self.name} gains {gained} {resource.replace('_', ' ').title()} from {effect.name}!")
                        fired_something = True

            # bonus_pct: real WoW-style "instant" proc - adds extra damage
            # or healing to the SAME hit that triggered it, applied
            # directly here via take_damage/heal on whichever side this
            # trigger concerns, rather than queuing a second attack. Only
            # meaningful when the triggering event actually had a real
            # amount attached (a pure self-buff ON_CAST has amount=0 and
            # nothing to scale off).
            bonus_pct = proc.get("bonus_pct")
            if bonus_pct and amount > 0:
                bonus_amt = max(1, int(amount * bonus_pct))
                if trigger in (ProcTrigger.ON_HEAL_CAST,) and self is target:
                    # Bonus healing lands on whoever the triggering heal
                    # actually healed (the carrier, since this fired via
                    # self.fire_proc_trigger on the recipient's own effect).
                    self.heal(bonus_amt)
                    messages.append(f"{effect.name} adds {bonus_amt} bonus healing to {self.name}!")
                    fired_something = True
                elif target is not None and hasattr(target, "take_damage"):
                    dealt = target.take_damage(bonus_amt, effect.damage_school)
                    messages.append(f"{effect.name} adds {dealt} bonus damage to {target.name}!")
                    fired_something = True
                    if engine is not None and hasattr(engine, "gain_threat"):
                        engine.gain_threat(self, target, dealt)

            # smart_heal: proc heals the single neediest living party
            # member (by HP%), same "always finds the worst-off ally"
            # logic Cryotherapist's Ability._lowest_hp_ally already uses -
            # ported here rather than imported since that's a method on
            # Ability, not reachable from a StatusEffect proc firing on
            # the Character side. Venomancer's Rejuvenating Venom is the
            # first real use: "your casts have a chance to heal a random
            # ally" is modeled as a smart/lowest-HP heal instead of a
            # true random pick (Kyle, Oct 2026: wants this to work like
            # Cryotherapist's smart heals, which is also just a more
            # useful version of "heals someone nearby" for actual
            # gameplay). engine.allies is the live party roster
            # (CombatEngine.allies, set from Party.members); with no
            # engine (an out-of-combat proc, or a monster with no party
            # concept) this safely falls back to healing the carrier.
            smart_heal_amt = proc.get("smart_heal")
            # smart_heal_pct: heal a PERCENTAGE OF THE TRIGGERING AMOUNT
            # rather than a flat number, for the procs whose wording is
            # proportional. Sun Cleric's Vow of Light is the case that forced
            # this - "heals the nearest ally equal to 10% of the amount", per
            # its own description and the confirmed screenshot in its _source
            # - and it was authored as a flat smart_heal of 90 on an
            # on_damage_taken trigger with chance 100 and NO internal
            # cooldown. Against the tank sim's attacker, which hits for ~120,
            # a flat 90 back on every single landed hit took Seraphim from
            # 47.5 net damage a turn to 7.8, and from 23 turns alive to 159.
            # Solo, that is an unkillable tank; 10% of the amount is 12, which
            # is what the ability actually says.
            #
            # Reads `amount`, the real damage or heal number this trigger
            # already carries for bonus_pct, so nothing new has to be plumbed.
            smart_heal_pct = proc.get("smart_heal_pct")
            if smart_heal_pct and not smart_heal_amt:
                smart_heal_amt = int((amount or 0) * smart_heal_pct / 100.0)
            if smart_heal_amt and hasattr(self, "heal"):
                candidates = [self]
                allies = getattr(engine, "allies", None) if engine is not None else None
                if allies:
                    candidates = [a for a in allies
                                  if a is not None and getattr(a, "is_alive", lambda: True)()] or [self]
                recipient = min(
                    candidates,
                    key=lambda c: getattr(c, "current_health", 0) / max(1, getattr(c, "health", 1)))
                recipient.heal(smart_heal_amt)
                messages.append(f"{effect.name} smart-heals {recipient.name} for {smart_heal_amt}!")
                fired_something = True

            # apply_effect: proc applies a fresh StatusEffect (its own
            # spec dict, same shape as any other StatusEffect kwargs) onto
            # the trigger's target, or the carrier itself if no target is
            # relevant (e.g. a self-buff proc). Lets a proc chain into a
            # real DoT/debuff/extra buff rather than only ever touching
            # resources/damage.
            # apply_effect accepts either one spec dict or a LIST of them.
            # A single proc often has to land something on the target AND
            # something on the caster off the same roll - Runemaster's Ice
            # Engraving slows the enemy and stacks Icebound Momentum on
            # itself from one 40% chance - and `on_target` is per-spec, so a
            # list is all that was missing. One dict stays exactly as it was.
            apply_spec = proc.get("apply_effect")
            for apply_spec in ([] if not apply_spec else
                               (apply_spec if isinstance(apply_spec, list)
                                else [apply_spec])):
                recipient = target if (apply_spec.get("on_target", True) and target is not None) else self
                if hasattr(recipient, "apply_status_effect"):
                    spec_kwargs = {k: v for k, v in apply_spec.items()
                                   if k not in ("on_target", "absorb_pct_max_health")}
                    # A proc's apply_effect states its duration in TURNS
                    # ("increasing your haste by 15% for 2 turns"), so it is
                    # turn-based unless the author deliberately says
                    # otherwise. Without this, real_time_seconds stayed
                    # _UNSET and StatusEffect.__init__ fell back to
                    # BUFF_DURATION_SECONDS - every proc-applied buff and
                    # debuff in the game silently lasted 30 REAL MINUTES
                    # instead of the handful of turns its tooltip promised,
                    # which made reactive talents permanent once they first
                    # fired. Pre-existing casualties included Nature's Grace,
                    # Redoubt and Blade Twisting. An author who genuinely
                    # wants a wall-clock buff can still pass
                    # real_time_seconds explicitly and it is respected.
                    spec_kwargs.setdefault("real_time_seconds", None)
                    # absorb_pct_max_health: convenience field for a shield
                    # sized relative to the RECIPIENT's own max HP rather
                    # than a flat number baked into the talent's JSON
                    # (Tinker's Reactive Plating: the real tooltip gives no
                    # fixed shield size, and a flat number would be either
                    # trivial at level 60 or overpowered at level 10 - a %
                    # of max HP scales naturally the same way every other
                    # level-scaling stat in this engine already does).
                    # Computed here, at the moment the proc actually fires,
                    # using the RECIPIENT's health (self, since this is a
                    # self-shield - on_target defaults True for most procs
                    # but Reactive Plating's is explicitly False), not
                    # baked into the static proc dict.
                    pct = apply_spec.get("absorb_pct_max_health")
                    if pct and hasattr(recipient, "health"):
                        spec_kwargs["absorb"] = max(1, int(recipient.health * pct))
                    new_effect = StatusEffect(**spec_kwargs)
                    recipient.apply_status_effect(new_effect)
                    messages.append(f"{effect.name} triggers {new_effect.name} on {recipient.name}!")
                    fired_something = True

            # extra_attack: Windfury Weapon/Totem's real mechanic - a
            # genuine SECOND independent swing against the same target,
            # not bonus damage folded into the current hit. Re-invokes the
            # caster's own basic-attack Ability (found via ability_book,
            # by the real "<class_prefix>_attack" convention every class's
            # data file uses - see combat/abilities.py's
            # _class_file_prefix), so the extra swing rolls its own real
            # hit/miss/crit/avoidance exactly like any other attack, with
            # its own combat log line - not a copy of the triggering hit's
            # number. Requires the carrier to actually have an
            # ability_book (Character does; Monster's own attack path
            # doesn't run through Ability.use() yet, so this safely no-ops
            # for monsters until that's built later).
            #
            # This proc's own "chance" field (checked at the top of this
            # loop) already gates whether we get here at all - a monster's
            # Windfury-style ability just sets a lower chance (e.g. 20 for
            # WoW's real ~20% Windfury proc rate) rather than needing a
            # second roll here.
            if proc.get("extra_attack") and target is not None and hasattr(self, "ability_book"):
                book = self.ability_book
                prefix = getattr(self, "char_class", "").lower().replace(" ", "_")
                basic_attack = book.get_ability(f"{prefix}_attack") if book else None
                if basic_attack is not None and target is not None and hasattr(target, "is_alive") and target.is_alive():
                    _ok, extra_msg = basic_attack.use(self, target, in_combat=True)
                    if _ok:
                        messages.append(f"{effect.name} triggers an extra attack! {extra_msg}")
                        fired_something = True

            # cast_ability: like extra_attack above, but for a SPECIFIC
            # named ability instead of always the caster's own basic
            # attack (Tinker's Build: Scrapmaw: "...basic attacks have a
            # 10% chance to fire an additional Scrap Shot at no Mana
            # cost" - a real secondary ability, not the basic attack
            # again). Looked up by ability_id via the carrier's own
            # ability_book (same requirement as extra_attack - safely
            # no-ops for anything without one, e.g. a monster). Always
            # cast with free=True (Ability.use's new parameter - skips
            # resource check/consume and cooldown check/set entirely),
            # matching "at no Mana cost" being the actual mechanic, not a
            # discount - a proc firing a secondary ability should never
            # be gated by that ability's own cooldown or cost just because
            # this specific cast didn't choose to pay for it.
            cast_ability_id = proc.get("cast_ability")
            if cast_ability_id and target is not None and hasattr(self, "ability_book"):
                book = self.ability_book
                cast_ability = book.get_ability(cast_ability_id) if book else None
                if cast_ability is not None and hasattr(target, "is_alive") and target.is_alive():
                    _ok, cast_msg = cast_ability.use(self, target, in_combat=True, free=True)
                    if _ok:
                        messages.append(f"{effect.name} triggers {cast_ability.name}! {cast_msg}")
                        fired_something = True

            if fired_something:
                icd = proc.get("icd", 0)
                if icd > 0:
                    effect.proc_icd_remaining = icd

        return messages

    #: Real WoW-style attunement cycle order for Runemaster (see
    #: current_attunement below). Frost -> Fire -> Arcane -> repeat, every
    #: RUNEMASTER_ATTUNEMENT_PERIOD real-world seconds - matches the
    #: class's actual identity (frontier_rpg_handoff.md: "cycles Frost/
    #: Fire/Arcane every 8s"), not a guessed simplification.
    RUNEMASTER_ATTUNEMENT_CYCLE = ("frost", "fire", "arcane")
    RUNEMASTER_ATTUNEMENT_PERIOD = 8.0

    def tick_seconds(self, dt):
        """
        Advance BUFF/DEBUFF effects by dt real-world seconds. Call this
        every frame, in combat AND in the overworld/menus, so a 30-minute
        buff counts down at the same rate no matter what screen the player
        is on. Returns a list of log messages for anything that expired.
        """
        messages = []
        for effect in list(self._effects()):
            if effect.effect_type not in (EffectType.BUFF, EffectType.DEBUFF):
                continue
            if effect.real_time_seconds is None:
                continue
            effect.real_time_seconds -= dt
            if effect.is_expired():
                self._effects().remove(effect)
                messages.append(f"{effect.name} fades from {self.name}.")
                # Same reasoning as the turn-based path above: a raid buff
                # like Fortitude expiring after its real 30 minutes must
                # drop max HP (and anything else its stat_mods touched)
                # back down immediately, or current HP can be left sitting
                # above the new, lower max until something unrelated
                # happens to trigger a recalc.
                self._on_status_effects_changed()
        self._tick_attunement(dt)
        return messages

    #: Real out-of-combat regen rates, per point of effective Spirit, per
    #: REAL SECOND (not per tile moved, and not per turn - see
    #: tick_out_of_combat_regen below). Kyle's real numbers, replacing the
    #: old flat "0.5 mana per Spirit per tile stepped" rate: that old rate
    #: only ever applied while walking (see overworld_screen.py's
    #: restore_resources_out_of_combat_step, called only inside `if
    #: moved:`) and had no HP-regen component at all. STANDING_STILL_MULT
    #: halves both rates while the player hasn't moved recently, matching
    #: Kyle's "half of that when standing still" - inverted from the old
    #: system, which required movement to regen anything at all and gave
    #: zero benefit to standing still.
    OUT_OF_COMBAT_MANA_REGEN_PER_SPIRIT = 0.1
    OUT_OF_COMBAT_HP_REGEN_PER_SPIRIT = 0.05
    STANDING_STILL_MULT = 0.5

    #: Real seconds of no movement before "standing still" regen kicks in,
    #: rather than flipping the instant a key is released - matches how
    #: real WoW's rested-state/regen distinctions work on a several-
    #: second threshold, not an instant one.
    STANDING_STILL_THRESHOLD = 3.0

    #: EATING AND DRINKING (Kyle, 2026-10-28: "food recovers hp over time and drink recovers mana").
    #: Held as {"left": seconds, "per_second": amount, "name": str} or None. Food and drink run at the
    #: same time, as they do in the game this borrows from - they fill different bars.
    #:
    #: WHY THIS IS NOT THE EXISTING "food" CONSUMABLE TYPE. That one is a STAT buff in a stat-buff slot
    #: - +6 Strength for half an hour, the Well Fed effect - and it is correct as it stands. This is the
    #: other thing food does: sit down, get the bar back, stand up. Two mechanics that share a word, so
    #: they get two consumable types ("meal" and "drink") and the UI calls them Food and Drink.
    def start_consumable_regen(self, kind, total, seconds, name=""):
        """Begin eating or drinking. kind is 'meal' or 'drink'."""
        slot = "_meal_regen" if kind == "meal" else "_drink_regen"
        setattr(self, slot, {"left": float(seconds),
                             "per_second": float(total) / max(0.1, float(seconds)),
                             "name": name})

    def consumable_regen_active(self):
        """[(kind, name, seconds_left)] for whatever is currently ticking - for the UI."""
        out = []
        for kind, slot in (("meal", "_meal_regen"), ("drink", "_drink_regen")):
            state = getattr(self, slot, None)
            if state and state["left"] > 0:
                out.append((kind, state["name"], state["left"]))
        return out

    def break_consumable_regen(self, reason="combat"):
        """Stop eating and drinking. Called when a fight starts or damage lands.

        This is the rule that makes food a RESTING item rather than a second potion: you cannot eat
        your way through a fight. Without it there is no reason to ever carry a healing potion.
        """
        self._meal_regen = None
        self._drink_regen = None

    def tick_consumable_regen(self, dt):
        """Advance eating/drinking. Returns (hp_gained, mana_gained).

        Deliberately separate from tick_out_of_combat_regen rather than folded into it: that method
        is Spirit-driven and scales with gear, and food must not. A level 1 character with no Spirit
        still gets the full value of their bread, which is the entire point of selling it to them.
        """
        hp = mana = 0.0
        meal = getattr(self, "_meal_regen", None)
        if meal and meal["left"] > 0:
            step = min(dt, meal["left"])
            meal["left"] -= step
            if self.current_health < self.health:
                hp = min(meal["per_second"] * step, self.health - self.current_health)
                self.current_health += hp
            if meal["left"] <= 0:
                self._meal_regen = None
        drink = getattr(self, "_drink_regen", None)
        if drink and drink["left"] > 0:
            step = min(dt, drink["left"])
            drink["left"] -= step
            if hasattr(self, "current_mana") and self.current_mana < getattr(self, "mana", 0):
                mana = min(drink["per_second"] * step, self.mana - self.current_mana)
                self.current_mana += mana
            if drink["left"] <= 0:
                self._drink_regen = None
        return hp, mana

    def tick_out_of_combat_regen(self, dt, is_moving):
        """Real time-based HP/Mana regen while out of combat, replacing
        the old per-tile-stepped system (see OUT_OF_COMBAT_MANA_REGEN_
        PER_SPIRIT's docstring for why). Runs unconditionally for every
        StatusEffectMixin user, same pattern as _tick_attunement - cheap
        no-op for anything with no mana pool or already at full HP.

        is_moving: real signal from the caller (overworld_screen.py
        tracks real seconds since the last tile step, NOT the raw per-
        tile movement_cooldown - that flag is tuned for tile-step
        throttling, ~100ms, which would make regen flicker between rates
        constantly during ordinary walking rather than reflecting genuine
        "standing still").

        Only regens MANA-resource classes' mana pool (mirrors the old
        step-based system - Rage/Energy have their own separate real
        out-of-combat behavior already, untouched by this) and HP for
        EVERY class (real WoW: Spirit contributes to HP regen regardless
        of your resource type, not just casters).
        """
        spirit = getattr(self, "effective_spirit", 0)
        if spirit <= 0:
            return

        mult = 1.0 if is_moving else self.STANDING_STILL_MULT

        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(getattr(self, "char_class", None), self)
        if resource == ResourceType.MANA and hasattr(self, "current_mana"):
            gain = spirit * self.OUT_OF_COMBAT_MANA_REGEN_PER_SPIRIT * mult * dt
            # mp5 (real gear suffix stat, "Mana Per 5 Seconds" - see
            # data/items/gear_suffixes.json's "of the Restorer"/"of the
            # Seer"/etc) - a flat regen source layered on top of the
            # Spirit-based formula, converted from its native "per 5
            # seconds" unit to "per second" to match this method's dt-based
            # tick. Previously stored on Character (see mp5 field) but
            # never actually consumed anywhere - gear rolling it did
            # nothing.
            mp5_bonus = getattr(self, "mp5", 0)
            if mp5_bonus:
                gain += (mp5_bonus / 5.0) * mult * dt
            self.current_mana = min(self.mana, self.current_mana + gain)

        if hasattr(self, "current_health") and hasattr(self, "health"):
            hp_gain = spirit * self.OUT_OF_COMBAT_HP_REGEN_PER_SPIRIT * mult * dt
            self.current_health = min(self.health, self.current_health + hp_gain)

    def _tick_attunement(self, dt):
        """Advance Runemaster's real Frost/Fire/Arcane attunement cycle by
        dt real-world seconds. Runs unconditionally for every
        StatusEffectMixin user (Character/Monster/Pet), same as
        tick_seconds itself - cheap for non-Runemasters since
        current_attunement simply sits unused if nothing ever reads it
        (an "attunement"-schooled ability - see DamageSchool's docstring
        for the sentinel - is the only thing that looks at this).

        current_attunement_elapsed tracks real seconds since the last
        cycle step; when it crosses RUNEMASTER_ATTUNEMENT_PERIOD, advances
        to the next school in RUNEMASTER_ATTUNEMENT_CYCLE and resets the
        counter (using modulo-style carryover, not a hard reset to 0, so
        a large dt - e.g. a slow frame, or time skipped while alt-tabbed -
        can't silently eat multiple real cycle steps).

        Lazily initializes current_attunement to the cycle's first entry
        on first tick, so a freshly-created Character always starts in a
        real, valid attunement rather than None.
        """
        if not hasattr(self, "current_attunement") or self.current_attunement is None:
            self.current_attunement = self.RUNEMASTER_ATTUNEMENT_CYCLE[0]
            self.current_attunement_elapsed = 0.0

        self.current_attunement_elapsed = getattr(self, "current_attunement_elapsed", 0.0) + dt
        period = self.RUNEMASTER_ATTUNEMENT_PERIOD
        while self.current_attunement_elapsed >= period:
            self.current_attunement_elapsed -= period
            cycle = self.RUNEMASTER_ATTUNEMENT_CYCLE
            idx = cycle.index(self.current_attunement) if self.current_attunement in cycle else 0
            self.current_attunement = cycle[(idx + 1) % len(cycle)]

    def clear_status_effects(self):
        """
        Wipe ALL effects, including buffs. Used only for hard resets (e.g.
        character death/respawn) - NOT called on ordinary combat exit any
        more, since buffs are meant to persist across fights on their own
        30-minute timer, the way WoW's Fortitude/Might do.
        """
        self.active_effects = []

    def clear_combat_effects(self):
        """
        Clear only DOT/HOT effects when combat ends. BUFF/DEBUFF effects
        are left alone - they expire on their own real-time clock via
        tick_seconds(), independent of whether a fight is happening.
        """
        self.active_effects = [
            e for e in self._effects()
            if e.effect_type not in (EffectType.DOT, EffectType.HOT)
        ]

    def get_effects_summary(self):
        """Compact list for UI display: [(name, turns_left, type), ...]"""
        return [(e.name, e.duration, e.effect_type) for e in self._effects()]
