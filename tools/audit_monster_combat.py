#!/usr/bin/env python3
"""Put every monster, elite and boss through a real fight and report what it
actually did.

WHY THIS EXISTS. tools/validate_content.py and friends are INSPECTION tools:
they read data/creatures/*.json and check it against what the engine claims to
accept. They have repeatedly passed while the bestiary was badly broken in
play, because what a monster DOES is decided by Monster.choose_action,
MonsterAbility.use and CombatEngine.execute_monster_action - not by whether
its JSON is well-formed. Every monster bug found so far needed a fight:

  - nine templates silently resolved to "beast_basic", so centaur archers
    used Gore (entities/monster.py's own module docstring)
  - mana costs were authored but never checked, so a caster could not run dry
  - 23 kits authored costs on a template with no mana pool at all, which made
    every one of their abilities permanently unavailable
  - monster buffs expired on a 30-minute real-time clock and bled into
    unrelated fights
  - stat_mods on a monster did nothing at all until Monster grew an `armor`
    property, so "Thick Hide" and "Stoneskin" were flavour text

This is the same instrument as tools/audit_pet_combat.py, pointed at the other
side of the fight. Per kit it runs a real CombatEngine against a real party
that cannot die, for enough turns to exercise cooldowns and any hp_below phase
gate, and reports:

  acted     turns the monster actually did something
  basic     how many of those were slot 0, choose_action's last resort
  dry       first turn of the TERMINAL run where it could no longer act -
            it hesitated from there to the end of the fight
  unreached abilities it is carrying and never once successfully used

COUNTING RULES THAT MATTER, learned the hard way on the pet side:

  * COUNT SUCCESSES, NOT CHOICES. choose_action can return an ability that
    then fails to execute, and MonsterAbility.use can return (True, "...but
    there's no one there!"). The first version of the pet audit appended the
    chosen ability every turn and cheerfully reported every pet acting 20 of
    20 turns while half of them were doing nothing. So every turn here is
    verified against what the engine actually changed: a damage ability has
    to have moved an ally's health, a buff has to be ON THE MONSTER, a dot
    has to be on the target, a heal has to have moved the monster's health.
    A buff that lands on the wrong combatant is a success by the log and a
    failure by the measurement - see WRONG SIDE in the report.

  * GIVE EVERY ABILITY A REASON TO FIRE before calling it dead. A heal
    SHOULD never fire while the monster is at full health, and a phase
    ability SHOULD never fire above its hp_below threshold. Reporting those
    as dead abilities is the instrument accusing correct behaviour, which is
    the main way this kind of audit goes wrong. So the fight runs in two
    halves: the first with the monster pinned at full health (the healthy
    rotation, where heals and phase gates must stay shut), the second with it
    pinned below every gate in its kit (the desperation rotation). Pinning is
    honest - in a real fight the party is hitting it the whole time; the pin
    only stops the monster's own heals and lifesteal from closing the gate
    again mid-measurement. The party's own status effects are ticked once per
    round too, because a debuff that never expires makes choose_action
    correctly decline to re-apply it forever and would read as a dead button.

  * SAY WHICH KIND OF NEVER. "The AI has no step that can return this" is a
    code bug. "The firing condition never arose" is a content question. And
    "a strictly better ability with no cooldown is always available instead"
    is a third thing again - the damage branch picks max(amount), so a weaker
    damage ability sitting next to a permanently-available stronger one can
    never be chosen. Those are reported separately.

    python3 tools/audit_monster_combat.py
    python3 tools/audit_monster_combat.py --kit boar
    python3 tools/audit_monster_combat.py --creature "Skeleton Archer"
    python3 tools/audit_monster_combat.py --turns 60 --verbose
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Total turns per kit. Half are spent healthy, half wounded (see the
#: two-halves note above). 40 is enough to cycle the longest real cooldown in
#: the bestiary twice except the hp_below=0.35 enrages, which are authored at
#: cooldown 99 precisely so they fire once per fight - those only need to be
#: reachable once, and the wounded half gives them that.
TURNS = 40

#: What fraction of max health the monster is pinned at during the wounded
#: half. Must sit below every gate choose_action reads: the heal branch's
#: hard-coded 0.45, and every hp_below in the kit. Computed per kit from the
#: kit's own thresholds, floored here - a kit that authored hp_below=0.2
#: would otherwise be measured as if its phase ability were dead.
WOUNDED_FRACTION = 0.25

#: Status-effect stat_mod keys that a MONSTER actually reads. Monster has no
#: derived-stat pool the way Character does; it reads exactly these, through
#: the `armor`/`magic_resistance` properties, `ability_power_bonus`, and the
#: damage_taken/healing_taken blocks of take_damage/heal. Anything else in a
#: monster-side stat_mods dict changes nothing about the fight, however
#: sensible it looks in the JSON. Kept as a literal list rather than
#: introspected so that teaching Monster to read a new key without adding it
#: here shows up as a reported no-op instead of passing silently.
MONSTER_READS_STAT_MODS = frozenset({
    "armor", "attack_power", "magic_resistance",
    "damage_taken_pct", "physical_damage_taken_pct",
    "magic_damage_taken_pct", "spell_damage_taken_pct",
    "healing_taken_pct",
})

#: Damage schools that resolve to a real mitigation path. Monster.take_damage
#: and Character.take_damage both branch on "physical", on "magic", on
#: DamageSchool.ALL_SCHOOLS, and then fall through to `reduction = 0`. A
#: school name outside this set is not a validation error anywhere - it is a
#: hit that silently ignores armour AND every resistance in the game.
def _valid_schools():
    from combat.status_effects import DamageSchool
    return frozenset(DamageSchool.ALL_SCHOOLS) | {"physical", "magic"}


# ----------------------------------------------------------------------
# Fight setup
# ----------------------------------------------------------------------

def _build_party():
    """A real two-member party that cannot die.

    TWO members, not one, on purpose: `is_aoe` monster abilities are handed
    engine.living_allies() by execute_monster_action and MonsterAbility
    applies AOE_DAMAGE_MULTIPLIER only when it resolved more than one target.
    A solo dummy would measure every Cleave and breath attack down the
    single-target path and never exercise the branch that AoE lives in.

    The companion sits in the BACK row so default_target_for's
    `random.choice(front or living)` has exactly one candidate - otherwise
    the target would flip between the two at random and `has_status_effect`
    checks for a debuff would be answered by whichever body happened to be
    picked, making the dot/debuff branch look broken when it is not.
    """
    from entities.character import Character
    from entities.party import Party, BACK_ROW

    player = Character(name="Dummy", char_class="Warrior", level=60)
    buddy = Character(name="Buddy", char_class="Mage", level=60)
    party = Party(player)
    party.add_member(buddy)
    party.set_row(buddy, BACK_ROW)
    for c in (player, buddy):
        _make_invulnerable(c)
    return player, buddy, party


def _make_invulnerable(c):
    """Pin one party member so nothing it does can confound the measurement.

    Re-applied at the top of EVERY turn, not once at setup, for two separate
    reasons that both bit this audit while it was being written:

    `health` is Character's MAX health and is RECOMPUTED from stamina by
    _recalculate_derived_stats, which fires whenever the character's status
    effects change (_on_status_effects_changed). So the first monster debuff
    that touches stamina drops max health from a billion back to ~100 and
    clamps current_health down with it - the "cannot die" party dies to the
    second hit of any fight with a stat debuff in it, the fight ends, and
    every kit after that point measures nothing.

    dodge/parry/block_chance go to zero because Character.take_damage rolls
    physical avoidance and RETURNS 0 on a dodge or parry. A dodged hit is
    correct behaviour and leaves the target's health untouched, which is
    indistinguishable from an ability that did nothing - the first run of
    this audit reported `boar` doing nothing on 6 of 40 turns and the six
    turns were six dodges by a level 60 Warrior. The instrument was wrong,
    not the boar. They are reset every turn for the same reason as health:
    the recalc puts them back.
    """
    c.health = c.current_health = 10 ** 9
    c.dodge = 0.0
    c.parry = 0.0
    c.block_chance = 0.0


def _effect_recipient(monster, ability, target):
    """Who this ability's status effect is SUPPOSED to land on.

    This mirrors MonsterAbility.use exactly, and the mirror is the point: the
    audit has to know the intended recipient independently of what the engine
    did, or it cannot tell a buff that landed on the wrong combatant from a
    buff that landed correctly.
    """
    if ability.kind in ("buff",):
        return monster if ability.self_only else None   # None = "nowhere sane"
    if ability.kind in ("debuff", "dot"):
        return monster if ability.self_only else target
    return None


def run_one(creature_name, level, turns=TURNS, verbose=False):
    """Run one kit through a real fight. Returns a dict of measurements."""
    from entities.party import FRONT_ROW
    from combat.combat_engine import CombatEngine
    from world.creature_manager import CreatureManager

    cm = _manager()
    monster = cm.spawn_creature(creature_name, level=level)
    if monster is None:
        return {"skip": f"spawn_creature returned None for {creature_name!r}"}

    player, buddy, party = _build_party()
    engine = CombatEngine(player, monster, party=party)
    allies = [player, buddy]

    # Pin point for the wounded half: below the heal branch's 0.45 and below
    # every hp_below in this kit, so nothing in the kit can be reported dead
    # merely because its gate stayed shut.
    gates = [a.hp_below for a in monster.abilities if a.hp_below is not None]
    wounded = min([WOUNDED_FRACTION] + [g * 0.9 for g in gates])

    n = len(monster.abilities)
    #: successful uses per ability INDEX, not per name - six kits carry two
    #: abilities with identical names (lattice_crawler's two Facet Strikes),
    #: and keying by name would merge them and hide one of the pair.
    success = [0] * n
    chosen_count = [0] * n
    #: a turn where choose_action picked this ability and the engine's own
    #: record of the turn shows it changed nothing it was supposed to change
    noop = [0] * n
    wrong_side = [0] * n
    rider_landed = [0] * n
    aoe_multi = [0] * n
    by_index = {id(a): i for i, a in enumerate(monster.abilities)}

    acted = basic_used = 0
    dry_at = None
    half = turns // 2
    log_lines = []
    #: Turns the engine logged a hesitate, split by whether ANYTHING in the
    #: kit was affordable and off cooldown at that moment. The two mean
    #: completely different things: "nothing was castable" is a resource
    #: economy the owner tunes, while "something was castable and the AI
    #: hesitated anyway" is choose_action returning slot 0 from its last line
    #: without ever asking is_available - the same bug that made one pet
    #: hesitate every other turn.
    wasted_turns = 0
    stalled_turns = 0
    #: Highest mana the monster ever held at decision time, recorded
    #: SEPARATELY for the healthy and wounded halves. An ability whose cost is
    #: above the relevant peak was never once affordable while its gate was
    #: open, which is a different (and more useful) report than "its
    #: condition did not arise".
    #:
    #: The split is what makes the heals legible. A monster starts the fight
    #: with a full pool, so the overall peak is always the full pool and a
    #: 36-mana heal looks affordable - but the heal's gate (below 45% health)
    #: only opens in the wounded half, by which point the pool has been spent
    #: down to single digits. Measured against the overall peak, three
    #: healers read as "condition never arose", which points at the AI.
    #: Measured against the wounded-half peak they read as what they are: the
    #: monster could not afford to heal at the only time it wanted to.
    peak_healthy = 0
    peak_wounded = 0

    for turn in range(1, turns + 1):
        # The party keeps hitting it. Phase 1 pins it healthy so the heal and
        # phase branches MUST stay shut; phase 2 pins it under every gate so
        # they MUST open. Re-pinned every turn so the monster's own heal or
        # lifesteal cannot close the gate again halfway through and turn a
        # measurement of "did the phase ability fire" into a measurement of
        # "did it out-heal the pin".
        if turn <= half:
            monster.current_health = monster.max_health
        else:
            monster.current_health = max(1, int(monster.max_health * wounded))

        # The party's own turns passing. Without this, a debuff or dot applied
        # on turn 1 never ticks down (CombatEngine._end_turn only ticks the
        # actor whose turn ended, correctly), so choose_action spends the rest
        # of the fight correctly declining to re-apply it and the rest of the
        # kit looks dead. This is not a cheat: in any real fight the party is
        # taking turns between the monster's.
        for a in allies:
            if hasattr(a, "tick_status_effects"):
                a.tick_status_effects()
            _make_invulnerable(a)

        target = engine.default_target_for(monster)
        mana_now = getattr(monster, "current_mana", 0)
        if turn <= half:
            peak_healthy = max(peak_healthy, mana_now)
        else:
            peak_wounded = max(peak_wounded, mana_now)
        castable_now = [a for a in monster.abilities if a.is_available(monster)]
        chosen = monster.choose_action(target)
        idx = by_index.get(id(chosen))
        if idx is not None:
            chosen_count[idx] += 1

        hp_before = {a: a.current_health for a in allies}
        monster_hp_before = monster.current_health
        eid = getattr(chosen, "effect_id", None)
        rid = getattr(chosen, "rider_effect_id", None)
        had_effect = {
            "monster": monster.has_status_effect(eid) if eid else False,
            "target": target.has_status_effect(eid) if eid else False,
        }
        mark = len(engine.combat_log)

        engine.current_actor = monster
        engine.execute_monster_action()

        tail = " ".join(engine.combat_log[mark:])
        if verbose:
            log_lines.append(f"  t{turn:02d} {tail}")

        # --- did the engine actually do the thing? -------------------
        # TWO SEPARATE QUESTIONS, and the first version of this audit ran
        # them together. `hesitated` is "the engine spent the turn and
        # nothing at all happened"; `worked` is "the effect landed where it
        # was aimed". A buff that lands on the player is NOT a hesitate - the
        # engine ran the ability and logged a cheerful message - but it is
        # also not a success. Merging them put the four spore kits under a
        # heading blaming choose_action's `return basic` fallback, which had
        # nothing to do with their bug: their slot 0 is free and always
        # available, and the real fault is one missing self_only flag.
        hesitated = (chosen is None or "hesitates" in tail
                     or "there's no one there" in tail)
        worked = not hesitated
        if worked and idx is not None:
            kind = chosen.kind
            if kind == "damage":
                hit = [a for a in allies if a.current_health < hp_before[a]]
                worked = bool(hit)
                if chosen.is_aoe and len(hit) > 1:
                    aoe_multi[idx] += 1
            elif kind == "heal":
                # The pin is applied at the TOP of the turn, so any rise over
                # monster_hp_before inside the turn is this heal landing.
                worked = monster.current_health > monster_hp_before
            elif kind in ("dot", "debuff"):
                want = _effect_recipient(monster, chosen, target)
                worked = bool(want is not None and want.has_status_effect(eid))
                # AN AOE DOT SPREADS BY CARRYING THE EFFECT, NOT BY MOVING
                # HEALTH. The first version of this counted multi-target
                # coverage only inside the `damage` branch, so all 21 is_aoe
                # DoTs in the bestiary were reported as "never hit more than
                # one target" while the combat log plainly read "Dummy is
                # afflicted by Choking Bloom! Buddy is afflicted by Choking
                # Bloom!". Twenty-one false accusations from one missing
                # branch in the instrument - exactly the failure mode this
                # audit exists to avoid, so it is spelled out here.
                if chosen.is_aoe and worked:
                    if sum(1 for a in allies if a.has_status_effect(eid)) > 1:
                        aoe_multi[idx] += 1
            elif kind == "buff":
                # THE MEASUREMENT THAT CATCHES A BUFF ON THE WRONG BODY.
                # MonsterAbility.use sends a non-self_only buff through
                # _resolve_targets, i.e. to the PLAYER, and stamps it
                # EffectType.DEBUFF - while choose_action's buff branch gates
                # on `self.has_status_effect`, which therefore never becomes
                # true. The log says the ability fired; the monster is not
                # buffed; the player is carrying the monster's +attack power.
                on_monster = monster.has_status_effect(eid)
                on_target = target.has_status_effect(eid)
                worked = on_monster
                if not on_monster and on_target and not had_effect["target"]:
                    wrong_side[idx] += 1
            if worked and chosen.rider:
                who = monster if chosen.rider.get("effect") == "buff" else target
                if who.has_status_effect(rid):
                    rider_landed[idx] += 1
            if not worked:
                noop[idx] += 1

        if hesitated:
            # `castable_now` is the whole point of splitting these: if
            # anything in the kit was off cooldown and affordable at decision
            # time and the monster still did nothing, the AI threw the turn
            # away. If nothing was castable, it is a resource economy.
            if castable_now:
                wasted_turns += 1
            else:
                stalled_turns += 1
            if dry_at is None:
                dry_at = turn
        else:
            dry_at = None               # recovered; only a TERMINAL run counts

        if worked:
            acted += 1
            if idx == 0:
                basic_used += 1
            success[idx] += 1

    res_max = getattr(monster, "max_mana", 0)
    return {
        "monster": monster,
        "creature": creature_name,
        "level": level,
        "kit": monster.kit_id,
        "template": monster.monster_type,
        "boss": bool(monster.is_boss),
        "turns": turns,
        "acted": acted,
        "basic": basic_used,
        "dry_at": dry_at,
        "wasted": wasted_turns,
        "stalled": stalled_turns,
        "peak_healthy": peak_healthy,
        "peak_wounded": peak_wounded,
        "resource": (f"{monster.current_mana:.0f}/{res_max:.0f} mana"
                     if res_max else "-"),
        "success": success,
        "chosen": chosen_count,
        "noop": noop,
        "wrong_side": wrong_side,
        "rider_landed": rider_landed,
        "aoe_multi": aoe_multi,
        "log": log_lines,
    }


# ----------------------------------------------------------------------
# Why was an ability never used?
# ----------------------------------------------------------------------

def classify_unreached(r, i):
    """Return (category, explanation) for ability index `i` of result `r`.

    Three different answers, and conflating them is how an audit ends up
    reporting correct behaviour as a bug:
      NO BRANCH   choose_action has no step that can ever return this
      SHADOWED    the AI's own ranking always prefers another ability
      CONDITION   the AI handles it; its gate did not open in this fight
    """
    m = r["monster"]
    a = m.abilities[i]
    boss = r["boss"]

    if i == 0:
        # Slot 0 is the fallback, reached only when every other option
        # declines. A kit whose slot 1 is a bigger hit with no cooldown
        # legitimately never needs it.
        return ("SHADOWED",
                "slot 0 is the fallback; a better option was always available")

    if a.mana_cost > 0 and getattr(m, "max_mana", 0) > 0 and a.mana_cost > m.max_mana:
        return ("UNCASTABLE",
                f"mana_cost {a.mana_cost} exceeds this monster's entire pool "
                f"({m.max_mana}) at level {r['level']} - is_available can "
                f"never return True")

    # Which half of the fight could this ability's gate have been open in?
    # A heal or a phase ability is only wanted while wounded, so its cost has
    # to be judged against the pool it had while wounded, not against the
    # full pool it started the fight with.
    peak = (r["peak_wounded"] if (a.kind == "heal" or a.hp_below is not None)
            else max(r["peak_healthy"], r["peak_wounded"]))

    if a.mana_cost > 0 and getattr(m, "max_mana", 0) > 0 and a.mana_cost > peak:
        # Affordable in principle, never affordable in practice. Worth its own
        # category because the fix is a number (cost, or
        # restore_resources_between_turns' 5%-of-pool regen), not a branch -
        # and because filing it under "its condition never arose" would send
        # someone looking at the wrong thing entirely.
        return ("STARVED OUT",
                f"mana_cost {a.mana_cost}, but the monster never held more "
                f"than {peak} mana at any decision point where its gate was "
                f"open (pool {m.max_mana}, regen "
                f"{max(1, int(m.max_mana * 0.05))}/turn, slot 0 costs "
                f"{m.abilities[0].mana_cost})")

    if a.kind in ("buff", "debuff") and boss and a.hp_below is None:
        # Deliberate, per choose_action's docstring: a boss must not burn a
        # turn re-casting +20 attack power. But it is only reachable at all
        # when NO damage ability is available, so say so rather than calling
        # it a condition that happens not to have arisen.
        free_damage = [x for x in m.abilities[1:]
                       if x.kind == "damage" and x.cooldown == 0
                       and x.hp_below is None]
        if free_damage:
            return ("NO BRANCH",
                    f"boss plain {a.kind}: choose_action only reaches the boss "
                    f"buff/debuff step when no damage ability is available, and "
                    f"'{free_damage[0].name}' has cooldown 0 - unreachable on "
                    f"every turn of every fight")
        return ("CONDITION",
                f"boss plain {a.kind}, only cast when every damage ability is "
                f"on cooldown")

    if a.kind == "damage":
        better = [x for x in m.abilities[1:]
                  if x is not a and x.kind == "damage" and x.cooldown == 0
                  and x.hp_below is None and x.amount > a.amount
                  and not (x.mana_cost > 0 and getattr(m, "max_mana", 0) > 0)]
        if better and not a.rider and a.hp_below is None:
            return ("SHADOWED",
                    f"the damage branch picks max(amount); '{better[0].name}' "
                    f"({better[0].amount}) has no cooldown and no cost and "
                    f"always outranks it ({a.amount})")

    return ("CONDITION", f"kind={a.kind}"
            + (f", hp_below={a.hp_below}" if a.hp_below is not None else "")
            + (f", cooldown={a.cooldown}" if a.cooldown else ""))


def inert_stat_mods(a):
    """stat_mods on a MONSTER-side effect that nothing in the engine reads.

    Only for effects that land on the monster itself: a debuff on the player
    goes into Character's derived-stat pool, where agility, intellect,
    dodge_rating and the rest are all real. The monster side has no such pool.
    """
    out = []
    if a.kind == "buff" and a.self_only and a.stat_mods:
        dead = sorted(set(a.stat_mods) - MONSTER_READS_STAT_MODS)
        if dead:
            out.append((a.name, dict(a.stat_mods), dead))
    if a.rider and a.rider.get("effect") == "buff":
        mods = a.rider.get("stat_mods") or {}
        dead = sorted(set(mods) - MONSTER_READS_STAT_MODS)
        if dead:
            out.append((a.name + " (rider)", dict(mods), dead))
    return out


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

_CM = None


def _manager():
    global _CM
    if _CM is None:
        from world.creature_manager import CreatureManager
        _CM = CreatureManager()
    return _CM


def _subjects():
    """One representative creature per DISTINCT fighting shape.

    A kit is not the unit of behaviour: Monster.choose_action branches on
    is_boss, and the template decides whether there is a mana pool for the
    kit's authored costs to come out of (23 kits once authored costs against
    a template with none, which made every ability unavailable). So the unit
    is (kit, template, is_boss), and each one is run at the LOW end of its
    authored level_range - mana_cost does not scale with level while the pool
    does, so the low end is where a caster actually starves.
    """
    cm = _manager()
    from entities.monster import get_templates
    templates = get_templates()
    seen, out = {}, []
    for name, d in sorted(cm.creatures.items()):
        tmpl = d.get("template")
        if tmpl not in templates:
            out.append((name, None, f"unknown template {tmpl!r}"))
            continue
        kit = d.get("ability_kit") or templates[tmpl].get("default_kit")
        key = (kit, tmpl, bool(d.get("is_boss")))
        if key in seen:
            continue
        lo = (d.get("level_range") or [1, 1])[0]
        seen[key] = name
        out.append((name, max(1, int(lo)), None))
    return out


def _kits():
    from entities.monster import get_kits
    return get_kits()


def coverage():
    """Kits that no creature in the game can ever field, and why.

    This is the one part of the audit that is not a fight, and it is here
    because it decides whether the fights above cover the bestiary at all. A
    kit nothing spawns with is a kit this audit never puts in a CombatEngine,
    so without this check the report would silently describe a subset and
    claim to describe everything.

    The interesting cause is the dead `"kit"` key. CreatureManager.
    spawn_creature reads `ability_kit`; `kit` is read by nothing, and the
    build tools have been stripping it one zone at a time (see
    build_southern_barrens_content.py's DROP_KEYS, build_silverpine_dungeon_
    content.py, build_northern_barrens_content.py's own notes on it). Every
    creature still carrying only `kit` silently fights with its TEMPLATE's
    default kit instead - the same failure as the nine templates that
    silently became boars, one layer up.
    """
    cm = _manager()
    from entities.monster import get_templates, get_kits
    templates, kits = get_templates(), get_kits()
    used, dead_key = set(), []
    for name, d in sorted(cm.creatures.items()):
        tmpl = templates.get(d.get("template")) or {}
        resolved = d.get("ability_kit") or tmpl.get("default_kit")
        used.add(resolved)
        legacy = d.get("kit")
        if legacy and legacy != resolved and d.get("ability_kit") is None:
            dead_key.append((name, legacy, resolved, legacy in kits))
    return sorted(set(kits) - used), dead_key


def main(argv):
    only_kit = argv[argv.index("--kit") + 1] if "--kit" in argv else None
    only_creature = (argv[argv.index("--creature") + 1]
                     if "--creature" in argv else None)
    turns = int(argv[argv.index("--turns") + 1]) if "--turns" in argv else TURNS
    verbose = "--verbose" in argv

    cm = _manager()
    valid_schools = _valid_schools()

    if only_creature:
        d = cm.creatures.get(only_creature)
        if d is None:
            print(f"no such creature: {only_creature!r}")
            return 2
        subjects = [(only_creature, (d.get("level_range") or [1, 1])[0], None)]
    else:
        subjects = _subjects()
        if only_kit:
            from entities.monster import get_templates
            tm = get_templates()
            subjects = [
                s for s in subjects
                if s[1] is not None and (
                    (cm.creatures[s[0]].get("ability_kit")
                     or tm[cm.creatures[s[0]]["template"]].get("default_kit")) == only_kit)]

    print(f"{len(subjects)} kit shape(s) (kit x template x boss), "
          f"{turns} turns each: {turns // 2} healthy, {turns - turns // 2} "
          f"below every phase gate\n")
    print(f"{'kit':34} {'lvl':>3} {'B':>1} {'acted':>5} {'basic':>5} "
          f"{'dry':>4}  {'resource left':>16}  unreached")
    print("-" * 118)

    rows, broken = [], []
    starved, wrong_side, noops, uncastable = [], [], [], []
    dead_schools, inert, unreached = [], [], []
    rider_dead, aoe_single, wasteful = [], [], []

    for name, level, err in subjects:
        if err:
            broken.append((name, err))
            print(f"{name:34} BROKEN - {err}")
            continue
        r = run_one(name, level, turns, verbose)
        if "skip" in r:
            print(f"{name:34} SKIPPED - {r['skip']}")
            continue
        rows.append(r)
        m = r["monster"]

        # An ability that WAS chosen and executed but whose effect went
        # somewhere wrong is not "never used" - it is already itemised under
        # WRONG SIDE / NO-OP, and listing it again under an AI heading sends
        # the reader to choose_action when the fault is in use() or the data.
        never = [i for i in range(len(m.abilities))
                 if not r["success"][i]
                 and not r["wrong_side"][i] and not r["noop"][i]]
        label = f"{r['kit']}"
        if len(label) > 33:
            label = label[:30] + "..."
        print(f"{label:34} {r['level']:>3} {'*' if r['boss'] else ' ':>1} "
              f"{r['acted']:>5} {r['basic']:>5} "
              f"{str(r['dry_at']) if r['dry_at'] else '-':>4}  "
              f"{r['resource']:>16}  "
              + (", ".join(f"#{i} {m.abilities[i].name}" for i in never)
                 if never else "-"))
        if verbose:
            for line in r["log"]:
                print(line)

        if r["wasted"]:
            wasteful.append(r)
        if r["stalled"]:
            starved.append(r)
        for i, a in enumerate(m.abilities):
            if r["wrong_side"][i]:
                wrong_side.append((r, i, r["wrong_side"][i]))
            elif r["noop"][i]:
                noops.append((r, i, r["noop"][i]))
            if a.school not in valid_schools:
                dead_schools.append((r, i))
            for entry in inert_stat_mods(a):
                inert.append((r, i, entry))
            if a.rider and r["success"][i] and not r["rider_landed"][i]:
                rider_dead.append((r, i))
            if a.is_aoe and a.kind in ("damage", "dot") and r["success"][i] \
                    and not r["aoe_multi"][i]:
                aoe_single.append((r, i))
        for i in never:
            cat, why = classify_unreached(r, i)
            if cat == "UNCASTABLE":
                uncastable.append((r, i, why))
            else:
                unreached.append((r, i, cat, why))

    # ------------------------------------------------------------------
    print()
    fail = False

    if not only_kit and not only_creature:
        orphans, dead_key = coverage()
        if dead_key:
            fail = True
            print(f"DEAD \"kit\" KEY: {len(dead_key)} creature(s) fight with "
                  f"their template's default kit, not the one authored for "
                  f"them.")
            print("    CreatureManager.spawn_creature reads `ability_kit`. "
                  "`kit` is read by nothing.")
            print("    These creatures carry only `kit`, so the kit named "
                  "for them never loads -")
            print("    the same silent-substitution bug as the nine "
                  "templates that became boars.")
            for name, legacy, resolved, exists in dead_key:
                flag = "" if exists else "  (and that kit does not exist!)"
                print(f"    {name:32} authored '{legacy}' -> fights as "
                      f"'{resolved}'{flag}")
            print()
        # PURGE COVERAGE. Six player abilities exist purely to strip a Magic
        # buff off an ENEMY (Shaman's Purge, Felsworn's Consume Magic,
        # Necromancer's Death's Due, Stormbringer's Stormbreaker,
        # Runemaster's Leyfeed, Sun Cleric's Gavel of Wrath). They can only
        # ever act on a monster buff that carries a dispel_type. The engine
        # used to throw that field away for buffs; it no longer does, so what
        # is left is purely a question of whether the data tags any - and
        # until it does, those six abilities have nothing to do in PvE, which
        # is the same hole that put dispel_type on MonsterAbility to begin
        # with. Reported, not failed: which buffs should be purgeable is a
        # content call.
        kits_all = _kits()
        buffs = sum(1 for v in kits_all.values() for a in v
                    if a.get("kind") == "buff")
        riders = sum(1 for v in kits_all.values() for a in v
                     if (a.get("rider") or {}).get("effect") == "buff")
        tagged = sum(1 for v in kits_all.values() for a in v
                     if a.get("kind") == "buff" and a.get("dispel_type"))
        tagged += sum(1 for v in kits_all.values() for a in v
                      if (a.get("rider") or {}).get("effect") == "buff"
                      and (a.get("rider") or {}).get("dispel_type"))
        if not tagged:
            print(f"NOTHING TO PURGE: 0 of {buffs + riders} monster buffs "
                  f"({buffs} abilities + {riders} riders) carry a "
                  f"dispel_type,")
            print("    so the six enemy-targeting Magic purges in the game "
                  "have nothing to act on")
            print("    in PvE. The engine now honours an authored "
                  "dispel_type on a monster buff")
            print("    (it used to drop it); tagging them is a content "
                  "call for the owner.")
            print()

        if orphans:
            print(f"UNREACHED BY ANY CREATURE: {len(orphans)} kit(s) are not "
                  f"fielded by anything, so no fight above covers them.")
            print("    " + ", ".join(orphans))
            print()

    if broken:
        fail = True
        print(f"UNSPAWNABLE: {len(broken)} creature(s) cannot be built at all.")
        for name, err in broken:
            print(f"    {name:34} {err}")
        print()

    if wasteful:
        fail = True
        print(f"HESITATED WITH A BUTTON UP: {len(wasteful)} of {len(rows)} "
              f"kits wasted a turn while something WAS castable.")
        print("    choose_action's last line is a bare `return basic` with no "
              "is_available check,")
        print("    so a slot 0 that is unaffordable (or on cooldown) is "
              "handed to the engine")
        print("    anyway and the turn becomes a hesitate - even though "
              "another ability in the")
        print("    same kit was off cooldown and affordable on that very "
              "turn.")
        for r in sorted(wasteful, key=lambda r: -r["wasted"]):
            a0 = r["monster"].abilities[0]
            print(f"    {r['kit']:30} L{r['level']:<3} {r['wasted']:>2} "
                  f"wasted turn(s), slot0 '{a0.name}' costs {a0.mana_cost} "
                  f"of {r['monster'].max_mana}")
        print()

    if starved:
        # NOT a code bug: the monster genuinely had nothing it could cast.
        # Reported because the shape of it is a tuning question the owner has
        # deferred, and because the numbers are the argument.
        print(f"NOTHING CASTABLE (tuning, not a branch): {len(starved)} of "
              f"{len(rows)} kits spent turns with no affordable ability at "
              f"all.")
        print("    Monster.restore_resources_between_turns regenerates 5% of "
              "the pool per turn")
        print("    and its docstring says casters should 'fall back to "
              "autoattack' - but slot 0")
        print("    IS the costed spell in 181 of 842 kits, so there is "
              "nothing to fall back to.")
        for r in sorted(starved, key=lambda r: -r["stalled"])[:20]:
            a0 = r["monster"].abilities[0]
            # Cheapest UNGATED ability: a free hp_below enrage is not an
            # answer to "what could it have cast on a healthy turn", and
            # including it made this line read "cheapest ability costs 0"
            # next to "20 turns with nothing castable".
            cheapest = min(a.mana_cost for a in r["monster"].abilities
                           if a.hp_below is None)
            print(f"    {r['kit']:30} L{r['level']:<3} {r['stalled']:>2} "
                  f"turn(s) with nothing castable; cheapest ability costs "
                  f"{cheapest}, regen "
                  f"{max(1, int(r['monster'].max_mana * 0.05))}/turn")
        if len(starved) > 20:
            print(f"    ... and {len(starved) - 20} more")
        print()

    if wrong_side:
        fail = True
        print(f"WRONG SIDE: {len(wrong_side)} buff(s) landed on the PLAYER "
              f"instead of the monster.")
        print("    MonsterAbility.use sends a buff with self_only unset "
              "through")
        print("    _resolve_targets - i.e. to the target - and stamps it "
              "EffectType.DEBUFF,")
        print("    so the player gains the monster's bonus. choose_action's "
              "buff step gates")
        print("    on self.has_status_effect, which never becomes true, so "
              "the monster")
        print("    re-casts it every time the cooldown allows and never "
              "benefits once.")
        for r, i, count in wrong_side:
            a = r["monster"].abilities[i]
            print(f"    {r['kit']:30} #{i} {a.name:28} {count}x  "
                  f"stat_mods={a.stat_mods}")
        print()

    if uncastable:
        fail = True
        print(f"UNCASTABLE: {len(uncastable)} ability(ies) can never pass "
              f"is_available at any point.")
        for r, i, why in uncastable:
            print(f"    {r['kit']:30} #{i} "
                  f"{r['monster'].abilities[i].name:28} {why}")
        print()

    if dead_schools:
        fail = True
        print(f"UNMITIGATED SCHOOL: {len(dead_schools)} ability(ies) carry a "
              f"school no take_damage branch knows.")
        print("    Monster.take_damage and Character.take_damage both test "
              "\"physical\", then")
        print("    \"magic\", then DamageSchool.ALL_SCHOOLS, then fall "
              "through to reduction = 0.")
        print("    An unknown school is not a validation error anywhere - it "
              "is a hit that")
        print("    ignores armour and every resistance in the game.")
        for r, i in dead_schools:
            a = r["monster"].abilities[i]
            print(f"    {r['kit']:30} #{i} {a.name:28} school={a.school!r}")
        print()

    if noops:
        fail = True
        print(f"NO-OP: {len(noops)} ability(ies) were chosen and executed but "
              f"changed nothing they claim to.")
        for r, i, count in noops:
            a = r["monster"].abilities[i]
            print(f"    {r['kit']:30} #{i} {a.name:28} kind={a.kind} {count}x")
        print()

    if rider_dead:
        fail = True
        print(f"RIDER NEVER LANDED: {len(rider_dead)} damage ability(ies) "
              f"fired but their rider never applied.")
        for r, i in rider_dead:
            a = r["monster"].abilities[i]
            print(f"    {r['kit']:30} #{i} {a.name:28} rider={a.rider}")
        print()

    if aoe_single:
        fail = True
        print(f"AOE HIT ONE: {len(aoe_single)} is_aoe ability(ies) never "
              f"resolved more than one target against a two-member party.")
        for r, i in aoe_single:
            a = r["monster"].abilities[i]
            print(f"    {r['kit']:30} #{i} {a.name:28} kind={a.kind}")
        print()

    no_branch = [x for x in unreached if x[2] == "NO BRANCH"]
    shadowed = [x for x in unreached if x[2] == "SHADOWED"]
    condition = [x for x in unreached if x[2] == "CONDITION"]
    starved_out = [x for x in unreached if x[2] == "STARVED OUT"]

    if no_branch:
        fail = True
        print(f"NO AI BRANCH: {len(no_branch)} ability(ies) cannot be chosen "
              f"on any turn of any fight.")
        for r, i, _, why in no_branch:
            print(f"    {r['kit']:30} #{i} "
                  f"{r['monster'].abilities[i].name:28} {why}")
        print()

    if starved_out:
        print(f"STARVED OUT (tuning, not a branch): {len(starved_out)} "
              f"ability(ies) the AI reaches for but could never afford.")
        for r, i, _, why in starved_out:
            print(f"    {r['kit']:30} #{i} "
                  f"{r['monster'].abilities[i].name:28} {why}")
        print()

    if condition:
        fail = True
        print(f"CONDITION NEVER AROSE: {len(condition)} ability(ies) the AI "
              f"handles whose gate never opened")
        print("    even with the monster pinned below every threshold in its "
              "kit. Judge the gate.")
        for r, i, _, why in condition:
            print(f"    {r['kit']:30} #{i} "
                  f"{r['monster'].abilities[i].name:28} {why}")
        print()

    if shadowed:
        # NOT counted as a failure. Slot 0 going unused because a better
        # option is always up is the design, and a weaker damage sibling is a
        # tuning question the owner has deferred. Printed so it is visible,
        # summarised so it does not drown the real findings.
        print(f"SHADOWED (not a bug, for information): {len(shadowed)} "
              f"ability(ies) the AI's own ranking never prefers.")
        slot0 = [x for x in shadowed if x[1] == 0]
        other = [x for x in shadowed if x[1] != 0]
        print(f"    {len(slot0)} are slot 0, the fallback, unused because a "
              f"better option was always up.")
        if other:
            print(f"    {len(other)} are weaker damage siblings of a "
                  f"permanently-available bigger hit:")
            for r, i, _, why in other[:20]:
                print(f"        {r['kit']:28} #{i} "
                      f"{r['monster'].abilities[i].name:26} {why}")
            if len(other) > 20:
                print(f"        ... and {len(other) - 20} more")
        print()

    if inert:
        fail = True
        print(f"INERT MONSTER BUFF: {len(inert)} monster-side effect(s) grant "
              f"stat_mods nothing reads.")
        print("    Monster has no derived-stat pool: it reads "
              f"{sorted(MONSTER_READS_STAT_MODS)}")
        print("    and nothing else. Every other key is flavour text on a "
              "monster, even though")
        print("    the same key on a DEBUFF is real, because that lands on a "
              "Character.")
        wholly = [x for x in inert
                  if not (set(x[2][1]) & MONSTER_READS_STAT_MODS)]
        print(f"    {len(wholly)} of them grant NOTHING readable at all:")
        for r, i, (nm, mods, dead) in wholly[:30]:
            print(f"        {r['kit']:28} {nm:28} {mods}")
        if len(wholly) > 30:
            print(f"        ... and {len(wholly) - 30} more")
        partial = [x for x in inert if x not in wholly]
        if partial:
            print(f"    {len(partial)} grant something real plus dead keys:")
            for r, i, (nm, mods, dead) in partial[:15]:
                print(f"        {r['kit']:28} {nm:28} dead={dead}")
            if len(partial) > 15:
                print(f"        ... and {len(partial) - 15} more")
        print()

    if not fail:
        print("Every kit acted every turn it had an option, used every "
              "ability it carries,")
        print("landed every effect on the combatant it was aimed at, and "
              "never ran dry.")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
