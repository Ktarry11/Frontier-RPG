#!/usr/bin/env python3
"""Validate a playable class end to end: abilities, talent trees, wiring, combat.

    PYTHONPATH=. python3 tools/validate_class.py guardian
    PYTHONPATH=. python3 tools/validate_class.py --all

WHY THIS EXISTS. Thirteen CoA classes are being authored at once, and the
single most expensive mistake available is authoring a key the engine never
reads. It produces a class that loads, creates, levels and fights, and is
quietly missing a third of its talents. That has already happened twice in
this codebase:

  - All 15 threat talents across 11 specs used threat_generation_pct while
    combat_engine read threat_multiplier. Every threat talent in the game,
    including Warrior Protection's Defiance, did nothing. Fixed 2026-10-28.
  - A whole sweep of class balance was invalidated by a hand-written list of
    effect_types that omitted spell_damage and spell_dot, so every caster
    fought with its basic attack.

So this tool does not carry a hand-maintained vocabulary. It DERIVES the live
effect-key set by scanning the engine for the patterns that actually read
talent effects, and it derives effect_type from the ability code. If the
engine changes, this tool changes with it. A key not in the derived set is
reported as dead, because that is what it is.

It also refuses to pass a class on static checks alone. A class must build a
real Character, learn abilities at 1/20/40/60, spend a full talent budget, and
land damage or healing in a real CombatEngine fight. Reading values back out
of the talent dict is how both bugs above stayed hidden; the dict agrees with
whatever you put in it.

EXIT CODE is the number of ERRORs (0 = pass). Warnings never fail the build.
"""
import argparse
import json
import re
import sys
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------- vocabularies

def live_talent_effect_keys():
    """Delegate to tools/audit_talents.py - do NOT reimplement this.

    This function used to be a hand-rolled scan, and writing it was a
    lesson. tools/audit_talents.py already answers "is this effect key
    live?" and answers it better, because it knows the families the engine
    builds at RUNTIME, which no scan of literals can see:

      <target>_from_<source>_pct   stat conversions, resolved against the
                                   shared STAT_CONVERSION_TARGETS/SOURCES
                                   maps that live in character.py precisely
                                   so two tools cannot drift
      <school>_spell_damage etc    assembled as f"{school}_spell_damage"
      scale_talent_key keys        looked up by name at proc time
      *_max resource caps          and a short named-live set

    Reimplementing it reported 60 errors against 17 shipped, working
    classes - every stat conversion, every school damage key, static_max,
    exposed_flesh_rage_pct - and every one of those was a FALSE DEAD. The
    audit tool's own docstring says a previous false verdict destroyed a
    working talent. One source of truth, imported, not copied.
    """
    sys.path.insert(0, str(ROOT / "tools"))
    import audit_talents
    live = audit_talents.live_effect_keys() | audit_talents.scale_talent_keys()
    return live, audit_talents


def key_is_live(key, live, audit):
    """True if the engine can read `key` - literal, or a runtime family."""
    if key in live:
        return True
    if audit._is_live_stat_conversion(key):
        return True
    if audit._is_live_school_key(key):
        return True
    if key in audit._NAMED_LIVE:
        return True
    if audit.SCALE_RE.match(key) if hasattr(audit, "SCALE_RE") else False:
        return True
    return False


def engine_string_literals():
    """Kept as a thin alias so call sites read clearly."""
    live, _audit = live_talent_effect_keys()
    return live


def live_effect_types(literals):
    """effect_type values the ability engine can act on.

    Same blunt rule as the effect keys, intersected with what is actually
    authored, so a stray literal elsewhere in the engine cannot invent an
    effect_type that no ability uses.
    """
    authored = set()
    for path in (ROOT / "data/abilities").glob("*.json"):
        doc = json.loads(path.read_text())
        for ability in doc.get("abilities", []):
            authored.add(ability.get("effect_type"))
    return {e for e in authored if e and e in literals}


