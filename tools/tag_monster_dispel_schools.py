#!/usr/bin/env python3
"""Make monster debuffs dispellable, so cleanses have something to remove.

THE PROBLEM. Fourteen player abilities across fourteen classes exist purely
to remove enemy debuffs - Paladin's Cleanse, Priest's Dispel Magic and
Abolish Disease, Druid's and Primalist's nature cleanses, Tinker's Med Pack,
Chronomancer's Roll Back, Sun Cleric's Sanctify, and more. A sweep of the
whole game found ZERO monster effects carrying a dispel_type, against 525
debuff and DoT monster abilities. Every one of those cleanses had literally
nothing to act on in PvE. The six dispellable effects in the game are all
applied by players, to players.

MonsterAbility had no dispel_type field at all, so this was not an
authoring oversight anyone could have fixed in the data - the engine could
not carry it. That part is fixed in entities/monster.py; this tool fills in
the schools.

THE RULES, and why each one. Matched against the ability name first, then
the damage school, because the name is what says what the thing IS:

  physical           -> NOT dispellable, full stop. A bleed is not a magic
                       effect in WoW and no cleanse has ever removed one.
                       This is the single biggest bucket and leaving it
                       untagged is the correct answer, not a gap.
  poison/venom/sting -> poison
  plague/rot/blight  -> disease
  curse/hex/jinx     -> curse
  any other non-physical debuff or DoT -> magic

Everything else - a monster's own self-buff - stays untagged. Frontier has
no purge-enemy-buff ability for it to serve, and MonsterAbility already
refuses to pass a dispel_type on a self_only effect.

The rules are deliberately conservative: a name has to actually say poison
to be poison. A frost DoT called "Chilling Grasp" becomes magic, which is
right - Frost debuffs are Magic in WoW.

    python3 tools/tag_monster_dispel_schools.py            # dry run, counts
    python3 tools/tag_monster_dispel_schools.py --apply
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data/creatures/ability_kits.json"

# These stems are matched ANYWHERE in the name, not only at a word boundary,
# because the compounds are real: "Neurotoxin" is a poison and a leading \b
# made it fall through to magic. "rot" is the one stem that must stay
# boundary-anchored - unanchored it matches "Throat", "Frost" and "Garrote".
POISON = re.compile(r"(poison|venom|toxin|toxic|envenom|acid)|\b(sting)", re.I)
DISEASE = re.compile(r"(plague|disease|blight|fever|infect|pestilen|putrid|"
                     r"festering|contagio|decay)|\brot(ting|ten)?\b", re.I)
CURSE = re.compile(r"(curse|hex|jinx|malediction)|\b(doom)", re.I)

#: kinds that land something removable on a player
DEBUFF_KINDS = {"debuff", "dot"}


def school_for(name: str, school: str) -> str | None:
    """The dispel school for one monster ability, or None for undispellable."""
    if POISON.search(name):
        return "poison"
    if DISEASE.search(name):
        return "disease"
    if CURSE.search(name):
        return "curse"
    # Physical is checked AFTER the name tests on purpose: a physical-school
    # ability named "Venom Spit" is still a poison, and WoW agrees - poisons
    # deal physical or nature damage and are dispellable either way.
    if (school or "physical") == "physical":
        return None
    return "magic"


def main(argv: list[str]) -> int:
    apply = "--apply" in argv
    doc = json.loads(KITS.read_text(encoding="utf-8"))
    kits = doc["kits"]

    counts = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)
    touched = 0

    for kit_name, entries in kits.items():
        for entry in entries:
            kind = entry.get("kind")
            name = entry.get("name", "")

            # A damage ability can still carry a rider debuff - that is how
            # bosses apply them without spending a turn - so riders are
            # tagged too, off the same rules.
            rider = entry.get("rider")
            if isinstance(rider, dict) and rider.get("effect") == "debuff":
                sch = school_for(name, entry.get("school", "physical"))
                if sch:
                    counts[f"rider:{sch}"] += 1
                    if len(examples[sch]) < 4:
                        examples[sch].append(f"{name} (rider)")
                    if apply:
                        rider["dispel_type"] = sch
                        touched += 1

            if kind not in DEBUFF_KINDS or entry.get("self_only"):
                continue
            sch = school_for(name, entry.get("school", "physical"))
            if sch is None:
                counts["undispellable (physical)"] += 1
                continue
            counts[sch] += 1
            if len(examples[sch]) < 4:
                examples[sch].append(name)
            if apply:
                entry["dispel_type"] = sch
                touched += 1

    print(f"{len(kits)} monster ability kits\n")
    for key, n in counts.most_common():
        print(f"  {key:<26}{n}")
    print()
    for sch in ("poison", "disease", "curse", "magic"):
        if examples[sch]:
            print(f"  {sch:<9} e.g. " + ", ".join(examples[sch]))

    if apply:
        KITS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {KITS.relative_to(ROOT)} - {touched} effects tagged")
    else:
        print("\n(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
