#!/usr/bin/env python3
"""Put every recruitable companion through a real fight and report what it actually did.

WHY THIS EXISTS, and why it is not another qa_recruits.py. tools/qa_recruits.py
is an INSPECTION tool: it reads recruits.json and checks each companion stands
on a walkable tile at a sensible level. It has never once put one in a fight.
Everything below needed a fight, a level-up or a save to actually HAPPEN:

  - four of the five tank-theme recruits were hired with an EMPTY main hand
  - no tank recruit ever got the shield GEAR_THEMES authored for it
  - fifteen execute-threshold abilities refuse on every real monster alive

The pet audit (tools/audit_pet_combat.py, read that first - this is the same
shape) exists because a pet's behaviour lives in Pet.choose_action, which no
data check can see. A recruit's situation is DIFFERENT in one way that matters
enormously, and getting it wrong is the first way this audit could lie:

    A RECRUIT IS NOT A THIRD KIND OF COMBATANT. A pet is its own class with
    its own AI; a recruit is a plain `Character` sitting in Party.members,
    and per entities/party.py the player drives its turn exactly as they
    drive their own ("The player controls every party member in combat,
    FF-style. There is NO companion AI"). So there is no choose_action to
    audit and no "the AI never picks a buff" bug to find - the equivalent
    question is whether a companion's turn, kit, resources, heals, levelling
    and save round trip work the same as the player's.

So every per-ability verdict below is measured TWICE: once on the recruit, and
once on a CONTROL - a plain Character of the same class and level built the
ordinary way. An ability the control cannot cast either is an engine-wide
fact, not a recruit bug, and is reported separately under ENGINE-WIDE. This is
the whole instrument: without the control, this tool would "find" fifteen
recruit bugs that are really one line in combat/abilities.py affecting
everybody.

WHAT IT MEASURES, per recruit:

  turns    turns the engine actually handed this companion in a shared fight
  acted    how many of those turns ended in a successful cast
  dry      first turn of the terminal run where nothing was castable - the
           companion stood there for the rest of the fight
  kit      learned abilities at the level they are hired, and at 60 after a
           REAL experience climb through Party.award_experience
  dead     learned abilities that never fired even with every gate satisfied
  gear     starter-kit slots the GEAR_THEMES table promised and did not deliver

COUNT SUCCESSES, NOT CHOICES. The pet version of this first reported every
pet acting on all twenty turns while half of them were doing nothing, because
it counted what the AI *picked*. Here the only thing that increments `acted`
is CombatEngine.execute_ability returning True.

GIVE EVERY ABILITY A REASON TO FIRE before calling it dead. A heal in a fight
where nobody is hurt SHOULD decline; so should Execute on a healthy target,
Shoot with no gun, and Mangle out of Bear Form. Reporting those as dead
abilities is this tool accusing correct behaviour, which is exactly how the
pet audit went wrong first time round. So _satisfy_gates below hurts the
party, wounds the enemy, equips the right ranged weapon, shifts the right
form, sets the right stance and plants dispel bait of every school, and the
engine's own refusal string is printed verbatim for anything still standing.

    python3 tools/audit_recruit_combat.py
    python3 tools/audit_recruit_combat.py --recruit dan_warrior
    python3 tools/audit_recruit_combat.py --turns 40 --no-climb
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TURNS = 20

#: The level the kit sweep runs at. 60, not the level the companion is hired
#: at, for the same reason the pet audit summons at 60: an ability gated to a
#: later level_req is not learned yet, so it cannot honestly be reported as
#: never-cast. Reaching 60 is itself one of the measurements - see climb().
CAP_LEVEL = 60

#: Every pool a class could spend from. Same list as
#: tools/smoke_play_all_classes.py's fill_resources; kept in both because a
#: new resource type must show up as a dry companion here rather than be
#: silently topped up by an import.
POOLS = ("rage", "energy", "static", "insanity", "combo", "life_force",
         "runes", "souls", "focus", "deathfire", "felfury",
         "archery_points", "solar_power", "vitality", "scrap")


# ----------------------------------------------------------------- plumbing

def max_hp(c):
    """Maximum health of any combatant.

    Character stores its maximum as `.health`; Pet and Monster store it as
    `.max_health`. Neither name can be assumed - entities/pet.py carries the
    same helper for the same reason, and combat/abilities.py's one remaining
    use of the Character-only name is a real bug this tool reports.
    """
    return getattr(c, "max_health", None) or getattr(c, "health", 0) or 0


def hp_frac(c):
    m = max_hp(c)
    return (c.current_health / m) if m else 1.0


def fill_resources(c):
    """Top up every pool the class could possibly spend from."""
    if getattr(c, "mana", 0):
        c.current_mana = c.mana
    for pool in POOLS:
        try:
            c.set_resource(pool, c.get_resource_max(pool))
        except Exception:                                      # noqa: BLE001
            pass


def dummy(level):
    """A target that cannot die.

    DELIBERATELY DOES NOT SET `.health`. Both existing fight tools
    (audit_pet_combat, smoke_play_all_classes) do `enemy.health =
    enemy.current_health = 10 ** 9` on their dummy, which invents an
    attribute Monster does not have - and that single line is why neither
    of them could see that every execute-threshold ability in the game
    refuses on every real monster (combat/abilities.py reads target.health,
    gets nothing, and treats the target as being at 100%). An instrument
    that patches the gap it is measuring cannot measure it.
    """
    from entities.monster import Monster
    m = Monster("Dummy", "humanoid_warrior", level=level)
    m.max_health = m.current_health = 10 ** 9
    return m


def learned(c):
    return [a for a in c.ability_book.get_all_abilities() if a.is_learned]


def cast(engine, actor, ability_id, target):
    """execute_ability, but an exception is a FINDING rather than the end of
    the run.

    A cast that raises is worse than a cast that refuses - in play it takes
    the game down mid-fight - so it has to be reported, and reporting it
    means surviving it. Found immediately: Presence of Yogg-Saron's proc
    builds a StatusEffect whose stat_mods is a string, and the twelfth
    Cultist cast of any damage spell raises AttributeError out of
    apply_status_effect.
    """
    try:
        return engine.execute_ability(actor, ability_id, target)
    except Exception as exc:                                   # noqa: BLE001
        return None, f"RAISED {type(exc).__name__}: {exc}"


def has_effect(combatant, effect_id):
    """Does this combatant already carry the effect this ability applies?

    Relies on effect_id == ability_id, which is the engine's convention for
    dot/hot/buff/debuff on a player-schema Ability - it is what makes an
    "already applied?" test possible at all, and it is what the combat
    screen's own buff-targeting uses.
    """
    effects = getattr(combatant, "_effects", None)
    if not callable(effects):
        return False
    return any(getattr(e, "effect_id", None) == effect_id for e in effects())


def resolve_target(engine, actor, ability, enemy):
    """Who this ability lands on - a copy of what the combat screen decides.

    CombatEngine.execute_ability resolves "enemy_aoe" itself and NOTHING
    else: "party", "ally" and "self" are resolved by the caller, which in
    play is ui/screens/combat_screen.py (_enter_targeting_mode and
    _resolve_target). A pet has no screen, which is why the engine grew a
    target-type branch inside execute_pet_action - and why a pet's party
    heal healed the pet until that branch existed. A companion's turn DOES
    go through the screen, so the honest thing for this audit to drive is
    the screen's resolution, not the engine's pet branch and not a single
    enemy for everything (which would make every party heal look like it
    healed nobody).
    """
    target_type = getattr(ability, "target_type", "enemy")
    if target_type == "self":
        return actor
    if target_type == "party":
        return engine.living_allies() or [actor]
    if target_type == "enemy_aoe":
        return engine.living_enemies()
    if target_type == "ally":
        allies = engine.living_allies()
        if not allies:
            return actor
        if ability.effect_type in ("heal", "hot"):
            return min(allies, key=hp_frac)
        unbuffed = [a for a in allies if not has_effect(a, ability.ability_id)]
        return min(unbuffed or allies, key=hp_frac)
    return enemy


def form_list(ability):
    """requires_form, normalised to a real list of ids.

    Several abilities author it as a bare STRING ("beetle", "spider") where
    the rest author a list. `current in "beetle"` happens to be True for the
    exact form, so the engine's gate works by accident - but iterating the
    string yields single characters, so anything that reads it as a list of
    ids (this tool included) sees six one-letter forms. Normalised here
    rather than reported as six unreachable abilities.
    """
    req = getattr(ability, "requires_form", None)
    if not req:
        return []
    if isinstance(req, str):
        return [req]
    return list(req)


# ------------------------------------------------------- reasons to fire

def _equip_ranged(actor, ability):
    """Give Shoot/Wand the weapon they ask for, if the class may hold one."""
    import json
    want = getattr(ability, "requires_ranged_weapon", None)
    if not want:
        return None
    want = [want] if isinstance(want, str) else list(want)
    data = json.loads((ROOT / "data/items/weapon_types.json").read_text())
    legal = data["class_weapon_map"].get(actor.char_class, [])
    choice = next((w for w in want if w in legal), None)
    if choice is None:
        # Not a gate the companion can ever satisfy, and not a bug: the
        # universal Shoot/Wand pair ships in every class book and the
        # weapon proficiency table decides which half a class may use.
        return f"class holds no {'/'.join(want)}"
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    template = gen.stat_templates["class_stat_template_map"].get(
        actor.char_class, "int_caster")
    item = gen.generate_weapon("ranged", choice, template,
                               max(1, actor.level - 2), "common")
    actor.add_to_inventory(item)
    actor.equip_item(item)
    return f"equipped {choice}"


def _enter_form(engine, actor, ability):
    """Shift/stance into something this ability will accept.

    Shapeshifting is a real castable ability in this engine (effect_type
    "shapeshift" - the standalone form screen was retired), and stances are
    set on whoever is acting, so a companion can reach both: this drives the
    same two paths the player's own turn uses.
    """
    wanted = set(form_list(ability))
    if not wanted:
        # SHIFT BACK BEFORE CASTING A SPELL, because the sweep runs the whole
        # book on one character and a form swaps the resource pool out: a
        # Druid left in Cat Form after the Shred test has a Mana pool of
        # zero, so the next six spells refuse with "Not enough mana" and the
        # tool blames the engine for a bear that cannot cast Healing Touch.
        # Casting the same form ability again is how a player reverts, so
        # this is the real path, not a back door.
        if getattr(actor, "current_form", None) and hasattr(actor, "revert_form"):
            actor.revert_form()
            fill_resources(actor)
            return "reverted to base form"
        return None
    current = getattr(actor, "current_form", None) or getattr(actor, "current_stance", None)
    if current in wanted:
        return None
    for shift in learned(actor):
        if shift.effect_type != "shapeshift":
            continue
        # shapeshift_form_id, NOT shapeshift_form. The JSON key is
        # "shapeshift_form" and the attribute Ability stores it in is
        # shapeshift_form_id, and reading the JSON spelling off the object
        # returns None for every form in the game - which made the first
        # run of this tool report ten Druid abilities as unreachable on a
        # class that shifts form with a hotbar button. Same class of
        # mistake as the pet audit that read the wrong attribute and
        # announced that 26 pets had no abilities.
        if getattr(shift, "shapeshift_form_id", None) in wanted:
            shift.turns_remaining = 0
            fill_resources(actor)
            ok, _msg = cast(engine, actor, shift.ability_id, actor)
            if ok:
                fill_resources(actor)    # shift_form zeroes every pool
                return f"shifted to {shift.shapeshift_form_id}"
    for stance_id in wanted:
        if hasattr(actor, "set_stance") and actor.can_use_stance(stance_id):
            ok, _msg = actor.set_stance(stance_id, free=True)
            if ok:
                return f"stance {stance_id}"
    return f"cannot reach form {sorted(wanted)}"


def _plant_dispel_bait(ability, recipients):
    """Something for a dispel to actually remove.

    An unmatched or absent school is a guaranteed no-match, so the bait is
    planted with THIS ability's own dispel_type rather than a guessed one -
    a Remove Curse that found a Magic buff would report a dead ability and
    be wrong about why.
    """
    from combat.status_effects import StatusEffect, EffectType, DispelType
    school = getattr(ability, "dispel_type", None)
    if not school:
        return None
    schools = list(school) if isinstance(school, (list, tuple)) else [school]
    planted = []
    for r in recipients:
        if not hasattr(r, "apply_status_effect"):
            continue
        for s in schools:
            try:
                dtype = s if isinstance(s, DispelType) else DispelType(str(s).lower())
            except Exception:                                  # noqa: BLE001
                continue
            r.apply_status_effect(StatusEffect(
                effect_id=f"audit_bait_{dtype.value}", name="Audit Bait",
                effect_type=EffectType.DEBUFF, duration=999,
                stat_mods={"attack_power": -1}, dispel_type=dtype,
                source_name="audit", real_time_seconds=None))
            planted.append(dtype.value)
    return f"bait {','.join(planted)}" if planted else None


def _feed_consumes_hot(engine, actor, ability, recipients):
    """Swiftmend has nothing to consume unless a HoT is already running."""
    if not getattr(ability, "consumes_hot", False):
        return None
    wanted = set(getattr(ability, "consumable_hot_ids", None) or [])
    for hot in learned(actor):
        if hot.effect_type != "hot":
            continue
        if wanted and hot.ability_id not in wanted:
            continue
        hot.turns_remaining = 0
        fill_resources(actor)
        ok, _msg = cast(engine, actor, hot.ability_id,
                        resolve_target(engine, actor, hot, None))
        if ok:
            return f"pre-cast {hot.ability_id}"
    return "no HoT available to consume"


def satisfy_gates(engine, actor, ability, enemy):
    """Clear every refusal the engine can raise that is not a bug.

    Returns a list of notes describing what had to be arranged. A note
    beginning "cannot" or "class holds no" means the gate could not be met,
    which is itself the verdict rather than a failure to report.
    """
    notes = []
    ability.turns_remaining = 0
    fill_resources(actor)

    for note in (_enter_form(engine, actor, ability),
                 _equip_ranged(actor, ability)):
        if note:
            notes.append(note)

    threshold = getattr(ability, "execute_threshold_pct", None)
    if threshold is not None and enemy is not None:
        enemy.current_health = max(1, int(max_hp(enemy) * (threshold / 200.0)))
        notes.append(f"enemy at {threshold / 2:.0f}%")

    target = resolve_target(engine, actor, ability, enemy)
    recipients = target if isinstance(target, list) else [target]
    for note in (_plant_dispel_bait(ability, recipients),
                 _feed_consumes_hot(engine, actor, ability, recipients)):
        if note:
            notes.append(note)

    ability.turns_remaining = 0
    fill_resources(actor)
    return notes


# ---------------------------------------------------------------- measures

def build_fight(subject, level, hurt=True):
    """A real party, a real engine, a target that cannot die.

    The player is a Warrior unless the subject is one, so the subject is
    never the only source of a given class's buffs, and so `living_allies()`
    has somebody other than the subject for an ally-targeted heal to prefer.
    """
    from entities.character import Character
    from entities.party import Party
    from combat.combat_engine import CombatEngine

    lead_class = "Priest" if subject.char_class == "Warrior" else "Warrior"
    lead = Character(name="Lead", char_class=lead_class, level=level)
    party = Party(lead)
    party.add_member(subject)
    enemy = dummy(level)
    engine = CombatEngine(lead, enemy, party=party)
    if hurt:
        # SOMEBODY HAS TO BE HURT or every heal and HoT in the game is
        # "correctly declined" and this tool calls them dead. Half health
        # on both, so an ally heal has a real lowest-HP pick and a self
        # heal has a reason too.
        lead.current_health = max(1, int(max_hp(lead) * 0.5))
        subject.current_health = max(1, int(max_hp(subject) * 0.5))
    return engine, lead, enemy


def kit_sweep(subject, level):
    """Can each learned ability fire at all, with every gate satisfied?

    A fresh engine per ability: a cast that lands a 3-turn debuff would
    otherwise change the conditions for the next one, and a fight that has
    drifted is not a controlled measurement.
    """
    out = {}
    for ability in learned(subject):
        engine, lead, enemy = build_fight(subject, level)
        notes = satisfy_gates(engine, subject, ability, enemy)
        target = resolve_target(engine, subject, ability, enemy)
        ok, msg = cast(engine, subject, ability.ability_id, target)
        out[ability.ability_id] = {
            "ok": ok, "msg": msg, "notes": notes,
            "effect_type": ability.effect_type,
            "target_type": ability.target_type,
        }
    return out


def heal_reach(subject, level):
    """Does a companion's heal actually land on a hurt PARTY MEMBER?

    This is the recruit-side version of the bug that made a pet's
    party-wide heal heal the pet: the engine hands a "party" ability
    whatever target the caller passed, so a heal aimed at the enemy
    degrades to the caster and the party is never touched. Measured by
    health on the LEAD, who is not the caster - nothing else proves the
    heal left the healer.
    """
    bad = []
    for ability in learned(subject):
        if ability.effect_type not in ("heal", "hot", "damage_and_heal"):
            continue
        if ability.target_type not in ("party", "ally"):
            continue
        engine, lead, enemy = build_fight(subject, level)
        satisfy_gates(engine, subject, ability, enemy)
        before_lead = lead.current_health
        before_self = subject.current_health
        target = resolve_target(engine, subject, ability, enemy)
        ok, msg = cast(engine, subject, ability.ability_id, target)
        if not ok:
            continue
        for _ in range(6):                      # let a HoT tick out
            try:
                lead.tick_status_effects()
            except Exception:                   # noqa: BLE001
                break
        if lead.current_health <= before_lead and subject.current_health <= before_self:
            bad.append((ability.ability_id, ability.target_type, msg))
    return bad


def turn_loop(subject, level, turns=TURNS):
    """Drive a real shared fight and count what the companion got done.

    Resources are NOT topped up inside the loop - the engine's own
    _end_turn -> restore_resources_between_turns is the thing under test.
    The surrogate controller stands in for the human: it prefers an
    ability it has not yet landed, so the loop explores the kit instead of
    spamming slot 0, and it only counts a turn as acted when the engine
    says the cast succeeded.
    """
    engine, lead, enemy = build_fight(subject, level)
    options = [a.ability_id for a in learned(subject)]
    landed, acted, offered, dry_at = set(), 0, 0, None
    guard = 0
    while offered < turns and guard < 400000:
        guard += 1
        # HOLD THE PARTY AT HALF HEALTH. The dummy hits back, and the first
        # version of this loop measured two turns instead of twenty because
        # the party was wiped by turn three - which would have been read as
        # a companion that stops acting partway through every fight, the
        # exact false positive this tool exists to avoid. Half health, not
        # full, so an ally heal still has somebody to prefer.
        for ally in (lead, subject):
            floor = max(1, int(max_hp(ally) * 0.5))
            if ally.current_health < floor:
                ally.current_health = floor
        engine.update(0.05)
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is not enemy and not engine.is_ally(actor):
            continue
        if actor is enemy:
            engine.execute_monster_action()
            continue
        if actor is not subject:
            # The lead's turn. Taken, not skipped: leaving it unspent would
            # stall the meter and the companion would never come round again.
            cast(engine, actor, actor.hotbar[0], enemy)
            if engine.current_actor is actor:
                engine.execute_defend(actor)
            continue

        offered += 1
        order = [a for a in options if a not in landed] + [a for a in options if a in landed]
        success = False
        for ability_id in order:
            ability = subject.ability_book.get_ability(ability_id)
            if ability is None or not ability.is_usable_by(subject):
                continue
            target = resolve_target(engine, subject, ability, enemy)
            success, _msg = cast(engine, subject, ability_id, target)
            if success:
                landed.add(ability_id)
                break
        if success:
            acted += 1
            dry_at = None               # recovered; only a terminal run counts
        else:
            if dry_at is None:
                dry_at = offered
            engine.execute_defend(subject)
        if not engine.is_active:
            break
    resource = "-"
    try:
        from combat.abilities import get_class_resource
        pool = get_class_resource(subject.char_class, subject)
        resource = (f"{subject.get_resource(pool):.0f}/"
                    f"{subject.get_resource_max(pool):.0f} "
                    f"{getattr(pool, 'value', pool)}")
    except Exception:                                          # noqa: BLE001
        pass
    return {"offered": offered, "acted": acted, "dry_at": dry_at,
            "landed": len(landed), "resource": resource,
            "lead_turns": None}


def climb(subject, to=CAP_LEVEL):
    """Level a companion the way play levels one: shared party experience.

    NOT level_up() in a loop. Party.award_experience ->
    Character.gain_experience is the only path a companion's levels ever
    come from (they cannot visit a trainer - training_enabled is False for
    everyone but the player, so their kit is purely level-based), and a
    companion that does not level on that path is a companion frozen at the
    level you found them, which is exactly what happened to pets for the
    life of the project.
    """
    from entities.character import Character
    from entities.party import Party
    from config import get_exp_needed_for_level

    lead = Character(name="Lead", char_class="Warrior", level=subject.level)
    party = Party(lead)
    party.add_member(subject)
    guard = 0
    while subject.level < to and guard < 5000:
        guard += 1
        party.award_experience(get_exp_needed_for_level(subject.level))
    return subject.level


def gear_gaps(recruit, character):
    """Slots the GEAR_THEMES table promised this companion and did not fill.

    GEAR_THEMES authors a main hand and (for tanks) an off hand per theme.
    Reported against what is actually equipped after build_character,
    because the promise and the result are not the same thing.
    """
    from world.recruit_manager import GEAR_THEMES
    theme = GEAR_THEMES.get(recruit.gear_theme)
    if not theme:
        return []
    slots = character.equipment.slots or {}
    gaps = []
    for slot in theme["slots"]:
        if not slots.get(slot):
            gaps.append(f"{slot} empty")
    for key in ("main_hand", "off_hand"):
        want = theme.get(key)
        if not want:
            continue
        item = slots.get(key)
        if item is None:
            gaps.append(f"{key} EMPTY (theme: {want})")
        elif getattr(item, "weapon_type", None) != want:
            gaps.append(f"{key} is {getattr(item, 'weapon_type', '?')} (theme: {want})")
    return gaps


def round_trip(recruit, character):
    """Everything a player would notice, through the real Party save path.

    Party.to_dict/from_dict, not Character.to_dict - the companion list,
    the bench, the rows and the shared purse only exist at the Party level,
    and tools/smoke_play_all_classes.py only ever round-trips a lone
    Character, so none of that has been measured anywhere until now.
    """
    from entities.character import Character
    from entities.party import Party

    def snap(c):
        return {
            "level": c.level, "health": round(max_hp(c)),
            "locked_spec": c.locked_spec, "recruit_id": c.recruit_id,
            "row": getattr(c, "row", None),
            "equipped": sum(1 for v in (c.equipment.slots or {}).values() if v),
            "learned": len(learned(c)),
            "hotbar": [h for h in c.hotbar if h],
            "talents_spent": sum(t.total_points_spent() for t in c.talent_trees.values()),
            "talent_points": c.talent_points_available,
            "pets": sorted(p.template_id for p in c.all_pets),
            "backstory": bool(c.backstory),
            "sections": sorted(c.background_sections or {}),
        }

    # DROP ACTIVE EFFECTS FIRST. The kit sweep casts the companion's whole
    # book, which leaves buffs running, and a buff carrying max_health_pct
    # makes max health higher than any save should record. The pet-era
    # version of this check reported twelve classes "losing health" across
    # a round trip and every one was a buff doing its job.
    character._effects().clear()
    character._recalculate_derived_stats()
    character.current_health = max_hp(character)

    lead = Character(name="Lead", char_class="Warrior", level=character.level)
    party = Party(lead)
    party.add_member(character)
    party.copper = 4242
    before = snap(character)
    restored = Party.from_dict(party.to_dict(), Character.from_dict(lead.to_dict()))
    mine = [m for m in restored.members + restored.bench
            if getattr(m, "recruit_id", None) == recruit.recruit_id]
    if not mine:
        return ["not in the save at all"]
    after = snap(mine[0])
    diffs = [f"{k}: {before[k]!r} -> {after[k]!r}" for k in before if before[k] != after[k]]
    if restored.copper != party.copper:
        diffs.append(f"copper: {party.copper} -> {restored.copper}")
    return diffs


# -------------------------------------------------------------------- main

#: A note starting with one of these means the gate could not be arranged at
#: all, so the engine's refusal is CORRECT and the ability is not dead. The
#: universal Shoot/Wand pair ships in every class book and the weapon
#: proficiency table decides which half a class may hold; a form-gated
#: ability on a class whose form is talent-locked is the same shape. Calling
#: either one "dead" is this tool accusing code that works, which is the main
#: way an audit like this goes wrong.
UNREACHABLE_GATE = ("class holds no", "cannot reach form", "no HoT available")


def verdict(ability_id, mine, control):
    """"ok" | "declined" | "engine" | "recruit" for one ability.

    declined - the gate could not be arranged, so refusing is right
    engine   - a plain Character of the same class and level cannot either
    recruit  - the control CAN, so the difference is the recruit build path
    """
    if mine["ok"]:
        return "ok"
    if any(n.startswith(UNREACHABLE_GATE) for n in mine["notes"]):
        return "declined"
    return "recruit" if control.get(ability_id, {}).get("ok", False) else "engine"


def control_for(char_class, level):
    """A plain Character of the same class and level, built the ordinary way.

    The whole point of the control: an ability this character cannot cast
    either is not a recruit bug. Training is deliberately left OFF (the
    Character default) so the only difference from the companion is the
    recruit build path itself - gear, spec lock, row - and not the
    trainer system, which companions do not use.
    """
    from entities.character import Character
    return Character(name="Control", char_class=char_class, level=level)


def run_one(recruit, turns=TURNS, do_climb=True):
    character = recruit.build_character()
    joined_level = character.level
    joined_kit = len(learned(character))
    gaps = gear_gaps(recruit, character)

    reached = climb(character) if do_climb else joined_level
    level = character.level

    sweep = kit_sweep(character, level)
    loop = turn_loop(character, level, turns)
    heals = heal_reach(character, level)
    save = round_trip(recruit, character)

    control = control_for(recruit.char_class, level)
    control_sweep = kit_sweep(control, level)

    return {
        "recruit": recruit, "character": character,
        "joined_level": joined_level, "joined_kit": joined_kit,
        "reached": reached, "kit": len(learned(character)),
        "sweep": sweep, "control": control_sweep,
        "loop": loop, "heals": heals, "save": save, "gaps": gaps,
    }


def main(argv):
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.chdir(ROOT)
    from world.recruit_manager import get_recruit_manager

    only = argv[argv.index("--recruit") + 1] if "--recruit" in argv else None
    turns = int(argv[argv.index("--turns") + 1]) if "--turns" in argv else TURNS
    do_climb = "--no-climb" not in argv

    manager = get_recruit_manager()
    items = ([(only, manager.recruits[only])] if only
             else sorted(manager.recruits.items()))

    print(f"\n{len(items)} recruit(s), {turns} turns each, "
          f"{'levelled to 60 on party XP' if do_climb else 'at the level they are hired'}\n")
    print(f"{'recruit':24} {'lvl':>5} {'kit':>7} {'turns':>6} {'acted':>6} {'dry':>5} "
          f"{'cast':>5} {'dead':>5}  {'resource left':>20}")
    print("-" * 104)

    results, engine_wide, declined = [], {}, {}
    for rid, recruit in items:
        r = run_one(recruit, turns, do_climb)
        results.append((rid, r))
        r["verdicts"] = {a: verdict(a, v, r["control"]) for a, v in r["sweep"].items()}
        for a, v in r["verdicts"].items():
            if v == "engine":
                engine_wide.setdefault(a, (rid, r["sweep"][a]))
            elif v == "declined":
                declined.setdefault(a, (rid, r["sweep"][a]))
        own = [a for a, v in r["verdicts"].items() if v == "recruit"]
        print(f"{rid:24} {r['joined_level']:>2}->{r['reached']:<2} "
              f"{r['joined_kit']:>3}->{r['kit']:<3} {r['loop']['offered']:>6} "
              f"{r['loop']['acted']:>6} "
              f"{(str(r['loop']['dry_at']) if r['loop']['dry_at'] else '-'):>5} "
              f"{r['loop']['landed']:>5} {len(own):>5}  {r['loop']['resource']:>20}")

    print()
    failures = 0

    never_acted = [(rid, r) for rid, r in results if r["loop"]["acted"] == 0]
    if never_acted:
        failures += 1
        print(f"NEVER ACTED: {len(never_acted)} companion(s) were handed turns in a real")
        print("    fight and never completed a single cast.")
        for rid, _r in never_acted:
            print(f"    {rid}")
        print()

    no_turns = [(rid, r) for rid, r in results if r["loop"]["offered"] == 0]
    if no_turns:
        failures += 1
        print(f"NO TURNS AT ALL: {len(no_turns)} companion(s) never came up on the turn")
        print("    meter - they are in Party.members and CombatEngine.combatants and")
        print("    still never act.")
        for rid, _r in no_turns:
            print(f"    {rid}")
        print()

    dry = [(rid, r["loop"]["dry_at"]) for rid, r in results if r["loop"]["dry_at"]]
    if dry:
        failures += 1
        print(f"RAN DRY: {len(dry)} of {len(results)} companions spent the rest of the")
        print("    fight unable to cast anything. Character.restore_resources_between_turns")
        print("    only refills Mana and Energy; every secondary pool is built, not")
        print("    regenerated. Check the control before calling this a companion bug -")
        print("    the player's own character runs on the same method.")
        for rid, turn in sorted(dry, key=lambda x: x[1]):
            print(f"    {rid:24} from turn {turn}")
        print()

    own_dead = [(rid, r) for rid, r in results
                if any(v == "recruit" for v in r["verdicts"].values())]
    if own_dead:
        failures += 1
        print("RECRUIT-ONLY DEAD ABILITIES: an ability the companion cannot cast and a")
        print("    plain Character of the same class and level CAN. Every gate was")
        print("    satisfied first, so this is the recruit build path, not the kit.")
        for rid, r in own_dead:
            for a, v in sorted(r["sweep"].items()):
                if r["verdicts"][a] != "recruit":
                    continue
                print(f"    {rid:22} {a:38} {v['effect_type']:14} {v['msg']}")
        print()

    bad_heals = [(rid, r["heals"]) for rid, r in results if r["heals"]]
    if bad_heals:
        failures += 1
        print("HEALS THAT REACHED NOBODY: the cast succeeded and neither the hurt party")
        print("    leader nor the caster gained any health.")
        for rid, items_ in bad_heals:
            for aid, tt, msg in items_:
                print(f"    {rid:22} {aid:38} target_type={tt}  {msg}")
        print()

    frozen = [(rid, r) for rid, r in results if do_climb and r["reached"] != CAP_LEVEL]
    if frozen:
        failures += 1
        print(f"DID NOT LEVEL: {len(frozen)} companion(s) could not climb to {CAP_LEVEL} on")
        print("    shared party experience, which is the only way a companion ever levels.")
        for rid, r in frozen:
            print(f"    {rid:24} stopped at {r['reached']}")
        print()

    lost = [(rid, r["save"]) for rid, r in results if r["save"]]
    if lost:
        failures += 1
        print("LOST ACROSS SAVE/LOAD: Party.to_dict -> Party.from_dict changed or dropped")
        print("    something a player would notice.")
        for rid, diffs in lost:
            for d in diffs:
                print(f"    {rid:22} {d}")
        print()

    gapped = [(rid, r["gaps"]) for rid, r in results if r["gaps"]]
    if gapped:
        failures += 1
        print("STARTER GEAR THE THEME PROMISED AND DID NOT DELIVER (world/recruit_manager.py")
        print("    GEAR_THEMES). An EMPTY main hand is the serious one - no weapon means no")
        print("    weapon damage, so the basic attack and every AP-scaled ability land soft.")
        for rid, gaps in gapped:
            print(f"    {rid:22} {'; '.join(gaps)}")
        print()

    if engine_wide:
        print("ENGINE-WIDE, NOT A RECRUIT BUG: the control - a plain Character of the same")
        print("    class and level - cannot cast these either, so they are reported here")
        print("    rather than against a companion. Listed once, with the first companion")
        print("    that hit it.")
        for a, (rid, v) in sorted(engine_wide.items()):
            notes = f"  [{'; '.join(v['notes'])}]" if v["notes"] else ""
            print(f"    {a:40} {v['effect_type']:14} {v['msg']}{notes}")
        print(f"    ({len(engine_wide)} abilities)")
        print()

    if declined:
        print("CORRECTLY DECLINED, counted as neither dead nor broken: the gate could not")
        print("    be arranged for this class at all, so refusing the cast is right.")
        for a, (rid, v) in sorted(declined.items()):
            print(f"    {a:40} {'; '.join(v['notes'])}")
        print(f"    ({len(declined)} abilities)")
        print()

    if not failures:
        print("Every companion took turns in a real fight, cast what it knows, healed the")
        print("party rather than itself, climbed to 60 on shared experience, came back")
        print("whole from a save, and arrived wearing what its theme promised.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