def effect_key_conventions(exclude_slug=None):
    """Per-key value distribution across every authored tree.

    THE CHECK THIS TOOL WAS MISSING. Key liveness is not enough: a live key
    with a value in the wrong convention is worse than a dead one, because
    it works and it is wrong. Conventions in this codebase differ PER KEY
    with no naming rule to tell you which is which -

        max_health_pct      FRACTION   0.02  means +2%   (health * (1 + v))
        armor_pct           PERCENT    2.0   means +2%
        damage_taken_pct    FRACTION  -0.02  means -2%
        block               PERCENT    3.0   means +3 percentage points

    - so "_pct" tells you nothing. Guardian shipped with max_health_pct at
    2.0 instead of 0.02, i.e. +200% health per rank. Iron Guardian and
    Resilient together gave +1600%, the spec reached 26,700 health and
    99,156 effective HP against the next tank's 2,987, and survived 177
    turns against 4 to 10. The validator passed it with 0 errors and 0
    warnings, because every key was live and every structure was correct.
    The balance sim caught it.

    So: compare each value against what the SHIPPED trees already use for
    that key. This is empirical rather than a hand-maintained table, for the
    same reason liveness is - a second copy of the conventions would drift.
    """
    ref = defaultdict(list)
    for path in (ROOT / "data/talents").glob("*.json"):
        if exclude_slug and path.stem.startswith(exclude_slug + "_"):
            continue
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        for node in doc.get("nodes", []):
            points = node.get("max_points", 1) or 1
            for key, value in (node.get("effects") or {}).items():
                if isinstance(value, (int, float)) and key != "unlock_ability":
                    # TOTAL contribution at full ranks, not the per-rank
                    # value. A 1-point node legitimately carries several
                    # times a 5-rank node's per-rank number - CoA's Bulwark
                    # is a single point of "+25% block value", which is the
                    # same total as a 5-rank node at 0.05 and was flagged as
                    # "8x too big" against per-rank values. Totals still
                    # catch an order-of-magnitude slip: Guardian's
                    # max_health_pct 2.0 over 5 ranks is 10.0 against a
                    # shipped 0.1, which is 100x either way.
                    ref[key].append(abs(value) * points)
    return ref


#: How far out of the shipped range a value has to be before it is an error
#: rather than a note. 8x is deliberately loose: a capstone legitimately
#: hits several times a per-rank talent's value, and the failure this is
#: hunting is an order-of-magnitude convention slip (100x, 114x), not a
#: designer choosing a big number on purpose.
MAGNITUDE_FACTOR = 8


def check_magnitudes(slug, report, conventions):
    """Flag talent values an order of magnitude off the shipped convention."""
    prefix = slug.replace("-", "_")
    for path in sorted(ROOT.glob(f"data/talents/{prefix}_*.json")):
        doc = json.loads(path.read_text())
        for node in doc.get("nodes", []):
            points = node.get("max_points", 1) or 1
            for key, value in (node.get("effects") or {}).items():
                if not isinstance(value, (int, float)) or key == "unlock_ability":
                    continue
                seen = conventions.get(key)
                if not seen:
                    continue            # no precedent: nothing to compare to
                median = statistics.median(seen)
                if not median:
                    continue
                ratio = abs(value) * points / median
                if ratio >= MAGNITUDE_FACTOR or ratio <= 1 / MAGNITUDE_FACTOR:
                    direction = "TOO BIG" if ratio >= 1 else "too small"
                    report.error(
                        f"{path.stem}/{node.get('name')}: {key}={value} over "
                        f"{points} rank(s) totals {abs(value) * points:g}, "
                        f"{max(ratio, 1/ratio):.0f}x {direction} - every other "
                        f"tree totals {min(seen):g} to {max(seen):g} (median "
                        f"{median:g}). Check whether this key wants a FRACTION "
                        f"or PERCENT POINTS.")


def proc_payload_keys():
    """Payload keys the PROC HANDLER reads, scanned out of status_effects.py.

    This used to be derived from the authored trees, which made it circular:
    it approved any payload simply because somebody had written it. That is
    how `damage_flat` passed - authored on six nodes, read by nothing, so
    every retaliation talent in the game dealt zero damage, Guardian's
    included, and the validator said 0 errors. (damage_flat is implemented
    now; the check is fixed so the NEXT one does not slip through.)

    Hand-listing them was the previous failure in the other direction - 9
    false warnings against shipped Warrior and Warlock trees - so this reads
    the handler itself: every proc.get("...") in combat/status_effects.py.
    """
    text = (ROOT / "combat/status_effects.py").read_text(encoding="utf-8",
                                                         errors="ignore")
    keys = set(re.findall(r'proc\.get\(\s*[\'"]([a-z_]+)[\'"]', text))
    return keys - {"trigger", "chance", "icd"}


def proc_triggers():
    """Derived from ProcTrigger.ALL, never hand-listed.

    A hardcoded copy went stale the moment the engine gained the avoidance
    triggers (on_dodge/on_parry/on_avoid/on_block) and would have failed
    every talent that used them.
    """
    from combat.status_effects import ProcTrigger
    return set(ProcTrigger.ALL)


PROC_TRIGGERS = proc_triggers()
NODE_TYPES = {"passive", "active"}


# ------------------------------------------------------------------- reporting

class Report:
    def __init__(self, label):
        self.label = label
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def dump(self):
        status = "FAIL" if self.errors else ("warn" if self.warnings else "PASS")
        print(f"\n{'='*74}\n{self.label}   [{status}]  "
              f"{len(self.errors)} errors, {len(self.warnings)} warnings\n{'='*74}")
        for msg in self.notes:
            print(f"  .  {msg}")
        for msg in self.warnings:
            print(f"  !  {msg}")
        for msg in self.errors:
            print(f"  X  {msg}")
        return len(self.errors)


# ------------------------------------------------------------------ class facts


