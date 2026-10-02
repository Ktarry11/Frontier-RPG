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

        self.max_health = int(t["base_hp"] * level_mult)
        self.current_health = getattr(self, "current_health", self.max_health)
        self.current_health = min(self.current_health, self.max_health)

        self.base_armor = int(t.get("base_armor", 0) * level_mult)
        self.magic_resistance = int(t.get("base_magic_resist", 0) * level_mult)
        self.attack_power = int(t.get("base_attack", 0) * level_mult)
        self.spell_power = int(t.get("base_spell_power", 0) * level_mult)
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

    def take_damage(self, amount, damage_type="physical", attacker_level=None):
        from entities.character import Character
        if damage_type == "physical":
            reduction = Character.mitigation_from(self.armor)
        elif damage_type == "magic":
            reduction = Character.mitigation_from(self.magic_resistance)
        else:
            reduction = 0

        from entities.party import row_damage_multiplier
        row_mult = row_damage_multiplier(self.row, damage_type)

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

    def choose_action(self, target):
        """
        Simple pet AI - real autonomous turn-taking (Kyle, 2026-09-06:
        "SHOULD have pets" - the Pet data model was always solid, real
        stats/resources/ability hotbar, but nothing ever called an
        equivalent of Monster.choose_action for it, so a summoned pet
        sat in the combatant list correctly classified as an ally but
        never actually acted on its own turn - same "looks done but
        never executes" gap as Bear/Cat Form earlier this session).

        Much simpler than Monster's priority stack (heal/buff/dot/best-
        damage/basic) since a pet's whole job is "hit whatever the owner
        is fighting" - not a boss with a rotation to play around:
          1. Self-heal if badly hurt and a heal is available and affordable.
          2. Biggest affordable damage ability (damage_and_heal counts as
             a damage option here too - Tinker's ZIGGI-6K's Wrench Toss
             both damages an enemy AND smart-heals the owner's party in
             one cast, so it needs to be reachable through the normal
             "attack something" priority, not just as an accidental
             last-resort fallback when it happens to be the only ability
             on the hotbar).
          3. Basic attack (first hotbar ability) as the guaranteed fallback.

        target: the owner's current target - passed straight through
        from CombatEngine.execute_pet_action, since a pet doesn't pick
        its own target independently, it fights whatever its owner does.
        """
        learned = [self.ability_book.get_ability(aid) for aid in self.hotbar if aid]
        learned = [a for a in learned if a is not None]
        if not learned:
            return None
        options = [a for a in learned[1:] if a.is_usable_by(self)]

        hurt = self.current_health < self.max_health * 0.4
        for a in options:
            if a.effect_type == "heal" and hurt and self.get_resource(a.resource_type) >= a.cost:
                return a

        damage_options = [
            a for a in options
            if a.effect_type in ("damage", "spell_damage", "ranged_damage", "damage_and_heal")
            and self.get_resource(a.resource_type) >= a.cost
        ]
        if damage_options:
            return max(damage_options, key=lambda a: a.effect_value)

        return learned[0]
