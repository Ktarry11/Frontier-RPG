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


def proc_payload_keys():
    """Payload keys real procs use, read off the authored trees.

    Hand-listing these produced 9 false warnings against shipped Warrior and
    Warlock trees, whose procs carry payloads the list had never heard of.
    """
    keys = Counter()
    for path in (ROOT / "data/talents").glob("*.json"):
        for node in json.loads(path.read_text()).get("nodes", []):
            proc = node.get("proc")
            if proc:
                keys.update(k for k in proc
                            if k not in {"trigger", "chance", "icd"})
    return set(keys)


PROC_TRIGGERS = {
    "on_damage_taken", "on_cast", "on_damage_cast", "on_weapon_swing",
    "on_crit", "on_kill", "on_heal_cast", "on_damage_or_heal_cast",
}
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
