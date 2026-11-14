#!/usr/bin/env python3
"""Cast all 1274 player abilities and check each one DID something.

WHY THIS EXISTS, and why the existing tools cannot answer it.

tools/smoke_play_all_classes.py already casts every learned ability of
every class through a real CombatEngine. It asks whether the cast
SUCCEEDED. That is a much weaker question than it looks, and this repo has
already been bitten by the gap: 113 abilities shipped with effect_value 0,
which means "apply 0% of my own stat_mods". Every one of them returned
success, logged a cheerful message, consumed its resource, started its
cooldown - and applied nothing at all. A whole session's validators passed
over them.

So this asks the harder question: after the cast, is anything different?

Per ability, matched to its effect_type:

  damage / spell_damage / ranged_damage   the target lost health
  dot / spell_dot                         a DoT landed AND ticks above 0
  heal / hot                              somebody gained health, or a HoT
                                          landed that ticks above 0
  buff / debuff                           a status effect landed AND that
                                          effect carries something real
  dispel                                  something was removed
  summon_pet                              a pet is on the field
  restore_resource                        a resource pool went up
  shapeshift                              the form changed
  reset_cooldowns                         a spent cooldown came back
  revive                                  a dead ally is standing
  enable_instant_cast                     the flag is set
  damage_and_heal                         BOTH halves happened
  damage_and_restore_mana                 BOTH halves happened

"Carries something real" is the subtle one. A buff that lands with empty
stat_mods, no proc, no absorb, no flag and no resource effect is dead data
dressed as a mechanism - the same trap as the `stunned` stat_mod that
nothing in the engine reads. But a buff whose whole job IS a proc, or a
flag like cc_immune, is perfectly healthy and carries no stat_mods, so the
test cannot simply demand stat_mods.

EVERY ABILITY IS GIVEN A REASON TO WORK before being called dead. A heal
cast on a full-health party heals nobody and is behaving correctly; an
execute cast on a healthy target is correctly refused; a dispel with
nothing to strip correctly declines. Reporting any of those as a defect is
the instrument accusing working code, which is how this kind of audit has
gone wrong eleven times in this repo. So the setup hurts the caster and the
party, puts the enemy low, and plants a dispellable effect of each school.

    python3 tools/audit_ability_effects.py
    python3 tools/audit_ability_effects.py --class Reaper
    python3 tools/audit_ability_effects.py --verbose
"""

from __future__ import annotations

import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: How many times to cast an ability before concluding it does nothing.
#: Hit chance, dodge and parry mean a single cast can legitimately produce
#: no change; eight attempts makes a run of pure misses vanishingly
#: unlikely while costing nothing on the abilities that work first try.
ATTEMPTS = 8

DAMAGE_TYPES = {"damage", "spell_damage", "ranged_damage"}
DOT_TYPES = {"dot", "spell_dot"}
HEAL_TYPES = {"heal", "hot"}


def all_classes():
    text = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    block = text.split("class_stats = {", 1)[1].split("\n        }", 1)[0]
    return re.findall(r'^\s*"([^"]+)":\s*\{\s*#?', block, re.M)


def fill_resources(c):
    if getattr(c, "mana", 0):
        c.current_mana = c.mana
    for pool in ("rage", "energy", "static", "insanity", "combo", "life_force",
                 "runes", "souls", "focus", "deathfire", "felfury",
                 "archery_points", "solar_power", "vitality", "scrap"):
        try:
            c.set_resource(pool, c.get_resource_max(pool))
        except Exception:                                      # noqa: BLE001
            pass


