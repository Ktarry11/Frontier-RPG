"""
Shared pet foundation - Hunter tamed beasts and Warlock summoned demons both
build on this one class. Matches this engine's core combat philosophy (see
combat/combat_engine.py's docstring: "the player controls EVERY ally,
FF-style - there is no companion AI") by giving a Pet real, player-castable
Ability objects instead of an AI-driven MonsterAbility kit like wild
monsters use. A pet takes its own turn on the shared turn meter, same as
any party member, and the player chooses its action every time.

WHY NOT REUSE Monster DIRECTLY: Monster is built around MonsterAbility
(fixed AI kits, no player target selection, no hotbar/UI integration) and
carries fields (exp_reward, is_boss) that make no sense for a pet. Pet
shares Monster's approach to stat scaling and StatusEffectMixin, but uses
the same real Ability class Characters use, so it can sit on a hotbar and
be cast through the exact same execute_ability() path.

WHY NOT PUT A PET IN party.members: Party is explicitly capped at 5
(entities/party.py, MAX_PARTY_SIZE) and members are recruited, spec-locked
Characters with their own gear/talent progression - a pet is neither of
those things, and stuffing it into that list would either eat one of the
player's 5 human-companion slots or require special-casing every place
that assumes party.members.length <= 5 means "at most 5 REAL characters".
Pets live in CombatEngine.pets instead (see the combat_engine.py change
alongside this file), a separate list that combines with party.members for
turn order and targeting but never counts against the party cap.
"""
from combat.status_effects import StatusEffectMixin
from combat.abilities import AbilityBook, ResourceType


