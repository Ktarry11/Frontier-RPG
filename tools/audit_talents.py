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


def effect_magnitudes(eff):
    """Every plausible rendering of an effect value, so the comparison is not
    fooled by sign (reductions are negative), by 0-1 vs percent, or by a
    duration stored in minutes against a description in seconds."""
    vals = set()
    for k, v in eff.items():
        if FLAG_KEY.search(k):
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            a = abs(float(v))
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

#: Effect-key prefixes/suffixes the engine resolves dynamically, so a grep
#: for the literal key name will never find them.
_DYNAMIC_KEY = re.compile(
    r"^(ability_.+_(damage|healing|cost|cooldown|duration|crit|potency)"
    r"|unlock_ability|unlock_mechanic"
    r"|(arcane|fire|frost|nature|shadow|holy)_(resistance|spell_power))$")


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
    LIVE = live_effect_keys()

    for tid, n in T.items():
        for key, val in (n.get("effects") or {}).items():
            if not (_DYNAMIC_KEY.match(key) or key in LIVE):
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
            vals = effect_magnitudes(eff)
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
