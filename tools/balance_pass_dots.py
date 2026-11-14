"""
One-time balance-pass script (Kyle's direction, 2026-09-05): rewrites
rank-1 effect_value (TOTAL damage across the whole duration, not
per-tick - see _apply_effect's dot/spell_dot branch: total = effect_value
+ power, split across duration turns) for every remaining OG9 dot/
spell_dot ability not already handled by expand_ranks_og9.py's 13
spam-skill expansion (Corruption, Shadow Word: Pain, Moonfire already
done there).

Targets follow the same CD-tier logic as balance_pass_damage.py, since a
DoT's total output over its lifetime is the fair comparison point to a
direct-damage hit of the same cooldown - NOT scaled down further for
being a DoT, since these totals were already being compared per-tick
in the old (too-high) baseline.

  cd=0:      42-50 total
  cd=1:      48-54 total
  cd=2:      54-62 total
  cd=3:      60-70 total
  cd=4+:     70-85 total

Same proportional-rank-rescaling approach as the other balance passes:
rank 1 is targeted directly, ranks 2+ keep the OLD table's growth ratio.

Run once, not idempotent-safe to run twice.
"""
import json

OG9 = ["warrior", "rogue", "hunter", "mage", "warlock", "priest", "shaman", "druid", "paladin"]

# ability_id -> new rank-1 effect_value (TOTAL over duration)
TARGETS = {
    # --- Warrior ---
    "warrior_rend": 46,                   # cd2, dur3

    # --- Rogue ---
    "rogue_rupture": 58,                  # cd3, dur4 - finisher-style
    "rogue_hemorrhage": 44,               # cd0, dur3

    # --- Hunter ---
    "hunter_serpent_sting": 52,           # cd2, dur4
    "hunter_explosive_trap": 62,          # cd3, dur3
    "hunter_explosive_shot": 60,          # cd2, dur2 - short/punchy
    "hunter_black_arrow": 66,             # cd3, dur5

    # --- Mage ---
    "mage_living_flame": 54,              # cd2, dur4

    # --- Warlock ---
    "warlock_immolate": 54,               # cd2, dur3
    "warlock_unstable_affliction": 64,    # cd3, dur3
    "warlock_curse_of_agony": 46,         # cd0, dur4

    # --- Priest ---
    "priest_mind_flay": 50,               # cd1, dur3
    "priest_vampiric_touch": 48,          # cd0, dur5 - long duration, keep per-tick sane
    "priest_mind_sear": 64,               # cd3, dur3, aoe

    # --- Shaman ---
    "shaman_flame_shock": 52,             # cd2, dur3
    "shaman_searing_totem": 56,           # cd2, dur4 - totem, persistent-ish
    "shaman_magma_totem": 62,             # cd3, dur4, aoe totem

    # --- Druid ---
    "druid_insect_swarm": 46,             # cd0, dur4
    "druid_starfall": 78,                 # cd4, dur3, aoe - premium cooldown
    "druid_rake": 44,                     # cd0, dur3, cat opener

    # --- Paladin ---
    "paladin_consecration": 56,           # cd2, dur3, aoe ground effect
}


def main():
    changed = []
    for cls in OG9:
        path = f"data/abilities/{cls}.json"
        d = json.load(open(path, encoding="utf-8"))
        touched = False
        for a in d["abilities"]:
            if a["ability_id"] not in TARGETS:
                continue
            new_r1 = TARGETS[a["ability_id"]]
            old_r1 = a["ranks"][0]["effect_value"]
            if old_r1 == 0:
                continue
            ratio = new_r1 / old_r1
            old_vals = [r["effect_value"] for r in a["ranks"]]
            for r in a["ranks"]:
                r["effect_value"] = max(1, int(round(r["effect_value"] * ratio)))
            a["ranks"][0]["effect_value"] = new_r1
            new_vals = [r["effect_value"] for r in a["ranks"]]
            changed.append((a["ability_id"], a["cooldown"], a["duration"], old_vals, new_vals))
            touched = True
        if touched:
            json.dump(d, open(path, "w", encoding="utf-8"), indent=2)

    print(f"Rebalanced {len(changed)} DoT abilities:\n")
    for ability_id, cd, dur, old, new in changed:
        print(f"  {ability_id:32s} cd={cd} dur={dur}  {old} -> {new}")


if __name__ == "__main__":
    main()