def is_stat_conversion(key):
    """True for a <target>_from_<source>_pct stat-conversion key.

    These are resolved dynamically in Character._recalculate_derived_stats
    against module-level STAT_CONVERSION_TARGETS and STAT_CONVERSION_SOURCES,
    so no literal grep finds them and audit_talents' key set does not carry
    them. They work through the STATUS channel as well as the talent one -
    verified by applying spell_power_from_agility_pct and ap_from_intellect_pct
    as buff stat_mods on a Templar: spell power went 5 -> 38 (half of 66
    Agility) and attack power 105 -> 119. Without this, the dead-key check
    reported Templar's Libram of Fervor as doing nothing when it does.
    """
    if not key.endswith("_pct") or "_from_" not in key:
        return False
    try:
        from entities.character import STAT_CONVERSION_TARGETS, STAT_CONVERSION_SOURCES
    except Exception:                                          # noqa: BLE001
        return True        # cannot check - do not accuse
    body = key[: -len("_pct")]
    target, _, source = body.partition("_from_")
    return target in STAT_CONVERSION_TARGETS and source in STAT_CONVERSION_SOURCES

def class_display_name(slug):
    """guardian -> Guardian, knight_of_xoroth -> Knight of Xoroth.

    Matched against the real registries rather than title-cased blindly, so
    'Sun Cleric' and 'Knight of Xoroth' resolve without a special case.
    """
    from combat.abilities import CLASS_RESOURCE_MAP
    want = slug.replace("_", " ").replace("-", " ").lower()
    for name in CLASS_RESOURCE_MAP:
        if name.lower() == want:
            return name
    return slug.replace("_", " ").title()


def all_ability_ids():
    ids = {}
    for path in (ROOT / "data/abilities").glob("*.json"):
        doc = json.loads(path.read_text())
        for ability in doc.get("abilities", []):
            ids.setdefault(ability.get("ability_id"), []).append(path.name)
    return ids


# -------------------------------------------------------------------- abilities