class Pet(StatusEffectMixin):
    """A persistent, player-controlled combat companion belonging to one
    Character (the "owner"). Only one pet can be active per owner at a
    time - summoning/taming a new one replaces the old (see
    Character.active_pet, a single slot, not a list)."""

    def __init__(self, name, template_id, owner, level=None):
        """
        name: display name (a Hunter's tamed beast keeps the monster's own
            name by default, e.g. "Elder Springpaw"; a Warlock's demon uses
            its family name, e.g. "Imp").
        template_id: key into PET_TEMPLATES (see pet_templates.py) -
            determines base stats, resource type, and starting abilities.
        owner: the Character this pet belongs to. Used for level syncing
            (a pet's level tracks its owner's, matching real WoW) and nothing
            else - a Pet does not reach into the owner's talents/gear.
        level: overrides owner.level if given (a freshly tamed low-level
            beast before it "levels up to match" - real WoW does this
            instantly on tame, so this parameter exists mainly for testing
            and is expected to equal owner.level in normal play).
        """
        self._init_status_effects()
        self.name = name
        self.template_id = template_id
        self.owner = owner
        self.is_pet = True  # lets UI/combat code distinguish from Character/Monster at a glance

        from combat.pet_templates import get_pet_template
        template = get_pet_template(template_id)
        if template is None:
            from combat.pet_templates import PET_TEMPLATES
            raise KeyError(
                f"Unknown pet template '{template_id}' for '{name}'. "
                f"Known: {sorted(PET_TEMPLATES)}")
        self.template = template

        self.level = level if level is not None else getattr(owner, "level", 1)
        self._apply_template_stats()

        # A synthetic "class" so get_class_resource() (see combat/abilities.py)
        # resolves this pet's resource type correctly without needing a
        # real player class to exist. CLASS_RESOURCE_MAP has no "Pet" entry
        # by design (see get_class_resource's own default-to-Mana fallback)
        # - self.resource_type below is read directly by Ability instead,
        # this attribute exists only so any code doing getattr(x,
        # "char_class", ...) degrades gracefully rather than crashing.
        self.char_class = "Pet"

        self.ability_book = AbilityBook()
        for entry in template.get("abilities", []):
            from combat.abilities import _ability_from_data
            self.ability_book.add_ability(_ability_from_data(entry))
        for ability in self.ability_book.get_all_abilities():
            ability.refresh_rank_for_level(self.level)
        self._scale_ability_power()

        self.hotbar = [None] * 10
        self._autofill_hotbar()

        # Turn meter state - same attributes TurnMeter expects on any
        # combatant (see combat/turn_meter.py's hasattr(char, "agility")/
        # hasattr(char, "speed") branch). Pets use the "speed" path since
        # they have no Agility stat of their own to derive it from.
        self.turn_meter = 0.0
        self.turn_speed = template.get("speed", 1.0)

        # Row placement mirrors Monster/Character convention (see
        # entities/party.py's row damage multipliers) - pets default to
        # front row like most Hunter/Warlock combat pets actually tank in
        # real WoW, but nothing stops a caster-type pet (Warlock's
        # Voidwalker vs a ranged Felhunter) being placed differently later.
        self.row = "front"

    def _apply_template_stats(self):
        """(Re)compute HP/resource/combat stats for self.level from the
        template's base values + per-level scaling. Called at construction
        and whenever the pet should re-sync to a new owner level (e.g. the
        owner leveled up between fights)."""
        t = self.template
        level_mult = 1.0 + (self.level - 1) * 0.15  # same curve as Monster

        # A PET IS A SHARE OF ITS OWNER, NOT A MONSTER THAT FOLLOWS YOU.
        #
        # These stats used to be `template_base * level_mult` and nothing
        # else, which is the Monster curve - so a pet's power was decided
        # entirely by which template it was and what level the owner had
        # reached, and the owner's own gear did not touch it. Measured on
        # geared characters (tools/sim_class_balance.dress) that produced:
        #
        #   level 60 Hunter   1252 hp / 186 ap
        #     wolf            1379 hp / 216 ap   - beat its owner at both
        #   level 60 Warrior  1796 hp
        #     mechano_bear    2561 hp            - more than a plate tank
        #   level 60 Warlock  1100 hp /  83 sp
        #     voidwalker      2167 hp / 256 ap   - the pet WAS the class
        #
        # Two things were wrong with that and they pull in opposite
        # directions. The pet outgrew the player, AND gearing the player
        # did nothing for the pet - so the one fantasy a pet class has
        # ("my beast gets better as I do") was the part that didn't work.
        #
        # So each template now declares what SHARE of its owner it is, and
        # the template's old absolute numbers are what those shares are
        # derived from (see pet_templates.shares_for), which keeps every
        # pet's relative identity - a mechano_bear is still the tanky one,
        # a war_falcon is still glass - while tying the whole roster to
        # whoever is holding the leash.
        #
        # The old curve is kept ONLY for an owner with no usable stats -
        # a pet built in a test, or before recalculate_stats has run. It
        # is not blended in: a curve floor that keeps climbing at 15% a
        # level overtakes the share and reinstates exactly the bug this
        # replaces (measured: it put a level-60 voidwalker at 2.04x its
        # Warlock's offensive stat, which is where it already was).
        from combat.pet_templates import shares_for
        hp_share, power_share, armor_share = shares_for(t)

        owner = getattr(self, "owner", None)
        o_hp = float(getattr(owner, "health", 0) or 0)
        # Character carries `.armor`; Monster-shaped code carries
        # `.base_armor`. Both spellings have to work here.
        o_arm = float(getattr(owner, "base_armor", 0)
                      or getattr(owner, "armor", 0) or 0)
        # The owner's MAIN offensive stat, whichever it is. A Warlock has
        # 18 attack power and 83 spell power at 60; scaling his voidwalker
        # off attack power would have made the demon useless the moment it
        # stopped being a free-standing monster.
        o_pow = max(float(getattr(owner, "attack_power", 0) or 0),
                    float(getattr(owner, "spell_power", 0) or 0))

        if o_hp <= 0:
            self.max_health = int(t["base_hp"] * level_mult)
            self.base_armor = int(t.get("base_armor", 0) * level_mult)
            self.attack_power = int(t.get("base_attack", 0) * level_mult)
            self.spell_power = int(t.get("base_spell_power", 0) * level_mult)
        else:
            self.max_health = max(1, int(o_hp * hp_share))
            self.base_armor = int(o_arm * armor_share)
            # Melee pets put the share into attack power, casters into
            # spell power, decided by which the template was authored
            # around. The other stat is left at a token value so a caster
            # pet's auto-attack is not literally zero.
            power = max(1, int(o_pow * power_share))
            if t.get("base_spell_power", 0) > t.get("base_attack", 0):
                self.spell_power = power
                self.attack_power = max(1, int(power * 0.25))
            else:
                self.attack_power = power
                self.spell_power = max(0, int(power * 0.25)) \
                    if t.get("base_spell_power", 0) else 0

        self.current_health = getattr(self, "current_health", self.max_health)
        self.current_health = min(self.current_health, self.max_health)
        self.magic_resistance = int(t.get("base_magic_resist", 0) * level_mult)

        # Owner talents that scale the pet. pet_damage, pet_health and
        # pet_armor were authored by five talents across Hunter Beast Mastery
        # and Stormbringer's Air Elemental nodes ("increases your pet's damage
        # by 6% per rank") and read by nothing at all, so the entire pet-
        # scaling fantasy of those specs did nothing.
        #
        # This is the one place a Pet deliberately DOES reach into its owner's
        # talents. The docstring above says a pet "does not reach into the
        # owner's talents/gear", which was true and was exactly the gap: a
        # pet class with no way to be talented into is not a pet class. Kept
        # narrow - three explicit keys read here, nothing else - rather than
        # inheriting the owner's whole bonus pool, which would hand the pet
        # the owner's gear stats too.
        #
        # Fractions (0.06 = +6%), matching how the data authors them. Applied
        # to the level-scaled base so the bonus grows with the pet rather than
        # being a flat number that matters at level 10 and not at 60.
        owner = getattr(self, "owner", None)
        if owner is not None and hasattr(owner, "get_talent_effect"):
            dmg = owner.get_talent_effect("pet_damage", 0.0) or 0.0
            if dmg:
                self.attack_power = int(self.attack_power * (1.0 + dmg))
                self.spell_power = int(self.spell_power * (1.0 + dmg))
            hp = owner.get_talent_effect("pet_health", 0.0) or 0.0
            if hp:
                self.max_health = int(self.max_health * (1.0 + hp))
            arm = owner.get_talent_effect("pet_armor", 0.0) or 0.0
            if arm:
                self.base_armor = int(self.base_armor * (1.0 + arm))
        self.healing_power = 0  # no pet heals itself/others in the starting template set

        self.resource_type = t.get("resource_type", "mana")
        max_resource = int(t.get("base_resource", 0) * level_mult)
        if self.resource_type == "mana":
            self.max_mana = max_resource
            self.current_mana = getattr(self, "current_mana", self.max_mana)
            self.current_mana = min(self.current_mana, self.max_mana)
        elif self.resource_type == "rage":
            self.max_rage = 100
            self.current_rage = getattr(self, "current_rage", 0)
        elif self.resource_type == "energy":
            self.max_energy = 100
            self.current_energy = getattr(self, "current_energy", 100)

        self.crit_chance_physical = t.get("crit_chance", 5.0)
        self.crit_chance_spell = t.get("crit_chance", 5.0)
        # Guarded because __init__ calls this BEFORE the ability book is
        # built; the construction path calls it again afterwards.
        if getattr(self, "ability_book", None) is not None:
            self._scale_ability_power()

    def _scale_ability_power(self):
        """Put this pet's ability damage on the same footing as the rest
        of the roster, then grow it with level.

        Two separate corrections, both measured (see
        combat/pet_templates.offense_norm and ABILITY_LEVEL_RATE):

          - every one of the 57 pet abilities is authored with a SINGLE
            rank, so a wolf's Bite was 45 damage at level 1 and still 45
            at level 60 while player abilities ranked up nine times. A
            pet stopped contributing almost entirely past the twenties.
          - the authored values were never balanced against each other,
            running 18 to 90 at rank 1 with no role behind the spread.

        Applied per-instance rather than written back into the shared
        template dicts, which every pet built from that template reads.
        """
        from combat.pet_templates import offense_norm, ABILITY_LEVEL_RATE
        scale = (offense_norm(self.template)
                 * (1.0 + (self.level - 1) * ABILITY_LEVEL_RATE))

        # pet_damage HAS TO REACH THE ABILITY, NOT JUST THE STAT. A pet's
        # hit is effect_value + attack_power * 0.5, and the effect_value
        # half is the larger one - so a talent that only raised attack
        # power delivered a fraction of what it said. Measured on a fully
        # specced Beast Mastery hunter at 60: the tree stacks to +106% pet
        # damage and the wolf gained 40%.
        #
        # Not double-dipping. _apply_template_stats puts the same fraction
        # on attack/spell power, so the two halves now rise together and
        # the pet's total damage moves by exactly the advertised amount.
        owner = getattr(self, "owner", None)
        if owner is not None and hasattr(owner, "get_talent_effect"):
            scale *= 1.0 + (owner.get_talent_effect("pet_damage", 0.0) or 0.0)

        for ability in self.ability_book.get_all_abilities():
            ability.power_scale = scale

    #: A Character's maximum health is .health and a Monster's is .max_health, and a Pet is
    #: treated as a party member by combat (is_ally, living_allies, the turn order) while being
    #: built like a monster. Every piece of ally-side UI reads .health, so a Pet reaching one
    #: raised AttributeError - which is part of why pets never appeared in a combat screen at
    #: all. Aliased rather than renamed: the template loader and the monster-shaped code paths
    #: write max_health, so both spellings have to keep working and stay the same number.
    @property
    def health(self):
        return self.max_health

    @health.setter
    def health(self, value):
        self.max_health = value

    def sync_to_owner_level(self):
        """Call when the owner levels up so the pet doesn't fall behind -
        real WoW pets level up automatically alongside their Hunter/Warlock.

        REAL BUG THIS FIXES: this method refreshed every ability's own
        is_learned flag via refresh_rank_for_level, but never re-ran
        _autofill_hotbar - so a pet whose kit grows with level (ZIGGI-6K:
        Wrench Toss at 1, a party heal at 20, an Evocation-like resource
        restore at 30 - Kyle, Oct 2026) would newly satisfy is_learned on
        level-up but sit in hotbar=[None]*10 forever, since the only
        autofill call happens once in __init__ before any later ability
        could possibly be learned yet. choose_action() reads straight from
        self.hotbar, so the pet's AI would never even consider an ability
        it had technically already learned. Every pet before ZIGGI-6K
        happened to learn its entire kit at construction time (summoned
        already at the owner's current level), so this never surfaced
        until a pet template had abilities gated to a LATER level_req.
        """
        if self.level != getattr(self.owner, "level", self.level):
            self.level = self.owner.level
            self._apply_template_stats()
            for ability in self.ability_book.get_all_abilities():
                ability.refresh_rank_for_level(self.level)
            self._scale_ability_power()
            self._autofill_hotbar()

    def _autofill_hotbar(self):
        """Slot every learned ability into the first empty hotbar spots,
        same convention as Character._autofill_hotbar - a pet with unbound
        abilities would be uncastable from the UI.

        REAL BUG FIXED HERE: the original version used one shared index `i`
        for both "which hotbar slot to check" and "whether to advance",
        checking only `hotbar[i]` for each ability in turn instead of
        scanning forward for the next empty slot. That's correct the FIRST
        time this runs against an all-None hotbar (every ability lands in
        the next slot in order), but calling it again after some slots are
        already filled (sync_to_owner_level now does this - see its own
        docstring) breaks completely: once hotbar[0] is already occupied,
        `i` never advances past 0, so every already-learned ability's
        already-occupied check fails forever and a genuinely new ability
        learned later never gets placed at all, even though empty slots
        exist further down the bar. Already-bound abilities (by
        ability_id, not slot index) are now skipped explicitly, and the
        empty-slot search scans the WHOLE hotbar for each unbound ability
        rather than assuming slots fill in lockstep with the learned list.
        """
        bound_ids = {aid for aid in self.hotbar if aid is not None}
        learned = [a for a in self.ability_book.get_all_abilities()
                   if a.is_learned and a.ability_id not in bound_ids]
        for ability in learned:
            try:
                empty_slot = self.hotbar.index(None)
            except ValueError:
                break
            self.hotbar[empty_slot] = ability.ability_id

    # ------------------------------------------------------------------
    # Combat interface - mirrors the subset of Character/Monster that
    # CombatEngine, TurnMeter, and Ability.use() actually touch.
    # ------------------------------------------------------------------

    @property
    def armor(self):
        return max(0, self.base_armor + self.get_status_stat_mod("armor"))

    def get_effective_spell_power(self, school):
        """Minimal stand-in for Character.get_effective_spell_power - real
        per-school spell power (gear suffixes like "of Fiery Wrath") is a
        gear mechanic that doesn't exist for pets at all, so this just
        returns the flat self.spell_power every damage_and_heal/spell_damage
        call site expects. Added alongside ZIGGI-6K's Wrench Toss (Tinker
        Invention's capstone, pet-system push, Oct 2026) - the first pet
        ability to use effect_type=damage_and_heal, which calls this method
        directly; every other pet ability so far only read self.spell_power
        inline, so this gap was never hit until now."""
        return getattr(self, "spell_power", 0)

    def is_alive(self):
        return self.current_health > 0

    def take_damage(self, amount, damage_type="physical", attacker_level=None, attacker=None):
        # attacker accepted for call-signature parity with
        # Character.take_damage - see Monster.take_damage's docstring for
        # why (combat/abilities.py calls this uniformly across target
        # types). Pet doesn't use it either.
        from entities.character import Character
        if damage_type == "physical":
            reduction = Character.mitigation_from(self.armor, attacker_level)
        elif damage_type == "magic":
            reduction = Character.resist_mitigation_from(self.magic_resistance, attacker_level)
        else:
            reduction = 0

        # Rows decide reach, not damage - see entities/party.py.
        row_mult = 1.0

        from combat.abilities import level_diff_multiplier
        level_mult = level_diff_multiplier(attacker_level, self.level)

        actual = max(1, int(amount * (1.0 - reduction) * row_mult * level_mult))
        self.current_health -= actual
        return actual

    def heal(self, amount):
        self.current_health = min(self.max_health, self.current_health + amount)

    def get_resource(self, resource_type):
        """Current amount of this resource - mana/rage/energy only (Pet
        has no dict-backed secondary resources the way Character does
        for CoA classes, since a pet's kit only ever uses one primary
        pool). Added alongside real pet combat AI (Kyle, 2026-09-06:
        "SHOULD have pets") - REAL BUG this fixes: Ability._has_resource
        checks `hasattr(caster, "get_resource")` and treats a caster
        WITHOUT it as always able to afford anything (see that method's
        docstring - "Monsters and anything else without the generic API
        are treated as always able to pay"). Pet never had this method,
        so every pet ability cast silently skipped its own resource cost
        check entirely - not a crash, just resource costs doing nothing,
        exactly the kind of gap that looks fine until you actually check.
        Returns 0 for an unrecognized resource_type rather than raising."""
        rt = resource_type.value if hasattr(resource_type, "value") else resource_type
        return {
            "mana": getattr(self, "current_mana", 0),
            "rage": getattr(self, "current_rage", 0),
            "energy": getattr(self, "current_energy", 0),
        }.get(rt, 0)

    def get_resource_max(self, resource_type):
        """Mirrors Character.get_resource_max's shape - added alongside
        ZIGGI-6K's Overcharge (effect_type=restore_resource, pet-system
        push, Oct 2026), the first pet ability to need "% of max resource"
        math. REAL BUG this fixes: Pet had max_mana/max_rage/max_energy
        set directly on self (see _apply_template_stats) but no generic
        get_resource_max accessor - restore_resource's dispatch branch in
        combat/abilities.py calls caster.get_resource_max(resource_type)
        exactly like it does for Character, and silently produced 0%
        restores for any pet (hasattr check made it skip entirely, so this
        wasn't a crash either) until this existed. Returns 0 for an
        unrecognized resource_type rather than raising, matching
        get_resource's own convention above."""
        rt = resource_type.value if hasattr(resource_type, "value") else resource_type
        return {
            "mana": getattr(self, "max_mana", 0),
            "rage": getattr(self, "max_rage", 0),
            "energy": getattr(self, "max_energy", 0),
        }.get(rt, 0)

    def gain_resource(self, resource_type, amount):
        """Mirrors Character.gain_resource's shape (resource_type as a
        ResourceType or matching string) since Ability._consume_resource
        calls this generically on any caster."""
        rt = resource_type.value if hasattr(resource_type, "value") else resource_type
        if rt == "mana":
            self.current_mana = min(self.max_mana, self.current_mana + amount)
        elif rt == "rage":
            self.current_rage = min(getattr(self, "max_rage", 100), self.current_rage + amount)
        elif rt == "energy":
            self.current_energy = min(getattr(self, "max_energy", 100), self.current_energy + amount)
        return amount

    def spend_resource(self, resource_type, amount):
        rt = resource_type.value if hasattr(resource_type, "value") else resource_type
        if rt == "mana":
            self.current_mana = max(0, self.current_mana - amount)
        elif rt == "rage":
            self.current_rage = max(0, self.current_rage - amount)
        elif rt == "energy":
            self.current_energy = max(0, self.current_energy - amount)

    #: Energy regenerated per turn. Deliberately the same 25 Character uses
    #: (restore_resources_between_turns), because the pools match too:
    #: energy is a flat 100 for pets exactly as it is for players, and pet
    #: ability costs are flat per rank, so the player's rate gives a pet the
    #: same feel - its cheap attack every turn, its 30-cost one most turns.
    ENERGY_REGEN_PER_TURN = 25
    #: Mana regenerated per turn, as a fraction of max. Pets have no Spirit,
    #: so the player's Spirit-driven formula has nothing to read; a flat
    #: fraction of pool is the honest substitute. 8% rather than the 5%
    #: Monster uses, because 5% is tuned for the opposite goal - Monster's
    #: own docstring wants casters to get "a handful of spells then fall
    #: back to autoattack", which for a pet the player paid a talent and a
    #: cast for is the bug, not the pacing. Measured against the real
    #: templates: 8% keeps every caster pet's cheap button affordable every
    #: turn at every level, and its expensive one roughly every third turn.
    MANA_REGEN_FRACTION = 0.08

    def restore_resources_between_turns(self):
        """Give a pet back some of its pool at the end of its turn.

        REAL BUG THIS FIXES, and it affected 18 of the 28 pet templates.
        CombatEngine._end_turn_housekeeping calls this method on whichever
        combatant just acted, guarded by hasattr. Character has it. Monster
        has it. Pet did not, so no pet in the game regenerated anything,
        ever - a pet spent its starting pool and then auto-attacked for the
        rest of the fight.

        It was invisible in two ways. Nothing crashes: the hasattr guard
        just skips a pet silently. And choose_action's last resort is
        hotbar slot 0 whether or not slot 0 is affordable, so a starved pet
        keeps getting "chosen" every turn and only the combat log's
        "hesitates" says it did nothing - which is why the first version of
        tools/audit_pet_combat.py reported all 28 pets acting on all 20
        turns while half of them finished at 0 resource.

        Measured, before this existed: every energy pet stopped acting at
        turn 5 or 6 (Wolf's Bite costs 25 from a flat 100 pool - exactly
        four bites, then nothing for the rest of the fight), and the mana
        pets followed between turns 15 and 20. Ten pets never ran dry only
        because their whole kit is cheap enough to outlast twenty turns.

        Rage is deliberately absent. Rage is generated by fighting, not
        regenerated between turns - Character.restore_resources_between_turns
        leaves it alone for the same reason, and no pet template uses it.
        """
        if self.resource_type == "energy":
            self.current_energy = min(getattr(self, "max_energy", 100),
                                      self.current_energy
                                      + self.ENERGY_REGEN_PER_TURN)
        elif self.resource_type == "mana" and getattr(self, "max_mana", 0) > 0:
            self.current_mana = min(
                self.max_mana,
                self.current_mana
                + max(5, int(self.max_mana * self.MANA_REGEN_FRACTION)))

    def choose_action(self, target, allies=None):
        """
        Simple pet AI - real autonomous turn-taking (Kyle, 2026-09-06:
        "SHOULD have pets" - the Pet data model was always solid, real
        stats/resources/ability hotbar, but nothing ever called an
        equivalent of Monster.choose_action for it, so a summoned pet
        sat in the combatant list correctly classified as an ally but
        never actually acted on its own turn - same "looks done but
        never executes" gap as Bear/Cat Form earlier this session).

        Shaped after Monster.choose_action's priority stack, because the
        job is the same shape and that one is already proven:

          1. Heal when badly hurt.
          2. Restore its own resource when nearly dry.
          3. Dispel, when the target is actually carrying something the
             pet can strip.
          4. A self-buff that is not already running.
          5. A DoT or debuff the recipient is not already carrying.
          6. The biggest affordable damage ability.
          7. Hotbar slot 0 as the guaranteed fallback.

        REAL BUG THIS FIXES. Steps 2 to 5 did not exist. The old stack was
        heal / best-damage / slot 0, so an ability whose effect_type was
        anything else was simply never returned - it could be authored,
        learned, slotted on the hotbar and paid for, and the AI would not
        consider it on any turn of any fight. Fourteen shipped abilities
        across thirteen templates were in that state: Furious Howl, Rend,
        Updraft, Overcharge, Blood Pact, Sacrifice, Seduction, Spell Lock,
        Devour Magic, Dread Howl, Calibrate, Iron Hide, Corroding Wound and
        Mana Siphon. Several are the pet's whole reason for existing -
        Felhunter without Spell Lock and Devour Magic is a worse Voidwalker.

        Two details worth keeping:

        `effect_id == ability_id` for dot, hot, buff and debuff (see the
        four StatusEffect constructions in combat/abilities.py), which is
        what makes the has_status_effect checks below work at all. Monster
        carries a separate effect_id on its own abilities; a pet uses a
        player-schema Ability and does not.

        The damage pick still ranks on effect_value, which is NOT a damage
        estimate - the same number means different things to an AP-scaled
        `damage` and an SP-scaled `spell_damage`, and three templates
        (abomination, hellfire_abyssal, infernal) carry one of each with
        spell power well under their attack power. It is left alone because
        it is right today, measured rather than assumed: the SP ability
        really does hit harder on all three, and on all fourteen templates
        with two damage options the effect_value order matches the measured
        damage order. tools/audit_pet_combat.py checks that it stays true,
        which is the honest fix for a trap that is not yet a bug - putting
        a second copy of the engine's damage maths in here to rank two
        buttons would be the more likely thing to go wrong.

        target: the owner's current target - passed straight through
        from CombatEngine.execute_pet_action, since a pet doesn't pick
        its own target independently, it fights whatever its owner does.
        """
        learned = [self.ability_book.get_ability(aid) for aid in self.hotbar if aid]
        learned = [a for a in learned if a is not None]
        if not learned:
            return None

        def affordable(a):
            return self.get_resource(a.resource_type) >= a.cost

        options = [a for a in learned[1:]
                   if a.is_usable_by(self) and affordable(a)]

        # WHO the heal is for decides WHOSE health gates it. A self-heal
        # fires when the pet is hurt; a party or ally heal fires when
        # somebody it would land on is hurt. Gating both on the pet's own
        # health is why ZIGGI-6K never once cast Regenerative Field: the
        # Tinker's healing-bot pet is tanky and rarely the hurt one, so a
        # party heal gated on the BOT's health sat unused while the owner
        # dropped. `allies` comes from CombatEngine.execute_pet_action; it
        # is optional so a direct caller can still ask for a decision
        # without an engine, and then only the pet's own health is known.
        def max_hp(c):
            # Character stores its maximum as .health; Pet and Monster store
            # it as .max_health. A party heal has to read both, so neither
            # name can be assumed - the first version of this crashed on
            # Character.max_health, which does not exist.
            return getattr(c, "max_health", None) or getattr(c, "health", 0)

        def anyone_hurt(ability):
            if ability.target_type in ("party", "ally"):
                pool = list(allies or []) or [self.owner]
                return any(c is not None and getattr(c, "is_alive", True)
                           and max_hp(c) and c.current_health < max_hp(c) * 0.7
                           for c in pool)
            return self.current_health < self.max_health * 0.4

        for a in options:
            if a.effect_type in ("heal", "hot") and anyone_hurt(a):
                return a

        # Nearly dry, and holding something that refills it (ZIGGI-6K's
        # Overcharge). Gated on actually being low, or the pet would open
        # every fight topping off a full pool.
        pool_max = self.get_resource_max(self.resource_type)
        if pool_max and self.get_resource(self.resource_type) < pool_max * 0.35:
            for a in options:
                if a.effect_type == "restore_resource":
                    return a

        # Strip something, if there is something to strip. Unlike a buff or
        # a DoT there is no "already applied" state to test, so the test is
        # whether the target currently carries a matching effect at all -
        # otherwise Devour Magic fires into an empty target every cooldown.
        # A dispel school arrives as a DispelType on one side and as a bare
        # string on the other, so both have to be normalised. Reading
        # .value off whichever happened to be the enum looked right and
        # matched nothing: the effect stores "magic" as a plain string, so
        # getattr("magic", "value", None) gave None, None == "magic" was
        # False, and Devour Magic declined a target that was visibly
        # carrying a dispellable Magic buff.
        def school_of(obj):
            s = getattr(obj, "dispel_type", None)
            s = getattr(s, "value", s)
            return s.lower() if isinstance(s, str) else None

        for a in options:
            if a.effect_type != "dispel":
                continue
            school = school_of(a)
            effects = target._effects() if hasattr(target, "_effects") else []
            for e in effects:
                if school is None or school_of(e) == school:
                    return a

        for a in options:
            if a.effect_type == "buff" and not self.has_status_effect(a.ability_id):
                return a

        for a in options:
            if a.effect_type not in ("dot", "spell_dot", "debuff"):
                continue
            recipient = self if a.target_type == "self" else target
            if not (hasattr(recipient, "has_status_effect")
                    and recipient.has_status_effect(a.ability_id)):
                return a

        # Slot 0 is included here, not kept back as a special fallback.
        # The ordering is unchanged in the normal case - slot 0 is the cheap
        # basic attack, so its effect_value loses to the real nuke whenever
        # the nuke is up - and it fixes the fallback below having no
        # usability check at all.
        castable = [a for a in learned if a.is_usable_by(self) and affordable(a)]
        damage_options = [
            a for a in castable
            if a.effect_type in ("damage", "spell_damage", "ranged_damage",
                                 "damage_and_heal", "damage_and_restore_mana")
        ]
        if damage_options:
            return max(damage_options, key=lambda a: a.effect_value)

        # REAL BUG THIS FIXES: this used to be an unconditional
        # `return learned[0]`, handing back slot 0 whether or not slot 0
        # could actually be cast. Every pet template but one has a
        # cooldown-free slot 0, which is why it went unnoticed; Succubus's
        # Lash of Pain has a 2-turn cooldown, so the Warlock's Succubus
        # alternated "casts Lash of Pain" and "hesitates" for the whole
        # fight and acted on 11 turns out of 20 with a full mana pool.
        # Anything still castable beats hesitating.
        if castable:
            return max(castable, key=lambda a: a.effect_value)
        return None