def drain_resources(c, ability):
    """Leave room to refuel into, while still affording the cast.

    A refuel ability has nothing to do with a full pool, so the pool has to
    come down - but draining it to ZERO makes the ability uncastable,
    because a refuel COSTS the very resource it restores. Cultist's Sanity
    Tap costs 18 Insanity, Reaper's Soul Tap 25 Souls, Stormbringer's
    Discharge 20 Static. Emptying every pool had all five of them refusing
    on all eight attempts with "Not enough <resource>" - the audit creating
    the failure it then reported.

    So each pool is set to exactly what this cast needs, plus a little, and
    no more.
    """
    cost = int(getattr(ability, "cost", 0) or 0)
    want = cost + 1
    try:
        c.current_mana = min(getattr(c, "mana", 0) or 0, want)
    except Exception:                                          # noqa: BLE001
        pass
    for pool in ("rage", "energy", "static", "insanity", "combo", "life_force",
                 "runes", "souls", "focus", "deathfire", "felfury",
                 "archery_points", "solar_power", "vitality", "scrap"):
        try:
            c.set_resource(pool, min(c.get_resource_max(pool), want))
        except Exception:                                      # noqa: BLE001
            pass


def effect_carries_something(effect):
    """Is this landed status effect a mechanism, or decoration?

    Deliberately generous. A buff whose entire job is a proc, or a single
    flag like cc_immune, is healthy and has no stat_mods - demanding
    stat_mods would report a large number of perfectly good abilities. What
    this rejects is an effect that lands carrying NOTHING: no stats, no
    proc, no absorb, no damage, no flag. That is the shape of the 113
    effect_value-0 buffs, which landed and applied nothing.
    """
    # A NON-ZERO value, not merely a non-empty dict. Druid's Thorns lands
    # carrying stat_mods {"physical_damage": 0} - the ability authors 0.03
    # and the buff branch int()s every non-_pct key, so 0.03 truncates to
    # nothing. Testing the dict for truthiness passed it, because
    # {"physical_damage": 0} is a non-empty dict. The whole point of this
    # check is substance, and a stat bonus of zero has none.
    mods = getattr(effect, "stat_mods", None) or {}
    if any(v for v in mods.values()):
        return True, "stat_mods"
    for attr in ("proc", "absorb", "absorb_remaining", "potency",
                 "is_stun", "resource_per_turn", "reflect_pct", "cc_immune"):
        if getattr(effect, attr, None):
            return True, attr
    # dispel_type and damage_school are deliberately NOT in that list.
    # Both are present on effects that do nothing else - they describe HOW
    # an effect would be removed or resisted, not what it does - so
    # accepting them would pass any empty effect that happened to carry a
    # school.
    if mods:
        return False, "stat_mods present but every value is zero"
    return False, "nothing"


def snapshot(c):
    """State worth comparing before and after a cast.

    Tolerant of WHICH combatant it is handed on purpose: the same function
    snapshots the caster, the ally and the enemy, and a Monster has no
    get_resource at all (that is Character's and Pet's generic API). The
    first version assumed it did and crashed on the enemy before a single
    ability was cast.
    """
    pools = ("mana", "rage", "energy", "focus", "combo", "souls",
             "runes", "deathfire", "felfury", "insanity", "static",
             "life_force", "solar_power", "vitality", "scrap",
             "archery_points")
    resources = {}
    if hasattr(c, "get_resource"):
        for p in pools:
            try:
                resources[p] = c.get_resource(p)
            except Exception:                                  # noqa: BLE001
                pass
    return {
        "health": c.current_health,
        "effects": {e.effect_id for e in c._effects()},
        "form": getattr(c, "current_form", None),
        "pets": len(getattr(c, "all_pets", []) or []),
        "resources": resources,
        "instant": getattr(c, "next_cast_instant", None) or getattr(
            c, "instant_cast_charges", None),
    }


