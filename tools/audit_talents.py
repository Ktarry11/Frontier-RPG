#!/usr/bin/env python3
"""Audit talent data for the ways it gets bastardised.

    python3 tools/audit_talents.py           # all checks
    python3 tools/audit_talents.py --verbose # list every hit, not just a sample

Kyle, 2026-10-26: "we should audit each talent since some of them are
bastardized."

1358 talents across 56 trees is too many to eyeball, and the damage is not
uniform - it is a handful of specific failure modes, each of which IS
detectable. This finds them. What it cannot judge is whether a talent is
BALANCED or whether its fantasy fits its spec; that still needs eyes.

The checks, and the real bug each was written for:

  dev-note-in-tooltip   warrior_arms "Sudden Death" shipped a design
                        rationale as its player-facing description: "Real
                        proc: ... matches Sudden Death's actual WOTLK
                        identity ... (previously Execute had no HP gate at
                        all)". A player reads that in the tooltip.
  junk-name             cultist_godblade's capstone was called "Nutcase".
  name-belongs-to-other A talent carrying a DIFFERENT talent's name while its
                        own description describes itself - primalist's
                        raptor_talons was named "Rylak's Bite" while
                        describing Raptor Talons, and a separate
                        rylaks_bite node existed alongside it.
  duplicate-name        Two talents with the same name in one tree. Always a
                        mistake: the player cannot tell them apart.
  orphan-prefix         A node whose id names a spec that is not the file it
                        lives in. Some of these are INTENTIONAL sub-spec
                        merges and are whitelisted (see MERGED_SUBSPECS):
                        Kyle, 2026-10-26 - "mage healers are frost and shaman
                        tanks are in enhancement". The name COLLISIONS those
                        merges created are still reported, because two
                        talents sharing a name in one tree is a problem for
                        the player whether or not the merge was deliberate.
  no-effects            A talent with a description but neither an effects
                        dict NOR a proc: it reads as doing something and does
                        nothing. Having only a proc is normal - reactive
                        talents are authored that way.
  vague-magnitude       The description states a condition but never the
                        number, while the effects carry one - "Reaching 60
                        Insanity grants a flat bonus to Magic damage" when
                        the effect is 10%.
  number-contradiction  A number in the description that matches NO effect
                        value, in either sign or scale.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Needed so _is_live_stat_conversion can import the engine's own conversion
# maps. Run as a script, sys.path[0] is tools/, not the repo root, so the
# import failed silently and reported all 24 stat-conversion talents as dead
# even though the engine handles them.
sys.path.insert(0, str(ROOT))
TALENTS = ROOT / "data" / "talents"

#: Words that belong in a design document and never in a tooltip.
DEV_NOTE = re.compile(
    r"\b(real proc|WOTLK|WotLK|per handoff|confirmed via|screenshot|identity as|"
    r"previously|now that|TODO|placeholder|source:|note to self)\b", re.I)

#: Sub-specs that deliberately live inside another spec's tree rather than
#: having their own file. Kyle, 2026-10-26: "mage healers are frost and shaman
#: tanks are in enhancement". Confirmed in code too - character.py's
#: get_talent_effects comments on "the Shaman Tank tree merge" where Tank was
#: merged into Enhancement's hex grid. Not orphans; design.
MERGED_SUBSPECS = {
    "mage_cryotherapist": "mage_frost",
    "shaman_tank": "shaman_enhancement",
}

#: Names that are obviously not shipping names. Deliberately narrow - an
#: earlier, looser version flagged "Test of Faith" and "Tempest's Call",
#: which are real talent names, so this matches whole words only.
JUNK_NAME = re.compile(r"^(nutcase|todo|tbd|placeholder|temp|test|xxx|untitled|new talent)$", re.I)

#: A description that sets a condition but gives no magnitude.
VAGUE = re.compile(r"\b(a flat bonus|scale up further|increases healing done|"
                   r"additional health|reduces damage that would|further)\b", re.I)


def load():
    out = {}
    for f in sorted(TALENTS.glob("*.json")):
        doc = json.loads(f.read_text())
        for n in doc.get("nodes", []):
            out[n["talent_id"]] = dict(n, _file=f.stem, _spec=doc.get("spec_name", f.stem))
    return out


def numbers(s):
    return {float(x) for x in re.findall(r"\b(\d+(?:\.\d+)?)\b", s)}


#: Effect keys whose value is a FLAG (1 = on), not a magnitude. Comparing a
#: description's numbers against these is meaningless - "after 3 Horrorbolt
#: casts" against a proc flag of 1 is not a contradiction.
FLAG_KEY = re.compile(r"(_proc|^unlock_|_unlock$|^ability_)", re.I)


def effect_magnitudes(eff, ranks=1):
    """Every plausible rendering of an effect value, so the comparison is not
    fooled by sign (reductions are negative), by 0-1 vs percent, or by a
    duration stored in minutes against a description in seconds.

    RANKS MATTERS. Effects are authored PER RANK, and this project writes
    descriptions both ways: "+15% per rank" quotes the per-rank value, while
    "increases your Armor by 200% of your Intellect" on a 3-rank node quotes
    the FULL INVESTMENT. Both are correct and both are already in the data,
    so a check that only knew the per-rank value called 35 correct
    descriptions contradictory the moment the Tinker and Primalist trees were
    re-ranked - the values changed, the ceilings did not, and the prose was
    describing the ceiling. The full-investment rendering is accepted too.

    This deliberately widens what passes. It still catches a number that
    matches NEITHER reading, which is the failure worth having: a
    description promising 50% where no rank count produces 50%.
    """
    vals = set()
    ranks = max(1, int(ranks or 1))
    for k, v in eff.items():
        if FLAG_KEY.search(k):
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            for a in {abs(float(v)), abs(float(v)) * ranks}:
                vals |= {a, a * 100, a / 100, a * 60}
    return vals


#: The only effect keys the engine divides by 100, so the only ones that take
#: percentage POINTS rather than a fraction. Kept in sync with the
#: `bonuses.get(... ) / 100.0` sites in Character._recalculate_derived_stats.
POINTS_PCT_KEYS = frozenset({
    "all_stats_pct", "strength_pct", "stamina_pct", "intellect_pct",
    "spirit_pct", "agility_pct", "attack_power_pct", "healing_power_pct",
    "armor_pct", "armor_penetration_pct",
})

#: Status-effect stat_mod keys the engine reads RAW (as a fraction) rather
#: than dividing by 100. Everything else ending in _pct inside a status
#: effect's stat_mods is in percentage POINTS. This single-key exception is
#: real: character.py's taken_mult adds get_status_stat_mod("damage_taken_pct")
#: undivided, while the physical_/magic_ variants beside it are divided.
#: block_value_pct belongs here too, verified by applying a status effect and
#: reading the stat back: 0.2 raised a 15.9 block value to 19.1, exactly +20%,
#: while 20 raised it to 333.9. It feeds the same `block_value *= (1.0 + x)`
#: multiply the talent path uses (entities/character.py), so it never gets
#: divided by 100 no matter which path reaches it. Without this entry the
#: audit called Knight of Xoroth's Infernal Bulwark a 100x unit error when
#: the node was right all along.
STATUS_FRACTION_PCT_KEYS = frozenset({"damage_taken_pct", "block_value_pct"})

#: Triggers combat/status_effects.py actually dispatches on. A proc with any
#: other trigger never fires.
#: Exactly the triggers combat/abilities.py actually calls
#: fire_proc_trigger with. Narrowed 2026-10-27: this set also listed
#: "on_target" and "on_cast_damage_or_heal", neither of which the engine
#: dispatches anywhere - "on_target" is only a FIELD inside apply_effect, and
#: the real combined trigger is spelled "on_damage_or_heal_cast". A proc
#: authored with either would have passed this audit and never fired. No
#: talent currently uses them; this stops the next one.
#: DERIVED FROM THE ENGINE, not listed here. This was a hardcoded set and it
#: went stale the moment combat/status_effects.py gained on_dodge, on_parry,
#: on_avoid and on_block - it then reported 10 perfectly good avoidance procs
#: across Cultist, Guardian and Starcaller as "a trigger the engine does not
#: dispatch", which is the exact opposite of the truth. A hand-maintained
#: mirror of engine state is a liability in an audit tool: it fails silently
#: in the direction of accusing working code. ProcTrigger.ALL is the engine's
#: own answer to this question, so ask it.
def _proc_triggers():
    try:
        from combat.status_effects import ProcTrigger
        return frozenset(ProcTrigger.ALL)
    except Exception:
        # Degrade loudly rather than quietly auditing against a guess.
        print("WARNING: could not import ProcTrigger - trigger check skipped",
              file=sys.stderr)
        return None


PROC_TRIGGERS = _proc_triggers()

#: The payload keys that make a proc do something. A proc carrying none of
#: these fires and has no effect.
#:
#: SCANNED OUT OF THE PROC HANDLER, for the same reason PROC_TRIGGERS is
#: derived rather than listed. This was hand-maintained too, and it had
#: already drifted twice - splash_damage and damage_flat each had to be added
#: by hand after a talent using them was found doing nothing. Reading the
#: handler's own proc.get("...") calls means a payload the engine learns is a
#: payload this tool knows about on the same commit. Same approach
#: tools/validate_class.py uses, so the two tools cannot disagree.
def _proc_payloads():
    try:
        text = (ROOT / "combat/status_effects.py").read_text(encoding="utf-8")
    except OSError:
        print("WARNING: could not read status_effects.py - payload check skipped",
              file=sys.stderr)
        return None
    keys = set(re.findall(r'proc\.get\(\s*[\'"]([a-z_]+)[\'"]', text))
    # Not payloads - the proc's own plumbing.
    return frozenset(keys - {"trigger", "chance", "icd"})


PROC_PAYLOADS = _proc_payloads()

#: Effect-key prefixes/suffixes the engine resolves dynamically, so a grep
#: for the literal key name will never find them.
_SCHOOLS = "arcane|fire|frost|nature|shadow|holy"
_DYNAMIC_KEY = re.compile(
    r"^(ability_.+_(damage|healing|cost|cooldown|duration|crit|potency)"
    r"|ability_.+_(cost_pct|cooldown_pct|crit_damage)"
    r"|unlock_ability"
    r"|all_ability_cost_pct|heal_cost_pct|healing_spell_cost_pct"
    r"|crit_damage_pct|crit_damage_spell|crit_damage_physical"
    rf"|({_SCHOOLS})_crit_damage_pct"
    # <school>_damage_taken_pct and <school>_resist_pct are built by string
    # interpolation in Character.take_damage - `school_key =
    # f"{damage_type}_damage_taken_pct"` - so no literal grep finds them.
    # Without these two the audit called Reaper's Weakened Souls dead on
    # both of its keys; applying the debuff and taking a 1000-damage hit
    # gives 1100 on a shadow hit and 1000 on a fire hit, i.e. the key is
    # live AND correctly school-specific.
    rf"|({_SCHOOLS})_damage_taken_pct"
    rf"|({_SCHOOLS})_resist_pct"
    rf"|({_SCHOOLS})_(resistance|spell_power))$")


#: The six real damage schools. A key naming one of these as a component is
#: resolved at runtime against the school an ability actually deals.
_SCHOOL_SET = frozenset({"arcane", "fire", "frost", "nature", "shadow", "holy"})


def _is_live_school_key(key):
    """True for the school-resolved key families the engine builds at runtime.

    These are constructed from the ability's real school rather than written
    out literally (`f"{real}_spell_damage"`), so a grep for the key name finds
    nothing. Combined keys are supported - fire_nature_resist_pct applies to
    Fire and to Nature - so membership is tested per underscore component.

    Deliberately strict about what counts as live:
      poison_disease_resist_pct names no real school, so it stays flagged.
      low_health_healing_pct keys off the RECIPIENT's health, which the
        damage-multiplier path has no access to, so it stays flagged too.
    Both are genuinely still dead and should keep showing up.
    """
    for suffix in ("_spell_damage", "_damage_pct", "_resist_pct", "_dot_damage",
                   "_crit_damage_pct"):
        if key.endswith(suffix):
            parts = key[:-len(suffix)].split("_")
            return any(p in _SCHOOL_SET for p in parts)
    return False


#: Keys the engine builds dynamically from a non-school component, so neither
#: a grep for the literal name nor _is_live_school_key finds them.
#: bleed_dot_damage and poison_dot_damage are assembled as
#: f"{flavour}_dot_damage" in Ability._damage_multiplier, and low_health_
#: healing_pct is read through the heal path's recipient branch.
_NAMED_LIVE = frozenset({
    "low_mana_healing_pct", "high_mana_healing_pct", "spell_damage_taken_pct",
    "block_value_pct", "aoe_damage", "dot_damage",
    "low_health_healing_pct",
    "pet_damage", "pet_health", "pet_armor",
    "static_max", "energy_max", "insanity_max", "runes_max",
    "solar_power_max",
})

#: The flavour halves of f"{flavour}_dot_damage" that the engine assembles.
#: Ability._damage_multiplier does this:
#:
#:     for flavour in ("bleed", "poison"):
#:         if flavour in self.ability_id:
#:             global_key += self._talent(caster, f"{flavour}_dot_damage")
#:
#: so the key is live ONLY while some ability's id contains that word. That
#: is not a given, and it was not true: bleed_dot_damage sat in _NAMED_LIVE
#: as unconditionally live while NO ability id in the game contained
#: "bleed", which made Primalist's Rending Claws and Bloodmage's Crimson
#: Curse dead and kept them passing this audit. poison_dot_damage was fine
#: all along - five abilities match it - which is exactly why hardcoding
#: the pair together hid the problem.
_DOT_FLAVOURS = ("bleed", "poison")


def live_flavour_dot_keys():
    """{"<flavour>_dot_damage"} for flavours some ability id actually has.

    Computed from the ability data rather than listed, so naming a new
    ability "..._bleed_..." turns bleed_dot_damage live by itself, and
    removing the last matching ability turns it dead again and says so.
    """
    ids = []
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        doc = json.loads(path.read_text())
        block = doc.get("abilities", doc)
        rows = (list(block.values()) if isinstance(block, dict)
                else block if isinstance(block, list) else [])
        for row in rows:
            if isinstance(row, dict) and row.get("ability_id"):
                ids.append(row["ability_id"])
    return {f"{f}_dot_damage" for f in _DOT_FLAVOURS
            if any(f in aid for aid in ids)}


def scale_talent_keys():
    """Keys read LIVE through a proc's grant_resource.scale_talent_key.

    These are looked up by name at proc time (see combat/status_effects.py),
    so the key never appears as a literal in the engine and the dead-key
    check calls it dead. It is not: Venomancer's Adrenal Carapace fed
    exposed_flesh_rage_pct into Exposed Flesh's own Rage grant and worked
    fine, and acting on the checker's false verdict destroyed a working
    talent before this existed.

    Collected from the talent data rather than a hardcoded list, so adding a
    new scale_talent_key anywhere automatically marks its key live.
    """
    keys = set()
    for path in (ROOT / "data/talents").glob("*.json"):
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        for node in doc.get("nodes", []):
            grant = ((node.get("proc") or {}).get("grant_resource") or {})
            key = grant.get("scale_talent_key")
            if key:
                keys.add(key)
    return keys


def _is_live_stat_conversion(key):
    """True for a <target>_from_<source>_pct key the engine really handles.

    These names are built at runtime from the key itself (see
    Character._recalculate_derived_stats), so grepping the engine for the
    literal key name never finds them and the dead-key check would report
    all twenty-four of them as dead. The target and source maps are imported
    from the engine rather than copied, so this cannot claim a pairing the
    engine does not actually implement - which matters, because several
    authored keys name targets it does NOT handle
    (holy_fire_spell_damage_from_intellect_pct), and those must stay flagged.
    """
    if not key.endswith("_pct") or "_from_" not in key:
        return False
    # Deliberately NOT wrapped in a bare except. An earlier version swallowed
    # the ImportError and returned False, which looks like "this key is dead"
    # - the exact failure this whole check exists to catch, produced by the
    # checker itself. If the engine cannot be imported, that is a real
    # problem and should be loud.
    from entities.character import (STAT_CONVERSION_TARGETS,
                                    STAT_CONVERSION_SOURCES)
    target, source = key[:-4].split("_from_", 1)
    return target in STAT_CONVERSION_TARGETS and source in STAT_CONVERSION_SOURCES


def live_effect_keys():
    """Every effect key the engine actually reads, found in the engine itself.

    Flat talent effects are pooled and read generically in
    Character._recalculate_derived_stats, so a key is live if and only if some
    Python file mentions it as a string literal. A key nothing mentions is
    silently dropped at runtime, which is why a dead talent is
    indistinguishable from a working one by inspection.

    This is the check that was missing when 22 talents across six classes sat
    dead for months (the _healing, _duration and _crit suffixes), and when
    Druid Feral's tier-6 capstone Predatory Instincts turned out to grant
    crit_damage_pct and aoe_damage_taken_pct - two keys with zero engine
    references anywhere. Those were found by hand. This finds the next one.
    """
    lits = set()
    for py in ROOT.rglob("*.py"):
        if "tools/" in str(py.relative_to(ROOT)):
            continue  # the tools name keys in their own doc/comments
        try:
            src = py.read_text(errors="ignore")
        except OSError:
            continue
        lits.update(re.findall(r"""['"]([a-z][a-z0-9_]{2,})['"]""", src))
    return lits