def validate_abilities(slug, report, effect_types, global_ids):
    from combat.abilities import CLASS_RESOURCE_MAP
    path = ROOT / f"data/abilities/{slug}.json"
    if not path.exists():
        report.error(f"no ability file at data/abilities/{slug}.json")
        return []
    doc = json.loads(path.read_text())
    abilities = doc.get("abilities", [])
    if not abilities:
        report.error(f"{path.name}: zero abilities")
        return []

    display = class_display_name(slug)
    if doc.get("class") != display:
        report.warn(f'{path.name}: "class" is {doc.get("class")!r}, '
                    f'registry name is {display!r}')

    # is_aoe DOES NOTHING ON A PLAYER ABILITY. CombatEngine reads it only for
    # MONSTER and PET abilities (combat_engine.py's execute_monster_action and
    # the pet turn); Ability.__init__ does not even accept it, so it is not an
    # attribute on a player ability at all. What decides a player AoE is
    # target_type == "enemy_aoe", which is also the only branch that honours
    # max_targets.
    #
    # Six Guardian abilities shipped with is_aoe=True and target_type="enemy":
    # Broad Sweep, Hammer of Kings, Song of Battle, Cavalry Charge, Sound of
    # War and Glorious Arena. Every one is explicitly cleave in CoA ("AoE
    # slam", "energy-dump filler and cleave", "for 3+ mobs"), and each hit
    # exactly one enemy - Broad Sweep, declared max_targets 3, hit 1 of 4.
    # The flag made the data look correct, which is why it survived.
    # DEAD STAT_MOD KEYS ON ABILITIES. audit_talents.py checks talent trees
    # for keys the engine never reads; nothing checked ABILITIES, and a sweep
    # found 46 such values across 25 keys. Some were plain misspellings of a
    # live stat - dodge_chance for dodge, parry_chance for parry,
    # cost_reduction_pct for all_ability_cost_pct - each silently dropping
    # half an ability's effect.
    #
    # The worst were FLAG-SHAPED: 23 values of "stunned", "silenced",
    # "rooted" and "stealthed", which look exactly like the mechanism and are
    # not (the real one is the ability-level is_stun flag). That is the same
    # trap as is_aoe: data that reads as correct and does nothing. Flagged as
    # an error so neither can come back.
    #
    # Everything else is reported as a WARNING rather than an error, because
    # most of the remainder are mechanics this engine genuinely lacks -
    # pushback, movement speed, ability range, reducing a target's hit chance
    # - rather than typos. Those are worth seeing and not worth failing a
    # build over.
    FLAG_KEYS = {"stunned", "silenced", "rooted", "stealthed"}
    audit_mod = None
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import audit_talents as audit_mod                      # noqa: PLC0415
        known = audit_mod.live_effect_keys() | audit_mod.scale_talent_keys()
        dynamic = audit_mod._DYNAMIC_KEY
    except Exception:                                          # noqa: BLE001
        known, dynamic = None, None
    for ability in abilities:
        for key in (ability.get("stat_mods") or {}):
            if key in FLAG_KEYS:
                report.error(
                    f"{ability.get('ability_id')}: stat_mod {key!r} is read by "
                    f"NOTHING - the real mechanism is the ability-level is_stun "
                    f"flag. A flag-shaped dead key is the is_aoe trap again.")
            elif (known is not None and key not in known
                    and not dynamic.match(key)
                    and not is_stat_conversion(key)):
                report.warn(
                    f"{ability.get('ability_id')}: stat_mod {key!r} is read by no "
                    f"engine code - this part of the ability does nothing")

    # UNIT CONVENTIONS ON ABILITY stat_mods. This is the single worst trap in
    # the codebase and nothing checked it. Six separate bugs came from it in
    # one session, two of them granting permanent damage immunity and one
    # granting +800% health:
    #
    #   starcaller_celestial_aegis   damage_taken_pct -25   meant -2500%
    #   starcaller_shrouded_stars    damage_taken_pct  -5   meant  -500%
    #   venomancer_harden            damage_taken_pct -45   meant -4500%
    #   runemaster_augurs_shield     damage_taken_pct -10   meant -1000%
    #   runemaster_aspect_...        damage_taken_pct  -8   meant  -800%
    #   guardian_heros_decree        max_health_pct   8.0   meant  +800%
    #
    # The conventions differ PER KEY with no naming rule, and the two worst
    # offenders sit four lines apart in Character.take_damage: the bare
    # damage_taken_pct is added UNDIVIDED while physical_/magic_ variants
    # right below it ARE divided by 100. Several _source notes in the repo
    # still state the rule backwards, because a previous session generalised
    # it FROM one of these bugs and cited itself twice - which is exactly why
    # this belongs in a tool rather than in a comment.
    FRACTION_MODS = {
        "damage_taken_pct", "max_health_pct", "max_mana_pct",
        "block_value_pct", "all_ability_cost_pct",
    }
    POINTS_MODS = {
        "physical_damage_taken_pct", "magic_damage_taken_pct",
        "spell_damage_taken_pct", "healing_taken_pct",
        "armor_pct", "stamina_pct", "threat_generation_pct",
    }
    for ability in abilities:
        for key, val in (ability.get("stat_mods") or {}).items():
            if not isinstance(val, (int, float)) or val == 0:
                continue
            if key in FRACTION_MODS and abs(val) > 1:
                report.error(
                    f"{ability.get('ability_id')}: {key}={val} is a FRACTION in an "
                    f"ability's stat_mods, so this means {val * 100:g}%. Use "
                    f"{val / 100:g}.")
            elif key in POINTS_MODS and abs(val) < 1:
                report.error(
                    f"{ability.get('ability_id')}: {key}={val} is in PERCENT POINTS "
                    f"in an ability's stat_mods, so this means {val:g}% and does "
                    f"almost nothing. Use {val * 100:g}.")

    # execute_threshold_pct IS A PERCENT ON A 0-100 SCALE, not a fraction.
    # Ability.use computes target_pct = current/max * 100 and refuses the
    # cast above the threshold, so 0.35 demands a target below 0.35% health.
    # Three abilities shipped that way - bloodmage_reave, felsworn_tyrants_
    # gaze and guardian_final_verdict - and were REFUSED at every health
    # value tested including 1%, i.e. dead buttons. Twelve others in the
    # game correctly use 20/25/35/50.
    for ability in abilities:
        thr = ability.get("execute_threshold_pct")
        if thr is not None and 0 < thr < 1:
            report.error(
                f"{ability.get('ability_id')}: execute_threshold_pct={thr} is a "
                f"fraction, but the engine compares health on a 0-100 scale - "
                f"this requires the target below {thr}% health and can never be "
                f"cast. Use {thr * 100:g}.")

    for ability in abilities:
        if ability.get("is_aoe") and ability.get("target_type") != "enemy_aoe":
            report.error(
                f"{ability.get('ability_id')}: is_aoe is set but target_type is "
                f"{ability.get('target_type')!r} - is_aoe is read ONLY for monster "
                f"and pet abilities, so this hits exactly one enemy. Use "
                f"target_type 'enemy_aoe' (with max_targets to cap it).")

    primary, secondary = CLASS_RESOURCE_MAP.get(display, (None, None))
    allowed = {r.value if hasattr(r, "value") else str(r)
               for r in (primary, secondary) if r is not None}
    allowed = {a.lower() for a in allowed} | {"health"}
    # Shapeshift and stance resources are legitimately OUTSIDE the class's
    # CLASS_RESOURCE_MAP entry: get_class_resource overrides the class
    # default while a form is active, so Druid Cat Form spends Energy and
    # Bear Form spends Rage even though Druid maps to Mana. Venomancer is
    # mapped Mana-only with its own comment saying the real answer is
    # "spec-dependent (Mana OR Rage)". Flagging those as errors failed four
    # shipped classes, so form resources are allowed and anything else
    # outside the map is a warning, not a failure.
    form_resources = set()
    try:
        from combat.forms import FORMS
        for form in FORMS.values():
            res = form.get("resource")
            if res is not None:
                form_resources.add(str(getattr(res, "value", res)).lower())
    except Exception:
        form_resources = {"rage", "energy"}
    allowed |= form_resources

    required = {"ability_id", "name", "resource_type", "cooldown", "effect_type",
                "duration", "stat_mods", "description", "ranks", "icon_id"}
    seen_ids = Counter()
    max_level = 0

    for ability in abilities:
        aid = ability.get("ability_id", "<missing id>")
        missing = required - set(ability)
        if missing:
            report.error(f"{aid}: missing required keys {sorted(missing)}")
        seen_ids[aid] += 1

        if not str(aid).startswith(slug.replace("-", "_")):
            report.warn(f"{aid}: id does not start with {slug!r}")
        dupes = [f for f in global_ids.get(aid, []) if f != path.name]
        if dupes:
            report.error(f"{aid}: ability_id also defined in {dupes}")

        etype = ability.get("effect_type")
        if etype not in effect_types:
            report.error(f"{aid}: effect_type {etype!r} is not handled by the "
                         f"ability engine (known: {sorted(effect_types)})")

        rtype = str(ability.get("resource_type", "")).lower()
        if rtype and rtype not in allowed:
            report.warn(f"{aid}: resource_type {rtype!r} is not a {display} "
                        f"resource ({sorted(allowed)}) - intended, or a typo?")

        ranks = ability.get("ranks") or []
        if not ranks:
            report.error(f"{aid}: no ranks")
        last_level, last_value = 0, None
        for index, rank in enumerate(ranks, start=1):
            if rank.get("rank") != index:
                report.warn(f"{aid} rank {index}: rank field is {rank.get('rank')}")
            level = rank.get("level_req", 0)
            # A rank above the level cap is unreachable but harmless, and
            # several shipped abilities carry WoW's own TBC/WotLK rank levels
            # (Paladin's Hammer of Wrath rank 3 at 72) which become real if
            # the cap ever rises. Worth saying, not worth failing. A FIRST
            # rank above the cap is different: that ability can never be
            # learned at all.
            if level < 1:
                report.error(f"{aid} rank {index}: level_req {level} below 1")
            elif level > 60 and index == 1:
                report.error(f"{aid}: first rank unlocks at level {level}, above "
                             f"the level cap - this ability is unlearnable")
            elif level > 60:
                report.warn(f"{aid} rank {index}: level_req {level} is above the "
                            f"level 60 cap, so this rank never unlocks")
            if level < last_level:
                report.error(f"{aid} rank {index}: level_req {level} goes "
                             f"backwards from {last_level}")
            last_level = max(last_level, level)
            max_level = max(max_level, level)
            value = rank.get("effect_value")
            if (isinstance(value, (int, float)) and isinstance(last_value, (int, float))
                    and value < last_value):
                report.warn(f"{aid} rank {index}: effect_value {value} is lower "
                            f"than rank {index-1}'s {last_value}")
            last_value = value
            cost = rank.get("cost", 0)
            if rtype in {"energy", "rage", "focus", "combo", "archery_points"} and cost > 100:
                report.error(f"{aid} rank {index}: {rtype} cost {cost} exceeds the "
                             f"100 pool cap - this ability can never be cast")

        gen = ability.get("generates")
        if gen and str(gen.get("resource", "")).lower() not in allowed:
            report.warn(f"{aid}: generates {gen.get('resource')!r}, which is not "
                        f"a {display} resource - nothing will receive it")

    for aid, count in seen_ids.items():
        if count > 1:
            report.error(f"{aid}: defined {count} times in this file")

    if max_level < 50:
        report.warn(f"highest rank unlocks at level {max_level} - nothing new "
                    f"past there")
    report.note(f"{len(abilities)} abilities, highest rank at level {max_level}")
    return abilities