def _audit_ranged(weapon_type):
    """A real Item in the Ranged slot, so a Shoot or Wand can be tested.

    These two abilities are gated on the equipped Ranged item's
    weapon_type, and most classes' starting gear has no Ranged item, so
    the first run of this audit reported universal_shoot and universal_wand
    as broken on class after class. They were refusing exactly as designed
    - Kyle's own report is why that gate exists ("my paladin without a wand
    or a gun actually just used both"). Reporting a correct refusal as a
    defect is the instrument accusing working code.

    This builds a REAL Item rather than a stub with the two or three
    attributes the first guess needed. The stub version passed the weapon
    gate and then crashed inside the damage maths on weapon_damage_max,
    which is the usual way a hand-rolled fake costs more than the real
    constructor: you discover its missing attributes one exception at a
    time, and each discovery looks like a bug in the code under test.
    """
    from entities.item import Item
    return Item(item_id=f"audit_{weapon_type}", name=f"Audit {weapon_type}",
                slot="ranged", item_level=60, rarity="common",
                weapon_type=weapon_type, weapon_damage_min=20,
                weapon_damage_max=40, attack_speed=2.0, required_level=1)


def _make_undo(fns):
    def _undo():
        for fn in reversed(fns):
            try:
                fn()
            except Exception:                                  # noqa: BLE001
                pass
    return _undo


def target_for(ability, caster, ally, enemy, party):
    """Point the ability at the kind of target the real game points it at.

    THE INSTRUMENT BUG THIS FIXES, and it is the player-side twin of a real
    engine bug fixed in the pet system the same day. `Ability._recipients`
    resolves target_type "party" and "ally" from the `target` argument it
    is handed. In play, ui/screens/combat_screen.py passes the party list
    for a party-wide ability, which is why heals work in the game. An audit
    that passes the enemy to everything therefore hands a friendly heal an
    enemy Monster as its recipient - and the heal dutifully resolves
    against it.

    Pointing everything at the enemy made 20-odd heals and dispels across
    nine classes look dead. They were not; the harness was aiming them at
    the wrong end of the fight. (The pet version of this WAS a real engine
    bug, because a pet has no screen to aim it - see
    CombatEngine.execute_pet_action.)

    A pet-targeted ability is its own case: Hunter's Mend Pet and Revive
    Pet take the pet, and a fight with no pet summoned cannot measure them
    at all.
    """
    tt = getattr(ability, "target_type", "enemy")
    aid = getattr(ability, "ability_id", "")
    if "pet" in aid and (getattr(caster, "active_pet", None) is not None):
        return caster.active_pet
    if tt == "self":
        return caster
    if tt == "ally":
        return ally if ally is not None else caster
    if tt == "party":
        members = [m for m in (getattr(party, "members", None) or [])
                   if m is not None]
        return members or [caster]
    return enemy


def satisfy_preconditions(ability, c):
    """Put the caster in a state where this ability is legal to cast.

    Returns an undo callable. Two hard gates in
    CombatEngine.execute_ability refuse a cast outright, and both are
    correct behaviour that an audit must satisfy rather than report:

      requires_form        a Druid form, a Priest form, a Warrior stance
                           or Tinker's Mechsuit. Checked against
                           current_form, current_stance and
                           current_mechsuit, so which attribute to set
                           depends on the id - "mechsuit" is a bool, the
                           rest are string ids, and setting the wrong one
                           leaves the ability still refusing.
      requires_ranged_weapon  the equipped Ranged item's weapon_type.
    """
    undo = []
    need = getattr(ability, "requires_form", None)
    if need:
        want = list(need)[0]
        if want == "mechsuit":
            prev = getattr(c, "current_mechsuit", False)
            c.current_mechsuit = True
            undo.append(lambda: setattr(c, "current_mechsuit", prev))
        else:
            prev_form = getattr(c, "current_form", None)
            prev_stance = getattr(c, "current_stance", None)
            c.current_form = want
            c.current_stance = want
            undo.append(lambda: (setattr(c, "current_form", prev_form),
                                 setattr(c, "current_stance", prev_stance)))

    need_w = getattr(ability, "requires_ranged_weapon", None)
    if need_w and hasattr(c, "equipment"):
        # PICK A TYPE THE CLASS CAN ACTUALLY WEAR. Shoot accepts four
        # weapon types (thrown/bow/gun/crossbow) and no class is
        # proficient in all four - a Warrior cannot use a bow, and a Druid
        # cannot use any of them. Equipping the first one in the list
        # bypassed the slot's proficiency rules and the damage maths then
        # produced nothing, which read as "Shoot deals no damage" on class
        # after class. It is proficiency working.
        from entities.proficiency import can_wear_weapon_type
        wanted = [need_w] if isinstance(need_w, str) else list(need_w)
        legal = [w for w in wanted if can_wear_weapon_type(c.char_class, w)]
        if legal:
            prev_item = c.equipment.slots.get("ranged")
            c.equipment.slots["ranged"] = _audit_ranged(legal[0])
            undo.append(lambda: c.equipment.slots.__setitem__("ranged", prev_item))
        else:
            # Nothing this class may wear satisfies the gate, so the
            # ability is uncastable by this class in play. That is a real
            # observation about the ability's placement, not a defect in
            # the ability, so it is reported as its own category rather
            # than as "changed nothing".
            undo.append(lambda: None)
            return _make_undo(undo), (
                f"{c.char_class} has no proficiency for any of "
                f"{', '.join(wanted)}, so this is uncastable in play")

    return _make_undo(undo), None