def main():
    verbose = "--verbose" in sys.argv
    T = load()
    findings = defaultdict(list)
    LIVE = live_effect_keys() | scale_talent_keys() | live_flavour_dot_keys()

    for tid, n in T.items():
        for key, val in (n.get("effects") or {}).items():
            if not (_DYNAMIC_KEY.match(key) or key in LIVE
                    or key in _NAMED_LIVE
                    or _is_live_stat_conversion(key)
                    or _is_live_school_key(key)):
                findings["dead-effect-key"].append(
                    f"{tid} ({n.get('name')!r}): {key!r} is read by no engine code")
            # Unit convention. These ten keys are the only ones the engine
            # divides by 100 (Character._recalculate_derived_stats), so they
            # take percentage POINTS - all eight ability buffs using them do
            # (all_stats_pct: 10, armor_pct: 20). Every OTHER _pct key in the
            # game is a plain fraction. Fifteen talents were authored the
            # wrong way round and were silently 100x too weak: ten healer
            # talents granting "healing_power_pct": 0.02 were giving 0.02%,
            # not 2%, and nothing distinguished them from working ones.
            if not isinstance(val, (int, float)) or val == 0:
                continue
            if key in POINTS_PCT_KEYS:
                if abs(val) < 1.0:
                    findings["pct-unit-mixup"].append(
                        f"{tid} ({n.get('name')!r}): {key}={val} - this key takes "
                        f"percentage POINTS, so that is {abs(val)}%, not {abs(val) * 100}%")
            elif key.endswith("_pct") and abs(val) > 1.0:
                findings["pct-unit-mixup"].append(
                    f"{tid} ({n.get('name')!r}): {key}={val} - this key is a "
                    f"FRACTION, so that is {abs(val) * 100}%")

            # Sign check. talented_cost does cost * (1 - pct) and
            # talented_cooldown does cd * (1 - pct), so POSITIVE means a
            # reduction - the same direction as the flat _cost/_cooldown keys.
            # Eight talents across four classes authored these negative,
            # intending a discount and delivering a surcharge: one made every
            # heal in its spec 10% MORE expensive while its tooltip promised
            # cheaper. Nothing caught it, because the value is perfectly valid.
            if (key.endswith("_cost_pct") or key.endswith("_cooldown_pct")) and val < 0:
                findings["pct-sign-inverted"].append(
                    f"{tid} ({n.get('name')!r}): {key}={val} - positive means a "
                    f"REDUCTION here, so this makes it {abs(val) * 100}% MORE expensive")

        # Proc payloads get the same scrutiny as `effects`. A proc's
        # apply_effect stat_mods are read through the same generic pool, so a
        # key nothing reads makes the proc fire and do nothing - and the
        # dead-effect-key check above only ever looked at `effects`, so this
        # whole surface was unchecked.
        proc = n.get("proc")
        if proc:
            if PROC_TRIGGERS is not None and proc.get("trigger") not in PROC_TRIGGERS:
                findings["proc-bad-trigger"].append(
                    f"{tid} ({n.get('name')!r}): trigger {proc.get('trigger')!r} "
                    f"is not one the engine dispatches")
            # UNKNOWN proc keys, not just missing ones. The no-payload check
            # below asks whether AT LEAST ONE known key is present, which a
            # proc passes while carrying any number of invented keys beside
            # it. On 5 Nov a Tinker proc shipped `restore_mana_pct` alongside
            # a valid grant_resource: the proc fired, the grant worked, and
            # the half the talent was named for did nothing. Nothing flagged
            # it, because something in the dict was recognised.
            #
            # PROC_PAYLOADS is scanned out of the engine's own handler, so
            # this cannot drift from what the engine really reads.
            if PROC_PAYLOADS is not None:
                known = set(PROC_PAYLOADS) | {
                    "trigger", "chance", "icd", "ability_filter",
                    "require_form", "require_mechsuit", "school",
                }
                for key in proc:
                    if key not in known:
                        findings["dead-effect-key"].append(
                            f"{tid} ({n.get('name')!r}): proc key {key!r} is read "
                            f"by no engine code")
            if PROC_PAYLOADS is not None and not any(k in proc for k in PROC_PAYLOADS):
                findings["proc-no-payload"].append(
                    f"{tid} ({n.get('name')!r}): proc has a trigger but no payload, "
                    f"so it fires and does nothing")
            if proc.get("chance", 1) == 0:
                findings["proc-no-payload"].append(
                    f"{tid} ({n.get('name')!r}): proc chance is 0")
            # apply_effect is one spec dict OR a list of them (a proc that
            # lands something on the target and something on the caster off
            # the same roll). Flatten before reading stat_mods - a bare
            # .get() on the list form raises, and an audit that crashes is
            # worse than no audit.
            _ae = proc.get("apply_effect") or []
            _specs = _ae if isinstance(_ae, list) else [_ae]
            mods = {}
            for _s in _specs:
                if isinstance(_s, dict):
                    mods.update(_s.get("stat_mods") or {})
                    # NESTED PROCS WERE UNAUDITED. StatusEffect.__init__ takes
                    # a `proc`, and apply_effect passes arbitrary keys through
                    # to it, so a buff can carry its own proc that only fires
                    # while the buff is up - which is how Runemaster's glyph
                    # chain expresses "while Frost Glyph is active", the
                    # engine having no require_effect gate. Those nested
                    # payloads are every bit as live as a top-level one, and
                    # this audit read only the top level, so a dead key or a
                    # bad trigger one layer down passed silently.
                    nested = _s.get("proc")
                    for _np in (nested if isinstance(nested, list) else [nested]):
                        if not isinstance(_np, dict):
                            continue
                        # ONLY check the trigger when there IS one. A nested
                        # proc without a trigger is not a broken trigger - it
                        # is the flag-style shape, e.g. Mage Fire's Hot Streak
                        # nests {"guarantee_next_crit": true}, read in
                        # combat/abilities.py rather than dispatched by the
                        # proc handler. Demanding a trigger and a payload here
                        # accused five working talents across Mage, Hunter,
                        # Ranger and Warrior. The payload check is skipped for
                        # nested procs entirely - the shapes are too varied to
                        # assert on, and the valuable part is the stat_mods
                        # dead-key sweep below, which now reaches them.
                        if (_np.get("trigger") is not None
                                and PROC_TRIGGERS is not None
                                and _np.get("trigger") not in PROC_TRIGGERS):
                            findings["proc-bad-trigger"].append(
                                f"{tid} ({n.get('name')!r}): NESTED proc trigger "
                                f"{_np.get('trigger')!r} is not one the engine "
                                f"dispatches")
                        for _nae in (_np.get("apply_effect") or []) if isinstance(
                                _np.get("apply_effect"), list) else [_np.get("apply_effect")]:
                            if isinstance(_nae, dict):
                                mods.update(_nae.get("stat_mods") or {})
            for key, val in mods.items():
                # _DYNAMIC_KEY as well as LIVE: a status stat_mod can name a
                # key the engine builds by interpolation just as a talent
                # effect can, and this branch only checked the literal LIVE
                # set. That called Reaper's Weakened Souls dead on both
                # shadow_damage_taken_pct and frost_damage_taken_pct, which
                # Character.take_damage reads via
                # f"{damage_type}_damage_taken_pct" - verified live by
                # applying the debuff and taking a hit.
                if key not in LIVE and not _DYNAMIC_KEY.match(key):
                    findings["dead-effect-key"].append(
                        f"{tid} ({n.get('name')!r}): proc stat_mod {key!r} is read "
                        f"by no engine code")
                elif isinstance(val, (int, float)) and key.endswith("_pct"):
                    # Inside a status effect most of these are POINTS, the
                    # opposite of the talent-effects convention - but NOT all
                    # of them, and an earlier version of this check assumed
                    # otherwise and flagged correct authoring. The engine
                    # divides get_status_stat_mod by 100 for the
                    # school-specific damage-taken keys, damage_dealt_pct and
                    # healing_done_pct, but reads plain damage_taken_pct RAW
                    # (character.py's taken_mult), so that one key alone is a
                    # fraction. Acting on the wrong assumption here turned
                    # Primalist's Mountain Avatar from a correct -0.15 into
                    # -15, i.e. -1500%.
                    if key in STATUS_FRACTION_PCT_KEYS:
                        if abs(val) > 1.0:
                            findings["pct-unit-mixup"].append(
                                f"{tid} ({n.get('name')!r}): proc stat_mod {key}={val} - "
                                f"this status key is read RAW, so that is "
                                f"{abs(val) * 100}%")
                    elif 0 < abs(val) < 1.0:
                        findings["pct-unit-mixup"].append(
                            f"{tid} ({n.get('name')!r}): proc stat_mod {key}={val} - "
                            f"status stat_mods take POINTS, so that is {abs(val)}%")

    by_file_name = defaultdict(list)
    for tid, n in T.items():
        by_file_name[(n["_file"], n.get("name"))].append(tid)

    for tid, n in T.items():
        name = (n.get("name") or "").strip()
        desc = (n.get("description") or "").strip()
        eff = n.get("effects") or {}

        if DEV_NOTE.search(desc):
            findings["dev-note-in-tooltip"].append(f"{tid}: {desc[:90]}")

        if JUNK_NAME.match(name):
            findings["junk-name"].append(f"{tid}: {name!r}")

        if not desc:
            findings["no-description"].append(tid)
        elif not eff and not n.get("proc") and n.get("node_type") != "ability":
            # A talent's mechanics can live in `proc` instead of `effects` -
            # reactive talents (Fingers of Frost, Spider Lord) are authored
            # entirely as a proc payload and have an empty effects dict by
            # design. Flagging those as "does nothing" was wrong: all seven
            # this check originally reported turned out to have real procs.
            findings["no-effects"].append(f"{tid} ({name!r}): {desc[:70]}")

        # a node whose id claims a spec it does not live in
        prefix = tid.rsplit("_", 1)[0]
        if not tid.startswith(n["_file"]):
            cls = n["_file"].split("_")[0]
            if tid.startswith(cls + "_"):
                subspec = next((s for s in MERGED_SUBSPECS if tid.startswith(s + "_")), None)
                if subspec and MERGED_SUBSPECS[subspec] == n["_file"]:
                    pass        # a deliberate merge, not an orphan
                else:
                    findings["orphan-prefix"].append(f"{tid} lives in {n['_file']}.json")

        # the name belongs to a DIFFERENT talent that also exists
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        if slug and not tid.endswith(slug):
            sibling = f"{n['_file']}_{slug}"
            if (sibling in T and sibling != tid
                    and (T[sibling].get("name") or "").strip() == name):
                # Only a problem when the sibling ALSO still carries the name -
                # two nodes claiming it. A node named after the ability it
                # teaches (alkahest_active -> "Alkahest") is correct and must
                # not trip this forever.
                findings["name-belongs-to-other"].append(
                    f"{tid} is named {name!r}, and so is {sibling}")

        if eff and desc:
            dn = numbers(desc)
            vals = effect_magnitudes(eff, n.get('max_points', 1))
            if vals and dn and not any(abs(x - y) <= max(0.011, 0.02 * max(x, y))
                                       for x in dn for y in vals):
                if VAGUE.search(desc):
                    findings["vague-magnitude"].append(
                        f"{tid} ({name!r}): {desc[:70]} | effects {eff}")
                else:
                    findings["number-contradiction"].append(
                        f"{tid} ({name!r}): {desc[:70]} | effects {eff}")
            elif vals and not dn and VAGUE.search(desc):
                findings["vague-magnitude"].append(
                    f"{tid} ({name!r}): {desc[:70]} | effects {eff}")

    for (f, name), ids in by_file_name.items():
        if len(ids) > 1 and name:
            findings["duplicate-name"].append(f"{f}: {name!r} on {', '.join(sorted(ids))}")

    print(f"audited {len(T)} talents across {len({n['_file'] for n in T.values()})} trees\n")
    if not findings:
        print("No issues found.")
        return 0

    total = sum(len(v) for v in findings.values())
    print(f"{total} findings\n" + "=" * 68)
    for check in sorted(findings, key=lambda k: -len(findings[k])):
        hits = findings[check]
        print(f"\n{check}  ({len(hits)})")
        for h in (hits if verbose else hits[:6]):
            print(f"    {h}")
        if not verbose and len(hits) > 6:
            print(f"    ... and {len(hits)-6} more (--verbose for all)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
