"""
Monster class for enemies. Separate from Character - creatures have their own
stat blocks instead of using player classes (a Boar isn't a "Warrior").

TEMPLATES ARE NOW LOADED FROM JSON
----------------------------------
This module used to carry its own hardcoded MONSTER_TEMPLATES dict with 6
entries, while data/creatures/templates.json carried 15 and was loaded by
nothing at all. Monster.__init__ fell back to "beast_basic" for anything it
didn't recognise, so the 9 JSON-only templates - humanoid_ranged,
humanoid_rogue, beast_large, undead_basic, demon_hound, demon_caster,
aquatic_basic, elemental_bruiser, vermin_swarm - silently became boars.
58 of 143 creatures had the wrong stat block AND the wrong moveset, which
is why centaur archers used Gore.

There is now exactly one template table (tools/monster_templates.py ->
templates.json) and an unknown template key is a hard error, not a boar.

ABILITY KITS
------------
Movesets no longer live on the template. Templates are mechanical shapes
("squishy, high INT, has mana"); kits are flavour. That separation is what
lets a Scarlet Crusade chaplain and a Burning Blade cultist share the
humanoid_caster stat block while casting completely different spells - the
Scarlet get Holy Smite and Holy Light, the cultists keep Shadow Bolt and
Curse of Agony.

Resolution order for a creature's kit:
    creatures.json "ability_kit"  ->  template "default_kit"  ->  hard error

The key is "ability_kit", not "kit". This line said "kit" for a long time and
the key it named was read by nothing, which is how 33 creatures ended up
fighting with their template's default moveset - Skeleton Archer as a generic
marksman, Zombie Bear as a boar - with their own authored kits loading for
nobody. CreatureManager._reject_dead_kit_key now raises on the dead key at
load time; its docstring has the full history.
"""
import json
import random
from pathlib import Path

from combat.status_effects import StatusEffect, EffectType, StatusEffectMixin


_DATA_DIR = Path(__file__).parent.parent / "data" / "creatures"
_TEMPLATES = None
_KITS = None


def _load_json(filename, root_key):
    path = _DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Regenerate it with "
            f"`python3 tools/generate_creatures.py`.")
    with open(path, "r") as f:
        return json.load(f).get(root_key, {})


def get_templates():
    global _TEMPLATES
    if _TEMPLATES is None:
        _TEMPLATES = _load_json("templates.json", "templates")
    return _TEMPLATES


def get_kits():
    global _KITS
    if _KITS is None:
        _KITS = _load_json("ability_kits.json", "kits")
    return _KITS


# Kept as a module-level name because other code and tools import it.
# It is now a view onto the JSON, not a second copy of the data.
class _TemplateView(dict):
    def __getitem__(self, key):
        return get_templates()[key]

    def get(self, key, default=None):
        return get_templates().get(key, default)

    def __contains__(self, key):
        return key in get_templates()

    def keys(self):
        return get_templates().keys()

    def items(self):
        return get_templates().items()

    def __len__(self):
        return len(get_templates())

    def __iter__(self):
        return iter(get_templates())


MONSTER_TEMPLATES = _TemplateView()