def apply_bait(c, ally, enemy):
    """Plant something dispellable of every school on every combatant.

    RE-APPLIED BEFORE EVERY ATTEMPT, not once per fight. The retry loop
    clears each combatant's effect list between attempts so that one
    cast's leftovers cannot be mistaken for the next cast's work - and
    that clear also wiped the bait. The first ability whose first attempt
    failed therefore stripped the bait for the whole rest of the run, and
    every dispel after it reported "removed nothing" however well it
    worked. Paladin's Cleanse was in that list while visibly removing a
    poison from the ally when called by hand.

    Both shapes go on the enemy: a DEBUFF for a friendly-style dispel and
    a BUFF for an offensive one (Dispel Magic, Purge), since which half of
    a dispel is under test depends on the shape of the bait rather than on
    the ability.
    """
    from combat.status_effects import StatusEffect, EffectType, DispelType
    for school in (DispelType.MAGIC, DispelType.CURSE,
                   DispelType.POISON, DispelType.DISEASE):
        name = getattr(school, "value", school)
        for who, shape, sign, prefix in (
                (enemy, EffectType.DEBUFF, -1, "bait"),
                (enemy, EffectType.BUFF, 1, "bait_buff"),
                (c, EffectType.DEBUFF, -1, "self_bait"),
                (ally, EffectType.DEBUFF, -1, "ally_bait")):
            if who is None:
                continue
            who.apply_status_effect(StatusEffect(
                effect_id=f"{prefix}_{name}", name=f"Bait {name}",
                effect_type=shape, duration=999,
                stat_mods={"attack_power": sign}, dispel_type=school,
                source_name="audit", real_time_seconds=None))


def build_fight(cls, level=60):
    """A character and a fight set up so every effect_type has a reason to
    work: the caster and an ally are hurt, the enemy is low enough for an
    execute, and the enemy carries one dispellable effect of each school."""
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat.abilities import get_class_abilities
    from combat.status_effects import StatusEffect, EffectType, DispelType
    import entities.starting_gear as starting_gear

    c = Character(name="Caster", char_class=cls, level=level)
    starting_gear.grant_starting_gear(c)
    c.ability_book = get_class_abilities(cls)
    for _ in range(level - 1):
        c.level_up()
    for tree in c.talent_trees.values():
        for node in tree.nodes.values():
            node.points_spent = node.max_points
    c._recalculate_derived_stats()

    ally = Character(name="Ally", char_class="Warrior", level=level)
    party = Party(c)
    try:
        party.add_member(ally)
    except Exception:                                          # noqa: BLE001
        ally = None

    enemy = Monster("Dummy", "humanoid_warrior", level=level)
    enemy.health = enemy.current_health = 10 ** 7
    engine = CombatEngine(c, enemy, party=party)

    # A PET ON THE FIELD, for the classes that have one. Hunter's Mend Pet
    # and Revive Pet take the pet as their target, so a fight with no pet
    # cannot measure them and reports both as dead. Summoned from the
    # class's own first summon ability rather than a hardcoded template, so
    # this keeps working as the roster changes.
    import json as _json
    apath = ROOT / f"data/abilities/{cls.lower().replace(' ', '_')}.json"
    if apath.exists():
        for entry in _json.loads(apath.read_text(encoding="utf-8")).get("abilities", []):
            tmpl = entry.get("summon_pet_template")
            if tmpl:
                try:
                    c.summon_pet(tmpl)
                except Exception:                              # noqa: BLE001
                    pass
                break

    apply_bait(c, ally, enemy)
    return c, ally, enemy, engine, party


