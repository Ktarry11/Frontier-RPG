"""
Regenerate every talent tree JSON in data/talents/ from the authoring data in
tools/talents_*.py, then validate the result.

Run from the project root:   python3 tools/generate_talents.py

Validation catches the two failure modes that would otherwise be silent:
  1. An effect key referencing an ability_id that does not exist, which would
     make the talent do nothing at all with no error.
  2. A stat effect key the Character recalc does not read, same problem.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.talent_builder import write_tree            # noqa: E402
from tools import talents_physical                      # noqa: E402
from tools import talents_casters                       # noqa: E402
from tools import talents_hybrids                       # noqa: E402
from tools import talents_coa                           # noqa: E402
from combat.abilities import get_class_abilities        # noqa: E402

OUT_DIR = ROOT / "data" / "talents"

CLASSES = ["Warrior", "Rogue", "Hunter", "Mage", "Warlock",
           "Priest", "Druid", "Shaman", "Paladin",
           # CoA classes with authored ability kits
           "Stormbringer", "Tinker", "Venomancer", "Primalist"]

# Effect keys consumed by Character._recalculate_derived_stats().
KNOWN_STAT_KEYS = {
    "strength", "stamina", "intellect", "spirit", "agility",
    "attack_power", "ranged_attack_power", "spell_power", "healing_power",
    "crit_chance_physical", "crit_chance_spell",
    "dodge", "parry", "block", "haste",
    "armor", "magic_resistance", "hit_rating",
    "max_health_pct", "max_mana_pct",
}

# Effect keys consumed by Ability._damage_multiplier().
KNOWN_GLOBAL_KEYS = {"all_damage", "physical_damage", "spell_damage", "healing_done"}

ABILITY_SUFFIXES = ("_damage", "_cost", "_cooldown")


def valid_ability_ids():
    ids = set()
    for c in CLASSES:
        for a in get_class_abilities(c).get_all_abilities():
            ids.add(a.ability_id)
    return ids


def validate(tree_id, talents, ability_ids):
    problems = []
    for suffix, name, tier, column, max_points, effects, desc in talents:
        if not 0 <= column <= 3:
            problems.append(f"{tree_id}/{suffix}: column {column} out of range 0-3")
        if not 0 <= tier <= 6:
            problems.append(f"{tree_id}/{suffix}: tier {tier} out of range 0-6")
        for key in effects:
            if key in KNOWN_STAT_KEYS or key in KNOWN_GLOBAL_KEYS:
                continue
            if key.startswith("ability_"):
                matched = None
                for tail in ABILITY_SUFFIXES:
                    if key.endswith(tail):
                        matched = key[len("ability_"):-len(tail)]
                        break
                if matched is None:
                    problems.append(f"{tree_id}/{suffix}: '{key}' has no valid suffix")
                elif matched not in ability_ids:
                    problems.append(
                        f"{tree_id}/{suffix}: '{key}' targets unknown ability '{matched}'")
                continue
            problems.append(f"{tree_id}/{suffix}: unknown effect key '{key}'")
    return problems


def check_layout(talents, tree_id):
    """No two talents may occupy the same (tier, column) slot - they would
    render exactly on top of each other and only one would be clickable."""
    seen = {}
    problems = []
    for suffix, name, tier, column, *_ in talents:
        if (tier, column) in seen:
            problems.append(
                f"{tree_id}: '{suffix}' collides with '{seen[(tier, column)]}' "
                f"at tier {tier} column {column}")
        seen[(tier, column)] = suffix
    return problems


def main():
    ability_ids = valid_ability_ids()
    all_problems = []
    total_nodes = 0
    written = []

    for module in (talents_physical, talents_casters, talents_hybrids,
                   talents_coa):
        for tree_id, spec_name, description, talents in module.TREES:
            all_problems += validate(tree_id, talents, ability_ids)
            all_problems += check_layout(talents, tree_id)
            path, count = write_tree(OUT_DIR, tree_id, spec_name, description, talents)
            written.append((tree_id, count))
            total_nodes += count

    for tree_id, count in written:
        print(f"  {tree_id:<26} {count:>3} talents")
    print(f"\n{len(written)} trees, {total_nodes} talents total")

    if all_problems:
        print(f"\n!! {len(all_problems)} VALIDATION PROBLEMS:")
        for p in all_problems:
            print("   -", p)
        return 1
    print("Validation passed: every effect key is consumed by real code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
