#!/usr/bin/env python3
"""A talent that grants a stat has to actually grant it.

    PYTHONPATH=. python3 tools/qa_talent_effects.py [--all]

Kyle, 7 Nov 2026: "druid sharpened claws (2/4/6% bonus crit) isnt showing up
under melee or spell crit... even leader of the pack".

Both wrote the effect key `crit_chance`. _recalculate_derived_stats reads
`crit_chance_physical` and `crit_chance_spell`. Nothing read `crit_chance`, so
three ranks of Sharpened Claws put 6.0 into the effect dict and moved crit by
exactly 0.00 - no error, no warning, the points simply bought nothing. Two more
talents (Demonic Tactics, Improved Demonic Tactics) had the same key.

THE FAILURE MODE IS SILENCE, which is why this exists as a suite rather than a
fix. A talent effect is a string key written into a dict and read out of it
somewhere else. Mistype it, or invent a reasonable-sounding name nobody wired
up, and nothing anywhere complains - the talent just does nothing forever. The
same shape already bit this codebase at least twice before, both recorded in
entities/character.py: a conversion target naming a phantom attribute (Clarity
of the Heavens), and block vs block_value.

WHAT IS CHECKED. Every effect key that looks like a CHARACTER STAT must be
consumed somewhere - read out of the bonus pool by the recalc, resolved through
BONUS_KEY_ALIASES, or named by some other module (combat/abilities.py reads a
lot of them at cast time, pet.py reads the pet_* ones).

WHAT IS NOT. Per-ability keys (ability_<x>_<y>) and conversion keys
(<stat>_from_<stat>_pct) are built by string concatenation at the point of use,
so a literal search cannot see them and a false alarm on every one of them
would make this suite useless. They are skipped deliberately, which is a real
hole: a typo inside an ability_ key is still silent. Catching those needs a
different check, against the ability registry.
"""
import argparse
import collections
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Words that make an effect key look like a character stat rather than a
#: per-ability knob. Deliberately broad; a false positive here costs one
#: KNOWN entry, a false negative costs a dead talent nobody notices.
STAT_WORDS = ("crit", "dodge", "parry", "block", "haste", "armor", "hit_",
              "resist", "power", "strength", "agility", "intellect", "spirit",
              "stamina", "health", "mana", "expertise", "penetration", "regen",
              "threat", "speed")

#: Keys that are stat-shaped, unread, and KNOWN to be unimplemented content
#: rather than a typo. Each one is a talent that currently does nothing - this
#: is a to-do list with a test attached, not an excuse list. Empty it by
#: implementing the key or by changing the talent to use a live one.
KNOWN_UNIMPLEMENTED = {
    "shadow_resist_pct": "per-school resistance from talents is not wired up",
    "fire_crit_damage_pct": "per-school crit damage is not wired up",
    "frost_crit_damage_pct": "per-school crit damage is not wired up",
    "shadow_crit_damage_pct": "per-school crit damage is not wired up",
}


def skip(key):
    return key.startswith("ability_") or "_from_" in key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="list every stat key and its reader")
    args = ap.parse_args()

    keys = collections.Counter()
    examples = collections.defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / "data/talents/*.json"))):
        for node in json.loads(Path(f).read_text(encoding="utf-8")).get("nodes", []):
            if not isinstance(node, dict):
                continue
            for k, v in (node.get("effects") or {}).items():
                if not isinstance(v, (int, float)) or skip(k):
                    continue
                keys[k] += 1
                if len(examples[k]) < 3:
                    examples[k].append(f"{node.get('name')} [{Path(f).stem}]")

    sources = {}
    for pat in ("entities/*.py", "combat/*.py", "world/*.py", "ui/**/*.py"):
        for f in glob.glob(str(ROOT / pat), recursive=True):
            sources[f] = Path(f).read_text(encoding="utf-8")
    blob = "\n".join(sources.values())

    from entities.character import BONUS_KEY_ALIASES
    aliased = set(BONUS_KEY_ALIASES)

    statish = {k: n for k, n in keys.items() if any(w in k for w in STAT_WORDS)}
    findings, known = [], []
    for k, n in sorted(statish.items(), key=lambda kv: -kv[1]):
        if k in aliased:
            continue
        if f'"{k}"' in blob or f"'{k}'" in blob:
            continue
        (known if k in KNOWN_UNIMPLEMENTED else findings).append((k, n, examples[k]))

    print(f"  {len(keys)} talent effect keys checked "
          f"({len(statish)} name a character stat)")
    print(f"  skipped: ability_* and *_from_*_pct, built by concatenation at "
          f"the point of use")
    print(f"  {len(aliased)} key(s) resolved through BONUS_KEY_ALIASES: "
          f"{', '.join(sorted(aliased))}\n")

    if known:
        print(f"  {len(known)} known-unimplemented key(s), {sum(n for _, n, _ in known)} "
              f"talent(s) currently doing nothing:")
        for k, n, ex in known:
            print(f"    {k:28}{n:>3}x  {KNOWN_UNIMPLEMENTED[k]}")
        print()

    if args.all:
        for k, n in sorted(statish.items()):
            where = [Path(f).name for f, s in sources.items()
                     if f'"{k}"' in s or f"'{k}'" in s]
            tag = "ALIAS" if k in aliased else (", ".join(sorted(set(where))[:3]) or "-")
            print(f"    {k:34}{n:>3}x  {tag}")
        print()

    if findings:
        print(f"  {len(findings)} stat-shaped effect key(s) that NOTHING reads - "
              f"these talents do nothing:\n")
        for k, n, ex in findings:
            print(f"    {k:28}{n:>3} talent(s)   {ex[0]}")
        print("\n  Either wire the key up, point the talent at a live key, or - if it is "
              "\n  content not built yet - add it to KNOWN_UNIMPLEMENTED with a reason.")
        print("\nFAIL")
        return 1

    print("  every stat-shaped talent effect is read by something")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