def verdict(ability, before, after, enemy_before, enemy_after,
            ally_before, ally_after, caster, enemy, pet_before=None,
            pet_after=None, ally=None):
    """Did this cast change anything appropriate to its effect_type?

    Returns (ok, why). `why` names the observation on a pass so the
    instrument itself can be audited - a pass for the wrong reason is worth
    as much as a false failure.
    """
    et = ability.effect_type
    new_on_caster = after["effects"] - before["effects"]
    new_on_enemy = enemy_after["effects"] - enemy_before["effects"]
    new_on_ally = ((ally_after["effects"] - ally_before["effects"])
                   if ally_before else set())

    def dot_ticks(owner, ids):
        for e in owner._effects():
            if e.effect_id in ids and getattr(e, "potency", 0):
                return True
        return False

    if et in DAMAGE_TYPES:
        if enemy_after["health"] < enemy_before["health"]:
            return True, "target lost health"
        return False, "target lost no health"

    if et in DOT_TYPES:
        if new_on_enemy and dot_ticks(enemy, new_on_enemy):
            return True, "DoT landed and ticks"
        if enemy_after["health"] < enemy_before["health"]:
            return True, "dealt damage"
        if new_on_enemy:
            return False, "DoT landed but ticks for 0"
        return False, "no DoT applied"

    if et in HEAL_TYPES:
        # A pet heal shows up on the PET, not on the caster or the party -
        # Hunter's Mend Pet and Revive Pet are the whole reason this third
        # list exists.
        pet_healed = any(b < a for b, a in zip(pet_before or [], pet_after or []))
        healed = (after["health"] > before["health"]
                  or pet_healed
                  or (ally_after and ally_after["health"] > ally_before["health"]))
        if healed:
            return True, "somebody gained health"
        # CHECK THE OWNER THE EFFECT LANDED ON, not always the caster. A
        # heal authored target_type "ally" or "party" is aimed at the ally
        # by target_for, so its HoT is on the ALLY's effect list - looking
        # for its potency on the caster finds nothing and reads as a HoT
        # ticking for 0. Rejuvenation and Regrowth were reported that way
        # while visibly healing 16 and 23 per turn.
        owners = [(caster, new_on_caster)]
        if ally is not None:
            owners.append((ally, new_on_ally))
        # And the pet, for Mend Pet: its HoT lands on the PET, so a scan of
        # the caster and the party finds nothing and calls it dead.
        for p in (getattr(caster, "all_pets", None) or []):
            owners.append((p, {e.effect_id for e in p._effects()}))
        landed_any = False
        for owner, landed in owners:
            if not landed or owner is None:
                continue
            landed_any = True
            if dot_ticks(owner, landed):
                return True, "HoT landed and ticks"
        if landed_any:
            return False, "HoT landed but ticks for 0"
        return False, "nobody healed and no HoT applied"

    if et in ("buff", "debuff"):
        # SCAN WHOEVER ACTUALLY RECEIVED IT. Pairing "what is new" with a
        # fixed owner - caster for a buff, enemy for a debuff - was wrong
        # for every ability authored target_type "ally" or "party", which
        # is most of the support kit. Those land on the ALLY, so the new
        # effect id was found on the ally while the carries-something test
        # read the caster's list, found nothing, and reported the ability
        # as landing empty. Power Word: Shield (absorb 126 plus armor and
        # magic resistance), Barbarian's Cheers and Chronomancer's Hasten
        # were all reported that way while plainly working.
        candidates = [(caster, new_on_caster), (enemy, new_on_enemy)]
        if ally is not None:
            candidates.append((ally, new_on_ally))
        landed = set()
        owner = caster
        for cand_owner, cand_landed in candidates:
            if cand_landed:
                owner, landed = cand_owner, cand_landed
                break
        if not landed:
            # Some buffs do their whole job immediately rather than by
            # lasting - a resource grant, a cooldown reset, a form change.
            if after["resources"] != before["resources"]:
                return True, "changed a resource immediately"
            if after["form"] != before["form"]:
                return True, "changed form"
            if after["pets"] != before["pets"]:
                return True, "summoned something"
            return False, "no status effect applied"
        for e in owner._effects():
            if e.effect_id in landed:
                ok, why = effect_carries_something(e)
                if ok:
                    return True, f"effect landed carrying {why}"
        return False, "effect landed carrying nothing"

    if et == "dispel":
        # COUNT ONLY THE BAIT, not any effect that happened to vanish.
        # Diffing the whole effect list made this check worthless: the
        # cast ends the actor's turn, that turn-end expires whatever was
        # due to expire, and the diff counted those as "removed". Templar's
        # Testament of Will passed on "removed an effect" while logging
        # "A has no Movement effect to remove!" and stripping nothing - a
        # false PASS, which is worse than a false failure because it hides
        # a real bug instead of wasting time on a non-bug.
        #
        # The bait is planted with duration 999 and nothing else touches
        # it, so a bait id disappearing can only mean a dispel took it.
        def bait_ids(snap):
            return {e for e in snap["effects"]
                    if e.startswith(("bait_", "self_bait_", "ally_bait_"))}

        removed = bait_ids(enemy_before) - bait_ids(enemy_after)
        removed |= bait_ids(before) - bait_ids(after)
        if ally_before and ally_after:
            removed |= bait_ids(ally_before) - bait_ids(ally_after)
        if removed:
            return True, f"removed bait ({', '.join(sorted(removed))})"
        return False, "removed nothing (bait of all 4 schools was present)"

    if et == "summon_pet":
        if after["pets"] > before["pets"] or after["pets"] > 0:
            return True, "a pet is on the field"
        return False, "no pet summoned"

    if et in ("restore_resource", "damage_and_restore_mana"):
        gained = any(after["resources"][k] > before["resources"][k]
                     for k in before["resources"])
        if et == "damage_and_restore_mana":
            dealt = enemy_after["health"] < enemy_before["health"]
            if dealt and gained:
                return True, "dealt damage and restored a resource"
            if not dealt:
                return False, "restored but dealt no damage"
            return False, "dealt damage but restored nothing"
        if gained:
            return True, "a resource went up"
        # The pools were drained to zero before this cast (see
        # drain_resources), so there is nowhere for "already full" to hide:
        # a refuel that moves nothing really moves nothing.
        return False, "restored nothing from an empty pool"

    if et == "damage_and_heal":
        dealt = enemy_after["health"] < enemy_before["health"]
        healed = (after["health"] > before["health"]
                  or (ally_after and ally_after["health"] > ally_before["health"]))
        if dealt and healed:
            return True, "dealt damage and healed"
        if dealt:
            return False, "dealt damage but healed nobody"
        return False, "dealt no damage"

    if et == "shapeshift":
        if after["form"] != before["form"]:
            return True, "form changed"
        return False, "form unchanged"

    if et == "enable_instant_cast":
        if after["instant"] != before["instant"]:
            return True, "instant-cast state changed"
        return False, "instant-cast state unchanged"

    if et == "reset_cooldowns":
        return None, "verified separately"

    if et == "revive":
        return None, "needs a dead ally - verified separately"

    if et == "totem_loadout":
        return None, "totem loadout - verified separately"

    return None, f"no check written for effect_type {et!r}"