# ---------------------------------------------------------------------- talents

def validate_talents(slug, report, live_keys, abilities, global_ids,
                     payload_keys, audit):
    prefix = slug.replace("-", "_")
    trees = sorted(ROOT.glob(f"data/talents/{prefix}_*.json"))
    if not trees:
        report.error(f"no talent trees matching data/talents/{prefix}_*.json")
        return
    own_ability_ids = {a.get("ability_id") for a in abilities}
    known_ability_ids = set(global_ids) | own_ability_ids
    #: Every ability_id some node in this class grants, across all trees.
    #: Checked against requires_talent after the loop - see below.
    granted = set()

    for path in trees:
        doc = json.loads(path.read_text())
        tag = path.stem
        if doc.get("tree_id") != tag:
            report.error(f"{tag}: tree_id is {doc.get('tree_id')!r}, "
                         f"filename says {tag!r}")

        tiers = {int(k): v for k, v in (doc.get("tier_requirements") or {}).items()}
        if not tiers:
            report.error(f"{tag}: no tier_requirements")
        else:
            ordered = [tiers[k] for k in sorted(tiers)]
            if ordered != sorted(ordered):
                report.error(f"{tag}: tier_requirements not ascending: {ordered}")

        nodes = doc.get("nodes") or []
        if not nodes:
            report.error(f"{tag}: zero nodes")
            continue

        ids = {n.get("talent_id") for n in nodes}
        seen, coords, total_points = Counter(), defaultdict(list), 0

        for node in nodes:
            nid = node.get("talent_id", "<missing>")
            seen[nid] += 1
            for key in ("talent_id", "name", "description", "node_type", "tier",
                        "max_points", "cost_per_point", "hex_x", "hex_y",
                        "effects", "connected_to"):
                if key not in node:
                    report.error(f"{tag}/{nid}: missing {key!r}")

            if node.get("node_type") not in NODE_TYPES:
                report.error(f"{tag}/{nid}: node_type {node.get('node_type')!r} "
                             f"not in {sorted(NODE_TYPES)}")
            tier = node.get("tier")
            if tiers and tier not in tiers:
                report.error(f"{tag}/{nid}: tier {tier} has no tier_requirements entry")

            max_points = node.get("max_points", 0)
            if not isinstance(max_points, int) or max_points < 1:
                report.error(f"{tag}/{nid}: max_points {max_points!r}")
            else:
                total_points += max_points

            coords[(node.get("hex_x"), node.get("hex_y"))].append(nid)

            for target in node.get("connected_to") or []:
                if target not in ids:
                    report.error(f"{tag}/{nid}: connected_to {target!r} "
                                 f"is not a node in this tree")

            effects = node.get("effects") or {}
            for key, value in effects.items():
                if key.startswith("ability_"):
                    # ability_<ability_id>_<stat>, built by string
                    # interpolation in abilities.py - a literal grep calls
                    # these dead, so match the longest real ability id.
                    body = key[len("ability_"):]
                    if not any(body.startswith(a[len(""):]) or body.startswith(a)
                               for a in known_ability_ids if a):
                        report.warn(f"{tag}/{nid}: {key!r} does not resolve to a "
                                    f"known ability_id")
                    continue
                if key == "unlock_ability":
                    targets = value if isinstance(value, list) else [value]
                    for target in targets:
                        granted.add(target)
                        if target not in known_ability_ids:
                            report.error(f"{tag}/{nid}: unlock_ability {target!r} "
                                         f"is not a real ability_id")
                    continue
                if key_is_live(key, live_keys, audit):
                    continue
                report.error(f"{tag}/{nid}: effect key {key!r} is read by NOTHING "
                             f"in the engine - this talent would do nothing")

            proc = node.get("proc")
            if proc:
                trigger = proc.get("trigger")
                if trigger not in PROC_TRIGGERS:
                    report.error(f"{tag}/{nid}: proc trigger {trigger!r} not in "
                                 f"{sorted(PROC_TRIGGERS)}")
                if "chance" not in proc:
                    report.error(f"{tag}/{nid}: proc has no chance")
                if payload_keys and not payload_keys & set(proc):
                    report.warn(f"{tag}/{nid}: proc has no recognised payload "
                                f"(one of {sorted(payload_keys)})")

        for nid, count in seen.items():
            if count > 1:
                report.error(f"{tag}: talent_id {nid!r} appears {count} times")
        for coord, nids in coords.items():
            if len(nids) > 1:
                report.error(f"{tag}: hex {coord} occupied by {nids}")

        if total_points < 51:
            report.error(f"{tag}: tree offers only {total_points} points; a level "
                         f"60 character has 51+ to spend in one tree")
        report.note(f"{tag}: {len(nodes)} nodes, {total_points} points available")

    # REACHABILITY. An ability with requires_talent is learned the moment
    # its talent has a point in it, and by nothing else - Ability.
    # refresh_rank_for_level() sets is_learned purely from talent_unlocked
    # for these, ignoring level and the trainer. So if no node grants it,
    # the ability exists in the class's book and can never be cast by
    # anyone. Nothing else in this validator notices: the ability's own
    # schema is fine, the trees are structurally fine, and a combat test
    # drives abilities directly rather than through the learn gate.
    #
    # Templar shipped exactly this way - Righteous Tempest, requires_talent
    # with no granting node - and passed with 0 errors. One ability in the
    # whole game, but the only reason it was one and not more is luck.
    for ability in abilities:
        aid = ability.get("ability_id")
        if ability.get("requires_talent") and aid not in granted:
            report.error(
                f"{aid}: requires_talent is set but NO talent node grants it "
                f"(effects.unlock_ability) - unobtainable, cannot ever be cast")

    # CROSS-TREE DEAD FILTERS. A node in one tree that filters on, casts, or
    # resets an ability only a DIFFERENT tree can unlock is dead for anyone
    # who actually specs the tree it sits in. Found twice by hand today:
    # Runemaster's Swift Etching sat in Engravement filtering on Hurricane,
    # which only Riftblade grants; and five CoA Demolition nodes key off
    # Tinker's Rocket Launcher, which only Invention grants. Note that
    # Character marks ANY unlock_ability target as talent-gated whether or
    # not the ability's own row sets requires_talent, so this bites even
    # when the data looks innocent.
    owner = {}
    for path in trees:
        doc = json.loads(path.read_text())
        for node in doc.get("nodes") or []:
            v = (node.get("effects") or {}).get("unlock_ability")
            for target in (v if isinstance(v, list) else [v]) if v else []:
                owner.setdefault(target, set()).add(path.stem)

    def referenced_abilities(blob):
        """Every ability id a node's proc machinery points at, nested procs
        included - audit_talents only reads the top-level proc, and a
        payload nested inside an apply_effect is just as live."""
        found = set()
        if isinstance(blob, dict):
            for key, val in blob.items():
                if key in ("ability_filter", "cast_ability"):
                    found.update(val if isinstance(val, list) else [val])
                elif key == "reset_cooldown":
                    spec = val if isinstance(val, dict) else {"ability": val}
                    ids = spec.get("ability") or spec.get("abilities") or []
                    found.update(ids if isinstance(ids, list) else [ids])
                else:
                    found |= referenced_abilities(val)
        elif isinstance(blob, list):
            for item in blob:
                found |= referenced_abilities(item)
        return {f for f in found if isinstance(f, str)}

    for path in trees:
        doc = json.loads(path.read_text())
        tag = path.stem
        for node in doc.get("nodes") or []:
            nid = node.get("talent_id", "<missing>")
            refs = referenced_abilities(node.get("proc"))
            # EFFECTS KEYS TOO, not just procs. ability_<id>_<suffix> in a
            # node's effects names an ability exactly as a filter does, and a
            # proc-only version of this check missed warlock_demonology/
            # decimation, which carried ability_warlock_shadowburn_damage
            # while Shadowburn is unlocked only in Destruction - so half that
            # talent's payout could never apply to the spec it sits in.
            for key in (node.get("effects") or {}):
                if not key.startswith("ability_"):
                    continue
                body = key[len("ability_"):]
                match = max((a for a in owner if body.startswith(a)),
                            key=len, default=None)
                if match:
                    refs.add(match)
            for target in sorted(refs):
                owners = owner.get(target)
                if owners and tag not in owners:
                    report.error(
                        f"{tag}/{nid}: references {target!r}, which is unlocked "
                        f"only by {', '.join(sorted(owners))} - dead for anyone "
                        f"who specs this tree")


