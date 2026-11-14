"""
One-time content-fix script (Kyle's correction, 2026-09-06): rewrites
primary_stats on every hand-authored unique_item_def across all 4 quest
files to draw from data/items/gear_styles.py's real variety, instead of
the same 5 stat shapes repeated 49 times (audited before this script:
19x str_physical, 15x agi_physical, 14x int_caster, and that's it -
zero spirit-leaning cloth/leather/mail, zero int mail, zero caster
plate, zero real hybrids anywhere).

METHOD: iterates every item across all 4 quest files in a fixed,
deterministic order and assigns gear styles by CYCLING through each
armor_type's style list (not randomly - reproducible, guarantees even
coverage rather than random clustering). Weapons get their stat_template
cycled through str_physical/agi_physical/int_caster/str_int_hybrid/
agi_int_hybrid similarly, respecting each weapon_type's real-world fit
(2H melee weapons skip pure int_caster, wands/staves skip pure
str_physical/agi_physical - not an engine requirement, just keeps
flavor coherent).

Preserves every item's name, slot, item_level, rarity, weapon_type/
armor_type, flavor_text, and label - ONLY primary_stats (and
stat_template, kept in sync) are touched. Total stat budget per item is
derived from summing its OLD primary_stats, so power level doesn't
drift, only the stat SHAPE changes.

Run once.
"""
import json
import sys
sys.path.insert(0, "data/items")
from gear_styles import GEAR_STYLES, roll_primary_stats

QUEST_FILES = [
    "data/quests/valley_of_trials.json",
    "data/quests/durotar.json",
    "data/quests/razor_hill.json",
    "data/quests/echo_isles.json",
]

WEAPON_TEMPLATE_CYCLE = [
    ("str_physical",   {"strength": 0.7, "stamina": 0.3}),
    ("agi_physical",   {"agility": 0.7, "stamina": 0.3}),
    ("int_caster",     {"intellect": 0.7, "spirit": 0.3}),
    ("str_int_hybrid", {"strength": 0.4, "intellect": 0.4, "stamina": 0.2}),
    ("agi_int_hybrid", {"agility": 0.4, "intellect": 0.4, "stamina": 0.2}),
]

MELEE_ONLY_WEAPON_TYPES = {"sword_2h", "axe_2h", "mace_2h", "fist_weapon"}
CASTER_ONLY_WEAPON_TYPES = {"wand", "staff"}


def budget_from(old_stats):
    return sum(old_stats.values()) if old_stats else 6


def main():
    armor_cycle_idx = {k: 0 for k in GEAR_STYLES}
    weapon_cycle_idx = 0
    changed = []

    for path in QUEST_FILES:
        d = json.load(open(path, encoding="utf-8"))
        for q in d["quests"]:
            for item in q.get("unique_item_defs", []):
                old_stats = item.get("primary_stats", {})
                budget = budget_from(old_stats)
                wtype = item.get("weapon_type")
                armor_type = item.get("armor_type")

                if wtype == "shield":
                    styles = GEAR_STYLES["shield"]
                    label, weights, template = styles[armor_cycle_idx["shield"] % len(styles)]
                    armor_cycle_idx["shield"] += 1
                    new_stats = {s: max(1, round(budget * w)) for s, w in weights.items()}
                    item["primary_stats"] = new_stats
                    changed.append((item["name"], old_stats, new_stats, f"shield:{label}"))
                    continue

                if armor_type and armor_type in GEAR_STYLES:
                    styles = GEAR_STYLES[armor_type]
                    label, new_stats, template = roll_primary_stats(
                        armor_type, armor_cycle_idx[armor_type] % len(styles), budget)
                    armor_cycle_idx[armor_type] += 1
                    item["primary_stats"] = new_stats
                    if template:
                        item["stat_template"] = template
                    changed.append((item["name"], old_stats, new_stats, f"{armor_type}:{label}"))
                    continue

                if wtype is not None:
                    candidates = list(WEAPON_TEMPLATE_CYCLE)
                    if wtype in MELEE_ONLY_WEAPON_TYPES:
                        candidates = [c for c in candidates if c[0] != "int_caster"]
                    if wtype in CASTER_ONLY_WEAPON_TYPES:
                        candidates = [c for c in candidates if c[0] in ("int_caster", "agi_int_hybrid", "str_int_hybrid")]
                    template, weights = candidates[weapon_cycle_idx % len(candidates)]
                    weapon_cycle_idx += 1
                    new_stats = {s: max(1, round(budget * w)) for s, w in weights.items()}
                    item["primary_stats"] = new_stats
                    item["stat_template"] = template
                    changed.append((item["name"], old_stats, new_stats, f"weapon:{template}"))
                    continue

                # Pure accessory (neck/waist/off_hand, weapon_type=None,
                # armor_type=None)
                styles = GEAR_STYLES["accessory"]
                label, weights, template = styles[armor_cycle_idx["accessory"] % len(styles)]
                armor_cycle_idx["accessory"] += 1
                new_stats = {s: max(1, round(budget * w)) for s, w in weights.items()}
                item["primary_stats"] = new_stats
                if template:
                    item["stat_template"] = template
                changed.append((item["name"], old_stats, new_stats, f"accessory:{label}"))

        json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Rebalanced {len(changed)} items across {len(QUEST_FILES)} files:\n")
    for name, old, new, style in changed:
        print(f"  {name:36s} {style:32s} {old} -> {new}")


if __name__ == "__main__":
    main()
