"""
Generate data/abilities/<class>.json from tools/ability_data.py.

Run from project root:   python3 tools/generate_abilities.py

Abilities were previously hardcoded as Python factory functions in
combat/abilities.py, which made them the only major game system NOT
data-driven (items, creatures, consumables and talents all live in JSON).
This brings them in line: the JSON is the source of truth at runtime, and
this script is an authoring convenience for regenerating it.

Validation catches:
  - duplicate ability ids within a class
  - unknown effect_type values
  - dot/hot/buff/debuff entries with no duration (they would silently
    become 1-turn effects)
  - buff/debuff entries with no stat_mods (they would do nothing)
  - any talent effect key pointing at an ability id that no longer exists
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.ability_data import CLASS_KITS              # noqa: E402
from combat.rank_generator import generate_rank_levels  # noqa: E402

OUT_DIR = ROOT / "data" / "abilities"

VALID_EFFECT_TYPES = {
    "damage", "spell_damage", "heal",
    "dot", "spell_dot", "hot", "buff", "debuff",
}
DURATION_REQUIRED = {"dot", "spell_dot", "hot", "buff", "debuff"}
MODS_REQUIRED = {"buff", "debuff"}

# Only Mana abilities get more expensive as they rank up (WoW-correct);
# Rage/Energy costs stay flat across all ranks.
COST_SCALES = {"mana"}

# Valid resource_type strings, derived from the ResourceType enum so an
# authoring typo ("statik") fails loudly here instead of silently becoming
# Mana at load time.
from combat.abilities import ResourceType  # noqa: E402
VALID_RESOURCES = {rt.value for rt in ResourceType}


def build_ranks(resource, num_ranks, level_learned,
                cost_start, cost_step, effect_start, effect_step):
    levels = generate_rank_levels(level_learned, num_ranks)
    ranks = []
    for i, lvl in enumerate(levels):
        cost = cost_start + (i * cost_step if resource in COST_SCALES else 0)
        ranks.append({
            "rank": i + 1,
            "level_req": lvl,
            "cost": cost,
            "effect_value": effect_start + i * effect_step,
        })
    return ranks


def build_class(prefix, kit):
    abilities = []
    for entry in kit:
        # Kits are 14-tuples. CoA builder/spender classes append a 15th
        # element, `generates`, e.g. {"resource": "static", "amount": 20}.
        (suffix, name, resource, num_ranks, level_learned,
         cost_start, cost_step, effect_start, effect_step,
         cooldown, effect_type, duration, stat_mods, desc) = entry[:14]
        generates = entry[14] if len(entry) > 14 else None

        ability = {
            "ability_id": f"{prefix}_{suffix}",
            "name": name,
            "resource_type": resource,
            "cooldown": cooldown,
            "effect_type": effect_type,
            "duration": duration,
            "stat_mods": stat_mods or {},
            "description": desc,
            "ranks": build_ranks(resource, num_ranks, level_learned,
                                 cost_start, cost_step,
                                 effect_start, effect_step),
        }
        if generates:
            ability["generates"] = generates
        abilities.append(ability)
    return abilities


def validate(class_name, abilities):
    problems = []
    seen = set()
    for a in abilities:
        aid = a["ability_id"]
        if aid in seen:
            problems.append(f"{class_name}: duplicate ability id '{aid}'")
        seen.add(aid)

        rt = a["resource_type"]
        if rt not in VALID_RESOURCES:
            problems.append(f"{class_name}/{aid}: unknown resource_type '{rt}'")

        gen = a.get("generates")
        if gen:
            if gen.get("resource") not in VALID_RESOURCES:
                problems.append(
                    f"{class_name}/{aid}: generates unknown resource "
                    f"'{gen.get('resource')}'")
            if gen.get("amount", 0) <= 0:
                problems.append(f"{class_name}/{aid}: generates non-positive amount")
            if gen.get("resource") == rt:
                problems.append(
                    f"{class_name}/{aid}: generates the same resource it costs")

        et = a["effect_type"]
        if et not in VALID_EFFECT_TYPES:
            problems.append(f"{class_name}/{aid}: unknown effect_type '{et}'")
        if et in DURATION_REQUIRED and a["duration"] < 1:
            problems.append(f"{class_name}/{aid}: '{et}' needs a duration >= 1")
        if et in MODS_REQUIRED and not a["stat_mods"]:
            problems.append(f"{class_name}/{aid}: '{et}' has no stat_mods, would do nothing")
        if not a["ranks"]:
            problems.append(f"{class_name}/{aid}: no ranks generated")
        for r in a["ranks"]:
            if r["level_req"] > 60:
                problems.append(f"{class_name}/{aid}: rank {r['rank']} past level cap")
    return problems


def check_talent_references(all_ability_ids):
    """Every ability_<id>_* key in the generated talent JSON must resolve."""
    problems = []
    talents_dir = ROOT / "data" / "talents"
    if not talents_dir.exists():
        return problems
    for path in sorted(talents_dir.glob("*.json")):
        data = json.loads(path.read_text())
        for node in data.get("nodes", []):
            for key in node.get("effects", {}):
                if not key.startswith("ability_"):
                    continue
                for tail in ("_damage", "_cost", "_cooldown"):
                    if key.endswith(tail):
                        target = key[len("ability_"):-len(tail)]
                        if target not in all_ability_ids:
                            problems.append(
                                f"{path.name}/{node['talent_id']}: "
                                f"references missing ability '{target}'")
                        break
    return problems


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    problems = []
    all_ids = set()
    total = 0

    for class_name, (prefix, kit) in CLASS_KITS.items():
        abilities = build_class(prefix, kit)
        problems += validate(class_name, abilities)
        all_ids.update(a["ability_id"] for a in abilities)

        payload = {"class": class_name, "abilities": abilities}
        (OUT_DIR / f"{prefix}.json").write_text(json.dumps(payload, indent=2))

        ranks = sum(len(a["ranks"]) for a in abilities)
        total += len(abilities)
        print(f"  {class_name:<9} {len(abilities):>2} abilities, {ranks:>3} ranks")

    problems += check_talent_references(all_ids)

    print(f"\n9 classes, {total} abilities total")
    if problems:
        print(f"\n!! {len(problems)} PROBLEMS:")
        for p in problems:
            print("   -", p)
        return 1
    print("Validation passed: effect types, durations, ranks, and every "
          "talent ability reference all resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
