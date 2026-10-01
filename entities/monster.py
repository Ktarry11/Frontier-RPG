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
    creatures.json "kit"  ->  template "default_kit"  ->  hard error
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
                 stat_mods=None, self_only=False, is_aoe=False):
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
        self.self_only = self_only
        # True for abilities that hit every living member of the opposing
        # side at once (Cleave, Whirlwind, Tail Sweep, Frost Nova, breath
        # attacks, ...). Previously there was no such concept at all - a
        # monster ability always hit exactly the single target passed to
        # use(), no matter how unambiguously AoE the name was.
        self.is_aoe = is_aoe

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
        if caster is not None and self.mana_cost > 0:
            if getattr(caster, "current_mana", 0) < self.mana_cost:
                return False
        return True

    def use(self, caster, target):
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
            for t in targets:
                actual = t.take_damage(amount, self.school,
                                        attacker_level=getattr(caster, "level", None))
                lines.append(f"{actual} to {t.name}")
                if first_actual is None:
                    first_actual = actual
            if self.is_aoe and len(targets) > 1:
                return True, f"{caster.name} uses {self.name} on everyone ({', '.join(lines)})!"
            return True, (f"{caster.name} uses {self.name} on "
                          f"{targets[0].name} for {first_actual} damage!")

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
        self.magic_resistance = int(template["base_magic_resist"] * level_mult)

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

    def take_damage(self, amount, damage_type="physical", attacker_level=None):
        """Apply damage with armor/resist reduction. Returns damage taken.

        attacker_level (optional): the level of whatever dealt this damage.
        Applies the same symmetric level-difference multiplier as
        Character.take_damage, so an overleveled party actually flattens
        low-level content instead of trading evenly with it.
        """
        from combat.status_effects import DamageSchool

        if damage_type == "physical":
            armor = self.armor
            reduction = armor / (armor + 100) if armor > 0 else 0
        elif damage_type == "magic":
            mr = self.magic_resistance
            reduction = mr / (mr + 100) if mr > 0 else 0
        elif damage_type in DamageSchool.ALL_SCHOOLS or isinstance(damage_type, (tuple, list)):
            resist = self.get_resistance(damage_type)
            reduction = resist / (resist + 100) if resist > 0 else 0
        else:
            reduction = 0

        from combat.abilities import level_diff_multiplier
        level_mult = level_diff_multiplier(attacker_level, self.level)

        actual = max(1, int(amount * (1.0 - reduction) * level_mult))
        self.current_health = max(0, self.current_health - actual)
        return actual

    def heal(self, amount):
        self.current_health = min(self.max_health,
                                  self.current_health + amount)

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
        Priority AI. The old version scanned abilities[1:], returned the
        first available one ONLY if it happened to be a heal at low HP, and
        otherwise fell through to the basic attack every single turn - so
        Charge, Execute, Pounce and every other special in the game were
        dead code. Monsters have literally never used their second ability.

        Order:
          1. Heal when badly hurt.
          2. Self-buff if not already running.
          3. Apply a DoT/debuff the target isn't carrying yet.
          4. Biggest affordable hit.
          5. Basic attack.
        """
        basic = self.abilities[0]
        options = [a for a in self.abilities[1:] if a.is_available(self)]

        hurt = self.current_health < self.max_health * 0.45
        for a in options:
            if a.kind == "heal" and hurt:
                return a

        for a in options:
            if a.kind == "buff" and not self.has_status_effect(a.effect_id):
                return a

        for a in options:
            if a.kind in ("dot", "debuff"):
                recipient = self if a.self_only else target
                if not recipient.has_status_effect(a.effect_id):
                    return a

        damage_options = [a for a in options if a.kind == "damage"]
        if damage_options:
            return max(damage_options, key=lambda a: a.amount)

        return basic

    def decrement_all_cooldowns(self):
        for ability in self.abilities:
            ability.decrement_cooldown()