def audit_class(cls, verbose=False):
    findings, passes, skipped = [], [], []
    try:
        c, ally, enemy, engine, party = build_fight(cls)
    except Exception as exc:                                   # noqa: BLE001
        return [(cls, "<setup>", f"{type(exc).__name__}: {exc}",
                 traceback.format_exc(limit=3))], [], []

    abilities = [a for a in c.ability_book.get_all_abilities() if a.is_learned]
    base_form = getattr(c, "current_form", None)
    base_stance = getattr(c, "current_stance", None)
    for ability in abilities:
        # TRY MORE THAN ONCE. A damage ability can legitimately MISS - hit
        # chance, dodge and parry are all live - so one cast dealing no
        # damage proves nothing. The first version of this audit used one
        # cast and reported Druid's basic Attack as dealing no damage; cast
        # three times by hand it dealt 21, 23 and 43. Anything that can
        # fail by a dice roll needs several attempts before it is called
        # dead, and passing on the FIRST success keeps the common case
        # cheap.
        res = why = None
        last_refusal = None
        for attempt in range(ATTEMPTS):
            # Fresh-ish state, with a REASON for every kind of ability to work.
            c.current_health = max(1, int(c.health * 0.4))
            if ally is not None:
                ally.current_health = max(1, int(ally.health * 0.4))
            enemy.current_health = int(enemy.health * 0.10)  # low, so executes fire
            for pet in (getattr(c, "all_pets", None) or []):
                pet.current_health = max(1, int(pet.max_health * 0.4))

            # RESET THE FORM EVERY TIME. A shapeshift ability's whole job is
            # to change form and it is not undone by satisfy_preconditions,
            # so without this the first shapeshift in the list leaks into
            # every later cast: once a Druid went into Bear, the rest of its
            # casts were measured in Bear form, where the mana pool is not
            # the caster's. That reported Starfire, Healing Touch, Regrowth,
            # Thorns and Entangling Roots as "Not enough mana" on a Druid
            # whose mana had been topped up a line earlier - five correct
            # refusals presented as five bugs.
            c.current_form = base_form
            c.current_stance = base_stance
            # AND RECALCULATE, or the reset is half a reset. Mana is a
            # DERIVED stat: a Druid in Bear form has c.mana == 0, so putting
            # current_form back to None without recalculating leaves the
            # maximum at 0, and fill_resources below is guarded on
            # `if getattr(c, "mana", 0)` and therefore fills nothing. Once
            # the form reset was added without this line it broke Cat Form,
            # which had been passing. Resetting half of a derived chain is
            # worse than not resetting it.
            c._recalculate_derived_stats()
            fill_resources(c)
            apply_bait(c, ally, enemy)

            # A JUDGEMENT NEEDS A SEAL. Paladin's Judgement carries
            # consumes_seal, and Ability._apply_effect routes it to
            # _apply_judgement_effect, which has nothing to consume unless
            # a Seal is already running - so it was reported as dealing no
            # damage while behaving exactly as designed. Put one up first.
            if getattr(ability, "consumes_seal", False):
                for other in c.ability_book.get_all_abilities():
                    if (other.is_learned
                            and getattr(other, "exclusive_group", None)
                            and "seal" in str(other.exclusive_group)):
                        other.turns_remaining = 0
                        try:
                            other.use(c, c, party=[c], engine=engine)
                        except Exception:                      # noqa: BLE001
                            pass
                        break

            # A REFUEL NEEDS AN EMPTY TANK. restore_resource abilities had
            # nowhere to restore into, because the line above had just
            # topped every pool up - so all 23 of them reported "resources
            # were already full" and were never actually verified. Drain the
            # class's own pool first and the ability has a job to do.
            if ability.effect_type in ("restore_resource",
                                       "damage_and_restore_mana"):
                drain_resources(c, ability)

            ability.turns_remaining = 0
            restore, uncastable = satisfy_preconditions(ability, c)
            if uncastable:
                restore()
                res, why = None, uncastable
                break

            before = snapshot(c)
            enemy_before = snapshot(enemy) if hasattr(enemy, "_effects") else None
            ally_before = snapshot(ally) if ally is not None else None
            pet_before = [p.current_health
                          for p in (getattr(c, "all_pets", None) or [])]
            try:
                ok, msg = engine.execute_ability(
                    c, ability.ability_id,
                    target_for(ability, c, ally, enemy, party))
            except Exception as exc:                           # noqa: BLE001
                restore()
                res, why = False, f"RAISED {type(exc).__name__}: {exc}"
                break
            if not ok:
                restore()
                last_refusal = msg
                res, why = False, f"refused with everything in its favour: {msg}"
                continue
            after = snapshot(c)
            enemy_after = snapshot(enemy)
            ally_after = snapshot(ally) if ally is not None else None
            restore()
            pet_after = [p.current_health
                         for p in (getattr(c, "all_pets", None) or [])]
            res, why = verdict(ability, before, after, enemy_before,
                               enemy_after, ally_before, ally_after, c, enemy,
                               pet_before, pet_after, ally)
            if res is not False:
                break
            # Clear what this cast left behind, so the next attempt's
            # "what is new" comparison is not fooled by its own leftovers.
            try:
                c._effects().clear()
                enemy._effects().clear()
                if ally is not None:
                    ally._effects().clear()
            except Exception:                                  # noqa: BLE001
                pass
        if res is False and last_refusal and ATTEMPTS > 1:
            why = (f"refused on every one of {ATTEMPTS} attempts with "
                   f"everything in its favour: {last_refusal}")
        if res is True:
            passes.append((cls, ability.ability_id, why))
        elif res is False:
            findings.append((cls, ability.ability_id,
                             f"{ability.effect_type}: {why}", None))
        else:
            skipped.append((cls, ability.ability_id, why))
    return findings, passes, skipped