# ----------------------------------------------------------------------- wiring

def validate_wiring(slug, report, abilities):
    display = class_display_name(slug)
    from combat.abilities import CLASS_RESOURCE_MAP

    if display not in CLASS_RESOURCE_MAP:
        report.error(f"{display!r} missing from CLASS_RESOURCE_MAP")

    armor = json.loads((ROOT / "data/items/armor_types.json").read_text())
    if display not in (armor.get("class_armor_map") or {}):
        report.error(f"{display!r} missing from armor_types.json class_armor_map")

    weapons = json.loads((ROOT / "data/items/weapon_types.json").read_text())
    if display not in (weapons.get("class_weapon_map") or {}):
        report.error(f"{display!r} missing from weapon_types.json class_weapon_map")

    stats_src = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    if f'"{display}": {{' not in stats_src:
        report.error(f"{display!r} has no entry in Character._initialize_class_stats")

    creation = (ROOT / "ui/screens/character_screen.py").read_text(encoding="utf-8")
    if f'"{display}"' not in creation:
        report.warn(f"{display!r} not in the character creation list - "
                    f"unselectable until added")

    tabs_path = ROOT / "data/spellbook_tabs_coa.json"
    tabs = json.loads(tabs_path.read_text()) if tabs_path.exists() else {}
    mapping = tabs.get(display)
    if mapping is None:
        report.warn(f"{display!r} has no spellbook tab mapping in {tabs_path.name}")
    else:
        unmapped = [a["ability_id"] for a in abilities
                    if a.get("ability_id") not in mapping]
        if unmapped:
            report.warn(f"{len(unmapped)} abilities have no spellbook tab: "
                        f"{unmapped[:6]}{' ...' if len(unmapped) > 6 else ''}")


