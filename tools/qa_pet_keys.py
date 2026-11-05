#!/usr/bin/env python3
"""Pet scaling keys must sit on a class that actually has a pet.

    PYTHONPATH=. python3 tools/qa_pet_keys.py

WHY THIS EXISTS. pet_damage, pet_health and pet_armor are real keys -
entities/pet.py:143-146 reads all three off the owner's talents - so
audit_talents, which asks only "does any engine code read this key",
passes them wherever they appear. But a pet key on a class that never
summons a pet is DEAD DATA: syntactically valid, read by live code, and
silent in play, because the loop that reads it runs per-pet and the class
has no pets to iterate.

Found 5 Nov 2026 while rebuilding Witch Doctor Shadow Hunting. Five CoA
talents in that spec buff Serpent Wards, and the obvious translation was
pet_damage / pet_health / pet_armor. But nothing in
data/abilities/witch_doctor.json summons a pet - Call of Sseratus, CoA's
"summon 4 Serpent Wards", had already been translated into an enemy_aoe
spell_dot by an earlier pass. Three nodes would have done nothing at all
while passing audit_talents, qa_ability_text, qa_talent_tiers_reachable
and qa_abilities_obtainable.

This is the project's signature bug shape - one rule, N implementations,
and a key whose name reads plausibly - so it gets its own check rather
than a note in a commit message.

HOW A CLASS IS JUDGED TO HAVE A PET. Its ability file contains an ability
carrying any of the pet-summoning fields the engine recognises, or naming
a template in combat/pet_templates.py. A class with none of those can
never have a pet in play, so a pet key in its trees is unreachable.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PET_KEYS = ("pet_damage", "pet_health", "pet_armor")

#: Ability fields that actually produce a pet. Kept as a tuple so a new
#: summoning field added to the engine shows up here as a missing name
#: rather than as a silent pass.
SUMMON_FIELDS = ("summons_pet", "pet_template", "pet_type", "summon_pet",
                 "pet_id", "summons")


def ability_records(path):
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("abilities", data)
    if isinstance(data, dict):
        data = list(data.values())
    return [a for a in data if isinstance(a, dict)]


def class_has_pet(path):
    """True when any ability in this class's file summons a pet."""
    for a in ability_records(path):
        for field in SUMMON_FIELDS:
            if a.get(field):
                return True, f"{a.get('ability_id')} has {field}"
        # effect_type is the other route - a summon effect with a template.
        if str(a.get("effect_type", "")).startswith("summon"):
            return True, f"{a.get('ability_id')} effect_type={a['effect_type']}"
    return False, ""


def tree_class_key(tree_id):
    """Map a tree_id onto its abilities file stem.

    Tree ids are <class>_<spec>, and class names with an underscore
    (witch_doctor, witch_hunter, sun_cleric, knight_of_xoroth) mean the
    split cannot be on the first underscore. So the longest ability-file
    stem that prefixes the tree id wins, which is unambiguous.
    """
    stems = sorted((p.stem for p in (ROOT / "data/abilities").glob("*.json")),
                   key=len, reverse=True)
    for stem in stems:
        if tree_id == stem or tree_id.startswith(stem + "_"):
            return stem
    return None


def main():
    abil_dir = ROOT / "data/abilities"
    pet_classes = {}
    for path in sorted(abil_dir.glob("*.json")):
        has, why = class_has_pet(path)
        pet_classes[path.stem] = (has, why)

    findings = []
    unmapped = []
    checked = 0
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        tree = json.loads(path.read_text())
        tree_id = tree.get("tree_id") or path.stem
        stem = tree_class_key(tree_id)
        if stem is None:
            unmapped.append(tree_id)
            continue
        has_pet = pet_classes.get(stem, (False, ""))[0]
        checked += 1
        if has_pet:
            continue
        for n in tree.get("nodes", []):
            hit = [k for k in (n.get("effects") or {}) if k in PET_KEYS]
            # also catch a pet key hidden in a proc's applied buff
            proc = n.get("proc") or {}
            ae = proc.get("apply_effect")
            for mods in ([ae.get("stat_mods")] if isinstance(ae, dict) else []):
                hit += [k for k in (mods or {}) if k in PET_KEYS]
            if hit:
                findings.append(
                    f"[{path.name}] {n['talent_id']} ({n['name']!r}): "
                    f"{', '.join(sorted(set(hit)))} on a class with no pet "
                    f"summon - dead data")

    classes_with = sorted(k for k, v in pet_classes.items() if v[0])
    print(f"  {len(pet_classes):>5} ability files, "
          f"{len(classes_with)} summon a pet")
    print(f"  {checked:>5} talent trees checked")
    if unmapped:
        print(f"  {len(unmapped):>5} trees whose class could not be resolved: "
              f"{', '.join(unmapped[:6])}")
    print(f"  {len(findings):>5} PET KEYS ON A PETLESS CLASS")
    if findings:
        print()
        for f in findings:
            print("   ", f)
        print("\nFAIL")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