def main(argv):
    only = argv[argv.index("--class") + 1] if "--class" in argv else None
    verbose = "--verbose" in argv
    classes = [only] if only else all_classes()

    print(f"Casting every learned ability of {len(classes)} class(es) at 60 "
          f"and checking each one changed something.\n")
    all_f, all_p, all_s = [], [], []
    for cls in classes:
        f, p, s = audit_class(cls, verbose)
        all_f += f
        all_p += p
        all_s += s
        flag = "FAIL" if f else "ok  "
        print(f"  {flag}  {cls:20} {len(p):>4} did something, "
              f"{len(f):>3} did not, {len(s):>3} not checked here")

    print(f"\n{len(all_p)} abilities verified to change something.")
    print(f"{len(all_s)} not checked by this tool (see --verbose).")
    if all_f:
        print(f"\n{len(all_f)} ABILITY(IES) EXECUTED SUCCESSFULLY AND CHANGED "
              f"NOTHING:\n")
        by_cls = {}
        for cls, aid, why, tb in all_f:
            by_cls.setdefault(cls, []).append((aid, why, tb))
        for cls, rows in sorted(by_cls.items()):
            print(f"=== {cls}")
            for aid, why, tb in rows:
                print(f"    {aid:44} {why}")
                if tb and verbose:
                    print(tb)
        print("\nAn ability that returns success, spends its resource, starts")
        print("its cooldown and applies nothing is the exact shape of the 113")
        print("effect_value-0 buffs this repo shipped. Check effect_value is")
        print("100, then check the units table before changing a number:")
        print("claude/value_conventions_and_dead_data_2026_10_29.md")
    if verbose and all_s:
        print(f"\nNOT CHECKED HERE ({len(all_s)}):")
        for cls, aid, why in all_s:
            print(f"    {cls:18} {aid:44} {why}")
    return 1 if all_f else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