class MonsterAbility:
    """
    One entry in a monster's moveset.

    Supports the same effect vocabulary the player has, so a monster can
    finally apply a DoT, shield itself, or slow you. Previously monsters
    could only deal flat damage or heal - every "poison", "bleed" and
    "hex" in the bestiary resolved as a plain hit with a scary name.
    """

    KINDS = ("damage", "heal", "dot", "buff", "debuff")

    #: Same convention as the player-side Ability.AOE_DAMAGE_MULTIPLIER -
    #: each target of an AoE monster ability takes a reduced share rather
    #: than full single-target damage, so a boss's Cleave/Whirlwind hits
    #: the whole party without trivializing single-target fights or making
    #: AoE strictly better than focusing one target for the same cost.
    AOE_DAMAGE_MULTIPLIER = 0.6

    def __init__(self, name, kind="damage", amount=0, cooldown=0,
                 mana_cost=0, school="physical", duration=0,
                 stat_mods=None, self_only=False, is_aoe=False,
                 rider=None, hp_below=None, lifesteal=0.0,
                 dispel_type=None):
        if kind not in self.KINDS:
            raise ValueError(f"{name}: unknown ability kind '{kind}'")
        self.name = name
        self.kind = kind
        self.amount = amount
        self.cooldown = cooldown
        self.turns_remaining = 0
        self.mana_cost = mana_cost
        self.school = school
        self.duration = duration
        self.stat_mods = stat_mods or {}
        # DISPEL SCHOOL - the thing that makes a cleanse worth casting. This
        # did not exist on MonsterAbility, so NO monster debuff or DoT in the
        # game was dispellable: a sweep found 0 monster effects carrying a
        # dispel_type against 525 debuff/dot monster abilities. Meanwhile 14
        # player abilities across 14 classes exist purely to remove them -
        # Paladin's Cleanse, Priest's Dispel Magic and Abolish Disease,
        # Primalist's Soothing Touch, Tinker's Med Pack and so on - and every
        # one of them had literally nothing to act on in PvE.
        # None stays the default, matching StatusEffect: most plain combat
        # debuffs are not dispellable, and a physical bleed never is.
        self.dispel_type = dispel_type
        self.self_only = self_only
        # True for abilities that hit every living member of the opposing
        # side at once (Cleave, Whirlwind, Tail Sweep, Frost Nova, breath
        # attacks, ...). Previously there was no such concept at all - a
        # monster ability always hit exactly the single target passed to
        # use(), no matter how unambiguously AoE the name was.
        self.is_aoe = is_aoe
        # Boss tools (2026-10-24: bosses were "glorified punching bags" because
        # their kits were basic + two weak self-buffs/debuffs that cost a whole
        # turn each).  A damage ability can now carry a RIDER - a buff on the
        # caster or a debuff on every target it hits - so the buff/debuff comes
        # with a real attack instead of replacing one.
        #   rider = {"effect": "buff"|"debuff", "duration": n, "stat_mods": {...}}
        self.rider = rider or None
        # Phase gate: only usable while the caster is at or below this fraction
        # of max health (enrage / desperation abilities).
        self.hp_below = hp_below
        # Fraction of damage dealt returned to the caster as healing.
        self.lifesteal = lifesteal

        # Stable id so re-applying refreshes rather than stacks, matching
        # how player DoTs behave.
        self.effect_id = "mob_" + name.lower().replace(" ", "_").replace(":", "")

    # -- Backwards compatibility ------------------------------------
    # Old code and saves referred to .damage / .effect_type.
    @property
    def damage(self):
        return self.amount if self.kind in ("damage", "dot") else 0

    @property
    def effect_type(self):
        return "heal" if self.kind == "heal" else self.kind

    @property
    def heal_amount(self):
        return self.amount if self.kind == "heal" else 0

    def is_available(self, caster=None):
        """Off cooldown AND affordable. The old version only checked the
        cooldown, so mana costs authored in the template data had no effect
        whatsoever - a caster could never actually run dry."""
        if self.turns_remaining > 0:
            return False
        # A monster with NO mana pool (max_mana 0) treats mana costs as flavour:
        # 23 kits (Maeve the Weeping, Lady Sarevess, Baron Ashbury, Thrumbone ...)
        # authored costs on templates that have no mana at all, which made every
        # one of those abilities - including the basic attack - permanently
        # unavailable, so those monsters just "hesitated" for the whole fight.
        if (caster is not None and self.mana_cost > 0
                and getattr(caster, "max_mana", 0) > 0):
            if getattr(caster, "current_mana", 0) < self.mana_cost:
                return False
        if self.hp_below is not None and caster is not None:
            if caster.current_health > caster.max_health * self.hp_below:
                return False
        return True

    @property
    def rider_effect_id(self):
        return self.effect_id + "_rider"

    def _apply_rider(self, caster, hit_targets):
        """Apply this damage ability's rider. Returns a list of log fragments."""
        if not self.rider:
            return []
        rider = self.rider
        is_buff = rider.get("effect") == "buff"
        recipients = [caster] if is_buff else list(hit_targets)
        out = []
        for r in recipients:
            effect = StatusEffect(
                effect_id=self.rider_effect_id, name=self.name,
                effect_type=EffectType.BUFF if is_buff else EffectType.DEBUFF,
                duration=rider.get("duration", 3),
                stat_mods=dict(rider.get("stat_mods") or {}),
                # A BUFF RIDER'S dispel_type USED TO BE HARD-DROPPED HERE,
                # same as the self-buff case in use() - see the long note
                # there. Passed through now, so a rider the data tags as
                # Magic is purgeable; absent from the data it is None, which
                # is what it already was.
                dispel_type=rider.get("dispel_type"),
                source_name=caster.name, real_time_seconds=None)
            out.append(r.apply_status_effect(effect))
        return out

    def use(self, caster, target, party=None, engine=None):
        """party/engine are accepted and ignored.

        CombatEngine calls .use() on player Abilities and MonsterAbilities
        through the same code paths, and player abilities now take `engine`
        so their procs can reach the other combatants (splash_heal and
        splash_damage both need it). Monsters carry no procs, so the
        parameters are absorbed here rather than making every call site
        branch on which kind of ability it is holding.
        """
        """Execute this ability. Returns (success, message).

        `target` may be a single combatant (existing callers, and every
        non-AoE ability) or a list of every living opposing combatant, for
        an is_aoe ability - combat_engine.py passes the full living-allies
        list when the monster's chosen ability is AoE. Non-AoE abilities
        normalize a list down to its first entry, so passing the full list
        unconditionally never breaks a single-target ability.
        """
        if not self.is_available(caster):
            return False, f"{self.name} unavailable"

        self.turns_remaining = self.cooldown
        if self.mana_cost > 0 and hasattr(caster, "current_mana"):
            caster.current_mana = max(0, caster.current_mana - self.mana_cost)

        power = getattr(caster, "ability_power_bonus", 0)

        if self.kind == "heal":
            healed = self.amount + power
            caster.heal(healed)
            return True, f"{caster.name} casts {self.name} and heals {healed}!"

        if self.kind == "damage":
            targets = self._resolve_targets(target)
            if not targets:
                return True, f"{caster.name} uses {self.name}, but there's no one there!"
            amount = self.amount + power
            if self.is_aoe and len(targets) > 1:
                amount = int(amount * self.AOE_DAMAGE_MULTIPLIER)
            lines = []
            first_actual = None
            total = 0
            landed = []
            for t in targets:
                actual = t.take_damage(amount, self.school,
                                        attacker_level=getattr(caster, "level", None))
                lines.append(f"{actual} to {t.name}")
                total += actual
                if actual > 0:
                    landed.append(t)
                if first_actual is None:
                    first_actual = actual
            if self.is_aoe and len(targets) > 1:
                msg = f"{caster.name} uses {self.name} on everyone ({', '.join(lines)})!"
            else:
                msg = (f"{caster.name} uses {self.name} on "
                       f"{targets[0].name} for {first_actual} damage!")
            if self.lifesteal > 0 and total > 0:
                healed = max(1, int(total * self.lifesteal))
                caster.heal(healed)
                msg += f" {caster.name} drains {healed} health."
            # a dodged / parried / fully absorbed hit carries no debuff
            extra = self._apply_rider(caster, landed)
            if extra:
                msg += " " + " ".join(extra)
            return True, msg

        if self.kind == "dot":
            targets = self._resolve_targets(target)
            if not targets:
                return True, f"{caster.name} uses {self.name}, but there's no one there!"
            amount = self.amount
            if self.is_aoe and len(targets) > 1:
                amount = max(1, int(amount * self.AOE_DAMAGE_MULTIPLIER))
            msgs = []
            for t in targets:
                effect = StatusEffect(
                    effect_id=self.effect_id, name=self.name,
                    effect_type=EffectType.DOT, duration=self.duration,
                    potency=amount, damage_school=self.school,
                    dispel_type=self.dispel_type,
                    source_name=caster.name)
                msgs.append(t.apply_status_effect(effect))
            if self.is_aoe and len(targets) > 1:
                return True, f"{caster.name} uses {self.name} on everyone. {' '.join(msgs)}"
            return True, f"{caster.name} uses {self.name}. {msgs[0]}"

        # buff / debuff
        if self.self_only:
            recipients = [caster]
        else:
            recipients = self._resolve_targets(target)
            if not recipients:
                recipients = [caster]
        msgs = []
        for recipient in recipients:
            effect = StatusEffect(
                effect_id=self.effect_id, name=self.name,
                effect_type=(EffectType.BUFF if self.self_only
                             else EffectType.DEBUFF),
                duration=self.duration, stat_mods=dict(self.stat_mods),
                # A SELF-BUFF'S AUTHORED dispel_type WAS THROWN AWAY HERE.
                # The line read `None if self.self_only else self.dispel_type`,
                # so no monster buff in the game could be purged no matter
                # what the kit said - which is the exact mirror of the bug
                # that put dispel_type on MonsterAbility in the first place
                # (see the comment in __init__: 14 player cleanses with
                # nothing to act on in PvE). Six player abilities exist purely
                # to strip a Magic buff off an ENEMY - Shaman's Purge,
                # Felsworn's Consume Magic, Necromancer's Death's Due,
                # Stormbringer's Stormbreaker, Runemaster's Leyfeed, Sun
                # Cleric's Gavel of Wrath - and all 435 monster buffs plus 198
                # buff riders were invisible to every one of them.
                #
                # Measured before this: a MonsterAbility built with
                # dispel_type="magic" and self_only=True applied a
                # StatusEffect whose dispel_type was None, and
                # monster.dispel_effect(DispelType.MAGIC) returned None.
                #
                # This changes NOTHING about today's balance: zero of the 435
                # buff entries in ability_kits.json author a dispel_type, so
                # every one of them still resolves to None exactly as before.
                # It only means that tagging them (the same pass that tagged
                # 444 dot/debuff effects, with 166 physical ones deliberately
                # left undispellable) will now actually do something. Which
                # buffs should be purgeable is a content call, deliberately
                # left to the owner rather than decided here.
                dispel_type=self.dispel_type,
                source_name=caster.name,
                # Monster buffs are COMBAT effects, so they must expire in turns.
                # The StatusEffect default gives buffs a 30-minute real-time
                # clock (correct for the player's Fortitude), which would leave
                # a monster's self-buff running for the rest of the session and
                # bleeding into unrelated fights.
                real_time_seconds=None)
            msgs.append(recipient.apply_status_effect(effect))
        # apply_status_effect() already names the recipient and describes
        # the stat_mods (e.g. "Cave Skitterer gains Skitter (+8 Agility)."),
        # so this doesn't repeat "uses {self.name}" - that used to make
        # every buff/debuff log line say the ability's name twice while
        # still never explaining what it actually did.
        return True, " ".join(msgs)

    def _resolve_targets(self, target):
        """Normalize a single target or a list into the list this ability
        should actually hit: every living entry for an is_aoe ability, or
        just the first for a single-target one - so callers can always
        pass the full living-opponents list without special-casing based
        on whether the chosen ability happens to be AoE."""
        if isinstance(target, (list, tuple)):
            living = [t for t in target if t is not None and t.is_alive()]
            if self.is_aoe:
                return living
            return living[:1]
        if target is None:
            return []
        return [target]

    def decrement_cooldown(self):
        if self.turns_remaining > 0:
            self.turns_remaining -= 1


