"""
Combat engine. Full ability system with resources and turn-based cooldowns.
Handles Character (player) vs Monster (enemy) - two DIFFERENT class systems.
"""
import random
from enum import Enum
from combat.turn_meter import TurnMeter
from entities.loot_generator import LootGenerator
from entities.boss_loot import get_fixed_boss_loot_all, shares_hoard


class CombatAction(Enum):
    ABILITY = "ability"
    DEFEND = "defend"
    ITEM = "item"
    FLEE = "flee"


class CombatEngine:
    """Combat system with abilities and resources."""
    
    #: Eating and drinking stop the moment a fight starts - see
    #: StatusEffectMixin.break_consumable_regen for why that rule is what keeps food from replacing
    #: potions outright.
    def _break_resting(self):
        for member in ([self.player] + list(getattr(self.party, "members", []))
                       if self.party else [self.player]):
            if hasattr(member, "break_consumable_regen"):
                member.break_consumable_regen()

    def __init__(self, player, enemy, party=None, enemies=None, zone=None):
        """
        Multi-combatant turn-based encounter.

        Backwards compatible with the old 1v1 signature: passing a single
        `player` and `enemy` still works and simply creates a one-member
        party against a one-member enemy group. `party` (an entities.Party)
        and `enemies` (a list of Monsters) are the multi-combatant path.

        The player controls EVERY ally, FF-style - there is no companion AI.
        Allies and enemies share one turn meter, so a fast Rogue really does
        act more often than a slow Thunder Lizard.

        zone: the real zone-key string combat is happening in (e.g.
        "valley_of_trials" or a cave name like "burning_blade_coven") -
        used only to feed QuestManager.record_kill's zone-restricted
        objectives (see _resolve_victory). None is fine for any test/
        script path that doesn't care about quest tracking - it just
        means zone-gated kill objectives won't advance from that fight,
        same as if the fight happened somewhere with no matching quest.
        """
        from entities.party import Party

        self.player = player
        self.party = party if party is not None else Party(player)
        self.zone = zone
        self._break_resting()

        # Keep .enemy pointing at a live enemy for any legacy caller, but the
        # real list is self.enemies.
        self.enemies = list(enemies) if enemies else ([enemy] if enemy else [])
        self.enemy = self.enemies[0] if self.enemies else None

        self.allies = self.party.members

        # Active pets ride alongside their owner as extra allies, but are
        # NOT party members (see entities/pet.py's module docstring for
        # why - party.members is capped at 5 recruited Characters, and a
        # pet is neither recruited nor a Character). Built fresh from
        # whichever party members currently have an active_pet, in the
        # same order as their owners, so a pet always sits right after
        # its owner in turn-order previews and UI lists.
        # all_pets, not active_pet: Tinker Mechanics and Necromancer
        # Animation field several at once (see Character.extra_pets), and
        # reading only the primary left every additional construct sitting
        # out of the fight it was summoned into.
        self.pets = [pet for m in self.allies for pet in getattr(m, "all_pets", None)
                     or ([m.active_pet] if getattr(m, "active_pet", None) else [])]

        self.combatants = self.allies + self.pets + self.enemies

        # Combat state
        self.turn_meter = TurnMeter(self.combatants)
        self.current_actor = None
        self.combat_log = []
        self.is_active = True
        self.combat_phase = "action"
        self.loot_generator = LootGenerator()
        self.loot_dropped = None   # last Item dropped, for the victory screen
        self.exp_earned = 0        # total XP awarded this fight, for the victory screen
        self.loot_gained = []      # every Item dropped this fight
        #: Drops the player could NOT take because their bags were full. Kyle,
        #: 2026-10-31, after reporting that no Grom's Rest boss dropped loot:
        #: "Ooooooh fuck bro I'm dumb. My bags are full." He was not dumb - the
        #: game knew, and said so only in the COMBAT LOG, while the victory panel
        #: he was actually looking at showed nothing at all. "Nothing dropped"
        #: and "something dropped and you could not carry it" rendered
        #: identically, which is how a full bag reads as six broken bosses.
        #: Equipment, epics and recipe scrolls INSERT at the front; vendor
        #: trash and material drops append. The victory banner only has room to
        #: name three, and losing a boss weapon matters more than losing a
        #: Choice Demon Horn.
        self.loot_missed = []
        self.copper_earned = 0     # coin dropped this fight (humanoids only), for the victory screen
        self.trash_gained = 0      # vendor trash items picked up this fight
        self.trash_value = 0       # their total sell value in copper
        self.victory = False
        #: Set by execute_flee. Distinct from `victory` being False, which
        #: otherwise means a wipe - the result screen has to tell "you ran"
        #: apart from "you died", and only one of those should offer loot.
        self.fled = False

        # Threat table: {enemy: {ally: threat_value}}. Per-enemy rather than
        # one shared pool, since two different monsters in the same fight
        # can (and in real WoW do) end up focused on different party
        # members - a table shared across all enemies would force them to
        # always agree on one target. Populated lazily (see gain_threat/
        # get_threat) so fights with no tank-style abilities in play never
        # allocate anything and default_target_for's random-choice fallback
        # below is untouched for them - existing non-tank content keeps
        # working exactly as it did before this system existed.
        self.threat_tables = {}

    # ------------------------------------------------------------------
    # Combatant queries
    # ------------------------------------------------------------------

    def living_allies(self):
        """Every living party member AND active pet - pets are allies for
        targeting purposes (buffs/heals can reach them, enemy_aoe never
        does), even though they're excluded from self.allies/party.members
        itself (see the pets-are-not-party-members note in __init__)."""
        return [a for a in self.allies + self.pets if a.is_alive()]

    def living_enemies(self):
        return [e for e in self.enemies if e.is_alive()]

    def summon_enemies(self, summoner, monsters, head_start=0.0):
        """Bring reinforcements into a fight already in progress.

        Kyle, 7 Nov: "build the boss summon add mechanics." Before this,
        tools/audit_boss_threat reported 0 of 358 bosses presenting "adds to
        handle", and the reason was structural the same way the stun was -
        the enemy list was built once in __init__ and nothing could ever
        append to it.

        Three things have to happen or a summoned add is scenery:

          enemies        so it can be targeted and counts toward the fight
                         being over
          combatants     so take_damage, AoE and row resolution see it
          turn_meter     so it ever gets a turn - see
                         TurnMeter.add_combatant

        Adds are marked is_summoned, which _calculate_exp_reward and the
        loot roll both check. A boss that can call help every six turns
        would otherwise be an infinite XP and loot faucet for anyone
        willing to stand there, which turns a mechanic into a farm.
        """
        added = []
        for m in monsters:
            if m is None:
                continue
            m.is_summoned = True
            m.summoned_by = getattr(summoner, "name", None)
            # An add inherits its summoner's row so melee still has to come
            # through the front line to reach a back-row caster's help.
            if not getattr(m, "row", None):
                m.row = getattr(summoner, "row", None) or "front"
            self.enemies.append(m)
            self.combatants.append(m)
            self.turn_meter.add_combatant(m, head_start=head_start)
            added.append(m)
        return added

    def is_ally(self, combatant):
        return combatant in self.allies or combatant in self.pets

    def gain_threat(self, ally, enemy, amount):
        """Add `amount` threat from `ally` on `enemy`'s table. Negative
        amounts are allowed (e.g. a future threat-reduction effect) but
        floor at 0 - real WoW threat never goes negative, it just stops
        being subtracted once it hits the floor.
        """
        if enemy is None or ally is None or amount == 0:
            return
        table = self.threat_tables.setdefault(enemy, {})
        table[ally] = max(0, table.get(ally, 0) + amount)

    def get_threat(self, enemy, ally):
        """Current threat `ally` has on `enemy`'s table (0 if never generated any)."""
        return self.threat_tables.get(enemy, {}).get(ally, 0)

    def highest_threat_target(self, enemy):
        """Living ally with the most threat on `enemy`'s table, or None if
        that enemy has no threat table yet (nobody's generated any threat
        against it) or everyone on its table has since died - callers
        should fall back to the existing random/front-row pick in that
        case, exactly as if no threat system were present.
        """
        table = self.threat_tables.get(enemy)
        if not table:
            return None
        living_entries = [(a, t) for a, t in table.items() if a.is_alive()]
        if not living_entries:
            return None
        return max(living_entries, key=lambda pair: pair[1])[0]

    def default_target_for(self, actor):
        """
        Sensible auto-target: enemies attack allies, allies attack enemies.

        Enemies prefer whoever holds highest threat on them, if any threat
        has been generated against them at all (see highest_threat_target) -
        this is what makes tank-style threat generation (Earthen Guardian,
        Defensive Stance, etc) actually redirect attacks rather than being a
        number nobody reads. Falls back to the original front-row-preferred
        random pick when there's no threat data for this enemy yet, so
        every fight that never touches threat behaves exactly as before.
        """
        if self.is_ally(actor):
            living = self.living_enemies()
            return living[0] if living else None

        from entities.party import FRONT_ROW
        living = self.living_allies()
        if not living:
            return None

        return self.threat_weighted_target(actor, living)

    #: How much of a share the lowest-threat ally still gets, relative to the highest. Threat
    #: should DECIDE who gets hit, not DICTATE it - see threat_weighted_target.
    #:
    #: 0.10 measured, not guessed: in a five-ally party it leaves the threat leader taking about
    #: three quarters of the swings and the other four about 7% each. 0.18 was tried first and
    #: gave the leader only 59%, which is too little for a tank holding five times the player's
    #: threat to feel like they are holding anything.
    THREAT_FLOOR = 0.10

    def threat_weighted_target(self, enemy, living):
        """Who this enemy swings at: usually whoever holds the most threat, not always.

        Kyle, 2026-10-31: "All 4 enemies just hit the exact same player and kill him. Then next
        time it's their turn, they do the same shit."

        He was describing strict argmax threat. The player does the damage, so the player tops
        every enemy's table, so every enemy in a four-mob pull swings at the player, every round,
        until the player is dead - and no amount of threat a companion generates changes a thing
        until it passes the player's, at which point the whole pack switches at once. Both states
        are the same bug: the target was a certainty rather than a tendency.

        A threat-WEIGHTED pick keeps the system meaning what it says - a tank who holds aggro
        takes most of the hits, and taunting still works - while letting a four-mob pull spread
        across the party the way it looks like it should. THREAT_FLOOR is what stops anyone
        being mathematically unhittable at zero threat, which is its own kind of fake.
        """
        from entities.party import FRONT_ROW
        from combat import rows as rowrules

        # ROWS GATE REACH BEFORE THREAT DECIDES. Kyle, 6 Nov: "melee mobs
        # will be stuck hitting front line, tank can still taunt ranged, but
        # they can go and attack back row if theyre not taunted." A melee
        # enemy simply cannot see the party's back line while anyone stands
        # in front, however much threat the back line has generated - which
        # is what finally makes a front row mean something. Ranged and caster
        # enemies are unrestricted, so a tank needs a ranged tool to peel
        # them. A taunt overrides rows entirely and is applied upstream, by
        # handing this method a single candidate.
        reachable = rowrules.reachable(enemy, self._enemy_attack_profile(enemy), living)
        living = reachable or living

        table = self.threat_tables.get(enemy) or {}
        entries = [(a, max(0.0, float(table.get(a, 0.0)))) for a in living]
        top = max((t for _, t in entries), default=0.0)
        if top <= 0:
            # Nobody has generated threat on this enemy yet - the original front-row-preferred
            # random pick, unchanged.
            front = [a for a in living if getattr(a, "row", FRONT_ROW) == FRONT_ROW]
            return random.choice(front or living)
        floor = top * self.THREAT_FLOOR
        weights = [max(floor, t) for _, t in entries]
        return random.choices([a for a, _ in entries], weights=weights, k=1)[0]

    def _enemy_attack_profile(self, enemy):
        """A stand-in ability describing how far this enemy can reach.

        A monster's auto-attack is not an Ability object, so there is
        nothing for combat/rows.reach_of to read. Its reach comes from where
        it stands: a back-row creature is a caster or a marksman and reaches
        either row; a front-row creature swings and does not. That holds for
        every one of the 18 templates and needs no per-creature authoring.
        """
        from combat import rows as rowrules

        class _Profile:
            reach = (rowrules.RANGED
                     if rowrules.row_of(enemy) == rowrules.BACK_ROW
                     else rowrules.MELEE)
            effect_type = None

        return _Profile

    def _owned_pets(self):
        """Every pet currently fielded by an ally, in owner order."""
        return [pet for m in self.allies
                for pet in (getattr(m, "all_pets", None)
                            or ([m.active_pet] if getattr(m, "active_pet", None) else []))]

    def sync_pets(self):
        """Bring pets summoned AFTER combat started into the fight.

        THE BUG THIS FIXES: self.pets and self.combatants were built once in
        __init__ and never updated, so a pet summoned mid-combat was inert for
        the rest of the fight. The cast succeeded, the owner gained the pet,
        and the engine never learned about it - it was absent from combatants,
        absent from the turn meter, and execute_pet_action's
        `if pet not in self.pets` guard rejected it outright. The turret just
        stood there.

        That is most of a class for Tinker, which has five summon_pet
        abilities (Sentry Turret at 1, Clockwork Assistant at 8, ZIGGI-6K at
        10, Mechano-Bear at 14, Rusthound at 30) and is built around fielding
        a board. It also silently broke every re-summon after a pet died
        mid-fight, for Hunter, Warlock, Necromancer, Witch Hunter and Felsworn
        alike - pets only ever worked if they were already out when combat
        began.

        Done here, engine-side, rather than in the summon_pet branch of
        Ability._apply_effect, so that ANY route that produces a pet is
        covered - a cast, a proc, a talent - without each one having to
        remember to announce itself.

        turn_meter.combatants is the same list object as self.combatants
        (TurnMeter stores the reference it is handed), so appending once
        registers the pet with both. A new pet starts on an empty meter and
        gets its turn speed computed the same way everyone else's is.

        Turn ORDER is meter-based, not list-based, so appending rather than
        inserting after the owner does not change when the pet acts - only
        where it shows up in a turn-order preview.
        """
        current = self._owned_pets()

        # A REPLACED PET LEAVES. Summoning a Voidwalker over an Imp swaps the owner's
        # active_pet, and this used to only ever ADD - so the dismissed Imp stayed in the
        # fight, still taking turns, with no owner. (And see update(): the swap was not even
        # noticed, because one pet for one pet does not change the count.) Kyle, 10 Nov: "if i
        # summon 1 demon - i CANT USE SUMMON TO REPLACE IT WITH ANOTHER."
        gone = [p for p in self.pets if not any(p is c for c in current)]
        for pet in gone:
            self.pets.remove(pet)
            if pet in self.combatants:
                self.combatants.remove(pet)
            if self.current_actor is pet:
                self.current_actor = None

        for pet in current:
            if pet in self.pets:
                continue
            self.pets.append(pet)
            self.combatants.append(pet)
            pet.turn_meter = 0.0
            self.turn_meter._refresh_turn_speed(pet)

    def update(self, dt):
        """Update combat state."""
        if not self.is_active:
            return

        # Cheap length check first - this runs every tick, and building the
        # pet list on each one would be wasteful for the overwhelming
        # majority of fights where nothing is summoned.
        # WHO, not how many: replacing one demon with another leaves the count at one, and a
        # count comparison never saw the swap.
        owned = self._owned_pets()
        if {id(p) for p in owned} != {id(p) for p in self.pets}:
            self.sync_pets()

        # Only look for a new actor if nobody is currently mid-turn. Without
        # this gate, current_actor stays stale after an action resolves and
        # resets its own meter to 0 - the very next frame would see
        # current_actor still equal to the actor who just went, and the
        # screen's "if current_actor is an enemy: act" check would fire
        # again, causing combatants to act multiple times per actual turn.
        if self.current_actor is None:
            actor = self.turn_meter.update(dt)
            if actor and actor.is_alive():
                self.current_actor = actor
                self.combat_phase = "action"

                # A STUNNED COMBATANT SPENDS THE TURN BEING STUNNED. This is
                # the only place a stun is paid for, and it has to be a real
                # turn: _end_turn is what ticks their status effects, which
                # is what counts the stun's duration down. See the deadlock
                # note in TurnMeter.update.
                #
                # It runs for the player and the monsters alike, so a stun
                # cannot behave differently depending on which side ate it.
                #
                # SAY SO IN THE LOG. The live report was "it kept forcing
                # turn skip on his druid" with nothing explaining why - the
                # stun was visible only as an icon in the stat panel, and a
                # turn that silently disappears reads as a broken game
                # rather than as a mechanic working.
                if getattr(actor, "is_stunned", False):
                    self.combat_log.append(
                        f"{actor.name} is stunned and loses the turn!")
                    actor.turn_meter = 0.0
                    self._end_turn(actor)
                    # Leave combat_phase alone: clearing current_actor is
                    # what hands the turn on, and the next update picks the
                    # following actor normally.
                    self.current_actor = None

        # A combatant who died to a DoT between turns must not keep the turn.
        if self.current_actor is not None and not self.current_actor.is_alive():
            self.current_actor = None

        # Check win/loss
        self._check_combat_end()

    def execute_ability(self, actor, ability_id, target):
        """Execute a PLAYER ability (Character only - uses ability_book)."""
        ability = actor.ability_book.get_ability(ability_id)
        if not ability:
            return False, "Ability not found"

        # Form-gated abilities (Mangle etc - see Ability.requires_form)
        # are hard-blocked here, not just visually flagged on the hotbar -
        # the button coloring in combat_screen.py is a courtesy, this is
        # the actual enforcement every cast path (hotbar, cast panel, any
        # future caller) funnels through.
        if hasattr(ability, "is_form_ready") and not ability.is_form_ready(actor):
            return False, f"{ability.name} requires a different form."

        # Ranged-weapon-gated abilities (universal Shoot/Wand - see
        # Ability.requires_ranged_weapon) get the same hard block. Before
        # this check existed, is_ranged_weapon_ready only affected the
        # hotbar button's grey-out color in combat_screen.py - nothing
        # actually stopped the ability from firing, so a Paladin with no
        # Ranged-slot item equipped could still use both Shoot AND Wand
        # (Kyle: "my paladin without a wand or a gun actually just used
        # both"). This is the real enforcement point every cast path
        # funnels through, same as the form check above it.
        if hasattr(ability, "is_ranged_weapon_ready") and not ability.is_ranged_weapon_ready(actor):
            return False, f"{ability.name} requires the right weapon equipped."

        # Wrong kind of creature for this crowd control. Ability.use refuses it too; asked here
        # as well so the refusal comes before a shapeshifter is dropped out of form to cast it.
        if target is not None and not isinstance(target, (list, tuple)) and target is not actor:
            from world.creature_types import blocked_reason
            if (getattr(ability, "max_targets", None) or 1) <= 1:
                reason = blocked_reason(ability.ability_id, ability.name, target)
                if reason:
                    return False, reason

        # CASTING BREAKS A NON-MANA FORM. Kyle, 3 Nov 2026: "in classic wow,
        # when a druid goes to cast it pulls them out of bear form (so we can
        # have it that if someone casts in bear form they will cast, but will
        # need to shift back into bear form and be at 0 rage when they're
        # back)."
        #
        # Only real spells break the form - the gate is "costs mana" and NOT
        # "is a mana ability", because every class's basic attack is itself
        # typed mana with a cost of 0 (druid_attack, warrior_attack, ...).
        # Gating on the type alone would have made swinging a paw in Bear Form
        # drop you out of it, which is both wrong and a different way to lose
        # a turn.
        #
        # Shapeshift abilities are exempt or shifting between forms would
        # revert you first and land you in Humanoid instead of Cat.
        if getattr(actor, "current_form", None) and hasattr(actor, "revert_form"):
            from combat.abilities import ResourceType
            from combat.forms import resource_for_form
            form_resource = resource_for_form(actor.current_form)
            cost = ability.talented_cost(actor) if hasattr(ability, "talented_cost") else 0
            if (form_resource is not None
                    and form_resource != ResourceType.MANA
                    and getattr(ability, "resource_type", None) == ResourceType.MANA
                    and cost > 0
                    and getattr(ability, "effect_type", None) != "shapeshift"):
                reverted, revert_msg = actor.revert_form()
                if reverted:
                    self.combat_log.append(revert_msg)

        # enemy_aoe abilities (Arcane Explosion, Chain Lightning,
        # Consecration, Multi-Shot, ...) hit every living enemy regardless
        # of which single target the player had selected - the selection
        # still matters for aiming single-target abilities, but an AoE
        # ability shouldn't be limited to whichever one enemy happened to
        # be highlighted.
        if getattr(ability, "target_type", None) == "enemy_aoe":
            # AN AOE HITS ONE ROW, AND THE PLAYER PICKS IT. Kyle's spec,
            # 6 Nov: "a warrior cleave only hits the front row when other
            # front liners are up, but a mage can pick an aoe on front or
            # back row. Then when front row is destroyed then the melee can
            # cleave the back row."
            #
            # combat/rows.targetable_rows has existed since the row system
            # landed and nothing ever called it, so every AoE in the game
            # hit the entire enemy side and rows did not apply to area
            # damage at all - which is most of what makes a back line mean
            # anything.
            #
            # The row is taken from whoever the player clicked rather than
            # from a new widget: a click already picks a combatant, and the
            # combatant it picks is standing in exactly one row. If the call
            # site passed a list (an AoE with no aimed target, or a monster
            # casting one), fall back to every living enemy, which is the
            # old behaviour.
            from combat import rows as rowrules
            living = self.living_enemies()
            aimed = target if not isinstance(target, (list, tuple)) else None
            if aimed is not None and aimed in living:
                row = rowrules.row_of(aimed)
                allowed = rowrules.targetable_rows(actor, ability, living)
                if row not in allowed and allowed:
                    row = allowed[0]
                target = rowrules.in_row(living, row) or living
            else:
                target = living

        # Nature's Swiftness-style effects: a buff that makes the CASTER'S
        # NEXT cast instant, rather than the triggering ability itself
        # being instant. next_cast_instant is a one-shot flag on the
        # actor (see Character.next_cast_instant), set by whatever grants
        # it and consumed here on the very next ability use - regardless
        # of what that ability is, matching how Nature's Swiftness works
        # in real WoW (it doesn't care what spell benefits, just that the
        # next one does).
        consumed_free_cast = False
        if getattr(actor, "next_cast_instant", False) and ability.effect_type != "enable_instant_cast":
            consumed_free_cast = True
            actor.next_cast_instant = False

        # Use ability. `party` is only consulted by damage_and_heal abilities
        # (Cryotherapist) to find the caster's lowest-HP ally to smart-heal -
        # every other effect_type ignores it. Passed as the actor's own
        # living allies (mirrors living_allies() usage a few lines up for
        # AoE targeting), so it naturally includes the actor's whole party
        # regardless of who's currently selected as the enemy target.
        success, message = ability.use(actor, target, party=self.living_allies(),
                                       engine=self)
        
        if success:
            self.combat_log.append(message)
            self._generate_threat_from_ability(actor, ability)

            # death_threat_retention_pct (Venomancer's Unyielding Will:
            # "reduces threat lost on death by 5%/rank") - a real talent
            # that previously had nothing to apply to, since this engine
            # had no resurrection mechanic at all. Ability._apply_effect's
            # new "revive" branch sets a one-shot _reviving_this_cast flag
            # on the target right after bringing them back to life (it has
            # no engine reference to touch threat_tables itself); this is
            # the one place that flag is read and cleared, since
            # threat_tables genuinely lives on the engine. The TARGET's own
            # talent applies (their own resilience against losing their
            # aggro), not the reviver's - a retention of 0 (no talent
            # spent) drops the revived character's threat entries
            # entirely, matching how a real death already behaves today
            # (highest_threat_target filters a dead ally out via
            # is_alive(), so their old threat was already functionally
            # zero the instant they died; this just makes that explicit in
            # the table itself rather than leaving a stale, since-dead
            # entry sitting there to be revived into).
            # wipes_threat (Kiet Somsak's "Nobody Looks Twice"): the caster stops existing as
            # far as every ordinary enemy is concerned. A boss does not forget.
            if getattr(ability, "wipes_threat", False):
                for enemy, table in self.threat_tables.items():
                    if not getattr(enemy, "is_boss", False):
                        table.pop(actor, None)

            if getattr(target, "_reviving_this_cast", False):
                target._reviving_this_cast = False
                retention = target.get_talent_effect("death_threat_retention_pct", 0.0) if hasattr(target, "get_talent_effect") else 0.0
                for table in self.threat_tables.values():
                    if target not in table:
                        continue
                    if retention > 0:
                        table[target] = max(0, int(table[target] * retention))
                    else:
                        table.pop(target, None)

            # Rage generation on basic attack: Warriors, and any Rage-form shapeshifter
            # (Druid Bear / Dire Bear, Venomancer Beetle) swinging their basic attack
            if (ability_id.endswith("_attack") and hasattr(actor, "generates_rage_from_combat")
                    and actor.generates_rage_from_combat()):
                actor.current_rage = min(100, actor.current_rage + 10)
                self.combat_log.append(f"{actor.name} gains 10 Rage!")

            if consumed_free_cast:
                self.combat_log.append(f"{ability.name} was instant!")

            # Turn-based translation of WoW's "instant cast": an ability
            # marked is_instant (Swiftmend, by its own nature) or one that
            # just consumed a pending next_cast_instant buff (Nature's
            # Swiftness -> anything) does NOT end the actor's turn -
            # current_actor stays set and combat_phase stays "action", so
            # the very next update() tick re-prompts the SAME actor for
            # another action instead of handing the turn meter to whoever
            # is next. Cooldowns/resource-restore/status-ticks for this
            # actor are deliberately skipped here too (see _end_turn) -
            # those only make sense once per real turn, not once per
            # instant cast within it.
            if not (ability.is_instant or consumed_free_cast):
                self._end_turn(actor)
        
        return success, message

    def _generate_threat_from_ability(self, actor, ability):
        """Convert the damage/healing an ability's cast actually dealt
        (Ability._last_threat_events, populated by _apply_effect) into real
        threat table entries.

        Threat model (documented rather than hidden in a magic constant):
          - Damage generates threat 1:1 with the amount dealt, credited to
            the specific enemy that was hit (multiple enemies from an AoE
            each get their own entry, off their own damage taken).
          - Healing generates threat at HEAL_THREAT_RATIO (0.5x the amount
            healed - real WoW's actual ratio, roughly), split against
            EVERY living enemy in the fight rather than one specific
            target, since a heal has no single enemy to attribute it to
            and real threat-from-healing works the same way (it threatens
            whoever's currently fighting you, not a chosen target).
          - Earthen Guardian's "+200% threat generated" (Shaman Tank) is
            read here as a flat 3x multiplier on the actor's own outgoing
            threat from this cast (200% MORE = 3x total), via the
            "threat_multiplier" talent-effect key - see
            Character.get_talent_effect. Anyone without that talent gets
            the multiplier's default of 1.0, so this is a no-op for every
            class that isn't tank-specced.

        No-ops entirely if this combat has no living enemies or the
        ability generated no threat events (e.g. a self-buff) - existing
        fights that never touch threat stay exactly as fast as before.
        """
        events = getattr(ability, "_last_threat_events", None)
        if not events:
            return

        HEAL_THREAT_RATIO = 0.5
        threat_mult = 1.0
        if hasattr(actor, "get_talent_effect"):
            threat_mult = actor.get_talent_effect("threat_multiplier", default=1.0) or 1.0
        # Temporary tank-stance BUFFS (CoA's "threat_generation_pct" stat_mod
        # - Cultist's Twilight Domain, Primalist's Heart of the Mountain,
        # Starcaller's Lunar Authority, etc) stack on top of the talent-based
        # multiplier above the same way Earthen Guardian's permanent talent
        # bonus does, just sourced from an active buff instead of a spent
        # talent point. Same +N% MORE convention (200 -> 3x, not 2x) as the
        # talent version, so both read identically in tooltips/JSON.
        if hasattr(actor, "get_status_stat_mod"):
            buff_pct = actor.get_status_stat_mod("threat_generation_pct") or 0.0
            threat_mult *= (1.0 + buff_pct / 100.0)

        # TALENT-sourced threat, same key but a DIFFERENT NUMERIC CONVENTION,
        # which is why it needs its own branch rather than folding into the
        # buff lookup above:
        #
        #   ability buff stat_mods  percent POINTS   (Twilight Domain: 180)
        #   talent node effects     FRACTIONS        (Defiance: 0.08/rank)
        #
        # Every threat talent in the game was authored on this key as a
        # fraction - 15 nodes across 11 specs, including Warrior
        # Protection's Defiance, the canonical tank threat talent, and the
        # threat-REDUCTION talents that are supposed to keep healers and
        # hybrid DPS off the top of the table (Subtlety, Healing Grace,
        # Spirit Weapons). None of them reached this method, because the
        # only talent key read here was threat_multiplier and NOT ONE node
        # uses it: threat_multiplier is reserved for Earthen Guardian, which
        # sets it as a true multiplier (3x) in get_talent_effects rather
        # than summing like every other key. So tanks held threat purely on
        # raw damage and healers generated full threat.
        #
        # Reading it here, additively, is what the 15 authored nodes already
        # mean, and it leaves threat_multiplier's multiplicative contract
        # untouched. Floored so a stack of reduction talents can only take
        # threat to zero, never invert it into healing the enemy's table.
        if hasattr(actor, "get_talent_effect"):
            talent_pct = actor.get_talent_effect("threat_generation_pct", 0.0) or 0.0
            threat_mult *= max(0.0, 1.0 + talent_pct)

        # low_health_threat_pct (Tinker's Battle Engineer: "+10%/rank
        # threat generated while below 50% health" - same "while below X%
        # health" shape as low_health_damage_reduction_pct in
        # Character.take_damage, just for threat instead of mitigation,
        # and read here rather than there since threat generation lives
        # entirely in this method). Shares that key's threshold-pairing
        # convention (low_health_threshold_pct on the same talent node) so
        # a future talent using a different threshold doesn't collide with
        # Battle Engineer's own 50%.
        if hasattr(actor, "get_talent_effect") and hasattr(actor, "health") and actor.health > 0:
            low_threat_pct = actor.get_talent_effect("low_health_threat_pct", 0.0)
            if low_threat_pct > 0:
                threshold = actor.get_talent_effect("low_health_threshold_pct", 0.5)
                if (actor.current_health / actor.health) < threshold:
                    threat_mult *= (1.0 + low_threat_pct)

        for enemy, amount, is_damage in events:
            if amount <= 0:
                continue
            if is_damage:
                if enemy is not None and enemy.is_alive():
                    self.gain_threat(actor, enemy, amount * threat_mult)
            else:
                # Heals have no single target enemy - threaten everyone
                # currently in the fight, same amount each.
                heal_threat = amount * HEAL_THREAT_RATIO * threat_mult
                for e in self.living_enemies():
                    self.gain_threat(actor, e, heal_threat)

    def execute_monster_action(self):
        """Execute the current enemy's turn using Monster's own AI/abilities."""
        enemy = self.current_actor
        if not enemy or self.is_ally(enemy) or not enemy.is_alive():
            return

        target = self.default_target_for(enemy)
        if target is None:
            self._end_turn(enemy)
            return

        chosen_ability = enemy.choose_action(target)
        # AoE monster abilities (Cleave, Whirlwind, Tail Sweep, breath
        # attacks, ...) hit every living ally at once - pass the full list
        # rather than just whichever single target choose_action() picked,
        # matching the player-side enemy_aoe handling in execute_ability().
        if getattr(chosen_ability, "is_aoe", False):
            success, message = chosen_ability.use(enemy, self.living_allies(), engine=self)
        else:
            success, message = chosen_ability.use(enemy, target, engine=self)

        if success:
            self.combat_log.append(message)
        else:
            # Shouldn't normally happen (basic attack always available), but
            # fall back safely rather than stalling the turn meter forever.
            self.combat_log.append(f"{enemy.name} hesitates.")

        if not target.is_alive():
            self.combat_log.append(f"{target.name} has fallen!")

        self._end_turn(enemy)

    def execute_pet_action(self):
        """Execute the current pet's turn using Pet.choose_action - real
        autonomous pet AI (Kyle, 2026-09-06: "SHOULD have pets"), same
        overall shape as execute_monster_action but a pet always attacks
        ENEMIES (it's an ally, per is_ally) rather than picking from
        living_allies() the way Monster AI does. A pet targets whatever
        its owner's own default target would be, not a target it picks
        independently - matches real WoW pet behavior (a Hunter's pet
        attacks what the Hunter is fighting, not its own separate pick).
        """
        pet = self.current_actor
        if not pet or pet not in self.pets or not pet.is_alive():
            return

        owner = getattr(pet, "owner", None)
        target = self.default_target_for(owner) if owner is not None else self.default_target_for(pet)
        if target is None:
            self._end_turn(pet)
            return

        chosen_ability = pet.choose_action(target, allies=self.living_allies())
        if chosen_ability is None:
            self.combat_log.append(f"{pet.name} has no action to take.")
            self._end_turn(pet)
            return

        # party=self.living_allies() mirrors execute_ability's own call
        # (see its "party is only consulted by damage_and_heal abilities"
        # comment) - without this, a damage_and_heal pet ability (Tinker's
        # ZIGGI-6K: "Wrench Toss... deals small damage and smart heals the
        # lowest-HP ally") would fall back to _apply_smart_heal's no-party
        # default of healing only the CASTER (the pet itself), never a
        # real party member, silently defeating the entire point of a
        # healing-bot pet. Found and fixed during the pet-system push
        # (Oct 2026) while building ZIGGI-6K - every ally-targeting pet
        # ability was missing its real target list until now, not just
        # this one spec's.
        # PET AoE WAS NOT EXPRESSIBLE AT ALL, and this line is why it looked
        # like it was. A pet uses a player-schema Ability, and Ability did not
        # accept is_aoe - only MonsterAbility has it - so this getattr always
        # returned False no matter what the template authored. Authoring
        # target_type "enemy_aoe" instead was strictly WORSE: this branch
        # still passed a single target, so _hostile_recipients saw one enemy
        # while AOE_DAMAGE_MULTIPLIER was applied anyway, i.e. a single-target
        # hit at 60% damage.
        #
        # Ability now accepts is_aoe, so a pet AoE needs BOTH: is_aoe to get
        # the full enemy list here, and target_type "enemy_aoe" so
        # _hostile_recipients spreads it. Player abilities are unaffected -
        # execute_ability never reads is_aoe and never did.
        # A FRIENDLY ability needs a FRIENDLY target, and this is where two
        # pet heals were being thrown at the enemy. `target` above is always
        # the owner's enemy, and Ability._recipients resolves target_type
        # "party" by reading that argument: given a list it heals the list,
        # given anything else it "degrades to the caster rather than
        # silently no-op" - so a pet's party heal healed the pet. Measured
        # before this: ZIGGI-6K's Regenerative Field cast with its owner at
        # 30% health logged "ZIGGI-6K casts Regenerative Field on ZIGGI-6K"
        # and healed nobody, because ZIGGI-6K was already full. A
        # healing-bot pet that cannot heal its owner is the whole spec.
        #
        # The player path never hit this: the combat screen passes the party
        # list as `target` for a party-wide ability. A pet has no screen, so
        # the engine has to resolve it, exactly as it already does for
        # enemy_aoe two lines down. Mindbender's Whispered Mending
        # (target_type "ally") was wrong the same way.
        if chosen_ability.target_type in ("party", "ally", "self"):
            success, message = chosen_ability.use(pet, self.living_allies(),
                                                  party=self.living_allies(), engine=self)
        elif getattr(chosen_ability, "is_aoe", False) and (
                chosen_ability.target_type == "enemy_aoe"):
            success, message = chosen_ability.use(pet, self.living_enemies(),
                                                  party=self.living_allies(), engine=self)
        else:
            success, message = chosen_ability.use(pet, target, party=self.living_allies(),
                                                  engine=self)

        if success:
            self.combat_log.append(message)
        else:
            self.combat_log.append(f"{pet.name} hesitates.")

        if not target.is_alive():
            self.combat_log.append(f"{target.name} has fallen!")

        self._end_turn(pet)

    def execute_defend(self, actor):
        """Execute defend action."""
        log_entry = f"{actor.name} takes a defensive stance!"
        self.combat_log.append(log_entry)
        self._end_turn(actor)

    def execute_flee(self, actor):
        """Leave the fight. Returns (fled, message).

        100% success, per Kyle on 3 Nov 2026: "We can have fleeing from
        combat at 100% chance." CombatAction.FLEE had been an enum member
        since the engine was written and nothing ever implemented it, so
        there was no way out of a fight at all - which is why a druid who
        could not act had to kill the process.

        No XP, no loot, no quest credit: _resolve_victory is deliberately
        not called. The enemies stay alive and keep whatever damage they
        took, matching the overworld's expectation that a fight you walked
        away from is a fight that did not happen.

        A full party flees together - one member running while the rest
        stay in combat is not a state anything else in the engine models.
        """
        if not self.is_active:
            return False, "The fight is already over."

        name = getattr(actor, "name", "The party")
        self.combat_log.append(f"{name} flees from combat!")
        self.is_active = False
        self.fled = True
        # Running away ends the fight as surely as winning it: nothing an enemy put on the
        # party follows it out. (Victory already did this; fleeing and wiping did not.)
        self.party.restore_after_combat()
        self.combat_phase = "fled"
        self.current_actor = None
        return True, f"{name} flees from combat!"
    
    def _end_turn(self, actor):
        """Shared turn-end logic: consume turn, decrement cooldowns, restore resources."""
        self.turn_meter.consume_turn(actor)
        self.current_actor = None
        self.combat_phase = "resolution"
        
        # Cooldowns and status effects both advance ONLY for the actor whose
        # turn just ended - "1 turn" means one of YOUR turns, not one of
        # anybody's. Previously both combatants were advanced on every single
        # turn, so a 4-turn Rejuvenation on the player lost 2 turns per round
        # (one on the player's turn, one on the enemy's) and a 4-turn DoT on
        # the enemy did the same. Every duration in the game was effectively
        # halved, and worse, it was halved unevenly once the turn meter let a
        # fast combatant act twice in a row.
        if hasattr(actor, "ability_book"):
            actor.ability_book.decrement_all_cooldowns()
        elif hasattr(actor, "decrement_all_cooldowns"):
            actor.decrement_all_cooldowns()

        # Restore resources for next turn (Characters only - monsters don't
        # use mana/rage/energy pools).
        if hasattr(actor, "restore_resources_between_turns"):
            actor.restore_resources_between_turns()

        # Tick DoTs/HoTs/buffs riding on the actor who just acted.
        if hasattr(actor, "tick_status_effects"):
            for msg in actor.tick_status_effects():
                self.combat_log.append(msg)

    def _check_combat_end(self):
        """Check for victory (all enemies down) or defeat (party wiped)."""
        if not self.living_enemies():
            self._resolve_victory()
        elif not self.living_allies():
            self.is_active = False
            self.victory = False
            self.combat_log.append("Defeat! The party has been wiped out!")
            self.party.restore_after_combat()

    _loot_item_drop_table = None  # class-level cache, loaded once across all CombatEngine instances

    @classmethod
    def _get_loot_item_drops(cls, creature_name):
        """LootItem drop entries for a creature, from
        data/creatures/quest_drops.json. Cached at the class level after
        first load - this file doesn't change during a play session, so
        re-parsing it on every single kill in every fight would be pure
        waste. Returns [] for a creature with no entries (the overwhelming
        majority), never raises on a missing/malformed file."""
        if cls._loot_item_drop_table is None:
            import json
            from pathlib import Path
            path = Path(__file__).parent.parent / "data" / "creatures" / "quest_drops.json"
            try:
                with open(path, "r") as f:
                    cls._loot_item_drop_table = json.load(f).get("drops", {})
            except (OSError, json.JSONDecodeError):
                cls._loot_item_drop_table = {}
        return cls._loot_item_drop_table.get(creature_name, [])

    def _resolve_victory(self):
        """Award XP, loot and currency once every enemy is down."""
        self.is_active = False
        self.victory = True

        # Clear lingering DoTs/HoTs/buffs on the whole party so nothing leaks
        # into the next fight (a Rejuvenation ticking through the overworld,
        # or an enemy debuff still stuck on someone two encounters later).
        self.party.restore_after_combat()

        defeated = ", ".join(e.name for e in self.enemies)
        self.combat_log.append(f"Victory! The party defeated {defeated}!")

        # Advance any active quest tracking these kills - real
        # QuestManager.record_kill call per enemy, not a batch, since
        # each enemy could independently be a boss (is_boss varies per
        # enemy in a mixed pull, e.g. a boss with trash adds).
        from world.quest_manager import get_quest_manager
        quest_mgr = get_quest_manager()
        from world.faction_manager import get_faction_manager
        faction_mgr = get_faction_manager()
        self.faction_gains = {}
        for e in self.enemies:
            quest_mgr.record_kill(e.name, self.zone, is_boss=getattr(e, "is_boss", False))
            # Only enemies a faction has a stake in pay anything - see faction_manager's docstring for why
            # this is not a flat "dungeon mobs give rep" rule. Almost every call here is a dict miss.
            # Returns a LIST - shared ground pays everyone with a stake in it, so one boss in the
            # Barrens can move both Orgrimmar and Thunder Bluff.
            for fid, gained, tier_up in faction_mgr.award_for_kill(
                    e.name, zone=self.zone, is_boss=getattr(e, "is_boss", False)):
                self.faction_gains[fid] = self.faction_gains.get(fid, 0) + gained
                if tier_up:
                    self.combat_log.append(
                        f"You are now {tier_up['name']} with {faction_mgr.get(fid).name}.")
        for fid, amt in self.faction_gains.items():
            self.combat_log.append(f"+{amt} reputation with {faction_mgr.get(fid).name}.")

        # BANTER on the two combat moments worth a reaction: a boss going down, and somebody walking
        # out of a fight that nearly ended them. The beat is queued here and drawn by the overworld
        # once the player is back on their feet - a line over the victory screen would be noise.
        from world.banter_manager import get_banter_manager
        banter = get_banter_manager()
        if any(getattr(e, "is_boss", False) for e in self.enemies):
            banter.fire("boss_down", self.party, zone=self.zone)
        else:
            hurt = [m for m in getattr(self.party, "members", [])
                    if getattr(m, "health", 0) and m.current_health / m.health <= 0.15]
            if hurt:
                banter.fire("close_call", self.party, zone=self.zone)

        # XP is summed across every enemy, then awarded to the whole roster.
        # Active members get full value, benched get a reduced share.
        exp_reward = sum(self._calculate_exp_reward(e) for e in self.enemies)
        self.combat_log.append(f"Gained {exp_reward} experience!")
        # Stored as an attribute (not just logged) so the victory screen can
        # show a clean "+X EXP" line without scraping combat_log text.
        self.exp_earned = exp_reward

        for member, levels in self.party.award_experience(exp_reward):
            if levels == 1:
                self.combat_log.append(
                    f"{member.name} leveled up! Now level {member.level}!")
            else:
                self.combat_log.append(
                    f"{member.name} gained {levels} levels! (now {member.level})")
            if member is self.player:
                for line in self._format_level_gains():
                    self.combat_log.append(line)

        # Loot rolls once per enemy, always into the PLAYER's own bag
        # specifically (per Kyle: kill loot always goes to the active
        # player character, even though every character - including
        # companions - now has their own independent inventory). Gear for
        # a companion is assigned by equipping it onto them afterward from
        # the party/inventory screen, moving it out of the player's bag.
        #
        # Bosses use generate_boss_loot() instead of the trash roll: a
        # guaranteed drop, floored at Rare ("blue") rarity, so killing a
        # boss is reliably worth it rather than rolling the identical table
        # a wolf rolls. Trash keeps the normal 35% chance / unfloored rarity.
        #
        # Fixed/curated boss loot (entities/boss_loot.py) is checked FIRST,
        # ahead of the procedural roll - a small, growing set of dungeon
        # bosses (Sunken Grotto's three, so far) have hand-authored drop
        # pools instead of a fully-random item, so their loot can be
        # designed around their theme (Kyle: "crab will have int/sp
        # shield, str/sp boots, and tank trinket", etc). Any boss not in
        # that table falls through to generate_boss_loot() exactly as
        # before - this never changes behavior for bosses without a
        # fixed table.
        # A BOSS CAN NOW DROP SEVERAL ITEMS, so this is a list of drops
        # rather than one. get_fixed_boss_loot_all returns one item for an
        # ordinary boss (identical behaviour), three for the Return Voyage's
        # double boss, and NONE for the second member of that pair, whose
        # hoard is the first member's - see entities/boss_loot.MULTI_DROP and
        # SHARED_HOARD. The empty list matters: a boss who shares a hoard
        # must not fall through to the procedural roll, or he adds a fourth
        # drop to a fight specified as three. `is None` would have let him.
        for enemy in self.enemies:
            # A SUMMONED ADD DROPS NOTHING. A boss that calls for help every
            # six turns would otherwise be an infinite loot faucet for anyone
            # willing to stand there and keep killing the help, which turns a
            # mechanic into a farm. Same reasoning in _calculate_exp_reward.
            if getattr(enemy, "is_summoned", False):
                continue
            if getattr(enemy, "is_boss", False):
                drops = get_fixed_boss_loot_all(enemy.name)
                if not drops and not shares_hoard(enemy.name):
                    drops = [self.loot_generator.generate_boss_loot(
                        creature_level=enemy.level,
                        char_class=self.player.char_class,
                        player_level=self.player.level,
                    )]
            else:
                drops = [self.loot_generator.generate_loot_for_creature(
                    creature_level=enemy.level,
                    char_class=self.player.char_class,
                    player_level=self.player.level,
                )]
            for loot in [d for d in drops if d]:
                if self.player.add_to_inventory(loot):
                    self.loot_dropped = loot
                    self.loot_gained.append(loot)
                    self.combat_log.append(f"{enemy.name} dropped: {loot.name}!")
                else:
                    # Bag full - the kill still happened and XP/currency
                    # below is unaffected, but the item itself never enters
                    # inventory. Silently eating the drop would just look
                    # like a missing-loot bug, so it's called out in the log.
                    self.combat_log.append(
                        f"{enemy.name} dropped {loot.name}, but your bags are full!")
                    self.loot_missed.insert(0, loot.name)

            # NAMED EPICS. Kyle, 2026-10-28: "occasional drops as epic after lvl 30 in Dungeons
            # and also for world drop after lvl 30." Rolled separately from the gear roll above
            # because that roll is bypassed on every level 30+ boss - get_fixed_boss_loot hands
            # back a fixed rare before rarity is ever considered, which is why there was not one
            # epic in the game. See entities/epic_drops.py for the rates and the reasoning.
            from entities.epic_drops import roll_epic
            epic = roll_epic(enemy, self.player.level)
            if epic is not None:
                if self.player.add_to_inventory(epic):
                    self.loot_gained.append(epic)
                    self.combat_log.append(f"{enemy.name} dropped: {epic.name}!")
                else:
                    self.combat_log.append(
                        f"{enemy.name} dropped {epic.name}, but your bags are full!")
                    self.loot_missed.insert(0, epic.name)

            # RECIPE SCROLLS. entities/recipe_drops.py decides; world/recipe_manager builds the
            # item; the inventory screen already knows how to learn from one on click. This call
            # site is the thing that was missing - 135 recipes carried source "drop" and nothing in
            # the codebase ever asked for one, so they were labelled as world drops and could not
            # be found. Rolled per enemy, same as every other drop here.
            from entities.recipe_drops import roll_recipe
            scroll_id = roll_recipe(enemy)
            if scroll_id:
                from world.recipe_manager import make_recipe_scroll
                scroll = make_recipe_scroll(scroll_id)
                if scroll is not None:
                    if self.player.add_to_inventory(scroll):
                        self.loot_gained.append(scroll)
                        self.combat_log.append(f"{enemy.name} dropped: {scroll.name}!")
                    else:
                        self.combat_log.append(
                            f"{enemy.name} dropped {scroll.name}, but your bags are full!")
                        self.loot_missed.insert(0, scroll.name)

            # Per-creature LootItem drops (quest items, materials, trash)
            # - a real drop table, separate from the gear roll above.
            # Added specifically to close the Sagewood Petal gap Kyle
            # found (a fetch quest referencing an item nothing dropped) -
            # data/creatures/quest_drops.json is the real source of
            # truth, keyed by the same creature-name string Monster.name
            # already carries.
            for drop_def in self._get_loot_item_drops(enemy.name):
                import random as _random
                if _random.random() > drop_def.get("chance", 1.0):
                    continue
                # Quest-category items stop dropping once the player
                # already has enough for every active quest that wants
                # them (Kyle's bug report - quest items are never
                # sellable, so over-dropping them left dead weight
                # permanently stuck in the bag with no way to clear it).
                # Materials/trash aren't quest-gated at all and always
                # pass this check.
                item_id = drop_def["item_id"]
                if drop_def.get("category", "quest") == "quest":
                    from world.quest_manager import get_quest_manager
                    if not get_quest_manager().still_needs_item(self.player, item_id):
                        continue
                from entities.loot_item import LootItem, add_loot_item
                fit = add_loot_item(
                    self.player, item_id, drop_def["name"],
                    category=drop_def.get("category", "quest"),
                    amount=drop_def.get("amount", 1),
                    description=drop_def.get("description", ""),
                    icon_id=drop_def.get("icon_id"),
                    sell_price=drop_def.get("sell_price", 0),
                    rarity=drop_def.get("rarity"),
                    starts_quest_id=drop_def.get("starts_quest"),
                )
                if fit:
                    self.combat_log.append(f"{enemy.name} dropped: {drop_def['name']}!")
                    # THE VICTORY SCREEN READS loot_gained, NOT THE LOG. Kyle, 2026-10-31:
                    # "When killing a monster that drops quest items, the victory screen doesnt
                    # show the quest item drops (it only shows equipment and vendor trash)."
                    # Every other drop path in this method appends to loot_gained; this one was
                    # written later and only ever wrote a log line, so the one drop a player is
                    # actively hunting was the one drop the results panel stayed silent about.
                    #
                    # add_loot_item returns True/False (it stacks, so there is no single new
                    # object to hand back), so the stack it landed in is fetched out of the bag.
                    # Reversed because a brand-new stack is appended at the end, and the panel
                    # only reads .name and .get_rarity_color(), both of which LootItem has.
                    stack = next((it for it in reversed(self.player.inventory)
                                  if isinstance(it, LootItem) and it.item_id == item_id), None)
                    if stack is not None:
                        self.loot_gained.append(stack)
                    if drop_def.get("starts_quest"):
                        self.combat_log.append("It looks important - open your bag and click it to read it.")
                else:
                    self.combat_log.append(
                        f"{enemy.name} dropped {drop_def['name']}, but your bags are full!")
                    self.loot_missed.append(drop_def['name'])

        # Coin + vendor trash (entities/vendor_trash.py, data/items/vendor_trash.json). WoW logic: only humanoid-type
        # creatures carry coin (dungeon mobs pay 1.5x, bosses 4x); everything else drops vendor trash by style (hides,
        # claws, cores...) 30% of the time in the open world, 60% in caves/dungeons. Rolled once PER ENEMY, so group
        # pulls pay per mob. Coin goes to the party's shared purse (Party.copper, see entities/party.py CURRENCY).
        from entities.vendor_trash import roll_drops
        from entities.loot_item import add_loot_item
        total_copper = 0
        trash_count = 0
        trash_value = 0
        for enemy in self.enemies:
            drop = roll_drops(enemy)
            total_copper += drop["copper"]
            for it in drop["items"]:
                fit = add_loot_item(self.player, it["item_id"], it["name"], category="trash", amount=1,
                                    description=it["description"], icon_id=it["icon_id"], sell_price=it["price"])
                if fit:
                    trash_count += 1
                    trash_value += it["price"]
                    self.combat_log.append(f"{enemy.name} dropped: {it['name']}.")
                else:
                    self.combat_log.append(f"{enemy.name} dropped {it['name']}, but your bags are full!")
                    self.loot_missed.append(it['name'])
        # Cloth for Tailoring (entities/cloth_drops.py): humanoids only. Materials stack without a bag cap.
        try:
            from entities.cloth_drops import roll_cloth
            from world.gathering_manager import get_gathering_node_manager
            gm = get_gathering_node_manager()
            for enemy in self.enemies:
                for material_id, qty in roll_cloth(enemy):
                    mat = gm.make_material_instance(material_id)
                    if mat is None:
                        continue
                    mat.quantity = qty
                    self.player.add_material(mat)
                    # The victory panel reads loot_gained, not the log - see the note on
                    # the quest-drop path above. Materials were log-only, so every cloth,
                    # meat and leather drop was silent on the results screen.
                    self.loot_gained.append(mat)
                    self.combat_log.append(f"{enemy.name} dropped: {mat.name}{' x%d' % qty if qty > 1 else ''}.")
        except Exception as exc:  # cloth is a bonus; never let it break victory
            print(f"WARNING: cloth drop failed: {exc}")
        # Meat for Cooking (entities/meat_drops.py): beasts only, and deliberately NOT gated on a
        # profession - anyone can take the meat off a boar, and you need Cooking to do something with
        # it. A profession you cannot start because you were never allowed to pick up its inputs is a
        # profession nobody takes.
        try:
            from entities.meat_drops import roll_meat
            from world.gathering_manager import get_gathering_node_manager
            gm_meat = get_gathering_node_manager()
            for enemy in self.enemies:
                for material_id, qty in roll_meat(enemy):
                    mat = gm_meat.make_material_instance(material_id)
                    if mat is None:
                        continue
                    mat.quantity = qty
                    self.player.add_material(mat)
                    # The victory panel reads loot_gained, not the log - see the note on
                    # the quest-drop path above. Materials were log-only, so every cloth,
                    # meat and leather drop was silent on the results screen.
                    self.loot_gained.append(mat)
                    self.combat_log.append(
                        f"You butchered {enemy.name}: {mat.name}{' x%d' % qty if qty > 1 else ''}.")
        except Exception as exc:
            print(f"WARNING: meat drop failed: {exc}")

        # Leather for Leatherworking (entities/skinning_drops.py): beasts only, Skinning gated.
        try:
            from entities.skinning_drops import roll_leather
            from world.gathering_manager import get_gathering_node_manager, TIER_SKILL_CAPS
            gm = get_gathering_node_manager()
            for enemy in self.enemies:
                for material_id, qty in roll_leather(enemy, player=self.player):
                    mat = gm.make_material_instance(material_id)
                    if mat is None:
                        continue
                    mat.quantity = qty
                    self.player.add_material(mat)
                    # The victory panel reads loot_gained, not the log - see the note on
                    # the quest-drop path above. Materials were log-only, so every cloth,
                    # meat and leather drop was silent on the results screen.
                    self.loot_gained.append(mat)
                    self.combat_log.append(f"You skinned {enemy.name}: {mat.name}{' x%d' % qty if qty > 1 else ''}.")

                    # Skinning skill-up. This was missing entirely: leather was
                    # handed over but the skill never moved, so Skinning would
                    # have sat at 0 forever and never tiered up - the one
                    # gathering profession that didn't progress. Same shape as
                    # the node-gathering path in overworld_screen._gather:
                    # roll against the material's own orange/yellow/green/grey
                    # skill_range, then award 1 point capped to the material's
                    # tier, and say so rather than leaving it silent.
                    current = self.player.profession_skills.get("skinning", 0)
                    if not gm.roll_skill_up(material_id, current):
                        continue
                    if current >= self.player.profession_cap("skinning"):
                        self.combat_log.append(
                            "Skinning is at its cap - visit your trainer to advance.")
                    else:
                        self.player.gain_profession_skill(
                            "skinning", 1, cap=TIER_SKILL_CAPS.get(mat.tier))
                        self.combat_log.append("Skinning skill up!")
        except Exception as exc:  # skinning is a bonus; never let it break victory
            print(f"WARNING: skinning drop failed: {exc}")
        self.trash_gained = trash_count
        self.trash_value = trash_value
        self.copper_earned = total_copper
        if total_copper > 0:
            self.party.add_currency(total_copper)
            self.combat_log.append(f"Looted: {self.party.get_currency_string()}")

    def _format_level_gains(self):
        """Turn the player's aggregated level-up gains into combat log lines."""
        gains = getattr(self.player, "last_level_gains", None) or {}
        lines = []

        stat_labels = [
            ("strength", "STR"), ("stamina", "STA"), ("intellect", "INT"),
            ("spirit", "SPI"), ("agility", "AGI"),
        ]
        stat_parts = [f"+{gains[key]} {label}"
                      for key, label in stat_labels if gains.get(key, 0) > 0]
        if stat_parts:
            lines.append("  " + "  ".join(stat_parts))

        pool_parts = []
        if gains.get("health", 0) > 0:
            pool_parts.append(f"+{gains['health']} HP")
        if gains.get("mana", 0) > 0:
            pool_parts.append(f"+{gains['mana']} Mana")
        if pool_parts:
            lines.append("  " + "  ".join(pool_parts))

        if gains.get("talent_points", 0) > 0:
            points = gains["talent_points"]
            lines.append(f"  +{points} talent point{'s' if points != 1 else ''}!")

        # Class training: new abilities / ranks are bought from a trainer of your class (any town)
        try:
            from world import training_manager
            waiting = len(training_manager.offers(self.player))
        except Exception:
            waiting = 0
        if waiting:
            lines.append(f"  {waiting} new skill{'s' if waiting != 1 else ''} to learn - visit your class trainer!")

        return lines

    def _calculate_exp_reward(self, enemy=None):
        """
        Calculate XP from enemy, scaled by monster level, with bonuses for:
          - Difficulty band vs the PARTY AVERAGE level, WoW con-colour style
            (combat/difficulty.py) - grey enemies pay nothing at all
          - Boss/elite creatures (is_boss flag, set by CreatureManager)
          - Cave/subzone encounters (location_type tag, set by CreatureManager) -
            NOTE: currently only ever fires for "open_zone" in practice, since
            cave/subzone tilemap traversal isn't built yet. The multiplier is
            wired in now so it activates automatically once that traversal
            exists, without needing to touch this method again.
        """
        from combat.difficulty import kill_xp_multiplier, party_average_level

        enemy = enemy or self.enemy
        # A summoned add pays no XP - see summon_enemies. Killing the help a
        # boss keeps calling should cost the party time and resources, not
        # reward them for letting the fight run long.
        if getattr(enemy, "is_summoned", False):
            return 0
        base_exp = enemy.get_exp_reward()

        # WoW con colours, against the PARTY AVERAGE rather than the player's
        # own level (Kyle, 4 Nov: "this should be based on the average party
        # level to simplify stuff"). A grey enemy returns 0.0 here and the whole
        # reward collapses to nothing, which is the point of the system.
        #
        # This REPLACES the old hand-rolled +-5 breakpoints rather than sitting
        # beside them. That block and world/quest.py's copy of it were written
        # to mirror each other by hand and each said so in its docstring - two
        # statements of one rule, which is the shape most of this project's
        # bugs have taken. Both now call combat/difficulty.py.
        party_level = party_average_level(self.party, fallback=self.player.level)
        multiplier = kill_xp_multiplier(enemy.level, party_level)
        if multiplier <= 0.0:
            return 0  # grey: no XP, and no boss/cave bonus on top of nothing
        reward = base_exp * multiplier

        # Boss/elite bonus - a beefed-up cave/subzone boss should feel like a
        # real event, not just "a slightly tankier trash mob"
        if getattr(enemy, "is_boss", False):
            reward = int(reward * 1.75)

        # Dungeon/cave bonus - see docstring note above on current activation status
        location_type = getattr(enemy, "location_type", "open_zone")
        if location_type == "cave":
            reward = int(reward * 1.5)
        elif location_type == "subzone":
            reward = int(reward * 1.2)

        # Global kill-XP rate, applied LAST so it scales the finished reward -
        # level difference, boss bonus and location bonus all included. Putting
        # it on base_exp instead would have let the 1.75x boss and 1.5x cave
        # multipliers claw part of the reduction back.
        from config import KILL_EXP_MULTIPLIER
        return max(1, int(reward * KILL_EXP_MULTIPLIER))
    
    def get_recent_log(self, count=5):
        """Get last N log entries."""
        return self.combat_log[-count:]
    
    def get_player_abilities(self):
        """Get all player abilities for hotbar display."""
        return self.player.ability_book.get_all_abilities()