# ----------------------------------------------------------------------- combat

def validate_live(slug, report):
    """Build the class for real and make it fight. Static checks cannot catch
    a class that loads fine and then cannot act."""
    display = class_display_name(slug)
    try:
        from entities.character import Character
        from entities.monster import Monster
        from entities.party import Party
        from combat.combat_engine import CombatEngine
    except Exception as exc:                                  # pragma: no cover
        report.error(f"cannot import engine: {exc}")
        return

    for level in (1, 20, 40, 60):
        try:
            char = Character("Probe", display, level)
        except Exception as exc:
            report.error(f"Character(level {level}) raised {type(exc).__name__}: {exc}")
            continue
        try:
            learned = char.get_learned_abilities()
        except Exception as exc:
            report.error(f"level {level}: get_learned_abilities raised "
                         f"{type(exc).__name__}: {exc}")
            continue
        if not learned:
            report.error(f"level {level}: knows ZERO abilities - empty spellbook")
            continue
        if level == 60:
            report.note(f"level 60 knows {len(learned)} abilities")

    # talent budget
    try:
        char = Character("Probe", display, 60)
        trees = getattr(char, "talent_trees", {}) or {}
        mine = {k: v for k, v in trees.items()
                if k.startswith(slug.replace("-", "_"))}
        if not mine:
            report.error("level 60 character has no talent trees for this class")
        for tree_id, tree in mine.items():
            spent = 0
            for _ in range(200):
                progressed = False
                for node in tree.nodes.values():
                    if node.points_spent < node.max_points and node.can_spend_point():
                        node.spend_point()
                        spent += 1
                        progressed = True
                        if spent >= 56:
                            break
                if spent >= 56 or not progressed:
                    break
            if spent < 51:
                report.error(f"{tree_id}: could only spend {spent} points; tier "
                             f"gates or connections block a level 60 build")
            else:
                report.note(f"{tree_id}: spent {spent} points cleanly")
    except Exception as exc:
        report.error(f"talent spend probe raised {type(exc).__name__}: {exc}")

    # a real fight
    try:
        char = Character("Probe", display, 60)
        for sync in ("_sync_talent_procs", "_sync_talent_unlocked_abilities",
                     "_recalculate_derived_stats", "_refresh_ability_ranks"):
            getattr(char, sync, lambda: None)()
        enemy = Monster("Dummy", "humanoid_warrior", 60)
        enemy.health = enemy.current_health = 10_000
        engine = CombatEngine(char, enemy, party=Party(char), enemies=[enemy])
        learned = char.get_learned_abilities()
        acted, hp_before = 0, enemy.current_health
        own_hp_before = char.current_health
        for _ in range(12):
            for pool in ("current_energy", "current_rage", "current_mana",
                         "current_focus", "current_insanity"):
                if hasattr(char, pool):
                    cap = {"current_energy": "max_energy", "current_mana": "mana"}.get(pool)
                    setattr(char, pool, getattr(char, cap, 100) if cap else 100)
            for ability in learned:
                ok, _why = engine.execute_ability(char, ability.ability_id, enemy)
                if ok:
                    acted += 1
                    break
        if not acted:
            report.error("could not successfully execute a SINGLE ability in "
                         "combat across 12 turns")
        else:
            dealt = hp_before - enemy.current_health
            healed = char.current_health - own_hp_before
            if dealt <= 0 and healed <= 0:
                report.error(f"executed {acted} abilities but dealt no damage and "
                             f"healed nothing - the kit does not function")
            else:
                report.note(f"combat: {acted} abilities executed, "
                            f"{dealt} damage dealt, {healed} self-healing")
    except Exception as exc:
        report.error(f"combat probe raised {type(exc).__name__}: {exc}")


