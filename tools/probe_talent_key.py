#!/usr/bin/env python3
"""Does a talent key actually do anything? Spend it and look.

    PYTHONPATH=. python3 tools/probe_talent_key.py <Class> <key>=<value> [...]

WHY THIS EXISTS. The single most expensive mistake in this project is
authoring a talent around a key nothing reads. The talent loads, every
audit passes, the tooltip reads correctly, the point spends - and the
effect never happens. Eighteen heal talents across four classes shipped
that way using ability_<id>_damage instead of _healing; ten Tinker nodes
shipped crashing combat; several CoA tank keys were dead for months.

GREP CANNOT ANSWER THIS. It proves a key IS read; it cannot prove one is
NOT, because keys are built with f-strings at runtime -
f"{school}_spell_damage" at abilities.py:1371 walks every component of a
school list, and exposed_flesh_rage_pct greps dead while working fine. The
reverse trap is just as bad: armor_penetration_pct is read by
monster.py:658 via getattr(attacker, ...) - a Character ATTRIBUTE, not
get_talent_effect - so a talent authoring that key only works if the stat
pipeline happens to surface it as an attribute. Grepping finds the read and
tells you nothing about whether your talent reaches it.

So this spends the key on a real Character and reports all three channels:

    talent      get_talent_effect(key) - the talent bus
    attribute   getattr(character, key) - the derived-stat pipeline
    delta       the same attribute measured before and after

A key that moves NONE of them is dead for that class, whatever grep says.
A key that shows on the talent bus but not as an attribute is readable by
anything calling get_talent_effect and invisible to anything using
getattr - which is the distinction that makes armor_penetration_pct a trap.

Example:

    python3 tools/probe_talent_key.py Rogue armor_penetration_pct=0.09 \\
        crit_taken_reduction=2 ability_rogue_rupture_damage=0.3

This does NOT prove a key has the effect its NAME implies, only that
something receives it. Magnitude and sign still have to be measured in a
real fight - the unit conventions are not inferable (see
claude/engine_findings_2026_11_06.md).
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def read_sites(key):
    """Count places the engine could read this key by its literal name.

    Deliberately crude, and only ever used to turn "on the bus" into "on
    the bus AND something reads it". A zero here does NOT prove a key is
    dead - keys get built with f-strings, which is how arcane_spell_damage
    was wrongly declared dead once already - so a literal-name miss is
    reported as UNVERIFIED, never as dead.
    """
    try:
        out = subprocess.run(
            ["grep", "-rn", "--include=*.py", "-e", key,
             str(ROOT / "combat"), str(ROOT / "entities")],
            capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return None, []
    lines = [ln for ln in out.splitlines() if "__pycache__" not in ln]
    # Only count lines that look like a READ, not a data definition.
    reads = [ln for ln in lines
             if re.search(r"get_talent_effect|_talent\(|getattr|"
                          r"get_status_stat_mod", ln)]
    return len(reads), reads[:2]


#: Keys whose f-string construction means a literal grep cannot see them.
#: Each one is a real lesson paid for in this project.
DYNAMIC = {
    "arcane_spell_damage", "fire_spell_damage", "frost_spell_damage",
    "shadow_spell_damage", "nature_spell_damage", "holy_spell_damage",
    "exposed_flesh_rage_pct",
}

#: The ability-scoped family, built as f"ability_{self.ability_id}_{field}"
#: at ten sites in abilities.py. The SUFFIX is what has to be real - the
#: ability_id part can be anything - so these are matched by suffix.
#: A typo in the ability_id is silently dead data and no grep can see it,
#: which is why the verdict for these says to check the id as well.
#:
#: ORDERED LONGEST-FIRST, and that ordering is the whole point. A single
#: regex with a greedy id group splits ability_X_crit_damage as
#: id="X_crit" + field="damage", because the longest possible id wins -
#: which reported all 20 of the project's legitimate _crit_damage keys as
#: naming non-existent abilities on this tool's first run. Matching the
#: longest suffix first reads it correctly as id="X" + field="crit_damage".
ABILITY_FIELDS = ("crit_damage", "cooldown_pct", "cost_pct", "cooldown",
                  "duration", "healing", "potency", "damage", "crit",
                  "cost")


def split_ability_key(key):
    """(ability_id, field) for an ability-scoped key, else None.

    Tries the longest field suffix first, and prefers a split whose id is
    a REAL ability - so an id that merely happens to end in "_crit" cannot
    steal the suffix from the field.
    """
    if not key.startswith("ability_"):
        return None
    body = key[len("ability_"):]
    fallback = None
    for field in ABILITY_FIELDS:
        suffix = "_" + field
        if not body.endswith(suffix):
            continue
        aid = body[:-len(suffix)]
        if not aid:
            continue
        if aid in _ability_ids():
            return aid, field
        if fallback is None:
            fallback = (aid, field)
    return fallback


_ABILITY_IDS = None


def _ability_ids():
    """Every real ability_id, so an ability-scoped key's id can be checked.

    A typo in the id half of ability_<id>_damage is silent dead data that
    no grep and no audit can see - the suffix is real, the key is well
    formed, and the talent simply never fires. This is the only way to
    catch it.
    """
    global _ABILITY_IDS
    if _ABILITY_IDS is None:
        import json
        _ABILITY_IDS = set()
        for path in (ROOT / "data/abilities").glob("*.json"):
            try:
                for a in json.loads(path.read_text()).get("abilities", []):
                    _ABILITY_IDS.add(a["ability_id"])
            except Exception:
                pass
    return _ABILITY_IDS


def probe(char_class, pairs):
    from entities.character import Character

    base = Character(name="Probe", char_class=char_class, level=60)
    before = {k: getattr(base, k, None) for k, _ in pairs}

    live = Character(name="Probe", char_class=char_class, level=60)

    # Inject the keys as if a talent granted them. _talent_effect_cache is
    # what get_talent_effect reads; _recalculate_derived_stats is what turns
    # talent effects into attributes, so both channels get a fair test.
    injected = {k: v for k, v in pairs}
    original = live.get_talent_effects

    def patched():
        merged = dict(original())
        for k, v in injected.items():
            merged[k] = merged.get(k, 0) + v
        return merged

    live.get_talent_effects = patched
    for attr in ("_talent_effects_cache", "_talent_effect_cache",
                 "_cached_talent_effects"):
        if hasattr(live, attr):
            setattr(live, attr, None)
    live._recalculate_derived_stats()

    print(f"  {char_class}, level 60\n")
    print(f"  {'key':40s} {'bus':>8s} {'attr':>10s} {'delta':>9s} "
          f"{'reads':>5s}  verdict")
    notes = []
    for k, v in pairs:
        bus = live.get_talent_effect(k, None)
        attr = getattr(live, k, None)
        was = before.get(k)
        if isinstance(attr, (int, float)) and isinstance(was, (int, float)):
            delta = f"{attr - was:+.4g}"
            moved = abs(attr - was) > 1e-9
        else:
            delta = "-"
            moved = False
        on_bus = bus not in (None, 0, 0.0)
        nreads, where = read_sites(k)

        if moved:
            verdict = "LIVE - attribute moved"
            # A talent value that lands on the attribute SCALED is the
            # single most common unit trap in this project.
            if (isinstance(attr, float) and isinstance(was, (int, float))
                    and abs((attr - was) - v) > 1e-6 * max(1.0, abs(v))):
                ratio = (attr - was) / v if v else 0
                verdict += f"  (SCALED x{ratio:.4g} - check the unit!)"
        elif on_bus and nreads:
            verdict = f"LIVE on the talent bus ({nreads} read site(s))"
        elif on_bus and k in DYNAMIC:
            verdict = "LIVE - built by f-string, grep cannot see it"
        elif on_bus and (split := split_ability_key(k)):
            aid, field = split
            known = aid in _ability_ids()
            verdict = (f"LIVE - ability-scoped '_{field}'"
                       + ("" if known else
                          f"  *** but '{aid}' IS NOT AN ABILITY ID ***"))
            if not known:
                notes.append(k)
        elif on_bus:
            verdict = "*** UNVERIFIED - on the bus, no read site found ***"
            notes.append(k)
        else:
            verdict = "*** DEAD - nothing received it ***"
            notes.append(k)
        print(f"  {k:40s} {str(bus):>8s} {str(attr):>10s} {delta:>9s} "
              f"{str(nreads):>5s}  {verdict}")

    print("\n  'LIVE on the talent bus' is correct for most keys - they are "
          "read through\n  get_talent_effect, not surfaced as attributes.")
    if notes:
        print(f"\n  CHECK BEFORE AUTHORING: {', '.join(notes)}")
        print("  A literal-name miss is not proof of death - keys get built "
              "with f-strings\n  (arcane_spell_damage was wrongly declared "
              "dead that way once). Confirm by\n  measuring the effect in a "
              "real fight before relying on it, or avoid the key.")


def audit_all():
    """Sweep every tree for an ability-scoped key naming a dead ability_id.

    This is the typo class the single-key probe found by accident: the
    suffix is real, the key is well formed, every audit passes, and the
    talent simply never fires because the ability_id half does not exist.
    Nothing else in the project can see it - a typo'd id is indistinguishable
    from a correct one to grep, to audit_talents and to the tooltip.
    """
    import json
    ids = _ability_ids()
    bad = []
    keys = 0
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        tree = json.loads(path.read_text())
        for node in tree["nodes"]:
            for key in (node.get("effects") or {}):
                split = split_ability_key(key)
                if not split:
                    continue
                keys += 1
                aid, _field = split
                if aid not in ids:
                    bad.append((path.name, node["talent_id"], key, aid))

    print(f"  {keys} ability-scoped talent keys across "
          f"{len(list((ROOT / 'data/talents').glob('*.json')))} trees")
    print(f"  checked against {len(ids)} real ability ids")
    if not bad:
        print("\n  0 KEYS NAME A NON-EXISTENT ABILITY\n\nPASS")
        return 0
    print(f"\n  {len(bad)} KEYS NAME AN ABILITY THAT DOES NOT EXIST")
    print("  Each is silent dead data: well-formed key, real suffix, "
          "talent never fires.\n")
    for name, talent, key, aid in bad:
        print(f"    {talent:46s} {key}")
        print(f"      {'':46s} -> no ability '{aid}'   ({name})")
    print("\nFAIL")
    return 1


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--audit-all":
        return audit_all()
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    char_class = sys.argv[1]
    pairs = []
    for arg in sys.argv[2:]:
        if "=" not in arg:
            print(f"  expected key=value, got {arg!r}")
            return 2
        k, v = arg.split("=", 1)
        pairs.append((k, float(v)))
    probe(char_class, pairs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