class Monster(StatusEffectMixin):
    """
    A creature/enemy with its own independent stat block.
    NOT tied to player classes - a Boar is a Boar, not a "Warrior".
    """

    def __init__(self, name, monster_type, level=1, kit=None):
        """
        Args:
            name: Display name (e.g. "Kolkar Outrunner")
            monster_type: Template key from templates.json
            level: Monster level (scales stats)
            kit: Ability kit id. Falls back to the template's default_kit.
        """
        self._init_status_effects()
        self.name = name
        self.monster_type = monster_type
        self.level = level
        self.is_monster = True
        self.is_boss = False

        templates = get_templates()
        if monster_type not in templates:
            # Deliberately loud. The old silent fallback to beast_basic is
            # what hid nine broken templates for the entire project.
            raise KeyError(
                f"Unknown monster template '{monster_type}' for '{name}'. "
                f"Known: {sorted(templates)}")
        template = templates[monster_type]

        level_mult = 1.0 + (level - 1) * 0.15  # +15% per level (conservative)

        self.max_health = int(template["base_hp"] * level_mult)
        self.current_health = self.max_health

        self.base_armor = int(template["base_armor"] * level_mult)
        self.base_magic_resist = int(template["base_magic_resist"] * level_mult)

        # Per-school resistances (Fire/Frost/Nature/Shadow/Arcane/Holy -
        # see DamageSchool in combat/status_effects.py and Character.
        # get_resistance for the shared real lookup/mitigation logic this
        # mirrors). Optional per-template keys (base_fire_resist,
        # base_frost_resist, ...); every existing template in
        # templates.json predates these keys and simply gets 0 for all
        # six, which is correct - a generic "Beast Basic" or "Humanoid
        # Warrior" template has no reason to resist any element. This is
        # the real hook for Kyle's actual per-monster-type goal (a Fire
        # Elemental template should set base_fire_resist high and
        # base_frost_resist 0 or even negative/vulnerable, a Frost
        # Elemental the reverse) - authoring those specific elemental
        # templates is a follow-up content task, not part of this engine
        # change.
        self.fire_resistance = int(template.get("base_fire_resist", 0) * level_mult)
        self.frost_resistance = int(template.get("base_frost_resist", 0) * level_mult)
        self.nature_resistance = int(template.get("base_nature_resist", 0) * level_mult)
        self.shadow_resistance = int(template.get("base_shadow_resist", 0) * level_mult)
        self.arcane_resistance = int(template.get("base_arcane_resist", 0) * level_mult)
        self.holy_resistance = int(template.get("base_holy_resist", 0) * level_mult)

        self.attack_power = int(template["base_attack"] * level_mult)
        self.spell_power = int(template.get("base_spell_power", 0) * level_mult)

        self.max_mana = int(template.get("base_mana", 0) * level_mult)
        self.current_mana = self.max_mana
        self.resource_type = template.get("resource_type", "rage")

        self.speed = template["speed"]
        self.crit_chance = template.get("crit_chance", 5.0)
        self.exp_reward_base = template["exp_reward"]

        # Ability kit
        self.kit_id = kit or template.get("default_kit")
        kits = get_kits()
        if self.kit_id not in kits:
            raise KeyError(
                f"Unknown ability kit '{self.kit_id}' for '{name}'. "
                f"Check data/creatures/ability_kits.json.")

        self.abilities = []
        for entry in kits[self.kit_id]:
            scaled = entry.get("amount", 0)
            # Buffs/debuffs carry no amount; scaling their stat_mods by level
            # would make a level 20 mob's self-buff wildly stronger than its
            # own attacks, so only damage/heal/dot potency scales.
            if entry.get("kind") in ("damage", "heal", "dot"):
                scaled = int(scaled * level_mult)
            self.abilities.append(MonsterAbility(
                name=entry["name"],
                kind=entry.get("kind", "damage"),
                amount=scaled,
                cooldown=entry.get("cooldown", 0),
                mana_cost=entry.get("mana_cost", 0),
                school=entry.get("school", "physical"),
                duration=entry.get("duration", 0),
                stat_mods=entry.get("stat_mods"),
                self_only=entry.get("self_only", False),
                is_aoe=entry.get("is_aoe", False),
                rider=entry.get("rider"),
                hp_below=entry.get("hp_below"),
                lifesteal=entry.get("lifesteal", 0.0),
                dispel_type=entry.get("dispel_type"),
            ))

        # Combat state
        self.turn_meter = 0.0
        self.turn_speed = self.speed
        self.status_effects = []

    # ------------------------------------------------------------------
    # Effective stats — buffs and debuffs on a MONSTER used to do nothing.
    # Character folds stat_mods into its derived-stat pool; Monster had no
    # equivalent, so "Thick Hide" and "Stoneskin" were flavour text.
    # ------------------------------------------------------------------
    @property
    def armor(self):
        return max(0, self.base_armor + self.get_status_stat_mod("armor"))

    @armor.setter
    def armor(self, value):
        # Kept so older code (and the boss multiplier) can assign directly.
        self.base_armor = value

    @property
    def magic_resistance(self):
        """Same story as `armor`, one stat later, and it stayed broken when
        armor was fixed.

        Every "Ward"/"Shroud"/"Aegis"/"Barrier" in the bestiary is a
        self_only buff or a buff rider granting `magic_resistance`, and
        take_damage DOES read self.magic_resistance (the "magic" branch) -
        but it was a plain attribute, so the status mod went nowhere. 29
        abilities across 29 kits, 696 points of magic resistance in total,
        all of it flavour text: Flame Ward, Fel Armor, Tidal Ward, Mana Ward,
        Amber Ward, Spirit Ward, Hollow Ward, Prismatic Ward, Storm Feathers,
        Chitin Veil, Lightning Shield and the rest.

        Measured before this existed, with a +200 magic_resistance buff on a
        humanoid_caster: a 1000-point magic hit landed for 893 both with and
        without the buff, while the same +200 through `armor` took a physical
        hit from 1000 to 523. tools/audit_monster_combat.py reports the whole
        set under INERT MONSTER BUFF; this moves the magic_resistance half of
        that list out of it.

        Floored at 0 so a future resistance-stripping debuff can strip the
        pool bare but never invert into bonus damage, exactly as `armor` does.
        """
        return max(0, self.base_magic_resist
                   + int(self.get_status_stat_mod("magic_resistance")))

    @magic_resistance.setter
    def magic_resistance(self, value):
        # Same reason as armor's setter: older code and the tools assign
        # straight to it (tools/monster_templates.py's elemental overrides,
        # any boss tuning pass), and a property with no setter would turn
        # those into AttributeError.
        self.base_magic_resist = value

    @property
    def ability_power_bonus(self):
        """Flat damage/healing swing from active buffs and debuffs."""
        return int(self.get_status_stat_mod("attack_power"))

    def is_alive(self):
        return self.current_health > 0

    def get_resistance(self, school):
        """Real per-school resistance lookup - mirrors Character.
        get_resistance exactly (same combined-school "lowest resist"
        rule), kept as Monster's own method rather than importing
        Character, since Monster's mitigation curve is already its own
        inline formula (take_damage's `rating / (rating + 100)`) rather
        than sharing Character.mitigation_from as a classmethod.
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

    def take_damage(self, amount, damage_type="physical", attacker_level=None, attacker=None):
        """Apply damage with armor/resist reduction. Returns damage taken.

        attacker_level (optional): the level of whatever dealt this damage.
        Applies the same symmetric level-difference multiplier as
        Character.take_damage, so an overleveled party actually flattens
        low-level content instead of trading evenly with it.

        attacker (optional): accepted for call-signature parity with
        Character.take_damage (combat/abilities.py calls take_damage
        uniformly across target types - Character, Monster, Pet - and
        passes attacker= for Character's absorb-shield bookkeeping). Also
        read here for attacker-side armor/spell penetration - see below.
        """
        from combat.status_effects import DamageSchool

        # Attacker penetration, matching Character.take_damage. The docstring
        # above used to say Monster "has no use for" the attacker and only
        # accepted it for call-signature parity - but armor penetration is
        # attacker-side, and a monster is what the player actually attacks, so
        # ignoring it here is precisely where the stat mattered most. Tinker's
        # Piercing Augmentation and Round Armor Pen, and every gear roll of
        # the stat, did nothing against any enemy in the game.
        def _pen_flat(name):
            return (getattr(attacker, name, 0) or 0) if attacker is not None else 0
        def _pen_pct(name):
            return (getattr(attacker, name, 0.0) or 0.0) if attacker is not None else 0.0

        # ONE CURVE FOR EVERYONE. This used to be its own inline `rating / (rating + 100)`, a
        # second copy of a formula Character already owned, and when that formula changed to scale
        # with attacker level the two would silently have disagreed - players mitigating one way
        # and the creatures they fight mitigating another. It calls the shared classmethod now.
        from entities.character import Character

        if damage_type == "physical":
            # Percentage first, then flat, floored at 0 so penetration can
            # strip armour but never grant bonus damage on its own.
            armor = max(0, int(self.armor * (1.0 - min(1.0, _pen_pct("armor_penetration_pct")))
                               - _pen_flat("armor_penetration")))
            reduction = Character.mitigation_from(armor, attacker_level)
        elif damage_type == "magic":
            mr = max(0, int(self.magic_resistance - _pen_flat("spell_penetration")))
            reduction = Character.mitigation_from(mr, attacker_level)
        elif damage_type in DamageSchool.ALL_SCHOOLS or isinstance(damage_type, (tuple, list)):
            resist = max(0, int(self.get_resistance(damage_type)
                                - _pen_flat("spell_penetration")))
            reduction = Character.mitigation_from(resist, attacker_level)
        else:
            reduction = 0

        from combat.abilities import level_diff_multiplier
        level_mult = level_diff_multiplier(attacker_level, self.level)

        # DAMAGE-TAKEN DEBUFFS DID NOTHING TO MONSTERS. This method read no
        # damage_taken_pct key of any kind, so every "the target now takes N%
        # more damage" effect in the game was inert against the only thing
        # players actually fight. 29 talent procs across 23 trees apply one of
        # these to their target - Mage Arcane alone has three - plus the
        # debuff abilities that do the same. All of them were correct in PvP
        # and silent in PvE.
        #
        # Conventions copied EXACTLY from Character.take_damage, because they
        # differ per key and a second, disagreeing copy is worse than none:
        # the bare damage_taken_pct is read UNDIVIDED (a fraction, 0.5 = +50%)
        # while every school-specific sibling is in percent POINTS and
        # divided by 100. Positive increases damage taken, matching how all
        # 29 are authored.
        taken_mult = 1.0
        if hasattr(self, "get_status_stat_mod"):
            taken_mult += self.get_status_stat_mod("damage_taken_pct")
            if damage_type == "physical":
                taken_mult += self.get_status_stat_mod("physical_damage_taken_pct") / 100.0
            else:
                taken_mult += self.get_status_stat_mod("magic_damage_taken_pct") / 100.0
                taken_mult += self.get_status_stat_mod("spell_damage_taken_pct") / 100.0
                if isinstance(damage_type, str):
                    taken_mult += self.get_status_stat_mod(
                        f"{damage_type}_damage_taken_pct") / 100.0
        taken_mult = max(0.0, taken_mult)

        actual = max(1, int(amount * (1.0 - reduction) * level_mult * taken_mult))
        self.current_health = max(0, self.current_health - actual)
        return actual

    def heal(self, amount):
        # healing_taken_pct, same as Character.heal - recipient-side, percent
        # POINTS, negative being the anti-heal that almost every real use of
        # it is. Four talent procs apply one to their target and none of them
        # reached a monster before this.
        mult = 1.0
        if hasattr(self, "get_status_stat_mod"):
            mult += self.get_status_stat_mod("healing_taken_pct") / 100.0
        self.current_health = min(self.max_health,
                                  self.current_health + amount * max(0.0, mult))

    def restore_resources_between_turns(self):
        """Mana regen so long fights don't leave a caster permanently dry
        after its opening burst. Roughly 5% of pool per turn, matching the
        'casters get a handful of spells then fall back to autoattack'
        pacing the template data was written for."""
        if self.max_mana > 0:
            self.current_mana = min(
                self.max_mana, self.current_mana + max(1, int(self.max_mana * 0.05)))

    def get_exp_reward(self):
        return int(self.exp_reward_base * (1.0 + (self.level - 1) * 0.5))

    def choose_action(self, target):
        """
        Priority AI.

        Order:
          1. Heal when badly hurt.
          2. Phase abilities (hp_below gate: enrage / desperation) the moment they unlock.
          3. Apply a DoT the target isn't carrying yet (and, for ordinary mobs, plain
             debuffs / self-buffs - see below).
          4. Damage abilities: first any with a rider whose effect has lapsed (the hit
             that re-applies the buff/debuff), otherwise the biggest hit available.
          5. Basic attack.

        Bosses never spend a turn on a pure self-buff or debuff while they have an
        attack to throw: a "glorified punching bag" was exactly a boss that burned
        a third of its turns re-casting +20 Attack Power. Their buffs/debuffs ride
        on attacks (see MonsterAbility.rider); any plain one left in a kit is only
        cast in place of the basic attack.
        """
        basic = self.abilities[0]
        options = [a for a in self.abilities[1:] if a.is_available(self)]
        boss = getattr(self, "is_boss", False)

        hurt = self.current_health < self.max_health * 0.45
        for a in options:
            if a.kind == "heal" and hurt:
                return a

        for a in options:
            if a.hp_below is not None:
                return a

        if not boss:
            for a in options:
                if a.kind == "buff" and not self.has_status_effect(a.effect_id):
                    return a

        for a in options:
            if a.kind == "dot" or (a.kind == "debuff" and not boss):
                recipient = self if a.self_only else target
                if not recipient.has_status_effect(a.effect_id):
                    return a

        damage_options = [a for a in options if a.kind == "damage"]
        if damage_options:
            lapsed = []
            for a in damage_options:
                if not a.rider:
                    continue
                recipient = self if a.rider.get("effect") == "buff" else target
                if not recipient.has_status_effect(a.rider_effect_id):
                    lapsed.append(a)
            if lapsed:
                return max(lapsed, key=lambda a: a.amount)
            return max(damage_options, key=lambda a: a.amount)

        if boss:
            for a in options:
                if a.kind in ("buff", "debuff"):
                    recipient = self if a.self_only else target
                    if not recipient.has_status_effect(a.effect_id):
                        return a

        if basic.is_available(self):
            return basic

        # SLOT 0 IS NOT ALWAYS CASTABLE, and this used to be a bare
        # `return basic`. The fallback never asked is_available, so a slot 0
        # the monster could not afford was handed to the engine anyway,
        # execute_monster_action got (False, "... unavailable") back, and the
        # turn became "Shadow Corruption hesitates." - while an affordable
        # ability was sitting off cooldown in the same kit. Slot 0 costs mana
        # in 181 of 842 kits and nothing else in the game guarantees a free
        # swing, so this is not a theoretical gap: tools/audit_monster_combat.py
        # caught Shadow Corruption doing exactly that, holding 30 mana with
        # Corrupting Bolt at 42 and Decay at 23 both on the table.
        #
        # This is the same bug the pet AI had (its fallback returned hotbar
        # slot 0 without checking it was castable, which made one pet hesitate
        # every other turn), and it is fixed the same way.
        #
        # It can only ever replace a turn that was ALREADY a guaranteed
        # hesitate - every path above returns before reaching here, and this
        # branch is entered only when slot 0 itself is unavailable - so no
        # currently-working rotation changes. The kind ordering keeps the
        # replacement sensible rather than merely non-empty: throw a hit,
        # re-apply a DoT or debuff, and only then spend the turn on a buff or
        # a heal the priority list already declined (an unhurt monster
        # "healing" to full is a wasted turn too, just a noisier one).
        FALLBACK_ORDER = {"damage": 0, "dot": 1, "debuff": 2, "buff": 3, "heal": 4}
        castable = [a for a in self.abilities if a.is_available(self)]
        if castable:
            return min(castable,
                       key=lambda a: (FALLBACK_ORDER.get(a.kind, 9), -a.amount))

        # Genuinely nothing to cast. Returning basic keeps the existing
        # contract with execute_monster_action, which logs the hesitate - that
        # is an out-of-resources monster, which is a tuning question (see the
        # NOTHING CASTABLE section of tools/audit_monster_combat.py), not
        # something the AI can route around.
        return basic

    def decrement_all_cooldowns(self):
        for ability in self.abilities:
            ability.decrement_cooldown()
