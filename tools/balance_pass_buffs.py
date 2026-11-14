"""
One-time balance-pass script (Kyle's direction, 2026-09-05): rewrites every
OG9 buff's raw-primary-stat stat_mods to sane early-game magnitudes.

Only touches stat_mods keys in PRIMARY_STATS. Derived-stat mods
(attack_power, spell_power, armor, haste, dodge, crit, resistances,
damage_taken_pct, max_mana_pct, etc.) are NOT touched - those are a
different scale and weren't part of what Kyle flagged as broken.

KNOWN LIMITATION (not fixed here, flagging rather than faking): every rank
of a multi-rank buff shares ONE stat_mods dict at the Ability level (see
Ability.__init__'s self.stat_mods and _apply_effect's buff/debuff branch,
which reads self.stat_mods directly with no per-rank lookup) - ranking up
mage_arcane_intellect etc. currently increases COST only, not the actual
buff magnitude. Real per-rank stat_mods scaling needs a new engine
mechanism (a per-rank stat_mods dict + a read-path change in
_apply_effect), which is out of scope for a numbers-only balance pass -
do NOT bolt on an unread JSON field to fake this. This script sets every
affected ability's flat stat_mods to its RANK-1 target value; higher
ranks will visibly still grant the same magnitude as rank 1 until that
engine work happens separately.

Run once, not idempotent-safe to run twice (would re-halve already-fixed
values) - this file is a historical record of the pass, not a repeatable
tool.
"""
import json

PRIMARY_STATS = {"strength", "agility", "intellect", "stamina", "spirit"}

# ability_id -> flat per-stat value applied to every primary-stat key
# already present in that ability's stat_mods (so a 5-stat buff and a
# 1-stat buff both use the same per-stat number, matching Kyle's "Mark
# should be +2 all stats" spec).
TARGETS = {
    "mage_arcane_intellect":            3,
    "warlock_demon_armor":              3,
    "priest_power_word_fortitude":      3,
    "shaman_mana_tide_totem":           4,
    "shaman_strength_of_earth_totem":   3,
    "druid_mark_of_the_wild":           2,   # Kyle's explicit number
    "paladin_blessing_of_might":        3,
    "paladin_blessing_of_kings":        3,
}

OG9 = ["warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"]


def main():
    changed = []
    for cls in OG9:
        path = f"data/abilities/{cls}.json"
        d = json.load(open(path, encoding="utf-8"))
        touched = False
        for a in d["abilities"]:
            if a["ability_id"] not in TARGETS:
                continue
            base = TARGETS[a["ability_id"]]
            mods = a["stat_mods"]
            primary_keys = [k for k in mods if k in PRIMARY_STATS]
            if not primary_keys:
                continue
            old_mods = dict(mods)
            for k in primary_keys:
                mods[k] = base
            changed.append((a["ability_id"], old_mods, dict(mods)))
            touched = True
        if touched:
            json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Rebalanced {len(changed)} buffs:\n")
    for ability_id, old, new in changed:
        print(f"  {ability_id}")
        print(f"    old: {old}")
        print(f"    new: {new}")


if __name__ == "__main__":
    main()