# -------------------------------------------------------------------------- cli

def validate(slug, live_keys, effect_types, global_ids, payload_keys, audit):
    report = Report(f"{class_display_name(slug)}  ({slug})")
    abilities = validate_abilities(slug, report, effect_types, global_ids)
    validate_talents(slug, report, live_keys, abilities, global_ids,
                     payload_keys, audit)
    validate_wiring(slug, report, abilities)
    check_magnitudes(slug, report, effect_key_conventions(exclude_slug=slug))
    validate_live(slug, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("classes", nargs="*", help="class slugs, e.g. guardian")
    parser.add_argument("--all", action="store_true",
                        help="every class with an ability file")
    args = parser.parse_args()

    live_keys, audit = live_talent_effect_keys()
    effect_types = live_effect_types(live_keys)
    global_ids = all_ability_ids()
    payload_keys = proc_payload_keys()

    slugs = args.classes
    if args.all or not slugs:
        slugs = sorted(p.stem for p in (ROOT / "data/abilities").glob("*.json")
                       if not p.stem.startswith("_") and p.stem != "asher_unique")

    print(f"liveness via tools/audit_talents.py: {len(live_keys)} keys; "
          f"{len(effect_types)} effect_types, {len(payload_keys)} proc payloads")

    failures = 0
    summary = []
    for slug in slugs:
        report = validate(slug, live_keys, effect_types, global_ids,
                          payload_keys, audit)
        count = report.dump()
        failures += count
        summary.append((slug, count, len(report.warnings)))

    print(f"\n{'='*74}\nSUMMARY")
    for slug, errors, warnings in summary:
        flag = "FAIL" if errors else "pass"
        print(f"  {flag}  {slug:22s} {errors:3d} errors  {warnings:3d} warnings")
    print(f"\n{failures} errors total")
    return failures


if __name__ == "__main__":
    sys.exit(min(main(), 125))
